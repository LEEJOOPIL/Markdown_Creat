---
id: SPEC-TELEGRAM-003
title: "텔레그램 봇 Windows 더블클릭 실행기 — 진행 기록"
version: "0.1.1"
status: in-progress
created: 2026-07-18
updated: 2026-07-18
author: manager-spec
priority: P2
phase: "v0.1.0 target"
module: "run_telegram_bot.bat"
lifecycle: spec-anchored
tags: "telegram, bot, launcher, windows, batch, ux"
depends_on: [SPEC-TELEGRAM-001]
tier: M
---

# SPEC-TELEGRAM-003 — 진행 기록 (progress.md)

## §E.1 Plan-phase Audit-Ready Signal

- Plan-phase 산출물 세트(spec.md + plan.md + acceptance.md + progress.md, 추가로 요약본 spec-compact.md) 생성 완료. Tier M(3-파일 세트 + progress.md — fail-fast·콘솔 유지 UX 계약의 감사 가능성을 위해 acceptance.md 별도 유지, `SPEC-TELEGRAM-001`/`002`와 동일한 구조적 관례를 따름).
- SPEC ID 사전 자가검증 통과: `decomposition: SPEC ✓ | TELEGRAM ✓ | 003 ✓ → PASS` (canonical regex `^SPEC(-[A-Z][A-Z0-9]*)+-\d{3}$`, Bash 실행 출력 `PASS`).
- Frontmatter 12 필드 canonical 스키마 검증 완료 + optional 필드 `depends_on: [SPEC-TELEGRAM-001]`, `tier: M` 기록.
- 요구사항 배경: `SPEC-TELEGRAM-001`(status: completed)로 구현된 텔레그램 봇(`python -m markdown_creat.telegram_bot`)을 터미널 없이 더블클릭만으로 실행할 수 있는 Windows `.bat` 실행기(`run_telegram_bot.bat`)를 정의. `SPEC-TELEGRAM-001` §A가 이미 "수동 실행(`python -m ...` 또는 실행 스크립트)"이라는 경로를 열어두었고, 본 SPEC이 그 "실행 스크립트" 경로를 구체화한다.
- EARS 요구사항 REQ-TELEGRAM-024~035 정의(Ubiquitous / Event-driven / Unwanted 혼합, 12개). REQ ID는 `SPEC-TELEGRAM-002`의 REQ-TELEGRAM-019~023에 이어 024부터 부여(동일 `TELEGRAM` 도메인 접두어 충돌 방지).
- §Exclusions에 7개 `### Out of Scope —` 하위 헤딩 포함(자동 시작/OS 서비스 등록[SPEC-TELEGRAM-001 계승], 백그라운드/데몬 실행, venv 자동 생성/의존성 자동 설치, 봇 토큰/설정 관리, 중복 실행 방지, macOS/Linux 셸 스크립트 등가물, 콘솔 유니코드/코드페이지 완전 대응).
- 의존성: `SPEC-TELEGRAM-001`(status: completed) — 실행 대상 봇 진입점(`__main__.py`)의 소유자. run-phase Depends_on Pre-flight Check는 통과가 예상된다.
- 개발 방법론: `quality.yaml` `constitution.development_mode: tdd`를 명목상 따르되, `.bat` 스크립트는 pytest/ruff/black 적용 대상이 아니므로 acceptance.md의 EARS/GEARS 시나리오 수동 검증으로 품질 게이트를 대체한다(plan.md §E 리스크에 명시).
- 사용자와 확인된 6대 인수 시나리오: (a) 정상 실행(venv+토큰 존재) → 봇 시작 로그 확인, (b) venv 부재 → 명확한 오류 + 콘솔 유지 + 0이 아닌 종료 코드, (c) 토큰 부재 → 기존 `MissingBotTokenError` 메시지가 콘솔에 노출되며 콘솔 유지, (d)~(f) 정적 스크립트 검토(bare `python` 미사용, OS 자동 시작 미등록, 포그라운드 전용 실행).
- **plan-audit iteration 1 리뷰 반영** (`.moai/reports/plan-audit/SPEC-TELEGRAM-003-review-1.md`, verdict FAIL, score 0.67 → 버전 0.1.1로 개정): (D1, critical) `acceptance.md` §D의 "GEARS / Given-When-Then" 이중 표기를 제거하고 3개 AC를 단일 절 EARS/GEARS 문장으로 재작성; (D2, major) REQ-TELEGRAM-030/033/034에 대한 정적 스크립트 검토 AC(AC-TELEGRAM-030s/033s/034s) 신설로 추적성 공백 해소; (D3, minor) AC-TELEGRAM-027a의 오류 메시지 판정 기준에서 퍼지 매치 제거; (D4, minor) REQ-TELEGRAM-031을 REQ-TELEGRAM-031/035로 분리(REQ-024~034 기존 순서 보존을 위해 035를 말미에 append). 상세는 spec.md HISTORY 0.1.1 행 참조.

