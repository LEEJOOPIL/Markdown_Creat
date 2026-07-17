---
id: SPEC-OCR-001
title: "OCR 코어 모듈 — 이미지·PDF 텍스트 추출 (한국어 지원)"
version: "0.1.0"
status: draft
created: 2026-07-17
updated: 2026-07-17
author: manager-spec
priority: P1
phase: "v0.1.0 target"
module: "src/markdown_creat"
lifecycle: spec-anchored
tags: "ocr, tesseract, pdf, markdown, korean, extraction, shared-module"
tier: M
depends_on: [SPEC-PDF-001, SPEC-TELEGRAM-001]
---

# SPEC-OCR-001 — OCR 코어 모듈: 이미지·PDF 텍스트 추출 (한국어 지원)

## HISTORY

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 0.1.0 | 2026-07-17 | manager-spec | 최초 초안 작성. 사진·PDF 공용 OCR 코어 모듈(`src/markdown_creat/ocr.py`) 신설, `pdf_to_markdown()` 자동 OCR 폴백 도입, 한국어(Tesseract `kor`) 지원 추가. Tier M. |

---

## §A. 개요 (Context)

`markdown_creat`는 문서·이미지·메시지를 표준화된 마크다운으로 다루는 Python 도구이다. 현재 OCR 기능은 SPEC-TELEGRAM-001의 `telegram_bot/ocr.py`에 텔레그램 사진 첨부 전용으로 한정되어 존재하며, PDF 경로(SPEC-PDF-001의 `pdf_to_markdown()`)는 스캔·이미지 전용 PDF(추출 가능한 텍스트가 없는 PDF)를 만나면 OCR을 시도하지 않고 `PDFNoTextError`를 발생시킨다(REQ-PDF-009, §Exclusions — OCR).

사용자가 텔레그램 봇으로 스캔된 PDF(`telegram-notes/files/2026-07-16_123156_7_52.pdf`, 1페이지, 추출 텍스트 0자, 임베디드 이미지 1개 — 직접 확인됨)를 전송했을 때 텍스트 추출이 실패한 사건이 본 SPEC의 직접적인 동기이다. 사용자는 다음 세 가지 아키텍처 결정을 이미 확정했다(AskUserQuestion을 통해 승인, 재검토 대상 아님):

1. **배치 위치**: OCR을 `src/markdown_creat/ocr.py`(최상위 공유/코어 모듈)로 승격한다. `telegram_bot/` 하위에 두지 않는다 — 텔레그램 봇과 PDF 파이프라인, 그리고 향후 기능(예: 아직 미구현인 SPEC-GEN-001 템플릿 생성기)이 모두 재사용할 수 있어야 한다.
2. **트리거 동작**: 자동 폴백. `pdf_to_markdown()`이 기존이라면 `PDFNoTextError`를 발생시켰을 상황(추출 가능한 텍스트 없음)에서, 예외를 즉시 발생시키기 전에 PDF의 페이지 이미지에 대해 자동으로 OCR을 시도한다. 별도의 옵트인 플래그는 없다 — 이것이 새로운 기본 동작이다.
3. **언어 지원**: 기존 영어 전용 OCR에 더해 한국어(Tesseract `kor` 언어팩) 지원을 추가한다. Tesseract `kor` traineddata는 시스템 레벨 사전 요구사항(pip 패키지가 아님)으로 README에 문서화한다.

### 기존 코드 인벤토리 (직접 확인됨, 라인 정확)

