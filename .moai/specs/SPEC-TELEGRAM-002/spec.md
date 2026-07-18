---
id: SPEC-TELEGRAM-002
title: "텔레그램 첨부파일 저장 경로 순회(Path Traversal) 취약점 수정"
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

# SPEC-TELEGRAM-002 — 텔레그램 첨부파일 저장 경로 순회(Path Traversal) 취약점 수정

## HISTORY

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 0.1.0 | 2026-07-18 | manager-spec | 최초 초안 작성. `storage.py`의 `save_attachment()`가 텔레그램 API로부터 받은 공격자 제어 가능한 `filename`을 정제 없이 저장 경로 조합에 사용하여 경로 순회/임의 파일 쓰기(CWE-22)가 가능한 취약점을 수정하는 보안 패치 SPEC. `save_attachment()`의 공개 시그니처는 변경하지 않는다. Tier M(3-파일, 보안 수정의 감사 가능성을 위해 `acceptance.md`를 별도 유지 — 상세 근거는 본 문서 §A 하단 Tier 판단 참조). 개발 방법론은 TDD(RED-GREEN-REFACTOR), Reproduction-First Bug Fix 원칙에 따라 현재 취약 코드를 대상으로 한 실패 재현 테스트를 먼저 작성한다. |

---

## §A. 개요 (Context)

### 배경 및 확인된 취약점

`SPEC-TELEGRAM-001`(`status: completed`)로 구현된 텔레그램 → 마크다운 저장 봇의 `src/markdown_creat/telegram_bot/storage.py` 모듈에서, 첨부파일(사진·문서) 원본을 저장하는 `save_attachment()` 함수(현재 90~104행)가 다음과 같은 경로 순회 취약점을 가지고 있음이 확인되었다:

```python
def save_attachment(
    base_dir: str | os.PathLike[str],
    timestamp: datetime,
    message_id: int,
    filename: str,
    content: bytes,
) -> Path:
    attachments_dir = Path(base_dir) / _ATTACHMENTS_DIRNAME
    attachments_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{timestamp.strftime('%Y-%m-%d_%H%M%S')}_{message_id}_{filename}"
    path = attachments_dir / safe_name
    path.write_bytes(content)
    return path
```

`filename`은 텔레그램 API가 전달하는 값으로, 봇에 사진/문서를 전송하는 임의의 발신자가 원하는 대로 지정할 수 있는 **공격자 제어 가능(attacker-influenceable)** 입력이다(예: `"../../../evil.txt"`, `"../../.env"`). 이 값이 정제 없이 `safe_name` 문자열 조합에 그대로 삽입된 뒤 `attachments_dir / safe_name`으로 경로가 만들어지므로, `filename`에 `..` 상위 디렉토리 이동 시퀀스나 절대 경로 형태 문자열이 포함되면 `pathlib.Path`의 `/` 연산자가 이를 그대로 경로 구분자로 해석하여 의도된 `<base_dir>/files/` 디렉토리를 벗어난 임의 위치에 파일을 쓸 수 있다 — 고전적인 경로 순회(path traversal) / 임의 파일 쓰기 취약점(OWASP path traversal, CWE-22에 해당)이다.

### 수정 범위 (사용자와 확인 완료)

본 SPEC은 **`save_attachment()`의 경로 순회 노출만** 수정한다. 수정 방식은 `filename`을 저장 경로 조합에 사용하기 전에 안전한 basename(디렉토리 구성요소가 제거된 최종 경로 세그먼트)으로 정제/유도하고, 순회 시퀀스를 거부·무력화하는 것이다. 합법적인 파일명에 대해서는 기존 `<timestamp>_<message_id>_<original-name>` 명명 규칙을 그대로 유지한다(회귀 없음). `save_attachment()`의 공개 함수 시그니처(여전히 `filename: str`을 받음)는 변경하지 않으며, `handlers.py`/`dispatch.py`의 호출부도 변경하지 않는다 — 그렙으로 호출부를 확인한 결과 `handlers.py:68`, `handlers.py:101`에서 `save_attachment(base_dir, timestamp, message_id, filename, content)` 형태로 호출되며, 시그니처가 유지되는 한 이 두 호출부는 수정이 필요하지 않다.

### Tier 판단 및 근거

