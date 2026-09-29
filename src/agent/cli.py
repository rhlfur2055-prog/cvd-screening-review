"""Semi-automated literature agent.  uv run python -m src.agent.cli <command>

  collect [PMID ...]   fetch abstracts/OA status (default: PMIDs from data/claims.json)
  search "query"       list candidate PMIDs (human decides what to add)
  verify               check every claim in data/claims.json against abstracts
  panel [--run]        build reviewer prompts (or call the API with --run)

Human gates (deliberately NOT automated): choosing papers, reading full texts for
'unverified' claims, running/accepting reviews, revising the manuscript.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import collect, panel, verify

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str]) -> None:
    cmd, rest = (argv[0] if argv else "help"), argv[1:]
    if cmd == "collect":
        pmids = rest or sorted({c["pmid"] for c in json.loads((ROOT / "data" / "claims.json").read_text(encoding="utf-8"))})
        print("wrote", collect.run(pmids))
    elif cmd == "search":
        for pmid in collect.search(" ".join(rest)):
            print(pmid)
    elif cmd == "verify":
        out = verify.run()
        print(out.read_text(encoding="utf-8"))
        if "unverified" in out.read_text(encoding="utf-8"):
            print("\nHUMAN GATE: open the full text for the unverified rows above.")
    elif cmd == "panel":
        paths = panel.run_api() if "--run" in rest else panel.build()
        print("\n".join(str(p.relative_to(ROOT)) for p in paths))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
