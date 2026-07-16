"""Tests for markdown_creat.telegram_bot.config.

Covers REQ-TELEGRAM-002 (env var or gitignored `.env` token source),
REQ-TELEGRAM-003/015 (fail-fast on missing token), REQ-TELEGRAM-012/014 (no
secret hardcoding/logging), REQ-TELEGRAM-018 (configurable base folder).
"""

from __future__ import annotations

import inspect

import pytest

from markdown_creat.telegram_bot.config import (
    DEFAULT_BASE_FOLDER,
    MissingBotTokenError,
    load_base_folder,
    load_bot_token,
    mask_secret,
)

# ---------------------------------------------------------------------------
# M3 -- token source + priority (REQ-TELEGRAM-002)
# ---------------------------------------------------------------------------


def test_load_bot_token_reads_from_environment_variable(monkeypatch, tmp_path):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "env-token-123")

    result = load_bot_token(env_path=str(tmp_path / "missing.env"))

    assert result == "env-token-123"


def test_load_bot_token_reads_from_dotenv_file_when_env_var_absent(monkeypatch, tmp_path):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=dotenv-token-456\n", encoding="utf-8")

    result = load_bot_token(env_path=str(env_file))

    assert result == "dotenv-token-456"


def test_load_bot_token_environment_variable_takes_priority_over_dotenv(monkeypatch, tmp_path):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "env-wins")
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=dotenv-loses\n", encoding="utf-8")

    result = load_bot_token(env_path=str(env_file))

    assert result == "env-wins"


def test_load_bot_token_ignores_comments_and_blank_lines_in_dotenv(monkeypatch, tmp_path):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment line\n\nTELEGRAM_BOT_TOKEN=quoted-token\n",
        encoding="utf-8",
    )

    result = load_bot_token(env_path=str(env_file))

    assert result == "quoted-token"


# ---------------------------------------------------------------------------
# M3 -- fail-fast on missing token (REQ-TELEGRAM-003, 015, AC-TELEGRAM-003a)
# ---------------------------------------------------------------------------


def test_load_bot_token_raises_when_no_token_configured_anywhere(monkeypatch, tmp_path):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(MissingBotTokenError) as exc_info:
        load_bot_token(env_path=str(tmp_path / "missing.env"))

    # Error names the missing configuration clearly (AC-TELEGRAM-003a).
    assert "TELEGRAM_BOT_TOKEN" in str(exc_info.value)


def test_load_bot_token_raises_when_dotenv_exists_but_lacks_the_key(monkeypatch, tmp_path):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("SOME_OTHER_KEY=value\n", encoding="utf-8")

    with pytest.raises(MissingBotTokenError):
        load_bot_token(env_path=str(env_file))


# ---------------------------------------------------------------------------
# M3 -- configurable base folder (REQ-TELEGRAM-018, AC-TELEGRAM-001b)
# ---------------------------------------------------------------------------


def test_load_base_folder_defaults_to_telegram_notes(monkeypatch, tmp_path):
    monkeypatch.delenv("TELEGRAM_NOTES_BASE_DIR", raising=False)

    result = load_base_folder(env_path=str(tmp_path / "missing.env"))

    assert result == DEFAULT_BASE_FOLDER


def test_load_base_folder_uses_configured_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("TELEGRAM_NOTES_BASE_DIR", "my-custom-notes")

    result = load_base_folder(env_path=str(tmp_path / "missing.env"))

    assert result == "my-custom-notes"


def test_load_base_folder_uses_configured_dotenv_value(monkeypatch, tmp_path):
    monkeypatch.delenv("TELEGRAM_NOTES_BASE_DIR", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_NOTES_BASE_DIR=dotenv-notes\n", encoding="utf-8")

    result = load_base_folder(env_path=str(env_file))

    assert result == "dotenv-notes"


# ---------------------------------------------------------------------------
# M3 -- secret discipline (REQ-TELEGRAM-012, 014, AC-TELEGRAM-005a/005b)
# ---------------------------------------------------------------------------


def test_mask_secret_never_exposes_full_token():
    masked = mask_secret("123456:ABCDEF-super-secret-token")

    assert "super-secret-token" not in masked
    assert masked != "123456:ABCDEF-super-secret-token"


def test_mask_secret_handles_short_values_without_leaking():
    masked = mask_secret("abc")

    assert "abc" not in masked


def test_bot_token_never_referenced_by_handlers_storage_ocr_extract_modules():
    """Static guard for REQ-TELEGRAM-012: the token must flow only through
    config.py -> bot.py, never into the modules that write `.md` files or
    logs (handlers/storage/ocr/extract)."""
    from markdown_creat.telegram_bot import extract, handlers, ocr, storage

    for module in (handlers, storage, ocr, extract):
        source = inspect.getsource(module)
        assert "TELEGRAM_BOT_TOKEN" not in source
        assert "bot_token" not in source.lower()
