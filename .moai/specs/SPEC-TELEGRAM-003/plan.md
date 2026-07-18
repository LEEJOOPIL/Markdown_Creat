---
id: SPEC-TELEGRAM-003
title: "텔레그램 봇 Windows 더블클릭 실행기 — 구현 계획"
version: "0.1.1"
status: completed
created: 2026-07-18
updated: 2026-07-18
author: manager-spec
priority: P2
phase: "v0.1.0 target"
module: "run_telegram_bot.bat"
lifecycle: spec-anchored
tags: "telegram, bot, launcher, windows, batch, ux"
depends_on: [SPEC-TELEGRAM-001]
tier: M
---

# SPEC-TELEGRAM-003 — 구현 계획 (plan.md)

## §A. 컨텍스트 (Context)

`SPEC-TELEGRAM-001`(status: completed)로 구현된 텔레그램 봇을 더블클릭으로 실행할 수 있는 Windows `.bat` 실행기(`run_telegram_bot.bat`) 1개 파일을 프로젝트 루트에 추가한다. 봇 코어 로직·토큰 로딩 로직은 전혀 수정하지 않는 순수 실행기 레이어 추가이므로, 분석할 기존 Python 코드 변경 사항이 없다. Tier M(감사 가능성을 위해 `acceptance.md` 별도 유지 — 근거: fail-fast·콘솔 유지 계약은 사용자가 직접 눈으로 검증해야 하는 UX 계약이라 시나리오별 추적이 유용함, `SPEC-TELEGRAM-001`/`002`와 동일 관례).

**의존성 확인**: `depends_on: [SPEC-TELEGRAM-001]`. `SPEC-TELEGRAM-001`은 `status: completed`이며 `python -m markdown_creat.telegram_bot`이 유효한 실행 진입점임을 확인했다(2026-07-18, `src/markdown_creat/telegram_bot/__main__.py`). `/moai run` 시 Depends_on Pre-flight Check는 통과할 것으로 예상된다.

## §B. PRESERVE / EXTEND

- **PRESERVE**: `src/markdown_creat/telegram_bot/` 패키지 전체(봇 코어 로직, `config.py`의 `load_bot_token()`/`MissingBotTokenError`/`mask_secret()` 포함) — 본 SPEC은 이 코드를 전혀 수정하지 않는다. `.venv/` 자체의 구성이나 `pyproject.toml`의 의존성 목록도 변경하지 않는다.
- **EXTEND**: 프로젝트 루트에 신규 파일 `run_telegram_bot.bat` 1개만 추가한다. README.md에 실행기 사용법을 한두 줄 언급하는 것은 선택적(M6, non-blocking)이며 본 SPEC의 필수 산출물이 아니다.

## §C. 기술 접근 (Technical Approach)

- **작업 디렉토리 앵커링**: 배치 스크립트 최상단에서 `cd /d "%~dp0"`(또는 동등한 관용구)로 스크립트 자신의 위치로 이동한다. `%~dp0`는 배치 확장 변수로 스크립트 파일의 드라이브+경로를 가리킨다 — 사용자가 바탕화면 바로가기나 다른 디렉토리에서 실행해도 항상 프로젝트 루트를 기준으로 동작하게 한다(REQ-TELEGRAM-025).
- **venv 사전 점검**: `cd /d` 앵커링 **이후**, `.venv\Scripts\python.exe`의 존재 여부를 `if not exist` 조건으로 검사한다. 존재하지 않으면 평이한 언어의 오류 메시지(예: "가상환경(.venv)을 찾을 수 없습니다. README를 참고해 먼저 `python -m venv .venv`로 생성해 주세요.")를 출력하고, `pause` 후 0이 아닌 코드로 종료한다 — 봇 모듈은 호출하지 않으며, 가공되지 않은 원시 Python 트레이스백이 유일한 실패 신호가 되지 않도록 한다(REQ-TELEGRAM-027, REQ-TELEGRAM-031, REQ-TELEGRAM-035).
- **봇 호출**: venv 존재가 확인되면 `".venv\Scripts\python.exe" -m markdown_creat.telegram_bot`을 실행한다. 출력 리다이렉트나 스트림 억제는 하지 않는다 — Python 프로세스의 표준출력/표준오류(시작 로그, 또는 `MissingBotTokenError` 트레이스백)가 그대로 같은 콘솔 창에 나타나야 한다(REQ-TELEGRAM-026, REQ-TELEGRAM-029, REQ-TELEGRAM-030).
- **콘솔 유지**: 모든 종료 경로(venv 부재 fail-fast 경로, 봇 프로세스가 정상/비정상으로 끝난 이후) 끝에 `pause`(또는 동등한 대기 명령)를 배치하여, 사용자가 키를 누르기 전까지 콘솔 창이 닫히지 않게 한다(REQ-TELEGRAM-028, REQ-TELEGRAM-032).
- 인코딩은 BOM 없는 형식으로 저장하고, 콘솔 코드페이지는 선택적으로 `chcp 65001 > nul`을 스크립트 시작부에 추가하는 것을 권장 관행으로 남긴다(강제 아님, §Exclusions "콘솔 유니코드/코드페이지 완전 대응" 참조).

