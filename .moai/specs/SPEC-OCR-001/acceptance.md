---
id: SPEC-OCR-001
title: "OCR 코어 모듈 — 이미지·PDF 텍스트 추출 (한국어 지원) — 인수 기준"
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

# SPEC-OCR-001 — 인수 기준 (acceptance.md)

## §D. 인수 시나리오 (GEARS)

### AC-OCR-001a — 이미지 OCR 텍스트 추출 성공 (REQ-OCR-001)
- **Given** 텍스트를 담은 이미지 파일이 존재하고,
- **When** 코어 OCR 모듈의 `extract_image_text(image_path)`를 호출하면,
- **Then** Tesseract OCR로 추출된 텍스트 문자열이 반환된다(`pytesseract.image_to_string` 모킹).

### AC-OCR-001b — 텍스트 없는 이미지 → 빈 문자열, 오류 아님 (REQ-OCR-002)
- **Given** 인식 가능한 텍스트가 없는 이미지가 주어지고,
- **When** `extract_image_text(image_path)`를 호출하면,
- **Then** 오류 없이 빈 문자열이 반환된다.

### AC-OCR-001c — Tesseract 엔진 오류 시 OcrError (REQ-OCR-003)
- **Given** Tesseract 엔진 자체가 실패하는 상황(미설치 시뮬레이션)이 주어지고,
- **When** `extract_image_text(image_path)`를 호출하면,
- **Then** `OcrError`가 발생한다.

### AC-OCR-002a — PDF 페이지 이미지 OCR 텍스트 추출 (REQ-OCR-004)
- **Given** 텍스트 레이어가 없는(스캔·이미지 전용) PDF 파일이 존재하고,
- **When** `extract_pdf_text_via_ocr(pdf_path)`를 호출하면,
- **Then** 각 페이지가 이미지로 렌더링된 뒤 OCR로 텍스트가 추출되어 페이지 순서대로 병합된 문자열이 반환된다.

### AC-OCR-002b — PDF 페이지 렌더링/OCR 실패 시 OcrError (REQ-OCR-005)
- **Given** PDF 페이지 렌더링 또는 렌더링된 이미지의 OCR 중 오류가 발생하는 상황이 주어지고,
- **When** `extract_pdf_text_via_ocr(pdf_path)`를 호출하면,
- **Then** `OcrError`가 발생한다.

### AC-OCR-003a — 언어 파라미터 미지정 시 영어 기본값 (REQ-OCR-006)
- **When** `extract_image_text(image_path)`를 언어 파라미터 없이 호출하면,
- **Then** Tesseract 호출이 기본 언어(`"eng"`)로 수행된다(`pytesseract.image_to_string` 호출 인자 검증).

### AC-OCR-003b — 한국어 언어팩 지정 시 사용 (REQ-OCR-007)
- **When** `extract_image_text(image_path, lang="kor")` 또는 `lang="kor+eng"`로 호출하면,
- **Then** Tesseract 호출이 지정된 언어 파라미터로 수행된다(`pytesseract.image_to_string` 호출 인자 검증).

### AC-OCR-003c — 언어팩 미설치 시 명확한 오류 (REQ-OCR-008)
- **Given** Tesseract가 지정된 언어팩(예: `"kor"`)의 traineddata를 찾지 못하는 상황(pytesseract가 언어팩 누락 오류를 발생시키는 상황을 시뮬레이션)이 주어지고,
- **When** `extract_image_text(image_path, lang="kor")`를 호출하면,
- **Then** `OcrError`가 발생하며, 예외 메시지에 어떤 언어팩이 누락되었는지 식별 가능한 정보(원본 pytesseract 오류 메시지)가 포함된다; 조용히 영어로 대체되거나 빈 문자열이 반환되지 않는다.

### AC-OCR-004a — 텍스트 없는 PDF 자동 OCR 폴백 성공 (REQ-OCR-009, 010)
- **Given** 추출 가능한 텍스트가 없는(스캔·이미지 전용) PDF 파일이 존재하고 자동 OCR 폴백이 비어 있지 않은 텍스트를 추출할 수 있는 상황이 주어지고,
- **When** `pdf_to_markdown(pdf_path, output_path)`를 호출하면,
- **Then** `PDFNoTextError`가 발생하지 않고, OCR로 추출된 텍스트를 본문으로 하는 UTF-8 `.md` 파일이 `output_path`에 생성된다.

### AC-OCR-004b — OCR 폴백도 실패 시 PDFNoTextError, 부분 파일 없음 (REQ-OCR-011, 012)
- **Given** 추출 가능한 텍스트가 없는 PDF 파일이 존재하고 자동 OCR 폴백 또한 텍스트를 추출하지 못하는(빈 결과 또는 OCR 자체 실패) 상황이 주어지고,
- **When** `pdf_to_markdown(pdf_path, output_path)`를 호출하면,
- **Then** `PDFNoTextError`가 발생하며, `output_path`에 빈 파일이나 부분적으로 기록된 파일이 남지 않는다.

