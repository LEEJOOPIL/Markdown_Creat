---
id: SPEC-TELEGRAM-001
title: "텔레그램 → 마크다운 저장 봇 — 구현 계획"
version: "0.2.0"
status: in-progress
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

# SPEC-TELEGRAM-001 — 구현 계획 (plan.md)

## §A. 컨텍스트 (Context)

그린필드 프로젝트의 세 번째 SPEC. 분석할 기존 코드 없음. `python-telegram-bot`으로 long polling 봇을 구성하여 수신 메시지를 날짜 폴더 기반 `.md`로 저장한다. 사진은 OCR(pytesseract), PDF/문서는 SPEC-PDF-001의 `pdf_to_markdown()` 재사용으로 텍스트를 추출한다. TDD(RED-GREEN-REFACTOR)로 구현한다. Tier M(봇 루프 + 다중 핸들러 + 저장 + 3종 외부 통합 + 다수 오류 경로).

**의존성 확인**: `depends_on: [SPEC-PDF-001]`. SPEC-PDF-001은 `status: completed`이며 `pdf_to_markdown(pdf_path: str, output_path: str) -> None`가 `src/markdown_creat/pdf_to_markdown.py:62`에 구현되어 있다(2026-07-16 확인). `/moai run` 시 Depends_on Pre-flight Check는 통과할 것으로 예상되므로, PDF 추출 부분(M5)은 보류 없이 완전 통합한다.

## §B. PRESERVE / EXTEND

- **PRESERVE**: 기존 코드 없음(그린필드). SPEC-GEN-001·SPEC-PDF-001의 계획된 모듈(`generator.py`, `pdf_to_markdown.py`)은 본 SPEC에서 수정하지 않는다.
- **EXTEND**: `src/markdown_creat/` 아래 신규 서브패키지 `telegram_bot/`를 추가한다. SPEC-PDF-001의 `pdf_to_markdown()`는 호출(재사용)만 하고 변경하지 않는다.

## §C. 기술 접근 (Technical Approach)

`structure.md` 제안 구조를 따르되, 본 SPEC은 신규 서브패키지 하나에 집중한다:

- `src/markdown_creat/telegram_bot/__init__.py` — 패키지 초기화
- `src/markdown_creat/telegram_bot/__main__.py` — `python -m markdown_creat.telegram_bot` 실행 진입점(봇 기동)
- `src/markdown_creat/telegram_bot/config.py` — 봇 토큰(환경변수/`.env`) + 베이스 폴더 설정 로딩, 토큰 부재 시 fail-fast
- `src/markdown_creat/telegram_bot/bot.py` — polling 루프 구성 + 핸들러 등록 + API 오류 복원
- `src/markdown_creat/telegram_bot/handlers.py` — 텍스트/사진/문서 메시지 핸들러
- `src/markdown_creat/telegram_bot/storage.py` — 날짜 폴더 + 타임스탬프 `.md` 작성 + `files/` 원본 저장
- `src/markdown_creat/telegram_bot/ocr.py` — 이미지 OCR 래퍼(pytesseract), 실패 시 예외 → 핸들러가 흡수
- `src/markdown_creat/telegram_bot/extract.py` — PDF 텍스트 추출 래퍼(SPEC-PDF-001 `pdf_to_markdown()` 호출), 실패 시 예외 → 핸들러가 흡수

(최종 모듈 분할은 M4~M6에서 확정. 위는 시작 제안.)

## §D. 마일스톤 (결정 번복 가능성 순 — 변경 가능성 높은 결정 우선)

> 사람이 검토할 때 변경 가능성이 가장 높은 결정(저장 레이아웃 · 노트 스키마 · 핸들러 계약 · 오류 정책)을 먼저 배치하고, 기계적 구현/리팩터 단계는 뒤로 미룬다.

### M1 — 저장 레이아웃 및 노트 스키마 결정 (변경 가능성 최상)
- 날짜 폴더/파일명 규칙 확정(REQ-TELEGRAM-008: `telegram-notes/YYYY-MM-DD/YYYY-MM-DD_HHMMSS.md`), 베이스 폴더 설정 키 확정.
- `.md` 본문 스키마 확정(REQ-TELEGRAM-009): 타임스탬프·발신자/채팅 컨텍스트·본문·첨부 링크의 배치(예: front-matter 유사 헤더 + 본문). 첨부 원본의 `files/` 배치 규칙(파일명 충돌 회피 전략 포함) 확정.
- 이는 사용자가 나중에 노트를 읽는 방식과 직결되어 검토가 가장 필요한 지점이다.
- RED: 저장기(storage)에 대한 실패 테스트 작성.

