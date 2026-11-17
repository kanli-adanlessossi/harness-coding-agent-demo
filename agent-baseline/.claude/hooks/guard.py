#!/usr/bin/env python3
"""PreToolUse guard hook for the coding agent.

Claude Code runs this before every Bash, Write, Edit and MultiEdit call and passes
the tool call as JSON on stdin. Exit code 2 blocks the call; the message on stderr
is shown to the agent so it can choose a safer path. Exit code 0 allows it.

Blocked:
  * secrets in file content (API keys, private keys, password assignments)
  * writing .env files
  * destructive or risky shell commands (rm -rf, force push, curl | sh, --no-verify)

Every block is appended to .claude/audit.jsonl (without the offending content).
Fails closed: if the input cannot be parsed, the call is blocked.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9_\-]{16,}", "API key (sk-...)"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"gh[pousr]_[A-Za-z0-9]{30,}", "GitHub token"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "private key"),
    (
        r"(?i)\b(?:api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*[\"'][^\"'\s]{12,}[\"']",
        "hardcoded credential assignment",
    ),
]

DANGEROUS_COMMANDS = [
    (r"\brm\s+(?:-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|--recursive\s+--force|--force\s+--recursive)\b", "recursive force delete"),
    (r"\bgit\s+push\b.*(?:\s--force\b|\s-f\b|\s--force-with-lease\b)", "force push"),
    (r"\b(?:curl|wget)\b[^|]*\|\s*(?:sudo\s+)?(?:ba|z)?sh\b", "piping a download into a shell"),
    (r"\bgit\s+commit\b.*--no-verify", "skipping commit hooks"),
    (r"\bchmod\s+(?:-R\s+)?777\b", "world-writable permissions"),
]

ENV_FILE = re.compile(r"(^|/)\.env(\.[\w-]+)?$")


def _audit(tool: str, reason: str) -> None:
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    log = project / ".claude" / "audit.jsonl"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "tool": tool,
                "decision": "block",
                "reason": reason,
            }) + "\n")
    except OSError:
        pass  # auditing must never break the agent


def _block(tool: str, reason: str, advice: str) -> None:
    _audit(tool, reason)
    print(f"Blocked by guard hook: {reason}. {advice}", file=sys.stderr)
    sys.exit(2)


def _written_text(tool: str, tool_input: dict) -> str:
    if tool == "Write":
        return tool_input.get("content", "")
    if tool == "Edit":
        return tool_input.get("new_string", "")
    if tool == "MultiEdit":
        return "\n".join(e.get("new_string", "") for e in tool_input.get("edits", []))
    return ""


def check(event: dict) -> tuple[str, str] | None:
    """Return (reason, advice) if the tool call must be blocked, else None."""
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input", {}) or {}

    if tool == "Bash":
        command = tool_input.get("command", "")
        for pattern, label in DANGEROUS_COMMANDS:
            if re.search(pattern, command):
                return label, "Ask the human to do this, or find a non-destructive alternative."
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, command):
                return f"{label} in a shell command", "Reference the environment variable instead."
        return None

    if tool in {"Write", "Edit", "MultiEdit"}:
        path = tool_input.get("file_path", "")
        if ENV_FILE.search(path):
            return "writing a .env file", (
                "Secrets are set outside the repository. Read them via app/config.py "
                "from environment variables and tell the user which variable to set."
            )
        text = _written_text(tool, tool_input)
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, text):
                return f"{label} in {path or 'file'}", (
                    "Never hardcode secrets. Read the value from an environment variable "
                    "in app/config.py and tell the user which variable to set."
                )
    return None


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        _block("unknown", "unreadable hook input", "Guard fails closed; retry the action.")
        return
    verdict = check(event)
    if verdict:
        _block(event.get("tool_name", "unknown"), *verdict)
    sys.exit(0)


if __name__ == "__main__":
    main()