- `src/markdown_creat/pdf_to_markdown.py` — SPEC-PDF-001, `status: completed`. 공개 함수 `pdf_to_markdown(pdf_path: str, output_path: str) -> None` (라인 62). `PDFNotFoundError` · `PDFCorruptedError` · `PDFEncryptedError` · `PDFNoTextError`(모두 `MarkdownConversionError` 하위)를 발생시킨다. 현재는 OCR을 전혀 시도하지 않는다 — 텍스트 없는 PDF는 항상 `PDFNoTextError`를 발생시킨다(REQ-PDF-009).
- `src/markdown_creat/telegram_bot/ocr.py` — SPEC-TELEGRAM-001 범위. `extract_image_text(image_path: str) -> str`(라인 18-37)이 `pytesseract.image_to_string()`을 래핑하며 언어 파라미터를 지정하지 않는다(영어 기본값). 실패 시 `ImageOcrError`를 발생시키며, 텍스트를 인식하지 못하면(오류 아님) 빈 문자열을 반환한다. `ImageOcrError` 클래스는 라인 14.
- `src/markdown_creat/telegram_bot/extract.py` — `extract_pdf_text(pdf_path: str) -> str`(라인 24-39)이 임시 파일 브리지를 통해 `pdf_to_markdown()`을 감싼다(해당 함수는 파일 출력 전용이므로). `MarkdownConversionError`(`PDFNoTextError` 포함)를 감싸 `DocumentExtractionError`를 발생시킨다.
- `src/markdown_creat/telegram_bot/handlers.py` — `handle_photo_message`(라인 ~53-84)는 `extract_image_text`를 호출하고 빈 문자열이면 "추출 텍스트 없음" 노트로, `ImageOcrError`면 `_OCR_FAILED_NOTE`로 대체한다. `handle_document_message`(라인 87-119)는 `.pdf` 파일에 대해 `extract_pdf_text`를 호출하고 `DocumentExtractionError`면 `_PDF_EXTRACTION_FAILED_NOTE`로 대체한다. 두 핸들러 모두 `save_attachment()`로 원본을 항상 먼저 보존한다.
- `pyproject.toml` — 의존성: `pymupdf>=1.24`, `python-telegram-bot>=22.0`, `pytesseract>=0.3.13`. Python `>=3.10`.
- 테스트 패턴: `tests/test_telegram_ocr.py`는 `unittest.mock.patch("markdown_creat.telegram_bot.ocr.pytesseract.image_to_string", ...)` 형태로 `pytesseract`를 모킹한다(Tesseract는 외부 시스템이므로). `tests/test_pdf_to_markdown.py`는 PyMuPDF(fitz) 자체로 실제 PDF 픽스처를 생성한다(PyMuPDF는 테스트 대상 자체이므로 모킹하지 않음). 본 SPEC은 신규 코어 OCR 모듈에서 `pytesseract` 호출을 모킹하고, PyMuPDF 페이지 렌더링(`get_pixmap()`)은 SPEC-PDF-001과 동일하게 실제 픽스처로 검증하는 방향을 따른다(§C 참조).

### 핵심 설계 결정: SPEC-PDF-001 앰언드먼트 (완료된 SPEC의 공개 함수 동작 계약 변경)

`SPEC-PDF-001/spec.md`(frontmatter `status: completed`)는 §Exclusions에 다음 배제 항목을 명시적으로 갖고 있다:

> ### Out of Scope — OCR (스캔·이미지 전용 PDF)
> 스캔되었거나 이미지로만 구성된 PDF에 대한 광학 문자 인식(OCR)은 다루지 않는다. 이러한 입력은 REQ-PDF-009에 따라 "추출 텍스트 없음" 오류로 처리한다.

사용자가 확정한 결정 #2(자동 OCR 폴백)는 이 배제 항목을 직접적으로 뒤집는다. 본 SPEC은 **경로 (b)**를 채택한다 — SPEC-OCR-001 자체가 SPEC-PDF-001의 앰언드먼트(`amendment_of`)가 되는 것이 아니라, **`pdf_to_markdown()`의 공개 함수 동작 계약이 변경되므로 SPEC-PDF-001 자체가 `completed → in-progress (amendment)` 전환을 거쳐야 한다.** 근거와 대안 검토는 `plan.md §B 핵심 아키텍처 결정 — SPEC-PDF-001 앰언드먼트 경로`에 상세히 기술한다.

본 SPEC(SPEC-OCR-001)은 `depends_on: [SPEC-PDF-001, SPEC-TELEGRAM-001]`을 선언하며, 자신의 구현(run-phase)이 시작되기 전에 SPEC-PDF-001의 앰언드먼트(REQ-PDF-009 문구 갱신 + `## Amendments` HISTORY 서브섹션 + `completed → in-progress` 전환)가 **manager-spec에 의해 별도로 수행**되어야 함을 전제 조건으로 명시한다(plan.md M2 참조). 이 앰언드먼트 자체는 본 SPEC의 3개 산출물(spec.md/plan.md/acceptance.md) 범위 밖이며, SPEC-PDF-001 자신의 `.moai/specs/SPEC-PDF-001/` 파일에서 별도로 수행된다.

