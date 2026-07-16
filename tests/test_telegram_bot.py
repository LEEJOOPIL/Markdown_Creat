"""Tests for markdown_creat.telegram_bot.bot.

Covers REQ-TELEGRAM-001/013 (long polling only, no webhook),
REQ-TELEGRAM-003/015 (fail-fast on missing token before polling starts),
REQ-TELEGRAM-010/016 (API/network error logged, polling continues -- the
error handler must never itself raise).
"""

from __future__ import annotations

import asyncio
import logging

import pytest

from markdown_creat.telegram_bot.bot import build_application, on_error, run_polling
from markdown_creat.telegram_bot.config import MissingBotTokenError


class _FakeContext:
    def __init__(self, error: Exception):
        self.error = error


# ---------------------------------------------------------------------------
# M3 -- API/network error handling (REQ-TELEGRAM-010, 016)
# ---------------------------------------------------------------------------


def test_on_error_logs_the_error(caplog):
    fake_context = _FakeContext(RuntimeError("network unreachable"))

    with caplog.at_level(logging.ERROR):
        asyncio.run(on_error(update=None, context=fake_context))

    assert any("network unreachable" in str(record.message) for record in caplog.records)


def test_on_error_never_raises_so_polling_can_continue():
    """The error handler itself must swallow the error -- python-telegram-bot's
    polling loop only survives an error callback that does not itself raise."""
    fake_context = _FakeContext(ValueError("boom"))

    # Must complete without propagating -- this IS the assertion.
    asyncio.run(on_error(update=None, context=fake_context))


# ---------------------------------------------------------------------------
# M3 -- application construction registers the error handler
# ---------------------------------------------------------------------------


def test_build_application_registers_error_handler():
    application = build_application(token="123456:fake-token-for-app-construction")

    assert len(application.error_handlers) == 1


# ---------------------------------------------------------------------------
# M3 -- fail-fast before any polling attempt (REQ-TELEGRAM-003, 015, AC-TELEGRAM-003a)
# ---------------------------------------------------------------------------


def test_run_polling_fails_fast_when_token_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(MissingBotTokenError):
        run_polling(env_path=str(tmp_path / "missing.env"))
