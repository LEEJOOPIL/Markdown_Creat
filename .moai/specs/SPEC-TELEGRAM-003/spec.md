---
id: SPEC-TELEGRAM-003
title: "텔레그램 봇 Windows 더블클릭 실행기 (.bat launcher)"
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

# SPEC-TELEGRAM-003 — 텔레그램 봇 Windows 더블클릭 실행기 (.bat launcher)

## HISTORY

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 0.1.0 | 2026-07-18 | manager-spec | 최초 초안 작성. `SPEC-TELEGRAM-001`(status: completed)로 구현된 텔레그램 봇(`python -m markdown_creat.telegram_bot`)을 터미널 없이 더블클릭만으로 실행할 수 있는 Windows `.bat` 실행기(`run_telegram_bot.bat`)를 정의한다. 실행 위치 독립성(cwd 앵커링), venv 전용 Python 호출, venv 부재 시 fail-fast, 콘솔 창 유지(pause) 4가지 핵심 계약을 EARS로 명세한다. OS 자동 시작/서비스 등록/백그라운드 데몬화는 명시적으로 범위 밖이며 `SPEC-TELEGRAM-001` §Exclusions의 기존 경계를 그대로 계승한다. Tier M(spec.md + plan.md + acceptance.md + progress.md — 실행기의 fail-fast·콘솔 유지 계약에 대한 감사 가능성을 위해 acceptance.md를 별도 유지, `SPEC-TELEGRAM-001`/`002`와 동일한 구조적 관례를 따름). 개발 방법론은 `quality.yaml`의 `constitution.development_mode: tdd`를 명목상 따르되, `.bat` 스크립트는 `pytest`/`ruff`/`black` 적용 대상이 아니므로 품질 게이트는 acceptance.md의 Given/When/Then 시나리오를 이용한 수동 검증으로 대체된다(상세: plan.md §E 리스크). |
| 0.1.1 | 2026-07-18 | manager-spec | plan-audit iteration 1 리뷰(`.moai/reports/plan-audit/SPEC-TELEGRAM-003-review-1.md`, verdict FAIL, score 0.67) 반영. (1) `acceptance.md` §D 헤더의 "GEARS / Given-When-Then" 이중 표기를 제거하고, 3개 AC(AC-TELEGRAM-024a/027a/027b)를 "Given" 없이 단일 절 EARS/GEARS 이벤트 기반(`When ..., the launcher shall ...`) 문장으로 재작성했다(D1, critical, Must-Pass Firewall). (2) REQ-TELEGRAM-030/033/034(부재-형 요구사항)에 대한 정적 스크립트 검토 기반 AC(AC-TELEGRAM-030s/033s/034s)를 `acceptance.md` §D에 신설하여 추적성 공백을 해소했다(D2, major). (3) AC-TELEGRAM-027a의 venv 부재 오류 메시지 판정 기준을 퍼지 매치("...류의") 대신 "누락 구성요소(.venv)를 평이한 언어로 명시하며 정확한 문구는 구현 시 결정"으로 재구성해 이진 테스트 가능성을 확보했다(D3, minor). (4) REQ-TELEGRAM-031(모듈 호출 금지 + 원시 트레이스백 단독 노출 금지 복합 요구사항)을 REQ-TELEGRAM-031(모듈 호출 금지)과 신규 REQ-TELEGRAM-035(원시 트레이스백 단독 노출 금지)로 분리했다 — 기존 REQ-024~034 순서를 보존하기 위해 말미에 REQ-035를 추가하는 방식을 택했다(renumbering 대신 append)(D4, minor, non-blocking). |

---

## §A. 개요 (Context)

