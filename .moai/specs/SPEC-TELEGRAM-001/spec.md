---
id: SPEC-TELEGRAM-001
title: "텔레그램 → 마크다운 저장 봇"
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

# SPEC-TELEGRAM-001 — 텔레그램 → 마크다운 저장 봇

## HISTORY

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 0.1.0 | 2026-07-15 | manager-spec | 최초 초안 작성. 텔레그램 봇이 수신한 텍스트·사진·문서 메시지를 날짜 폴더 기반 `.md`로 저장. long polling, 봇 토큰 환경변수 주입, 사진 OCR(신규 범위), PDF 텍스트 추출은 SPEC-PDF-001 재사용. Tier M. |

---

## §A. 개요 (Context)

`markdown_creat`는 문서를 표준화된 마크다운으로 다루는 Python 도구이다. SPEC-GEN-001(템플릿 → `.md` 생성)과 SPEC-PDF-001(PDF → `.md` 변환)이 로컬 파일을 입력으로 삼는 반면, 본 SPEC은 **텔레그램 메시지를 입력원으로** 삼아 수신한 내용을 자동으로 마크다운 노트로 축적하는 **상시 실행 봇**을 정의한다.

- **입력**: 개인 텔레그램 봇(BotFather로 생성)에게 전송된 메시지 — 플레인 텍스트, 사진(이미지), 문서(PDF 등 파일)
- **동작**: long polling으로 메시지를 상시 수신하고, 메시지 유형별로 처리하여 날짜 기반 폴더 구조에 메시지당 하나의 `.md` 파일을 저장한다. 첨부 원본은 별도 폴더에 보관하고, 추출 가능한 텍스트(문서 텍스트·이미지 OCR)는 `.md` 본문에 포함한다.
- **출력**: `telegram-notes/YYYY-MM-DD/` 하위의 타임스탬프 기반 `.md` 파일들 + 첨부 원본을 담는 `files/` 하위 폴더

본 봇은 로컬/개인용으로, 수동 실행(`python -m ...` 또는 실행 스크립트)을 전제로 한다. 실행 라이브러리는 `python-telegram-bot`, 이미지 OCR은 `pytesseract` + Tesseract OCR 엔진을 사용한다.

### PDF 텍스트 추출 재사용 (SPEC-PDF-001 의존)

PDF/문서 첨부의 텍스트 추출은 **SPEC-PDF-001의 `pdf_to_markdown(pdf_path, output_path)` 공개 함수를 재사용**한다. 본 SPEC은 PDF 파싱 로직을 재구현하지 않는다. SPEC-PDF-001이 아직 구현되지 않았으므로 frontmatter에 `depends_on: [SPEC-PDF-001]`을 기록하여, run-phase의 Depends_on Pre-flight Check가 미충족 의존성을 사용자에게 노출(wait/override/abort)하도록 한다. (이미지 OCR은 SPEC-PDF-001이 명시적으로 제외한 범위이므로 본 SPEC에서 신규 정의한다 — §B REQ-TELEGRAM-007.)

기술 기반: Python 3.10+, `src/` 레이아웃(`src/markdown_creat/telegram_bot/`), 봇 라이브러리 `python-telegram-bot`, OCR `pytesseract` + Tesseract 엔진. 개발 방법론은 `quality.yaml`의 `constitution.development_mode: tdd`(RED-GREEN-REFACTOR)를 따른다.

---

## §B. 요구사항 (EARS Requirements)

### 봇 실행 및 연결

- **REQ-TELEGRAM-001 (Ubiquitous)**: The bot shall long polling 방식으로 텔레그램 서버에서 메시지를 지속적으로 수신하며, webhook 방식을 사용하지 않는다.
- **REQ-TELEGRAM-002 (Ubiquitous)**: The bot shall 봇 토큰을 환경변수(`TELEGRAM_BOT_TOKEN`) 또는 gitignored `.env` 파일에서 읽으며, 토큰을 소스코드에 하드코딩하거나 버전 관리에 커밋하지 않는다.
- **REQ-TELEGRAM-003 (Event-driven / unwanted)**: When 봇 시작 시 봇 토큰이 설정되어 있지 않으면, the bot shall 어떤 설정이 누락되었는지 알리는 명확한 오류 메시지와 함께 즉시 종료(fail fast)하며, 조용히 멈추거나 무한 대기하지 않는다.

### 텍스트 메시지 처리

- **REQ-TELEGRAM-004 (Event-driven)**: When 봇이 플레인 텍스트 메시지를 수신하면, the bot shall 해당 텍스트를 본문으로 하는 `.md` 파일 하나를 저장한다.

### 첨부파일 처리 (사진·문서)

- **REQ-TELEGRAM-005 (Event-driven)**: When 봇이 첨부파일(사진 또는 문서)을 수신하면, the bot shall 원본 파일을 로컬 `files/` 하위 폴더에 원본 그대로 항상 저장한다.
- **REQ-TELEGRAM-006 (Event-driven)**: When 봇이 PDF/문서 첨부를 수신하면, the bot shall 원본 저장(REQ-TELEGRAM-005)에 더해 SPEC-PDF-001의 `pdf_to_markdown()`를 재사용하여 추출한 텍스트를 해당 메시지의 `.md` 본문에 포함한다.
- **REQ-TELEGRAM-007 (Event-driven)**: When 봇이 사진(이미지) 첨부를 수신하면, the bot shall 원본 저장(REQ-TELEGRAM-005)에 더해 이미지 내 텍스트를 OCR(`pytesseract` + Tesseract 엔진)로 추출하여 해당 메시지의 `.md` 본문에 포함한다.

