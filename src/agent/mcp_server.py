"""Local MCP server exposing the literature tools (Part 3, Phase 3).

Tools: search_papers, get_paper, verify_claims. Read-only; no network writes.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import collect, verify

mcp = FastMCP("cvd-literature")


@mcp.tool()
def search_papers(query: str, n: int = 10) -> list[str]:
    """Europe PMC free-text search; returns PMIDs (a human decides which to keep)."""
    return collect.search(query, n)


@mcp.tool()
def get_paper(pmid: str) -> dict:
    """Title, journal, year, abstract, open-access status for one PMID."""
    return collect.fetch(pmid)


@mcp.tool()
def verify_claims() -> str:
    """Check every claim in data/claims.json against fetched abstracts; returns a markdown table."""
    return verify.run().read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
