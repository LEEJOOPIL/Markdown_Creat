# markdown-creat

Tools for converting documents to and from standardized Markdown.

## Features

- **PDF → Markdown** (`markdown_creat.pdf_to_markdown`): converts a PDF file
  to a Markdown file. Body text is extracted in reading order, and heading
  structure (`#`, `##`, `###`) is detected using a font-size heuristic.

## Installation

```bash
pip install -e .
```

Requires Python 3.10+ and [PyMuPDF](https://pypi.org/project/PyMuPDF/) (installed automatically as a dependency).

## Usage

```python
from markdown_creat import pdf_to_markdown

pdf_to_markdown("document.pdf", "document.md")
```

`pdf_to_markdown(pdf_path, output_path)` writes a UTF-8 encoded `.md` file at
`output_path`, overwriting any existing file there. On error, no file is
written or left partially written.

Raised exceptions (all subclasses of `MarkdownConversionError`):

| Exception | Raised when |
|-----------|-------------|
| `PDFNotFoundError` | No file exists at `pdf_path` |
| `PDFCorruptedError` | The file exists but cannot be parsed as a PDF |
| `PDFEncryptedError` | The PDF is password-protected |
| `PDFNoTextError` | No extractable text was found (e.g. a scanned/image-only PDF) |

## Out of Scope (current version)

Table extraction, image/figure extraction, OCR, batch/multi-file processing,
and a CLI entry point are not implemented. See
`.moai/specs/SPEC-PDF-001/spec.md` for the full scope definition.

## Development

```bash
pip install -e .
pytest
ruff check .
```

## Project Status

- SPEC-PDF-001 (PDF → Markdown core conversion): implemented, all acceptance
  criteria passing (17 tests).
- SPEC-GEN-001 (Markdown generation from templates): see
  `.moai/specs/SPEC-GEN-001/`.
