"""Step 3 (semi-automatic): reviewer panel with independent context per reviewer.

Each reviewer sees ONLY: the manuscript, the claim-verification table, and its own
persona — never the other reviews (independence protocol). Two modes:
  * prompts (default): writes reviews/prompts/<id>.md; a human runs each in a fresh
    Claude session and saves the answer to reviews/<id>.md.
  * --run: calls the Anthropic API (needs ANTHROPIC_API_KEY and `uv sync --extra llm`).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = "claude-sonnet-5-5"
TEMPLATE = """당신은 논문 리뷰어입니다. 역할: {persona}

규칙:
- 아래 원고와 수치 검증표만 근거로 판단한다. 다른 리뷰어의 의견은 볼 수 없다.
- 출처 없는 통계는 지적한다. 검증표에서 'unverified-in-abstract'인 값은 원문 확인 전까지 근거로 인정하지 않는다.
- 형식: 첫 줄에 판정(Accept / Minor Revision / Major Revision / Reject), 이어서 번호 매긴 구체적 지적. 칭찬은 한 줄 이내.

## 수치 검증표
{verification}

## 원고
{manuscript}
"""


def build() -> list[Path]:
    personas = json.loads((Path(__file__).parent / "personas.json").read_text(encoding="utf-8"))
    ms = (ROOT / "paper" / "main.md").read_text(encoding="utf-8")
    ver = (ROOT / "results" / "claim_verification.md").read_text(encoding="utf-8")
    out_dir = ROOT / "reviews" / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for rid, persona in personas.items():
        p = out_dir / f"{rid}.md"
        p.write_text(TEMPLATE.format(persona=persona, verification=ver, manuscript=ms), encoding="utf-8")
        paths.append(p)
    return paths


def run_api(outdir: str = "reviews/auto") -> list[Path]:
    import anthropic  # optional dependency

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY not set — use prompt mode instead.")
    client = anthropic.Anthropic()
    dest = ROOT / outdir
    dest.mkdir(parents=True, exist_ok=True)
    outs = []
    for p in build():
        msg = client.messages.create(model=MODEL, max_tokens=2000, messages=[{"role": "user", "content": p.read_text(encoding="utf-8")}])
        o = dest / p.name
        o.write_text(msg.content[0].text, encoding="utf-8")
        outs.append(o)
    return outs
