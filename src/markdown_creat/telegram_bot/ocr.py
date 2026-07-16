"""Extract text from photo (image) attachments via OCR (REQ-TELEGRAM-007).

Uses Tesseract OCR through the `pytesseract` wrapper. This scope is new to
`markdown_creat` -- SPEC-PDF-001 explicitly excludes image OCR.
"""

from __future__ import annotations

import pytesseract

__all__ = ["extract_image_text", "ImageOcrError"]


class ImageOcrError(Exception):
    """Raised when OCR extraction fails (e.g. Tesseract not installed)."""


def extract_image_text(image_path: str) -> str:
    """Return the OCR-extracted text for the image at `image_path`.

    Returns an empty string when the image contains no recognizable text
    (not an error -- acceptance.md SS D.1 edge case).

    Raises:
        ImageOcrError: The Tesseract engine is unavailable or OCR failed
            for another reason (REQ-TELEGRAM-011).
    """
    try:
        # Broad except: pytesseract/Tesseract can raise a variety of
        # exception types (missing binary, unreadable image, engine
        # crash) that must all funnel into the same REQ-TELEGRAM-011
        # extraction-failure fallback in handlers.py.
        text = pytesseract.image_to_string(image_path)
    except Exception as exc:  # noqa: BLE001
        raise ImageOcrError(f"OCR extraction failed: {exc}") from exc

    return text.strip()
