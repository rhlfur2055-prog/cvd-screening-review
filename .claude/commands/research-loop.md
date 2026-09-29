---
description: 읽기→실행→평가→수정 연구 루프를 최대 3회 돌린다
---

연구 루프를 실행한다. 한 회차는 아래 5단계다. **종료 조건**을 매 회차 끝에 검사한다.

1. **읽기**: `literature-reviewer` 서브에이전트로 `data/claims.json`의 미검증 수치를 확인한다.
2. **실행**: `uv run src/analysis.py` → `uv run python -m src.agent.cli verify`.
3. **평가**: `critical-reviewer`와 `writing-reviewer`를 각각 별도 서브에이전트로 실행한다(서로의 결과를 넘기지 않는다). 결과는 `reviews/loop/<회차>_<이름>.md`에 저장.
4. **정리**: `experiment-log` 스킬로 `results/EXPERIMENT_LOG.md`에 회차를 기록한다.
5. **수정**: Major 지적과 unverified 수치만 `paper/main.md`에 반영한다. 반영하지 않은 지적은 사유를 기록한다.

**종료 조건 (하나라도 만족하면 중단)**
- 모든 claim이 `verified`이고 두 리뷰어 판정이 Minor 이하
- 3회차 완료
- 같은 Major 지적이 2회 연속 반복됨 (사람 판단 필요 → 멈추고 보고)

**사람 게이트**: 새 논문을 근거로 추가하거나 결론 문장을 바꾸기 전에 사용자에게 확인한다.
