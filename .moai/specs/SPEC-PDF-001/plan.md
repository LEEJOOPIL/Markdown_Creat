---
id: SPEC-PDF-001
title: "PDF → 마크다운 변환 코어 기능 — 구현 계획"
version: "0.2.0"
status: completed
created: 2026-07-14
updated: 2026-07-19
author: manager-spec
priority: P1
phase: "v0.2.0 target"
module: "src/markdown_creat"
lifecycle: spec-anchored
tags: "pdf, markdown, extraction, pymupdf, conversion, ocr"
tier: M
amendment_of: SPEC-PDF-001
depends_on: [SPEC-OCR-001]
---

# SPEC-PDF-001 — 구현 계획 (plan.md)

## §A. 컨텍스트 (Context)

그린필드 프로젝트의 두 번째 SPEC(SPEC-GEN-001과 병렬, 반대 방향). 분석할 기존 코드 없음. PyMuPDF(fitz)로 PDF 텍스트·제목을 추출하여 `.md` 파일로 변환하는 코어 함수를 TDD(RED-GREEN-REFACTOR)로 구현한다. Tier M(단일 공개 함수이나 제목 감지 휴리스틱 + 4종 오류 경로로 순수 Tier S보다 복잡).

## §B. 기술 접근 (Technical Approach)

`structure.md` 제안 구조를 따르되, 본 SPEC은 신규 모듈 하나에 집중한다:

- `src/markdown_creat/pdf_to_markdown.py` — PDF 경로 · 출력 경로 → `.md` 변환 코어 공개 함수. PyMuPDF `fitz.open()`으로 문서를 열고, 페이지별 텍스트 스팬(span)의 폰트 크기 메타데이터를 수집하여 제목/본문을 분류한 뒤 마크다운 문자열로 조립하고 파일에 기록한다.

내부 책임(단일 모듈 내 함수 분리 권장, 최종 형태는 M4에서 확정):
- PDF 열기 + 오류 분류(부재/손상/암호화)
- 페이지 텍스트·폰트 메타데이터 추출
- 제목 감지 휴리스틱(폰트 크기 → 제목 레벨 매핑)
- 마크다운 조립 + UTF-8 파일 기록(원자적: 완성 후에만 기록)

`cli.py`, `config.py`, SPEC-GEN-001의 생성 모듈은 본 SPEC에서 다루지 않는다.

## §C. 마일스톤 (결정 번복 가능성 순 — 변경 가능성 높은 결정 우선)

> 사람이 검토할 때 변경 가능성이 가장 높은 결정(공개 인터페이스 · 제목 휴리스틱 · 오류 계약)을 먼저 배치하고, 기계적 단계는 뒤로 미룬다.

### M1 — 공개 API 인터페이스 결정 (변경 가능성 최상) — ✅ 완료 (`53dddd2`)
- `pdf_to_markdown.py`의 코어 공개 함수 시그니처 확정: 인자(pdf_path, output_path)의 형태(문자열/Path), 반환값(None), 예외 계약.
- 이는 하위 모든 호출자(향후 CLI 포함)가 의존하는 계약이므로 사람 검토가 가장 필요한 지점이다.
- RED: 성공 경로에 대한 실패 테스트 작성.

### M2 — 제목 감지 휴리스틱 결정 (변경 가능성 상) — ✅ 완료 (`53dddd2`)
- 폰트 크기/스타일을 제목 레벨로 매핑하는 규칙 확정(REQ-PDF-002). 예: 문서 내 폰트 크기 분포를 수집해 상위 N개 크기를 `#`~`###`에 매핑, 본문 크기는 문단으로. 굵기(bold) 보조 신호 사용 여부 결정.
- 휴리스틱이 지나치게 복잡해질 경우 Tier M 범위에 맞춰 단순화(예: 크기 기준 상위 1~3레벨만) — 선택한 휴리스틱을 spec/plan에 문서화(REQ-PDF-002의 "문서화된 휴리스틱" 충족).
- RED: 제목/문단 분류에 대한 실패 테스트 작성.

