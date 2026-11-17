"""post-docs: a read-only MCP server that gives the coding agent access to
internal engineering knowledge (conventions, business rules, guidelines).

In a real setup the same pattern connects Confluence, Backstage, Jira or an
internal API. The server is deliberately read-only: it can inform the agent,
not act on its behalf.

Run standalone:  python mcp_server/server.py   (stdio transport)
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from mcp.types import ToolAnnotations

try:  # mcp >= 2.0
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

DOCS_DIR = Path(os.environ.get("POST_DOCS_DIR", Path(__file__).parent / "docs")).resolve()
MAX_SNIPPET = 900
READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)

mcp = _Server("post-docs")


def _load_docs() -> dict[str, str]:
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted(DOCS_DIR.glob("*.md"))}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9äöüéèà]+", text.lower())


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _sections(text: str) -> list[tuple[str, str]]:
    """Split a markdown doc into (heading, body) sections at '## ' headings."""
    parts = re.split(r"^## ", text, flags=re.MULTILINE)
    sections = [("(intro)", parts[0])]
    for part in parts[1:]:
        heading, _, body = part.partition("\n")
        sections.append((heading.strip(), body))
    return sections


@mcp.tool(annotations=READ_ONLY)
def list_docs() -> list[dict]:
    """List all internal engineering documents with their titles."""
    return [{"name": name, "title": _title(text, name)} for name, text in _load_docs().items()]


@mcp.tool(annotations=READ_ONLY)
def search_docs(query: str, limit: int = 3) -> list[dict]:
    """Search internal engineering docs (API conventions, tariff rules,
    security guidelines). Use this before guessing any business rule."""
    terms = set(_tokens(query))
    if not terms:
        return []
    hits = []
    for name, text in _load_docs().items():
        for heading, body in _sections(text):
            words = _tokens(heading + " " + body)
            score = sum(words.count(t) for t in terms) + 3 * sum(t in _tokens(heading) for t in terms)
            if score:
                hits.append(
                    {"doc": name, "section": heading, "score": score, "snippet": body.strip()[:MAX_SNIPPET]}
                )
    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits[: max(1, min(limit, 10))]


@mcp.tool(annotations=READ_ONLY)
def get_doc(name: str) -> str:
    """Return the full text of one internal document by name (see list_docs)."""
    docs = _load_docs()
    if name not in docs:  # also prevents path traversal: only known names resolve
        raise ValueError(f"Unknown document '{name}'. Available: {', '.join(docs)}")
    return docs[name]


if __name__ == "__main__":
    mcp.run()
