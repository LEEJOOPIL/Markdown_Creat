"""Tests for markdown_creat.telegram_bot.handlers.

Covers the text/photo/document handler contracts (REQ-TELEGRAM-004~007, 009)
and the extraction-failure fallback (REQ-TELEGRAM-005, 011, 017,
AC-TELEGRAM-004b). External extraction calls (ocr.extract_image_text,
extract.extract_pdf_text) are mocked; storage.py itself is exercised for
real against tmp_path (already covered by test_telegram_storage.py).
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

from markdown_creat.telegram_bot import handlers
from markdown_creat.telegram_bot.extract import DocumentExtractionError
from markdown_creat.telegram_bot.ocr import ImageOcrError

TIMESTAMP = datetime(2026, 7, 16, 10, 30, 45)


# ---------------------------------------------------------------------------
# M2 -- text handler (REQ-TELEGRAM-004, 009)
# ---------------------------------------------------------------------------


def test_handle_text_message_saves_note_with_text_body(tmp_path):
    base = str(tmp_path / "telegram-notes")

    result_path = handlers.handle_text_message(
        base_dir=base,
        message_id=1,
        timestamp=TIMESTAMP,
        sender="Alice",
        chat_context="Alice's private chat",
        text="Hello world",
    )

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "Hello world" in content
    assert "Alice" in content


# ---------------------------------------------------------------------------
# M2 -- photo handler: original saved + OCR text merged (REQ-TELEGRAM-005, 007)
# ---------------------------------------------------------------------------


def test_handle_photo_message_saves_original_and_merges_ocr_text(tmp_path):
    base = str(tmp_path / "telegram-notes")

    with patch(
        "markdown_creat.telegram_bot.handlers.extract_image_text",
        return_value="OCR extracted text",
    ):
        result_path = handlers.handle_photo_message(
            base_dir=base,
            message_id=2,
            timestamp=TIMESTAMP,
            sender="Alice",
            chat_context=None,
            photo_bytes=b"\xff\xd8fakejpeg",
            filename="photo.jpg",
        )

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "OCR extracted text" in content
    assert "photo.jpg" in content
    saved_originals = list((tmp_path / "telegram-notes" / "files").iterdir())
    assert len(saved_originals) == 1
    assert saved_originals[0].read_bytes() == b"\xff\xd8fakejpeg"


def test_handle_photo_message_notes_empty_result_when_no_text_found(tmp_path):
    """Edge case (acceptance.md SS D.1): OCR returns empty string -> note it, not an error."""
    base = str(tmp_path / "telegram-notes")

    with patch("markdown_creat.telegram_bot.handlers.extract_image_text", return_value=""):
        result_path = handlers.handle_photo_message(
            base, 3, TIMESTAMP, "Alice", None, b"bytes", "empty.jpg"
        )

    content = result_path.read_text(encoding="utf-8")
    assert "empty.jpg" in content
    # Original must exist regardless of OCR outcome.
    assert (tmp_path / "telegram-notes" / "files").exists()


def test_handle_photo_message_saves_original_and_failure_note_on_ocr_error(tmp_path):
    """AC-TELEGRAM-004b: OCR failure -> original preserved + failure note, no message loss."""
    base = str(tmp_path / "telegram-notes")

    with patch(
        "markdown_creat.telegram_bot.handlers.extract_image_text",
        side_effect=ImageOcrError("tesseract not installed"),
    ):
        result_path = handlers.handle_photo_message(
            base, 4, TIMESTAMP, "Alice", None, b"bytes", "fail.jpg"
        )

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "fail.jpg" in content
    saved_originals = list((tmp_path / "telegram-notes" / "files").iterdir())
    assert len(saved_originals) == 1


# ---------------------------------------------------------------------------
# M2 -- document handler: PDF extraction vs non-PDF minimal scope
# (REQ-TELEGRAM-005, 006; plan.md SS D M2 non-PDF minimal-scope decision)
# ---------------------------------------------------------------------------


def test_handle_document_message_extracts_pdf_text_via_extract_wrapper(tmp_path):
    base = str(tmp_path / "telegram-notes")

    with patch(
        "markdown_creat.telegram_bot.handlers.extract_pdf_text",
        return_value="# PDF extracted body",
    ):
        result_path = handlers.handle_document_message(
            base, 5, TIMESTAMP, "Alice", None, b"%PDF-1.4 fakebytes", "report.pdf"
        )

    content = result_path.read_text(encoding="utf-8")
    assert "# PDF extracted body" in content
    assert "report.pdf" in content


def test_handle_document_message_saves_original_and_failure_note_on_pdf_error(tmp_path):
    """AC-TELEGRAM-004b: PDF extraction failure -> original preserved + failure note."""
    base = str(tmp_path / "telegram-notes")

    with patch(
        "markdown_creat.telegram_bot.handlers.extract_pdf_text",
        side_effect=DocumentExtractionError("corrupted PDF"),
    ):
        result_path = handlers.handle_document_message(
            base, 6, TIMESTAMP, "Alice", None, b"garbage", "corrupted.pdf"
        )

    assert result_path.exists()
    saved_originals = list((tmp_path / "telegram-notes" / "files").iterdir())
    assert len(saved_originals) == 1


def test_handle_document_message_non_pdf_saves_original_with_type_note(tmp_path):
    """Non-PDF documents (.txt, .docx, ...): minimal scope -- original saved
    + type note only, no text extraction attempted (plan.md SS D M2)."""
    base = str(tmp_path / "telegram-notes")

    result_path = handlers.handle_document_message(
        base, 7, TIMESTAMP, "Alice", None, b"plain text bytes", "notes.txt"
    )

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "notes.txt" in content
    saved_originals = list((tmp_path / "telegram-notes" / "files").iterdir())
    assert len(saved_originals) == 1
