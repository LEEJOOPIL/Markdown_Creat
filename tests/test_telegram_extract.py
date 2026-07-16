"""Tests for markdown_creat.telegram_bot.extract.

Covers REQ-TELEGRAM-006: PDF text extraction by reusing SPEC-PDF-001's
`pdf_to_markdown()` (file-output-only contract) via a temp-file
write-then-read wrapper. `pdf_to_markdown` itself is mocked here -- its
correctness is already covered by SPEC-PDF-001's own test suite
(acceptance.md SS D.2: PyMuPDF dependencies isolated with mocks/stubs).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from markdown_creat.pdf_to_markdown import PDFCorruptedError
from markdown_creat.telegram_bot.extract import DocumentExtractionError, extract_pdf_text


def _fake_pdf_to_markdown_writes_content(content: str):
    def _fake(pdf_path: str, output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(content)

    return _fake


def test_extract_pdf_text_returns_content_written_by_pdf_to_markdown():
    with patch(
        "markdown_creat.telegram_bot.extract.pdf_to_markdown",
        side_effect=_fake_pdf_to_markdown_writes_content("# Extracted body\n"),
    ):
        result = extract_pdf_text("dummy.pdf")

    assert result == "# Extracted body\n"


def test_extract_pdf_text_supports_korean_utf8_content():
    with patch(
        "markdown_creat.telegram_bot.extract.pdf_to_markdown",
        side_effect=_fake_pdf_to_markdown_writes_content("한글 추출 내용"),
    ):
        result = extract_pdf_text("dummy.pdf")

    assert "한글 추출 내용" in result


def test_extract_pdf_text_wraps_conversion_error(tmp_path):
    with patch(
        "markdown_creat.telegram_bot.extract.pdf_to_markdown",
        side_effect=PDFCorruptedError("corrupted"),
    ):
        with pytest.raises(DocumentExtractionError):
            extract_pdf_text("dummy.pdf")


def test_extract_pdf_text_does_not_leak_temp_file_path(tmp_path):
    """The temp `.md` file used to bridge pdf_to_markdown()'s file-output
    contract must not leak into the returned text or leave residue behind."""
    with patch(
        "markdown_creat.telegram_bot.extract.pdf_to_markdown",
        side_effect=_fake_pdf_to_markdown_writes_content("clean content"),
    ):
        result = extract_pdf_text("dummy.pdf")

    assert result == "clean content"
    assert "tmp" not in result.lower()
