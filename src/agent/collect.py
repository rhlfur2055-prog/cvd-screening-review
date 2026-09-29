"""Step 1 (automatic): fetch metadata + abstract + open-access status from Europe PMC."""
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def fetch(pmid: str) -> dict:
    r = requests.get(API, params={"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "core"}, timeout=30)
    r.raise_for_status()
    hits = r.json()["resultList"]["result"]
    if not hits:
        return {"pmid": pmid, "found": False}
    h = hits[0]
    return {
        "pmid": pmid, "found": True, "title": h.get("title"), "journal": h.get("journalTitle"),
        "year": h.get("pubYear"), "pmcid": h.get("pmcid"), "open_access": h.get("isOpenAccess") == "Y",
        "abstract": h.get("abstractText", ""), "doi": h.get("doi"),
    }


def search(query: str, n: int = 10) -> list[str]:
    """Return PMIDs for a free-text query (candidate discovery; human picks which to keep)."""
    r = requests.get(API, params={"query": f"({query}) AND SRC:MED", "format": "json", "pageSize": n, "resultType": "lite"}, timeout=30)
    r.raise_for_status()
    return [h["pmid"] for h in r.json()["resultList"]["result"] if "pmid" in h]


def run(pmids: list[str]) -> Path:
    out = ROOT / "data" / "papers.json"
    out.parent.mkdir(exist_ok=True)
    papers = [fetch(p) for p in pmids]
    out.write_text(json.dumps(papers, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
