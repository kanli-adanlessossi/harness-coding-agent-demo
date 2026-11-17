#!/usr/bin/env python3
"""Run the coding-agent eval suite.

Each task runs in a fresh workspace (sample service + agent baseline). After the
agent finishes, a hidden check test is copied in and the full test suite runs.
A task passes if every test is green (hidden check + existing tests = no regressions).

Agents:
  claude     the real Claude Code CLI in headless mode (needs ANTHROPIC_API_KEY)
  reference  applies the known-good solution: proves every task is solvable
  none       changes nothing: proves every check actually tests something

Examples:
  python evals/run_evals.py --agent reference --expect all-pass
  python evals/run_evals.py --agent claude --repeat 3 --out results/head.json
  python evals/run_evals.py --agent claude --baseline /tmp/old/agent-baseline --out results/base.json
  python evals/run_evals.py --agent claude --model <model-id> --out results/new-model.json
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workspace import DEFAULT_BASELINE, REPO_ROOT, create_workspace  # noqa: E402

TASKS_DIR = Path(__file__).resolve().parent / "tasks"
SCRUBBED_ENV = {"TARIFF_API_KEY"}


def load_tasks(selected: list[str] | None) -> list[dict]:
    tasks = []
    for task_dir in sorted(p for p in TASKS_DIR.iterdir() if p.is_dir()):
        spec = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
        spec["dir"] = task_dir
        if not selected or spec["id"] in selected:
            tasks.append(spec)
    if selected and len(tasks) != len(selected):
        found = {t["id"] for t in tasks}
        raise SystemExit(f"Unknown task(s): {sorted(set(selected) - found)}")
    return tasks


def run_claude(workspace: Path, prompt: str, model: str | None, max_budget: float, timeout: int) -> dict:
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--permission-mode", "acceptEdits",
        "--max-budget-usd", str(max_budget),
        "--mcp-config", str(workspace / ".mcp.json"),
        "--strict-mcp-config",
    ]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k not in SCRUBBED_ENV}
    try:
        proc = subprocess.run(cmd, cwd=workspace, capture_output=True, text=True, timeout=timeout, env=env)
    except FileNotFoundError:
        raise SystemExit("Claude Code CLI not found. Install it: npm install -g @anthropic-ai/claude-code")
    except subprocess.TimeoutExpired:
        return {"agent_error": f"timeout after {timeout}s"}
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"agent_error": (proc.stderr or proc.stdout)[-500:]}
    return {
        "cost_usd": out.get("total_cost_usd"),
        "turns": out.get("num_turns"),
        "agent_error": out.get("result") if out.get("is_error") else None,
    }


def run_reference(workspace: Path, task: dict) -> dict:
    shutil.copytree(task["dir"] / "reference", workspace, dirs_exist_ok=True)
    return {}


def run_checks(workspace: Path, task: dict) -> tuple[bool, str]:
    target = workspace / "tests" / f"test_hidden_{task['id'].replace('-', '_')}.py"
    shutil.copy2(task["dir"] / "check_test.py", target)
    env = {k: v for k, v in os.environ.items() if k not in SCRUBBED_ENV}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
        cwd=workspace, capture_output=True, text=True, env=env, timeout=300,
    )
    tail = "\n".join(proc.stdout.strip().splitlines()[-15:])
    return proc.returncode == 0, tail


def guard_blocks(workspace: Path) -> int:
    log = workspace / ".claude" / "audit.jsonl"
    return len(log.read_text(encoding="utf-8").splitlines()) if log.exists() else 0


def run_task(task: dict, args: argparse.Namespace, attempt: int) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix=f"eval-{task['id']}-"))
    workspace = create_workspace(tmp / "ws", Path(args.baseline))
    started = time.monotonic()
    if args.agent == "claude":
        meta = run_claude(workspace, task["prompt"], args.model, args.max_budget_usd, args.timeout)
    elif args.agent == "reference":
        meta = run_reference(workspace, task)
    else:
        meta = {}
    duration = round(time.monotonic() - started, 1)
    passed, output = run_checks(workspace, task)
    result = {
        "task": task["id"],
        "attempt": attempt,
        "passed": passed,
        "duration_s": duration,
        "guard_blocks": guard_blocks(workspace),
        **meta,
    }
    if not passed:
        result["check_output"] = output
    if args.keep:
        result["workspace"] = str(workspace)
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return result


def summarise(runs: list[dict], tasks: list[dict]) -> dict:
    per_task = {}
    for task in tasks:
        mine = [r for r in runs if r["task"] == task["id"]]
        costs = [r["cost_usd"] for r in mine if r.get("cost_usd") is not None]
        turns = [r["turns"] for r in mine if r.get("turns") is not None]
        per_task[task["id"]] = {
            "passes": sum(r["passed"] for r in mine),
            "attempts": len(mine),
            "pass_rate": round(sum(r["passed"] for r in mine) / len(mine), 3),
            "avg_cost_usd": round(sum(costs) / len(costs), 4) if costs else None,
            "avg_turns": round(sum(turns) / len(turns), 1) if turns else None,
            "guard_blocks": sum(r["guard_blocks"] for r in mine),
            "capability": task.get("tests_capability", ""),
        }
    total = len(runs)
    return {"pass_rate": round(sum(r["passed"] for r in runs) / total, 3) if total else 0.0, "tasks": per_task}


def to_markdown(report: dict) -> str:
    m = report["meta"]
    lines = [
        f"### Agent evals: baseline {m['baseline_version']} · agent `{m['agent']}`"
        + (f" · model `{m['model']}`" if m.get("model") else ""),
        "",
        f"**Overall pass rate: {report['summary']['pass_rate']:.0%}** ({m['repeat']} attempt(s) per task)",
        "",
        "| Task | Passed | Avg turns | Avg cost (USD) | Guard blocks | Tests |",
        "|---|---|---|---|---|---|",
    ]
    for tid, s in report["summary"]["tasks"].items():
        cost = f"{s['avg_cost_usd']:.4f}" if s["avg_cost_usd"] is not None else "–"
        turns = s["avg_turns"] if s["avg_turns"] is not None else "–"
        lines.append(f"| {tid} | {s['passes']}/{s['attempts']} | {turns} | {cost} | {s['guard_blocks']} | {s['capability']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agent", choices=["claude", "reference", "none"], default="claude")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE), help="path to an agent-baseline folder")
    parser.add_argument("--tasks", nargs="*", help="task ids (default: all)")
    parser.add_argument("--repeat", type=int, default=1, help="attempts per task (agents are non-deterministic)")
    parser.add_argument("--model", help="model id passed to the agent CLI")
    parser.add_argument("--max-budget-usd", type=float, default=1.0, help="spend cap per agent run")
    parser.add_argument("--timeout", type=int, default=600, help="seconds per agent run")
    parser.add_argument("--out", help="write the JSON report here")
    parser.add_argument("--md", help="append a markdown summary here (e.g. $GITHUB_STEP_SUMMARY)")
    parser.add_argument("--keep", action="store_true", help="keep workspaces for inspection")
    parser.add_argument("--expect", choices=["all-pass", "all-fail"], help="exit 1 unless every task matches")
    args = parser.parse_args()

    tasks = load_tasks(args.tasks)
    baseline = Path(args.baseline)
    version_file = baseline / "VERSION"
    runs = []
    for task in tasks:
        for attempt in range(1, args.repeat + 1):
            result = run_task(task, args, attempt)
            mark = "PASS" if result["passed"] else "FAIL"
            print(f"[{mark}] {task['id']} (attempt {attempt}, {result['duration_s']}s)", flush=True)
            runs.append(result)

    report = {
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "agent": args.agent,
            "model": args.model,
            "baseline": str(baseline),
            "baseline_version": version_file.read_text().strip() if version_file.exists() else "unknown",
            "repeat": args.repeat,
            "repo": str(REPO_ROOT),
        },
        "summary": summarise(runs, tasks),
        "runs": runs,
    }
    md = to_markdown(report)
    print("\n" + md)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.md:
        with open(args.md, "a", encoding="utf-8") as fh:
            fh.write(md + "\n")

    if args.expect == "all-pass" and not all(r["passed"] for r in runs):
        raise SystemExit("Expected every task to pass.")
    if args.expect == "all-fail" and any(r["passed"] for r in runs):
        raise SystemExit("Expected every task to fail on the untouched service (a check tests nothing).")


if __name__ == "__main__":
    main()
