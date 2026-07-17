---
id: SPEC-OCR-001
title: "OCR 코어 모듈 — 이미지·PDF 텍스트 추출 (한국어 지원) — 구현 계획"
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

# SPEC-OCR-001 — 구현 계획 (plan.md)

## §A. 컨텍스트 (Context)

두 개의 완료된 SPEC(SPEC-PDF-001, SPEC-TELEGRAM-001) 위에 신설되는 네 번째 SPEC. 기존 코드 두 곳(사진 OCR, PDF 텍스트 추출)을 통합·일반화하고 신규 코어 모듈을 추가한다. Tier M(신규 모듈 1개 + 기존 완료 SPEC 2개의 공개 함수 재사용/재노출 + 완료 SPEC 1개의 동작 계약 변경 + 다국어 지원 + 다수 오류 경로로 Tier S보다 복잡, Tier L 문턱인 15개 파일·1000 LOC에는 미달).

**의존성 확인**: `depends_on: [SPEC-PDF-001, SPEC-TELEGRAM-001]`. 둘 다 `status: completed`이며 각각 `pdf_to_markdown(pdf_path, output_path)`(`src/markdown_creat/pdf_to_markdown.py:62`)와 `extract_image_text(image_path)`(`src/markdown_creat/telegram_bot/ocr.py:18`)가 실제로 구현되어 있다(2026-07-17 확인). `/moai run` 시 Depends_on Pre-flight Check는 두 SPEC 모두 `status: completed`이므로 통과가 예상된다. 단, §B의 M2 앰언드먼트 선행 조건은 Depends_on Pre-flight Check와 별개의 추가 게이트임에 유의한다(아래 참조).

## §B. 핵심 아키텍처 결정 — SPEC-PDF-001 앰언드먼트 경로 (경로 a vs b)

manager-spec의 판단: **경로 (b)를 채택** — SPEC-PDF-001 자신이 `completed → in-progress (amendment)` 전환을 거친다. 아래에 두 경로를 모두 검토하고 근거를 기록한다.

### 검토한 경로

**경로 (a)**: SPEC-OCR-001이 `depends_on: [SPEC-PDF-001, SPEC-TELEGRAM-001]`을 선언하고, 자신의 본문에서 SPEC-PDF-001의 OCR 배제 조항을 "상위 SPEC으로서" 무효화한다고 서술한다. SPEC-PDF-001 자체는 건드리지 않는다.

**경로 (b)**: SPEC-PDF-001이 `.claude/rules/moai/development/spec-frontmatter-schema.md` § Status Enum에 정의된 `completed → in-progress (amendment)` 전환을 별도로 거친다. `amendment_of: SPEC-PDF-001`(자기 참조), HISTORY에 `## Amendments` 서브섹션(이전 완료 버전, `prior_completed_sha`, 앰언드먼트 사유, 영향받는 REQ 범위 기록), REQ-PDF-009 문구 갱신, §Exclusions의 "OCR" 배제 항목 수정.

### 선택 근거