### SPEC-TELEGRAM-001과의 관계 (앰언드먼트 불필요)

SPEC-TELEGRAM-001(`status: completed`, `depends_on: [SPEC-PDF-001]`)은 REQ-TELEGRAM-007(사진 OCR)을 자체적으로 정의하며 spec.md 43행에서 "이미지 OCR은 SPEC-PDF-001이 명시적으로 제외한 범위이므로 본 SPEC에서 신규 정의한다"고 명시한다. 본 SPEC은 `telegram_bot/ocr.py`의 **공개 계약(함수 시그니처 `extract_image_text(image_path: str) -> str`, 예외 타입 `ImageOcrError`, 관찰 가능한 동작)을 그대로 유지**하면서 내부 구현만 신규 코어 모듈(`markdown_creat.ocr`)에 위임하는 **얇은 재노출(thin re-export)**로 전환한다(§B REQ-OCR-012, 013). 이는 SPEC-TELEGRAM-001의 공개 계약을 변경하지 않으므로 SPEC-TELEGRAM-001은 앰언드먼트 대상이 아니다.

다만 `tests/test_telegram_ocr.py`는 현재 `unittest.mock.patch("markdown_creat.telegram_bot.ocr.pytesseract.image_to_string", ...)` 형태로 `pytesseract`를 `telegram_bot.ocr` 네임스페이스에서 직접 모킹한다. 재노출 전환 후 실제 `pytesseract` 호출은 `markdown_creat.ocr` 모듈 내부로 이동하므로, 이 테스트 파일의 모킹 대상 경로를 `markdown_creat.ocr.pytesseract.image_to_string`로 갱신해야 한다(plan.md M4 참조). 이는 테스트 파일의 기계적 갱신이며 REQ-TELEGRAM-007의 관찰 가능한 동작 자체는 변경되지 않으므로 SPEC-TELEGRAM-001 body/frontmatter 앰언드먼트를 요구하지 않는다.

제안 공개 인터페이스(형태는 plan.md M1에서 확정):

```python
def extract_image_text(image_path: str, lang: str = "eng") -> str: ...
def extract_pdf_text_via_ocr(pdf_path: str, lang: str = "eng") -> str: ...
```

기술 기반: Python 3.10+, 기존 의존성(`pymupdf`, `pytesseract`)만 재사용하며 신규 pip 의존성을 추가하지 않는다(§C 참조). Tesseract `kor` traineddata는 시스템 레벨 사전 요구사항이다.

---

## §B. 요구사항 (EARS/GEARS Requirements)

### 코어 OCR 모듈 — 이미지 텍스트 추출 (기존 REQ-TELEGRAM-007 일반화)

- **REQ-OCR-001 (Ubiquitous)**: The system shall 이미지 파일 경로가 주어지면 Tesseract OCR을 통해 해당 이미지의 텍스트를 추출하는 코어 함수를 `src/markdown_creat/ocr.py`에 제공한다.
- **REQ-OCR-002 (Event-driven)**: When OCR 대상 이미지에서 인식 가능한 텍스트가 없으면, the system shall 오류를 발생시키지 않고 빈 문자열을 반환한다.
- **REQ-OCR-003 (Event-driven / unwanted)**: When Tesseract 엔진 자체의 오류(미설치, 실행 실패 등)가 발생하면, the system shall `OcrError`를 발생시킨다.

### 코어 OCR 모듈 — PDF 페이지 이미지 텍스트 추출 (신규)

- **REQ-OCR-004 (Ubiquitous)**: The system shall PDF 파일 경로가 주어지면 각 페이지를 이미지로 렌더링한 뒤 OCR로 텍스트를 추출하여 페이지 순서대로 병합하는 코어 함수를 `src/markdown_creat/ocr.py`에 제공한다.
- **REQ-OCR-005 (Event-driven / unwanted)**: When PDF 페이지 렌더링 또는 렌더링된 페이지 이미지의 OCR 중 오류가 발생하면, the system shall `OcrError`를 발생시킨다.

### 다국어 지원 — 한국어

