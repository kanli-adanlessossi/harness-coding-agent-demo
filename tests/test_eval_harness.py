"""The eval suite must be trustworthy: every task solvable, every check meaningful."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "evals" / "run_evals.py"
COMPARE = ROOT / "evals" / "compare.py"


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)


def test_reference_solutions_pass_every_task(tmp_path):
    res = run(RUNNER, "--agent", "reference", "--expect", "all-pass", "--out", tmp_path / "ref.json")
    assert res.returncode == 0, res.stdout + res.stderr


def test_untouched_service_fails_every_task(tmp_path):
    res = run(RUNNER, "--agent", "none", "--expect", "all-fail", "--out", tmp_path / "none.json")
    assert res.returncode == 0, res.stdout + res.stderr


def test_compare_reports_improvement(tmp_path):
    run(RUNNER, "--agent", "none", "--out", tmp_path / "base.json")
    run(RUNNER, "--agent", "reference", "--out", tmp_path / "head.json")
    res = run(COMPARE, tmp_path / "base.json", tmp_path / "head.json", "--fail-on-regression")
    assert res.returncode == 0
    assert "**Better:**" in res.stdout


def test_compare_flags_regression(tmp_path):
    run(RUNNER, "--agent", "reference", "--out", tmp_path / "base.json")
    run(RUNNER, "--agent", "none", "--out", tmp_path / "head.json")
    res = run(COMPARE, tmp_path / "base.json", tmp_path / "head.json", "--fail-on-regression")
    assert res.returncode == 1
    assert "**Worse:**" in res.stdout


def test_workspace_has_baseline_and_mcp_config(tmp_path):
    ws = tmp_path / "ws"
    assert run(ROOT / "scripts" / "new_workspace.py", ws).returncode == 0
    assert (ws / "CLAUDE.md").exists()
    assert (ws / ".claude" / "hooks" / "guard.py").exists()
    assert (ws / ".claude" / "skills" / "rest-endpoint" / "SKILL.md").exists()
    config = json.loads((ws / ".mcp.json").read_text())
    assert "post-docs" in config["mcpServers"]
    assert not (ws / "docs").exists(), "internal docs must only be reachable via MCP"
