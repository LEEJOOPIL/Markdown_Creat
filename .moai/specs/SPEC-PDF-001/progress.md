---
id: SPEC-PDF-001
title: "PDF → 마크다운 변환 코어 기능 — 진행 기록"
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

# SPEC-PDF-001 — 진행 기록 (progress.md)

## §E.1 Plan-phase Audit-Ready Signal

- Plan-phase 산출물 세트(spec.md + plan.md + acceptance.md + spec-compact.md + progress.md) 생성 완료.
- SPEC ID 사전 자가검증 통과: `decomposition: SPEC ✓ | PDF ✓ | 001 ✓ → PASS`.
- Frontmatter 12 필드 스키마 검증 완료. Tier M 분류.
- PyMuPDF AGPL 라이선스 리스크를 plan.md §D에 명시(사용자 검토 대상).

## §E.2 Run-phase Evidence

TDD RED-GREEN-REFACTOR cycle completed for SPEC-PDF-001. Greenfield Python packaging
scaffolded (`pyproject.toml`, `src/markdown_creat/__init__.py`); public function
`pdf_to_markdown(pdf_path: str, output_path: str) -> None` implemented in
`src/markdown_creat/pdf_to_markdown.py`.

| AC | Status | Verification Command | Actual Output |
|----|--------|----------------------|----------------|
| AC-PDF-001a (텍스트 추출/파일 생성) | PASS | `pytest -k test_pdf_to_markdown_creates_utf8_md_file_with_body_text -v` | `PASSED` |
| AC-PDF-001b (제목 구조 감지) | PASS | `pytest -k "detects_large_font_as_heading or maps_multiple_heading_sizes_to_levels" -v` | `2 PASSED` |
| AC-PDF-001c (기존 파일 덮어쓰기) | PASS | `pytest -k test_pdf_to_markdown_overwrites_existing_output_file -v` | `PASSED` |
| AC-PDF-002a (파일 부재 오류) | PASS | `pytest -k test_pdf_to_markdown_raises_clear_error_when_file_missing -v` | `PASSED` |
| AC-PDF-002b (손상된 PDF 오류) | PASS | `pytest -k test_pdf_to_markdown_raises_clear_error_for_corrupted_pdf -v` | `PASSED` |
| AC-PDF-002c (암호화된 PDF 오류) | PASS | `pytest -k test_pdf_to_markdown_raises_clear_error_for_encrypted_pdf -v` | `PASSED` |
| AC-PDF-002d (텍스트 없음 오류) | PASS | `pytest -k test_pdf_to_markdown_raises_clear_error_when_no_extractable_text -v` | `PASSED` |
| AC-PDF-002e (오류 시 부분 출력 없음) | PASS | `pytest -k test_pdf_to_markdown_never_leaves_partial_output_on_error -v` | `4 PASSED (parametrized)` |

Additional invariant coverage (edge cases, acceptance.md §D.1): uniform-font-size
document (no headings, not an error), multi-page concatenation in page order,
Korean UTF-8 content, missing parent-directory auto-creation — all covered by
dedicated tests, all PASS.

REQ traceability (spec.md §B, all 10 requirements covered by ≥1 test):
REQ-PDF-001/003 → reading-order + paragraph tests; REQ-PDF-002 → 3 heading-heuristic
tests; REQ-PDF-004 → UTF-8 body-text + Korean tests; REQ-PDF-005 → overwrite test;
REQ-PDF-006~009 → one dedicated error test each; REQ-PDF-010 → the 4-case
parametrized partial-output test plus an explicit `not output_path.exists()`
assertion on every individual error test.

Test-fixture strategy: PyMuPDF (fitz) is the core dependency under test, not an
external network/OCR dependency (spec.md §C), so fixtures are small real PDFs
built programmatically with `fitz.open()` / `page.insert_text()` rather than
mocks/stubs of PyMuPDF's own API.

