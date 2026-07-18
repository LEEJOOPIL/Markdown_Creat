# markdown-creat

Tools for converting documents to and from standardized Markdown.

## Features

- **PDF → Markdown** (`markdown_creat.pdf_to_markdown`): converts a PDF file
  to a Markdown file. Body text is extracted in reading order, and heading
  structure (`#`, `##`, `###`) is detected using a font-size heuristic.
- **OCR core module** (`markdown_creat.ocr`, SPEC-OCR-001): shared image and
  PDF-page OCR text extraction via `pytesseract`, with English and Korean
  language support (`lang="eng"` default, `lang="kor"` / `"kor+eng"` for
  Korean). Used by the Telegram bot's photo path below; the PDF page-image
  function (`extract_pdf_text_via_ocr`) is a building block for a future
  automatic OCR fallback in `pdf_to_markdown` (not yet wired in).
- **Telegram → Markdown bot** (`markdown_creat.telegram_bot`, SPEC-TELEGRAM-001):
  a long-polling Telegram bot that saves incoming text, photo, and PDF/document
  messages as dated Markdown notes under `telegram-notes/YYYY-MM-DD/`, with
  OCR text extraction for photos (via the shared `markdown_creat.ocr` module
  above, wired to extract Korean + English text) and PDF text extraction
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

### Tesseract Korean language pack (`kor` traineddata)

Korean OCR (`lang="kor"` / `"kor+eng"`) requires the Tesseract `kor`
traineddata to be installed at the system level, in addition to the
Tesseract binary itself. This is a system-level prerequisite, not a pip
package:

```bash
# Debian/Ubuntu
sudo apt-get install tesseract-ocr-kor

# macOS (Homebrew)
brew install tesseract-lang

# Windows
# Download kor.traineddata from
# https://github.com/tesseract-ocr/tessdata and place it in Tesseract's
# tessdata directory (e.g. C:\Program Files\Tesseract-OCR\tessdata).
```

If the `kor` language pack is missing, OCR calls with `lang="kor"` or
`lang="kor+eng"` raise `markdown_creat.ocr.OcrError` with the original
Tesseract error message (identifying which language pack is missing) instead
of silently falling back to English or returning an empty result.

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

Table extraction, image/figure extraction, batch/multi-file processing, and
a CLI entry point are not implemented. Automatic OCR fallback inside
`pdf_to_markdown` for scanned/image-only PDFs is also not yet wired in (see
`.moai/specs/SPEC-OCR-001/spec.md` §Exclusions — planned as a future
`SPEC-PDF-001` amendment). See `.moai/specs/SPEC-PDF-001/spec.md` for the
full PDF-conversion scope definition.

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

On Windows, double-click `run_telegram_bot.bat` at the project root to start
the bot without opening a terminal (SPEC-TELEGRAM-003). It anchors to its own
location, checks for `.venv\Scripts\python.exe` before launching, and keeps
the console window open after exit so any error is visible.

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
- SPEC-TELEGRAM-002 (attachment path traversal fix, CWE-22): implemented,
  4/4 acceptance criteria passing, `storage.py` coverage 100%.
- SPEC-OCR-001 (shared OCR core module + Korean photo-path wiring):
  implemented, all acceptance criteria passing.
- SPEC-GEN-001 (Markdown generation from templates): see
  `.moai/specs/SPEC-GEN-001/`.
