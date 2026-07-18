---
id: SPEC-TELEGRAM-003
title: "텔레그램 봇 Windows 더블클릭 실행기 — 인수 기준"
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

# SPEC-TELEGRAM-003 — 인수 기준 (acceptance.md)

## §D. 인수 시나리오 (GEARS)

각 인수 기준(AC)은 단일 절의 EARS/GEARS 패턴 문장(Event-driven `When [trigger], the launcher shall [response]` 또는 Unwanted `The [subject] shall not [undesired]`)으로 기술한다. "Given"은 GEARS가 인정하는 수식어(Where/While/When)에 포함되지 않으므로, 선행 조건(precondition)은 트리거 절(`When`) 안으로 접어 넣는다.

### AC-TELEGRAM-024a (Event-driven) — 정상 실행: venv + 토큰 존재 (REQ-TELEGRAM-024, 025, 026, 028, 029)

When `.venv\Scripts\python.exe`가 존재하고 `TELEGRAM_BOT_TOKEN`이 환경변수 또는 프로젝트 루트의 `.env` 파일로 해석 가능한 상태에서 사용자가 Windows 탐색기에서 `run_telegram_bot.bat`을 더블클릭하면, the launcher shall 자기 자신의 파일 위치로 작업 디렉토리를 고정(anchor)한 뒤 `.venv\Scripts\python.exe -m markdown_creat.telegram_bot`을 호출하고, 콘솔 창에 봇의 시작 로그(예: long polling 시작을 알리는 메시지)를 그대로 노출하며, 사용자가 입력을 제공할 때까지 콘솔 창을 자동으로 닫지 않는다.

### AC-TELEGRAM-027a (Event-driven) — venv 부재 (REQ-TELEGRAM-027, 031, 032, 035)

When 실행 시점에 `.venv\Scripts\python.exe`가 존재하지 않으면, the launcher shall 봇 모듈을 호출하지 않고, 누락된 구성 요소(`.venv`)를 평이한 언어로 명시하는 오류 메시지(정확한 문구는 구현 시 결정 가능 — plan.md §D M1 참조)를 콘솔에 출력하며, 0이 아닌 종료 코드로 종료하고, 사용자가 키를 누르기 전까지 콘솔 창을 열어 둔다.

### AC-TELEGRAM-027b (Event-driven) — 봇 토큰 부재 (REQ-TELEGRAM-028, 029)

When `.venv\Scripts\python.exe`는 존재하지만 `TELEGRAM_BOT_TOKEN` 환경변수와 `.env` 파일 값이 모두 없는 상태에서 사용자가 `run_telegram_bot.bat`을 더블클릭하면, the launcher shall venv 사전 점검을 통과시켜 봇 모듈을 호출하고, 봇 프로세스가 발생시키는 기존 `config.py`의 `MissingBotTokenError` 메시지("TELEGRAM_BOT_TOKEN is not set. Set it as an environment variable or in a gitignored .env file at the project root.")를 가로채거나 억제하지 않고 콘솔에 그대로 노출한 채 종료하며, 그 이후에도 콘솔 창을 닫지 않고 대기한다.

### AC-TELEGRAM-030s (Unwanted, 정적 스크립트 검토) — bare `python` 미사용 (REQ-TELEGRAM-030)

The launcher script(`run_telegram_bot.bat`)는 shall not 시스템 PATH에 의존하는 bare `python`(또는 `python.exe`) 호출을 포함한다 — 검증: 코드 리뷰 시 스크립트 텍스트를 검사하여 모든 Python 호출이 `.venv\Scripts\python.exe` 전체 경로로만 한정됨을 확인한다.

### AC-TELEGRAM-033s (Unwanted, 정적 스크립트 검토) — OS 자동 시작 미등록 (REQ-TELEGRAM-033)

The launcher script는 shall not Windows 서비스 등록, 작업 스케줄러(`schtasks`) 등록, 또는 부팅 시 자동 실행 후크에 해당하는 명령을 포함한다 — 검증: 코드 리뷰 시 스크립트 텍스트에 `schtasks`, `sc create`, 레지스트리 `Run` 키 조작 등의 문자열이 존재하지 않음을 확인한다.

### AC-TELEGRAM-034s (Unwanted, 정적 검토 + M5 실행 중 관찰) — 포그라운드 전용 실행 (REQ-TELEGRAM-034)

The launcher는 shall not 봇 프로세스를 백그라운드로 분리(detach)하는 명령(`start /b` 등 백그라운드 전환 옵션)을 포함한다 — 검증: (a) 코드 리뷰 시 스크립트에 백그라운드 전환 명령이 없음을 확인하고, (b) M5 수동 검증 시 작업 관리자(Task Manager)에서 봇 프로세스가 `run_telegram_bot.bat`이 연 `cmd.exe` 콘솔 창의 자식 프로세스로 표시됨을 관찰로 확인한다.

