# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Security

- **Telegram 봇 토큰 로그 노출 차단** (SPEC-TELEGRAM-001, REQ-TELEGRAM-012):
  `httpx`가 요청 URL 전체를 INFO 레벨로 기록하고 `python-telegram-bot`은 그 URL에
  봇 토큰을 담기 때문에 raw 토큰이 로그에 남던 문제를 수정. 진입점
  (`telegram_bot/__main__.py`)에서 `httpx` 로거를 WARNING 레벨로 낮춰 억제한다.
  sync 이후 라이브 스모크 테스트 중 발견되었으며, 회귀 방지 테스트로 가드한다.

### Added

- `pdf_to_markdown(pdf_path, output_path)` (SPEC-PDF-001): converts a PDF file
  to a UTF-8 encoded Markdown file.
  - Extracts body text in reading order across all pages.
  - Detects heading structure via a font-size heuristic (levels 1-3).
  - Raises `PDFNotFoundError`, `PDFCorruptedError`, `PDFEncryptedError`, or
    `PDFNoTextError` for missing, corrupted, encrypted, or textless PDFs.
  - Never leaves a partial `.md` file on error (output is assembled in
    memory before the file is written).
  - Overwrites an existing file at `output_path`.
- **Telegram → Markdown bot** (`markdown_creat.telegram_bot`, SPEC-TELEGRAM-001):
  a long-polling bot that saves incoming text, photo, and PDF/document
  messages as dated Markdown notes.
  - Saves each received message as a single `.md` file under
    `telegram-notes/YYYY-MM-DD/` (timestamp-based filename), with a
    configurable base folder to replace the default.
  - Saves the original attachment (photo or document) under a `files/`
    subfolder, always, regardless of extraction success.
  - Extracts photo text via OCR (`pytesseract` + Tesseract engine) and merges
    it into the message's `.md` body.
  - Extracts PDF/document text by reusing SPEC-PDF-001's `pdf_to_markdown()`
    (no PDF-parsing logic reimplemented) and merges it into the message's
    `.md` body.
  - Reads the bot token from the `TELEGRAM_BOT_TOKEN` environment variable or
    a gitignored `.env` file; exits immediately with a clear error message if
    no token is configured (fail-fast), never hardcodes or logs the token.
  - Uses long polling only — no webhook registered.
  - On a Telegram API or network error, logs the error and continues polling
    instead of crashing.
  - On OCR or PDF extraction failure, saves the original attachment plus a
    `.md` note indicating extraction failure, so the message is never lost.
  - Adds `python-telegram-bot>=22.0` and `pytesseract>=0.3.13` as project
    dependencies; Tesseract OCR itself is a system-level binary not managed by
    pip.
  - Out of scope: auto-start/OS service registration, webhook mode, access
    control (allowlist/denylist), a note browsing UI, and cloud sync.
  - 10/10 acceptance criteria passing, 96% test coverage.
- **OCR 코어 모듈** (`markdown_creat.ocr`, SPEC-OCR-001): 이미지·PDF 페이지 OCR
  텍스트 추출을 위한 최상위 공유 코어 모듈.
  - `extract_image_text(image_path, lang="eng")` — 기존에 텔레그램 봇 전용이던
    이미지 OCR 로직을 공유 모듈로 일반화. 한국어 지원을 위한 `lang` 파라미터
    추가(`"kor"` 또는 `"kor+eng"` 지정 가능, 기본값은 기존과 동일한 `"eng"`).
  - `extract_pdf_text_via_ocr(pdf_path, lang="eng")` — 신규 함수. PyMuPDF로 PDF
    각 페이지를 이미지로 렌더링(`get_pixmap(dpi=300)`)한 뒤 OCR로 텍스트를
    추출하여 페이지 순서대로 병합. 임시 파일 경유 방식으로 구현하여 신규
    Pillow 의존성을 추가하지 않음.
  - 두 함수 모두 실패 시 `OcrError`를 발생시키며, 지정한 언어팩이 설치되어
    있지 않으면 원본 Tesseract 오류 메시지를 보존한 채 명확한 오류로
    처리한다(조용히 영어로 대체하거나 빈 결과를 반환하지 않음).
  - `telegram_bot/ocr.py`는 코어 모듈의 얇은 재노출(thin re-export)로 축소—
    기존 임포트 경로·함수 시그니처·예외(`ImageOcrError`)는 하위 호환을
    유지하며, OCR 파싱 로직은 재구현하지 않음.
  - 텔레그램 봇의 사진(이미지) 첨부 처리 경로(`handle_photo_message`)가
    `lang="kor+eng"`로 코어 OCR 함수를 호출하도록 배선되어, 사진 속 한국어
    텍스트가 저장되는 `.md` 본문에 종단 추출된다.
  - README에 Tesseract `kor` traineddata(시스템 레벨 설치 필요) 안내 추가.
  - 신규 pip 의존성 없음 — 기존 `pymupdf`, `pytesseract`만 재사용.
  - **참고(미인도 범위)**: PDF(스캔) 경로에서 `pdf_to_markdown()`이 텍스트
    없는 PDF를 만났을 때 자동으로 OCR을 시도하는 폴백 통합은 본 SPEC의
    범위 밖이며 아직 구현되지 않았다 — 향후 별도의 SPEC-PDF-001 앰언드먼트가
    다룰 예정이다. `extract_pdf_text_via_ocr()`는 그 통합이 사용할 코어
    함수로 미리 제공되었으나 아직 호출자가 없다.
  - 10/10 인수 기준 통과, `ocr.py` 테스트 커버리지 100%, 전체 테스트
    스위트 84/84 그린(기존 대비 회귀 없음).