### M3 — 오류 처리 계약 결정 (변경 가능성 상) — ✅ 완료 (`53dddd2`)
- 파일 부재(REQ-PDF-006), 손상(REQ-PDF-007), 암호화(REQ-PDF-008), 추출 텍스트 없음(REQ-PDF-009)에 대해 발생시킬 예외 타입/메시지 형태 확정.
- 부분 출력 방지(REQ-PDF-010) 전략(마크다운 완성 후에만 파일 기록) 확정.
- RED: 각 오류 케이스에 대한 실패 테스트 작성.

### M4 — 구현 (GREEN, 기계적) — ✅ 완료 (`53dddd2`)
- `pdf_to_markdown.py` 최소 구현으로 테스트 통과. PyMuPDF 텍스트 딕셔너리(`page.get_text("dict")`) 기반 스팬 순회 구현.

### M5 — 리팩터 및 품질 게이트 (REFACTOR, 기계적) — ✅ 완료 (`53dddd2`)
- `ruff` + `black` 정리, 커버리지 85% 확인, 중복 제거, 함수 분리 정리.

## §D. 리스크 (Risks)

- **[라이선스 — 사용자 검토 필요] PyMuPDF AGPL 라이선스**: PyMuPDF(fitz)는 AGPL-3.0 라이선스이다. 내부 사용/개인 도구에는 문제가 없으나, 이 도구를 **상업적으로 재배포하거나 SaaS로 제공**할 경우 AGPL의 소스 공개 의무가 적용될 수 있어 별도 라이선스 검토가 필요하다. 사용자가 PyMuPDF를 명시적으로 선택했으므로 본 SPEC은 PyMuPDF로 진행하되, 재배포 시나리오가 생기면 (a) 상용 라이선스 취득 또는 (b) MIT/BSD 계열 대안(예: `pypdf`, `pdfminer.six`)으로의 교체를 별도 SPEC에서 검토할 것을 권장한다.
- **제목 감지 휴리스틱의 정확도**: 폰트 크기만으로는 제목/본문 구분이 부정확할 수 있다(디자인이 균일한 PDF, 크기가 유사한 문서). Tier M 범위에서 완벽한 정확도를 목표하지 않으며, "합리적 휴리스틱"으로 한정하고 그 한계를 문서화한다 → M2에서 확정.
- **추출 텍스트 없음 vs 빈 페이지 구분**: 스캔 PDF(이미지 전용)와 실제로 텍스트가 비어있는 PDF 모두 REQ-PDF-009 경로로 처리 → M3에서 판정 기준 확정.
- **출력 경로 부모 디렉터리 부재** 시 동작(생성할지 오류낼지) → M3에서 결정.
- **인코딩**: UTF-8 고정(spec.md §C에 명시). PDF 내부 텍스트 인코딩 이슈는 PyMuPDF가 유니코드로 정규화하므로 별도 처리 최소화.

## §E. 참조

- `spec.md` (요구사항 SSOT), `acceptance.md` (인수 시나리오)
- 관련 SPEC: `.moai/specs/SPEC-GEN-001/plan.md` (순방향 생성, 오류 처리 철학 참조)

---

## §F. v0.2.0 앰언드먼트 — OCR 자동 폴백 통합

§A~§E는 v0.1.0(완료, `53dddd2`)의 구현 계획이며 수정하지 않는다. 아래는 v0.2.0 앰언드먼트(스캔 PDF OCR 자동 폴백)의 구현 계획이다. `spec.md`의 Amendments 섹션이 rationale/scope의 SSOT이며, 여기서는 반복하지 않는다.

### §F.1 컨텍스트

`extract_pdf_text_via_ocr(pdf_path: str, lang: str = "eng") -> str`(`src/markdown_creat/ocr.py:65`, SPEC-OCR-001 `status: completed`)는 이미 존재하며 완전히 구현·테스트되어 있다. 본 앰언드먼트는 이 함수를 `pdf_to_markdown()`의 텍스트-없음 오류 경로에 배선(wiring)할 뿐이며, OCR 로직 자체는 한 줄도 수정하지 않는다(SPEC-OCR-001 스코프 보존 — 앰언드먼트 대상 아님). 변경 파일 예상 범위: `src/markdown_creat/pdf_to_markdown.py`(핵심 변경), `tests/test_pdf_to_markdown.py`(기존 테스트 조정 + 신규 테스트), `README.md`(선택 — 동작 변경 문서화). `src/markdown_creat/telegram_bot/*`는 수정하지 않는다 — `extract.py`의 `extract_pdf_text()`가 `pdf_to_markdown()`을 그대로 호출하므로 이 앰언드먼트의 효과는 브리지 계층을 거쳐 투명하게 텔레그램 봇에 전파된다.