Design decisions made during run-phase (per plan.md §C open points):
- **M2 heading heuristic**: body size = font size with the highest line-frequency
  (ties broken toward the smaller size, since headings are both larger and less
  frequent by convention); sizes strictly larger than body size are sorted
  descending and mapped to heading levels 1-3, with any additional larger sizes
  beyond the third collapsed into level 3. Grouping is per PyMuPDF text block
  (`page.get_text("dict")`), so consecutive lines PyMuPDF already recognizes as
  one paragraph become one Markdown paragraph.
- **M3 error hierarchy**: `MarkdownConversionError` base with 4 subclasses —
  `PDFNotFoundError`, `PDFCorruptedError` (raised on `fitz.FileDataError`),
  `PDFEncryptedError` (checked via `document.is_encrypted` / `needs_pass`
  immediately after open, before any text access), `PDFNoTextError`.
- **M3 atomicity (REQ-PDF-010)**: the full Markdown string is assembled in
  memory (all validation/error paths execute first) and the output file is
  opened and written exactly once, after assembly succeeds — no error path
  reaches the write step, so no partial file is ever created.
- **Missing parent directory** (plan.md §D open risk): auto-create via
  `os.makedirs(..., exist_ok=True)` rather than raising an error.

## §E.3 Run-phase Audit-Ready Signal

```yaml
run_complete_at: "2026-07-16"
run_commit_sha: "pending-backfill-run-close"
run_status: green
ac_pass_count: 8
ac_fail_count: 0
preserve_list_post_run_count: 0
l44_pre_commit_fetch: "0 0 (origin/master...HEAD, in-sync)"
l44_post_push_fetch: "pending-backfill-post-push"
new_warnings_or_lints_introduced: 0
cross_platform_build:
  windows: "N/A (Python project, no cross-platform build tags)"
total_run_phase_files: 4
m1_to_mN_commit_strategy: "single commit covering M1-M5 (RED+GREEN+REFACTOR authored in one continuous session; no RED state was ever pushed to master)"
```

## §E.4 Sync-phase Audit-Ready Signal

_<pending sync-phase — manager-docs 소유>_

## §F Phase 4 Mode Selection

**Input parameters**: tier=M, scope≈2-3 files (src/markdown_creat/pdf_to_markdown.py + tests/test_pdf_to_markdown.py, plus greenfield scaffolding pyproject.toml/__init__.py), domain count=1 (Python backend library function), file language mix=100% Python, concurrency benefit=LOW (coding-heavy, per Anthropic's coding-task parallelism caveat), Agent Teams prereqs=N/A (Mode 3 retired).

**Mode evaluation**:
| Mode | Selected? | Rationale |
|------|-----------|-----------|
| 1 trivial | No | Non-trivial: new module + TDD cycle + greenfield scaffolding |
| 2 background | No | Write-heavy work, not read-only |
| 3 agent-team | No | RETIRED |
| 4 parallel | No | Single domain, coding-heavy — not research-heavy multi-domain |
| 6 workflow | No | Scope far below ~30-file mechanical threshold; semantic/new-code work |
| 5 sub-agent | **Selected** | Default fallback; coding-heavy single-domain work per Anthropic's coding-task parallelism caveat |

**Decision**: sub-agent

**Justification**: SPEC-PDF-001 is a single-domain (Python backend), single-module implementation (one public function + greenfield scaffolding) with a sequential TDD milestone structure (M1→M5). Anthropic's coding-task parallelism caveat favors sequential sub-agent delegation over parallel fan-out for coding-heavy work. Mode 5 is the correct default.

**Plan Audit Gate**: plan-auditor iteration 2/3 verdict PASS (0.87 harmonic / 0.89 simple average, Tier M threshold 0.80). Iteration 1 FAIL (MP-2 mis-scoping, corrected in iteration 2 — see .moai/reports/plan-audit/SPEC-PDF-001-review-2.md).

**Implementation Kickoff Approval**: user approved via AskUserQuestion — "바로 구현 시작" (proceed to implementation immediately).
