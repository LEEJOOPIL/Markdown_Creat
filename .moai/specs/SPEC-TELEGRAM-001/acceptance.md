---
id: SPEC-TELEGRAM-001
title: "텔레그램 → 마크다운 저장 봇 — 인수 기준"
version: "0.1.0"
status: draft
created: 2026-07-15
updated: 2026-07-15
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

## §D. 인수 시나리오 (Given-When-Then)

### AC-TELEGRAM-001a — 텍스트 메시지 저장 (REQ-TELEGRAM-004, 008, 009)
- **Given** 봇이 실행 중이고,
- **When** 사용자가 봇에게 플레인 텍스트 메시지를 전송하면,
- **Then** `telegram-notes/YYYY-MM-DD/` 하위에 타임스탬프 기반 파일명의 `.md` 파일 하나가 생성되고, 메시지 타임스탬프·발신자/채팅 컨텍스트·텍스트 본문이 기록된다.

### AC-TELEGRAM-002a — 사진 첨부 원본 저장 + OCR (REQ-TELEGRAM-005, 007, 009)
- **Given** 봇이 실행 중이고 Tesseract OCR 엔진이 사용 가능하며,
- **When** 사용자가 텍스트가 포함된 사진(이미지)을 전송하면,
- **Then** 원본 이미지가 `files/` 하위에 저장되고, OCR로 추출한 텍스트가 해당 메시지의 `.md` 본문에 포함되며, `.md`는 저장된 원본 파일 경로로 링크한다.

### AC-TELEGRAM-002b — 문서(PDF) 첨부 원본 저장 + 텍스트 추출 (REQ-TELEGRAM-005, 006, 009)
- **Given** 봇이 실행 중이고 SPEC-PDF-001의 `pdf_to_markdown()`가 사용 가능하며,
- **When** 사용자가 텍스트 기반 PDF 문서를 전송하면,
- **Then** 원본 PDF가 `files/` 하위에 저장되고, SPEC-PDF-001을 재사용해 추출한 텍스트가 해당 메시지의 `.md` 본문에 포함되며, PDF 파싱 로직은 본 SPEC 내에서 재구현되지 않는다.

### AC-TELEGRAM-003a — 토큰 부재 시 fail-fast (REQ-TELEGRAM-003)
- **Given** `TELEGRAM_BOT_TOKEN` 환경변수와 `.env` 어디에도 토큰이 설정되지 않았고,
- **When** 봇을 기동하면,
- **Then** 토큰 누락을 알리는 명확한 오류 메시지와 함께 봇이 즉시 종료되며, 조용히 멈추거나 무한 대기하지 않는다.

### AC-TELEGRAM-003b — long polling 사용 (REQ-TELEGRAM-001)
- **Given** 유효한 봇 토큰이 주입되었고,
- **When** 봇을 기동하면,
- **Then** 봇은 long polling으로 메시지를 수신하며 webhook 엔드포인트를 등록/사용하지 않는다.

### AC-TELEGRAM-004a — API/네트워크 오류 시 폴링 지속 (REQ-TELEGRAM-010)
- **Given** 봇이 폴링 중이고,
- **When** 텔레그램 API 또는 네트워크 오류가 발생하면,
- **Then** 폴링 루프가 조용히 크래시하지 않고 오류를 기록한 뒤 폴링을 계속한다.

### AC-TELEGRAM-004b — 추출 실패 시 원본 보존 (REQ-TELEGRAM-005, 011)
- **Given** 봇이 첨부(사진 또는 문서)를 수신했고,
- **When** OCR 또는 PDF 텍스트 추출이 실패하면(예: Tesseract 미설치, 손상된 PDF),
- **Then** 원본 파일은 `files/`에 정상 저장되고, "추출 실패"를 알리는 노트를 포함한 `.md`가 저장되며, 메시지 전체가 유실되지 않는다.

### AC-TELEGRAM-005a — 비밀 값 비기록 (REQ-TELEGRAM-012)
- **Given** 봇이 실행되어 메시지를 처리·기록하고,
- **When** `.md` 저장 및 로그 기록이 이루어지면,
- **Then** 봇 토큰 등 비밀 값이 저장된 `.md` 파일이나 로그에 포함되지 않는다.

## §D.1 엣지 케이스 (Edge Cases)

- 봇과 대화하는 임의의 채팅에서 온 메시지 → 접근 제어 없이 모두 저장된다(§Exclusions — 접근 제어 미구현). 이는 오류가 아니며 plan.md §E 리스크로 기록됨.
- 동일 초(second)에 여러 메시지 도착 → 타임스탬프 파일명 충돌 회피 전략(plan.md §D M1에서 확정)에 따라 각각 별도 `.md`로 저장된다.
- 텍스트가 없는 이미지(OCR 결과 빈 문자열) → 오류가 아니며, 원본 저장 + 본문에 "추출 텍스트 없음" 노트로 처리한다.
- 비-PDF 문서(예: `.txt`, `.docx`) → 최소 범위에서는 원본 저장 + 유형 노트로 처리(텍스트 추출 대상은 PDF에 한정, plan.md §D M2에서 확정).
- SPEC-PDF-001 미구현 상태에서의 run → Depends_on Pre-flight Check가 미충족 의존성을 노출(wait/override/abort). PDF 추출 통합은 보류 가능하며, 그 상태를 progress.md에 기록한다.
- 한글 등 비ASCII 메시지/추출 텍스트 → UTF-8로 정확히 기록된다.

## §D.2 품질 게이트 / Definition of Done

- [ ] AC-TELEGRAM-001a, 002a, 002b, 003a, 003b, 004a, 004b, 005a 전 시나리오 통과.
- [ ] 테스트 커버리지 85% 이상 (`quality.yaml` `constitution.test_coverage_target`). 텔레그램 API·Tesseract·PyMuPDF(SPEC-PDF-001)는 목/스텁으로 격리.
- [ ] `ruff` 린트 무경고, `black` 포맷 준수, `pytest` 전체 그린.
- [ ] spec.md의 REQ-TELEGRAM-001~012가 각각 최소 1개 테스트로 검증됨(추적성).
- [ ] `.env`가 `.gitignore`에 등록되어 있고, 소스·커밋에 토큰 하드코딩이 없음(REQ-TELEGRAM-002).
- [ ] PDF 파싱 로직이 본 SPEC 내에서 재구현되지 않고 SPEC-PDF-001을 재사용함(§Exclusions 준수).
- [ ] 봇 토큰 등 비밀 값이 `.md`/로그에 기록되지 않음(REQ-TELEGRAM-012).