### §F.2 아키텍처 결정 (변경 가능성 최상 — 사람 검토 우선 배치)

다음 4개 질문은 위임 프롬프트가 열어둔 설계 결정이며, 각각 채택안과 근거를 아래에 확정한다. manager-develop은 이 결정들을 그대로 구현하며 재논의하지 않는다(단, 구현 중 근거를 무효화하는 사실이 발견되면 blocker report로 보고).

#### 결정 1 — 통합 지점: `pdf_to_markdown()` 내부 (extract.py 브리지 계층이 아님)

**채택**: OCR 폴백은 `pdf_to_markdown()` 함수 **내부**에서 호출한다. `_build_markdown(document)`가 `None`을 반환하는 지점(텍스트 레이어 없음 감지) 직후, 기존처럼 즉시 `PDFNoTextError`를 발생시키는 대신 `extract_pdf_text_via_ocr(pdf_path, lang="kor+eng")`를 호출한다. `src/markdown_creat/telegram_bot/extract.py`는 **변경하지 않는다**.

**근거**:
1. **사용자가 이미 확정한 아키텍처 결정과 정확히 일치한다.** SPEC-OCR-001 spec.md §A 결정 #2(재검토 대상 아님, AskUserQuestion으로 승인됨): "예외를 즉시 발생시키기 전에 PDF의 페이지 이미지에 대해 자동으로 OCR을 시도한다... 별도의 옵트인 플래그는 없다 — 이것이 새로운 기본 동작이다." "기본 동작(default behavior)"은 `pdf_to_markdown()` 자신의 계약이지, 특정 호출자(텔레그램 봇)만의 계약이 아니다. `extract.py` 브리지에만 넣으면 향후 다른 호출자(예: 미구현 SPEC-GEN-001 확장, CLI, 직접 라이브러리 사용)는 이 기본 동작을 받지 못한다.
2. **SPEC-OCR-001 자신의 서술과 일치한다.** SPEC-OCR-001은 이 통합 지점을 반복적으로 "`pdf_to_markdown.py`에 폴백 **훅**을 삽입"(spec.md §Exclusions, plan.md §B 경로 c)이라고 서술한다 — 브리지 계층이 아니라 코어 함수 자신의 훅이다. `plan.md` §B D4 이연 앵커 레시피의 마지막 단계도 "REQ-PDF-009 문구를 자동 OCR 폴백 계약으로 개정"이라고 명시한다 — `pdf_to_markdown()`의 계약 자체가 바뀐다는 뜻이다.
3. **블라스트 반경 우려가 실제로는 없다.** 위임 프롬프트가 제기한 "`pytesseract` 의존성을 기본 경로에 추가하는 것의 블라스트 반경" 우려를 확인한 결과: `pytesseract>=0.3.13`은 이미 `pyproject.toml`에 프로젝트 전역 의존성으로 선언되어 있다(SPEC-OCR-001에서 추가, 직접 확인). 신규 pip 의존성은 추가되지 않는다 — 우려했던 "다른 비-봇 호출자에 새 의존성을 강제한다"는 비용이 존재하지 않는다.
4. **SSOT 원칙**: SPEC-OCR-001 plan.md §B가 스스로 정립한 원칙 — "`pdf_to_markdown()`의 동작 계약은 SPEC-PDF-001 문서 한 곳에서만 서술되어야 한다"(SSOT). 이 계약을 `extract.py`(텔레그램 봇 소유)에 분산시키면 이 원칙에 반한다.

**기각한 대안 (extract.py 브리지 계층)**: `extract_pdf_text()`가 `PDFNoTextError`를 잡아 `extract_pdf_text_via_ocr()`를 2차 시도하는 방식. 장점(핵심 라이브러리를 OCR-free하게 유지)은 실재하지 않는 우려(신규 의존성)에 대한 해법이었으므로 근거가 사라진다. 단점(사용자가 승인한 "새로운 기본 동작"을 텔레그램 봇에만 국한시킴, SSOT 위반)이 그대로 남는다. 기각.

