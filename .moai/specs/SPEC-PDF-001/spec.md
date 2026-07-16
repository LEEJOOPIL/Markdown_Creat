---
id: SPEC-PDF-001
title: "PDF → 마크다운 변환 코어 기능"
version: "0.1.0"
status: completed
created: 2026-07-14
updated: 2026-07-16
author: manager-spec
priority: P1
phase: "v0.1.0 target"
module: "src/markdown_creat"
lifecycle: spec-anchored
tags: "pdf, markdown, extraction, pymupdf, conversion"
tier: M
---

# SPEC-PDF-001 — PDF → 마크다운 변환 코어 기능

## HISTORY

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 0.1.0 | 2026-07-14 | manager-spec | 최초 초안 작성. PDF 파일 → 텍스트·제목 구조 추출 → `.md` 파일 변환 코어 기능 정의. PyMuPDF(fitz) 기반. Tier M. |

---

## §A. 개요 (Context)

`markdown_creat`는 문서를 표준화된 마크다운으로 다루는 Python 도구이다. SPEC-GEN-001이 **템플릿 + 데이터 → `.md` 생성**(순방향)을 다루는 반면, 본 SPEC은 그 **반대 방향**인 **기존 PDF 문서 → `.md` 변환**을 정의한다.

- **입력**: PDF 파일 경로 1개
- **동작**: PDF에서 본문 텍스트를 읽기 순서대로 추출하고, 폰트 크기/스타일 휴리스틱으로 제목 구조를 감지하여 마크다운 제목(`#`, `##`, ...)과 문단으로 재구성
- **출력**: 변환된 마크다운을 호출자가 지정한 경로의 `.md` 파일로 저장

본 기능은 CLI 진입점이 아니라, PDF 경로 · 출력 경로를 인자로 받아 `.md` 파일을 생성하는 **Python 함수/모듈** 수준의 기능이다. 이는 SPEC-GEN-001 생성기의 입출력 패턴(경로 인자 → 파일 기록)과 일관된다. 표 추출, 이미지 추출, OCR, 배치 처리, CLI는 본 SPEC의 범위가 아니다(§Exclusions 참조).

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

- **REQ-PDF-006 (Event-driven / unwanted)**: When 지정된 경로에 PDF 파일이 존재하지 않으면, the system shall 어떤 파일이 없는지 식별 가능한 명확한 오류를 발생시키며, 불투명한 스택 트레이스로 종료되지 않는다.
- **REQ-PDF-007 (Event-driven / unwanted)**: When PDF 파일이 손상되어 파싱할 수 없으면, the system shall 파일을 읽을 수 없음을 사용자가 이해할 수 있는 형태로 알리는 명확한 오류를 발생시키며, 조용히 실패하지 않는다.
- **REQ-PDF-008 (Event-driven / unwanted)**: When PDF가 암호화(비밀번호 보호)되어 있으면, the system shall 암호화된 PDF임을 알리는 명확한 오류를 발생시키며, 빈 결과나 부분 결과를 만들지 않는다.
- **REQ-PDF-009 (Event-driven / unwanted)**: When PDF에서 추출 가능한 텍스트가 없으면(예: 스캔·이미지 전용 PDF), the system shall 추출된 텍스트가 없음을 알리는 명확한 오류를 발생시키며, 빈 `.md` 파일을 기록하지 않는다.
- **REQ-PDF-010 (Ubiquitous / unwanted)**: The system shall 오류 발생 시 불완전하거나 부분적으로 기록된 `.md` 파일을 출력 경로에 남기지 않는다.

---

## §C. 제약 및 품질 게이트 (Constraints)

- Python 3.10+, PyMuPDF(fitz)만 PDF 파싱에 사용한다(사용자 명시 선택).
- 개발 방법론: `quality.yaml`의 `development_mode: tdd` (RED-GREEN-REFACTOR).
- 품질 게이트: `ruff`(린트) + `black`(포맷) + `pytest`(테스트), 커버리지 85% 이상.
- 출력 인코딩은 UTF-8로 고정한다(한글 문서 대응).
- 코드 식별자 · 함수명 · 기술 용어는 영어로 작성한다(언어 정책).
- PyMuPDF AGPL 라이선스 검토 사항은 `plan.md §D`에서 리스크로 다룬다(본 spec.md 범위에는 포함하지 않음).

---

## §Exclusions / 만들지 않는 것 (What NOT to Build)

본 SPEC은 텍스트 + 제목 구조 추출 코어 기능에만 집중한다. 아래 항목은 명시적으로 범위 밖이며 향후 별도 SPEC으로 분리한다.

### Out of Scope — 표 추출
- PDF 내 표(table) 감지 및 마크다운 표 생성은 본 SPEC에서 구현하지 않는다. 향후 별도 SPEC으로 분리한다.

### Out of Scope — 이미지/도표 추출
- PDF 내 이미지·도표(figure)의 추출, 저장, 마크다운 임베딩은 범위 밖이다.

### Out of Scope — OCR (스캔·이미지 전용 PDF)
- 스캔되었거나 이미지로만 구성된 PDF에 대한 광학 문자 인식(OCR)은 다루지 않는다. 이러한 입력은 REQ-PDF-009에 따라 "추출 텍스트 없음" 오류로 처리한다.

### Out of Scope — 배치/다중 파일 처리
- 여러 PDF를 일괄 변환하는 배치 기능은 범위 밖이다. 본 SPEC은 단일 PDF → 단일 `.md`만 다룬다.

### Out of Scope — CLI 및 GUI
- 커맨드라인 진입점(`cli.py`), 인자 파싱, `python -m markdown_creat` 실행 방식과 모든 형태의 GUI는 본 SPEC에서 구현하지 않는다. 본 기능은 코어 라이브러리 함수로만 제공한다.

---

## §E. 참조 (Cross-References)

- 프로젝트 문서: `.moai/project/product.md`, `.moai/project/structure.md`, `.moai/project/tech.md`
- 관련 SPEC(순방향 생성): `.moai/specs/SPEC-GEN-001/spec.md`
- 품질 설정: `.moai/config/sections/quality.yaml`
- 구현 계획: `plan.md`
- 상세 인수 기준: `acceptance.md`