## §D.1 엣지 케이스 (Edge Cases)

- **실행 위치 독립성**: 사용자가 프로젝트 루트가 아닌 다른 디렉토리(예: 바탕화면 바로가기)에서 `run_telegram_bot.bat`을 실행해도 REQ-TELEGRAM-025의 cwd 앵커링 덕분에 동일하게 동작해야 한다.
- **사용자에 의한 강제 종료**: 사용자가 콘솔 창의 X 버튼을 눌러 강제로 닫거나 작업 관리자로 프로세스를 종료하는 경우, OS 레벨 강제 종료의 본질적 한계로 `pause` 로직이 실행되지 못할 수 있다 — 이는 REQ-TELEGRAM-028 위반이 아니며, 본 인수 기준은 launcher가 자기 자신의 정상/비정상 종료 경로에서 pause를 배치하는지만 검증한다.
- **venv는 존재하나 의존성 미설치**: `.venv\Scripts\python.exe`는 존재하지만 `python-telegram-bot` 등 필수 패키지가 설치되지 않은 경우, launcher는 이를 별도로 사전 검증하지 않는다(§Exclusions "venv 자동 생성 / 의존성 자동 설치" 참조) — Python이 발생시키는 `ModuleNotFoundError`가 콘솔에 그대로 노출되고, REQ-TELEGRAM-028/029의 콘솔 유지·출력 노출 계약이 동일하게 적용되어 사용자가 오류를 읽을 수 있다.
- **중복 실행**: 사용자가 launcher를 여러 번 더블클릭하는 경우 중복 실행 방지 로직은 없다(§Exclusions 참조) — 각 실행은 독립적인 봇 프로세스를 시작하며, 이 인수 기준의 검증 대상이 아니다.
- **한글 로그 출력**: 봇이 한글 메시지가 포함된 노트를 처리하며 콘솔에 한글이 섞인 로그를 출력할 경우, 코드페이지 설정에 따라 일부 mojibake가 발생할 수 있다 — §Exclusions "콘솔 유니코드/코드페이지 완전 대응"에 따라 완전한 해결은 범위 밖이며, 이 인수 기준의 PASS/FAIL 판정에 영향을 주지 않는다.

## §D.2 품질 게이트 / Definition of Done

- [ ] `run_telegram_bot.bat`이 프로젝트 루트(`E:\Desktop\markdown_creat\run_telegram_bot.bat`)에 존재하며, BOM 없는 인코딩으로 저장되어 `cmd.exe`가 정상 파싱한다.
- [ ] AC-TELEGRAM-024a, 027a, 027b 세 실행 시나리오 모두 실제 Windows 환경에서 더블클릭으로 수동 검증되어 통과한다(자동화 테스트 도구 미적용 — plan.md §E 참조).
- [ ] AC-TELEGRAM-030s, 033s, 034s 세 정적 스크립트 검토 시나리오가 코드 리뷰(034s는 추가로 M5 작업 관리자 관찰)로 검증되어 통과한다.
- [ ] §D.1 엣지 케이스 중 "실행 위치 독립성"이 최소 2가지 실행 위치(프로젝트 루트 직접 실행, 다른 디렉토리에서 실행 또는 바로가기)로 검증된다.
- [ ] REQ-TELEGRAM-024~035(12개)가 각각 위 6개 AC 또는 §D.1 엣지 케이스 중 최소 1곳으로 추적 가능하다(추적성 — REQ-030/033/034는 AC-030s/033s/034s로, REQ-031/035는 AC-027a로 추적).
- [ ] `src/` 하위 Python 소스 코드에 변경이 없음을 `git diff --stat`로 확인한다(`telegram_bot/` 패키지, `config.py` 등 PRESERVE 대상 무변경).
- [ ] `pyproject.toml`에 신규 의존성이 추가되지 않았음을 확인한다.
- [ ] 기존 `tests/test_telegram_*.py` 스위트가 전부 통과한다(Python 코드 변경이 없으므로 자명하나, 회귀 없음을 명시적으로 재확인한다).
- [ ] `ruff`/`black`/`pytest`는 `.bat` 파일에 적용되지 않는다 — 본 SPEC의 품질 게이트는 위 EARS/GEARS 인수 시나리오(실행 시나리오 3개 + 정적 스크립트 검토 시나리오 3개) 수동 검증으로 대체됨을 진행 기록(`progress.md`)에 명시한다.
