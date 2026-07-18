---
id: SPEC-TELEGRAM-002
title: "텔레그램 첨부파일 저장 경로 순회 취약점 수정 — 구현 계획"
version: "0.1.0"
status: in-progress
created: 2026-07-18
updated: 2026-07-18
author: manager-spec
priority: P0
phase: "v0.1.0 target"
module: "src/markdown_creat/telegram_bot"
lifecycle: spec-anchored
tags: "telegram, bot, security, path-traversal, storage"
depends_on: [SPEC-TELEGRAM-001]
tier: M
---

# SPEC-TELEGRAM-002 — 구현 계획 (plan.md)

## §A. 컨텍스트 (Context)

`SPEC-TELEGRAM-001`(`status: completed`)로 구현된 `src/markdown_creat/telegram_bot/storage.py`의 `save_attachment()`에서 발견된 경로 순회(Path Traversal, CWE-22) 취약점을 수정하는 단일 파일 보안 패치. 분석할 신규 기능 없음 — 기존 함수의 내부 정제 로직만 추가한다. TDD(RED-GREEN-REFACTOR)로 구현하며, Reproduction-First Bug Fix 원칙에 따라 수정 전 현재 취약 코드를 대상으로 한 실패 재현 테스트를 먼저 작성한다. Tier M(보안 수정 감사 가능성을 위해 `acceptance.md` 별도 유지 — 근거는 spec.md §A 참조).

**의존성 확인**: `depends_on: [SPEC-TELEGRAM-001]`. `SPEC-TELEGRAM-001`은 `status: completed`이며, `save_attachment()`가 `src/markdown_creat/telegram_bot/storage.py:90`에 실제로 구현되어 있음을 확인했다(2026-07-18). `/moai run` 시 Depends_on Pre-flight Check는 통과할 것으로 예상된다.

## §B. PRESERVE / EXTEND

- **PRESERVE**: `note_dir()`, `note_filename()`, `note_path()`, `render_note()`, `save_note()` — 본 SPEC은 이 함수들을 수정하지 않는다(§Exclusions 참조). `handlers.py:68`, `handlers.py:101`의 `save_attachment()` 호출부 — 시그니처가 유지되므로 수정 불필요(그렙 확인 완료). `save_attachment()`의 공개 시그니처(`base_dir, timestamp, message_id, filename, content) -> Path`) 자체.
- **EXTEND**: `save_attachment()` 함수 본문 내부에만 `filename` 정제 로직을 추가한다. 신규 헬퍼 함수(예: basename 정제 함수)를 `storage.py` 내부에 추가하는 것은 허용되나, 모듈 외부에 노출되는 공개 계약을 늘리지 않는 범위로 최소화한다.

## §C. 기술 접근 (Technical Approach)

