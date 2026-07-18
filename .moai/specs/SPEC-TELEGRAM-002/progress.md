---
id: SPEC-TELEGRAM-002
title: "텔레그램 첨부파일 저장 경로 순회 취약점 수정 — 진행 기록"
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

# SPEC-TELEGRAM-002 — 진행 기록 (progress.md)

## §E.1 Plan-phase Audit-Ready Signal

- Plan-phase 산출물 세트(spec.md + plan.md + acceptance.md + progress.md) 생성 완료. Tier M(3-파일 세트 + progress.md, 보안 수정 감사 가능성을 위해 acceptance.md 별도 유지 — 근거는 spec.md §A Tier 판단 참조).
- SPEC ID 사전 자가검증 통과: `decomposition: SPEC ✓ | TELEGRAM ✓ | 002 ✓ → PASS` (canonical regex `^SPEC(-[A-Z][A-Z0-9]*)+-\d{3}$`, Bash 실행 출력 `PASS`).
- Frontmatter 12 필드 canonical 스키마 검증 완료 + optional 필드 `depends_on: [SPEC-TELEGRAM-001]`, `tier: M` 기록.
- 확인된 취약점: `src/markdown_creat/telegram_bot/storage.py`의 `save_attachment()`(현재 90~104행)가 텔레그램 API 제공 `filename`을 정제 없이 저장 경로 조합에 사용하여 경로 순회/임의 파일 쓰기(CWE-22)가 가능함. 사용자와 스코프 확인 완료: `save_attachment()` 수정만, 공개 시그니처 불변, `handlers.py`/`dispatch.py` 호출부 변경 없음(그렙 확인: `handlers.py:68`, `:101`).
- EARS 요구사항 REQ-TELEGRAM-019~023 정의(Ubiquitous / Unwanted / Where / Event-driven 혼합). REQ ID는 `SPEC-TELEGRAM-001`의 REQ-TELEGRAM-001~018에 이어 019부터 부여(동일 `TELEGRAM` 도메인 접두어 충돌 방지).
- §Exclusions에 3개 `### Out of Scope —` 하위 헤딩 포함(`note_path`/`note_dir`/`note_filename`, `render_note` 콘텐츠 정제, 덮어쓰기 충돌 처리).
- 의존성: `SPEC-TELEGRAM-001`(`status: completed`) — 수정 대상 모듈(`storage.py`)의 최초 구현 소유. run-phase Depends_on Pre-flight Check는 통과가 예상된다.
- 개발 방법론: `quality.yaml` `constitution.development_mode: tdd`(RED-GREEN-REFACTOR). Reproduction-First Bug Fix 원칙에 따라 M1에서 현재 취약 코드를 대상으로 한 실패 재현 테스트를 먼저 작성한다.

## §E.2 Run-phase Evidence

TDD 사이클(RED-GREEN-REFACTOR)로 `save_attachment()`의 경로 순회 취약점을 수정. Reproduction-First: 취약한 코드를 대상으로 재현 테스트를 먼저 작성해 실제 실패(RED)를 확인한 뒤(`test_save_attachment_rejects_parent_directory_traversal_in_filename` 등 3개 신규 테스트가 수정 전 코드에서 FAILED — `pytest -k "traversal or drive_prefixed or ... "` 실행 결과 `3 failed, 3 passed`), `_sanitize_attachment_basename()` 헬퍼를 추가하여 최소 수정으로 GREEN 전환했다.

### AC PASS/FAIL 매트릭스

