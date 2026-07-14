---
id: SPEC-GEN-001
title: "템플릿 기반 마크다운 생성 코어 기능 — 인수 기준"
version: "0.1.0"
status: draft
created: 2026-07-14
updated: 2026-07-14
author: manager-spec
priority: P1
phase: "v0.1.0 target"
module: "src/markdown_creat"
lifecycle: spec-anchored
tags: "generation, jinja2, yaml, markdown, rendering"
---

# SPEC-GEN-001 — 인수 기준 (acceptance.md)

## §D. 인수 시나리오 (Given-When-Then)

### AC-GEN-001a — 정상 렌더링 및 파일 생성 (REQ-GEN-001, 002, 003)
- **Given** 유효한 Jinja2 템플릿 파일(`report.md.j2`, 예: `# {{ title }}\n작성자: {{ author }}`)과 유효한 YAML 데이터 파일(`sample_data.yaml`, 예: `title: 주간보고\nauthor: 홍길동`)이 존재하고,
- **When** 생성 함수를 템플릿 경로 · 데이터 경로 · 출력 경로와 함께 호출하면,
- **Then** 지정된 출력 경로에 `.md` 파일이 생성되고, 그 내용에 `# 주간보고` 및 `작성자: 홍길동`이 정확히 치환되어 포함된다.

### AC-GEN-001b — 중첩 구조 및 반복 렌더링 (REQ-GEN-002)
- **Given** 리스트를 순회하는 템플릿(`{% for item in items %}- {{ item }}\n{% endfor %}`)과 리스트 값을 담은 YAML 데이터가 존재하고,
- **When** 생성 함수를 호출하면,
- **Then** 리스트의 각 항목이 순서대로 렌더링된 `.md` 파일이 생성된다.

### AC-GEN-001c — 기존 파일 덮어쓰기 (REQ-GEN-004)
- **Given** 출력 경로에 이미 파일이 존재하고,
- **When** 동일 출력 경로로 생성 함수를 호출하면,
- **Then** 기존 파일이 새 렌더링 결과로 덮어써진다.

### AC-GEN-002a — 파일 부재 오류 (REQ-GEN-005)
- **Given** 존재하지 않는 템플릿 경로(또는 존재하지 않는 데이터 경로)가 주어지고,
- **When** 생성 함수를 호출하면,
- **Then** 어떤 파일이 없는지 식별 가능한 명확한 오류가 발생하며, 불투명한 스택 트레이스로 종료되지 않는다.

### AC-GEN-002b — 잘못된 YAML 문법 오류 (REQ-GEN-006)
- **Given** 문법이 깨진 YAML 데이터 파일이 주어지고,
- **When** 생성 함수를 호출하면,
- **Then** YAML 파싱 실패를 사용자가 이해할 수 있는 형태로 알리는 명확한 오류가 발생하며, 조용히 실패하지 않는다.

### AC-GEN-002c — 오류 시 부분 출력 없음 (REQ-GEN-007)
- **Given** 위 오류 조건 중 하나가 발생하는 입력이 주어지고,
- **When** 생성 함수를 호출하면,
- **Then** 출력 경로에 불완전하거나 부분적으로 렌더링된 `.md` 파일이 남지 않는다.

## §D.1 엣지 케이스 (Edge Cases)

- 빈 데이터 파일(유효한 빈 YAML) → 변수 없는 템플릿은 정상 렌더링, 변수 있는 템플릿의 미정의 변수 처리 정책은 plan.md §D 리스크에서 확정.
- 출력 경로 부모 디렉터리 부재 → plan.md §D에서 확정한 정책에 따라 동작(생성 또는 명확한 오류).
- 한글 등 비ASCII 콘텐츠 → UTF-8로 정확히 기록됨.

## §D.2 품질 게이트 / Definition of Done

- [ ] AC-GEN-001a~c, AC-GEN-002a~c 전 시나리오 통과.
- [ ] 테스트 커버리지 85% 이상 (`quality.yaml` `constitution.test_coverage_target`).
- [ ] `ruff` 린트 무경고, `black` 포맷 준수.
- [ ] `pytest` 전체 그린.
- [ ] spec.md의 REQ-GEN-001~007이 각각 최소 1개 테스트로 검증됨(추적성).
