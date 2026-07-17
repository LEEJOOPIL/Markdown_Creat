---
id: SPEC-TELEGRAM-001
title: "텔레그램 → 마크다운 저장 봇 — 진행 기록"
version: "0.3.0"
status: completed
created: 2026-07-15
updated: 2026-07-18
author: manager-spec
priority: P1
phase: "v0.1.0 target"
module: "src/markdown_creat/telegram_bot"
lifecycle: spec-anchored
tags: "telegram, bot, markdown, ocr, polling"
depends_on: [SPEC-PDF-001]
tier: M
---

# SPEC-TELEGRAM-001 — 진행 기록 (progress.md)

## §E.1 Plan-phase Audit-Ready Signal

- Plan-phase 산출물 세트(spec.md + plan.md + acceptance.md + progress.md) 생성 완료. Tier M(3-파일 세트 + progress.md).
- SPEC ID 사전 자가검증 통과: `decomposition: SPEC ✓ | TELEGRAM ✓ | 001 ✓ → PASS` (canonical regex `^SPEC(-[A-Z][A-Z0-9]*)+-\d{3}$`, Bash 실행 출력 `PASS`).
- Frontmatter 12 필드 canonical 스키마 검증 완료 + optional 필드 `depends_on: [SPEC-PDF-001]`, `tier: M` 기록.
- EARS 요구사항 REQ-TELEGRAM-001~018 정의(Ubiquitous / Event-driven / Unwanted / Where 혼합, 4차 반복에서 013~018 추가). §Exclusions에 6개 `### Out of Scope —` 하위 헤딩 포함.
- 의존성: SPEC-PDF-001(`status: completed`) — PDF 텍스트 추출 재사용 대상, `pdf_to_markdown(pdf_path, output_path)`가 `src/markdown_creat/pdf_to_markdown.py:62`에서 사용 가능함을 확인(2026-07-16). run-phase Depends_on Pre-flight Check는 통과가 예상된다.
- plan-audit 4차 반복(2026-07-16) 수정 반영: acceptance.md 8개 AC를 GEARS 패턴으로 재작성 + AC-TELEGRAM-005b(REQ-TELEGRAM-002 커버리지) 추가, REQ-TELEGRAM-001/002/003/010/011/012 복합 절 분리(REQ-TELEGRAM-013~017 신규), REQ-TELEGRAM-008 설정 가능성을 REQ-TELEGRAM-018(Where)로 분리, plan.md M4에 `pyproject.toml` 의존성 추가 단계 명시.
- 신규 범위: 사진 OCR(pytesseract, SPEC-PDF-001이 제외한 범위) — REQ-TELEGRAM-007.
- plan-audit 5차 반복(narrow-scope, 2026-07-16) 수정 반영: REQ-TELEGRAM-018 인수 기준 부재 해소(AC-TELEGRAM-001b 신규), REQ-TELEGRAM-006/007의 shall 절에서 함수·라이브러리 리터럴 제거(§C로 일원화), AC-TELEGRAM-005b `.gitignore` 정적 점검을 런타임 트리거에서 분리, AC-TELEGRAM-002b 미구현 절에 §Exclusions 추적 참조 추가.
- **Plan Audit Gate 최종 결과 (2026-07-16)**: plan-auditor 5회 반복 끝에 **PASS** (overall score 1.00, Tier M 기준 0.80). Must-pass 5 PASS + 2 N/A, 전 카테고리(Clarity/Completeness/Testability/Traceability) 1.0. 상세 보고서: `.moai/reports/plan-audit/SPEC-TELEGRAM-001-review-5.md`. Depends_on Pre-flight Check도 통과(SPEC-PDF-001 `status: completed`). plan_status: audit-ready.

## §F Phase 4 Mode Selection

- Input parameters: tier=M, scope≈8-10 files(신규 `src/markdown_creat/telegram_bot/` 서브패키지 7개 모듈 + 대응 테스트, 단일 도메인(Python 봇 백엔드)), domain count=1, file language mix=100% Python, concurrency benefit=LOW(코딩 중심 작업).
- Mode evaluation: trivial — not selected(단순 오타 수준 아님) / background — not selected(쓰기 작업 포함) / agent-team — RETIRED(선택 불가) / parallel — not selected(단일 도메인 코딩 작업, Anthropic 코딩-작업 병렬성 예외 적용) / workflow — not selected(파일 수 ~30 미만, 기계적 변환 아님) / **sub-agent — selected**(TDD 순차 마일스톤 진행에 적합한 기본값).
- **Decision: sub-agent** (Mode 5).
- Justification: SPEC-TELEGRAM-001은 단일 Python 서브패키지 내 순차적 TDD(RED-GREEN-REFACTOR) 구현이며, plan.md §D가 이미 M1~M6 순서(결정 번복 가능성 순)로 마일스톤화되어 있다. Anthropic의 코딩-작업 병렬성 예외("most coding tasks involve fewer truly parallelizable tasks than research")에 따라 순차 sub-agent(manager-develop, cycle_type=tdd) 위임이 적절하다.

