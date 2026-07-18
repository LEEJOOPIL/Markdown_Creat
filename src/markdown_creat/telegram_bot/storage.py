"""Store received Telegram messages as date-folder based Markdown notes.

Layout (REQ-TELEGRAM-008): ``<base_dir>/YYYY-MM-DD/YYYY-MM-DD_HHMMSS_<message_id>.md``.
The trailing ``message_id`` suffix avoids filename collisions when multiple
messages arrive within the same second (plan.md SS D M1 decision).

Attachment originals (REQ-TELEGRAM-005) are stored under
``<base_dir>/files/`` using the same timestamp + message-id prefix to avoid
collisions across messages.

Note body schema (REQ-TELEGRAM-009): timestamp, sender/chat context (when
available), text/extracted-text body, and links to any saved attachments.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

DEFAULT_BASE_FOLDER = "telegram-notes"
_ATTACHMENTS_DIRNAME = "files"
_FALLBACK_ATTACHMENT_BASENAME = "attachment"


def note_dir(base_dir: str | os.PathLike[str], timestamp: datetime) -> Path:
    """Return the date-based directory a note for `timestamp` belongs in."""
    return Path(base_dir) / timestamp.strftime("%Y-%m-%d")


def note_filename(timestamp: datetime, message_id: int) -> str:
    """Return the timestamp+message-id based `.md` filename."""
    return f"{timestamp.strftime('%Y-%m-%d_%H%M%S')}_{message_id}.md"


def note_path(base_dir: str | os.PathLike[str], timestamp: datetime, message_id: int) -> Path:
    """Return the full path a note for `timestamp`/`message_id` is saved at."""
    return note_dir(base_dir, timestamp) / note_filename(timestamp, message_id)


def render_note(
    timestamp: datetime,
    sender: str | None,
    chat_context: str | None,
    body_text: str,
    attachment_paths: list[str] | None = None,
) -> str:
    """Render the Markdown body for a single message note."""
    lines: list[str] = ["# Telegram Message", ""]
    lines.append(f"- Timestamp: {timestamp.isoformat()}")
    if chat_context:
        lines.append(f"- Chat: {chat_context}")
    if sender:
        lines.append(f"- Sender: {sender}")
    lines.append("")
    lines.append("## Content")
    lines.append("")
    lines.append(body_text)

    if attachment_paths:
        lines.append("")
        lines.append("## Attachments")
        lines.append("")
        for attachment_path in attachment_paths:
            name = Path(attachment_path).name
            lines.append(f"- [{name}]({attachment_path})")

    lines.append("")
    return "\n".join(lines)


def save_note(
    base_dir: str | os.PathLike[str],
    timestamp: datetime,
    message_id: int,
    sender: str | None,
    chat_context: str | None,
    body_text: str,
    attachment_paths: list[str] | None = None,
) -> Path:
    """Render and write a note `.md` file, creating the date folder as needed."""
    target_dir = note_dir(base_dir, timestamp)
    target_dir.mkdir(parents=True, exist_ok=True)

    path = note_path(base_dir, timestamp, message_id)
    content = render_note(timestamp, sender, chat_context, body_text, attachment_paths)
    path.write_text(content, encoding="utf-8")
    return path


def _sanitize_attachment_basename(filename: str) -> str:
    """Reduce `filename` to a safe, separator-free basename.

    Defeats path traversal (CWE-22, REQ-TELEGRAM-019~021) by explicitly
    splitting on both `/` and `\\` -- the Telegram-provided `filename` string
    may contain either separator regardless of host OS, so relying solely on
    `pathlib`'s platform-dependent separator recognition would miss one of
    the two vectors. Falls back to a fixed placeholder when the sanitized
    result is empty or a directory-reference-only segment (REQ-TELEGRAM-023).
    Non-separator characters (including non-ASCII) are left untouched
    (REQ-TELEGRAM-022).
    """
    normalized = filename.replace("\\", "/")
    segments = [segment for segment in normalized.split("/") if segment]
    basename = segments[-1] if segments else ""
    if basename in ("", ".", ".."):
        return _FALLBACK_ATTACHMENT_BASENAME
    return basename


def save_attachment(
    base_dir: str | os.PathLike[str],
    timestamp: datetime,
    message_id: int,
    filename: str,
    content: bytes,
) -> Path:
    """Write the original attachment bytes under `<base_dir>/files/`.

    `filename` is sanitized to a safe basename before path construction to
    prevent path traversal / arbitrary file write (CWE-22, REQ-TELEGRAM-019
    ~023 -- SPEC-TELEGRAM-002).
    """
    attachments_dir = Path(base_dir) / _ATTACHMENTS_DIRNAME
    attachments_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = _sanitize_attachment_basename(filename)
    safe_name = f"{timestamp.strftime('%Y-%m-%d_%H%M%S')}_{message_id}_{safe_filename}"
    path = attachments_dir / safe_name
    path.write_bytes(content)
    return path
