---
id: SPEC-PDF-001
title: "PDF → 마크다운 변환 코어 기능"
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

# SPEC-PDF-001 — PDF → 마크다운 변환 코어 기능

## HISTORY

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 0.1.0 | 2026-07-14 | manager-spec | 최초 초안 작성. PDF 파일 → 텍스트·제목 구조 추출 → `.md` 파일 변환 코어 기능 정의. PyMuPDF(fitz) 기반. Tier M. |
| 0.2.0 | 2026-07-18 | manager-spec | **In-place amendment.** REQ-PDF-009를 개정하여 `pdf_to_markdown()`이 텍스트 없음(스캔·이미지 전용 PDF)을 감지했을 때 즉시 오류를 발생시키기 전에 SPEC-OCR-001의 `extract_pdf_text_via_ocr()`(언어 `kor+eng`)를 자동으로 호출하는 OCR 폴백을 코어 함수 내부에 통합한다. OCR로도 텍스트를 찾지 못하면 기존과 동일하게 `PDFNoTextError`를 발생시킨다(동작 계약 재확인, REQ-PDF-009). OCR 엔진 자체의 오류(Tesseract 미설치·언어팩 누락 등)는 신설된 `PDFOCRFailedError`로 구분해 발생시킨다(REQ-PDF-011 신설). OCR 언어 기본값 `kor+eng`를 명시한다(REQ-PDF-012 신설). §Exclusions의 OCR 배제 항목을 "OCR 자동 폴백 자체"에서 "OCR 세부 범위(정확도 튜닝·언어 설정 가능화·페이지 수 제한)"로 좁혀 재작성한다. 동기: 텔레그램 봇으로 전송된 스캔 PDF가 원본은 저장되나 본문에 OCR 텍스트 없이 고정 실패 메시지만 기록되는 라이브 사용자 리포트. SPEC-OCR-001이 이 통합 지점을 명시적으로 이연해 두었다(SPEC-OCR-001 plan.md §B D4 "이연 앵커 레시피"). |

## Amendments

- **prior_completed_version**: `0.1.0`
- **prior_completed_sha**: `b19d6223` (커밋 `docs(SPEC-PDF-001): sync-phase artifacts` — 0.1.0을 `completed`로 전환한 sync 커밋)
- **rationale**: SPEC-OCR-001(`status: completed`, v0.3.0)이 코어 OCR 함수 `extract_pdf_text_via_ocr()`를 `src/markdown_creat/ocr.py`에 신설하면서, 그 유일한 예정 소비자인 `pdf_to_markdown()` 자동 OCR 폴백 통합을 "SPEC-PDF-001 자신의 향후 앰언드먼트가 소유"하도록 의도적으로 이연했다(SPEC-OCR-001 spec.md §Exclusions, plan.md §B 경로 c). SPEC-OCR-001 완료 이후 라이브 사용자가 텔레그램 봇으로 스캔 PDF를 전송했을 때 원본만 저장되고 OCR이 전혀 시도되지 않는 것을 확인했다 — 이연되었던 통합 지점이 실제로 필요해진 시점이다. 본 앰언드먼트는 이미 완성되어 있는 `extract_pdf_text_via_ocr()`를 배선(wiring)할 뿐, 신규 OCR 로직을 구현하지 않는다.
- **scope**: REQ-PDF-009(개정), REQ-PDF-011(신설), REQ-PDF-012(신설). REQ-PDF-001~008, REQ-PDF-010은 변경 없음. `§Exclusions — OCR` 항목 재작성.

---

## §A. 개요 (Context)

`markdown_creat`는 문서를 표준화된 마크다운으로 다루는 Python 도구이다. SPEC-GEN-001이 **템플릿 + 데이터 → `.md` 생성**(순방향)을 다루는 반면, 본 SPEC은 그 **반대 방향**인 **기존 PDF 문서 → `.md` 변환**을 정의한다.

- **입력**: PDF 파일 경로 1개
- **동작**: PDF에서 본문 텍스트를 읽기 순서대로 추출하고, 폰트 크기/스타일 휴리스틱으로 제목 구조를 감지하여 마크다운 제목(`#`, `##`, ...)과 문단으로 재구성
- **출력**: 변환된 마크다운을 호출자가 지정한 경로의 `.md` 파일로 저장

