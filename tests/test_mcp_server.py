import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_server"))
import server  # noqa: E402


def test_list_docs_has_titles():
    names = {d["name"]: d["title"] for d in server.list_docs()}
    assert {"api-conventions", "tariff-guideline", "security-guideline"} <= set(names)
    assert names["tariff-guideline"].startswith("Tariff Guideline")


def test_search_finds_saturday_surcharge():
    hits = server.search_docs("saturday delivery surcharge")
    assert hits[0]["doc"] == "tariff-guideline"
    assert "4.80" in hits[0]["snippet"]


def test_search_finds_validation_rules():
    hits = server.search_docs("zip code validation")
    assert any("four digits" in h["snippet"] for h in hits)


def test_search_limit_and_empty_query():
    assert len(server.search_docs("parcels", limit=1)) == 1
    assert server.search_docs("   ") == []


def test_get_doc_rejects_unknown_and_traversal():
    assert "CHF 4.80" in server.get_doc("tariff-guideline")
    with pytest.raises(ValueError):
        server.get_doc("../server")


def test_tools_are_registered_over_mcp():
    tools = asyncio.run(server.mcp.list_tools())
    assert {t.name for t in tools} == {"list_docs", "search_docs", "get_doc"}