**공개 시그니처 변경 여부**: `pdf_to_markdown(pdf_path: str, output_path: str) -> None` 시그니처는 **변경하지 않는다**(REQ-PDF-001~008 안정성, `@MX:ANCHOR` 계약 보존). OCR 언어는 새 공개 파라미터로 노출하지 않고 함수 내부에서 리터럴 `"kor+eng"`로 고정 호출한다(결정 4, REQ-PDF-012) — 이는 REQ-OCR-015가 이미 정립한 선례(리터럴 고정, 설정 가능화는 별도 관심사)와 일관되며, 기존 호출자와 100% 하위 호환이다.

#### 결정 2 — OCR 실패 후 오류 시맨틱

**채택**: 두 개의 구분되는 실패 모드를 서로 다른 예외로 처리한다.

1. **OCR 엔진 자체 오류** (`ocr.py`의 `OcrError` — Tesseract 미설치, 언어팩 누락, 페이지 렌더링 실패): `pdf_to_markdown()`은 이를 **`PDFOCRFailedError`(신규, `MarkdownConversionError` 하위 클래스)**로 감싸 재발생시킨다(`raise PDFOCRFailedError(...) from ocr_exc`). 원본 `OcrError`를 그대로 전파하지 않는다.
2. **OCR이 오류 없이 완료되었으나 텍스트를 찾지 못함** (빈 문자열 또는 공백만 있는 병합 결과 — `extract_pdf_text_via_ocr()`가 REQ-OCR-002 계약에 따라 반환): 기존과 동일하게 **`PDFNoTextError`**를 발생시킨다(신규 타입 불필요 — REQ-PDF-009 의미가 "텍스트 레이어에도, OCR에도 텍스트 없음"으로 자연스럽게 확장됨).

**근거**:
- **예외 계층 보존이 결정적이다.** `pdf_to_markdown()`의 공개 계약은 "`MarkdownConversionError` 및 그 4개(→5개) 하위 클래스만 발생시킨다"이다(spec.md docstring, `@MX:ANCHOR`). `ocr.py`의 `OcrError`는 이 계층에 속하지 않는다 — 감싸지 않고 그대로 전파하면 `extract.py`의 `except MarkdownConversionError`가 이를 잡지 못해, `handle_document_message()`에서 처리되지 않은 예외로 봇 핸들러가 죽는다(REQ-TELEGRAM-005/011의 "원본은 항상 보존, 실패는 폴백 노트로" 계약을 깨뜨림). `PDFOCRFailedError(MarkdownConversionError)`로 감싸면 기존 `except MarkdownConversionError` catch-all이 계속 유효하다.
- **두 실패 모드를 구분하는 이유**: "엔진이 고장남"(설치/설정 문제, 사용자가 조치 가능)과 "이 PDF에는 정말 텍스트가 없음"(콘텐츠 문제)은 근본 원인이 다르며, 별도 타입으로 구분해야 향후 로깅/모니터링에서 구별 가능하다. REQ-PDF-011이 이를 요구사항으로 명문화한다.
- **REQ-PDF-009의 불변조건(빈/부분 `.md` 없음)은 두 경로 모두에서 구조적으로 보장된다** — 두 예외 모두 마크다운 문자열 조립(`_build_markdown` 및 OCR 텍스트 대입) 완료 **이전**에 발생하므로, `_write_markdown_file()` 호출부에 도달하지 않는다(REQ-PDF-010 참조).

**예외 계층 (갱신)**: `MarkdownConversionError`(base) → `PDFNotFoundError` | `PDFCorruptedError` | `PDFEncryptedError` | `PDFNoTextError` | **`PDFOCRFailedError`**(신규). `pdf_to_markdown.py`의 `__all__`에 `PDFOCRFailedError` 추가.

#### 결정 3 — 성능/UX 상한 (페이지 수 · 타임아웃)

**채택**: 본 앰언드먼트 범위에서는 페이지 수/시간 상한을 두지 **않는다**(명시적으로 범위 밖 — `spec.md §Exclusions` 참조). Enforce Simplicity + YAGNI 적용:

