---
id: SPEC-TELEGRAM-001
title: "텔레그램 → 마크다운 저장 봇 — 인수 기준"
version: "0.3.0"
status: completed
created: 2026-07-15
updated: 2026-07-16
author: manager-spec
priority: P1
phase: "v0.1.0 target"
module: "src/markdown_creat/telegram_bot"
lifecycle: spec-anchored
tags: "telegram, bot, markdown, ocr, polling"
depends_on: [SPEC-PDF-001]
tier: M
---

# SPEC-TELEGRAM-001 — 인수 기준 (acceptance.md)

## §D. 인수 시나리오 (GEARS)

### AC-TELEGRAM-001a — 텍스트 메시지 저장 (REQ-TELEGRAM-004, 008, 009)
- When the bot receives a plain-text message, the bot shall save a `.md` file under `telegram-notes/YYYY-MM-DD/` with a timestamp-based filename, recording the message timestamp, sender/chat context, and text body.

### AC-TELEGRAM-001b — 베이스 폴더 설정 사용 (REQ-TELEGRAM-018, 008)
- Where a base-folder configuration value is provided, When the bot saves a `.md` file for any received message, the bot shall use the configured base folder in place of the default `telegram-notes/` for that message's date-based save path (`<configured-base>/YYYY-MM-DD/`).

### AC-TELEGRAM-002a — 사진 첨부 원본 저장 + OCR (REQ-TELEGRAM-005, 007, 009)
- Where the Tesseract OCR engine is available, When the bot receives a photo (image) containing text, the bot shall save the original image under `files/` and shall include the OCR-extracted text in the message's `.md` body, linked to the saved original file's path.

### AC-TELEGRAM-002b — 문서(PDF) 첨부 원본 저장 + 텍스트 추출 (REQ-TELEGRAM-005, 006, 009)
- Where SPEC-PDF-001's `pdf_to_markdown()` is available, When the bot receives a text-based PDF document, the bot shall save the original PDF under `files/` and shall include the text extracted via SPEC-PDF-001 reuse in the message's `.md` body; the bot shall not reimplement PDF parsing logic within this SPEC (§Exclusions — PDF 파싱 재구현 제외 참조).

### AC-TELEGRAM-003a — 토큰 부재 시 fail-fast (REQ-TELEGRAM-003, 015)
- When the bot starts and no bot token is set in either the `TELEGRAM_BOT_TOKEN` environment variable or `.env`, the bot shall exit immediately with a clear error message identifying the missing configuration; the bot shall not hang silently or wait indefinitely.

### AC-TELEGRAM-003b — long polling 사용 (REQ-TELEGRAM-001, 013)
- When the bot starts with a valid bot token injected, the bot shall receive messages via long polling; the bot shall not register or use a webhook endpoint.

### AC-TELEGRAM-004a — API/네트워크 오류 시 폴링 지속 (REQ-TELEGRAM-010, 016)
- When a Telegram API or network error occurs while the bot is polling, the bot shall log the error and continue polling; the bot shall not silently crash the polling loop.

### AC-TELEGRAM-004b — 추출 실패 시 원본 보존 (REQ-TELEGRAM-005, 011, 017)
- When OCR or PDF text extraction fails for a received attachment (e.g., Tesseract not installed, corrupted PDF), the bot shall save the original file under `files/` and shall save a `.md` file containing a note indicating extraction failure; the bot shall not lose the message entirely.

### AC-TELEGRAM-005a — 비밀 값 비기록 (REQ-TELEGRAM-012)
- When the bot processes and records a message (saving `.md` and writing logs), the bot shall not include secret values such as the bot token in the saved `.md` file or in logs.

### AC-TELEGRAM-005b — 토큰 환경변수/`.env` 소스 및 미노출 (REQ-TELEGRAM-002, 014)
- When the bot starts, the bot shall read the bot token from the `TELEGRAM_BOT_TOKEN` environment variable or a gitignored `.env` file; the bot shall not hardcode the token literal in source code or commit it to version control. (정적 `.env`/`.gitignore` 등록 점검은 런타임 트리거가 아니므로 §D.2 DoD 체크리스트 항목으로 분리 소유.)

## §D.1 엣지 케이스 (Edge Cases)

- 봇과 대화하는 임의의 채팅에서 온 메시지 → 접근 제어 없이 모두 저장된다(§Exclusions — 접근 제어 미구현). 이는 오류가 아니며 plan.md §E 리스크로 기록됨.
- 동일 초(second)에 여러 메시지 도착 → 타임스탬프 파일명 충돌 회피 전략(plan.md §D M1에서 확정)에 따라 각각 별도 `.md`로 저장된다.
- 텍스트가 없는 이미지(OCR 결과 빈 문자열) → 오류가 아니며, 원본 저장 + 본문에 "추출 텍스트 없음" 노트로 처리한다.
- 비-PDF 문서(예: `.txt`, `.docx`) → 최소 범위에서는 원본 저장 + 유형 노트로 처리(텍스트 추출 대상은 PDF에 한정, plan.md §D M2에서 확정).
- SPEC-PDF-001 의존성 충족 확인 → SPEC-PDF-001은 `status: completed`이며 `pdf_to_markdown(pdf_path, output_path)`가 `src/markdown_creat/pdf_to_markdown.py:62`에 구현되어 있다(2026-07-16 확인). Depends_on Pre-flight Check는 통과가 예상되며, PDF 추출(AC-TELEGRAM-002b)은 보류 없이 완전 통합 대상이다.
- 한글 등 비ASCII 메시지/추출 텍스트 → UTF-8로 정확히 기록된다.

## §D.2 품질 게이트 / Definition of Done

- [x] AC-TELEGRAM-001a, 001b, 002a, 002b, 003a, 003b, 004a, 004b, 005a, 005b 전 시나리오 통과. **(as-implemented, 2026-07-16)** 10/10 AC PASS — 상세 검증 명령·출력은 `progress.md` §E.2 AC Binary PASS/FAIL Matrix 참조.
- [x] 테스트 커버리지 85% 이상 (`quality.yaml` `constitution.test_coverage_target`). 텔레그램 API·Tesseract·PyMuPDF(SPEC-PDF-001)는 목/스텁으로 격리. **실제**: 96% overall coverage (70 passed) — `progress.md` §E.2 Full Suite + Coverage 참조.
- [x] `ruff` 린트 무경고, `black` 포맷 준수, `pytest` 전체 그린. **실제**: `ruff check` all checks passed, `black --check` 18 files unchanged, `pytest` 70 passed.
- [x] spec.md의 REQ-TELEGRAM-001~018이 각각 최소 1개 테스트로 검증됨(추적성). **실제**: per-REQ grep sweep으로 전 REQ 추적성 확인됨(`progress.md` §E.2).
- [x] `.env`가 `.gitignore`에 등록되어 있고(정적 파일 존재 점검), 소스·커밋에 토큰 하드코딩이 없음(REQ-TELEGRAM-002, 014). **실제**: AC-TELEGRAM-005b 검증에서 `.env` gitignore 등록 확인됨.
- [x] PDF 파싱 로직이 본 SPEC 내에서 재구현되지 않고 SPEC-PDF-001을 재사용함(§Exclusions 준수). **실제**: `extract.py`가 `pdf_to_markdown()`을 임시 파일 write-then-read 래퍼로 재사용(재구현 없음).
- [x] 봇 토큰 등 비밀 값이 `.md`/로그에 기록되지 않음(REQ-TELEGRAM-012). **실제**: AC-TELEGRAM-005a 검증 통과.
