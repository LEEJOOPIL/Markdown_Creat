---
id: SPEC-PDF-001
title: "PDF → 마크다운 변환 코어 기능 — 인수 기준"
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

# SPEC-PDF-001 — 인수 기준 (acceptance.md)

## §D. 인수 시나리오 (GEARS)

각 인수 기준(AC)은 단일 절의 EARS/GEARS 패턴 문장(Event-driven `When [trigger], the system shall [response]` 또는 Unwanted `When [undesired-condition-detected], the system shall not [undesired]`)으로 기술한다. "Given"은 GEARS가 인정하는 수식어(Where/While/When)에 포함되지 않으므로, 선행 조건(precondition)은 트리거 절(`When`) 안으로 접어 넣는다.

### AC-PDF-001a (Event-driven) — 텍스트 추출 및 파일 생성 (REQ-PDF-001, 003, 004)

When 변환 함수가 본문 텍스트를 담은 유효한 텍스트 기반 PDF 경로와 출력 경로와 함께 호출되면, the system shall 지정된 출력 경로에 UTF-8 `.md` 파일을 생성하고, PDF의 본문 텍스트를 읽기 순서대로 문단 형태로 그 파일에 포함시킨다.

### AC-PDF-001b (Event-driven) — 제목 구조 감지 (REQ-PDF-002)

When 변환 함수가 큰 폰트의 제목과 작은 폰트의 본문이 구분되는 PDF와 함께 호출되면, the system shall 큰 폰트 텍스트를 마크다운 제목(`#`/`##` 등)으로, 본문 텍스트를 문단으로 표현한 `.md` 파일을 생성한다.

### AC-PDF-001c (Event-driven) — 기존 파일 덮어쓰기 (REQ-PDF-005)

When 출력 경로에 이미 파일이 존재하는 상태에서 변환 함수가 동일 출력 경로와 함께 호출되면, the system shall 기존 파일을 새 변환 결과로 덮어쓴다.

### AC-PDF-002a (Event-driven) — PDF 파일 부재 오류 (REQ-PDF-006)

When 변환 함수가 존재하지 않는 PDF 경로와 함께 호출되면, the system shall 요청된 PDF 파일 경로를 포함하여 어떤 파일이 없는지 평이한 언어로 명시하는 오류 메시지와 함께 `PDFNotFoundError`를 발생시키며, 불투명한 스택 트레이스로 종료되지 않는다.

### AC-PDF-002b (Event-driven) — 손상된 PDF 오류 (REQ-PDF-007)

When 변환 함수가 손상되어 파싱할 수 없는 PDF 파일과 함께 호출되면, the system shall 요청된 PDF 파일 경로를 포함하여 파일을 파싱할 수 없음을 평이한 언어로 명시하는 오류 메시지와 함께 `PDFCorruptedError`를 발생시키며, 조용히 실패하지 않는다.

### AC-PDF-002c (Event-driven) — 암호화된 PDF 오류 (REQ-PDF-008)

When 변환 함수가 비밀번호로 보호된(암호화된) PDF 파일과 함께 호출되면, the system shall 요청된 PDF 파일 경로를 포함하여 PDF가 암호화되어 있음을 평이한 언어로 명시하는 오류 메시지와 함께 `PDFEncryptedError`를 발생시키며, 빈/부분 결과 파일을 생성하지 않는다.

### AC-PDF-002d (Event-driven) — 추출 텍스트 없음 오류 (REQ-PDF-009)

When 변환 함수가 스캔·이미지 전용이거나 추출 가능한 텍스트가 없는 PDF와 함께 호출되면, the system shall 요청된 PDF 파일 경로를 포함하여 추출 가능한 텍스트가 없음을 평이한 언어로 명시하는 오류 메시지와 함께 `PDFNoTextError`를 발생시키며, 빈 `.md` 파일을 기록하지 않는다.

### AC-PDF-002e (Unwanted) — 오류 시 부분 출력 없음 (REQ-PDF-010)

When 위 오류 조건(AC-PDF-002a~002d) 중 하나가 발생하면, the system shall not 출력 경로에 불완전하거나 부분적으로 기록된 `.md` 파일을 남긴다.

### AC-PDF-003a (Event-driven) — 스캔 PDF, OCR 복구 가능한 텍스트 있음 → 성공 (REQ-PDF-009 개정, 신규 v0.2.0)

