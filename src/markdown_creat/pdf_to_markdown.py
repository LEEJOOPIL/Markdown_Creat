"""Convert a PDF document to a Markdown file.

Core public function: :func:`pdf_to_markdown`. Extracts body text and a
heading structure (via a font-size heuristic) from a PDF using PyMuPDF
(fitz), and writes the result as a UTF-8 encoded ``.md`` file.

Heading heuristic (REQ-PDF-002, documented per acceptance.md SS D.2):
the font size that occurs most often across all text lines in the
document is treated as the "body" size. Distinct font sizes strictly
larger than the body size are sorted in descending order and mapped to
heading levels 1-3 (largest -> ``#``, next -> ``##``, next -> ``###``).
Any additional, smaller-but-still-larger-than-body sizes beyond the
first three are collapsed into heading level 3. When no size is larger
than the body size (a visually uniform document), no headings are
produced and every line is treated as a paragraph -- this is not an
error (acceptance.md SS D.1).
"""

from __future__ import annotations

import os
from collections import Counter

import fitz

__all__ = [
    "pdf_to_markdown",
    "MarkdownConversionError",
    "PDFNotFoundError",
    "PDFCorruptedError",
    "PDFEncryptedError",
    "PDFNoTextError",
]

_MAX_HEADING_LEVEL = 3


class MarkdownConversionError(Exception):
    """Base exception for all markdown_creat conversion errors."""


class PDFNotFoundError(MarkdownConversionError):
    """Raised when the input PDF file does not exist at the given path."""


class PDFCorruptedError(MarkdownConversionError):
    """Raised when the PDF file exists but cannot be parsed (corrupted)."""


class PDFEncryptedError(MarkdownConversionError):
    """Raised when the PDF file is password-protected / encrypted."""


class PDFNoTextError(MarkdownConversionError):
    """Raised when the PDF contains no extractable text (e.g. scanned/image-only)."""


# @MX:ANCHOR: [AUTO] Public API boundary -- the sole entry point all future
# callers (a planned CLI, batch tooling, other SPECs) depend on.
# @MX:REASON: SPEC-PDF-001 REQ-PDF-001~010; changing the signature or the
# exception hierarchy is a breaking change for every downstream caller.
def pdf_to_markdown(pdf_path: str, output_path: str) -> None:
    """Convert the PDF at `pdf_path` to a Markdown file at `output_path`.

    Args:
        pdf_path: Path to the source PDF file.
        output_path: Path where the resulting ``.md`` file is written
            (UTF-8 encoded). An existing file at this path is overwritten.

    Raises:
        PDFNotFoundError: No file exists at `pdf_path`.
        PDFCorruptedError: The file exists but cannot be parsed as a PDF.
        PDFEncryptedError: The PDF is password-protected.
        PDFNoTextError: No extractable text was found in the PDF.

    On any error, no file is written or modified at `output_path` -- the
    Markdown string is fully assembled in memory before the output file
    is opened, so a partial/incomplete file is never left behind
    (REQ-PDF-010).
    """
    if not os.path.isfile(pdf_path):
        raise PDFNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        document = fitz.open(pdf_path)
    except fitz.FileDataError as exc:
        raise PDFCorruptedError(f"PDF file is corrupted and cannot be read: {pdf_path}") from exc

    try:
        if document.is_encrypted or document.needs_pass:
            raise PDFEncryptedError(f"PDF file is encrypted/password-protected: {pdf_path}")

        markdown_text = _build_markdown(document)
    finally:
        document.close()

    if markdown_text is None:
        raise PDFNoTextError(f"No extractable text found in PDF: {pdf_path}")

    _write_markdown_file(output_path, markdown_text)


def _write_markdown_file(output_path: str, markdown_text: str) -> None:
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(markdown_text)


def _iter_text_blocks(document: fitz.Document) -> list[list[tuple[str, float]]]:
    """Return text blocks (in reading order, across all pages) as (text, size) lines."""
    blocks: list[list[tuple[str, float]]] = []
    for page in document:
        page_dict = page.get_text("dict")
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:  # 0 == text block; skip images etc.
                continue
            block_lines: list[tuple[str, float]] = []
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(span.get("text", "") for span in spans).strip()
                if not text:
                    continue
                size = max(span.get("size", 0.0) for span in spans)
                block_lines.append((text, size))
            if block_lines:
                blocks.append(block_lines)
    return blocks


def _classify_heading_levels(sizes: list[float]) -> dict[float, int]:
    """Map font sizes larger than the body (most common) size to heading levels 1-3.

    The body size is the size occurring most often across all lines. When
    multiple sizes tie for the highest frequency (e.g. a document with a
    single title line and a single body line), the smallest of the tied
    sizes is treated as the body -- headings are, by convention, both
    larger and less frequent than body text, so ties resolve toward the
    smaller size.
    """
    if not sizes:
        return {}

    rounded_sizes = [round(size, 1) for size in sizes]
    size_counts = Counter(rounded_sizes)
    max_count = max(size_counts.values())
    body_size = min(size for size, count in size_counts.items() if count == max_count)

    heading_sizes = sorted({size for size in size_counts if size > body_size}, reverse=True)

    return {size: min(index + 1, _MAX_HEADING_LEVEL) for index, size in enumerate(heading_sizes)}


def _build_markdown(document: fitz.Document) -> str | None:
    """Assemble the full Markdown string for `document`, or None if no text found."""
    blocks = _iter_text_blocks(document)
    all_sizes = [size for block in blocks for _, size in block]
    if not all_sizes:
        return None

    level_map = _classify_heading_levels(all_sizes)

    markdown_blocks: list[str] = []
    for block_lines in blocks:
        block_size = round(max(size for _, size in block_lines), 1)
        level = level_map.get(block_size)
        text = " ".join(line_text for line_text, _ in block_lines)
        if level:
            markdown_blocks.append(f"{'#' * level} {text}")
        else:
            markdown_blocks.append(text)

    return "\n\n".join(markdown_blocks) + "\n"
