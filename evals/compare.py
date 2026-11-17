#!/usr/bin/env python3
"""Compare two eval reports and answer: did the change make the agent better,
or did it only make it different?

  python evals/compare.py results/base.json results/head.json [--md $GITHUB_STEP_SUMMARY] [--fail-on-regression]

Verdict per task:
  better / worse             pass rate went up / down
  same quality, cheaper      pass rate equal, cost or turns down by more than 10 %
  same quality, costlier     pass rate equal, cost or turns up by more than 10 %
  no measurable change       otherwise

With few attempts per task, small differences are noise: use --repeat 3 or more
before trusting a single-step change.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

THRESHOLD = 0.10


def _rel_change(base: float | None, head: float | None) -> float | None:
    if base in (None, 0) or head is None:
        return None
    return (head - base) / base


def verdict(b: dict, h: dict) -> str:
    if h["pass_rate"] > b["pass_rate"]:
        return "better"
    if h["pass_rate"] < b["pass_rate"]:
        return "worse"
    for key in ("avg_cost_usd", "avg_turns"):
        change = _rel_change(b.get(key), h.get(key))
        if change is not None and change < -THRESHOLD:
            return "same quality, cheaper"
        if change is not None and change > THRESHOLD:
            return "same quality, costlier"
    return "no measurable change"


def compare(base: dict, head: dict) -> tuple[str, bool]:
    bt, ht = base["summary"]["tasks"], head["summary"]["tasks"]
    lines = [
        f"### Baseline {base['meta']['baseline_version']} → {head['meta']['baseline_version']}",
        "",
        "| Task | Before | After | Avg turns | Verdict |",
        "|---|---|---|---|---|",
    ]
    regression = False
    for tid in sorted(set(bt) | set(ht)):
        if tid not in bt or tid not in ht:
            lines.append(f"| {tid} | {'–' if tid not in bt else 'ok'} | {'–' if tid not in ht else 'ok'} | | new or removed task |")
            continue
        b, h = bt[tid], ht[tid]
        v = verdict(b, h)
        regression |= v == "worse"
        turns = f"{b.get('avg_turns') or '–'} → {h.get('avg_turns') or '–'}"
        lines.append(f"| {tid} | {b['passes']}/{b['attempts']} | {h['passes']}/{h['attempts']} | {turns} | {v} |")

    bp, hp = base["summary"]["pass_rate"], head["summary"]["pass_rate"]
    if hp > bp:
        overall = f"**Better:** pass rate {bp:.0%} → {hp:.0%}."
    elif hp < bp:
        overall = f"**Worse:** pass rate {bp:.0%} → {hp:.0%}. Do not roll out."
    else:
        overall = f"**Different, not better:** pass rate unchanged at {hp:.0%}."
    if regression and hp >= bp:
        overall += " Note: at least one task regressed."
    return "\n".join(lines + ["", overall]) + "\n", regression


def main() -> None:
    # Markdown output contains non-ASCII (→, –); Windows pipes default to cp1252.
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("base")
    parser.add_argument("head")
    parser.add_argument("--md", help="append the markdown table here")
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args()

    base = json.loads(Path(args.base).read_text(encoding="utf-8"))
    head = json.loads(Path(args.head).read_text(encoding="utf-8"))
    md, regression = compare(base, head)
    print(md)
    if args.md:
        with open(args.md, "a", encoding="utf-8") as fh:
            fh.write(md + "\n")
    if args.fail_on_regression and regression:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
