"""Thin re-export of the shared core OCR module (REQ-OCR-013, REQ-OCR-014).

Image OCR extraction (REQ-TELEGRAM-007) now lives in the shared core module
`markdown_creat.ocr` (SPEC-OCR-001). This module re-exports its public
contract unchanged so existing callers (`handlers.py`) and their import path
keep working -- no OCR parsing logic is reimplemented here.
"""

from __future__ import annotations

from markdown_creat.ocr import OcrError as ImageOcrError
from markdown_creat.ocr import extract_image_text

__all__ = ["extract_image_text", "ImageOcrError"]
