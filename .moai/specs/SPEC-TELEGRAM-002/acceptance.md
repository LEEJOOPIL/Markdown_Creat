---
id: SPEC-TELEGRAM-002
title: "텔레그램 첨부파일 저장 경로 순회 취약점 수정 — 인수 기준"
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

# SPEC-TELEGRAM-002 — 인수 기준 (acceptance.md)

## §D. 인수 시나리오 (GEARS)

### AC-TELEGRAM-019a — 상위 디렉토리 이동 시퀀스 포함 파일명 무력화 (REQ-TELEGRAM-019, 020, 021)
- When the bot receives an attachment whose Telegram-provided filename contains `..` traversal sequences (e.g. `"../../../evil.txt"`), the bot shall save the attachment strictly under `<base_dir>/files/` using only the sanitized basename, and shall not create or write any file outside that directory.

### AC-TELEGRAM-019b — 절대 경로/드라이브 문자 형태 파일명 무력화 (REQ-TELEGRAM-019, 020, 021)
- When the bot receives an attachment whose filename is an absolute-path-like string (e.g. `"/etc/passwd"`) or a Windows drive-letter-prefixed path (e.g. `"C:\\Windows\\evil.txt"`), the bot shall discard the path prefix and drive component and shall save the attachment only under `<base_dir>/files/` using the sanitized basename.

### AC-TELEGRAM-019c — 정상 파일명 명명 규칙 회귀 없음 (REQ-TELEGRAM-022)
- When the bot receives an attachment with a legitimate filename containing no path separators (e.g. `"photo.jpg"`), the bot shall continue to save it as `<timestamp>_<message_id>_<filename>` exactly as before this fix, with no change in behavior for non-malicious inputs.

### AC-TELEGRAM-019d — 정제 후 빈 basename 폴백 (REQ-TELEGRAM-023)
- When the sanitized basename of a received filename is empty or resolves to a directory-reference-only string (e.g. the filename is exactly `".."` or `"."`), the bot shall fall back to a fixed placeholder filename so that the attachment save neither fails nor is silently dropped.

## §D.1 엣지 케이스 (Edge Cases)

- **혼합 구분자**: 파일명이 백슬래시 기반 순회를 사용하는 경우(예: `"..\\..\\evil.txt"`) — 호스트 OS가 POSIX이든 Windows이든 관계없이 `/`와 `\` 양쪽 구분자가 모두 정제 대상이어야 한다(plan.md §C).
- **서브디렉토리 형태의 상대 경로**: 파일명이 순회는 아니지만 서브디렉토리를 포함하는 경우(예: `"subdir/photo.jpg"`) — 기존 `save_attachment()`는 첨부파일을 항상 `files/` 아래 평평하게(flat) 저장하므로, 이 경우도 `photo.jpg`라는 basename으로 축약되어야 한다(서브디렉토리 생성 없음).
- **널 바이트 포함**: 파일명에 널 바이트(예: `"evil.txt\x00.jpg"`)가 포함된 극단적 케이스 — 정제 로직은 이런 입력에서도 처리되지 않은 예외로 봇 전체가 크래시하지 않아야 한다(§D.2 DoD의 회귀 없음 항목과 결합하여 검증).
- **`.`/`..`만으로 구성된 파일명**: AC-TELEGRAM-019d가 다루는 케이스 — 정제 결과가 빈 문자열이 되는 경우와 동일하게 폴백 파일명으로 처리된다.
- **한글 등 비ASCII 정상 파일명**: 경로 구분자가 없는 한 정제 로직이 문자 자체를 손상시키지 않아야 한다 — 기존 `test_telegram_storage.py`의 UTF-8 관련 테스트가 이 부분의 회귀를 간접적으로 감시한다.

## §D.2 품질 게이트 / Definition of Done

- [ ] Reproduction-First: **현재 취약한** `save_attachment()`를 대상으로 한 익스플로잇 재현 테스트가 작성되고, 수정 전 실제로 실패함이 확인되었다(RED).
- [ ] AC-TELEGRAM-019a, 019b, 019c, 019d 전 시나리오가 수정 후 통과한다(GREEN).
- [ ] 기존 `SPEC-TELEGRAM-001` 테스트 스위트(`tests/test_telegram_storage.py`, `tests/test_telegram_handlers.py`, `tests/test_telegram_dispatch.py`)가 회귀 없이 전부 통과한다.
- [ ] `storage.py` 테스트 커버리지가 85% 이상으로 유지된다(`quality.yaml` `constitution.test_coverage_target`).
- [ ] `ruff` 린트 무경고, `black` 포맷 준수.
- [ ] `save_attachment()`의 공개 함수 시그니처가 변경되지 않았다 — `handlers.py:68`, `:101`의 호출부가 수정되지 않았음을 `git diff --stat`로 확인한다.
- [ ] 신규 외부 의존성이 추가되지 않았다(`pyproject.toml` 변경 없음).
- [ ] REQ-TELEGRAM-019~023이 각각 최소 1개 테스트로 검증됨(추적성).