**근거**:
1. **동기 사건은 1페이지 스캔 PDF다** — SPEC-OCR-001 spec.md §A에서 직접 확인된 사건(`telegram-notes/files/2026-07-16_123156_7_52.pdf`, 1페이지, 임베디드 이미지 1개)이 본 앰언드먼트의 동기다. 다중 페이지 대용량 스캔 PDF로 인한 지연이 실제 문제로 보고된 바 없다.
2. **선례가 이미 상한을 두지 않는다** — `extract_pdf_text_via_ocr()`(SPEC-OCR-001, 완료) 자신도 페이지 수 상한을 두지 않았다. 그 함수를 그대로 재사용하는 본 앰언드먼트가 호출부에서만 새로운 제약을 추가하는 것은 일관성이 없고, 상한값(몇 페이지? 몇 초?)을 결정할 데이터도 없다.
3. **상한 도입은 새 요구사항·새 오류 경로·새 테스트를 추가하는 범위 확장이다** — 값을 근거 없이 임의로 정하면 오히려 자의적 실패 모드를 만든다(Scope Discipline).

**잔여 위험 (문서화, 완화하지 않음)**: `handle_document_message()`는 동기 핸들러다(python-telegram-bot 프레임워크 컨텍스트). 매우 큰 다중 페이지 스캔 PDF(예: 수백 페이지)가 전송되면 페이지당 300 DPI 렌더링 + Tesseract OCR이 누적되어 핸들러가 오래 블로킹될 수 있다 — 봇의 다른 동시 요청 처리에 영향을 줄 수 있다. 이 리스크는 §F.4에 기록하며, 실제 운영 문제로 확인되면 후속 SPEC(또는 본 SPEC의 후속 앰언드먼트)에서 상한·비동기화·타임아웃을 다룬다.

#### 결정 4 — OCR 언어 기본값

**채택**: `kor+eng` 리터럴 고정(REQ-PDF-012). 텔레그램 봇 사진 경로(`handlers.py:71`, REQ-OCR-015)가 이미 동일한 값을 사용 중이므로 일관성을 유지한다. 설정 가능화(환경변수 등)는 범위 밖(`spec.md §Exclusions`, SPEC-OCR-001의 동일 선례를 따름).

### §F.3 마일스톤 (결정 번복 가능성 순)

#### M1 — 예외 계층 확장 확정 (변경 가능성 최상 — §F.2 결정 1·2의 구현)
- `pdf_to_markdown.py`에 `PDFOCRFailedError(MarkdownConversionError)` 신설, `__all__`에 추가.
- `pdf_to_markdown()` 내부에서 `markdown_creat.ocr`의 `extract_pdf_text_via_ocr`, `OcrError`를 임포트.
- RED: OCR 폴백 성공 경로(스캔 PDF + OCR이 텍스트를 찾음 → 정상 `.md` 생성) 및 OCR 엔진 실패 경로(`OcrError` → `PDFOCRFailedError`)에 대한 실패 테스트 작성. `pytesseract.image_to_string`은 `markdown_creat.ocr.pytesseract.image_to_string` 경로에서 모킹(SPEC-OCR-001 §C와 동일 전략), PyMuPDF 페이지 렌더링은 실제 픽스처로 검증.

#### M2 — `_build_markdown` 텍스트-없음 분기의 OCR 폴백 배선 (변경 가능성 상)
- `pdf_to_markdown()` 본문에서 `_build_markdown(document)`가 `None`을 반환하는 지점을 OCR 폴백 호출로 대체: `extract_pdf_text_via_ocr(pdf_path, lang="kor+eng")` 호출 → 결과가 비어있지 않으면(공백 제거 후) 그 텍스트를 마크다운 본문으로 사용(문단으로만 구성, 제목 구조 없음 — REQ-PDF-009 후반부), 비어있으면 `PDFNoTextError` 발생. `OcrError` 발생 시 `PDFOCRFailedError`로 감싸 재발생.
- 이 배선은 `document.close()` (현재 `finally` 블록 내부에서 `_build_markdown` 호출) **이후**에 발생해야 한다는 점에 유의 — `extract_pdf_text_via_ocr()`는 자신만의 `fitz.open(pdf_path)` 호출로 PDF를 재오픈하므로(코어 함수 재사용, `document` 객체 공유 없음), 기존 `document`가 이미 닫힌 뒤에도 안전하게 호출 가능하다. 이 순서를 M1의 RED 테스트가 명시적으로 검증한다.
- RED: 위 배선 경로에 대한 통합 테스트(전체 `pdf_to_markdown()` 호출 경로).

