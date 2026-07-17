---
id: SPEC-GEN-001
title: "템플릿 기반 마크다운 생성 코어 기능"
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

# SPEC-GEN-001 — 템플릿 기반 마크다운 생성 코어 기능

## HISTORY

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 0.1.0 | 2026-07-14 | manager-spec | 최초 초안 작성. 프로젝트 첫 SPEC. Jinja2 템플릿 + YAML 데이터 → `.md` 파일 렌더링 코어 기능 정의. |

---

## §A. 개요 (Context)

`markdown_creat`는 데이터를 템플릿에 바인딩하여 표준화된 마크다운 문서를 자동 생성하는 Python 도구이다. 본 SPEC은 그 **코어 라이브러리 기능**만을 정의한다.

- **입력**: Jinja2 템플릿 파일(예: `report.md.j2`) 1개 + YAML 데이터 파일(예: `sample_data.yaml`) 1개
- **동작**: 템플릿의 `{{ variable }}` 플레이스홀더에 YAML 데이터 값을 치환하여 렌더링
- **출력**: 렌더링된 결과를 호출자가 지정한 경로의 `.md` 파일로 저장

본 기능은 CLI 진입점이 아니라, 템플릿 경로 · 데이터 경로 · 출력 경로를 인자로 받아 `.md` 파일을 생성하는 **Python 함수/모듈** 수준의 기능이다. CLI, JSON 지원, 배치 생성은 본 SPEC의 범위가 아니다(§Exclusions 참조).

기술 기반: Python 3.10+, 템플릿 엔진 Jinja2, 데이터 파서 PyYAML (`.moai/project/tech.md` 준수).

---

## §B. 요구사항 (EARS Requirements)

### 렌더링 및 값 치환

- **REQ-GEN-001 (Ubiquitous)**: The system shall Jinja2 템플릿 파일을 YAML 데이터 파일의 값으로 렌더링하여, 템플릿 내 `{{ variable }}` 플레이스홀더를 대응하는 데이터 값으로 치환한다.
- **REQ-GEN-002 (Ubiquitous)**: The system shall YAML 데이터의 중첩 구조(딕셔너리 · 리스트)를 Jinja2 표현식(`{{ obj.key }}`, `{% for %}`)에서 접근 가능하도록 그대로 렌더링 컨텍스트로 전달한다.

### 출력 파일 생성

- **REQ-GEN-003 (Event-driven)**: When 생성 함수가 유효한 템플릿 경로 · 데이터 경로 · 출력 경로와 함께 호출되면, the system shall 렌더링된 마크다운 문자열을 지정된 출력 경로에 `.md` 파일로 기록한다.
- **REQ-GEN-004 (Event-driven)**: When 출력 파일이 이미 존재하는 경로로 생성 함수가 호출되면, the system shall 기존 파일을 렌더링 결과로 덮어쓴다.

### 오류 처리 (Unwanted Behavior)

- **REQ-GEN-005 (Event-driven / unwanted)**: When 템플릿 파일 또는 데이터 파일이 지정된 경로에 존재하지 않으면, the system shall 어떤 파일이 없는지 식별 가능한 명확한 오류를 발생시키며, 불투명한 스택 트레이스로 종료되지 않는다.
- **REQ-GEN-006 (Event-driven / unwanted)**: When YAML 데이터 파일이 잘못된 문법을 포함하면, the system shall YAML 파싱 실패를 사용자가 이해할 수 있는 형태로 알리는 명확한 오류를 발생시키며, 조용히 실패하지 않는다.
- **REQ-GEN-007 (Ubiquitous / unwanted)**: The system shall 오류 발생 시 불완전하거나 부분적으로 렌더링된 `.md` 파일을 출력 경로에 남기지 않는다.

---

## §C. 인수 기준 (Acceptance Criteria — Tier S 인라인)

> Tier S 규칙에 따라 인수 기준을 spec.md 본문에 인라인으로 포함한다. 상세 Given-When-Then 시나리오는 `acceptance.md`에 확장 기술한다.

- **AC-GEN-001**: 유효한 Jinja2 템플릿 + 유효한 YAML 데이터를 입력하면, 템플릿 변수가 올바르게 치환되고 지정된 출력 경로에 기대한 렌더링 내용을 담은 `.md` 파일이 생성된다. (REQ-GEN-001~004)
- **AC-GEN-002**: 잘못된 입력(템플릿 파일 없음 / 데이터 파일 없음 / 잘못된 YAML 문법)에 대해, 조용한 실패나 불투명한 스택 트레이스 대신 사용자가 이해할 수 있는 명확한 오류가 반환/발생한다. (REQ-GEN-005~007)
- **AC-GEN-003**: 테스트 커버리지는 프로젝트 `quality.yaml`의 `constitution.test_coverage_target` 값(85%)을 충족한다. 이는 프로젝트 전역 기본값이며 본 SPEC에서 새로 도출한 수치가 아니다.

---

## §D. 제약 및 품질 게이트 (Constraints)

- Python 3.10+, Jinja2, PyYAML만 사용한다(최소 의존성 원칙, `tech.md` 준수).
- 개발 방법론: `quality.yaml`의 `development_mode: tdd` (RED-GREEN-REFACTOR).
- 품질 게이트: `ruff`(린트) + `black`(포맷) + `pytest`(테스트), 커버리지 85% 이상.
- 코드 식별자 · 함수명 · 기술 용어는 영어로 작성한다(언어 정책).

---

## §Exclusions / 만들지 않는 것 (What NOT to Build)

본 SPEC은 코어 라이브러리 기능에만 집중한다. 아래 항목은 명시적으로 범위 밖이며 향후 별도 SPEC으로 분리한다.

### Out of Scope — CLI 인터페이스
- 커맨드라인 진입점(`cli.py`), 인자 파싱(argparse/typer/click), `python -m markdown_creat` 실행 방식은 본 SPEC에서 구현하지 않는다.

### Out of Scope — 데이터 포맷 확장
- JSON 데이터 포맷 지원은 범위 밖이다. 본 SPEC은 YAML 입력만 다룬다.
- TOML 입력 및 `tomllib` 의존(Python 3.11+ 관련)은 다루지 않는다.

### Out of Scope — 배치/다중 파일 생성
- 여러 템플릿 · 여러 데이터 파일을 일괄 처리하는 배치 생성 기능은 범위 밖이다. 본 SPEC은 단일 템플릿 + 단일 데이터 → 단일 출력만 다룬다.

### Out of Scope — 기본 제공 템플릿 및 패키징
- 보고서 · 회의록 등 기본 제공 템플릿 자산은 범위 밖이다.
- `templates/` 디렉터리가 설치 가능한 `src/markdown_creat/` 패키지 외부에 위치하여 pip 휠에 번들되지 않을 수 있다는 패키징 부채(PROJECT-review-1.md에서 지적됨)는 본 SPEC에서 해결하지 않는다. 본 SPEC은 호출자가 임의 경로의 템플릿 파일을 지정하는 방식이므로 번들 템플릿에 의존하지 않으며, 이 부채는 명시적으로 향후 SPEC으로 유보한다.

---

## §E. 참조 (Cross-References)

- 프로젝트 문서: `.moai/project/product.md`, `.moai/project/structure.md`, `.moai/project/tech.md`
- 감사 보고서: `.moai/reports/plan-audit/PROJECT-review-1.md`
- 품질 설정: `.moai/config/sections/quality.yaml`
- 구현 계획: `plan.md`
- 상세 인수 기준: `acceptance.md`
