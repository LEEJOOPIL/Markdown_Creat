---
id: SPEC-OCR-001
title: "OCR 코어 모듈 — 이미지·PDF 텍스트 추출 (한국어 지원) — 진행 기록"
version: "0.3.0"
status: completed
created: 2026-07-17
updated: 2026-07-18
author: manager-spec
priority: P1
phase: "v0.1.0 target"
module: "src/markdown_creat"
lifecycle: spec-anchored
tags: "ocr, tesseract, pdf, markdown, korean, extraction, shared-module"
tier: M
depends_on: [SPEC-TELEGRAM-001]
---

# SPEC-OCR-001 — 진행 기록 (progress.md)

## §E.1 Plan-phase Audit-Ready Signal

- plan_status: audit-ready
- plan_complete_at: 2026-07-17
- artifact_set: spec.md, plan.md, acceptance.md (Tier M, 3-file) + progress.md (canonical §E skeleton)
- depends_on: [SPEC-TELEGRAM-001] — `status: completed` as of plan-phase authoring (verified 2026-07-17)
- key architecture decision recorded in plan.md §B: **path (c) re-scoping** — this SPEC owns ONLY `src/markdown_creat/ocr.py` + the `telegram_bot/ocr.py` thin re-export. It neither calls, modifies, nor amends `pdf_to_markdown()`. `amendment_of` is not set on SPEC-OCR-001 and SPEC-PDF-001 is NOT a dependency.
- plan-auditor iteration 1 verdict: **PASS 0.87** (Tier M threshold 0.80). Dimensions: Clarity 0.85 / Completeness 0.80 / Testability 0.90 / Traceability 1.00. All 7 must-pass PASS or N/A. Report: `.moai/reports/plan-audit/SPEC-OCR-001-review-1.md` (gitignored). Findings D1-D8 remediated in v0.3.0 (see below).

### v0.3.0 audit remediation (2026-07-17)

Iteration-1 audit passed at 0.87 but surfaced a rationale error and a scope gap. v0.3.0 applies:

- **D3 (highest) — Korean OCR had no reachable call path.** `handlers.py:71` called `extract_image_text()` with no `lang` argument, so REQ-OCR-006 defaulted it to `"eng"`; no REQ/AC wired `lang="kor"` to any caller. The user's approved decision #3 (Korean support) was architecturally stranded — the capability shipped in `ocr.py` but nothing activated it. This predated path (c) (v0.1.0's PDF fallback also passed no lang). Fixed by new **REQ-OCR-015** (bot photo path calls the core function with literal `"kor+eng"`) + **AC-OCR-006a** (seam test asserting the lang argument reaches mocked `pytesseract.image_to_string`). Split delivery is stated in spec.md §A: the **photo path** now delivers Korean end-to-end; the **PDF path** still delivers nothing until SPEC-PDF-001's amendment.
- **D1/D2 — the v0.2.0 "circular dependency" framing below was factually wrong.** The Depends_on Pre-flight Check is a one-shot entry gate run BEFORE the plan-auditor, when SPEC-PDF-001 is still `completed`, so it passes; M2 runs afterward and cannot retroactively fail it. The accurate term is a **self-invalidating precondition** (re-entrancy hazard on a second `/moai run`), NOT a graph cycle. And `--ignore-deps` is a sanctioned 3-option override (`spec-workflow.md`), so defect 1 was never a blocker — its avoidance is not a benefit worth scoring (double-count removed). **path (c)'s justification rests on defect 2 alone** (the reversed dependency arrow / SSOT duplication), which remains verified. Corrected wording lives in spec.md HISTORY + plan.md §B; the v0.2.0 text below is retained as the record of what was corrected.
- **D4 — deferred-amendment anchor: no schema-supported mechanical anchor exists now.** The canonical `amendment_of` + `completed → in-progress` anchor requires flipping SPEC-PDF-001 out of `completed` (the exact hazard path (c) avoids); a present-tense `depends_on: [SPEC-OCR-001]` on the completed PDF SPEC would be a git-contradicted false declaration. manager-spec instead downgraded the unkeepable promise in spec.md §Exclusions and pre-recorded the exact frontmatter recipe (to run at amendment-authoring time) in plan.md §B. SPEC-PDF-001 was NOT edited.
- **D5-D8 — minor**: GWT label, `Where`→`When` in REQ-OCR-006/007, hybrid-label simplification (all three of REQ-OCR-003/005/008), §A residue.

