---
id: SPEC-PDF-001
title: "PDF → 마크다운 변환 코어 기능 — 인수 기준"
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

# SPEC-PDF-001 — 인수 기준 (acceptance.md)

## §D. 인수 시나리오 (Given-When-Then)

### AC-PDF-001a — 텍스트 추출 및 파일 생성 (REQ-PDF-001, 003, 004)
- **Given** 본문 텍스트를 담은 유효한 텍스트 기반 PDF 파일이 존재하고,
- **When** 변환 함수를 PDF 경로 · 출력 경로와 함께 호출하면,
- **Then** 지정된 출력 경로에 UTF-8 `.md` 파일이 생성되고, PDF의 본문 텍스트가 읽기 순서대로 문단 형태로 포함된다.

### AC-PDF-001b — 제목 구조 감지 (REQ-PDF-002)
- **Given** 큰 폰트의 제목과 작은 폰트의 본문이 구분되는 PDF가 존재하고,
- **When** 변환 함수를 호출하면,
- **Then** 큰 폰트 텍스트가 마크다운 제목(`#`/`##` 등)으로, 본문 텍스트가 문단으로 표현된 `.md` 파일이 생성된다.

### AC-PDF-001c — 기존 파일 덮어쓰기 (REQ-PDF-005)
- **Given** 출력 경로에 이미 파일이 존재하고,
- **When** 동일 출력 경로로 변환 함수를 호출하면,
- **Then** 기존 파일이 새 변환 결과로 덮어써진다.

### AC-PDF-002a — PDF 파일 부재 오류 (REQ-PDF-006)
- **Given** 존재하지 않는 PDF 경로가 주어지고,
- **When** 변환 함수를 호출하면,
- **Then** 어떤 파일이 없는지 식별 가능한 명확한 오류가 발생하며, 불투명한 스택 트레이스로 종료되지 않는다.

### AC-PDF-002b — 손상된 PDF 오류 (REQ-PDF-007)
- **Given** 손상되어 파싱할 수 없는 PDF 파일이 주어지고,
- **When** 변환 함수를 호출하면,
- **Then** 파일을 읽을 수 없음을 사용자가 이해할 수 있는 형태로 알리는 명확한 오류가 발생하며, 조용히 실패하지 않는다.

### AC-PDF-002c — 암호화된 PDF 오류 (REQ-PDF-008)
- **Given** 비밀번호로 보호된(암호화된) PDF 파일이 주어지고,
- **When** 변환 함수를 호출하면,
- **Then** 암호화된 PDF임을 알리는 명확한 오류가 발생하며, 빈/부분 결과 파일이 생성되지 않는다.

### AC-PDF-002d — 추출 텍스트 없음 오류 (REQ-PDF-009)
- **Given** 스캔·이미지 전용이거나 추출 가능한 텍스트가 없는 PDF가 주어지고,
- **When** 변환 함수를 호출하면,
- **Then** 추출된 텍스트가 없음을 알리는 명확한 오류가 발생하며, 빈 `.md` 파일이 기록되지 않는다.

### AC-PDF-002e — 오류 시 부분 출력 없음 (REQ-PDF-010)
- **Given** 위 오류 조건(002a~002d) 중 하나가 발생하는 입력이 주어지고,
- **When** 변환 함수를 호출하면,
- **Then** 출력 경로에 불완전하거나 부분적으로 기록된 `.md` 파일이 남지 않는다.

## §D.1 엣지 케이스 (Edge Cases)

- 폰트 크기가 균일하여 제목/본문 구분이 어려운 PDF → 모든 텍스트를 문단으로 처리(제목 없음)하며, 이는 오류가 아니다.
- 여러 페이지에 걸친 문서 → 페이지 순서대로 텍스트가 연결되어 하나의 `.md`로 병합된다.
- 출력 경로 부모 디렉터리 부재 → plan.md §D에서 확정한 정책에 따라 동작(생성 또는 명확한 오류).
- 한글 등 비ASCII 콘텐츠 → UTF-8로 정확히 기록됨.

## §D.2 품질 게이트 / Definition of Done

- [ ] AC-PDF-001a~c, AC-PDF-002a~e 전 시나리오 통과.
- [ ] 테스트 커버리지 85% 이상 (`quality.yaml` `constitution.test_coverage_target`).
- [ ] `ruff` 린트 무경고, `black` 포맷 준수.
- [ ] `pytest` 전체 그린.
- [ ] spec.md의 REQ-PDF-001~010이 각각 최소 1개 테스트로 검증됨(추적성).
- [ ] 채택한 제목 감지 휴리스틱이 plan.md §C M2에 문서화됨(REQ-PDF-002 "문서화된 휴리스틱").
