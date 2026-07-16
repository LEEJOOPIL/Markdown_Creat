# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `pdf_to_markdown(pdf_path, output_path)` (SPEC-PDF-001): converts a PDF file
  to a UTF-8 encoded Markdown file.
  - Extracts body text in reading order across all pages.
  - Detects heading structure via a font-size heuristic (levels 1-3).
  - Raises `PDFNotFoundError`, `PDFCorruptedError`, `PDFEncryptedError`, or
    `PDFNoTextError` for missing, corrupted, encrypted, or textless PDFs.
  - Never leaves a partial `.md` file on error (output is assembled in
    memory before the file is written).
  - Overwrites an existing file at `output_path`.
- **Telegram → Markdown bot** (`markdown_creat.telegram_bot`, SPEC-TELEGRAM-001):
  a long-polling bot that saves incoming text, photo, and PDF/document
  messages as dated Markdown notes.
  - Saves each received message as a single `.md` file under
    `telegram-notes/YYYY-MM-DD/` (timestamp-based filename), with a
    configurable base folder to replace the default.
  - Saves the original attachment (photo or document) under a `files/`
    subfolder, always, regardless of extraction success.
  - Extracts photo text via OCR (`pytesseract` + Tesseract engine) and merges
    it into the message's `.md` body.
  - Extracts PDF/document text by reusing SPEC-PDF-001's `pdf_to_markdown()`
    (no PDF-parsing logic reimplemented) and merges it into the message's
    `.md` body.
  - Reads the bot token from the `TELEGRAM_BOT_TOKEN` environment variable or
    a gitignored `.env` file; exits immediately with a clear error message if
    no token is configured (fail-fast), never hardcodes or logs the token.
  - Uses long polling only — no webhook registered.
  - On a Telegram API or network error, logs the error and continues polling
    instead of crashing.
  - On OCR or PDF extraction failure, saves the original attachment plus a
    `.md` note indicating extraction failure, so the message is never lost.
  - Adds `python-telegram-bot>=22.0` and `pytesseract>=0.3.13` as project
    dependencies; Tesseract OCR itself is a system-level binary not managed by
    pip.
  - Out of scope: auto-start/OS service registration, webhook mode, access
    control (allowlist/denylist), a note browsing UI, and cloud sync.
  - 10/10 acceptance criteria passing, 96% test coverage.