`SPEC-TELEGRAM-001`(status: completed)로 구현된 텔레그램 → 마크다운 저장 봇은 `python -m markdown_creat.telegram_bot`으로 실행되며, long polling 방식의 상시 blocking 루프로 동작한다(REQ-TELEGRAM-001). `SPEC-TELEGRAM-001` §Exclusions는 "부팅 시 자동 시작, Windows 서비스 등록, 작업 스케줄러 연동은 구현하지 않는다. 봇은 수동 실행(`python -m ...` 또는 실행 스크립트)만 지원한다"고 명시하며, 같은 문서 §A는 "본 봇은 로컬/개인용으로, 수동 실행(`python -m ...` 또는 실행 스크립트)을 전제로 한다"고 이미 "실행 스크립트" 경로를 열어두었다. 본 SPEC은 그 열려 있던 "실행 스크립트" 경로를 구체화한다.

현재 봇을 실행하려면 사용자가 터미널을 열고 가상환경을 활성화한 뒤 명령을 직접 입력해야 한다. 이는 터미널 사용에 익숙하지 않은 사용자에게 진입 장벽이 된다. 본 SPEC은 **Windows 탐색기에서 더블클릭만으로 봇을 실행**할 수 있는 배치 파일(`.bat`) 실행기를 정의한다.

### 기존 인프라 (재사용 대상)

- 프로젝트 루트: `E:\Desktop\markdown_creat` (Windows, Python 3.10+, `src/` 레이아웃)
- 봇 진입점: `src/markdown_creat/telegram_bot/__main__.py`, `python -m markdown_creat.telegram_bot`으로 호출
- 가상환경: `.venv/` (Windows 경로: `.venv\Scripts\python.exe`) — 이미 프로젝트에 존재
- 봇 토큰 설정: 프로젝트 루트의 `.env` 파일(gitignored), `TELEGRAM_BOT_TOKEN` 키. `src/markdown_creat/telegram_bot/config.py`의 `load_bot_token()`이 환경변수를 `.env` 파일보다 우선 적용하며, 둘 다 없으면 `MissingBotTokenError`를 즉시 발생시켜 fail-fast한다(REQ-TELEGRAM-003, REQ-TELEGRAM-015 재사용 — 신규 재구현 없음).
- 봇은 long polling(상시 blocking 루프)으로 동작하며 스스로 데몬화하거나 백그라운드로 전환하지 않는다.

본 SPEC은 위 기존 인프라를 **그대로 재사용**하며, 봇 자체의 로직(`telegram_bot/` 패키지 내부)이나 토큰 로딩 로직(`config.py`)을 전혀 수정하지 않는다 — 순수하게 사용자가 기존 봇을 더 쉽게 "실행"할 수 있게 하는 실행기(launcher) 레이어를 프로젝트 루트에 추가할 뿐이다.

### 제안 파일명

`run_telegram_bot.bat` — 프로젝트 루트(`E:\Desktop\markdown_creat\run_telegram_bot.bat`)에 위치한다.

---

## §B. 요구사항 (EARS Requirements)

### 실행 트리거 (Launch)

- **REQ-TELEGRAM-024 (Ubiquitous)**: The launcher shall 프로젝트 루트에 더블클릭으로 실행 가능한 Windows `.bat` 파일(`run_telegram_bot.bat`)로 제공되며, 사용자가 터미널을 열거나 명령을 입력하지 않고도 텔레그램 봇을 시작할 수 있게 한다.
- **REQ-TELEGRAM-025 (Ubiquitous)**: The launcher shall 봇을 호출하기 전에, 실행된 위치(현재 작업 디렉토리)와 무관하게 자기 자신의 파일 위치로 작업 디렉토리를 고정(anchor)한다.
- **REQ-TELEGRAM-026 (Ubiquitous)**: The launcher shall 프로젝트의 가상환경 Python 인터프리터(`.venv\Scripts\python.exe`)를 사용하여 `-m markdown_creat.telegram_bot` 모듈 호출로 봇을 실행한다.

### venv 사전 점검 (Pre-flight Check)