### M2 — 메시지 핸들러 계약 및 추출 통합 결정 (변경 가능성 상)
- 텍스트/사진/문서 핸들러의 입력→출력 계약 확정(REQ-TELEGRAM-004~007). 사진 OCR(REQ-TELEGRAM-007)과 문서 PDF 추출(REQ-TELEGRAM-006)을 언제·어떻게 `.md` 본문에 병합할지 확정.
- SPEC-PDF-001 `pdf_to_markdown(pdf_path, output_path)` 재사용 방식 확정: 임시 `.md`로 추출 후 본문에 병합할지, 또는 SPEC-PDF-001에 인메모리 추출 경로가 필요한지 판단. **후자가 필요하면 SPEC-PDF-001 범위 확장이 되므로, 구현하지 말고 blocker report로 오케스트레이터에 반환**(본 SPEC은 PDF 파싱 재구현 금지 — §Exclusions).
- 비-PDF 문서(예: `.txt`, `.docx`) 처리 범위 확정 — 최소 범위(PDF만 텍스트 추출, 그 외는 원본 저장 + 유형 노트)로 시작 권장.
- RED: 각 핸들러에 대한 실패 테스트 작성(외부 API·Tesseract·PDF는 목/스텁).

### M3 — 오류 처리 및 토큰 주입 정책 결정 (변경 가능성 상)
- 토큰 부재 fail-fast(REQ-TELEGRAM-003), API/네트워크 오류 시 폴링 지속(REQ-TELEGRAM-010), OCR/PDF 추출 실패 시 원본 보존 + 실패 노트(REQ-TELEGRAM-011), 비밀 값 비기록(REQ-TELEGRAM-012)의 구체 동작·메시지 형태 확정.
- 환경변수 vs `.env` 로딩 우선순위 및 `.env`의 `.gitignore` 등록 확정.
- RED: 각 오류 경로에 대한 실패 테스트 작성.

### M4 — 봇 구성 및 진입점 구현 (GREEN, 기계적)
- `config.py` + `bot.py` + `__main__.py` 최소 구현. `python-telegram-bot`으로 polling 루프 + 핸들러 등록. long polling만 사용(REQ-TELEGRAM-001).
- `pyproject.toml`의 `[project.dependencies]`에 `python-telegram-bot`과 `pytesseract`를 추가한다(현재 `pymupdf>=1.24`만 선언됨). Tesseract OCR 엔진 자체는 시스템 레벨 외부 바이너리로 pip 의존성 범위 밖이며, §C 제약에 따라 별도 설치가 필요하다.

### M5 — 핸들러·저장·추출 구현 (GREEN, 기계적)
- `handlers.py` + `storage.py` + `ocr.py` + `extract.py` 최소 구현으로 테스트 통과. SPEC-PDF-001의 `pdf_to_markdown(pdf_path, output_path)`가 사용 가능하므로, `extract.py`에서 PDF 추출 경로를 완전 통합한다(임시 `.md` 출력 후 본문 병합 방식, M2에서 확정한 계약을 따름) — 스킵/보류 없이 통합 테스트를 포함한다.

### M6 — 리팩터 및 품질 게이트 (REFACTOR, 기계적)
- `ruff` + `black` 정리, 커버리지 85% 확인, 중복 제거, 함수 분리 정리. `.env` gitignore 확인.

## §E. 리스크 (Risks)

- **[통합 방식] 파일 출력 계약 흡수 (리스크 해소됨)**: SPEC-PDF-001은 `status: completed`이며 `pdf_to_markdown(pdf_path, output_path)`가 `src/markdown_creat/pdf_to_markdown.py:62`에서 사용 가능하다(2026-07-16 확인) — 더 이상 의존성 리스크가 아니다. 참고로 이 함수는 파일 출력 계약이므로, 봇에서는 임시 `.md`로 추출 후 본문 병합하는 접근을 사용한다(M2에서 확정, M5에서 완전 통합).
- **[보안/접근 제어 — 리스크로만 기록, 구현 안 함]**: 접근 제어(allowlist)가 없으므로 봇 토큰을 아는 임의의 채팅이 봇에 메시지를 보내 노트를 축적시킬 수 있다. 개인용 봇 전제에서는 허용 리스크이나, 봇 토큰 유출 시 스팸/원치 않는 저장이 발생할 수 있다. 필요 시 후속 SPEC에서 chat_id allowlist를 도입할 것을 권장한다(§Exclusions에 따라 본 SPEC은 미구현).
- **[외부 바이너리] Tesseract 미설치**: OCR은 시스템에 Tesseract 엔진이 설치되어 있어야 한다. 미설치/실패 시 REQ-TELEGRAM-011에 따라 원본 저장 + 실패 노트로 처리(메시지 손실 없음).
- **[네트워크] 장시간 폴링 안정성**: 네트워크 단절·API rate limit 시 REQ-TELEGRAM-010에 따라 루프가 죽지 않고 재시도/지속한다. `python-telegram-bot`의 내장 재시도 동작에 위임 가능.
- **[비밀 취급] 토큰 로깅 금지**: 로그/노트에 토큰이 새지 않도록 REQ-TELEGRAM-012를 준수. 오류 메시지 구성 시 토큰 마스킹 확인.
- **[파일명 충돌] 동일 초에 다수 메시지**: 타임스탬프 초 단위 파일명이 충돌할 수 있음 → M1에서 충돌 회피(접미사/메시지 id 부가) 전략 확정.

## §F. 참조

- `spec.md` (요구사항 SSOT), `acceptance.md` (인수 시나리오)
- 의존 SPEC: `.moai/specs/SPEC-PDF-001/spec.md` (`pdf_to_markdown()` 재사용)
- 관련 SPEC: `.moai/specs/SPEC-GEN-001/spec.md`