1. **공개 함수 동작 계약이 실제로 변경된다.** `pdf_to_markdown(pdf_path, output_path)`는 `@MX:ANCHOR`(공개 API 경계, `pdf_to_markdown.py:58-61`)로 표시되어 있으며, REQ-PDF-009("추출 가능한 텍스트가 없으면 명확한 오류를 발생시키며 빈 `.md` 파일을 기록하지 않는다")는 이 함수의 관찰 가능한 동작 계약의 일부다. 자동 OCR 폴백 도입은 "텍스트 없음 → 즉시 오류"에서 "텍스트 없음 → OCR 시도 → (성공 시) 파일 기록 / (실패 시) 오류"로 이 계약을 직접 수정한다. 이는 SPEC-PDF-001 **자신의** 문서가 서술하는 동작이 사실과 달라지는 문제이지, SPEC-OCR-001이 "추가"하는 새 기능이 아니다.
2. **schema.md가 정확히 이 상황을 위해 앰언드먼트 메커니즘을 제공한다.** `spec-frontmatter-schema.md`는 `completed → in-progress (amendment)` 전환을 "해당 SPEC 자신의 공개 함수 동작 계약이 변경되는 경우"로 명시적으로 정의하고 있다. 새 메커니즘을 발명할 필요 없이 기존 계약을 그대로 적용한다.
3. **SSOT(Single Source of Truth) 원칙 유지.** `pdf_to_markdown()`의 동작 계약을 SPEC-PDF-001과 SPEC-OCR-001 두 문서에 분산 서술하면(경로 a), 향후 독자가 "이 함수는 텍스트 없는 PDF를 만나면 어떻게 동작하는가?"를 알기 위해 두 SPEC을 모두 읽어야 한다. 경로 (b)는 SPEC-PDF-001의 REQ-PDF-009 자체를 갱신하므로 SPEC-PDF-001 문서만 읽어도 최신 동작이 정확히 서술되어 있다.
4. **"상위 SPEC이 하위 완료 SPEC의 배제 조항을 무효화한다"는 거버넌스 패턴은 이 프로젝트의 기존 관례에 선례가 없다.** 반면 `amendment_of` + `## Amendments` 메커니즘은 schema.md에 이미 정의되어 있고 lint 엔진(`internal/spec/lint.go`)의 지원을 받는다.

### 실행 조율 (본 SPEC의 범위 경계)

SPEC-PDF-001의 앰언드먼트 실행(REQ-PDF-009 문구 갱신, HISTORY `## Amendments` 추가, frontmatter `status`/`updated` 전환)은 **본 SPEC(SPEC-OCR-001)의 3개 산출물(spec.md/plan.md/acceptance.md) 작성 범위 밖**이며, `.moai/specs/SPEC-PDF-001/` 자체 파일에서 별도로 수행되어야 한다. Status Transition Ownership Matrix(spec-frontmatter-schema.md)에 따르면 이 전환의 소유자는 **manager-spec**(재위임, D-NEW-1 inline-fix 패턴)이다.

**M2를 SPEC-OCR-001 run-phase의 필수 선행 마일스톤으로 지정**한다(§D 마일스톤 참조): manager-develop이 `pdf_to_markdown.py`의 동작을 변경하기 전에, 오케스트레이터는 SPEC-PDF-001 앰언드먼트를 manager-spec에 위임하여 완료해야 한다. manager-develop은 SPEC body 콘텐츠(spec.md REQ 문구)를 수정할 권한이 없으므로(SPEC Artifact Ownership 경계), 앰언드먼트가 완료되지 않은 상태에서 이 작업에 도달하면 blocker report를 반환해야 한다.

**SPEC-TELEGRAM-001은 앰언드먼트 대상이 아니다** — §A에서 서술한 대로 공개 계약(`extract_image_text(image_path: str) -> str`, `ImageOcrError`)이 보존되므로, `completed` 상태 그대로 유지되며 오직 `tests/test_telegram_ocr.py`의 모킹 대상 경로만 기계적으로 갱신된다(M4 참조).

## §C. 기술 접근 (Technical Approach)

- `src/markdown_creat/ocr.py` — 신규 코어 공유 모듈. 두 개의 공개 함수:
  - `extract_image_text(image_path: str, lang: str = "eng") -> str` — 기존 `telegram_bot/ocr.py`의 `extract_image_text()`를 언어 파라미터를 추가하여 일반화. `pytesseract.image_to_string(image_path, lang=lang)` 호출.
  - `extract_pdf_text_via_ocr(pdf_path: str, lang: str = "eng") -> str` — 신규. PyMuPDF로 PDF를 열고 각 페이지를 `page.get_pixmap()`으로 이미지 렌더링 → 임시 파일에 저장 → `extract_image_text()` 재사용으로 OCR → 페이지 순서대로 텍스트 병합.
  - 예외: `OcrError`(기존 `ImageOcrError`를 일반화한 이름 — 이미지·PDF 페이지 OCR 모두의 실패를 포괄).