## §F Phase 4 Mode Selection

- Input parameters: tier=M, scope=1 new file (`run_telegram_bot.bat`), domain count=1 (Windows batch scripting), file language mix=100% batch script (no Python/Go), concurrency benefit=LOW (single sequential file, no parallelizable sub-tasks).
- Mode evaluation: trivial — not selected (semantic content, not a typo fix); background — not selected (write task, needs to complete before user sees result); agent-team — RETIRED, not selectable; parallel — not selected (single domain, single file, no research fan-out value); workflow — not selected (scope is 1 file, far below the ~30-file mechanical-transform threshold); sub-agent — **selected** (default fallback; coding-heavy single-file task per Anthropic's coding-task parallelism caveat).
- Decision: sub-agent
- Justification: This SPEC adds exactly one new file with no research value in parallelizing and no mechanical bulk-transform shape, so Mode 5 (single sequential `Agent()` delegation to manager-develop) is the correct and only reasonable choice. Plan Audit Gate re-verification (Phase 1) already completed via a separate `plan-auditor` spawn (PASS, 0.87) prior to this mode-selection log entry.

## §E.2 Run-phase Evidence

| AC / Invariant | Actual Output | Status |
|---|---|---|
| AC-TELEGRAM-024a (정상 실행) | 정적 리뷰로 REQ-024/025/026/028/029 정합 확인(`cd /d "%~dp0"` → `chcp 65001` → venv 체크 → `.venv\Scripts\python.exe -m markdown_creat.telegram_bot` 무리다이렉트 호출 → `pause`). 실제 더블클릭 실행(long-polling blocking 특성상 자동화 에이전트가 끝까지 실행 불가)은 사용자의 수동 검증이 필요 — Gaps 참조. | PASS-WITH-DEBT (정적 검증만 완료, 런타임 실행은 사용자 수동 검증 대상) |
| AC-TELEGRAM-027a (venv 부재) | 스크래치 복사본을 `.moai/state/_verify_scratch/`(project root와 다른 위치, `.venv` 없음)에서 `cmd.exe`로 3회 실행(project root cwd에서 절대경로 호출 1회, 세 번째 위치인 `subdir`를 초기 cwd로 설정해 `call ..\...bat`로 호출 1회 포함). 매 회 봇 모듈 미호출·"[오류] 가상환경 .venv 를 찾을 수 없습니다" 평이한 언어 오류 출력·`pause`("Press any key to continue . . .") 도달·`exit=1`(0이 아닌 종료 코드) 확인. PATH에 `System32` 포함 시(정상 더블클릭 환경과 동일) `chcp 65001`이 정상 적용되어 한글 텍스트가 mojibake 없이 정확히 렌더링됨을 확인. | PASS |
| AC-TELEGRAM-027b (토큰 부재) | 정적 리뷰로 REQ-028/029 정합 확인 — venv 사전 점검 통과 후 봇 모듈 호출부에 출력 리다이렉트가 없어(grep 확인) 기존 `config.py`의 `MissingBotTokenError` 메시지가 가로채임 없이 그대로 노출됨. 실제 토큰 부재 상태의 실 프로세스 실행은 사용자의 수동 검증이 필요 — Gaps 참조. | PASS-WITH-DEBT (정적 검증만 완료) |
| AC-TELEGRAM-030s (bare `python` 미사용) | `grep -n "python" run_telegram_bot.bat` → 매치 3건 모두 `.venv\Scripts\python.exe`(1건은 exist 체크, 1건은 오류 안내 문구 내 사용자 안내용 `python -m venv .venv` 텍스트, 1건은 실제 호출부) — 실행 가능한 bare `python`/`python.exe` 호출은 0건. | PASS |
| AC-TELEGRAM-033s (OS 자동 시작 미등록) | `grep -ni "schtasks\|sc create\|reg add.*run\|HKCU.*Run\|HKLM.*Run" run_telegram_bot.bat` → 0 매치. | PASS |
| AC-TELEGRAM-034s (포그라운드 전용 실행) | `grep -ni "start /b\|start/b" run_telegram_bot.bat` → 0 매치. 작업 관리자를 통한 M5 실 프로세스 관찰(정상 실행 시나리오)은 사용자의 수동 검증이 필요 — Gaps 참조. | PASS-WITH-DEBT (정적 검증만 완료) |
| 실행 위치 독립성 (§D.1 엣지 케이스) | 3가지 서로 다른 초기 위치(project root cwd에서 절대경로 호출, project root cwd에서 스크래치 위치로 호출, `subdir`를 초기 cwd로 설정 후 상대경로 `call`)에서 동일하게 스크립트 자신의 파일 위치를 기준으로 venv 체크가 수행됨을 확인 — `cd /d "%~dp0"` 앵커링이 초기 cwd와 무관하게 정확히 동작함. | PASS (2가지 이상 실행 위치 검증 요건 충족) |
| PRESERVE 무결성 | `git diff --stat -- src/ pyproject.toml .env` → 빈 출력(변경 없음). | PASS |
| 기존 테스트 스위트 회귀 없음 | `pytest tests/test_telegram_bot.py tests/test_telegram_config.py tests/test_telegram_storage.py -v` → 37 passed in 8.97s. | PASS |
| 파일 인코딩 (BOM 없음) | 바이너리 검사로 BOM(`EF BB BF`) 부재 확인, CRLF 라인엔딩(23개 라인 전부 CRLF, LF 단독 없음) 확인. | PASS |

## §E.3 Run-phase Audit-Ready Signal

```yaml
run_complete_at: "2026-07-18T00:00:00+09:00"
run_commit_sha: "e47f1cb0"
run_status: "pass-with-debt"
ac_pass_count: 6
ac_fail_count: 0
ac_pass_with_debt_count: 3
preserve_list_post_run_count: 3  # src/markdown_creat/telegram_bot/, pyproject.toml, .env — all confirmed unmodified
l44_pre_commit_fetch: "n/a — Route A Hybrid Trunk main-direct, single-session, no parallel-session race detected"
l44_post_push_fetch: "confirmed synced — git rev-list --count --left-right origin/master...HEAD → 0 0"
new_warnings_or_lints_introduced: "n/a — .bat file is not a ruff/black/pytest target per plan.md §E"
cross_platform_build:
  applicable: false
  reason: "Windows-only .bat launcher; no Go/cross-platform build target"
total_run_phase_files: 5  # run_telegram_bot.bat (new) + spec.md/plan.md/acceptance.md/progress.md (frontmatter status transition only)
m1_to_mN_commit_strategy: "single M1 commit covering M1-M4 (UX wording + venv check + cwd anchor + bot invocation + pause) since scope is 1 new file; M5 manual-verification and M6 optional README mention are non-code milestones folded into the same run-phase report"
```

**Gaps (미검증)**: AC-TELEGRAM-024a's full runtime path (실제 더블클릭으로 봇이 long-polling을 시작하고 시작 로그가 콘솔에 표시되는 것) and AC-TELEGRAM-027b's full runtime path (실제 토큰 부재 상태에서 `MissingBotTokenError`가 실제로 발생·노출되는 것) were NOT executed end-to-end by manager-develop — both require an actual interactive Windows double-click session, and AC-024a in particular enters an indefinite long-polling blocking loop that cannot safely be run to completion by an automated agent. These two scenarios were verified via careful static line-by-line script review only (command, arguments, and absence of output redirection confirmed to match REQ-TELEGRAM-024/025/026/028/029 exactly). AC-TELEGRAM-034s's M5 Task-Manager observation (봇 프로세스가 `cmd.exe`의 자식 프로세스로 표시됨) was also not performed — requires the same real interactive session. acceptance.md's own Definition of Done designates these three items for manual human double-click verification; this is expected, not a shortfall.

## §E.4 Sync-phase Audit-Ready Signal

_<pending sync-phase>_
