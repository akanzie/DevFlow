"""Tests for file storage."""

from __future__ import annotations

from datetime import datetime

import pytest

from DailyClip.core.config import AppConfig
from DailyClip.core.entities import ClipItem, DailyNote
from DailyClip.infrastructure.storage import FileStorageService


@pytest.mark.asyncio
async def test_create_daily_folder_creates_standard_subdirectories(temp_data_dir):
    """Storage should create the expected daily folder structure."""
    storage = FileStorageService(temp_data_dir)

    daily_dir = await storage.create_daily_folder("2026-03-07")

    assert daily_dir.exists()
    assert (daily_dir / AppConfig.CLIPPINGS_DIRNAME).exists()
    assert (daily_dir / AppConfig.IMAGES_DIRNAME).exists()
    assert (daily_dir / AppConfig.NOTES_DIRNAME).exists()


@pytest.mark.asyncio
async def test_append_clip_uses_per_second_file_and_appends(temp_data_dir):
    """Clips captured in the same second should append to the same JSONL file."""
    storage = FileStorageService(temp_data_dir)
    timestamp = datetime(2026, 3, 7, 9, 30, 5)
    first_clip = ClipItem.create_text("first", timestamp=timestamp)
    second_clip = ClipItem.create_text("second", timestamp=timestamp)

    first_path = await storage.append_clip(first_clip)
    second_path = await storage.append_clip(second_clip)
    clips = await storage.get_clips_for_date("2026-03-07")

    assert first_path == second_path
    assert first_path.name == "clips_09-30-05.jsonl"
    assert [clip.content for clip in clips] == ["first", "second"]


@pytest.mark.asyncio
async def test_save_note_and_get_note_round_trip(temp_data_dir):
    """Notes should persist to notes_YYYY-MM-DD.md and load back."""
    storage = FileStorageService(temp_data_dir)
    note = DailyNote.create(
        date="2026-03-07",
        content="# Test note",
        timestamp=datetime(2026, 3, 7, 10, 0, 0),
    )

    note_path = await storage.save_note(note)
    loaded_note = await storage.get_note("2026-03-07")

    assert note_path.name == "notes_2026-03-07.md"
    assert loaded_note is not None
    assert loaded_note.content == "# Test note"


@pytest.mark.asyncio
async def test_save_screenshot_adds_numeric_suffix_when_name_collides(temp_data_dir):
    """Screenshots captured in the same second should not overwrite each other."""
    storage = FileStorageService(temp_data_dir)
    captured_at = datetime(2026, 3, 7, 10, 15, 22)

    first_path = await storage.save_screenshot(b"first", captured_at=captured_at)
    second_path = await storage.save_screenshot(b"second", captured_at=captured_at)

    assert first_path.name == "screen_10-15-22.png"
    assert second_path.name == "screen_10-15-22_1.png"


@pytest.mark.asyncio
async def test_list_browse_entries_returns_recent_folders_and_files(temp_data_dir):
    """Browse mode should expose day folders plus note, image, and clip files."""
    storage = FileStorageService(temp_data_dir)
    timestamp = datetime(2026, 3, 7, 9, 30, 5)

    image_path = await storage.save_screenshot(b"img", captured_at=timestamp)
    image_clip = ClipItem.create_image(
        content=f"Clipboard image {image_path.name}",
        file_path=image_path,
        timestamp=timestamp,
    )
    await storage.append_clip(image_clip)
    await storage.save_note(
        DailyNote.create(
            date="2026-03-07",
            content="# Browse note",
            timestamp=datetime(2026, 3, 7, 9, 45, 0),
        )
    )

    entries = await storage.list_browse_entries(limit=10)
    entry_types = {entry.entry_type for entry in entries}

    assert "folder" in entry_types
    assert "note" in entry_types
    assert "image" in entry_types
    assert "clip_file" in entry_types
