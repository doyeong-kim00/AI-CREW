# 원가 차이 관리 앱 — 하이젠알앤엠 기업과제

국립창원대 AIX CREW 2026 · 과제 01 제품별 원가 흐름 분석 · 원가 관리 모델

기종별로 한 대 만드는 원가가 달마다 어떻게 변하는지 보여주고, 견적보다 돈이 더(덜) 든 프로젝트를 금액 큰 순서로 세워
그 차이가 **재료를 더 써서인지 · 재료값이 올라서인지 · 그 밖의 이유인지** 나눠 보여주는 반응형 웹 앱.

> 모든 숫자는 시연용 **가상 데이터**입니다. 원인은 담당자가 확정합니다.

## 바이브 코딩 5단계 진행 상황
| 단계 | 파일 | 상태 |
|---|---|---|
| 1 기획에서 코드로 | [intent.md](intent.md), [CLAUDE.md](CLAUDE.md) | 완료 |
| 2 spec 고정 | [docs/spec.md](docs/spec.md), [정답.md](정답.md) | 완료 (중간점검 1 반영) |
| 3 Plan Mode | [docs/plan.md](docs/plan.md) | 승인 |
| 4 한 조각씩 | [index.html](index.html) | 조각 4/8 완료 (뼈대 + 디자인 C, 계산 엔진, 가상 데이터·예외, 프로젝트 목록 — 자가 검산 118/118) |
| 5 검증·시연 | [validation/](validation/), [ai-log/](ai-log/) | 조각마다 기록 중 |

## 실행
`index.html`을 브라우저로 열면 됩니다. 서버·설치 필요 없음.

## 검증 방법
| 방법 | 하는 법 | 무엇을 보나 |
|---|---|---|
| 자가 검산 | 앱 → 설정 탭, 또는 `index.html?selftest` | [정답.md](정답.md) 예시 A~I + 가상 데이터 점검 통과 수 |
| 가로 넘침 검사 | `index.html?layoutcheck` | 왼쪽 위 `overflow=false` |
| 무작위 교차 비교 | `python validation/tools/diffcheck.py index.html 결과.html` → 결과.html 열기 | 파이썬 독립 구현과 계산 엔진이 7,501항목 일치하는지 |
| 가상 데이터 통계 | `python validation/tools/datastats.py index.html 통계.html` → 통계.html 열기 | 확인 필요 분포, 기종 주의, 시연 이야기가 나오는지 |

점검 기록: [validation/](validation/) · AI 사용 기록: [ai-log/](ai-log/)

## 원본 기획서
[하이젠알앤엠_최종기획서_v2.pdf](하이젠알앤엠_최종기획서_v2.pdf)
