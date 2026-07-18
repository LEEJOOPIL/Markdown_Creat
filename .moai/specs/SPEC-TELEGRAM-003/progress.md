---
id: SPEC-TELEGRAM-003
title: "텔레그램 봇 Windows 더블클릭 실행기 — 진행 기록"
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

# SPEC-TELEGRAM-003 — 진행 기록 (progress.md)

## §E.1 Plan-phase Audit-Ready Signal

- Plan-phase 산출물 세트(spec.md + plan.md + acceptance.md + progress.md, 추가로 요약본 spec-compact.md) 생성 완료. Tier M(3-파일 세트 + progress.md — fail-fast·콘솔 유지 UX 계약의 감사 가능성을 위해 acceptance.md 별도 유지, `SPEC-TELEGRAM-001`/`002`와 동일한 구조적 관례를 따름).
- SPEC ID 사전 자가검증 통과: `decomposition: SPEC ✓ | TELEGRAM ✓ | 003 ✓ → PASS` (canonical regex `^SPEC(-[A-Z][A-Z0-9]*)+-\d{3}$`, Bash 실행 출력 `PASS`).
- Frontmatter 12 필드 canonical 스키마 검증 완료 + optional 필드 `depends_on: [SPEC-TELEGRAM-001]`, `tier: M` 기록.
- 요구사항 배경: `SPEC-TELEGRAM-001`(status: completed)로 구현된 텔레그램 봇(`python -m markdown_creat.telegram_bot`)을 터미널 없이 더블클릭만으로 실행할 수 있는 Windows `.bat` 실행기(`run_telegram_bot.bat`)를 정의. `SPEC-TELEGRAM-001` §A가 이미 "수동 실행(`python -m ...` 또는 실행 스크립트)"이라는 경로를 열어두었고, 본 SPEC이 그 "실행 스크립트" 경로를 구체화한다.
- EARS 요구사항 REQ-TELEGRAM-024~035 정의(Ubiquitous / Event-driven / Unwanted 혼합, 12개). REQ ID는 `SPEC-TELEGRAM-002`의 REQ-TELEGRAM-019~023에 이어 024부터 부여(동일 `TELEGRAM` 도메인 접두어 충돌 방지).
- §Exclusions에 7개 `### Out of Scope —` 하위 헤딩 포함(자동 시작/OS 서비스 등록[SPEC-TELEGRAM-001 계승], 백그라운드/데몬 실행, venv 자동 생성/의존성 자동 설치, 봇 토큰/설정 관리, 중복 실행 방지, macOS/Linux 셸 스크립트 등가물, 콘솔 유니코드/코드페이지 완전 대응).
- 의존성: `SPEC-TELEGRAM-001`(status: completed) — 실행 대상 봇 진입점(`__main__.py`)의 소유자. run-phase Depends_on Pre-flight Check는 통과가 예상된다.
- 개발 방법론: `quality.yaml` `constitution.development_mode: tdd`를 명목상 따르되, `.bat` 스크립트는 pytest/ruff/black 적용 대상이 아니므로 acceptance.md의 EARS/GEARS 시나리오 수동 검증으로 품질 게이트를 대체한다(plan.md §E 리스크에 명시).
- 사용자와 확인된 6대 인수 시나리오: (a) 정상 실행(venv+토큰 존재) → 봇 시작 로그 확인, (b) venv 부재 → 명확한 오류 + 콘솔 유지 + 0이 아닌 종료 코드, (c) 토큰 부재 → 기존 `MissingBotTokenError` 메시지가 콘솔에 노출되며 콘솔 유지, (d)~(f) 정적 스크립트 검토(bare `python` 미사용, OS 자동 시작 미등록, 포그라운드 전용 실행).
- **plan-audit iteration 1 리뷰 반영** (`.moai/reports/plan-audit/SPEC-TELEGRAM-003-review-1.md`, verdict FAIL, score 0.67 → 버전 0.1.1로 개정): (D1, critical) `acceptance.md` §D의 "GEARS / Given-When-Then" 이중 표기를 제거하고 3개 AC를 단일 절 EARS/GEARS 문장으로 재작성; (D2, major) REQ-TELEGRAM-030/033/034에 대한 정적 스크립트 검토 AC(AC-TELEGRAM-030s/033s/034s) 신설로 추적성 공백 해소; (D3, minor) AC-TELEGRAM-027a의 오류 메시지 판정 기준에서 퍼지 매치 제거; (D4, minor) REQ-TELEGRAM-031을 REQ-TELEGRAM-031/035로 분리(REQ-024~034 기존 순서 보존을 위해 035를 말미에 append). 상세는 spec.md HISTORY 0.1.1 행 참조.

## §E.2 Run-phase Evidence

_<pending run-phase>_

## §E.3 Run-phase Audit-Ready Signal

_<pending run-phase>_

## §E.4 Sync-phase Audit-Ready Signal

_<pending sync-phase>_