### 저장 구조

- **REQ-TELEGRAM-008 (Ubiquitous)**: The bot shall 저장하는 각 메시지를 날짜 기반 폴더(`YYYY-MM-DD/`) 하위에 타임스탬프 기반 파일명(예: `YYYY-MM-DD_HHMMSS.md`)의 `.md` 파일 하나로 저장한다. 기본 베이스 폴더는 프로젝트 루트의 `telegram-notes/`이며, 설정으로 변경 가능하다.
- **REQ-TELEGRAM-009 (Ubiquitous)**: The bot shall 각 `.md` 파일에 최소한 메시지 타임스탬프, 발신자/채팅 컨텍스트(가용 시), 텍스트/추출 텍스트 본문을 기록하며, 첨부는 `files/`에 저장된 파일의 경로로 링크한다.

### 오류 처리 (Unwanted Behavior)

- **REQ-TELEGRAM-010 (Event-driven / unwanted)**: When 텔레그램 API 또는 네트워크 오류가 발생하면, the bot shall 폴링 루프를 조용히 크래시시키지 않고 오류를 기록한 뒤 폴링을 계속한다.
- **REQ-TELEGRAM-011 (Event-driven / unwanted)**: When OCR 또는 PDF 텍스트 추출이 실패하면, the bot shall 원본 파일 저장(REQ-TELEGRAM-005)과 "추출 실패"를 알리는 노트를 포함한 `.md` 파일을 저장하며, 메시지 전체를 잃지 않는다.
- **REQ-TELEGRAM-012 (Ubiquitous / unwanted)**: The bot shall 봇 토큰 등 비밀 값을 저장된 `.md` 파일이나 로그에 기록하지 않는다.

---

## §C. 제약 및 품질 게이트 (Constraints)

- Python 3.10+, `src/` 레이아웃. 봇 라이브러리는 `python-telegram-bot`, 이미지 OCR은 `pytesseract` + Tesseract 엔진을 사용한다. Tesseract는 시스템 레벨 외부 바이너리 의존이므로 미설치 시의 동작을 REQ-TELEGRAM-011(추출 실패 → 원본 보존)로 흡수한다.
- PDF 텍스트 추출은 SPEC-PDF-001의 `pdf_to_markdown()`를 재사용한다. PDF 파싱 로직을 재구현하지 않는다(§Exclusions 참조). 본 SPEC은 `depends_on: [SPEC-PDF-001]`을 선언한다.
- 개발 방법론: `quality.yaml`의 `constitution.development_mode: tdd`(RED-GREEN-REFACTOR).
- 품질 게이트: `ruff`(린트) + `black`(포맷) + `pytest`(테스트), 커버리지 85% 이상. 외부 네트워크(텔레그램 API)·Tesseract·PyMuPDF 의존은 테스트에서 목/스텁으로 격리한다.
- 출력 인코딩은 UTF-8로 고정한다(한글 메시지 대응).
- 봇 토큰은 환경변수 또는 gitignored `.env`로만 주입한다. `.env`는 `.gitignore`에 포함되어야 한다.
- 코드 식별자·함수명·기술 용어는 영어로 작성한다(언어 정책).

---

## §Exclusions / 만들지 않는 것 (What NOT to Build)

본 SPEC은 "수신한 메시지를 로컬 마크다운 노트로 저장하는 상시 봇" 코어 기능에 집중한다. 아래 항목은 명시적으로 범위 밖이다.

### Out of Scope — 자동 시작 / OS 서비스 등록
- 부팅 시 자동 시작, Windows 서비스 등록, 작업 스케줄러(task scheduler) 연동은 구현하지 않는다. 봇은 수동 실행(`python -m ...` 또는 실행 스크립트)만 지원한다.

### Out of Scope — Webhook 모드
- webhook 방식 수신은 다루지 않는다. long polling만 지원한다(REQ-TELEGRAM-001).

### Out of Scope — 접근 제어 (allowlist/denylist)
- 다중 사용자/다중 채팅에 대한 접근 제어 로직은 구현하지 않는다. 봇과 대화하는 모든 채팅의 메시지가 저장된다. 무제한 접근이 리스크가 될 수 있는 점은 plan.md §E 리스크로 기록하되, allowlist/denylist 기능은 만들지 않는다.

### Out of Scope — 노트 조회 UI / 대시보드
- 저장된 노트를 열람·검색하는 웹 UI나 대시보드는 구현하지 않는다.

### Out of Scope — 클라우드 동기화 / 백업
- `telegram-notes/` 폴더의 클라우드 동기화나 백업은 다루지 않는다.

### Out of Scope — PDF 파싱 재구현
- PDF 텍스트 추출 로직을 새로 구현하지 않는다. SPEC-PDF-001의 `pdf_to_markdown()`를 재사용한다(REQ-TELEGRAM-006).

---

## §E. 참조 (Cross-References)

- 프로젝트 문서: `.moai/project/product.md`, `.moai/project/structure.md`, `.moai/project/tech.md`
- 의존 SPEC(PDF 텍스트 추출 재사용): `.moai/specs/SPEC-PDF-001/spec.md` (`pdf_to_markdown(pdf_path, output_path)`)
- 관련 SPEC(순방향 생성): `.moai/specs/SPEC-GEN-001/spec.md`
- 품질 설정: `.moai/config/sections/quality.yaml`
- 구현 계획: `plan.md`
- 상세 인수 기준: `acceptance.md`