### AC-OCR-005a — 텔레그램 봇 재노출 하위 호환성 (REQ-OCR-013, 014)
- **Given** `telegram_bot/ocr.py`가 코어 OCR 모듈의 재노출로 전환된 상태에서,
- **When** 기존 `handlers.py`의 임포트 경로(`from markdown_creat.telegram_bot.ocr import extract_image_text, ImageOcrError`)로 호출하면,
- **Then** 시그니처(`extract_image_text(image_path: str) -> str`), 반환값, 예외 발생 조건이 SPEC-TELEGRAM-001 완료 시점과 동일하게 관찰되며, `telegram_bot/ocr.py` 내부에 Tesseract 호출 로직이 재구현되어 있지 않다(코어 모듈 임포트만 존재).

## §D.1 엣지 케이스 (Edge Cases)

- PDF의 일부 페이지에만 텍스트가 있고 나머지는 이미지 전용인 경우 → 이는 `_build_markdown()`이 `None`이 아닌 결과를 반환하는 경우이므로(REQ-PDF-001~003 정상 경로), 본 SPEC의 자동 OCR 폴백(REQ-OCR-009)은 트리거되지 않는다 — 폴백은 오직 전체 문서에서 추출 가능한 텍스트가 전혀 없을 때만 작동한다(기존 REQ-PDF-009 조건과 동일).
- OCR로 추출된 텍스트에는 제목 구조 감지(폰트 크기 휴리스틱)가 적용되지 않는다 — OCR 결과는 문단으로만 구성된다(plan.md M1에서 확정). 이는 오류가 아니며, 이미지 기반 텍스트에는 폰트 메타데이터가 없어 원본 SPEC-PDF-001의 REQ-PDF-002 휴리스틱을 적용할 수 없기 때문이다.
- 한글 등 비ASCII OCR 결과 → UTF-8로 정확히 기록된다.
- 텔레그램 봇을 통해 스캔 PDF가 재전송되는 경우(사용자 보고 사건 재현) → `extract_pdf_text()`(`telegram_bot/extract.py`, 변경 없음)가 내부적으로 `pdf_to_markdown()`을 호출하므로, 자동 OCR 폴백이 투명하게 적용되어 이전에는 `DocumentExtractionError`로 처리되던 케이스가 이제 성공적으로 텍스트를 추출할 수 있다(단, OCR 결과가 비어 있으면 기존과 동일하게 `_PDF_EXTRACTION_FAILED_NOTE`로 처리됨).
- SPEC-PDF-001·SPEC-TELEGRAM-001 의존성 충족 확인 → 두 SPEC 모두 `status: completed`(SPEC-PDF-001은 M2 앰언드먼트 완료 후 `in-progress`를 거쳐 다시 `completed`로 복귀). Depends_on Pre-flight Check는 M2 완료 후 통과가 예상된다.

## §D.2 품질 게이트 / Definition of Done

- [ ] AC-OCR-001a~c, AC-OCR-002a~b, AC-OCR-003a~c, AC-OCR-004a~b, AC-OCR-005a 전 시나리오 통과.
- [ ] 테스트 커버리지 85% 이상 (`quality.yaml` `constitution.test_coverage_target`). `pytesseract`는 신규 코어 모듈 테스트에서 목/스텁으로 격리; PyMuPDF 페이지 렌더링은 실제 픽스처로 검증.
- [ ] `ruff` 린트 무경고, `black` 포맷 준수, `pytest` 전체 그린(기존 70개 텔레그램 테스트 + `test_pdf_to_markdown.py` 기존 테스트 포함, 회귀 없음).
- [ ] spec.md의 REQ-OCR-001~014가 각각 최소 1개 테스트로 검증됨(추적성).
- [ ] SPEC-PDF-001 앰언드먼트(M2)가 완료되어 REQ-PDF-009 문구가 자동 OCR 폴백을 반영하도록 갱신되고, HISTORY에 `## Amendments` 서브섹션이 존재함.
- [ ] `tests/test_telegram_ocr.py`의 모킹 대상 경로가 `markdown_creat.ocr.pytesseract.image_to_string`로 갱신되어 4개 기존 테스트가 계속 통과함.
- [ ] `telegram_bot/ocr.py`에 Tesseract 호출 로직이 재구현되지 않고 코어 모듈을 재노출함(§Exclusions 준수, REQ-OCR-014).
- [ ] README에 Tesseract `kor` traineddata 시스템 레벨 설치 안내가 문서화됨.
- [ ] `pyproject.toml`에 신규 pip 의존성이 추가되지 않음(§C 제약 준수).
