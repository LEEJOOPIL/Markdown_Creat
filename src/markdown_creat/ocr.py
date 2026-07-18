"""Shared core OCR module -- image and PDF-page text extraction (REQ-OCR-001~008).

Generalizes the image OCR logic formerly private to
`telegram_bot/ocr.py` (SPEC-TELEGRAM-001) into a top-level shared module so
the Telegram bot, the PDF pipeline, and future features can all reuse it
(spec.md SS A decision #1). Adds PDF page-image OCR extraction and
English/Korean language parameter support (spec.md SS A decisions #2/#3).

This module does NOT call `pdf_to_markdown()` -- the dependency direction is
the reverse (`pdf_to_markdown.py` -> `extract_pdf_text_via_ocr()`), owned by
a future SPEC-PDF-001 amendment (spec.md SS 범위 경계).
"""

from __future__ import annotations

import os
import tempfile

import fitz
import pytesseract

__all__ = ["extract_image_text", "extract_pdf_text_via_ocr", "OcrError"]


class OcrError(Exception):
    """Raised when OCR extraction fails.

    Covers: the Tesseract engine itself failing (not installed, execution
    error), a missing language pack (REQ-OCR-008), or PDF page rendering /
    page-image OCR failure (REQ-OCR-005).
    """


def extract_image_text(image_path: str, lang: str = "eng") -> str:
    """Return the OCR-extracted text for the image at `image_path`.

    Args:
        image_path: Path to the image file to OCR.
        lang: Tesseract language parameter (REQ-OCR-006/007). Defaults to
            English (`"eng"`); pass `"kor"` or `"kor+eng"` for Korean.

    Returns:
        The extracted text, stripped of leading/trailing whitespace. An
        empty string when no recognizable text is found -- not an error
        (REQ-OCR-002).

    Raises:
        OcrError: The Tesseract engine is unavailable, execution failed,
            or the requested language pack is not installed (REQ-OCR-003,
            REQ-OCR-008). The original pytesseract error message is
            preserved so the missing component is identifiable.
    """
    try:
        # Broad except: pytesseract/Tesseract can raise a variety of
        # exception types (missing binary, missing language pack,
        # unreadable image, engine crash) that must all funnel into the
        # same OcrError contract for every caller.
        text = pytesseract.image_to_string(image_path, lang=lang)
    except Exception as exc:  # noqa: BLE001
        raise OcrError(f"OCR extraction failed: {exc}") from exc

    return text.strip()


def extract_pdf_text_via_ocr(pdf_path: str, lang: str = "eng") -> str:
    """Render each page of the PDF at `pdf_path` to an image and OCR it.

    Args:
        pdf_path: Path to the PDF file (typically scanned/image-only, with
            no extractable text layer).
        lang: Tesseract language parameter, forwarded to
            :func:`extract_image_text` for every page.

    Returns:
        The OCR text of each page, merged in page order (plain text, no
        heading structure -- acceptance.md SS D.1: image-based text carries
        no font-size metadata to detect headings from).

    Raises:
        OcrError: The PDF cannot be opened, a page cannot be rendered, or
            a page's OCR fails (REQ-OCR-005).
    """
    try:
        document = fitz.open(pdf_path)
    except Exception as exc:  # noqa: BLE001
        raise OcrError(f"Failed to open PDF for OCR: {pdf_path}: {exc}") from exc

    try:
        page_texts: list[str] = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            for page_index, page in enumerate(document):
                page_texts.append(_ocr_page(page, page_index, tmp_dir, lang))
    finally:
        document.close()

    return "\n\n".join(page_texts)


def _ocr_page(page: fitz.Page, page_index: int, tmp_dir: str, lang: str) -> str:
    """Render a single PDF page to a temp image and OCR it (M2 decision:
    temp-file bridge, consistent with `telegram_bot/extract.py`, avoiding a
    direct Pillow dependency)."""
    try:
        pixmap = page.get_pixmap(dpi=300)
        tmp_image_path = os.path.join(tmp_dir, f"page-{page_index}.png")
        pixmap.save(tmp_image_path)
    except Exception as exc:  # noqa: BLE001
        raise OcrError(f"Failed to render PDF page {page_index}: {exc}") from exc

    return extract_image_text(tmp_image_path, lang=lang)