## §E.2 Run-phase Evidence

manager-develop (cycle_type=tdd, RED-GREEN-REFACTOR) implemented `src/markdown_creat/telegram_bot/` across milestones M1-M6 per plan.md §D. 8 new modules (`__init__.py`, `__main__.py`, `config.py`, `bot.py`, `dispatch.py`, `handlers.py`, `storage.py`, `ocr.py`, `extract.py`) + 9 new test files (70 test cases total, including the 16 pre-existing SPEC-PDF-001 tests). PRESERVE targets (`pdf_to_markdown.py`, `src/markdown_creat/__init__.py`, `tests/test_pdf_to_markdown.py`) verified unmodified (`git diff --stat` empty).

### AC Binary PASS/FAIL Matrix

| AC | Status | Verification Command | Actual Output |
|----|--------|----------------------|----------------|
| AC-TELEGRAM-001a (text save, REQ-004/008/009) | PASS | `pytest tests/test_telegram_storage.py::test_save_note_writes_utf8_md_file_and_creates_date_dir tests/test_telegram_dispatch.py::test_on_text_message_saves_note_with_sender_and_stripped_timestamp` | 2 passed |
| AC-TELEGRAM-001b (base folder config, REQ-018/008) | PASS | `pytest tests/test_telegram_storage.py::test_note_dir_uses_configured_base_folder_instead_of_default tests/test_telegram_config.py::test_load_base_folder_uses_configured_env_var` | 2 passed |
| AC-TELEGRAM-002a (photo save + OCR, REQ-005/007/009) | PASS | `pytest tests/test_telegram_handlers.py::test_handle_photo_message_saves_original_and_merges_ocr_text tests/test_telegram_dispatch.py::test_on_photo_message_downloads_highest_resolution_photo_and_saves_note` | 2 passed |
| AC-TELEGRAM-002b (PDF save + extraction, REQ-005/006/009) | PASS | `pytest tests/test_telegram_handlers.py::test_handle_document_message_extracts_pdf_text_via_extract_wrapper tests/test_telegram_extract.py tests/test_telegram_dispatch.py::test_on_document_message_downloads_and_extracts_pdf_text` | 6 passed |
| AC-TELEGRAM-003a (token fail-fast, REQ-003/015) | PASS | `pytest tests/test_telegram_config.py::test_load_bot_token_raises_when_no_token_configured_anywhere tests/test_telegram_bot.py::test_run_polling_fails_fast_when_token_missing tests/test_telegram_main.py` | 3 passed |
| AC-TELEGRAM-003b (long polling only, no webhook, REQ-001/013) | PASS | `pytest tests/test_telegram_bot.py::test_build_application_registers_error_handler` + static check: `grep -ri webhook src/markdown_creat/telegram_bot/` -> no matches (only `run_polling()` is used) | 1 passed; grep empty |
| AC-TELEGRAM-004a (API/network error -> continue polling, REQ-010/016) | PASS | `pytest tests/test_telegram_bot.py::test_on_error_logs_the_error tests/test_telegram_bot.py::test_on_error_never_raises_so_polling_can_continue` | 2 passed |
| AC-TELEGRAM-004b (extraction failure -> original preserved, REQ-005/011/017) | PASS | `pytest tests/test_telegram_handlers.py::test_handle_photo_message_saves_original_and_failure_note_on_ocr_error tests/test_telegram_handlers.py::test_handle_document_message_saves_original_and_failure_note_on_pdf_error` | 2 passed |
| AC-TELEGRAM-005a (no secret in .md/logs, REQ-012) | PASS | `pytest tests/test_telegram_config.py::test_bot_token_never_referenced_by_handlers_storage_ocr_extract_modules tests/test_telegram_config.py::test_mask_secret_never_exposes_full_token` | 2 passed |
| AC-TELEGRAM-005b (token source env/.env, no hardcode, REQ-002/014) | PASS | `pytest tests/test_telegram_config.py::test_load_bot_token_reads_from_dotenv_file_when_env_var_absent tests/test_telegram_config.py::test_load_bot_token_environment_variable_takes_priority_over_dotenv` + static check: `.gitignore` contains `.env` (confirmed) | 2 passed; `.env` gitignore entry confirmed |