When 텍스트 레이어가 없는 스캔 PDF(예: `make_no_text_pdf()`가 생성하는, 텍스트 레이어 없이 렌더링 가능한 페이지)와 `markdown_creat.ocr.pytesseract.image_to_string`이 비어있지 않은 텍스트(예: `"Hello from OCR"`)를 반환하도록 모킹된 상태에서 변환 함수가 PDF 경로 · 출력 경로와 함께 호출되면, the system shall `PDFNoTextError`를 발생시키지 않고, 지정된 출력 경로에 UTF-8 `.md` 파일을 생성하며, 그 본문에 OCR이 반환한 텍스트를 포함시키고, `extract_pdf_text_via_ocr()`를 `lang="kor+eng"`로 호출한다(REQ-PDF-012).

### AC-PDF-003b (Event-driven) — 스캔 PDF, OCR도 텍스트를 찾지 못함 → 기존과 동일하게 실패 (REQ-PDF-009 개정, 신규 v0.2.0)

When 텍스트 레이어가 없는 PDF와 `markdown_creat.ocr.pytesseract.image_to_string`이 빈 문자열(`""`)을 반환하도록 모킹된 상태(진짜로 복구 가능한 텍스트가 없는 스캔 페이지를 시뮬레이션)에서 변환 함수가 호출되면, the system shall (v0.1.0과 동일하게) 요청된 PDF 파일 경로를 포함하여 추출 가능한 텍스트가 없음을 평이한 언어로 명시하는 오류 메시지와 함께 `PDFNoTextError`를 발생시키며, 빈 `.md` 파일을 기록하지 않는다 — AC-PDF-002d/002e의 기존 검증이 이 경로에서도 그대로 유지된다.

### AC-PDF-003c (Event-driven) — OCR 엔진 자체 오류 → `PDFOCRFailedError` (REQ-PDF-011, 신규 v0.2.0)

When 텍스트 레이어가 없는 PDF와 `markdown_creat.ocr.pytesseract.image_to_string`이 엔진 오류(예: `RuntimeError("tesseract is not installed")`)를 발생시키도록 모킹된 상태에서 변환 함수가 호출되면, the system shall `PDFOCRFailedError`(`MarkdownConversionError`의 하위 클래스)를 발생시키되 그 메시지에 원본 OCR 엔진 오류의 메시지 텍스트(예: `"tesseract is not installed"`)를 포함시키며, 빈/부분 `.md` 파일을 출력 경로에 남기지 않는다.

### AC-PDF-003d (Event-driven) — 기존 텍스트 포함 PDF는 회귀 없음 — OCR 폴백 미호출 (REQ-PDF-001~004, 회귀 확인, 신규 v0.2.0)

When 본문 텍스트를 담은 유효한 텍스트 기반 PDF(AC-PDF-001a와 동일 픽스처)와 함께 변환 함수가 호출되면, the system shall AC-PDF-001a와 동일하게 텍스트 레이어 추출만으로 `.md`를 생성하고, `markdown_creat.ocr.pytesseract.image_to_string`(OCR 경로)을 호출하지 않는다(mock `assert_not_called()`로 검증) — 텍스트 레이어가 있는 PDF는 OCR 폴백 분기에 전혀 도달하지 않음을 명시적으로 확인한다.

## §D.1 엣지 케이스 (Edge Cases)

- 폰트 크기가 균일하여 제목/본문 구분이 어려운 PDF → 모든 텍스트를 문단으로 처리(제목 없음)하며, 이는 오류가 아니다.
- 여러 페이지에 걸친 문서 (REQ-PDF-013) → 페이지 순서대로 텍스트가 연결되어 하나의 `.md`로 병합된다.
- 출력 경로 부모 디렉터리 부재 → plan.md §D에서 확정한 정책에 따라 동작(생성 또는 명확한 오류).
- 한글 등 비ASCII 콘텐츠 → UTF-8로 정확히 기록됨.
- **(v0.2.0)** OCR 폴백으로 생성된 `.md` 본문에는 제목 구조(`#`/`##`/`###`)가 없다 — OCR 결과는 폰트 크기 메타데이터를 갖지 않으므로 REQ-PDF-002의 제목 감지 휴리스틱이 적용되지 않으며, 이는 오류가 아니라 의도된 동작이다(`spec.md §Exclusions` 참조).
- **(v0.2.0)** OCR이 반환한 텍스트가 공백만으로 구성된 경우(`" \n ".strip() == ""`)는 "텍스트 없음"으로 취급하여 `PDFNoTextError`를 발생시킨다 — 빈 문자열과 공백 전용 문자열을 동일하게 처리한다.
- **(v0.2.0)** 다중 페이지 스캔 PDF에 대한 페이지 수/시간 상한은 두지 않는다(`plan.md §F.2` 결정 3, `§F.4` 잔여 위험 참조) — 매우 큰 스캔 PDF는 처리 시간이 길어질 수 있으나 이는 본 앰언드먼트의 범위 밖으로 남는다.

