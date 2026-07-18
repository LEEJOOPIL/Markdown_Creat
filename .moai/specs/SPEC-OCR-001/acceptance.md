---
id: SPEC-OCR-001
title: "OCR 코어 모듈 — 이미지·PDF 텍스트 추출 (한국어 지원) — 인수 기준"
version: "0.3.0"
status: completed
created: 2026-07-17
updated: 2026-07-18
author: manager-spec
priority: P1
phase: "v0.1.0 target"
module: "src/markdown_creat"
lifecycle: spec-anchored
tags: "ocr, tesseract, pdf, markdown, korean, extraction, shared-module"
tier: M
depends_on: [SPEC-TELEGRAM-001]
---

# SPEC-OCR-001 — 인수 기준 (acceptance.md)

## §D. 인수 시나리오 (Given/When/Then)

> **AC-OCR-004a·004b는 의도적 결번이다.** 0.1.0에서 `pdf_to_markdown()` 자동 OCR 폴백 시나리오(REQ-OCR-009~012)로 사용되었으나, 0.2.0의 경로 (c) 재범위 조정으로 SPEC-PDF-001의 향후 앰언드먼트로 이관되었다(spec.md §Exclusions, plan.md §B). 남은 AC를 재번호하지 않는다 — REQ 결번과 동일한 근거로, 재번호하면 기존 식별자가 다른 의미로 조용히 재할당되어 추적성이 깨진다.

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

### AC-OCR-005a — 텔레그램 봇 재노출 하위 호환성 (REQ-OCR-013, 014)
- **Given** `telegram_bot/ocr.py`가 코어 OCR 모듈의 재노출로 전환된 상태에서,
- **When** 기존 `handlers.py`의 임포트 경로(`from markdown_creat.telegram_bot.ocr import extract_image_text, ImageOcrError`)로 호출하면,
- **Then** 시그니처(`extract_image_text(image_path: str) -> str`), 반환값, 예외 발생 조건이 SPEC-TELEGRAM-001 완료 시점과 동일하게 관찰되며, `telegram_bot/ocr.py` 내부에 Tesseract 호출 로직이 재구현되어 있지 않다(코어 모듈 임포트만 존재).

### AC-OCR-006a — 텔레그램 봇 사진 경로 한국어 종단 배선 (REQ-OCR-015)
- **Given** `pytesseract.image_to_string`가 한국어 텍스트를 반환하도록 모킹되고(외부 Tesseract 격리), 한국어 텍스트를 담은 사진 첨부가 주어지고,
- **When** 텔레그램 봇의 사진 처리 경로(`handlers.py`의 `handle_photo_message`)가 해당 첨부를 처리하면,
- **Then** (1) 코어 OCR 함수를 거쳐 모킹된 `pytesseract.image_to_string`에 **`lang="kor+eng"`** 인자가 도달하고(호출 인자 검증 — seam), (2) 모킹이 반환한 한국어 텍스트가 저장되는 `.md` 본문에 포함된다. *(검증은 seam에서 수행 — 실제 OCR 출력이 아니라 lang 인자 전달과 본문 반영을 단언한다.)*

## §D.1 엣지 케이스 (Edge Cases)

- `extract_pdf_text_via_ocr()`의 반환 계약은 **구조 없는 평문(페이지 순서 병합)** 이다 — 제목 구조 감지(폰트 크기 휴리스틱)를 적용하지 않는다. 이미지 기반 텍스트에는 폰트 메타데이터가 없기 때문이며, 오류가 아니다. 이 평문을 마크다운으로 어떻게 조립할지(제목 감지 적용 여부 등)는 호출자의 책임이며 본 SPEC의 범위 밖이다.
- PDF의 일부 페이지만 이미지이고 나머지에 텍스트 레이어가 있는 경우 → `extract_pdf_text_via_ocr()`는 호출되면 **모든** 페이지를 이미지로 렌더링해 OCR한다(REQ-OCR-004). 텍스트 레이어 유무에 따라 페이지를 선별하지 않는다. 이 함수를 언제 호출할지(예: 전체 문서에 추출 텍스트가 전혀 없을 때만)를 판단하는 것은 호출자의 책임이다.
- 한글 등 비ASCII OCR 결과 → 반환 문자열에 정확히 보존된다(파이썬 `str`, 손실·치환 없음). 파일 기록 시의 UTF-8 인코딩은 호출자 책임이다(본 SPEC의 코어 함수는 파일을 쓰지 않는다).
- SPEC-TELEGRAM-001 의존성 충족 확인 → `status: completed`. Depends_on Pre-flight Check는 추가 게이트 없이 통과가 예상된다(0.2.0에서 SPEC-PDF-001을 `depends_on`에서 제거하여 자기 무효화 전제조건을 해소 — plan.md §B 결함 1; "순환 의존"은 오기였음, 0.3.0 D1 정정).

## §D.2 품질 게이트 / Definition of Done

- [ ] AC-OCR-001a~c, AC-OCR-002a~b, AC-OCR-003a~c, AC-OCR-005a, AC-OCR-006a 전 시나리오 통과(AC-OCR-004a~b는 결번 — §D 안내 참조).
- [ ] 테스트 커버리지 85% 이상 (`quality.yaml` `constitution.test_coverage_target`). `pytesseract`는 신규 코어 모듈 테스트에서 목/스텁으로 격리; PyMuPDF 페이지 렌더링은 실제 픽스처로 검증.
- [ ] `ruff` 린트 무경고, `black` 포맷 준수, `pytest` 전체 그린(기존 70개 텔레그램 테스트 + `test_pdf_to_markdown.py` 기존 테스트 포함, 회귀 없음).
- [ ] spec.md의 REQ-OCR-001~008, 013, 014, **015**가 각각 최소 1개 테스트로 검증됨(추적성; REQ-OCR-015 → AC-OCR-006a). REQ-OCR-009~012는 결번이므로 대상이 아니다(§B 결번 안내).
- [ ] `src/markdown_creat/telegram_bot/handlers.py`의 변경이 **사진 OCR 호출 지점의 언어 인자 추가 1곳으로 한정**됨(REQ-OCR-015). PDF 처리 경로(`handle_document_message`)·예외 처리·그 외 로직은 미수정. `git diff` 상 handlers.py 변경이 최소임을 확인.
- [ ] `src/markdown_creat/pdf_to_markdown.py`가 **수정되지 않음**(본 SPEC 범위 밖 — spec.md §Exclusions). `git diff --stat`에 해당 파일이 나타나지 않아야 한다.
- [ ] `tests/test_telegram_ocr.py`의 모킹 대상 경로가 `markdown_creat.ocr.pytesseract.image_to_string`로 갱신되어 4개 기존 테스트가 계속 통과함.
- [ ] `telegram_bot/ocr.py`에 Tesseract 호출 로직이 재구현되지 않고 코어 모듈을 재노출함(§Exclusions 준수, REQ-OCR-014).
- [ ] README에 Tesseract `kor` traineddata 시스템 레벨 설치 안내가 문서화됨.
- [ ] `pyproject.toml`에 신규 pip 의존성이 추가되지 않음(§C 제약 준수).