본 기능은 CLI 진입점이 아니라, PDF 경로 · 출력 경로를 인자로 받아 `.md` 파일을 생성하는 **Python 함수/모듈** 수준의 기능이다. 이는 SPEC-GEN-001 생성기의 입출력 패턴(경로 인자 → 파일 기록)과 일관된다. 표 추출, 이미지 추출, 배치 처리, CLI는 본 SPEC의 범위가 아니다(§Exclusions 참조). **OCR은 v0.1.0에서는 전면 배제였으나, v0.2.0 앰언드먼트로 "텍스트 없음 감지 시 자동 폴백"에 한해 범위 안으로 들어왔다** — OCR 세부 범위(정확도 튜닝, 언어 설정 가능화, 페이지 수 제한)는 여전히 범위 밖이다(§Exclusions 참조).

제안 공개 인터페이스(형태는 plan.md M1에서 확정):

```python
def pdf_to_markdown(pdf_path: str, output_path: str) -> None: ...
```

기술 기반: Python 3.10+, PDF 파서 **PyMuPDF (fitz)**. PyMuPDF의 AGPL 라이선스 관련 검토 사항은 상업적 재배포 시 라이선스 리뷰가 필요할 수 있으므로 `plan.md §D 리스크`에 제약/리스크로 명시한다(사용자 명시 선택에 따라 PyMuPDF 채택 진행).

---

## §B. 요구사항 (EARS Requirements)

### 텍스트 및 제목 구조 추출

- **REQ-PDF-001 (Ubiquitous)**: The system shall PDF 파일의 각 페이지에서 본문 텍스트를 읽기 순서대로 추출한다.
- **REQ-PDF-002 (Ubiquitous)**: The system shall 문서화된 휴리스틱(폰트 크기/스타일 기반)으로 제목을 감지하여, 감지된 제목을 마크다운 제목 레벨(`#`, `##`, `###` ...)로 표현한다.
- **REQ-PDF-003 (Ubiquitous)**: The system shall 제목이 아닌 텍스트를 마크다운 문단으로 표현하며, 문단 간 구분을 보존한다.

### 출력 파일 생성

- **REQ-PDF-004 (Event-driven)**: When 변환 함수가 유효한 PDF 경로 · 출력 경로와 함께 호출되면, the system shall 변환된 마크다운을 지정된 출력 경로에 UTF-8 인코딩의 `.md` 파일로 기록한다.
- **REQ-PDF-005 (Event-driven)**: When 출력 파일이 이미 존재하는 경로로 변환 함수가 호출되면, the system shall 기존 파일을 변환 결과로 덮어쓴다.

### 오류 처리 (Unwanted Behavior)

- **REQ-PDF-006 (Event-driven / unwanted)**: When 지정된 경로에 PDF 파일이 존재하지 않으면, the system shall 요청된 PDF 파일 경로를 포함하여 어떤 파일이 없는지 평이한 언어로 명시하는 오류 메시지와 함께 오류를 발생시키며, 불투명한 스택 트레이스로 종료되지 않는다.
- **REQ-PDF-007 (Event-driven / unwanted)**: When PDF 파일이 손상되어 파싱할 수 없으면, the system shall 요청된 PDF 파일 경로를 포함하여 파일을 파싱할 수 없음을 평이한 언어로 명시하는 오류 메시지와 함께 오류를 발생시키며, 조용히 실패하지 않는다.
- **REQ-PDF-008 (Event-driven / unwanted)**: When PDF가 암호화(비밀번호 보호)되어 있으면, the system shall 요청된 PDF 파일 경로를 포함하여 PDF가 암호화되어 있음을 평이한 언어로 명시하는 오류 메시지와 함께 오류를 발생시키며, 빈 결과나 부분 결과를 만들지 않는다.
- **REQ-PDF-009 (Event-driven / unwanted) — v0.2.0 개정**: When PDF의 텍스트 레이어에서 추출 가능한 텍스트가 없으면(예: 스캔·이미지 전용 PDF), the system shall 즉시 오류를 발생시키기 전에 각 페이지를 이미지로 렌더링하여 광학 문자 인식(OCR)을 자동으로 시도하고, OCR을 통해서도 추출 가능한 텍스트를 찾지 못하면 요청된 PDF 파일 경로를 포함하여 추출 가능한 텍스트가 없음을 평이한 언어로 명시하는 오류 메시지와 함께 오류를 발생시키며, 빈 `.md` 파일을 기록하지 않는다. OCR로 텍스트를 찾은 경우, 그 텍스트를 본문으로 하는 `.md` 파일을 정상적으로 기록한다(REQ-PDF-004와 동일한 출력 계약 — 단 OCR 결과에는 폰트 크기 메타데이터가 없으므로 제목 구조 없이 문단으로만 기록된다). OCR을 수행하는 구체적 함수·모듈은 본 spec.md의 범위가 아니며 `plan.md §F`에서 확정한다.
- **REQ-PDF-010 (Ubiquitous / unwanted)**: The system shall 오류 발생 시 불완전하거나 부분적으로 기록된 `.md` 파일을 출력 경로에 남기지 않는다. (v0.2.0: 이 불변조건은 REQ-PDF-009의 OCR 폴백 경로와 REQ-PDF-011의 OCR 엔진 오류 경로에도 동일하게 적용된다 — 마크다운 문자열은 OCR 폴백을 포함한 모든 추출 시도가 성공적으로 완료된 뒤에만 조립되어, 조립이 완료되기 전 어떤 오류 경로도 파일 기록 단계에 도달하지 않는다.)

