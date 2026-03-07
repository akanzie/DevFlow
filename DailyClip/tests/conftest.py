"""Pytest fixtures for DailyClip."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from DailyClip.core.entities import ClipItem, DailyNote


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Provide a temporary data directory."""
    return tmp_path / 'dailyclip-data'


@pytest.fixture
def sample_timestamp() -> datetime:
    """Provide a stable timestamp for tests."""
    return datetime(2026, 3, 7, 9, 30, 5)


@pytest.fixture
def sample_clip(sample_timestamp: datetime) -> ClipItem:
    """Provide a stable clip item."""
    return ClipItem.create_text(
        content='Test clipboard content https://example.com',
        source_url='https://example.com',
        timestamp=sample_timestamp,
    )


@pytest.fixture
def sample_note() -> DailyNote:
    """Provide a stable daily note."""
    return DailyNote.create(
        date='2026-03-07',
        content='# Daily Note\n\nTest content',
        timestamp=datetime(2026, 3, 7, 9, 45, 0),
    )
