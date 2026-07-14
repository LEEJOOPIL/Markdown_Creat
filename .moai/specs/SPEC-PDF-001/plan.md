---
id: SPEC-PDF-001
title: "PDF → 마크다운 변환 코어 기능 — 구현 계획"
version: "0.1.0"
status: draft
created: 2026-07-14
updated: 2026-07-14
author: manager-spec
priority: P1
phase: "v0.1.0 target"
module: "src/markdown_creat"
lifecycle: spec-anchored
tags: "pdf, markdown, extraction, pymupdf, conversion"
tier: M
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

### M1 — 공개 API 인터페이스 결정 (변경 가능성 최상)
- `pdf_to_markdown.py`의 코어 공개 함수 시그니처 확정: 인자(pdf_path, output_path)의 형태(문자열/Path), 반환값(None), 예외 계약.
- 이는 하위 모든 호출자(향후 CLI 포함)가 의존하는 계약이므로 사람 검토가 가장 필요한 지점이다.
- RED: 성공 경로에 대한 실패 테스트 작성.

### M2 — 제목 감지 휴리스틱 결정 (변경 가능성 상)
- 폰트 크기/스타일을 제목 레벨로 매핑하는 규칙 확정(REQ-PDF-002). 예: 문서 내 폰트 크기 분포를 수집해 상위 N개 크기를 `#`~`###`에 매핑, 본문 크기는 문단으로. 굵기(bold) 보조 신호 사용 여부 결정.
- 휴리스틱이 지나치게 복잡해질 경우 Tier M 범위에 맞춰 단순화(예: 크기 기준 상위 1~3레벨만) — 선택한 휴리스틱을 spec/plan에 문서화(REQ-PDF-002의 "문서화된 휴리스틱" 충족).
- RED: 제목/문단 분류에 대한 실패 테스트 작성.

### M3 — 오류 처리 계약 결정 (변경 가능성 상)
- 파일 부재(REQ-PDF-006), 손상(REQ-PDF-007), 암호화(REQ-PDF-008), 추출 텍스트 없음(REQ-PDF-009)에 대해 발생시킬 예외 타입/메시지 형태 확정.
- 부분 출력 방지(REQ-PDF-010) 전략(마크다운 완성 후에만 파일 기록) 확정.
- RED: 각 오류 케이스에 대한 실패 테스트 작성.

### M4 — 구현 (GREEN, 기계적)
- `pdf_to_markdown.py` 최소 구현으로 테스트 통과. PyMuPDF 텍스트 딕셔너리(`page.get_text("dict")`) 기반 스팬 순회 구현.

### M5 — 리팩터 및 품질 게이트 (REFACTOR, 기계적)
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
