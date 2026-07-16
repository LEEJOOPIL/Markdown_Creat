"""Bot configuration: token loading (fail-fast) and base-folder selection.

Token source priority (plan.md SS D M3 decision): the `TELEGRAM_BOT_TOKEN`
environment variable always wins over a value in a gitignored `.env` file.
When neither is set, `load_bot_token()` raises `MissingBotTokenError`
immediately (REQ-TELEGRAM-003, REQ-TELEGRAM-015 -- fail fast, never hang silently).

Secret discipline (REQ-TELEGRAM-012, REQ-TELEGRAM-014): the token itself is never
returned in a masked/loggable form by this module's own log-facing helper,
`mask_secret()`. Callers (bot.py) MUST use `mask_secret()` for any
startup log line that would otherwise include the token.
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = [
    "DEFAULT_BASE_FOLDER",
    "MissingBotTokenError",
    "load_bot_token",
    "load_base_folder",
    "mask_secret",
]

DEFAULT_BASE_FOLDER = "telegram-notes"
_ENV_FILE_NAME = ".env"
_TOKEN_ENV_VAR = "TELEGRAM_BOT_TOKEN"
_BASE_FOLDER_ENV_VAR = "TELEGRAM_NOTES_BASE_DIR"


class MissingBotTokenError(Exception):
    """Raised when no bot token is configured anywhere (fail-fast)."""


def _read_dotenv(env_path: str | os.PathLike[str]) -> dict[str, str]:
    """Parse a minimal `KEY=VALUE` `.env` file; missing file -> empty dict."""
    path = Path(env_path)
    if not path.is_file():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_bot_token(env_path: str | os.PathLike[str] = _ENV_FILE_NAME) -> str:
    """Return the bot token from the environment or a `.env` file.

    Raises:
        MissingBotTokenError: Neither the `TELEGRAM_BOT_TOKEN` environment
            variable nor the `.env` file at `env_path` provides a token.
    """
    token = os.environ.get(_TOKEN_ENV_VAR)
    if token:
        return token

    token = _read_dotenv(env_path).get(_TOKEN_ENV_VAR)
    if token:
        return token

    raise MissingBotTokenError(
        f"{_TOKEN_ENV_VAR} is not set. Set it as an environment variable "
        f"or in a gitignored .env file at the project root."
    )


def load_base_folder(env_path: str | os.PathLike[str] = _ENV_FILE_NAME) -> str:
    """Return the configured notes base folder, or `DEFAULT_BASE_FOLDER`."""
    base_folder = os.environ.get(_BASE_FOLDER_ENV_VAR)
    if base_folder:
        return base_folder

    base_folder = _read_dotenv(env_path).get(_BASE_FOLDER_ENV_VAR)
    if base_folder:
        return base_folder

    return DEFAULT_BASE_FOLDER


def mask_secret(value: str) -> str:
    """Return a masked representation of `value` safe for logs (REQ-TELEGRAM-012)."""
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