## §D. 마일스톤 (결정 번복 가능성 순 — 변경 가능성 높은 결정 우선)

> UX·메시지 문구 같은 변경 가능성이 높은 결정을 먼저 배치하고, 수동 검증·문서화 같은 기계적 단계는 뒤로 미룬다.

### M1 (Priority High) — UX 흐름 및 오류 메시지 문구 확정 (변경 가능성 최상)
- 파일명 확정: `run_telegram_bot.bat` (프로젝트 루트).
- venv 부재 오류 메시지의 정확한 문구와 언어(한국어/영어) 확정 — `code_comments: ko` 설정을 참고하되, 최종 문구는 사용자에게 노출되는 실행기 UX이므로 재검토 가능. `acceptance.md` AC-TELEGRAM-027a는 정확한 문구를 요구하지 않고 "누락 구성요소(.venv)를 평이한 언어로 명시"라는 관찰 가능한 조건만 요구하므로, 본 M1에서 문구를 자유롭게 결정해도 인수 기준과 충돌하지 않는다(plan-audit iteration 1 D3 반영).
- 정상 실행 시 콘솔에 어떤 안내 문구(예: "봇을 시작합니다...")를 표시할지, 표시하지 않고 Python 자체 로그만 노출할지 결정.
- 이 결정들은 REQ-TELEGRAM-024, 027, 029에 직접 영향을 미치며 사용자 피드백에 따라 가장 먼저 바뀔 가능성이 높다.

### M2 (Priority High) — venv 사전 점검 / fail-fast 분기 설계
- `if not exist ".venv\Scripts\python.exe"` 검사 로직과 실패 시 종료 코드(`exit /b 1` 등) 확정.
- fail-fast 분기가 `cd /d` 앵커링 **이후**에 상대 경로로 검사됨을 보장(§C 기술 접근 참조 — 순서가 바뀌면 실행 위치에 따라 오탐 가능).
- REQ-TELEGRAM-027, 031, 035 대응.

### M3 (Priority Medium) — cwd 앵커링 + 봇 호출 커맨드 작성 (기계적)
- `cd /d "%~dp0"` 앵커링 라인 작성.
- `".venv\Scripts\python.exe" -m markdown_creat.telegram_bot` 호출 라인 작성, 출력 리다이렉트 없음을 확인.
- REQ-TELEGRAM-025, 026, 030 대응.

### M4 (Priority Medium) — 콘솔 유지(pause) 로직 작성 (기계적)
- 모든 종료 경로(fail-fast 경로 + 봇 프로세스 종료 후 경로) 끝에 `pause` 배치.
- REQ-TELEGRAM-028, 029, 032 대응.

### M5 (Priority Low) — 수동 검증 (Windows 환경, 기계적/검증 단계)
- `acceptance.md`의 3개 실행 시나리오(AC-TELEGRAM-024a/027a/027b: 정상 실행, venv 부재, 토큰 부재)를 실제 Windows 환경에서 더블클릭으로 재현하여 수동 검증한다.
- `acceptance.md`의 3개 정적 스크립트 검토 시나리오(AC-TELEGRAM-030s/033s/034s: bare `python` 미사용, OS 자동 시작 미등록, 포그라운드 전용 실행)를 코드 리뷰로 검증하며, AC-TELEGRAM-034s는 추가로 작업 관리자(Task Manager)에서 봇 프로세스가 콘솔 창의 자식 프로세스임을 관찰로 확인한다.
- 실행 위치 독립성(바탕화면 바로가기 vs 프로젝트 루트 직접 실행 vs 다른 디렉토리에서 실행)도 함께 검증한다.

