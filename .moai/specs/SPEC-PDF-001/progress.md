---
id: SPEC-PDF-001
title: "PDF → 마크다운 변환 코어 기능 — 진행 기록"
version: "0.2.0"
status: completed
created: 2026-07-14
updated: 2026-07-19
author: manager-spec
priority: P1
phase: "v0.2.0 target"
module: "src/markdown_creat"
lifecycle: spec-anchored
tags: "pdf, markdown, extraction, pymupdf, conversion, ocr"
tier: M
amendment_of: SPEC-PDF-001
depends_on: [SPEC-OCR-001]
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

### v0.2.0 앰언드먼트 — OCR 자동 폴백 통합 (Run-phase Evidence)

plan.md §F의 M1~M5(TDD RED-GREEN-REFACTOR)를 그대로 구현. `pdf_to_markdown.py`에
`PDFOCRFailedError(MarkdownConversionError)` 신설(`__all__`에 추가), `_build_markdown()`이
`None`을 반환하는 지점(텍스트 레이어 없음)을 신규 헬퍼 `_ocr_fallback_markdown()` 호출로
대체 — `document.close()` 이후(기존 `finally` 블록 밖)에 호출되어 plan.md §F.3 M2의
순서 요구사항을 만족한다. `markdown_creat.ocr.extract_pdf_text_via_ocr()`는 원본 그대로
재사용(수정 없음 — 아래 diff 확인 참조), `lang="kor+eng"` 리터럴 고정(REQ-PDF-012, 새 공개
파라미터 미노출).

| AC | Status | Verification Command | Actual Output |
|----|--------|----------------------|----------------|
| AC-PDF-003a (스캔 PDF, OCR 성공) | PASS | `pytest -k test_pdf_to_markdown_ocr_fallback_succeeds_for_scanned_pdf -v` | `PASSED` |
| AC-PDF-003b (스캔 PDF, OCR도 텍스트 없음) | PASS | `pytest -k test_pdf_to_markdown_ocr_fallback_finds_no_text_raises_pdfnotext -v` | `PASSED` |
| AC-PDF-003c (OCR 엔진 오류 → PDFOCRFailedError) | PASS | `pytest -k test_pdf_to_markdown_ocr_engine_failure_raises_pdfocrfailederror -v` | `PASSED` |
| AC-PDF-003d (텍스트 PDF는 OCR 미호출, 회귀 없음) | PASS | `pytest -k test_pdf_to_markdown_text_layer_pdf_never_calls_ocr -v` | `PASSED` |

기존 테스트 조정(plan.md §F.3 M3): `test_pdf_to_markdown_raises_clear_error_when_no_extractable_text`
및 `test_pdf_to_markdown_never_leaves_partial_output_on_error[no_text]`를
`markdown_creat.ocr.pytesseract.image_to_string` 빈 문자열(`""`) 모킹으로 갱신 —
assertion 자체(`pytest.raises(PDFNoTextError)`, `not output_path.exists()`)는 변경 없음.

REQ traceability 추가: REQ-PDF-009(개정, "텍스트 레이어에도 OCR에도 텍스트 없음"으로
의미 확장) → 위 2개 조정 테스트 + AC-PDF-003b; REQ-PDF-011(OCR 엔진 오류 시맨틱) →
AC-PDF-003c; REQ-PDF-012(OCR 언어 `kor+eng` 리터럴 고정) → AC-PDF-003a의
`mock_ocr.call_args.kwargs.get("lang") == "kor+eng"` assertion; REQ-PDF-013(다중 페이지
병합)은 기존 `test_pdf_to_markdown_multi_page_merges_into_single_md_in_page_order`로
이미 검증됨(v0.2.0에서 신규 테스트 불필요, 재확인만).

전체 회귀: `pytest tests/ -v` 94 passed (기존 v0.1.0 17개 + telegram_bot/ocr 관련 기존
77개 전체 무수정 그린, 신규 4개 포함). 커버리지: `pdf_to_markdown.py` 95%(86 stmts, 4 miss
— 라인 159/164/167/186, 기존 `_classify_heading_levels`/`_build_markdown`의 도달 불가
방어 분기, v0.2.0 신규 분기와 무관). 린트: `ruff check` 무경고, `black --check` 무수정.

`ocr.py` 재사용 확인(diff): `git diff --stat src/markdown_creat/ocr.py` → 무출력(변경 없음).
`telegram_bot/*` 재확인: `git status --porcelain`에 미포함(무수정) — 브리지 계층을 통해
효과가 투명하게 전파됨(수정 불필요).

설계 결정(v0.2.0, plan.md §F.2에서 이미 확정된 4개 결정을 그대로 구현, 재논의 없음):
- 통합 지점: `pdf_to_markdown()` 내부(결정 1). `extract.py` 브리지 계층은 수정하지 않음.
- 오류 시맨틱: OCR 엔진 오류 → `PDFOCRFailedError`(신규), OCR 완료 후 텍스트 없음 →
  기존 `PDFNoTextError` 재사용(결정 2). 원본 `OcrError` 메시지가 감싸는 메시지에 보존됨
  (`f"OCR fallback failed for PDF: {pdf_path}: {exc}"`).
- 페이지 수/타임아웃 상한 없음(결정 3, YAGNI 적용, 잔여 위험으로 문서화).
- OCR 언어 `kor+eng` 리터럴 고정(결정 4).

## §E.3 Run-phase Audit-Ready Signal