- **REQ-TELEGRAM-027 (Event-driven)**: When 실행 시점에 `.venv\Scripts\python.exe`가 존재하지 않으면, the launcher shall 어떤 구성 요소(가상환경)가 누락되었는지 명확한 평이한 언어의 오류 메시지와 함께 즉시 실패(fail-fast)하고, 봇 모듈을 호출하지 않은 채 0이 아닌 종료 코드로 종료한다.

### 콘솔 유지 (Console Persistence)

- **REQ-TELEGRAM-028 (Ubiquitous)**: The launcher shall 봇 프로세스가 정상 종료, 처리되지 않은 오류, 또는 venv 사전 점검 실패(REQ-TELEGRAM-027) 중 어떤 방식으로 끝나든, 사용자가 입력을 제공할 때까지 콘솔 창을 열어 둔다.
- **REQ-TELEGRAM-029 (Event-driven)**: When 호출된 봇 프로세스가 표준출력/표준오류에 내용(시작 로그 또는 `MissingBotTokenError`와 같은 처리되지 않은 Python 예외 포함)을 기록하면, the launcher shall 해당 출력을 가로채거나 숨기지 않고 콘솔 창에 그대로 노출한 채 종료 대기 상태(REQ-TELEGRAM-028)로 진입한다.

### 분리된 Unwanted (GEARS 단일 패턴 준수)

- **REQ-TELEGRAM-030 (Unwanted)**: The launcher shall not 시스템 PATH에 의존하는 bare `python` 명령을 호출한다(REQ-TELEGRAM-026의 venv 전용 호출 제약).
- **REQ-TELEGRAM-031 (Unwanted)**: When `.venv\Scripts\python.exe`가 존재하지 않으면, the launcher shall not 봇 모듈(`markdown_creat.telegram_bot`) 호출을 시도한다(REQ-TELEGRAM-027의 fail-fast 제약 — venv 부재가 확인되면 봇 모듈 호출 자체를 금지한다).
- **REQ-TELEGRAM-032 (Unwanted)**: The launcher shall not 명시적인 대기(pause) 단계 없이 프로세스 종료 즉시 콘솔 창이 자동으로 닫히도록 허용한다(REQ-TELEGRAM-028의 콘솔 유지 제약).
- **REQ-TELEGRAM-033 (Unwanted)**: The launcher shall not 봇을 OS 레벨 자동 시작 대상으로 등록한다 — Windows 서비스 등록, 작업 스케줄러(Task Scheduler) 등록, 부팅 시 자동 실행 후크 중 어느 것도 구현하지 않는다(`SPEC-TELEGRAM-001` §Exclusions "자동 시작 / OS 서비스 등록"과 동일한 경계 — §Exclusions 참조).
- **REQ-TELEGRAM-034 (Unwanted)**: The launcher shall not 봇을 백그라운드 또는 데몬 프로세스로 실행한다 — 봇은 항상 launcher가 연 콘솔 창의 foreground에서 실행된다.
- **REQ-TELEGRAM-035 (Unwanted)**: When `.venv\Scripts\python.exe`가 존재하지 않으면, the launcher shall not 가공되지 않은 원시 Python 트레이스백(스택 트레이스)만을 유일한 실패 신호로 사용자에게 노출한다 — REQ-TELEGRAM-027이 정의하는 명확한 평이한 언어 오류 메시지를 반드시 함께(또는 대신) 제공해야 한다(REQ-TELEGRAM-031과 짝을 이루는 venv 부재 시 출력 형식 제약 — plan-audit iteration 1 D4에 따라 기존 REQ-TELEGRAM-031에서 분리 신설).

---

## §C. 제약 및 품질 게이트 (Constraints)

