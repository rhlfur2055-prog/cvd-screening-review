"""Step 2 (automatic): check each numeric claim against the fetched abstract.

A claim is `verified` only if its number string appears in the abstract. Anything
else is `unverified-in-abstract` (it may still be true in the full text, which a
human must open) — this is the no-fabricated-statistics gate.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run() -> Path:
    papers = {p["pmid"]: p for p in json.loads((ROOT / "data" / "papers.json").read_text(encoding="utf-8"))}
    claims = json.loads((ROOT / "data" / "claims.json").read_text(encoding="utf-8"))
    rows = []
    for c in claims:
        p = papers.get(c["pmid"], {})
        abstract = p.get("abstract", "")
        status = "verified" if p.get("found") and re.search(r"(?<![\d.,])" + re.escape(c["value"]) + r"(?![\d]|[.,]\d)", abstract.replace(",", "")) else "unverified-in-abstract"
        rows.append({**c, "status": status, "open_access": p.get("open_access"), "title": p.get("title")})
    out = ROOT / "results" / "claim_verification.md"
    with out.open("w", encoding="utf-8") as f:
        f.write("| Claim | Value | PMID | Status | Full text OA |\n|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['claim']} | {r['value']} | {r['pmid']} | {r['status']} | {r['open_access']} |\n")
    return out