- `src/markdown_creat/pdf_to_markdown.py` — `_build_markdown(document)`가 `None`을 반환하는 지점(현재 라인 97-98, `PDFNoTextError` 발생 직전)에 자동 OCR 폴백 훅을 삽입. `extract_pdf_text_via_ocr(pdf_path)`를 호출하여 비어있지 않은 텍스트를 얻으면 이를 마크다운 본문으로 사용(제목 감지는 OCR 텍스트에는 적용하지 않음 — 문단으로만 구성, plan.md M1에서 확정); 실패하거나 빈 결과면 기존과 동일하게 `PDFNoTextError`를 발생시킨다.
- `src/markdown_creat/telegram_bot/ocr.py` — 얇은 재노출로 축소:
  ```python
  from markdown_creat.ocr import OcrError as ImageOcrError, extract_image_text
  __all__ = ["extract_image_text", "ImageOcrError"]
  ```
- `src/markdown_creat/telegram_bot/extract.py`, `handlers.py` — **변경 없음**. `extract_pdf_text()`는 `pdf_to_markdown()`을 그대로 호출하므로, 자동 OCR 폴백은 이 래퍼를 거쳐 투명하게 적용된다. `handlers.py`의 임포트 경로(`telegram_bot.ocr`)도 재노출로 인해 변경 불필요.
- `pyproject.toml` — 변경 없음(기존 `pymupdf`, `pytesseract` 재사용).
- `README.md` — Tesseract `kor` traineddata 시스템 레벨 설치 안내 섹션 추가.

(최종 모듈 분할은 M4~M5에서 확정. 위는 시작 제안.)

## §D. 마일스톤 (결정 번복 가능성 순 — 변경 가능성 높은 결정 우선)

> 사람이 검토할 때 변경 가능성이 가장 높은 결정(공개 API 시그니처 · SPEC-PDF-001 앰언드먼트 조율 · PDF 페이지 렌더링 방식)을 먼저 배치하고, 기계적 구현/리팩터 단계는 뒤로 미룬다.

### M1 — 코어 OCR 모듈 공개 API 및 예외 계약 확정 (변경 가능성 최상)
- `ocr.py`의 `extract_image_text(image_path, lang="eng")`, `extract_pdf_text_via_ocr(pdf_path, lang="eng")` 시그니처 확정(REQ-OCR-001, 004, 006, 007).
- `OcrError` 예외 하나로 통일할지, 이미지 실패/PDF 렌더링 실패를 별도 하위 클래스로 분리할지 결정 — 최소 범위로 시작(단일 `OcrError`), 필요 시 하위 클래스는 후속 SPEC(REQ-OCR-003, 005).
- 언어팩 미설치 시 오류 문구 계약 확정(REQ-OCR-008) — `pytesseract.TesseractError`의 원본 메시지(언어팩 파일 경로 포함)를 `OcrError`로 감싸 그대로 전달하는 방식으로 별도 파싱 로직 없이 충족 가능함을 확인(구현 시 실제 오류 메시지로 검증).
- `pdf_to_markdown()` 자동 폴백 훅의 정확한 삽입 지점과, OCR로 얻은 텍스트를 마크다운으로 어떻게 조립할지(제목 감지 미적용, 문단으로만 구성) 확정(REQ-OCR-009, 010, 011).
- 이는 하위 모든 호출자(telegram_bot 재노출, pdf_to_markdown 통합)가 의존하는 계약이므로 사람 검토가 가장 필요한 지점이다.
- RED: 코어 모듈 성공/실패 경로에 대한 실패 테스트 작성(`pytesseract` 모킹).

