"""Tests for markdown_creat.telegram_bot.__main__.

Covers REQ-TELEGRAM-003, REQ-TELEGRAM-015, AC-TELEGRAM-003a: the CLI entry point exits
cleanly (non-zero exit code, clear stderr message, no raw traceback) when
no bot token is configured.
"""

from __future__ import annotations

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
