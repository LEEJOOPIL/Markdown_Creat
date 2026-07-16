"""Tests for markdown_creat.pdf_to_markdown.

Test fixtures use PyMuPDF (fitz) itself to build small in-memory/temp PDFs,
since PyMuPDF is the core dependency under test here (not an external
network/OCR dependency) -- per spec.md SS C, mocking is reserved for
genuinely external systems, of which this SPEC has none.
"""

from __future__ import annotations

import fitz
import pytest

from markdown_creat.pdf_to_markdown import (
    PDFCorruptedError,
    PDFEncryptedError,
    PDFNoTextError,
    PDFNotFoundError,
    pdf_to_markdown,
)

# Type alias (documentation only): a page is a list of blocks; a block is a
# list of (text, fontsize) lines meant to render as a single paragraph or
# heading. Lines within a block use tight spacing so PyMuPDF's layout
# analysis merges them into one text block; blocks are separated by extra
# vertical whitespace so distinct paragraphs/headings stay in distinct
# blocks (verified empirically against this PyMuPDF version).
Page = list[list[tuple[str, float]]]


def make_pdf(path: str, pages: list[Page], fontname: str = "helv") -> None:
    """Create a simple PDF file at `path` from `pages` (see the `Page` alias)."""
    doc = fitz.open()
    for page_blocks in pages:
        page = doc.new_page(width=595, height=842)  # A4
        y = 72.0
        for block in page_blocks:
            for text, fontsize in block:
                page.insert_text((72, y), text, fontsize=fontsize, fontname=fontname)
                y += fontsize + 4
            y += 20
    doc.save(path)
    doc.close()


def make_encrypted_pdf(path: str) -> None:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 72), "secret content", fontsize=12)
    doc.save(
        path,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw="owner-secret",
        user_pw="user-secret",
    )
    doc.close()


def make_no_text_pdf(path: str) -> None:
    """A page with no text content at all (simulates a scanned/image-only PDF)."""
    doc = fitz.open()
    doc.new_page(width=595, height=842)
    doc.save(path)
    doc.close()


# ---------------------------------------------------------------------------
# M1 -- public API: success path (AC-PDF-001a, REQ-PDF-001/003/004)
# ---------------------------------------------------------------------------


def test_pdf_to_markdown_creates_utf8_md_file_with_body_text(tmp_path):
    pdf_path = tmp_path / "simple.pdf"
    output_path = tmp_path / "simple.md"
    make_pdf(
        str(pdf_path),
        pages=[
            [
                [
                    ("This is the first line of body text.", 11),
                    ("This is the second line of the same paragraph.", 11),
                ]
            ]
        ],
    )

    result = pdf_to_markdown(str(pdf_path), str(output_path))

    assert result is None
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "This is the first line of body text." in content
    assert "This is the second line of the same paragraph." in content


def test_pdf_to_markdown_preserves_reading_order(tmp_path):
    pdf_path = tmp_path / "order.pdf"
    output_path = tmp_path / "order.md"
    make_pdf(
        str(pdf_path),
        pages=[
            [
                [("Alpha paragraph.", 11)],
                [("Beta paragraph.", 11)],
                [("Gamma paragraph.", 11)],
            ]
        ],
    )

    pdf_to_markdown(str(pdf_path), str(output_path))

    content = output_path.read_text(encoding="utf-8")
    assert content.index("Alpha") < content.index("Beta") < content.index("Gamma")


def test_pdf_to_markdown_supports_korean_utf8_content(tmp_path):
    pdf_path = tmp_path / "korean.pdf"
    output_path = tmp_path / "korean.md"
    make_pdf(
        str(pdf_path),
        pages=[[[("한글 문서 내용입니다.", 11)]]],
        fontname="korea-s",
    )

    pdf_to_markdown(str(pdf_path), str(output_path))

    content = output_path.read_text(encoding="utf-8")
    assert "한글" in content


# ---------------------------------------------------------------------------
# M2 -- heading detection heuristic (AC-PDF-001b, REQ-PDF-002)
# ---------------------------------------------------------------------------


def test_pdf_to_markdown_detects_large_font_as_heading(tmp_path):
    pdf_path = tmp_path / "heading.pdf"
    output_path = tmp_path / "heading.md"
    make_pdf(
        str(pdf_path),
        pages=[
            [
                [("Document Title", 24)],
                [("Body paragraph text goes here.", 11)],
            ]
        ],
    )

    pdf_to_markdown(str(pdf_path), str(output_path))

    content = output_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    assert "# Document Title" in lines
    assert "Body paragraph text goes here." in content
    assert "# Body paragraph text goes here." not in content


def test_pdf_to_markdown_maps_multiple_heading_sizes_to_levels(tmp_path):
    pdf_path = tmp_path / "multi_heading.pdf"
    output_path = tmp_path / "multi_heading.md"
    make_pdf(
        str(pdf_path),
        pages=[
            [
                [("Main Title", 24)],
                [("Body text one.", 11)],
                [("Sub Heading", 16)],
                [("Body text two.", 11)],
            ]
        ],
    )

    pdf_to_markdown(str(pdf_path), str(output_path))

    content = output_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    assert "# Main Title" in lines
    assert "## Sub Heading" in lines