### M2 — SPEC-PDF-001 앰언드먼트 실행 조율 (변경 가능성 상, 선행 조건)
- §B에서 확정한 경로 (b)에 따라 SPEC-PDF-001의 앰언드먼트를 실행한다: `amendment_of: SPEC-PDF-001`(자기 참조), `status: completed → in-progress`, HISTORY에 `## Amendments`(이전 완료 버전 `0.1.0`, `prior_completed_sha` — SPEC-PDF-001의 최종 완료 커밋 SHA 기록, 앰언드먼트 사유, 영향받는 REQ 범위: REQ-PDF-009) 추가, REQ-PDF-009 문구 갱신("추출 가능한 텍스트가 없으면 자동 OCR 폴백을 먼저 시도하고, 폴백도 실패하면 명확한 오류를 발생시킨다"), §Exclusions의 "OCR" 배제 항목을 "SPEC-OCR-001에 의해 자동 폴백으로 흡수됨, 표/도표 OCR 및 다국어 확장은 계속 배제"로 수정.
- **소유권**: 이 마일스톤은 manager-spec이 수행한다(Status Transition Ownership Matrix). manager-develop은 이 전환을 수행할 권한이 없다 — M3~M5 착수 전 오케스트레이터가 이 마일스톤의 완료를 확인해야 한다.
- **차단 조건**: M2가 완료되지 않은 상태에서 manager-develop이 `pdf_to_markdown.py`의 자동 폴백 동작 구현(M4)에 도달하면, blocker report를 반환하고 오케스트레이터가 manager-spec에 재위임해야 한다(SPEC Artifact Ownership 경계 위반 방지).
- RED: 없음(이 마일스톤은 SPEC 문서 갱신이며 코드 변경이 아님).

### M3 — PDF 페이지 렌더링 방식 및 해상도 결정 (변경 가능성 상)
- `page.get_pixmap()` 호출 시 DPI/줌 매트릭스 결정 — PyMuPDF 기본값(72 DPI)은 OCR 정확도에 부족할 수 있으므로, 더 높은 해상도(예: `dpi=300` 또는 2x 줌 매트릭스)를 기본값으로 채택하고 정확도 대 속도/메모리 트레이드오프를 문서화한다.
- 렌더링된 페이지 이미지를 OCR에 전달하는 방식 확정: 임시 파일 경유(기존 `extract.py`의 write-then-read 패턴과 일관성 유지, 신규 PIL 직접 의존성 회피) vs 인메모리 PIL Image 전달(Pillow를 명시적 의존성으로 추가 필요). **임시 파일 경유 방식을 채택**(§C 결정 — 기존 패턴과의 일관성, 신규 의존성 회피).
- RED: PDF 페이지 → 이미지 → OCR 통합 경로에 대한 실패 테스트 작성(실제 PyMuPDF 픽스처 + `pytesseract` 모킹의 혼합 전략 — §C 참조).

### M4 — `telegram_bot/ocr.py` 재노출 및 기존 테스트 갱신 확정 (변경 가능성 중)
- 재노출 형태 확정(§C 코드 스니펫). `ImageOcrError` 이름을 하위 호환을 위해 별칭(alias)으로 유지하는 것을 확정(REQ-OCR-013).
- **기존 테스트 파일 갱신**: `tests/test_telegram_ocr.py`의 4개 테스트가 현재 `unittest.mock.patch("markdown_creat.telegram_bot.ocr.pytesseract.image_to_string", ...)` 형태로 모킹한다(직접 확인됨). 재노출 전환 후 실제 `pytesseract` 호출은 `markdown_creat.ocr` 모듈로 이동하므로, 모킹 대상 경로를 `markdown_creat.ocr.pytesseract.image_to_string`로 갱신해야 4개 테스트가 계속 통과한다. 이는 REQ-TELEGRAM-007의 관찰 가능한 동작을 변경하지 않는 기계적 테스트 파일 갱신이다(SPEC-TELEGRAM-001 앰언드먼트 불필요, §B 참조).
- RED: 재노출 계약에 대한 실패 테스트(임포트 경로, 예외 별칭) 작성.