### M6 (Priority Low) — README 언급 (선택적, 기계적)
- `README.md`에 `run_telegram_bot.bat` 실행기 사용법을 한두 줄 추가하는 것은 선택적이며 본 SPEC의 완료 조건이 아니다. 시간이 허락하면 수행한다.

## §E. 리스크 (Risks)

- **[검증 도구 부재] `.bat` 파일은 pytest/ruff/black 대상이 아님**: 본 프로젝트의 기본 개발 방법론(`quality.yaml` `development_mode: tdd`)은 Python 소스 코드를 전제로 한 RED-GREEN-REFACTOR 자동화 테스트를 가정하지만, 배치 스크립트에는 이 도구 체인이 적용되지 않는다. 완화: `acceptance.md`의 EARS/GEARS 인수 시나리오(실행 시나리오 3개 + 정적 스크립트 검토 시나리오 3개)를 수동 회귀 테스트 절차로 명시하고, 향후 스크립트가 수정될 때마다 재실행하도록 한다.
- **[순서 오류] cwd 앵커링 전에 venv 검사를 수행하면 오탐/미탐 발생**: `cd /d` 이전에 상대 경로로 `.venv\Scripts\python.exe`를 검사하면 실행 위치에 따라 결과가 달라질 수 있다. 완화: M2에서 앵커링 이후 검사 순서를 명시적으로 고정하고 M5에서 여러 실행 위치로 검증한다.
- **[조기 종료] pause 이전에 스크립트 오류로 창이 닫힐 가능성**: 배치 스크립트 자체의 구문 오류나 예상치 못한 조기 종료 경로가 있으면 `pause`에 도달하지 못해 창이 즉시 닫힐 수 있다. 완화: M5에서 정상/venv 부재/토큰 부재 3가지 경로 모두를 실제로 실행해 창이 닫히지 않음을 눈으로 확인한다.
- **[가독성] `MissingBotTokenError` 트레이스백이 장황하여 핵심 메시지가 묻힐 가능성**: Python 예외 트레이스백은 여러 줄로 출력되며 핵심 오류 메시지가 스크롤되어 잘 보이지 않을 수 있다. 완화: 출력을 가로채거나 축약하지 않는다(REQ-TELEGRAM-029) — 트레이스백 자체를 축약/재가공하는 것은 `config.py`를 건드리지 않는다는 PRESERVE 제약과 충돌하므로 본 SPEC에서는 다루지 않는다(가공 없는 원문 노출이 fail-fast 철학과 일치).
- **[플랫폼 제약] Windows 전용, 크로스플랫폼 검증 불가**: 개발/리뷰 환경이 non-Windows일 경우 실제 더블클릭 검증이 불가능할 수 있다. 완화: `cmd.exe` 문법 규칙(예: `%~dp0`, `if not exist`, `pause`)은 잘 알려진 표준 관용구이므로 코드 리뷰로 상당 부분 검증 가능하며, 최종 M5는 Windows 환경에서 수행되어야 한다.

## §F. 참조

- `spec.md` (요구사항 SSOT), `acceptance.md` (인수 시나리오), `spec-compact.md` (요약본)
- 의존 SPEC(실행 대상 봇, 실행 스크립트 경로 예고): `.moai/specs/SPEC-TELEGRAM-001/spec.md`
- 관련 SPEC(동일 모듈 선행 수정, Tier M 구조 선례): `.moai/specs/SPEC-TELEGRAM-002/spec.md`
- 대상 파일(신규): `run_telegram_bot.bat` (프로젝트 루트)
- 참조 대상(수정 없음): `src/markdown_creat/telegram_bot/__main__.py`, `src/markdown_creat/telegram_bot/config.py`
