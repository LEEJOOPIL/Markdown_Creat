# markdown-creat

Tools for converting documents to and from standardized Markdown.

## Features

- **PDF → Markdown** (`markdown_creat.pdf_to_markdown`): converts a PDF file
  to a Markdown file. Body text is extracted in reading order, and heading
  structure (`#`, `##`, `###`) is detected using a font-size heuristic.
- **Telegram → Markdown bot** (`markdown_creat.telegram_bot`, SPEC-TELEGRAM-001):
  a long-polling Telegram bot that saves incoming text, photo, and PDF/document
  messages as dated Markdown notes under `telegram-notes/YYYY-MM-DD/`, with
  OCR text extraction for photos (`pytesseract`) and PDF text extraction
  (reusing `pdf_to_markdown` above). Original attachments are always kept
  under a `files/` subfolder alongside the note.

## Installation

```bash
pip install -e .
```

Requires Python 3.10+ and [PyMuPDF](https://pypi.org/project/PyMuPDF/) (installed automatically as a dependency).

The Telegram bot additionally requires `python-telegram-bot>=22.0` and
`pytesseract>=0.3.13` (also installed automatically as dependencies). OCR
requires the Tesseract OCR engine to be installed separately as a system
binary — it is not a Python package and is not installed by `pip`.

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

## Telegram bot usage

Running the bot:

```bash
python -m markdown_creat.telegram_bot
```

The bot uses long polling only — it does not register or use a webhook. The
bot token is read from the `TELEGRAM_BOT_TOKEN` environment variable, or from
a gitignored `.env` file if the environment variable is not set. The token is
never hardcoded in source code, never committed to version control, and never
written to saved `.md` files or logs. If no token is configured at startup,
the bot exits immediately with a clear error message (fail-fast) instead of
hanging.

By default, notes are saved under `telegram-notes/YYYY-MM-DD/` at the project
root; a configurable base folder can replace this default. See
`.moai/specs/SPEC-TELEGRAM-001/spec.md` for the full requirement set,
including error-handling behavior (API/network errors keep polling; OCR/PDF
extraction failures preserve the original attachment with a failure note) and
explicitly out-of-scope items (auto-start/OS service registration, webhook
mode, access control/allowlist, note browsing UI, cloud sync).

## Development

```bash
pip install -e .
pytest
ruff check .
```

## Project Status

- SPEC-PDF-001 (PDF → Markdown core conversion): implemented, all acceptance
  criteria passing (17 tests).
- SPEC-TELEGRAM-001 (Telegram → Markdown storage bot): implemented, 10/10
  acceptance criteria passing, 96% test coverage.
- SPEC-GEN-001 (Markdown generation from templates): see
  `.moai/specs/SPEC-GEN-001/`.