```yaml
run_complete_at: "2026-07-16"
run_commit_sha: "53dddd2"  # backfilled 2026-07-17 — M1-M5 단일 커밋 (feat(SPEC-PDF-001): M1-M5 PDF to Markdown core conversion (TDD))
run_status: green
ac_pass_count: 8
ac_fail_count: 0
preserve_list_post_run_count: 0
l44_pre_commit_fetch: "0 0 (origin/master...HEAD, in-sync)"
l44_post_push_fetch: "unrecoverable — run-phase(2026-07-16) 당시 값이 기록되지 않았고 사후 복원 불가. 2026-07-17 확인: 53dddd2는 origin/master(1d38743)의 조상이므로 이후 시점에 push되었으나, run-phase 종료 시점의 fetch 상태는 알 수 없음."
new_warnings_or_lints_introduced: 0
cross_platform_build:
  windows: "N/A (Python project, no cross-platform build tags)"
total_run_phase_files: 4
m1_to_mN_commit_strategy: "single commit covering M1-M5 (RED+GREEN+REFACTOR authored in one continuous session; no RED state was ever pushed to master)"
```

### v0.2.0 앰언드먼트 — Run-phase Audit-Ready Signal (addendum)

```yaml
run_complete_at: "2026-07-19"
run_commit_sha: "01312495"  # backfilled — feat(SPEC-PDF-001): M1-M5 wire automatic OCR fallback into pdf_to_markdown
run_status: green
ac_pass_count: 4  # AC-PDF-003a~d (신규); 기존 8 AC(v0.1.0)도 전체 재확인 PASS, 회귀 없음
ac_fail_count: 0
preserve_list_post_run_count: 0  # ocr.py, telegram_bot/* 모두 무수정 확인됨
new_warnings_or_lints_introduced: 0
cross_platform_build:
  windows: "N/A (Python project, no cross-platform build tags)"
total_run_phase_files: 2  # src/markdown_creat/pdf_to_markdown.py, tests/test_pdf_to_markdown.py
m1_to_mN_commit_strategy: "single commit covering M1-M5 (RED tests + GREEN implementation authored together, per Tier M plan.md §F.3 milestones)"
```

## §E.4 Sync-phase Audit-Ready Signal

```yaml
sync_complete_at: "2026-07-16"
sync_commit_sha: "b19d622"  # backfilled 2026-07-17 — docs(SPEC-PDF-001): sync-phase artifacts (README.md·CHANGELOG.md 신규 생성 커밋)
docs_updated:
  - "README.md (created)"
  - "CHANGELOG.md (created)"
spec_status_transition: "in-progress -> completed"
```

Sync 범위: 프로젝트 루트에 README.md, CHANGELOG.md를 신규 생성하고 SPEC-PDF-001의
spec.md/progress.md frontmatter 상태를 `in-progress` → `completed`로 전환.
테스트 재검증: `pytest -q` 17 passed (회귀 없음).

무관한 변경 제외: 이번 세션에서 git 상태에 함께 나타난 300개 이상의 "수정됨" 표시
파일(.claude/, .moai/config/ 등)은 `core.autocrlf=true` 설정으로 인한 줄바꿈 문자
정규화 경고일 뿐 실제 내용 변경이 아니며, SPEC-PDF-001과 무관하므로 사용자 확인 후
이번 sync 커밋 범위에서 명시적으로 제외함.

### v0.2.0 앰언드먼트 — Sync-phase Audit-Ready Signal (addendum)

```yaml
sync_complete_at: "2026-07-19"
sync_commit_sha: "c0ee1801"  # backfilled — docs(SPEC-PDF-001): sync-phase artifacts + 3-phase close (v0.2.0 OCR fallback)
docs_updated:
  - "README.md (OCR fallback description, PDFOCRFailedError, Out of Scope, Project Status)"
  - "CHANGELOG.md ([Unreleased] Added — v0.2.0 OCR fallback entry + stale note update)"
spec_status_transition: "in-progress -> completed"
```

Sync 범위(v0.2.0): plan-phase 단계에서 초안 작성된 채 커밋되지 않고 남아 있던
spec.md/plan.md/acceptance.md의 v0.2.0 앰언드먼트 본문(REQ-PDF-009 개정,
REQ-PDF-011/012/013 신설, Amendments 섹션)을 run-phase 구현(커밋 `01312495`)과
함께 이번 sync 커밋에서 최초로 커밋한다 — 본문 내용은 이미 작성 완료된 상태였으며
이번 sync에서는 frontmatter `status:` 전환만 수행(spec-frontmatter-schema.md
Status Transition Ownership Matrix에 따라 manager-docs 소유 범위 내).
README.md/CHANGELOG.md의 "OCR 폴백 아직 미구현" 서술을 실제 구현 완료 상태로 갱신.
테스트 재검증: `pytest -q` 94 passed(전체), `pytest tests/test_pdf_to_markdown.py -q`
21 passed(회귀 없음). `ruff check .` 무경고. 커버리지 `pdf_to_markdown.py` 95%
(기존 progress.md §E.3 addendum 값과 일치, 재측정으로 확인).

제외: `.moai/specs/.moai/state/context-usage.json`(원인 불명 런타임 상태 파일,
SPEC-PDF-001과 무관), `telegram-notes/`(텔레그램 봇 런타임 데이터, 코드/문서
변경 아님) — 둘 다 이번 sync 커밋 범위에서 명시적으로 제외.

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
