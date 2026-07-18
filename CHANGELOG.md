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
- **첨부파일 저장 경로 순회(Path Traversal) 취약점 수정** (SPEC-TELEGRAM-002,
  REQ-TELEGRAM-019~023, CWE-22): 텔레그램 API가 제공하는 공격자 제어 가능한
  `filename`을 정제 없이 저장 경로 조합에 사용하던 `save_attachment()`의
  취약점을 수정. `_sanitize_attachment_basename()` 헬퍼를 추가해 `/`와 `\`
  양쪽 구분자를 명시적으로 제거한 순수 basename만 저장 경로에 사용하도록
  했다(`pathlib`의 플랫폼 종속적 구분자 인식에 의존하지 않음). 상위 디렉토리
  이동(`..`), 절대 경로, Windows 드라이브 문자 형태 파일명을 모두 무력화하고,
  정제 결과가 비거나 `.`/`..`만 남으면 고정 폴백 파일명을 사용한다. 정상
  파일명(경로 구분자 없음)의 기존 `<timestamp>_<message_id>_<original-name>`
  명명 규칙과 비ASCII(한글 등) 파일명 보존은 회귀 없이 그대로 유지된다.
  `save_attachment()`의 공개 함수 시그니처는 변경되지 않았으며 `handlers.py`
  호출부도 수정하지 않았다. Reproduction-First TDD로 개발: 수정 전 코드를
  대상으로 한 익스플로잇 재현 테스트가 먼저 RED임을 확인한 뒤 GREEN 전환.
  4/4 인수 기준(AC-TELEGRAM-019a~d) 통과, `storage.py` 커버리지 100%, 기존
  회귀 스위트(31개 테스트) 전부 통과.

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
- **자동 OCR 폴백 통합** (SPEC-PDF-001 v0.2.0 앰언드먼트): `pdf_to_markdown()`이
  텍스트 레이어 없는 PDF(스캔·이미지 전용)를 만났을 때, 즉시 오류를 내는 대신
  SPEC-OCR-001의 `extract_pdf_text_via_ocr()`(언어 `kor+eng` 고정)를 자동으로
  호출해 OCR 텍스트를 시도한다.
  - OCR로 텍스트를 찾으면 문단으로만 구성된 `.md` 파일을 정상적으로 기록한다
    (OCR 결과에는 폰트 크기 정보가 없어 제목 구조는 감지하지 않음).
  - OCR로도 텍스트를 찾지 못하면 기존과 동일하게 `PDFNoTextError`를 발생시킨다
    (REQ-PDF-009, 동작 계약 재확인).
  - OCR 엔진 자체의 오류(Tesseract 미설치·언어팩 누락 등)는 신규 예외
    `PDFOCRFailedError`로 구분해 발생시킨다(REQ-PDF-011).
  - 텔레그램 봇의 PDF 처리 경로는 `pdf_to_markdown()`을 그대로 재사용하므로
    별도 수정 없이 이 동작을 그대로 상속받는다.
  - 신규 pip 의존성 없음(`pytesseract`는 SPEC-OCR-001에서 이미 추가됨).
  - 4개 신규 인수 기준(AC-PDF-003a~d) 통과, 기존 8개 인수 기준 회귀 없이
    재확인. `pdf_to_markdown.py` 커버리지 95%.
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
  - **후속(완료)**: PDF(스캔) 경로 자동 OCR 폴백 통합은 위 "자동 OCR 폴백
    통합" 항목(SPEC-PDF-001 v0.2.0 앰언드먼트)에서 완료되었다.
    `extract_pdf_text_via_ocr()`는 신규 로직 없이 그대로 재사용되었다.
  - 10/10 인수 기준 통과, `ocr.py` 테스트 커버리지 100%, 전체 테스트
    스위트 84/84 그린(기존 대비 회귀 없음).
- **텔레그램 봇 Windows 더블클릭 실행기** (`run_telegram_bot.bat`,
  SPEC-TELEGRAM-003): 터미널을 열지 않고도 Windows 탐색기에서 더블클릭만으로
  기존 텔레그램 봇(`python -m markdown_creat.telegram_bot`, SPEC-TELEGRAM-001)을
  실행할 수 있는 배치 파일 실행기를 프로젝트 루트에 추가. 봇 코어 로직이나
  토큰 로딩 로직(`config.py`)은 전혀 수정하지 않는 순수 실행기 레이어이다.
  - `%~dp0` 확장 변수로 자기 자신의 파일 위치로 작업 디렉토리를 고정(cwd
    앵커링)하여, 바탕화면 바로가기 등 어느 위치에서 실행해도 프로젝트 루트를
    기준으로 동일하게 동작한다.
  - venv 사전 점검: `.venv\Scripts\python.exe`가 없으면 평이한 언어의 오류
    메시지와 함께 봇 모듈을 호출하지 않고 즉시 실패(fail-fast)하며, 0이 아닌
    종료 코드로 종료한다.
  - 시스템 PATH에 의존하는 bare `python` 호출 없이 항상 venv 전용 Python
    인터프리터(`.venv\Scripts\python.exe`)로만 봇 모듈을 호출하며, 표준출력/
    표준오류를 가로채거나 억제하지 않는다.
  - 봇은 항상 launcher가 연 콘솔 창의 foreground에서 실행되며(OS 자동 시작·
    서비스 등록·백그라운드 데몬화 없음), 정상/비정상 종료 또는 venv 부재
    실패 등 모든 종료 경로 끝에서 `pause`로 콘솔 창을 유지해 출력을 읽을 수
    있게 한다.
  - 6개 인수 기준(AC-TELEGRAM-024a/027a/027b/030s/033s/034s) 중 3개
    (bare `python` 미사용, OS 자동 시작 미등록, 포그라운드 전용 실행)와
    venv 부재 시나리오(AC-TELEGRAM-027a)는 정적 스크립트 검토 및 스크래치
    복사본 실 실행으로 독립 검증되어 PASS. 정상 실행 경로(AC-TELEGRAM-024a)와
    토큰 부재 경로(AC-TELEGRAM-027b)는 실제 대화형 Windows 더블클릭 세션이
    필요한 long-polling 블로킹 특성상 자동화 에이전트가 끝까지 실행할 수
    없어, 명령·인자·출력 무리다이렉트를 라인 단위로 대조하는 정적 검토로만
    검증되었다 — `acceptance.md`의 Definition of Done에 따라 사람의 실제
    더블클릭 1회 검증이 남아 있다(예정된 잔여 검증이며 결함이 아님).
  - 신규 Python 소스 코드 변경, 신규 의존성 추가, 기존 테스트 스위트 회귀
    없음(`src/` 무변경 확인, 37개 텔레그램 관련 테스트 전부 통과).