- 대상 셸: Windows `cmd.exe` 배치 스크립트(`.bat`). PowerShell 스크립트(`.ps1`)가 아니다.
- 작업 디렉토리 고정은 `cd /d "%~dp0"` 패턴(또는 동등한 관용구)을 사용하여, 스크립트 자신의 드라이브·경로로 이동한다(`%~dp0`는 배치 스크립트 자기 위치를 가리키는 표준 확장 변수).
- venv 존재 여부 점검은 `if not exist ".venv\Scripts\python.exe" (...)` 형태의 조건문으로 수행하며, 반드시 `cd /d` 앵커링 **이후**에 상대 경로로 검사한다(앵커링 이전에 검사하면 실행 위치에 따라 오탐/미탐이 발생할 수 있음).
- 봇 호출 시 표준출력/표준오류를 리다이렉트하거나 억제하지 않는다 — `.env` 부재 시의 `MissingBotTokenError` 메시지(`config.py`의 기존 메시지, 예: `"TELEGRAM_BOT_TOKEN is not set. Set it as an environment variable or in a gitignored .env file at the project root."`)를 포함한 Python 자체의 출력이 그대로 같은 콘솔 창에 표시되어야 한다(REQ-TELEGRAM-029).
- 콘솔 유지는 스크립트의 모든 종료 경로(venv 부재 fail-fast 경로, 봇 프로세스 정상/비정상 종료 경로) 끝에 `pause`(또는 동등한 대기 명령)를 배치하여 구현한다.
- 신규 Python 소스 코드 변경이나 `pyproject.toml` 의존성 추가는 없다 — 순수 배치 스크립트 1개 파일 추가만으로 구현 가능해야 한다.
- 봇 코어 로직(`telegram_bot/` 패키지)과 `config.py`의 토큰 로딩·fail-fast 로직은 수정하지 않는다(PRESERVE) — 본 SPEC은 그것들을 호출만 한다.
- 파일 인코딩: `cmd.exe`가 UTF-8 BOM이 있는 파일의 첫 줄을 오동작(문자 깨짐)시킬 수 있으므로, BOM 없는 인코딩으로 저장한다.
- 콘솔 코드페이지(예: 한글 로그 출력 시 mojibake)를 줄이기 위해 스크립트 시작부에 `chcp 65001 > nul`을 넣는 것을 권장 관행으로 남기되, 인수 기준으로 강제하지는 않는다(§Exclusions 참조).
- 개발 방법론: `quality.yaml`의 `constitution.development_mode: tdd`를 명목상 따르나, `.bat` 파일은 `pytest`/`ruff`/`black` 대상이 아니므로 검증은 acceptance.md의 EARS/GEARS 인수 시나리오 수동 검증으로 수행한다(plan.md §E 참조).
- 코드 식별자·기술 용어(변수명, 라벨 등)는 영어로 작성한다(언어 정책). 사용자에게 표시되는 오류 메시지 텍스트의 언어는 구현 시 결정(plan.md §D M1 참조).

---

## §Exclusions / 만들지 않는 것 (What NOT to Build)

본 SPEC은 "기존 텔레그램 봇을 더블클릭으로 시작하는 수동 foreground 실행기" 단일 관심사에 집중한다. 아래 항목은 명시적으로 범위 밖이다.

### Out of Scope — 자동 시작 / OS 서비스 등록 (SPEC-TELEGRAM-001 §Exclusions 계승)
- `SPEC-TELEGRAM-001` §Exclusions "자동 시작 / OS 서비스 등록"의 경계를 그대로 계승한다. 부팅 시 자동 시작, Windows 서비스 등록, 작업 스케줄러(Task Scheduler) 연동은 구현하지 않는다. 본 launcher는 사용자가 직접 더블클릭하는 **수동 실행만** 지원하며, 자기 자신을 자동 시작 대상으로 등록하는 기능도 포함하지 않는다(REQ-TELEGRAM-033).

### Out of Scope — 백그라운드 / 데몬 실행
- 봇을 백그라운드 프로세스로 전환하거나, 콘솔 창을 최소화·숨김 상태로 실행하거나, launcher 종료 후에도 봇이 계속 살아있게 하는(detach) 기능은 다루지 않는다. 봇은 항상 launcher가 연 foreground 콘솔 창에서 실행되며, 그 창이 강제로 닫히면 봇도 함께 종료된다(REQ-TELEGRAM-034).

