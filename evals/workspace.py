"""Build a fresh workspace: the sample service plus an agent baseline.

Used by the eval runner and by scripts/new_workspace.py for the live demo.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = REPO_ROOT / "sample_service"
MCP_SERVER = REPO_ROOT / "mcp_server" / "server.py"
MCP_DOCS = REPO_ROOT / "mcp_server" / "docs"
DEFAULT_BASELINE = REPO_ROOT / "agent-baseline"

_IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc", "audit.jsonl")


def write_mcp_config(dest: Path) -> Path:
    """Point the workspace at the post-docs MCP server via absolute paths, so the
    docs are reachable only through MCP and not as files inside the workspace."""
    config = {
        "mcpServers": {
            "post-docs": {
                "command": sys.executable,
                "args": [str(MCP_SERVER)],
                "env": {"POST_DOCS_DIR": str(MCP_DOCS)},
            }
        }
    }
    path = dest / ".mcp.json"
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return path


def create_workspace(dest: Path, baseline: Path = DEFAULT_BASELINE) -> Path:
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError(f"{dest} exists and is not empty")
    shutil.copytree(SERVICE_DIR, dest, ignore=_IGNORE, dirs_exist_ok=True)
    shutil.copy2(baseline / "CLAUDE.md", dest / "CLAUDE.md")
    shutil.copytree(baseline / ".claude", dest / ".claude", ignore=_IGNORE)
    write_mcp_config(dest)
    (dest / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n.claude/audit.jsonl\n.env\n", encoding="utf-8")
    _git_init(dest)
    return dest


def _git_init(dest: Path) -> None:
    git = shutil.which("git")
    if not git:
        return
    run = lambda *a: subprocess.run([git, *a], cwd=dest, capture_output=True, check=False)  # noqa: E731
    run("init", "-q")
    run("add", "-A")
    run("-c", "user.name=eval", "-c", "user.email=eval@example.invalid", "commit", "-q", "-m", "baseline")