10/10 AC PASS. All REQ-TELEGRAM-001~018 confirmed traceable (>=1 explicit `REQ-TELEGRAM-0NN` reference across source/tests each; verified via per-REQ grep sweep).

### Full Suite + Coverage

```
$ pytest tests/ --cov=src/markdown_creat --cov-report=term-missing
70 passed in 5.64s
TOTAL   297 stmts, 11 miss, 96% coverage
```

Per-module coverage: `storage.py`/`config.py`/`extract.py`/`ocr.py`/`handlers.py`/`dispatch.py` = 100%; `bot.py` = 83% (uncovered: the blocking `application.run_polling()` network call, intentionally excluded from unit tests); `__main__.py` = 87% (uncovered: `sys.exit(main())` guard). 96% overall exceeds the 85% target (`quality.yaml` `constitution.test_coverage_target`) and the 80% per-commit minimum on every milestone commit.

### Lint/Format

```
$ ruff check src/markdown_creat/telegram_bot/ tests/   -> All checks passed!
$ black --check src/markdown_creat/telegram_bot/ tests/ -> All done! 18 files would be left unchanged.
```

### Files Created (planned vs actual, plan.md §C)

Planned: `__init__.py`, `__main__.py`, `config.py`, `bot.py`, `handlers.py`, `storage.py`, `ocr.py`, `extract.py` (8 modules, "최종 모듈 분할은 M4~M6에서 확정" per plan.md).
Actual: all 8 planned modules + 1 additional module `dispatch.py` (Update -> handlers.py adapter layer, isolating `python-telegram-bot`'s `Update`/`Context` types from the bot-library-independent `handlers.py` so handlers stay unit-testable without a live bot). This is a scope-internal drift (new file within the already-approved `telegram_bot/` subpackage, no new external dependency), not a SPEC-body change.

Test files (9): `test_telegram_storage.py`, `test_telegram_extract.py`, `test_telegram_ocr.py`, `test_telegram_handlers.py`, `test_telegram_config.py`, `test_telegram_bot.py`, `test_telegram_main.py`, `test_telegram_dispatch.py` (8 new) + pre-existing `test_pdf_to_markdown.py` (untouched).

`pyproject.toml`: added `python-telegram-bot>=22.0` and `pytesseract>=0.3.13` to `[project.dependencies]` (pulled forward from M4 to M2, since M2's handler/extraction tests required them importable — see M2 commit message for rationale).

### Milestone Commits (local, not pushed — `git-strategy.yaml` mode=manual, push_to_remote=false)

| Milestone | Commit SHA | Subject |
|-----------|-----------|---------|
| M1 | `01b8a96` | feat(SPEC-TELEGRAM-001): M1 storage layout and note schema (TDD RED-GREEN) |
| M2 | `45a4048` | feat(SPEC-TELEGRAM-001): M2 handler contracts and extraction integration (TDD RED-GREEN) |
| M3 | `1b0a8d2` | feat(SPEC-TELEGRAM-001): M3 error handling and token injection policy (TDD RED-GREEN) |
| M4 | `a05bf5f` | feat(SPEC-TELEGRAM-001): M4 bot entry point (python -m markdown_creat.telegram_bot) |
| M5 | `5f82809` | feat(SPEC-TELEGRAM-001): M5 full handler/storage/extraction integration (TDD RED-GREEN) |
| M6 | `605cea4` (backfilled at sync-phase) | chore(SPEC-TELEGRAM-001): M6 refactor, quality gate, and status transition (TDD REFACTOR) |

No `git push` was attempted at any milestone (push_to_remote: false confirmed in `.moai/config/sections/git-strategy.yaml`). No `--no-verify` was used on any commit.

### Blocker Reports

None. The in-memory PDF extraction question flagged in plan.md §D M2 as a potential blocker did not materialize: `pdf_to_markdown()`'s file-output-only contract was bridged cleanly via a temp-file write-then-read wrapper (`extract.py`), with no need to modify or reimplement SPEC-PDF-001.

## §E.3 Run-phase Audit-Ready Signal

```yaml
run_complete_at: "2026-07-16"
run_commit_sha: ["01b8a96", "45a4048", "1b0a8d2", "a05bf5f", "5f82809"]
run_status: PASS
ac_pass_count: 10
ac_fail_count: 0
preserve_list_post_run_count: 3  # pdf_to_markdown.py, src/markdown_creat/__init__.py, tests/test_pdf_to_markdown.py -- all verified unmodified via `git diff --stat`
l44_pre_commit_fetch: "n/a -- push_to_remote: false (git-strategy.yaml manual mode); no remote fetch performed or required during this local-only run-phase"
l44_post_push_fetch: "n/a -- no git push was attempted at any milestone"
new_warnings_or_lints_introduced: 0  # ruff check + black --check both clean across all new/modified files
cross_platform_build:
  windows_native: "N/A for Python (no cross-compilation step); pytest/ruff/black all executed natively on Windows via project .venv"
total_run_phase_files: 17  # 9 new src modules + 8 new test files (test_pdf_to_markdown.py pre-existing, untouched)
m1_to_mN_commit_strategy: "one commit per milestone (M1-M6), each following RED (failing test) -> GREEN (minimal implementation) per plan.md's M1-M3=RED / M4-M5=GREEN / M6=REFACTOR grouping; M2 additionally pulled forward pyproject.toml dependency declarations from M4 since M2's own tests required them importable"
```

## §E.4 Sync-phase Audit-Ready Signal

manager-docs (Level 2 spec-anchored sync) updated spec.md (as-implemented annotation for `dispatch.py`), plan.md (M1-M6 marked complete with actual commit SHAs + dependency-timing note reconciliation), acceptance.md (10/10 AC PASS confirmation cross-referenced against this file's §E.2 matrix), README.md (new Telegram bot Features/Usage/Project Status sections), and CHANGELOG.md (new `[Unreleased]` → `### Added` entry). Frontmatter `status:` transitioned `in-progress → completed` across all 4 SPEC artifacts on the single sync commit (merged 3-phase close per spec-frontmatter-schema.md). MX tag scan: skipped (best-effort, no obviously-missing `@MX:ANCHOR` observed on a quick pass; not blocking per sync-phase scope). No `git push` / `gh pr create` performed (`push_to_remote: false`, main_direct workflow, solo-developer local-only).

```yaml
sync_complete_at: "2026-07-16"
sync_commit_sha: "15cb129"  # backfilled 2026-07-17 -- docs(SPEC-TELEGRAM-001): sync-phase documentation and completion status
sync_status: PASS
changelog_entry_position: "[Unreleased] > ### Added, appended after the existing SPEC-PDF-001 entry"
frontmatter_status_transitions:
  spec_md: "in-progress -> completed"
  plan_md: "in-progress -> completed"
  acceptance_md: "in-progress -> completed"
  progress_md: "in-progress -> completed"
```

## §G Post-completion Incident Log

> Fresh top-level section per `.claude/rules/moai/development/spec-frontmatter-schema.md` § progress.md Section Map (Section-letter allocation rule: new concerns claim a fresh top-level letter and MUST NOT overload `§E`/`§E.N`; retired `§E.5` is not reused). `status:`/`version:`는 변경하지 않음(`completed` 유지).

### Post-completion incident: httpx token leak (2026-07-16)

- **증상/분류**: sync 완료 이후 라이브 스모크 테스트에서 봇 토큰이 로그에 raw로 노출됨 (REQ-TELEGRAM-012 위반: "봇 토큰 등 비밀 값을 저장된 `.md` 파일이나 로그에 기록하지 않는다").
- **근본 원인**: `httpx`가 요청 URL 전체를 INFO 레벨로 기록하고 `python-telegram-bot`이 그 URL에 봇 토큰을 담아, `bot.py`의 `mask_secret()` 마스킹 경로를 우회함. 애플리케이션 자체 로그 라인은 이미 토큰을 마스킹했으나 httpx의 요청 로그는 그 마스킹을 거치지 않았다.
- **수정**: commit `1d38743` — 진입점 `src/markdown_creat/telegram_bot/__main__.py:22`에서 `logging.getLogger("httpx").setLevel(logging.WARNING)`로 httpx INFO 로깅을 억제. 소스 변경 없음(가드만 추가).
- **AC 검증 공백**: AC-TELEGRAM-005a는 §E.2 매트릭스에서 PASS로 기록되었으나, 원 검증(`test_bot_token_never_referenced_by_handlers_storage_ocr_extract_modules`, `test_mask_secret_never_exposes_full_token`)은 httpx 로깅 경로를 실행하지 않아 실제 위반을 놓쳤다.
- **공백 폐쇄**: `tests/test_telegram_main.py::test_main_suppresses_httpx_info_logging_to_prevent_token_leak` 회귀 가드 추가 — `main()` 실행 후 httpx 로거의 `.level == logging.WARNING`을 검증하며, 억제 줄(`__main__.py:22`) 제거 시 실패한다. 이로써 AC-TELEGRAM-005a가 httpx 경로까지 커버.
