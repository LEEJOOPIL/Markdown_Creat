"""Tests for markdown_creat.ocr -- the shared core OCR module.

Covers REQ-OCR-001~008: image OCR text extraction and PDF page-image OCR
extraction via pytesseract, with English/Korean language parameter support.

`pytesseract` is mocked (external system dependency, per spec.md SS C).
PyMuPDF page rendering (`get_pixmap()`) is exercised for real against small
in-memory PDFs built with `fitz` itself, matching the strategy already used
in test_pdf_to_markdown.py -- PyMuPDF is the dependency under test here, not
an external system.
"""

from __future__ import annotations

from unittest.mock import patch

import fitz
import pytest

from markdown_creat.ocr import OcrError, extract_image_text, extract_pdf_text_via_ocr


def make_pdf(path: str, page_count: int = 1) -> None:
    """Create a minimal valid PDF at `path` with `page_count` blank pages.

    Page content is irrelevant here -- `pytesseract.image_to_string` is
    mocked, so only a renderable page (for `get_pixmap()`) is needed.
    """
    doc = fitz.open()
    for _ in range(page_count):
        doc.new_page(width=595, height=842)
    doc.save(path)
    doc.close()


# ---------------------------------------------------------------------------
# M1 -- extract_image_text: success / empty / engine-error paths
# (AC-OCR-001a, AC-OCR-001b, AC-OCR-001c)
# ---------------------------------------------------------------------------


def test_extract_image_text_returns_ocr_result():
    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        return_value="  Hello from OCR  \n",
    ):
        result = extract_image_text("photo.jpg")

    assert result == "Hello from OCR"


def test_extract_image_text_returns_empty_string_when_no_text_found():
    """Edge case (REQ-OCR-002): text-less image -> empty string, not an error."""
    with patch("markdown_creat.ocr.pytesseract.image_to_string", return_value=""):
        result = extract_image_text("photo.jpg")

    assert result == ""


def test_extract_image_text_wraps_tesseract_engine_failure():
    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        side_effect=RuntimeError("tesseract is not installed"),
    ):
        with pytest.raises(OcrError):
            extract_image_text("photo.jpg")


# ---------------------------------------------------------------------------
# M1 -- multilingual support (AC-OCR-003a, AC-OCR-003b, AC-OCR-003c)
# ---------------------------------------------------------------------------


def test_extract_image_text_defaults_to_english_when_lang_not_given():
    with patch("markdown_creat.ocr.pytesseract.image_to_string", return_value="text") as mock_ocr:
        extract_image_text("photo.jpg")

    mock_ocr.assert_called_once_with("photo.jpg", lang="eng")


@pytest.mark.parametrize("lang", ["kor", "kor+eng"])
def test_extract_image_text_passes_through_korean_lang_parameter(lang):
    with patch("markdown_creat.ocr.pytesseract.image_to_string", return_value="한글") as mock_ocr:
        result = extract_image_text("photo.jpg", lang=lang)

    mock_ocr.assert_called_once_with("photo.jpg", lang=lang)
    assert result == "한글"


def test_extract_image_text_raises_clear_error_on_missing_language_pack():
    """REQ-OCR-008: missing traineddata -> identifiable OcrError, never a
    silent fallback to English or an empty result."""
    missing_pack_message = "Failed loading language 'kor'"
    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        side_effect=RuntimeError(missing_pack_message),
    ):
        with pytest.raises(OcrError, match="kor"):
            extract_image_text("photo.jpg", lang="kor")


# ---------------------------------------------------------------------------
# M2 -- extract_pdf_text_via_ocr: page rendering + OCR merge
# (AC-OCR-002a, AC-OCR-002b)
# ---------------------------------------------------------------------------


def test_extract_pdf_text_via_ocr_merges_pages_in_order(tmp_path):
    pdf_path = tmp_path / "scanned.pdf"
    make_pdf(str(pdf_path), page_count=2)

    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        side_effect=["Page one text", "Page two text"],
    ):
        result = extract_pdf_text_via_ocr(str(pdf_path))

    assert result.index("Page one text") < result.index("Page two text")


def test_extract_pdf_text_via_ocr_supports_korean_lang_parameter(tmp_path):
    pdf_path = tmp_path / "scanned-kor.pdf"
    make_pdf(str(pdf_path), page_count=1)

    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        return_value="한글 텍스트",
    ) as mock_ocr:
        result = extract_pdf_text_via_ocr(str(pdf_path), lang="kor+eng")

    assert result == "한글 텍스트"
    _, kwargs = mock_ocr.call_args
    assert kwargs.get("lang") == "kor+eng"


def test_extract_pdf_text_via_ocr_raises_ocr_error_when_pdf_cannot_be_opened(tmp_path):
    missing_path = tmp_path / "does-not-exist.pdf"

    with pytest.raises(OcrError):
        extract_pdf_text_via_ocr(str(missing_path))


def test_extract_pdf_text_via_ocr_raises_ocr_error_when_page_ocr_fails(tmp_path):
    pdf_path = tmp_path / "scanned-fail.pdf"
    make_pdf(str(pdf_path), page_count=1)

    with patch(
        "markdown_creat.ocr.pytesseract.image_to_string",
        side_effect=RuntimeError("tesseract crashed"),
    ):
        with pytest.raises(OcrError):
            extract_pdf_text_via_ocr(str(pdf_path))


def test_extract_pdf_text_via_ocr_raises_ocr_error_when_page_render_fails(tmp_path):
    pdf_path = tmp_path / "scanned-render-fail.pdf"
    make_pdf(str(pdf_path), page_count=1)

    with patch("fitz.Page.get_pixmap", side_effect=RuntimeError("render crashed")):
        with pytest.raises(OcrError):
            extract_pdf_text_via_ocr(str(pdf_path))