본 SPEC은 단일 파일(`storage.py`)·단일 함수(`save_attachment`)를 대상으로 하는 낮은 LOC의 보안 수정이며, `.claude/rules/moai/workflow/spec-workflow.md` § SPEC Complexity Tier 가이드(< 300 LOC, < 5 files)만 보면 Tier S(spec.md + plan.md, AC를 spec.md §3에 인라인)가 기본값으로 타당하다. 그럼에도 본 SPEC은 **Tier M**(spec.md + plan.md + acceptance.md 3-파일)으로 분류한다. 근거:

1. 보안 취약점 수정은 감사 가능성(auditability)이 중요하다 — 공격 벡터별(상위 디렉토리 이동, 절대 경로, 정제 후 빈 문자열 등) 인수 기준을 spec.md 본문에 섞기보다 `acceptance.md`에 별도 GEARS 시나리오로 명시적으로 열거하는 편이, 향후 이 수정을 검토하는 사람이 "어떤 공격 벡터가 어떤 테스트로 봉쇄되었는지"를 spec.md를 헤집지 않고 바로 확인할 수 있게 한다.
2. 프로젝트 선례(`SPEC-TELEGRAM-001`)가 동일 모듈에 대해 이미 Tier M + 전용 `acceptance.md` 구조를 사용하고 있어, 동일 모듈의 후속 보안 수정 SPEC도 같은 구조를 유지하는 것이 일관적이다.
3. LOC/파일 수 자체는 Tier S 범위이지만, "보안 수정"이라는 리스크 카테고리는 순수 LOC 가이드가 포착하지 못하는 감사 요구를 추가한다고 판단한다.

### 재현·검증 방법론

`quality.yaml`의 `constitution.development_mode: tdd`(RED-GREEN-REFACTOR)를 따른다. Reproduction-First Bug Fix 원칙에 따라, 수정 전 **현재 취약한 코드**를 대상으로 익스플로잇을 재현하는 실패 테스트(예: `filename="../../../evil.txt"`로 `save_attachment()`를 호출했을 때 `<base_dir>/files/` 바깥에 파일이 생성됨을 검증)를 먼저 작성하고, 해당 테스트가 실제로 실패함을 확인한 뒤 최소 수정으로 통과시킨다.

### REQ ID 번호 규칙에 대한 참고

`SPEC-TELEGRAM-001`이 이미 `REQ-TELEGRAM-001`~`018`을 사용했으므로, 동일 도메인(`TELEGRAM`) 접두어를 공유하는 본 SPEC의 신규 요구사항은 ID 충돌·모호성을 피하기 위해 `REQ-TELEGRAM-019`부터 이어서 번호를 부여한다.

---

## §B. 요구사항 (EARS Requirements)

### 첨부파일 저장 경로 정제 (경로 순회 방지)

