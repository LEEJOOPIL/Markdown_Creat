"""Bot construction, long-polling entry point, and polling-loop resilience.

Long polling only (REQ-TELEGRAM-001, REQ-TELEGRAM-013 -- no webhook mode is
registered or supported). Token is resolved via `config.load_bot_token()`,
which fails fast (REQ-TELEGRAM-003, REQ-TELEGRAM-015) before any network
activity is attempted. API/network errors during polling are logged and
swallowed so the polling loop keeps running (REQ-TELEGRAM-010, REQ-TELEGRAM-016).
"""

from __future__ import annotations

import logging

from telegram.ext import Application, ContextTypes, MessageHandler, filters

from markdown_creat.telegram_bot.config import load_base_folder, load_bot_token, mask_secret
from markdown_creat.telegram_bot.dispatch import (
    on_document_message,
    on_photo_message,
    on_text_message,
)

logger = logging.getLogger(__name__)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log a Telegram API/network error without re-raising it.

    python-telegram-bot's polling loop only keeps running when the
    registered error handler itself does not raise
    (REQ-TELEGRAM-010, REQ-TELEGRAM-016).
    """
    logger.error(
        "Telegram API/network error while polling: %s", context.error, exc_info=context.error
    )


def build_application(token: str) -> Application:
    """Construct the `Application`, registering the shared error handler."""
    application = Application.builder().token(token).build()
    application.add_error_handler(on_error)
    return application


def register_handlers(application: Application, base_dir: str) -> None:
    """Register the text/photo/document message handlers against `base_dir`."""

    async def _text_callback(update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await on_text_message(update, context, base_dir)

    async def _photo_callback(update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await on_photo_message(update, context, base_dir)

    async def _document_callback(update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await on_document_message(update, context, base_dir)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _text_callback))
    application.add_handler(MessageHandler(filters.PHOTO, _photo_callback))
    application.add_handler(MessageHandler(filters.Document.ALL, _document_callback))


def run_polling(env_path: str = ".env") -> None:
    """Load configuration, build the application, and start long polling.

    Raises:
        MissingBotTokenError: No token is configured (fail-fast before any
            polling attempt -- REQ-TELEGRAM-003, REQ-TELEGRAM-015, AC-TELEGRAM-003a).
    """
    token = load_bot_token(env_path)
    base_dir = load_base_folder(env_path)

    logger.info("Starting Telegram bot (base folder=%s, token=%s)", base_dir, mask_secret(token))

    application = build_application(token)
    register_handlers(application, base_dir)
    application.run_polling()
