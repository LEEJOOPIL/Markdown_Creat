"""Extract text from PDF document attachments (REQ-TELEGRAM-006).

Reuses SPEC-PDF-001's `pdf_to_markdown()` public function. This module does
NOT reimplement any PDF parsing logic (spec.md SS Exclusions -- "PDF 파싱
재구현" is explicitly out of scope). `pdf_to_markdown()` is a
file-output-only contract (writes to `output_path`, returns None), so this
wrapper bridges it to an in-memory string via a temporary `.md` file.
"""

from __future__ import annotations

import os
import tempfile

from markdown_creat.pdf_to_markdown import MarkdownConversionError, pdf_to_markdown

__all__ = ["extract_pdf_text", "DocumentExtractionError"]


class DocumentExtractionError(Exception):
    """Raised when a document's text cannot be extracted (REQ-TELEGRAM-011)."""


def extract_pdf_text(pdf_path: str) -> str:
    """Return the Markdown text extracted from the PDF at `pdf_path`.

    Raises:
        DocumentExtractionError: The underlying `pdf_to_markdown()` call
            failed (e.g. corrupted/encrypted PDF, no extractable text).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_output_path = os.path.join(tmp_dir, "extracted.md")
        try:
            pdf_to_markdown(pdf_path, tmp_output_path)
        except MarkdownConversionError as exc:
            raise DocumentExtractionError(f"Failed to extract text from PDF: {exc}") from exc

        with open(tmp_output_path, encoding="utf-8") as handle:
            return handle.read()
