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

## 로드맵: 계산에서 실측 기반 논문으로

이 저장소는 현재 **발표된 수치의 결합 분석**입니다. 강의형 논문(표의 모든 값을 직접 돌려 얻는 실험 논문)으로 가기 위해 필요한 자료 경로와 진행 상태입니다. 표의 "확인됨"은 실제로 조회한 것만 적었습니다.

### 1. 논문 전문 확보

| 경로 | 용도 | 상태 |
|---|---|---|
| Europe PMC REST API | 오픈액세스 여부·PMCID 조회, 전문 XML 수집 | 인용한 5편 조회 완료 — **5편 모두 오픈액세스 아님(PMCID 없음)**. 전문 자동 수집은 불가, 초록·메타데이터만 사용 |
| OpenAlex / Semantic Scholar API | 관련 문헌 검색, 인용 관계 수집 | 미구현 |
| arXiv | 프리프린트 검색 | 이 주제와 관련성 낮음, 미구현 |

전문이 막힌 논문의 수치는 초록 또는 유료 접근으로 직접 확인한 값만 쓰고, 확인하지 못한 값은 논문 2.2절처럼 가정으로 표시합니다.

### 2. 원시 데이터 (실측 유병률·모델 실험)

| 데이터 | 용도 | 상태 |
|---|---|---|
| 국민건강영양조사(KNHANES, 질병관리청) | 색각 검사 항목이 있으면 유병률을 직접 산출해 현재의 인용값 대체 | 회원가입·이용동의 필요. **색각 항목 포함 연도 미확인** |
| Kaggle / UCI / Zenodo / OpenML | 표 형태 데이터로 여러 모델을 돌려 비교하는 실험 논문 | 주제 미정 |

원칙: 표에는 코드를 돌려 나온 값만 넣습니다. 원시 데이터가 없는 항목은 만들지 않고 "가정"으로 남깁니다.

### 3. 연구 에이전트 (반자동)

강의 구조(Skill → Subagents → Hooks/Loop/MCP)에 맞춰 `.claude/`와 `src/agent/`에 구현했습니다. **사람이 결정하는 단계(논문 선택, 전문 확인, 결론 문장 변경)는 일부러 자동화하지 않았습니다.**

| 강의 파트 | 이 저장소 | 상태 |
|---|---|---|
| P1 논문 읽기 Skill | `.claude/skills/paper-reader/` (절차·스키마·판단 기준) | 작성됨, 실사용 검증 전 |
| P1 실험 로그 Skill + 품질 규칙 | `.claude/skills/experiment-log/` | 작성됨, 실사용 검증 전 |
| P2 Subagents | `.claude/agents/` — literature-reviewer, experiment-planner, critical-reviewer, writing-reviewer | 정의됨, 자동 실행 검증 전 |
| P3 Hooks | `.claude/settings.json` + `.claude/hooks/` — 수치 게이트(claims 수정 시 재검증), 생성 파일 수동 수정 차단 | 훅 스크립트 단독 실행 테스트 완료(종료코드 확인). Claude Code 안에서의 실제 발동은 미확인 |
| P3 Loop | `.claude/commands/research-loop.md` (종료 조건 3개, 사람 게이트) | 정의됨, 실행 안 해봄 |
| P3 MCP | `.mcp.json` + `src/agent/mcp_server.py` (search_papers, get_paper, verify_claims) | 도구 3개 등록 확인, Claude Code 연결은 미확인 |

**실제로 자동 동작하는 것** (`uv run python -m src.agent.cli <명령>`)

| 명령 | 동작 |
|---|---|
| `collect` | Europe PMC에서 초록·오픈액세스 여부를 받아 `data/papers.json` 저장 |
| `verify` | `data/claims.json`의 각 수치가 초록에 있는지 대조 → `results/claim_verification.md` |
| `search "질의"` | 후보 PMID 목록 (선택은 사람) |
| `panel` | 리뷰어별 독립 프롬프트 생성. `--run`은 `ANTHROPIC_API_KEY`가 있을 때만 API 호출(키 없음, **실행해 본 적 없음**) |

**수치 게이트가 실제로 잡은 것**: 첫 검증에서 `TV-plate sensitivity upper bound = 99`가 `unverified`로 나왔습니다. 초록은 "99.0%"로 표기했기 때문이며, 값을 `99.0`으로 고치자 통과했습니다. 같은 초록은 95.5%가 "8오류 기준", 99.0%가 "3오류 기준"임도 밝히고 있어 논문 표에 조건을 추가했습니다.

**아직 없는 것**: 문헌 요약의 LLM 자동화, 리뷰어 패널 API 실행 결과, KNHANES 실측 데이터.