### OCR 폴백 (신규 — v0.2.0 앰언드먼트, SPEC-OCR-001 통합)

- **REQ-PDF-011 (Event-driven / unwanted)**: When REQ-PDF-009의 OCR 폴백 시도 중 OCR 엔진 자체의 오류(예: OCR 엔진 미설치, 지정된 언어팩 누락, 페이지 렌더링 실패)가 발생하면, the system shall 그 원본 OCR 엔진 오류의 메시지 텍스트를 포함하는 오류 메시지와 함께 오류를 발생시키며(추출 가능한 텍스트가 끝내 없다는 오류와는 구분되는 별도의 오류 타입), 빈 `.md` 파일이나 부분적으로 기록된 `.md` 파일을 남기지 않는다.
- **REQ-PDF-012 (Ubiquitous)**: The system shall REQ-PDF-009의 OCR 폴백 시 언어 파라미터로 `kor+eng`(한국어+영어)를 사용한다(텔레그램 봇 사진 경로의 기존 기본값과 일관성 유지 — SPEC-OCR-001 REQ-OCR-015 참조). 이 언어 값은 리터럴로 고정되며 설정 가능하지 않다(§Exclusions 참조).

### 다중 페이지 처리 (v0.2.0 신설 — 기존 엣지 케이스의 REQ 수준 추적성 보강)

- **REQ-PDF-013 (Ubiquitous)**: The system shall 다중 페이지 PDF를 변환할 때 각 페이지에서 추출된 텍스트(REQ-PDF-001의 텍스트 레이어 추출 경로 또는 REQ-PDF-009의 OCR 폴백 경로 중 실제로 사용된 경로의 결과)를 페이지 순서대로 연결하여 단일 출력 `.md` 파일로 병합한다.

> 구현 수준의 함수명·예외 클래스명(`extract_pdf_text_via_ocr()`, `PDFNoTextError`, `PDFOCRFailedError` 등)은 spec.md에 명시하지 않는다 — 이는 `plan.md §F`(기술 접근)와 `acceptance.md`(검증 시나리오)의 범위다.

---

## §C. 제약 및 품질 게이트 (Constraints)

- Python 3.10+, PyMuPDF(fitz)만 PDF 파싱에 사용한다(사용자 명시 선택).
- 개발 방법론: `quality.yaml`의 `development_mode: tdd` (RED-GREEN-REFACTOR).
- 품질 게이트: `ruff`(린트) + `black`(포맷) + `pytest`(테스트), 커버리지 85% 이상.
- 출력 인코딩은 UTF-8로 고정한다(한글 문서 대응).
- 코드 식별자 · 함수명 · 기술 용어는 영어로 작성한다(언어 정책).
- PyMuPDF AGPL 라이선스 검토 사항은 `plan.md §D`에서 리스크로 다룬다(본 spec.md 범위에는 포함하지 않음).
- **v0.2.0**: OCR 폴백은 `src/markdown_creat/ocr.py`(SPEC-OCR-001, `status: completed`)의 기존 공개 함수 `extract_pdf_text_via_ocr()`를 재사용한다 — OCR 파싱 로직(Tesseract 호출)을 재구현하지 않는다. `pytesseract`는 `pyproject.toml`에 이미 프로젝트 전역 의존성으로 선언되어 있으므로(SPEC-OCR-001에서 추가됨) 본 앰언드먼트는 신규 pip 의존성을 추가하지 않는다.

