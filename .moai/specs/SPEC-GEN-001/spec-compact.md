---
id: SPEC-GEN-001
title: "템플릿 기반 마크다운 생성 코어 기능 (compact)"
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

# SPEC-GEN-001 (compact)

**목표**: Jinja2 템플릿 파일 + YAML 데이터 파일 → 변수 치환 렌더링 → 지정 경로 `.md` 파일 생성. CLI 없는 코어 라이브러리 함수. Tier S.

**요구사항 (EARS)**:
- REQ-GEN-001/002: Jinja2 템플릿을 YAML 값으로 렌더링, `{{ var }}` 및 중첩 dict/list 치환.
- REQ-GEN-003/004: 유효 입력 시 출력 경로에 `.md` 기록, 기존 파일 덮어쓰기.
- REQ-GEN-005: 템플릿/데이터 파일 부재 → 명확한 오류(불투명 스택 트레이스 금지).
- REQ-GEN-006: 잘못된 YAML → 사용자 이해 가능한 파싱 오류(조용한 실패 금지).
- REQ-GEN-007: 오류 시 부분 렌더링 `.md` 잔존 금지.

**인수 기준**:
- AC-GEN-001: 정상 입력 → 치환된 `.md` 생성.
- AC-GEN-002: 잘못된 입력 → 명확한 오류.
- AC-GEN-003: 커버리지 85% (`quality.yaml` 전역 기본값).

**범위 밖**: CLI, JSON/TOML 지원, 배치/다중 파일, 기본 제공 템플릿·패키징 번들.

**스택**: Python 3.10+, Jinja2, PyYAML, TDD, ruff/black/pytest.
