"""Tests for core entities and config helpers."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime
from pathlib import Path

import pytest

from DailyClip.core.config import AppConfig
from DailyClip.core.entities import ClipItem, DailyNote, SearchResult


class TestClipItem:
    """Tests for clipboard items."""

    def test_create_text_clip_sets_defaults(self) -> None:
        """Text clip factory should set type, format, and source URL."""
        clip = ClipItem.create_text(
            content='hello',
            source_url='https://example.com',
            timestamp=datetime(2026, 3, 7, 9, 0, 0),
        )

        assert clip.content == 'hello'
        assert clip.clip_type == 'text'
        assert clip.format == 'plain'
        assert clip.source_url == 'https://example.com'

    def test_from_dict_round_trip_preserves_fields(self, sample_clip: ClipItem) -> None:
        """Serialization round-trip should preserve clip content."""
        restored = ClipItem.from_dict(sample_clip.to_dict())

        assert restored == sample_clip

    def test_immutability_raises_frozen_instance_error(self, sample_clip: ClipItem) -> None:
        """Clip items should remain immutable."""
        with pytest.raises(FrozenInstanceError):
            sample_clip.content = 'modified'  # type: ignore[misc]


class TestDailyNote:
    """Tests for daily notes."""

    def test_update_content_returns_new_note(self, sample_note: DailyNote) -> None:
        """Updating note content should preserve created_at and change content."""
        updated = sample_note.update_content(
            'Updated content',
            timestamp=datetime(2026, 3, 7, 10, 0, 0),
        )

        assert updated.content == 'Updated content'
        assert updated.created_at == sample_note.created_at
        assert updated.updated_at > sample_note.updated_at


class TestSearchResult:
    """Tests for search results."""

    def test_to_dict_serializes_all_public_fields(self) -> None:
        """Search result serialization should expose the MVP contract."""
        result = SearchResult(
            entry_id='clip:123',
            entry_type='clip',
            timestamp=datetime(2026, 3, 7, 9, 30, 5),
            content='full text',
            preview='full text',
            file_path=Path('clip.jsonl'),
            source_url='https://example.com',
            score=0.95,
        )

        payload = result.to_dict()

        assert payload['entry_id'] == 'clip:123'
        assert payload['entry_type'] == 'clip'
        assert payload['file_path'] == 'clip.jsonl'
        assert payload['score'] == 0.95


class TestAppConfig:
    """Tests for naming helpers and defaults."""

    def test_clip_filename_uses_srs_pattern(self) -> None:
        """Clip files should follow the per-second naming convention."""
        timestamp = datetime(2026, 3, 7, 9, 30, 5)

        assert AppConfig.get_clip_filename(timestamp) == 'clips_09-30-05.jsonl'

    def test_screenshot_filename_uses_srs_pattern(self) -> None:
        """Screenshot files should follow the SRS naming convention."""
        timestamp = datetime(2026, 3, 7, 9, 30, 5)

        assert AppConfig.get_screenshot_filename(timestamp) == 'screen_09-30-05.png'