Surviving requirement set (v0.3.0): REQ-OCR-001~008, 013, 014, **015** (11 requirements).
Surviving AC set (v0.3.0): AC-OCR-001a~c, 002a~b, 003a~c, 005a, **006a** (10 scenarios).

### v0.2.0 re-scope (2026-07-17)

> Note: the "circular dependency" framing in this v0.2.0 record was corrected in v0.3.0 (see D1/D2 above) — the accurate term is a *self-invalidating precondition*. This section is retained as the record of the re-scope as authored, not as a current statement of the defect taxonomy.

Artifacts revised from v0.1.0 (path b) to v0.2.0 (path c) before any plan-audit or implementation. Two defects in the v0.1.0 design drove the change:

- **Defect 1 — circular dependency**: v0.1.0 declared `depends_on: [SPEC-PDF-001, ...]` while its own M2 transitioned SPEC-PDF-001 `completed → in-progress`. The Depends_on Pre-flight Check requires `status: completed` strictly, so M2 would have failed this SPEC's own preflight. v0.1.0 acceptance.md §D.1 assumed an `--ignore-deps` override without stating it.
- **Defect 2 — reversed dependency arrow + unmet SSOT goal**: `ocr.py` never calls `pdf_to_markdown()` (`extract_pdf_text_via_ocr()` uses PyMuPDF directly; `extract_image_text()` uses pytesseract directly). The real arrow is `pdf_to_markdown.py` → `extract_pdf_text_via_ocr()`. Meanwhile REQ-OCR-009~012 and the planned REQ-PDF-009 amendment would have described the same contract twice — the duplication path (b) claimed to prevent.

