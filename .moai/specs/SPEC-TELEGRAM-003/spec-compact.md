---
id: SPEC-TELEGRAM-003
title: "텔레그램 봇 Windows 더블클릭 실행기 — 요약본"
version: "0.1.1"
status: draft
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

# SPEC-TELEGRAM-003 — 요약본 (spec-compact.md)

> 전체 상세는 `spec.md` / `plan.md` / `acceptance.md`를 참조. 본 문서는 빠른 검토를 위한 1페이지 요약이다.

## 한 줄 요약

프로젝트 루트에 `run_telegram_bot.bat`을 추가하여, 터미널 없이 더블클릭만으로 기존 텔레그램 봇(`SPEC-TELEGRAM-001`, `python -m markdown_creat.telegram_bot`)을 시작할 수 있게 한다.

## 핵심 계약 (4가지)

1. **더블클릭 실행** — 프로젝트 루트의 `run_telegram_bot.bat`을 더블클릭하면 봇이 시작된다.
2. **실행 위치 독립성** — `cd /d "%~dp0"` 패턴으로 자기 위치에 작업 디렉토리를 고정, 어디서 실행해도 동일하게 동작.
3. **venv 전용 호출 + fail-fast** — `.venv\Scripts\python.exe -m markdown_creat.telegram_bot`만 호출(bare `python` 금지); `.venv\Scripts\python.exe`가 없으면 명확한 오류로 즉시 종료(0이 아닌 exit code).
4. **콘솔 유지** — 성공/실패 어느 경로든 프로세스 종료 후 `pause`로 창을 열어 두어, 사용자가 출력(시작 로그 또는 `MissingBotTokenError` 등)을 읽을 수 있게 한다.

## REQ 목록 (REQ-TELEGRAM-024~035)

| REQ | 패턴 | 한 줄 설명 |
|-----|------|-----------|
| REQ-TELEGRAM-024 | Ubiquitous | 프로젝트 루트에 더블클릭 실행 가능한 `.bat` 제공 |
| REQ-TELEGRAM-025 | Ubiquitous | 실행 전 자기 위치로 cwd 앵커링 |
| REQ-TELEGRAM-026 | Ubiquitous | venv Python으로 `-m markdown_creat.telegram_bot` 호출 |
| REQ-TELEGRAM-027 | Event-driven | venv 부재 시 fail-fast (명확한 오류 + 0이 아닌 exit code) |
| REQ-TELEGRAM-028 | Ubiquitous | 모든 종료 경로에서 콘솔 창 유지 |
| REQ-TELEGRAM-029 | Event-driven | 봇 프로세스 출력(오류 포함)을 가로채지 않고 그대로 노출 |
| REQ-TELEGRAM-030 | Unwanted | bare `python`(시스템 PATH 의존) 호출 금지 |
| REQ-TELEGRAM-031 | Unwanted | venv 부재 시 봇 모듈 호출 시도 금지 |
| REQ-TELEGRAM-032 | Unwanted | pause 없이 창이 즉시 닫히도록 허용 금지 |
| REQ-TELEGRAM-033 | Unwanted | OS 자동 시작/서비스/스케줄러 등록 금지 |
| REQ-TELEGRAM-034 | Unwanted | 백그라운드/데몬 실행 금지 |
| REQ-TELEGRAM-035 | Unwanted | venv 부재 시 원시 Python 트레이스백만을 유일한 실패 신호로 노출 금지(REQ-031과 짝) |

## AC 목록 (acceptance.md)

- **AC-TELEGRAM-024a** (Event-driven): 정상 실행 — venv + 토큰 존재 → 시작 로그 확인, 창 유지.
- **AC-TELEGRAM-027a** (Event-driven): venv 부재 → 명확한 오류, 0이 아닌 exit code, 창 유지.
- **AC-TELEGRAM-027b** (Event-driven): 토큰 부재 → 기존 `MissingBotTokenError` 메시지 노출, 창 유지.
- **AC-TELEGRAM-030s** (Unwanted, 정적 검토): bare `python` 미사용을 스크립트 텍스트 검사로 확인.
- **AC-TELEGRAM-033s** (Unwanted, 정적 검토): OS 자동 시작/서비스 등록 미포함을 스크립트 텍스트 검사로 확인.
- **AC-TELEGRAM-034s** (Unwanted, 정적 검토 + 실행 관찰): 백그라운드 미분리를 스크립트 검토 + 작업 관리자 관찰로 확인.

## Exclusions (7개, 상세는 spec.md §Exclusions)

자동 시작/OS 서비스 등록(SPEC-TELEGRAM-001 계승) · 백그라운드/데몬 실행 · venv 자동 생성/의존성 자동 설치 · 봇 토큰/설정 관리 · 중복 실행 방지 · macOS/Linux 셸 스크립트 · 콘솔 유니코드/코드페이지 완전 대응.

## 핵심 파일 경로

| 항목 | 경로 |
|------|------|
| 신규 실행기 (본 SPEC 산출물) | `run_telegram_bot.bat` (프로젝트 루트) |
| 실행 대상 진입점 (수정 없음) | `src/markdown_creat/telegram_bot/__main__.py` |
| 토큰 로딩 (수정 없음) | `src/markdown_creat/telegram_bot/config.py` |
| 가상환경 | `.venv\Scripts\python.exe` |

## 의존 / 관련 SPEC

- `depends_on`: `SPEC-TELEGRAM-001`(completed) — 실행 대상 봇 소유
- 관련: `SPEC-TELEGRAM-002`(completed) — 동일 모듈 선행 보안 수정, Tier M 구조 선례

## 품질 게이트 특이사항

`.bat` 파일은 `pytest`/`ruff`/`black` 대상이 아니므로, 품질 게이트는 acceptance.md의 실행 시나리오 3개(Windows 환경 더블클릭 수동 검증) + 정적 스크립트 검토 시나리오 3개(코드 리뷰)로 대체된다.