- **REQ-OCR-006 (Where)**: Where OCR 함수 호출 시 언어 파라미터가 지정되지 않으면, the system shall 기본값으로 영어("eng")를 사용한다.
- **REQ-OCR-007 (Where)**: Where OCR 함수 호출 시 언어 파라미터로 한국어("kor" 또는 "kor+eng")가 지정되면, the system shall 해당 Tesseract 언어팩으로 OCR을 수행한다.
- **REQ-OCR-008 (Event-driven / unwanted)**: When 지정된 Tesseract 언어팩(예: "kor")이 시스템에 설치되어 있지 않으면, the system shall 어떤 언어팩이 누락되었는지 식별 가능한 명확한 오류를 발생시키며, 조용히 영어로 대체하거나 빈 결과를 반환하지 않는다.

### `pdf_to_markdown()` 자동 OCR 폴백 (SPEC-PDF-001 동작 계약 변경 — §A 앰언드먼트 참조)

- **REQ-OCR-009 (Event-driven)**: When `pdf_to_markdown()` 호출 시 PDF에서 추출 가능한 텍스트가 없으면(기존 REQ-PDF-009 조건 충족), the system shall `PDFNoTextError`를 즉시 발생시키기 전에 해당 PDF의 페이지 이미지에 대해 코어 OCR 모듈을 통한 자동 OCR을 시도한다.
- **REQ-OCR-010 (Event-driven)**: When 자동 OCR 폴백이 비어 있지 않은 텍스트를 성공적으로 추출하면, the system shall 추출된 OCR 텍스트로 마크다운 본문을 구성하여 지정된 출력 경로에 UTF-8 `.md` 파일을 기록한다.
- **REQ-OCR-011 (Event-driven / unwanted)**: When 자동 OCR 폴백을 시도했음에도 텍스트를 추출하지 못하면(OCR 결과가 비어 있거나 OCR 자체가 실패), the system shall `PDFNoTextError`를 발생시키며 빈 `.md` 파일이나 부분적으로 기록된 파일을 출력 경로에 남기지 않는다.
- **REQ-OCR-012 (Ubiquitous)**: The system shall `pdf_to_markdown()`의 자동 OCR 폴백 시도 여부와 무관하게, 오류 발생 시 출력 경로에 불완전하거나 부분적으로 기록된 `.md` 파일을 남기지 않는다(기존 REQ-PDF-010 불변식 유지).

### 재사용 및 하위 호환 (텔레그램 봇)

- **REQ-OCR-013 (Ubiquitous)**: The system shall `telegram_bot/ocr.py`의 `extract_image_text()` 함수와 `ImageOcrError` 예외를 신규 코어 OCR 모듈의 얇은 재노출(re-export)로 제공하며, 기존 호출자(`handlers.py`)의 임포트 경로와 관찰 가능한 동작(시그니처, 반환값, 예외 발생 조건)을 그대로 유지한다.
- **REQ-OCR-014 (Unwanted)**: The system shall `telegram_bot/ocr.py` 내부에서 OCR 파싱 로직(Tesseract 호출 로직)을 재구현하지 않는다.

---

## §C. 제약 및 품질 게이트 (Constraints)

- Python 3.10+, 기존 의존성(`pymupdf>=1.24`, `pytesseract>=0.3.13`)만 사용한다. 신규 pip 의존성을 `pyproject.toml`에 추가하지 않는다(PDF 페이지 → 이미지 변환은 PyMuPDF의 `page.get_pixmap()`으로 처리하며, 임시 파일 경유 방식을 사용해 PIL 직접 임포트를 피한다 — plan.md M3에서 확정).
- Tesseract OCR 엔진은 시스템 레벨 외부 바이너리이며, 한국어 지원을 위한 `kor` traineddata는 별도의 시스템 레벨 설치가 필요하다(pip 패키지 아님). README에 설치 방법을 문서화한다(REQ-OCR-008 관련).
- 개발 방법론: `quality.yaml`의 `constitution.development_mode: tdd`(RED-GREEN-REFACTOR).
- 품질 게이트: `ruff`(린트) + `black`(포맷) + `pytest`(테스트), 커버리지 85% 이상. Tesseract·PyMuPDF의 외부 바이너리/네트워크 의존은 없으나, `pytesseract.image_to_string()` 호출은 신규 코어 모듈 테스트에서 모킹으로 격리한다(Tesseract 실행 파일은 CI 환경에 없을 수 있음). PyMuPDF의 `get_pixmap()` 페이지 렌더링은 SPEC-PDF-001과 동일하게 실제 픽스처로 검증한다(모킹하지 않음 — PyMuPDF 자체는 테스트 대상 경로의 일부).
- 출력 인코딩은 UTF-8로 고정한다(한글 문서·OCR 결과 대응).
- 코드 식별자·함수명·기술 용어는 영어로 작성한다(언어 정책).
- 본 SPEC은 `depends_on: [SPEC-PDF-001, SPEC-TELEGRAM-001]`을 선언한다. `/moai run` 시 Depends_on Pre-flight Check가 두 의존 SPEC의 `status: completed`를 확인한다.
- **선행 조건(run-phase 진입 전)**: SPEC-PDF-001의 REQ-PDF-009 앰언드먼트(`completed → in-progress (amendment)` 전환, `## Amendments` HISTORY 서브섹션 추가)가 manager-spec에 의해 별도로 완료되어야 한다(plan.md M2). 이 전환이 완료되지 않은 상태에서 manager-develop이 `pdf_to_markdown.py`의 동작을 변경하면 SPEC Artifact Ownership 경계(spec.md body 수정 금지)를 위반하므로, 완료되지 않았을 경우 manager-develop은 blocker report를 반환해야 한다.

