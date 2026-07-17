"""Tests for markdown_creat.telegram_bot.__main__.

Covers REQ-TELEGRAM-003, REQ-TELEGRAM-015, AC-TELEGRAM-003a: the CLI entry point exits
cleanly (non-zero exit code, clear stderr message, no raw traceback) when
no bot token is configured.
"""

from __future__ import annotations

import logging

from markdown_creat.telegram_bot.__main__ import main


def test_main_returns_nonzero_and_prints_clear_error_when_token_missing(
    monkeypatch, tmp_path, capsys
):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)  # no .env file present in this empty tmp dir

    exit_code = main()

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "TELEGRAM_BOT_TOKEN" in captured.err


def test_main_suppresses_httpx_info_logging_to_prevent_token_leak(
    monkeypatch, tmp_path
):
    """main()은 httpx 로거를 WARNING으로 낮춰 봇 토큰이 로그에 노출되지 않게 한다.

    httpx는 요청 URL 전체를 INFO 레벨로 기록하고 python-telegram-bot은 그 URL에
    봇 토큰을 그대로 담으므로, 억제하지 않으면 raw 토큰이 로그에 남는다
    (REQ-TELEGRAM-012 위반). AC-TELEGRAM-005a의 회귀 가드이며, __main__.py의
    httpx 로거 억제 한 줄(commit 1d38743)이 제거되면 이 테스트가 실패한다.
    """
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)  # 빈 tmp 디렉터리 -> .env 없음

    # 프로세스 전역 logging 상태를 NOTSET(0)으로 리셋해, WARNING 설정이 선행
    # 테스트가 아니라 main() 자체에서 일어났음을 증명한다(vacuous pass 방지).
    logging.getLogger("httpx").setLevel(logging.NOTSET)

    # 토큰 미설정 -> main()은 httpx 억제 줄을 먼저 실행한 뒤 run_polling()에서
    # MissingBotTokenError로 실패해 1을 반환한다(억제 줄은 항상 먼저 실행됨).
    exit_code = main()

    assert exit_code == 1
    # getEffectiveLevel()은 조상(root) 설정에 의존해 테스트 실행 순서에 취약하다.
    # 반면 httpx 로거의 .level 속성은 억제 줄이 해당 로거에 직접 설정하는 값이라
    # root 상태와 무관하게 결정적이므로, .level 을 직접 검사한다.
    assert logging.getLogger("httpx").level == logging.WARNING