#### M3 — 기존 테스트 조정 (변경 가능성 중 — 기존 계약의 의미 확장)
- `tests/test_pdf_to_markdown.py`의 `test_pdf_to_markdown_raises_clear_error_when_no_extractable_text`(라인 258)와 `test_pdf_to_markdown_never_leaves_partial_output_on_error`의 `no_text` 파라미터 케이스(라인 288-291)는 **의미가 "텍스트 레이어 없음"에서 "텍스트 레이어에도 OCR에도 텍스트 없음"으로 확장**되므로, `markdown_creat.ocr.pytesseract.image_to_string`을 빈 문자열(`""`) 반환으로 모킹하도록 갱신한다(`make_no_text_pdf()`는 실제로 렌더링 가능한 빈 페이지를 생성하므로 — `page.get_pixmap()`은 정상 동작하고, 모킹된 OCR이 빈 결과를 반환해야 `PDFNoTextError`가 유지된다는 점을 직접 확인함).
- assertion 자체(`pytest.raises(PDFNoTextError)`, `not output_path.exists()`)는 변경하지 않는다 — 최종 관찰 가능한 동작은 동일하되, 도달 경로에 OCR 모킹이 추가될 뿐이다.
- 신규 테스트(acceptance.md 참조): 스캔 PDF에서 OCR이 텍스트를 찾는 성공 경로, OCR 엔진 실패 경로, 기존 텍스트-포함 PDF에 대한 회귀 없음(OCR 폴백이 전혀 호출되지 않음을 모킹 미호출로 검증).

#### M4 — 구현 (GREEN, 기계적)
- M1~M3에서 확정한 계약대로 `pdf_to_markdown.py` 최소 구현. 기존 M1~M5(v0.1.0)의 로직(`_iter_text_blocks`, `_classify_heading_levels`)은 변경하지 않는다.

#### M5 — 리팩터 및 품질 게이트 (REFACTOR, 기계적)
- `ruff` + `black` 정리, 커버리지 85% 이상 확인(신규 분기 포함). 기존 8개 AC + 신규 AC 전체 회귀 그린 확인. `README.md`에 OCR 자동 폴백 동작 변경을 반영할지 검토(선택 — manager-docs가 sync 단계에서 판단해도 무방).

### §F.4 리스크 (v0.2.0 추가분)

- **[성능/UX — 잔여 위험, 완화하지 않기로 결정]** 대용량 다중 페이지 스캔 PDF의 동기 OCR 처리 시간(§F.2 결정 3 참조). 실제 운영 문제로 확인되면 후속 SPEC에서 다룬다.
- **[OCR 정확도]** Tesseract 기본 설정 + 300 DPI 렌더링만 사용하므로 저품질 스캔에서는 OCR 결과가 부정확하거나 비어 있을 수 있다(SPEC-OCR-001에서 이미 식별된 리스크, 상속). "낮은 정확도의 텍스트가 성공으로 처리되는" 경우는 본 앰언드먼트의 범위 밖 — 빈 문자열이 아닌 한 성공으로 간주한다.
- **[테스트 회귀]** 기존 8개 AC(v0.1.0) 중 텍스트-없음 관련 2개 테스트가 M3에서 모킹 경로가 추가되며 조정된다 — 나머지 6개(파일 부재/손상/암호화/덮어쓰기/텍스트 추출/제목 감지)는 OCR 폴백 분기에 도달하지 않으므로 무수정 그린이 기대된다(회귀 확인 목적으로 실행).
- **[의존성 순서]** `depends_on: [SPEC-OCR-001]`가 frontmatter에 추가되었다 — `/moai run` 진입 시 Depends_on Pre-flight Check가 SPEC-OCR-001의 `status: completed`를 확인한다(현재 completed이므로 통과 예상). SPEC-OCR-001 plan.md §B D4 "이연 앵커 레시피"가 정확히 이 배선을 사전에 기록해 두었다.

### §F.5 참조

- `.moai/specs/SPEC-OCR-001/spec.md`, `plan.md` §B (경로 c 재범위 조정, §B D4 이연 앵커 레시피 — 본 앰언드먼트가 그대로 적용)
- `src/markdown_creat/ocr.py` (재사용 대상, 수정하지 않음)
- `src/markdown_creat/telegram_bot/extract.py`, `handlers.py` (수정하지 않음 — 브리지 계층을 통해 효과가 투명하게 전파됨)
