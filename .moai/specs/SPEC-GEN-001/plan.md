---
id: SPEC-GEN-001
title: "템플릿 기반 마크다운 생성 코어 기능 — 구현 계획"
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
tier: S
---

# SPEC-GEN-001 — 구현 계획 (plan.md)

## §A. 컨텍스트 (Context)

그린필드 프로젝트의 첫 SPEC. 분석할 기존 코드 없음. Jinja2 템플릿 + YAML 데이터 → `.md` 파일 렌더링 코어 함수를 TDD(RED-GREEN-REFACTOR)로 구현한다. Tier S(단일 모듈, 300 LOC 미만, CLI/다중포맷 없음).

## §B. 기술 접근 (Technical Approach)

`structure.md` 제안 구조를 따르되 본 SPEC 범위에 필요한 모듈만 다룬다:
- `renderer.py` — Jinja2 엔진 호출을 캡슐화 (템플릿 문자열 → 렌더링된 문자열)
- `loader.py` — YAML 데이터 파일 파싱 (파일 → dict), 파일 부재/YAML 오류 처리
- `generator.py` — 위 둘을 조합하여 템플릿 경로 · 데이터 경로 · 출력 경로 → `.md` 파일 생성. 코어 공개 함수.

`cli.py`, `config.py`는 본 SPEC에서 다루지 않는다.

## §C. 마일스톤 (결정 번복 가능성 순 — 변경 가능성 높은 결정 우선)

> 사람이 검토할 때 변경 가능성이 가장 높은 결정(공개 인터페이스 · 오류 계약)을 먼저 배치하고, 기계적 단계는 뒤로 미룬다.

### M1 — 공개 API 인터페이스 결정 (변경 가능성 최상)
- `generator.py`의 코어 공개 함수 시그니처 확정: 인자(template_path, data_path, output_path)의 형태(문자열/Path), 반환값(None 또는 생성된 경로), 예외 계약.
- 이는 하위 모든 호출자(향후 CLI 포함)가 의존하는 계약이므로 사람 검토가 가장 필요한 지점이다.
- RED: 성공 경로에 대한 실패 테스트 작성.

### M2 — 오류 처리 계약 결정 (변경 가능성 상)
- 파일 부재(REQ-GEN-005), YAML 문법 오류(REQ-GEN-006)에 대해 발생시킬 예외 타입/메시지 형태 확정.
- 부분 출력 방지(REQ-GEN-007) 전략(렌더링 완료 후에만 파일 기록) 확정.
- RED: 각 오류 케이스에 대한 실패 테스트 작성.

### M3 — 렌더링 컨텍스트 매핑 (변경 가능성 중)
- YAML 중첩 구조(dict/list) → Jinja2 컨텍스트 전달 방식 확정(REQ-GEN-002).

### M4 — 구현 (GREEN, 기계적)
- `loader.py`, `renderer.py`, `generator.py` 최소 구현으로 테스트 통과.

### M5 — 리팩터 및 품질 게이트 (REFACTOR, 기계적)
- `ruff` + `black` 정리, 커버리지 85% 확인, 중복 제거.

## §D. 리스크 (Risks)

- Jinja2 `StrictUndefined` 사용 여부: 정의되지 않은 변수를 오류로 볼지 빈 문자열로 볼지 결정 필요 → M1/M2에서 계약으로 확정 권장.
- 출력 경로 부모 디렉터리 부재 시 동작(생성할지 오류낼지) → M2에서 결정.
- 인코딩(UTF-8 고정) — 한글 문서 대응 위해 명시적 UTF-8 권장.

## §E. 참조

- `spec.md` (요구사항 SSOT), `acceptance.md` (인수 시나리오)