### Out of Scope — venv 자동 생성 / 의존성 자동 설치
- `.venv`가 존재하지 않을 때 launcher가 자동으로 `python -m venv` 또는 `pip install`을 수행하는 기능은 구현하지 않는다. venv 부재는 명확한 오류로 보고하고 종료하는 것으로 그친다(REQ-TELEGRAM-027).
- venv는 존재하지만 필수 의존성(`python-telegram-bot`, `pytesseract` 등)이 설치되어 있지 않은 경우에 대한 별도의 launcher 레벨 사전 검증도 하지 않는다 — 이 경우 Python이 발생시키는 `ModuleNotFoundError`가 콘솔에 그대로 노출되며, REQ-TELEGRAM-028/029의 콘솔 유지·출력 노출 계약이 이 케이스에도 동일하게 적용되어 사용자가 오류를 읽을 수 있다.

### Out of Scope — 봇 토큰 / 설정 관리
- `.env` 파일 생성, 봇 토큰 유효성 검증, 토큰 등록 UI는 다루지 않는다 — 이는 기존 `SPEC-TELEGRAM-001`의 `config.py` 책임 영역이며 본 SPEC은 그 로직을 그대로 재사용만 한다.

### Out of Scope — 중복 실행 방지 (락 파일 등)
- 사용자가 launcher를 여러 번 더블클릭하여 봇 프로세스가 중복 실행되는 것을 방지하는 락(lock) 파일이나 프로세스 존재 검사 메커니즘은 구현하지 않는다.

### Out of Scope — macOS / Linux 셸 스크립트 등가물
- 본 SPEC은 Windows `.bat` 실행기만 다룬다. macOS/Linux용 `.sh` 셸 스크립트 등가물은 범위 밖이며, 필요 시 별도 SPEC의 대상이다.

### Out of Scope — 콘솔 유니코드 / 코드페이지 완전 대응
- Windows 콘솔 코드페이지(CP949 vs UTF-8)로 인한 한글 텍스트의 완전한 mojibake 방지는 범위 밖이다. `chcp 65001` 적용은 권장 관행으로 §C에 남기되, 이를 인수 기준으로 강제하지 않는다.

### Out of Scope — 바탕화면 바로가기 / 아이콘 생성 자동화
- `run_telegram_bot.bat`에 대한 바탕화면 바로가기(.lnk) 자동 생성이나 커스텀 아이콘 지정은 다루지 않는다. 사용자가 원하면 Windows 탐색기 기본 기능(바로가기 만들기)으로 직접 생성할 수 있다.

---

## §E. 참조 (Cross-References)

- 프로젝트 문서: `.moai/project/product.md`, `.moai/project/structure.md`, `.moai/project/tech.md`
- 의존 SPEC(실행 대상 봇의 소유자, 실행 스크립트 경로를 이미 예고): `.moai/specs/SPEC-TELEGRAM-001/spec.md` (§A "수동 실행(`python -m ...` 또는 실행 스크립트)", §Exclusions "자동 시작 / OS 서비스 등록")
- 관련 SPEC(동일 모듈의 선행 보안 수정, 3-파일 Tier M 구조 선례): `.moai/specs/SPEC-TELEGRAM-002/spec.md`
- 실행 대상 진입점: `src/markdown_creat/telegram_bot/__main__.py` (`python -m markdown_creat.telegram_bot`)
- 토큰 로딩 / fail-fast 로직(수정 없이 재사용): `src/markdown_creat/telegram_bot/config.py` (`load_bot_token()`, `MissingBotTokenError`)
- 가상환경: `.venv/` (Windows: `.venv\Scripts\python.exe`)
- 품질 설정: `.moai/config/sections/quality.yaml` (`constitution.development_mode: tdd`)
- 구현 계획: `plan.md`
- 상세 인수 기준: `acceptance.md`
- 요약본: `spec-compact.md`
