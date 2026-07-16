"""Entry point: `python -m markdown_creat.telegram_bot`.

Manual execution only -- no auto-start/OS-service registration is provided
(spec.md SS Exclusions).
"""

from __future__ import annotations

import logging
import sys

from markdown_creat.telegram_bot.bot import run_polling
from markdown_creat.telegram_bot.config import MissingBotTokenError


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    try:
        run_polling()
    except MissingBotTokenError as exc:
        # Fail fast with a clear message, no traceback noise (REQ-TELEGRAM-003,
        # 015, AC-TELEGRAM-003a).
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