Scope removed from this SPEC (now owned by SPEC-PDF-001's own future amendment, to be authored AFTER this SPEC reaches `status: completed`):

- REQ-OCR-009, 010, 011, 012 (`pdf_to_markdown()` auto-OCR-fallback contract)
- AC-OCR-004a, 004b (fallback scenarios)
- plan.md M2 (SPEC-PDF-001 amendment coordination); remaining milestones renumbered M1..M5
- the `pdf_to_markdown.py` fallback hook from plan.md §C

Numbering discipline: REQ-OCR-013/014 and AC-OCR-005a **retain their numbers**; 009~012 and 004a/b are left as deliberate gaps. Renumbering would silently reassign a retired identifier to a new meaning and break traceability for existing references.

Surviving requirement set: REQ-OCR-001~008, 013, 014 (10 requirements).
Surviving AC set: AC-OCR-001a~c, 002a~b, 003a~c, 005a (9 scenarios).

Deferred-work pointer: `spec.md` §Exclusions carries the forward reference to SPEC-PDF-001's amendment. That amendment is NOT yet authored — it is the tracked next step after this SPEC completes, and it is the sole remaining home for the removed 009~012 semantics.

## §E.2 Run-phase Evidence

### Phase 1 Plan Audit Gate (run-gate, date-based stream) — 2026-07-18

- Verdict: **FAIL** (aggregate 0.80) → **overridden to PASS-with-debt** by orchestrator decision, per user selection at Implementation Kickoff.
- Two must-pass firewall items triggered:
  - **MP-1 (REQ numbering gap)**: REQ-OCR-009~012 absent from the sequence. Accepted as debt — the gap is the deliberate, twice-documented artifact of the v0.2.0/v0.3.0 path-(c) re-scope (spec.md HISTORY, plan.md §B, progress.md D9); renumbering would collide with git-history identifiers (commit `8563de2`).
  - **MP-2 (GEARS format binding on AC)**: acceptance.md's 10 scenarios are Given/When/Then, not GEARS "shall" statements. Accepted as debt — this matches the already-completed SPEC-TELEGRAM-001 convention; content is concretely testable (Testability 0.75, Completeness 1.0, Traceability 1.0, Clarity 0.95).
- All other must-pass items PASS or N/A (MP-3 frontmatter, MP-5 cross-SPEC status, MP-6 cross-platform N/A, MP-7 clarification-gate).
- Follow-up (not blocking this SPEC): consider a documented-exception carve-out for MP-1/MP-2 at the plan-auditor rubric level for future SPECs using the same conventions.
- Full independent audit report: agent `plan-audit-ocr001` (2026-07-18), not persisted as a separate file per this run (see this progress.md entry as the record).

### TDD Milestones (manager-develop, cycle_type=tdd) — 2026-07-18

| Milestone | Content | Result |
|-----------|---------|--------|
| M1 | `ocr.py` public API + `OcrError` exception contract; RED tests in `tests/test_ocr.py` | GREEN |
| M2 | PDF page rendering via `page.get_pixmap(dpi=300)` + temp-file bridge (no new Pillow dependency); merge in page order | GREEN |
| M3 | `telegram_bot/ocr.py` reduced to thin re-export; `handlers.py` photo-path `lang="kor+eng"` wiring; `tests/test_telegram_ocr.py` mock target updated to `markdown_creat.ocr.pytesseract.image_to_string` | GREEN |
| M4 | Full implementation verified against acceptance.md | GREEN |
| M5 | `ruff` + `black` clean on all touched files; coverage 100% on `ocr.py` (exceeds 85% target); full suite 84/84 green (0 regressions vs 71-test baseline: 71 pre-existing + 12 new `test_ocr.py` + 1 new `test_telegram_handlers.py` AC-OCR-006a test) | GREEN |

### AC PASS/FAIL Matrix

| AC | REQ | Status | Verification command | Actual output (abbreviated) |
|----|-----|--------|----------------------|------------------------------|
| AC-OCR-001a | REQ-OCR-001 | PASS | `pytest tests/test_ocr.py::test_extract_image_text_returns_ocr_result -q` | `1 passed` |
| AC-OCR-001b | REQ-OCR-002 | PASS | `pytest tests/test_ocr.py::test_extract_image_text_returns_empty_string_when_no_text_found -q` | `1 passed` |
| AC-OCR-001c | REQ-OCR-003 | PASS | `pytest tests/test_ocr.py::test_extract_image_text_wraps_tesseract_engine_failure -q` | `1 passed` |
| AC-OCR-002a | REQ-OCR-004 | PASS | `pytest tests/test_ocr.py::test_extract_pdf_text_via_ocr_merges_pages_in_order -q` | `1 passed` |
| AC-OCR-002b | REQ-OCR-005 | PASS | `pytest tests/test_ocr.py -k "raises_ocr_error_when_pdf_cannot_be_opened or raises_ocr_error_when_page_ocr_fails or raises_ocr_error_when_page_render_fails" -q` | `3 passed` |
| AC-OCR-003a | REQ-OCR-006 | PASS | `pytest tests/test_ocr.py::test_extract_image_text_defaults_to_english_when_lang_not_given -q` | `1 passed` |
| AC-OCR-003b | REQ-OCR-007 | PASS | `pytest tests/test_ocr.py::test_extract_image_text_passes_through_korean_lang_parameter -q` | `2 passed` (parametrized kor / kor+eng) |
| AC-OCR-003c | REQ-OCR-008 | PASS | `pytest tests/test_ocr.py::test_extract_image_text_raises_clear_error_on_missing_language_pack -q` | `1 passed` (original pytesseract message preserved via `match="kor"`) |
| AC-OCR-005a | REQ-OCR-013, 014 | PASS | `pytest tests/test_telegram_ocr.py -q` | `4 passed` (mock target updated to `markdown_creat.ocr.pytesseract.image_to_string`; `telegram_bot/ocr.py` contains no Tesseract call, only re-export) |
| AC-OCR-006a | REQ-OCR-015 | PASS | `pytest tests/test_telegram_handlers.py::test_handle_photo_message_wires_korean_lang_to_pytesseract_seam -q` | `1 passed` (seam-level: mocked `pytesseract.image_to_string` receives `lang="kor+eng"`; mocked Korean text lands in saved `.md` body) |

(AC-OCR-004a/004b: deliberately absent — see §B numbering-gap note above; not applicable to this SPEC.)

## §E.3 Run-phase Audit-Ready Signal

- run_status: implemented, all AC PASS, 0 regressions
- run_complete_at: 2026-07-18
- ac_pass_count: 10 (AC-OCR-001a~c, 002a~b, 003a~c, 005a, 006a)
- ac_fail_count: 0
- full_suite_result: 84 passed (baseline 71 + 13 new: 12 in `tests/test_ocr.py` + 1 in `tests/test_telegram_handlers.py`)
- coverage: `src/markdown_creat/ocr.py` 100% (target 85%)
- lint_format: `ruff check` all-clean; `black --check` clean on all files touched this session (pre-existing `tests/test_telegram_main.py` black-debt is untouched baseline, out of this SPEC's scope)
- diff_scope: `src/markdown_creat/pdf_to_markdown.py` does NOT appear in `git diff --stat`; `handlers.py` diff is a single 1-line hunk (added `lang="kor+eng"`); no new `pyproject.toml` dependency
- new files: `src/markdown_creat/ocr.py`, `tests/test_ocr.py`
- modified files: `src/markdown_creat/telegram_bot/ocr.py` (thin re-export), `src/markdown_creat/telegram_bot/handlers.py` (1-line wiring), `tests/test_telegram_ocr.py` (mock target update), `tests/test_telegram_handlers.py` (new AC-OCR-006a test), `README.md` (OCR feature + kor traineddata install docs), 3 SPEC artifact frontmatter (`draft` → `in-progress`)

## §E.4 Sync-phase Audit-Ready Signal

- sync_status: completed
- sync_complete_at: 2026-07-18
- summary: 10/10 AC PASS (AC-OCR-001a~c, 002a~b, 003a~c, 005a, 006a); full suite 84/84 green (0 regressions vs 71-test baseline); coverage `src/markdown_creat/ocr.py` 100% (target 85%); `ruff` clean; `pdf_to_markdown.py` untouched per SPEC scope boundary.
- artifacts_synced: CHANGELOG.md (`[Unreleased]` § Added, new SPEC-OCR-001 entry), README.md (spot-checked, no correction needed — manager-develop's edits verified accurate against `ocr.py`/`handlers.py`), spec.md/plan.md/acceptance.md frontmatter (`in-progress` → `completed`, `updated: 2026-07-18`)
- sync_commit_sha: 839acd3

## §F Phase 4 Mode Selection

- Input parameters: tier=M; scope≈5 files (`src/markdown_creat/ocr.py` new, `telegram_bot/ocr.py`, `telegram_bot/handlers.py` 1 call site, `tests/test_telegram_ocr.py`, `README.md`); domain count=1 (Python core module + thin re-export, single language); file language mix=100% Python (+README); concurrency benefit=LOW (coding-heavy, sequential milestones with dependencies M1→M2→M3→M4→M5).
- Mode evaluation: trivial=not selected (non-trivial multi-file TDD work); background=not selected (writes code); agent-team=RETIRED, not selected; parallel=not selected (coding-heavy, single domain, Anthropic coding-task caveat applies); workflow=not selected (far below ~30-file mechanical threshold, and this is semantic new-code work); **sub-agent=SELECTED (default)**.
- Decision: sub-agent
- Justification: Tier M SPEC with 5 sequential, dependency-ordered milestones (M1 API/exception contract → M2 PDF rendering → M3 re-export+wiring → M4 GREEN → M5 refactor/quality-gate) implemented via `manager-develop` with `cycle_type: tdd`. Single Python domain, no genuine parallelism opportunity — matches Anthropic's coding-task parallelism caveat (most coding tasks have fewer truly parallelizable tasks than research).