### M5 — 구현 (GREEN, 기계적)
- `ocr.py` 최소 구현. `pdf_to_markdown.py`에 자동 폴백 훅 통합(M2 앰언드먼트 완료 후에만 착수). `telegram_bot/ocr.py` 재노출로 축소. `tests/test_telegram_ocr.py` 모킹 경로 갱신. README에 Tesseract `kor` 설치 안내 추가.

### M6 — 리팩터 및 품질 게이트 (REFACTOR, 기계적)
- `ruff` + `black` 정리, 커버리지 85% 확인, 중복 제거. `pdf_to_markdown.py`·`telegram_bot/ocr.py`·`telegram_bot/extract.py` 전체 회귀 테스트(70개 기존 텔레그램 테스트 + 신규 OCR 코어 테스트) 그린 확인.

## §E. 리스크 (Risks)

- **[거버넌스] SPEC-PDF-001 앰언드먼트 조율 실패**: M2가 누락되거나 지연되면 manager-develop이 SPEC Artifact Ownership 경계를 위반하며 `pdf_to_markdown.py`를 수정할 위험이 있다. 완화: M2를 M3~M5보다 먼저 배치하고, 오케스트레이터가 run-phase 진입 전 M2 완료 여부를 명시적으로 확인한다.
- **[테스트 회귀] 기존 70개 텔레그램 테스트**: `telegram_bot/ocr.py` 재노출 전환이 `tests/test_telegram_ocr.py`의 모킹 대상 경로를 깨뜨릴 수 있다(직접 확인됨 — 현재 `markdown_creat.telegram_bot.ocr.pytesseract.image_to_string` 경로 모킹). 완화: M4에서 이 갱신을 명시적 마일스톤으로 지정.
- **[OCR 정확도] Tesseract 기본 설정의 한계**: 이미지 전처리 없이 기본 설정만 사용하므로 저품질 스캔 PDF에서는 OCR 결과가 부정확하거나 비어 있을 수 있다. REQ-OCR-011에 따라 OCR도 실패하면 기존과 동일하게 `PDFNoTextError`로 처리되므로 조용한 실패는 없으나, "낮은 정확도의 텍스트가 성공으로 처리되는" 경우는 본 SPEC의 범위 밖(§Exclusions — 정확도 튜닝)이다.
- **[외부 바이너리] `kor` traineddata 미설치**: REQ-OCR-008에 따라 명확한 오류로 처리되지만, 사용자가 README를 읽지 않으면 이 오류를 처음 마주할 수 있다. 완화: README에 설치 안내를 명확히 문서화(M5).
- **[해상도/성능] PDF 페이지 렌더링 해상도 트레이드오프**: 높은 DPI는 OCR 정확도를 높이지만 렌더링 시간과 메모리 사용량을 증가시킨다. M3에서 구체적 수치를 확정하고 문서화한다.
- **[라이선스] PyMuPDF AGPL 라이선스 (SPEC-PDF-001에서 이미 리스크로 기록됨)**: 본 SPEC은 PyMuPDF의 기존 의존성을 재사용할 뿐 새로운 라이선스 리스크를 추가하지 않는다. 참고만 함.

## §F. 참조

- `spec.md` (요구사항 SSOT), `acceptance.md` (인수 시나리오)
- 앰언드먼트 대상 의존 SPEC: `.moai/specs/SPEC-PDF-001/spec.md`, `plan.md` (`pdf_to_markdown()` 동작 계약 변경)
- 재노출 대상 의존 SPEC(앰언드먼트 불필요): `.moai/specs/SPEC-TELEGRAM-001/spec.md`, `plan.md` (`telegram_bot/ocr.py`)
- 앰언드먼트 메커니즘 SSOT: `.claude/rules/moai/development/spec-frontmatter-schema.md` § Status Enum, § Status Transition Ownership Matrix
