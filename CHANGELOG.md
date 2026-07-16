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