def test_pdf_to_markdown_uniform_font_size_has_no_headings(tmp_path):
    """Edge case (acceptance.md SS D.1): uniform font size -> all paragraphs, not an error."""
    pdf_path = tmp_path / "uniform.pdf"
    output_path = tmp_path / "uniform.md"
    make_pdf(
        str(pdf_path),
        pages=[
            [
                [("Line one.", 11)],
                [("Line two.", 11)],
                [("Line three.", 11)],
            ]
        ],
    )

    pdf_to_markdown(str(pdf_path), str(output_path))

    content = output_path.read_text(encoding="utf-8")
    assert "#" not in content


# ---------------------------------------------------------------------------
# M1/M1c -- existing output file overwrite (AC-PDF-001c, REQ-PDF-005)
# ---------------------------------------------------------------------------


def test_pdf_to_markdown_overwrites_existing_output_file(tmp_path):
    pdf_path = tmp_path / "overwrite.pdf"
    output_path = tmp_path / "overwrite.md"
    output_path.write_text("stale previous content", encoding="utf-8")
    make_pdf(str(pdf_path), pages=[[[("Fresh content.", 11)]]])

    pdf_to_markdown(str(pdf_path), str(output_path))

    content = output_path.read_text(encoding="utf-8")
    assert "Fresh content." in content
    assert "stale previous content" not in content


# ---------------------------------------------------------------------------
# M3 -- error handling contract (AC-PDF-002a~e, REQ-PDF-006~010)
# ---------------------------------------------------------------------------


def test_pdf_to_markdown_raises_clear_error_when_file_missing(tmp_path):
    missing_path = tmp_path / "does_not_exist.pdf"
    output_path = tmp_path / "out.md"

    with pytest.raises(PDFNotFoundError) as exc_info:
        pdf_to_markdown(str(missing_path), str(output_path))

    assert str(missing_path) in str(exc_info.value)
    assert not output_path.exists()


def test_pdf_to_markdown_raises_clear_error_for_corrupted_pdf(tmp_path):
    corrupted_path = tmp_path / "corrupted.pdf"
    corrupted_path.write_bytes(b"%PDF-1.4\nnot a real pdf content garbage garbage")
    output_path = tmp_path / "out.md"

    with pytest.raises(PDFCorruptedError):
        pdf_to_markdown(str(corrupted_path), str(output_path))

    assert not output_path.exists()


def test_pdf_to_markdown_raises_clear_error_for_encrypted_pdf(tmp_path):
    encrypted_path = tmp_path / "encrypted.pdf"
    make_encrypted_pdf(str(encrypted_path))
    output_path = tmp_path / "out.md"

    with pytest.raises(PDFEncryptedError):
        pdf_to_markdown(str(encrypted_path), str(output_path))

    assert not output_path.exists()


def test_pdf_to_markdown_raises_clear_error_when_no_extractable_text(tmp_path):
    no_text_path = tmp_path / "no_text.pdf"
    make_no_text_pdf(str(no_text_path))
    output_path = tmp_path / "out.md"

    with pytest.raises(PDFNoTextError):
        pdf_to_markdown(str(no_text_path), str(output_path))

    assert not output_path.exists()


@pytest.mark.parametrize(
    "builder_name",
    ["missing", "corrupted", "encrypted", "no_text"],
)
def test_pdf_to_markdown_never_leaves_partial_output_on_error(tmp_path, builder_name):
    """AC-PDF-002e / REQ-PDF-010: no incomplete .md file survives any error path."""
    output_path = tmp_path / "partial.md"

    if builder_name == "missing":
        pdf_path = tmp_path / "missing.pdf"
        expected_exc = PDFNotFoundError
    elif builder_name == "corrupted":
        pdf_path = tmp_path / "corrupted.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\nnot a real pdf content garbage garbage")
        expected_exc = PDFCorruptedError
    elif builder_name == "encrypted":
        pdf_path = tmp_path / "encrypted.pdf"
        make_encrypted_pdf(str(pdf_path))
        expected_exc = PDFEncryptedError
    else:
        pdf_path = tmp_path / "no_text.pdf"
        make_no_text_pdf(str(pdf_path))
        expected_exc = PDFNoTextError

    with pytest.raises(expected_exc):
        pdf_to_markdown(str(pdf_path), str(output_path))

    assert not output_path.exists()


# ---------------------------------------------------------------------------
# acceptance.md SS D.1 edge cases
# ---------------------------------------------------------------------------


def test_pdf_to_markdown_multi_page_merges_into_single_md_in_page_order(tmp_path):
    pdf_path = tmp_path / "multipage.pdf"
    output_path = tmp_path / "multipage.md"
    make_pdf(
        str(pdf_path),
        pages=[
            [[("Page one content.", 11)]],
            [[("Page two content.", 11)]],
        ],
    )

    pdf_to_markdown(str(pdf_path), str(output_path))

    content = output_path.read_text(encoding="utf-8")
    assert content.index("Page one content.") < content.index("Page two content.")


def test_pdf_to_markdown_creates_missing_parent_directory(tmp_path):
    pdf_path = tmp_path / "simple.pdf"
    output_path = tmp_path / "nested" / "dir" / "out.md"
    make_pdf(str(pdf_path), pages=[[[("Some text.", 11)]]])

    pdf_to_markdown(str(pdf_path), str(output_path))

    assert output_path.exists()