## §D.2 품질 게이트 / Definition of Done

- [x] AC-PDF-001a~c, AC-PDF-002a~e 전 시나리오 통과. **(as-implemented, 2026-07-16, v0.1.0)** 8/8 AC PASS — 상세 검증 명령·출력은 `progress.md` §E.2 AC 매트릭스 참조.
- [ ] **(v0.2.0)** AC-PDF-003a~d 전 시나리오 통과 — run-phase에서 검증 예정(manager-develop). 완료 시 이 항목과 `progress.md`가 갱신된다.
- [x] 테스트 커버리지 85% 이상 (`quality.yaml` `constitution.test_coverage_target`). **실제 (v0.1.0)**: `pdf_to_markdown.py` 95% (76 stmts, 4 miss). 단, run-phase(2026-07-16) 당시 커버리지 수치는 `progress.md` §E.2에 기록되지 않았으므로 이 값은 **2026-07-17 사후 측정**이다 — `.venv/Scripts/python.exe -m pytest tests/test_pdf_to_markdown.py --cov=markdown_creat.pdf_to_markdown -q`. **(v0.2.0)**: 신규 OCR 폴백 분기를 포함해 85% 이상 재확인 필요 — run-phase에서 측정.
- [x] `ruff` 린트 무경고, `black` 포맷 준수. **실제 (v0.1.0)**: `progress.md` §E.3 `new_warnings_or_lints_introduced: 0`. **(v0.2.0)**: run-phase에서 재확인.
- [x] `pytest` 전체 그린. **실제 (v0.1.0)**: 17 passed (`progress.md` §E.4 sync 재검증 및 2026-07-17 재확인 모두 17 passed). **(v0.2.0)**: 기존 17개 + 신규 AC-PDF-003a~d 테스트 전체 그린 필요 — run-phase에서 재확인.
- [x] spec.md의 REQ-PDF-001~010이 각각 최소 1개 테스트로 검증됨(추적성). **실제 (v0.1.0)**: REQ별 테스트 매핑이 `progress.md` §E.2 "REQ traceability"에 기록됨(10/10 커버). **(v0.2.0)**: REQ-PDF-009(개정), REQ-PDF-011, REQ-PDF-012도 각각 최소 1개 테스트로 검증 필요 — run-phase에서 추적성 매핑 갱신. REQ-PDF-013(다중 페이지 병합, §D.1 엣지 케이스로 추적)은 기존 다중 페이지 픽스처 테스트로 이미 검증됨을 run-phase에서 재확인한다(신규 테스트 불필요 — v0.1.0부터 존재하는 동작의 REQ 수준 추적성 보강일 뿐).
- [x] 채택한 제목 감지 휴리스틱이 문서화됨(REQ-PDF-002 "문서화된 휴리스틱"). **실제**: 채택된 휴리스틱(빈도 최다 폰트 크기를 본문으로 판정, 그보다 큰 크기를 내림차순으로 제목 레벨 1~3에 매핑)은 `plan.md` §C M2가 아니라 `progress.md` §E.2 "Design decisions made during run-phase"에 기록되어 있다 — 요구사항은 충족하나 위치가 본 DoD 항목의 원래 서술과 다르다. (v0.2.0에서는 변경 없음 — OCR 폴백 경로는 이 휴리스틱을 적용하지 않는다.)
- [ ] **(v0.2.0)** `extract_pdf_text_via_ocr()`가 `ocr.py`(SPEC-OCR-001) 원본 그대로 재사용되었고 재구현되지 않았음을 diff로 확인.
- [ ] **(v0.2.0)** 기존 텍스트 기반 PDF 경로(AC-PDF-001a~c, AC-PDF-002a~c)에 회귀가 없음을 전체 스위트 재실행으로 확인.