- **REQ-TELEGRAM-019 (Ubiquitous)**: The bot shall 첨부파일 저장 시 텔레그램 API가 제공한 `filename`에서 디렉토리 구성요소를 모두 제거한 최종 경로 세그먼트(순수 basename)만을 안전한 저장 파일명 조합에 사용한다.
- **REQ-TELEGRAM-020 (Unwanted)**: The bot shall not 첨부파일 저장 시 `filename`에 포함된 상위 디렉토리 이동 시퀀스(`..`)나 경로 구분자(`/`, `\`)를 그대로 최종 저장 경로 조합에 반영한다.
- **REQ-TELEGRAM-021 (Ubiquitous)**: The bot shall `save_attachment()`로 저장하는 모든 첨부파일의 최종 파일 경로가 `<base_dir>/files/` 디렉토리 하위를 항상 벗어나지 않도록 보장한다.
- **REQ-TELEGRAM-022 (Where)**: Where 정제된 basename이 경로 구성요소를 포함하지 않는 합법적인 파일명인 경우, the bot shall 기존 `<timestamp>_<message_id>_<original-name>` 명명 규칙을 그대로 유지한다(회귀 없음).
- **REQ-TELEGRAM-023 (Event-driven)**: When 정제 후 basename이 비어 있거나 디렉토리 참조만 남는 문자열(예: `.`, `..`)이 되면, the bot shall 고정된 폴백 파일명을 사용하여 첨부파일 저장이 실패하거나 조용히 무시되지 않도록 한다.

---

## §C. 제약 및 품질 게이트 (Constraints)

- Python 3.10+, `src/` 레이아웃. 기존 `SPEC-TELEGRAM-001` 기술 기반(`python-telegram-bot`, `pytesseract`)은 변경하지 않는다.
- `save_attachment()`의 공개 함수 시그니처(파라미터 목록·타입·반환 타입)는 변경하지 않는다. `handlers.py:68`, `handlers.py:101`의 호출부는 수정하지 않는다(그렙으로 확인 완료 — 시그니처가 유지되는 한 호출부 변경은 필요 없다).
- 정제 로직은 신규 외부 의존성을 추가하지 않는다 — 표준 라이브러리 경로 유틸리티(예: `pathlib.PurePath.name` 또는 동등한 basename 추출)로 구현 가능하다. 다만 `/`와 `\` 두 구분자 모두를 방어해야 한다는 점에 유의한다 — 텔레그램 API가 제공하는 `filename` 문자열은 호스트 OS와 무관하게 임의의 문자를 담을 수 있으므로, 호스트가 POSIX든 Windows든 관계없이 두 구분자를 모두 정제 대상으로 취급해야 한다(`pathlib`의 구분자 인식은 플랫폼 종속적이므로, 문자열 레벨에서 두 구분자를 명시적으로 다루는 접근이 필요할 수 있다).
- 개발 방법론: `quality.yaml`의 `constitution.development_mode: tdd`(RED-GREEN-REFACTOR). Reproduction-First — 수정 전 현재 취약 코드를 대상으로 한 실패 재현 테스트를 먼저 작성하고 실패를 확인한다.
- 품질 게이트: `ruff`(린트) + `black`(포맷) + `pytest`(테스트), 커버리지 85% 이상 유지. `SPEC-TELEGRAM-001`의 기존 `tests/test_telegram_storage.py`, `tests/test_telegram_handlers.py`, `tests/test_telegram_dispatch.py` 스위트에 회귀가 없어야 한다.
- 합법적인 비ASCII(한글 등) 파일명은 basename 추출 후에도 그대로 보존되어야 한다 — 정제 로직이 경로 구분자 외의 문자를 손상시키지 않는다.
- 코드 식별자·함수명·기술 용어는 영어로 작성한다(언어 정책).

---

## §Exclusions / 만들지 않는 것 (What NOT to Build)

본 SPEC은 "`save_attachment()`의 경로 순회 노출 수정" 단일 관심사에 집중한다. 아래 항목은 사용자와 확인을 거쳐 명시적으로 범위 밖으로 확정되었다.

### Out of Scope — `note_path` / `note_dir` / `note_filename` 정제
- 이 세 함수가 사용하는 `message_id`는 텔레그램 API가 부여하는 `int` 값으로, 공격자가 임의 문자열을 주입할 수 있는 경로가 아니므로 경로 순회 리스크가 무시할 수준이다. 본 SPEC은 이 세 함수를 수정하지 않는다(필요 시 후속 SPEC에서 재평가).

### Out of Scope — `render_note`의 `sender` / `chat_context` / `body_text` 마크다운·텍스트 정제
- 텔레그램 발신자명·채팅 컨텍스트·본문 텍스트를 `.md` 본문에 삽입하기 전 마크다운 인젝션 등을 방지하는 콘텐츠 무결성 정제는 본 SPEC의 경로 순회 보안 스코프에 포함되지 않는다. 별도 관심사로 후속 SPEC 대상이다.

### Out of Scope — `save_note` / `save_attachment`의 덮어쓰기(overwrite) 충돌 처리
- 동일 경로에 이미 파일이 존재할 때 덮어쓸지, 거부할지, 별도 접미사를 부여할지는 데이터 무결성 관심사이며 본 SPEC 범위 밖이다. 본 SPEC이 수정하는 것은 경로 자체의 순회 가능성뿐이며, 충돌 처리 정책 자체는 변경하지 않는다.

---

## §E. 참조 (Cross-References)

- 프로젝트 문서: `.moai/project/product.md`, `.moai/project/structure.md`, `.moai/project/tech.md`
- 의존 SPEC(수정 대상 모듈 소유): `.moai/specs/SPEC-TELEGRAM-001/spec.md` (`storage.py` 최초 구현, `status: completed`)
- 취약점 대상 파일: `src/markdown_creat/telegram_bot/storage.py` (`save_attachment()`, 현재 90~104행)
- 호출부(변경 없음, 그렙 확인): `src/markdown_creat/telegram_bot/handlers.py:68`, `:101`
- 품질 설정: `.moai/config/sections/quality.yaml` (`constitution.development_mode: tdd`)
- 구현 계획: `plan.md`
- 상세 인수 기준: `acceptance.md`
