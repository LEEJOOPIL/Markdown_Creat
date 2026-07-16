"""Adapt python-telegram-bot `Update` objects into calls against the pure,
bot-library-independent `handlers.py` functions (REQ-TELEGRAM-004~007).

This module is the sole place `python-telegram-bot`'s `Update`/`Context`
types are touched -- `handlers.py` itself has no dependency on the bot
library, which keeps it unit-testable without a live bot connection.
"""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from markdown_creat.telegram_bot.handlers import (
    handle_document_message,
    handle_photo_message,
    handle_text_message,
)

__all__ = ["on_text_message", "on_photo_message", "on_document_message"]


def _sender_name(update: Update) -> str | None:
    user = update.effective_user
    if user is None:
        return None
    return user.full_name or user.username


def _chat_context(update: Update) -> str | None:
    chat = update.effective_chat
    if chat is None:
        return None
    return chat.title or chat.username or str(chat.id)


async def on_text_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, base_dir: str
) -> None:
    """Handle a plain-text message (REQ-TELEGRAM-004)."""
    message = update.message
    handle_text_message(
        base_dir=base_dir,
        message_id=message.message_id,
        timestamp=message.date.replace(tzinfo=None),
        sender=_sender_name(update),
        chat_context=_chat_context(update),
        text=message.text,
    )


async def on_photo_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, base_dir: str
) -> None:
    """Handle a photo (image) message (REQ-TELEGRAM-005, 007)."""
    message = update.message
    photo = message.photo[-1]  # last entry = highest resolution
    telegram_file = await photo.get_file()
    photo_bytes = bytes(await telegram_file.download_as_bytearray())
    filename = f"{photo.file_unique_id}.jpg"

    handle_photo_message(
        base_dir=base_dir,
        message_id=message.message_id,
        timestamp=message.date.replace(tzinfo=None),
        sender=_sender_name(update),
        chat_context=_chat_context(update),
        photo_bytes=photo_bytes,
        filename=filename,
    )


async def on_document_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, base_dir: str
) -> None:
    """Handle a document (PDF or other file) message (REQ-TELEGRAM-005, 006)."""
    message = update.message
    document = message.document
    telegram_file = await document.get_file()
    document_bytes = bytes(await telegram_file.download_as_bytearray())
    filename = document.file_name or document.file_unique_id

    handle_document_message(
        base_dir=base_dir,
        message_id=message.message_id,
        timestamp=message.date.replace(tzinfo=None),
        sender=_sender_name(update),
        chat_context=_chat_context(update),
        document_bytes=document_bytes,
        filename=filename,
    )