---

## §Exclusions / 만들지 않는 것 (What NOT to Build)

본 SPEC은 텍스트 + 제목 구조 추출 코어 기능에만 집중한다. 아래 항목은 명시적으로 범위 밖이며 향후 별도 SPEC으로 분리한다.

### Out of Scope — 표 추출
- PDF 내 표(table) 감지 및 마크다운 표 생성은 본 SPEC에서 구현하지 않는다. 향후 별도 SPEC으로 분리한다.

### Out of Scope — 이미지/도표 추출
- PDF 내 이미지·도표(figure)의 추출, 저장, 마크다운 임베딩은 범위 밖이다.

### Out of Scope — OCR 세부 범위 (v0.2.0 개정 — 자동 폴백 자체는 더 이상 배제되지 않음)
- **v0.1.0에서는 이 항목이 "스캔·이미지 전용 PDF의 OCR 자체를 배제"했으나, v0.2.0 앰언드먼트로 그 배제는 철회되었다** — REQ-PDF-009가 개정되어 텍스트 없음 감지 시 자동 OCR 폴백을 코어 함수 내부에서 시도한다(§Amendments 참조). 아래는 v0.2.0 이후에도 여전히 범위 밖으로 남는 OCR 관련 세부 항목이다.
- **OCR 이미지 전처리·정확도 튜닝**: 이진화(binarization), 노이즈 제거, 기울기 보정(deskew) 등 OCR 정확도를 높이기 위한 이미지 전처리 파이프라인은 구현하지 않는다(SPEC-OCR-001 §Exclusions 상속). Tesseract 기본 설정 + PyMuPDF 300 DPI 렌더링만 사용한다.
- **OCR 언어의 설정 가능화**: REQ-PDF-012는 언어 값을 리터럴 `kor+eng`로 고정한다. 환경변수·설정 파일·사용자별 언어 선택 등으로 설정 가능하게 만드는 작업은 범위 밖이다(별도 관심사 — SPEC-OCR-001 REQ-OCR-015의 동일한 배제 결정과 일관).
- **대용량 스캔 PDF의 페이지 수/시간 제한**: 다수 페이지로 구성된 스캔 PDF에 대해 OCR 폴백이 소요할 수 있는 처리 시간에 상한(최대 페이지 수, 타임아웃)을 두지 않는다. 근거와 잔여 위험은 `plan.md §D 리스크`에 기록한다. 이 제한이 실제 운영 문제로 확인되면 별도 SPEC(또는 본 SPEC의 후속 앰언드먼트)에서 다룬다.
- **OCR 결과에 대한 제목 구조 감지**: OCR로 추출된 텍스트는 폰트 크기 메타데이터가 없으므로(SPEC-OCR-001 acceptance.md §D.1), REQ-PDF-002의 제목 감지 휴리스틱을 OCR 결과에 적용하지 않는다 — OCR 폴백 경로의 출력은 항상 문단으로만 구성된다.

### Out of Scope — 배치/다중 파일 처리
- 여러 PDF를 일괄 변환하는 배치 기능은 범위 밖이다. 본 SPEC은 단일 PDF → 단일 `.md`만 다룬다.

### Out of Scope — CLI 및 GUI
- 커맨드라인 진입점(`cli.py`), 인자 파싱, `python -m markdown_creat` 실행 방식과 모든 형태의 GUI는 본 SPEC에서 구현하지 않는다. 본 기능은 코어 라이브러리 함수로만 제공한다.

---

## §E. 참조 (Cross-References)

- 프로젝트 문서: `.moai/project/product.md`, `.moai/project/structure.md`, `.moai/project/tech.md`
- 관련 SPEC(순방향 생성): `.moai/specs/SPEC-GEN-001/spec.md`
- 의존 SPEC(v0.2.0 앰언드먼트 — `depends_on`, OCR 코어 함수 소유): `.moai/specs/SPEC-OCR-001/spec.md`, `plan.md` §B (경로 c 재범위 조정 근거 + §B D4 이연 앵커 레시피 — 본 앰언드먼트가 그대로 적용함)
- 품질 설정: `.moai/config/sections/quality.yaml`
- 구현 계획: `plan.md`
- 상세 인수 기준: `acceptance.md`