- `filename`을 저장 경로 조합에 사용하기 전에, 디렉토리 구성요소를 제거한 순수 basename만 추출한다. `/`와 `\` 두 구분자 모두를 명시적으로 다뤄야 한다 — 텔레그램이 제공하는 `filename` 문자열은 호스트 OS와 무관한 임의 문자열이므로, `pathlib`의 플랫폼 종속적 구분자 인식에만 의존하면 한쪽 구분자를 놓칠 수 있다.
- 정제 후 결과가 비어 있거나(`""`) 디렉토리 참조만 남는 경우(`"."`, `".."`)에는 고정 폴백 파일명을 사용한다(REQ-TELEGRAM-023).
- 합법적인 파일명(경로 구성요소 없음)에 대해서는 기존 `<timestamp>_<message_id>_<original-name>` 명명 규칙을 정확히 그대로 유지한다 — 이 부분의 회귀 여부는 `SPEC-TELEGRAM-001`의 기존 `test_telegram_storage.py` 스위트가 그대로 통과하는지로 검증한다.
- 신규 외부 의존성은 추가하지 않는다. 표준 라이브러리 경로 유틸리티로 충분하다.

## §D. 마일스톤 (결정 번복 가능성 순 — 변경 가능성 높은 결정 우선)

> 정제 전략·폴백 파일명 같은 변경 가능성이 높은 결정을 먼저 배치하고, 리팩터/품질 게이트 같은 기계적 단계는 뒤로 미룬다.

### M1 — 정제 전략 및 폴백 파일명 결정 + 재현 테스트 작성 (변경 가능성 최상, RED)
- 정제 전략 확정: basename 추출 방식(양쪽 구분자 처리), `..`/`.`-only 케이스의 폴백 파일명 리터럴, 절대 경로·드라이브 문자(`C:\...`) 케이스의 처리 방식을 확정한다.
- Reproduction-First: **현재 취약한** `save_attachment()`를 대상으로 익스플로잇 재현 실패 테스트를 작성한다(예: `filename="../../../evil.txt"` 호출 시 `<base_dir>/files/` 바깥에 파일이 생성됨을 검증) — 수정 전에 이 테스트가 실제로 실패함을 먼저 확인한다.
- RED: `acceptance.md`의 AC-TELEGRAM-019a~d에 대응하는 실패 테스트를 추가로 작성한다(상위 디렉토리 이동, 절대 경로, 정상 파일명 회귀 없음, 빈 basename 폴백).

### M2 — `save_attachment()` 수정 구현 (GREEN, 기계적)
- M1에서 확정한 정제 전략을 `save_attachment()` 내부에 최소 구현한다. 공개 시그니처는 변경하지 않는다.
- M1의 신규 RED 테스트가 모두 GREEN으로 전환되는지 확인한다.
- 기존 `tests/test_telegram_storage.py`, `tests/test_telegram_handlers.py`, `tests/test_telegram_dispatch.py` 전체 스위트가 회귀 없이 통과하는지 확인한다.

### M3 — 리팩터 및 품질 게이트 (REFACTOR, 기계적)
- `ruff` + `black` 정리, `storage.py` 커버리지 85% 이상 확인, 중복 제거.
- `handlers.py`/`dispatch.py`가 수정되지 않았음을 `git diff --stat`로 확인(스코프가 `storage.py` + 대응 테스트 파일로만 한정되었는지 검증).

## §E. 리스크 (Risks)

- **[과잉 정제] 합법적 유니코드 파일명 손상**: basename 추출 로직이 경로 구분자 외의 문자(한글 등 비ASCII 포함)까지 건드리면 정상 파일명이 손상될 수 있다. 경로 구분자만 대상으로 하는 최소 정제로 완화한다 — 기존 `test_telegram_storage.py`의 한글 관련 테스트(`save_note` UTF-8 테스트)가 이 회귀를 간접적으로 감시한다.
- **[크로스플랫폼] 구분자 처리 편향**: `pathlib`가 호스트 OS에 따라 `\`를 구분자로 인식하지 않을 수 있어(POSIX 호스트에서), 문자열 레벨에서 `/`와 `\` 양쪽을 명시적으로 다루지 않으면 한쪽 벡터가 누락될 수 있다. M1에서 양쪽 구분자 처리를 명시적으로 결정하고 테스트로 고정한다.
- **[폴백 충돌] 다중 첨부파일의 폴백 파일명 충돌**: 여러 첨부파일이 모두 폴백 파일명으로 귀결되는 극단적 케이스에서도, 기존 `<timestamp>_<message_id>_...` 접두어(메시지별로 다른 `message_id`)가 충돌을 방지한다(`SPEC-TELEGRAM-001` M1의 충돌 회피 전략과 동일 메커니즘) — 신규 리스크 아님.
- **[스코프 누락] 후속 유사 취약점**: `note_path`/`note_dir`/`note_filename`(§Exclusions에서 리스크 낮음으로 판단) 및 `render_note`의 콘텐츠 정제는 본 SPEC에서 다루지 않는다 — 필요 시 후속 SPEC 대상으로 남긴다.

## §F. 참조

- `spec.md` (요구사항 SSOT), `acceptance.md` (인수 시나리오)
- 의존 SPEC: `.moai/specs/SPEC-TELEGRAM-001/spec.md` (`storage.py` 최초 구현)
- 대상 파일: `src/markdown_creat/telegram_bot/storage.py`, `tests/test_telegram_storage.py`
