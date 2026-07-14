---
id: SPEC-PDF-001
title: "PDF → 마크다운 변환 코어 기능 (compact)"
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

# SPEC-PDF-001 (compact)

**목표**: PDF 파일 → 텍스트 + 제목 구조 추출 → 지정 경로 `.md` 파일 생성. CLI 없는 코어 라이브러리 함수(`pdf_to_markdown(pdf_path, output_path) -> None`). PyMuPDF(fitz) 기반. Tier M.

**요구사항 (EARS)**:
- REQ-PDF-001/002/003: 페이지 텍스트 읽기 순서 추출, 폰트 크기 휴리스틱으로 제목→마크다운 제목 레벨, 그 외는 문단.
- REQ-PDF-004/005: 유효 입력 시 출력 경로에 UTF-8 `.md` 기록, 기존 파일 덮어쓰기.
- REQ-PDF-006: PDF 파일 부재 → 명확한 오류(불투명 스택 트레이스 금지).
- REQ-PDF-007: 손상 PDF → 파싱 불가 명확한 오류(조용한 실패 금지).
- REQ-PDF-008: 암호화 PDF → 명확한 오류(빈/부분 결과 금지).
- REQ-PDF-009: 추출 텍스트 없음(스캔·이미지 전용) → 명확한 오류(빈 `.md` 금지).
- REQ-PDF-010: 오류 시 부분 기록 `.md` 잔존 금지.

**인수 기준**:
- AC-PDF-001a~c: 텍스트 추출·제목 감지·덮어쓰기.
- AC-PDF-002a~e: 부재·손상·암호화·텍스트없음·부분출력없음 오류.
- 커버리지 85% (`quality.yaml` 전역 기본값).

**범위 밖**: 표 추출, 이미지/도표 추출, OCR, 배치/다중 파일, CLI, GUI.

**리스크**: PyMuPDF는 AGPL — 상업적 재배포 시 라이선스 검토 필요(plan.md §D).

**스택**: Python 3.10+, PyMuPDF(fitz), TDD, ruff/black/pytest.
