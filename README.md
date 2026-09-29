# 색각 이상 자가 테스트는 얼마나 믿을 수 있는가

발표된 유병률·검사 성능 수치를 베이즈 규칙으로 결합해, 색각 자가 테스트의 양성예측도(PPV)·놓침·오경보를 계산한 문헌 기반 분석입니다.

**새 실험 데이터는 없습니다.** 입력값은 모두 PubMed 확인 논문(`paper/main.md` 참고문헌)이고, 출처 없는 값은 가정(†)으로 표시했습니다.

| 산출물 | 위치 |
|---|---|
| 논문 (MD / PDF) | `paper/main.md`, `paper/cvd-screening-review.pdf` |
| 발표 슬라이드 | `slides/cvd-screening-review.pptx` |
| 5인 리뷰어 패널 + 종합 | `reviews/` |
| 분석 코드·결과표·그림 | `src/analysis.py`, `results/`, `figures/` |

## 재현

```bash
uv sync
uv run src/analysis.py   # 결과표·그림 재생성
uv run playwright install chromium
uv run src/build.py      # PDF·PPTX 재생성
```

## 리뷰어 패널에 대한 고지

`reviews/`의 5인 패널은 AI가 페르소나(방법론·공정성·도메인·회의적 독자·글쓰기)를 시뮬레이션한 **자체 점검**입니다. 외부 동료 심사가 아닙니다. 지적 사항과 반영 내역은 `reviews/review_synthesis.md`에 있습니다.

## 한계

인쇄판 특이도(.95)와 앱 민감도(.955)는 가정이며, 유병률과 검사 성능은 서로 다른 집단에서 왔습니다. 자세한 내용은 논문 4.1절. 이 자료는 의료 조언이 아니며 확진은 안과 검사가 필요합니다.
