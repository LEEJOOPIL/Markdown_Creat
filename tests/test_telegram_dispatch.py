"""Tests for markdown_creat.telegram_bot.dispatch.

Covers the Update -> handlers.py adapter layer end-to-end (REQ-TELEGRAM-004~007,
009): field extraction (sender, chat context, timestamp), attachment download,
and delegation into the real storage layer. Telegram file-download I/O and
OCR/PDF extraction are mocked; storage.py runs for real against tmp_path.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from markdown_creat.telegram_bot.dispatch import (
    on_document_message,
    on_photo_message,
    on_text_message,
)

TIMESTAMP = datetime(2026, 7, 16, 10, 30, 45, tzinfo=timezone.utc)


def _make_update(*, text=None, photo=None, document=None, sender_name="Alice", chat_title=None):
    update = MagicMock()
    update.message.message_id = 1
    update.message.date = TIMESTAMP
    update.message.text = text
    update.message.photo = photo
    update.message.document = document

    update.effective_user = MagicMock(full_name=sender_name, username="alice123")
    update.effective_chat = MagicMock(title=chat_title, username=None, id=999)
    return update


# ---------------------------------------------------------------------------
# M5 -- text message adapter (REQ-TELEGRAM-004, 009)
# ---------------------------------------------------------------------------


def test_on_text_message_saves_note_with_sender_and_stripped_timestamp(tmp_path):
    base_dir = str(tmp_path / "telegram-notes")
    update = _make_update(text="Hello world", chat_title="My Chat")

    asyncio.run(on_text_message(update, context=None, base_dir=base_dir))

    saved = list((tmp_path / "telegram-notes" / "2026-07-16").iterdir())
    assert len(saved) == 1
    content = saved[0].read_text(encoding="utf-8")
    assert "Hello world" in content
    assert "Alice" in content
    assert "My Chat" in content


def test_on_text_message_falls_back_to_username_when_full_name_absent(tmp_path):
    base_dir = str(tmp_path / "telegram-notes")
    update = _make_update(text="Hi", sender_name=None)
    update.effective_user.full_name = None
    update.effective_user.username = "just_a_username"

    asyncio.run(on_text_message(update, context=None, base_dir=base_dir))

    saved = list((tmp_path / "telegram-notes" / "2026-07-16").iterdir())
    content = saved[0].read_text(encoding="utf-8")
    assert "just_a_username" in content


def test_on_text_message_handles_missing_user_and_chat_context(tmp_path):
    """Defensive edge case: effective_user/effective_chat can be None."""
    base_dir = str(tmp_path / "telegram-notes")
    update = _make_update(text="Hi")
    update.effective_user = None
    update.effective_chat = None

    asyncio.run(on_text_message(update, context=None, base_dir=base_dir))

    saved = list((tmp_path / "telegram-notes" / "2026-07-16").iterdir())
    content = saved[0].read_text(encoding="utf-8")
    assert "Hi" in content


# ---------------------------------------------------------------------------
# M5 -- photo message adapter (REQ-TELEGRAM-005, 007)
# ---------------------------------------------------------------------------


def test_on_photo_message_downloads_highest_resolution_photo_and_saves_note(tmp_path):
    base_dir = str(tmp_path / "telegram-notes")

    small_photo = MagicMock(file_unique_id="small")
    large_photo = MagicMock(file_unique_id="large")
    telegram_file = MagicMock()
    telegram_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"photobytes"))
    large_photo.get_file = AsyncMock(return_value=telegram_file)

    update = _make_update(photo=[small_photo, large_photo])

    with patch(
        "markdown_creat.telegram_bot.handlers.extract_image_text",
        return_value="OCR text",
    ):
        asyncio.run(on_photo_message(update, context=None, base_dir=base_dir))

    saved_files = list((tmp_path / "telegram-notes" / "files").iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == b"photobytes"
    assert saved_files[0].name.endswith("large.jpg")


# ---------------------------------------------------------------------------
# M5 -- document message adapter (REQ-TELEGRAM-005, 006)
# ---------------------------------------------------------------------------


def test_on_document_message_downloads_and_extracts_pdf_text(tmp_path):
    base_dir = str(tmp_path / "telegram-notes")

    document = MagicMock(file_name="report.pdf", file_unique_id="doc123")
    telegram_file = MagicMock()
    telegram_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"%PDF-1.4 bytes"))
    document.get_file = AsyncMock(return_value=telegram_file)

    update = _make_update(document=document)

    with patch(
        "markdown_creat.telegram_bot.handlers.extract_pdf_text",
        return_value="# extracted",
    ):
        asyncio.run(on_document_message(update, context=None, base_dir=base_dir))

    saved_files = list((tmp_path / "telegram-notes" / "files").iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].name.endswith("report.pdf")

    saved_notes = list((tmp_path / "telegram-notes" / "2026-07-16").iterdir())
    content = saved_notes[0].read_text(encoding="utf-8")
    assert "# extracted" in content


def test_on_document_message_uses_file_unique_id_when_filename_missing(tmp_path):
    base_dir = str(tmp_path / "telegram-notes")

    document = MagicMock(file_name=None, file_unique_id="fallback-id")
    telegram_file = MagicMock()
    telegram_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"bytes"))
    document.get_file = AsyncMock(return_value=telegram_file)

    update = _make_update(document=document)

    asyncio.run(on_document_message(update, context=None, base_dir=base_dir))

    saved_files = list((tmp_path / "telegram-notes" / "files").iterdir())
    assert any("fallback-id" in f.name for f in saved_files)
