#!/usr/bin/env python3
"""Create a ready-to-use demo workspace: sample service + agent baseline + MCP config.

  python scripts/new_workspace.py ~/demo-ws
  cd ~/demo-ws && claude
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
from workspace import DEFAULT_BASELINE, create_workspace  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("dest")
parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))
args = parser.parse_args()

ws = create_workspace(Path(args.dest).expanduser(), Path(args.baseline))
print(f"Workspace ready: {ws}\nNext: cd {ws} && claude")
