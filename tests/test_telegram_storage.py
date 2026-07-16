"""Tests for markdown_creat.telegram_bot.storage.

Covers REQ-TELEGRAM-008 (date-folder + timestamp filename layout, configurable
base folder) and REQ-TELEGRAM-009 (note body schema: timestamp, sender/chat
context, text body, attachment links) -- AC-TELEGRAM-001a, AC-TELEGRAM-001b.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from markdown_creat.telegram_bot.storage import (
    note_dir,
    note_filename,
    note_path,
    render_note,
    save_attachment,
    save_note,
)

TIMESTAMP = datetime(2026, 7, 16, 10, 30, 45)


# ---------------------------------------------------------------------------
# M1 -- date-folder + timestamp-filename layout (REQ-TELEGRAM-008)
# ---------------------------------------------------------------------------


def test_note_dir_is_date_based_under_base_dir(tmp_path):
    result = note_dir(str(tmp_path / "telegram-notes"), TIMESTAMP)

    assert result == tmp_path / "telegram-notes" / "2026-07-16"


def test_note_filename_is_timestamp_based_with_message_id_suffix():
    # Message-id suffix avoids collisions when multiple messages land in the
    # same second (plan.md SS D M1 collision-avoidance decision).
    result = note_filename(TIMESTAMP, message_id=42)

    assert result == "2026-07-16_103045_42.md"


def test_note_path_combines_dir_and_filename(tmp_path):
    result = note_path(str(tmp_path / "telegram-notes"), TIMESTAMP, message_id=42)

    assert result == tmp_path / "telegram-notes" / "2026-07-16" / "2026-07-16_103045_42.md"


def test_two_messages_in_same_second_get_distinct_paths(tmp_path):
    base = str(tmp_path / "telegram-notes")

    first = note_path(base, TIMESTAMP, message_id=1)
    second = note_path(base, TIMESTAMP, message_id=2)

    assert first != second


# ---------------------------------------------------------------------------
# M1 -- configurable base folder (REQ-TELEGRAM-018, AC-TELEGRAM-001b)
# ---------------------------------------------------------------------------


def test_note_dir_uses_configured_base_folder_instead_of_default(tmp_path):
    custom_base = str(tmp_path / "my-custom-notes")

    result = note_dir(custom_base, TIMESTAMP)

    assert result == Path(custom_base) / "2026-07-16"


# ---------------------------------------------------------------------------
# M1 -- note body schema (REQ-TELEGRAM-009)
# ---------------------------------------------------------------------------


def test_render_note_includes_timestamp_sender_chat_and_body():
    content = render_note(
        timestamp=TIMESTAMP,
        sender="Alice",
        chat_context="Alice's private chat",
        body_text="Hello world",
    )

    assert TIMESTAMP.isoformat() in content
    assert "Alice" in content
    assert "Alice's private chat" in content
    assert "Hello world" in content


def test_render_note_omits_sender_and_chat_when_unavailable():
    content = render_note(
        timestamp=TIMESTAMP,
        sender=None,
        chat_context=None,
        body_text="Hello world",
    )

    assert "Hello world" in content
    assert "Sender" not in content
    assert "Chat:" not in content


def test_render_note_links_attachment_paths_in_body():
    content = render_note(
        timestamp=TIMESTAMP,
        sender="Alice",
        chat_context=None,
        body_text="See attached",
        attachment_paths=["telegram-notes/files/2026-07-16_103045_42_photo.jpg"],
    )

    assert "photo.jpg" in content
    assert "telegram-notes/files/2026-07-16_103045_42_photo.jpg" in content


# ---------------------------------------------------------------------------
# M1 -- save_note / save_attachment write to disk (REQ-TELEGRAM-004, 005)
# ---------------------------------------------------------------------------


def test_save_note_writes_utf8_md_file_and_creates_date_dir(tmp_path):
    base = str(tmp_path / "telegram-notes")

    result_path = save_note(
        base_dir=base,
        timestamp=TIMESTAMP,
        message_id=42,
        sender="Alice",
        chat_context="Alice's private chat",
        body_text="한글 메시지 내용",
    )

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "한글 메시지 내용" in content


def test_save_attachment_writes_original_bytes_under_files_dir(tmp_path):
    base = str(tmp_path / "telegram-notes")

    result_path = save_attachment(
        base_dir=base,
        timestamp=TIMESTAMP,
        message_id=42,
        filename="photo.jpg",
        content=b"\xff\xd8\xff\xe0fakejpegbytes",
    )

    assert result_path.exists()
    assert result_path.parent == Path(base) / "files"
    assert result_path.read_bytes() == b"\xff\xd8\xff\xe0fakejpegbytes"


def test_save_attachment_avoids_filename_collision_across_messages(tmp_path):
    base = str(tmp_path / "telegram-notes")

    first = save_attachment(base, TIMESTAMP, 1, "photo.jpg", b"first")
    second = save_attachment(base, TIMESTAMP, 2, "photo.jpg", b"second")

    assert first != second
    assert first.read_bytes() == b"first"
    assert second.read_bytes() == b"second"
