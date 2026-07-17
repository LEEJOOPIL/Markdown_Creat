---
id: SPEC-OCR-001
title: "OCR 코어 모듈 — 이미지·PDF 텍스트 추출 (한국어 지원) — 진행 기록"
version: "0.3.0"
status: draft
created: 2026-07-17
updated: 2026-07-17
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

_<pending run-phase>_

## §E.3 Run-phase Audit-Ready Signal

_<pending run-phase>_

## §E.4 Sync-phase Audit-Ready Signal

_<pending sync-phase>_
