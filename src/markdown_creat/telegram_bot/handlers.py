"""Message handler contracts for text/photo/document Telegram messages.

Input -> output contract (plan.md SS D M2): each `handle_*_message()`
function takes the message's decomposed fields (base_dir, message_id,
timestamp, sender, chat_context, plus type-specific payload) and returns
the `Path` of the saved `.md` note. Handlers are independent of the
`python-telegram-bot` `Update`/`Context` types so they can be unit tested
without a live bot -- `bot.py` adapts `Update` objects into these calls.

Extraction-failure fallback (REQ-TELEGRAM-005, REQ-TELEGRAM-011,
REQ-TELEGRAM-017, AC-TELEGRAM-004b): the original attachment is ALWAYS
saved first; OCR/PDF extraction failure never causes the message or the
original file to be lost -- only the note body records a failure note
instead of extracted text.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from markdown_creat.telegram_bot.extract import DocumentExtractionError
from markdown_creat.telegram_bot.extract import extract_pdf_text as extract_pdf_text
from markdown_creat.telegram_bot.ocr import ImageOcrError
from markdown_creat.telegram_bot.ocr import extract_image_text as extract_image_text
from markdown_creat.telegram_bot.storage import save_attachment, save_note

__all__ = [
    "handle_text_message",
    "handle_photo_message",
    "handle_document_message",
]

_NO_TEXT_EXTRACTED_NOTE = "(추출 텍스트 없음 / no text extracted)"
_OCR_FAILED_NOTE = "OCR extraction failed for this image; original file preserved above."
_PDF_EXTRACTION_FAILED_NOTE = (
    "PDF text extraction failed for this document; original file preserved above."
)


def handle_text_message(
    base_dir: str,
    message_id: int,
    timestamp: datetime,
    sender: str | None,
    chat_context: str | None,
    text: str,
) -> Path:
    """Save a plain-text message as a `.md` note (REQ-TELEGRAM-004, 009)."""
    return save_note(base_dir, timestamp, message_id, sender, chat_context, text)


def handle_photo_message(
    base_dir: str,
    message_id: int,
    timestamp: datetime,
    sender: str | None,
    chat_context: str | None,
    photo_bytes: bytes,
    filename: str,
) -> Path:
    """Save the original photo, OCR its text, and save a merged `.md` note.

    The original is always saved first (REQ-TELEGRAM-005). OCR failure
    (REQ-TELEGRAM-011) falls back to a failure note without losing the
    original or the message.
    """
    attachment_path = save_attachment(base_dir, timestamp, message_id, filename, photo_bytes)

    try:
        ocr_text = extract_image_text(str(attachment_path), lang="kor+eng")
        body = ocr_text if ocr_text else _NO_TEXT_EXTRACTED_NOTE
    except ImageOcrError:
        body = _OCR_FAILED_NOTE

    return save_note(
        base_dir,
        timestamp,
        message_id,
        sender,
        chat_context,
        body,
        attachment_paths=[str(attachment_path)],
    )


def handle_document_message(
    base_dir: str,
    message_id: int,
    timestamp: datetime,
    sender: str | None,
    chat_context: str | None,
    document_bytes: bytes,
    filename: str,
) -> Path:
    """Save the original document; extract PDF text when applicable.

    Non-PDF documents (`.txt`, `.docx`, ...) use the minimal scope decided
    in plan.md SS D M2: original saved + a type note, no text extraction.
    """
    attachment_path = save_attachment(base_dir, timestamp, message_id, filename, document_bytes)

    if filename.lower().endswith(".pdf"):
        try:
            body = extract_pdf_text(str(attachment_path))
        except DocumentExtractionError:
            body = _PDF_EXTRACTION_FAILED_NOTE
    else:
        body = f"Non-PDF attachment ({filename}); original saved, no text extraction performed."

    return save_note(
        base_dir,
        timestamp,
        message_id,
        sender,
        chat_context,
        body,
        attachment_paths=[str(attachment_path)],
    )
