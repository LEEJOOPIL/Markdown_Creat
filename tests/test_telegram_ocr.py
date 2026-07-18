"""Tests for markdown_creat.telegram_bot.ocr.

Covers REQ-TELEGRAM-007: image OCR text extraction via pytesseract. As of
SPEC-OCR-001 (REQ-OCR-013, 014), `telegram_bot/ocr.py` is a thin re-export
of the shared core `markdown_creat.ocr` module -- the actual `pytesseract`
call now lives there, so the mock target below patches
`markdown_creat.ocr.pytesseract.image_to_string` rather than a
`telegram_bot.ocr`-local name. Tesseract itself remains an external system
dependency isolated from tests per acceptance.md SS D.2.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from markdown_creat.telegram_bot.ocr import ImageOcrError, extract_image_text


def test_extract_image_text_returns_stripped_ocr_result():
    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        return_value="  Hello from OCR  \n",
    ):
        result = extract_image_text("photo.jpg")

    assert result == "Hello from OCR"


def test_extract_image_text_supports_korean_utf8_content():
    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        return_value="한글 OCR 결과",
    ):
        result = extract_image_text("photo.jpg")

    assert result == "한글 OCR 결과"


def test_extract_image_text_returns_empty_string_when_no_text_found():
    """Edge case (acceptance.md SS D.1): text-less image -> empty string,
    not an error. The caller (handlers.py) is responsible for the
    "no extracted text" note."""
    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        return_value="",
    ):
        result = extract_image_text("photo.jpg")

    assert result == ""


def test_extract_image_text_wraps_tesseract_failure():
    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        side_effect=RuntimeError("tesseract is not installed"),
    ):
        with pytest.raises(ImageOcrError):
            extract_image_text("photo.jpg")