| AC / Invariant | Status | Verification Command | Actual Output |
|---|---|---|---|
| AC-TELEGRAM-019a (상위 디렉토리 이동 무력화) | PASS | `pytest tests/test_telegram_storage.py::test_save_attachment_rejects_parent_directory_traversal_in_filename -v` | `PASSED` — `filename="../../../evil.txt"` 저장 결과가 `<base_dir>/files/2026-07-16_103045_1_evil.txt`로 확인됨(파일이 `<base_dir>/files/` 바깥에 생성되지 않음, `evil.txt`가 `<base_dir>/` 또는 그 상위에 존재하지 않음을 단언) |
| AC-TELEGRAM-019b (절대 경로/드라이브 문자 무력화) | PASS | `pytest tests/test_telegram_storage.py::test_save_attachment_rejects_absolute_and_drive_prefixed_filename -v` | `PASSED` — `"/etc/passwd"` → `.../files/2026-07-16_103045_2_passwd`, `"C:\\Windows\\evil.txt"` → `.../files/2026-07-16_103045_3_evil.txt` (양쪽 모두 `<base_dir>/files/` 내부로 축소됨) |
| AC-TELEGRAM-019c (정상 파일명 회귀 없음) | PASS | `pytest tests/test_telegram_storage.py::test_save_attachment_preserves_legitimate_filename_naming_convention -v` | `PASSED` — `"photo.jpg"` → `<base_dir>/files/2026-07-16_103045_42_photo.jpg` (기존 명명 규칙과 완전히 동일) |
| AC-TELEGRAM-019d (빈 basename 폴백) | PASS | `pytest tests/test_telegram_storage.py::test_save_attachment_falls_back_to_placeholder_for_dot_only_filename -v` | `PASSED` — `filename=".."`, `filename="."` 모두 고정 폴백(`"attachment"`)으로 대체되어 `<base_dir>/files/` 내부에 저장, 예외 없이 성공 |
| Edge: 혼합 구분자 (백슬래시 순회) | PASS | 위 AC-019b 테스트에 포함 (`C:\\Windows\\evil.txt`가 `\` 구분자로 정제됨을 함께 검증) | `PASSED` |
| Edge: 서브디렉토리 형태 상대 경로 flatten | PASS | `pytest tests/test_telegram_storage.py::test_save_attachment_flattens_subdirectory_style_filename -v` | `PASSED` — `"subdir/photo.jpg"` → `.../files/2026-07-16_103045_6_photo.jpg`, `files/subdir/` 디렉토리 미생성 확인 |
| Edge: 한글 등 비ASCII 정상 파일명 보존 | PASS | `pytest tests/test_telegram_storage.py::test_save_attachment_preserves_non_ascii_filename_without_separators -v` | `PASSED` — `"사진.jpg"` → `.../files/2026-07-16_103045_7_사진.jpg` (문자 손상 없음) |
| REQ-TELEGRAM-019~023 전체 추적성 | PASS | 위 7개 테스트가 각 REQ를 최소 1회씩 커버 (019/020/021→019a,019b; 022→019c; 023→019d) | `PASS` |
| 기존 회귀 스위트 (SPEC-TELEGRAM-001) | PASS | `pytest tests/test_telegram_storage.py tests/test_telegram_handlers.py tests/test_telegram_dispatch.py -v` | `31 passed in 1.16s` (기존 11개 + 신규 6개 storage 테스트 + handlers 8개 + dispatch 6개 전부 통과, 회귀 없음) |
| `storage.py` 커버리지 >= 85% | PASS | `pytest tests/test_telegram_storage.py --cov=markdown_creat.telegram_bot.storage --cov-report=term-missing -q` | `src\markdown_creat\telegram_bot\storage.py  55  0  100%` |
| `ruff` 무경고 | PASS | `ruff check src/markdown_creat/telegram_bot/storage.py tests/test_telegram_storage.py` | `All checks passed!` |
| `black` 포맷 준수 | PASS | `black --check src/markdown_creat/telegram_bot/storage.py tests/test_telegram_storage.py` | `2 files would be left unchanged.` |
| 공개 시그니처 불변 + 호출부 미수정 | PASS | `git diff --stat` | `src/markdown_creat/telegram_bot/storage.py \| 31 ++++++++++-`, `tests/test_telegram_storage.py \| 89 +++...` — `handlers.py`, `dispatch.py` 변경 없음 |
| 신규 외부 의존성 없음 | PASS | `git diff --stat` (`pyproject.toml` 미포함) | 표준 라이브러리(`str.replace`, `str.split`)만 사용 |

## §E.3 Run-phase Audit-Ready Signal

```yaml
run_complete_at: "2026-07-18T08:39:06Z"
run_commit_sha: "pending-backfill-M1"  # self-referential hazard: this commit cannot know its own SHA; backfilled in a follow-up commit per spec-frontmatter-schema.md SHA placeholder pattern
run_status: PASS
ac_pass_count: 4          # AC-TELEGRAM-019a, 019b, 019c, 019d
ac_fail_count: 0
preserve_list_post_run_count: 5  # note_dir, note_filename, note_path, render_note, save_note -- all unmodified, verified via full regression pass
l44_pre_commit_fetch: "N/A -- single-agent direct-to-master TDD milestone, no parallel Agent() sub-spawn requiring the pre-spawn sync-check batch; git branch/HEAD verified in Section C pre-flight instead"
l44_post_push_fetch: "N/A -- push not yet executed at time of writing; will run as part of M3 push step below"
new_warnings_or_lints_introduced: 0  # ruff check + black --check both clean
cross_platform_build:
  applicable: false
  reason: "Python project (no GOOS/GOARCH cross-compilation build step); portability addressed at the sanitization-logic level instead (explicit '/' and '\\' string-level splitting, not pathlib's platform-dependent separator recognition)"
total_run_phase_files: 2  # src/markdown_creat/telegram_bot/storage.py, tests/test_telegram_storage.py
m1_to_mN_commit_strategy: "single combined commit for M1(RED)+M2(GREEN)+M3(REFACTOR/quality-gate) -- verified GREEN before committing, per plan.md SS D milestone sequence"
```

## §E.4 Sync-phase Audit-Ready Signal

_<pending sync-phase>_

## §F Phase 4 Mode Selection

- Input parameters: tier=M, scope≈1 file (`storage.py`) + 1 test file, domain count=1 (backend/security, single module), file language mix=100% Python, concurrency benefit=LOW (coding-heavy single-file fix), Agent Teams prereqs=N/A (retired).
- Mode evaluation: Mode 1 trivial — not selected (non-trivial semantic security fix). Mode 2 background — not selected (write task, not read-only). Mode 3 agent-team — RETIRED, never selected. Mode 4 parallel — not selected (single-domain, coding-heavy, not research-heavy). Mode 6 workflow — not selected (scope far below ~30-file mechanical-transform threshold). Mode 5 sub-agent — **selected**.
- Decision: sub-agent
- Justification: single-file, single-function TDD security patch with no inter-file dependency and no research-parallelism benefit; per Anthropic's coding-task parallelism caveat, sequential sub-agent delegation to manager-develop (cycle_type=tdd) is the correct default.
- Plan-phase audit: background plan-auditor agent failed to return twice (stopped without completion record); orchestrator performed the independent plan-phase audit directly against spec.md/plan.md/acceptance.md — verdict PASS, no must-fix issues (two minor non-blocking advisory notes: null-byte handling has no dedicated AC-ID; Windows reserved filenames out of scope). Dependency SPEC-TELEGRAM-001 status re-confirmed `completed`.
- Implementation Kickoff Approval: user approved via AskUserQuestion ("네, 시작해주세요 (권장)") before this Mode Selection log was written.