---

## §Exclusions / 만들지 않는 것 (What NOT to Build)

본 SPEC은 사진·PDF 공용 OCR 코어 모듈과 `pdf_to_markdown()`의 자동 OCR 폴백에만 집중한다. 아래 항목은 명시적으로 범위 밖이다.

### Out of Scope — 한국어·영어 외 추가 언어
- 일본어, 중국어 등 한국어·영어 외 Tesseract 언어팩 지원은 본 SPEC에서 구현하지 않는다. 향후 별도 SPEC에서 언어 파라미터를 확장할 수 있다.

### Out of Scope — OCR 정확도 튜닝 / 이미지 전처리
- 이진화(binarization), 노이즈 제거, 기울기 보정(deskew) 등 OCR 정확도를 높이기 위한 이미지 전처리 파이프라인은 구현하지 않는다. Tesseract 기본 설정 + PyMuPDF 기본 렌더링 해상도(plan.md M3에서 확정)만 사용한다.

### Out of Scope — Tesseract / 언어팩 자동 설치
- Tesseract 엔진이나 `kor` 언어팩의 자동 설치, 패키지 관리자 연동은 구현하지 않는다. 시스템 레벨 사전 요구사항으로 README에 문서화하는 것에 한정한다.

### Out of Scope — 표 추출 / 이미지·도표 추출 (SPEC-PDF-001 배제 상속)
- PDF·이미지 내 표(table) 감지, 도표(figure) 추출·임베딩은 본 SPEC의 범위가 아니다(SPEC-PDF-001 §Exclusions 상속).

### Out of Scope — 배치/다중 파일 처리 (SPEC-PDF-001 배제 상속)
- 여러 파일을 일괄 OCR 처리하는 배치 기능은 범위 밖이다.

### Out of Scope — CLI 및 GUI (SPEC-PDF-001 배제 상속)
- 커맨드라인 진입점, 인자 파싱, GUI는 본 SPEC에서 구현하지 않는다. 코어 라이브러리 함수로만 제공한다.

### Out of Scope — 접근 제어 / 노트 조회 UI (SPEC-TELEGRAM-001 배제 상속)
- 텔레그램 봇의 접근 제어(allowlist), 노트 조회 UI·대시보드는 본 SPEC의 범위가 아니다.

---

## §E. 참조 (Cross-References)

- 프로젝트 문서: `.moai/project/product.md`, `.moai/project/structure.md`, `.moai/project/tech.md` (주의: 세 문서 모두 그린필드 시점 계획안으로 stale — 실제 코드베이스가 authoritative)
- 의존 SPEC(공개 함수 동작 계약 변경 — 별도 앰언드먼트 필요): `.moai/specs/SPEC-PDF-001/spec.md` (`pdf_to_markdown(pdf_path, output_path)`)
- 의존 SPEC(재노출 대상, 앰언드먼트 불필요): `.moai/specs/SPEC-TELEGRAM-001/spec.md` (`telegram_bot/ocr.py`)
- 품질 설정: `.moai/config/sections/quality.yaml`
- 구현 계획: `plan.md`
- 상세 인수 기준: `acceptance.md`
