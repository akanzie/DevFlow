"""Tests for DuckDB-backed search."""

from __future__ import annotations

from datetime import datetime

import pytest

duckdb = pytest.importorskip('duckdb')

from DailyClip.core.entities import ClipItem, DailyNote
from DailyClip.infrastructure.search import DuckDBSearchService
from DailyClip.infrastructure.storage import FileStorageService


@pytest.mark.asyncio
async def test_rebuild_index_and_search_return_results(temp_data_dir):
    """Rebuilding the index should make clips and notes searchable."""
    storage = FileStorageService(temp_data_dir)
    search = DuckDBSearchService(temp_data_dir)

    clip = ClipItem.create_text(
        'async await clipboard',
        timestamp=datetime(2026, 3, 7, 9, 30, 5),
    )
    note = DailyNote.create(
        date='2026-03-07',
        content='Markdown note about async await',
        timestamp=datetime(2026, 3, 7, 10, 0, 0),
    )

    await storage.append_clip(clip)
    await storage.save_note(note)
    await search.rebuild_index()

    results = await search.search('async')

    assert len(results) >= 2
    assert results[0].timestamp >= results[1].timestamp


@pytest.mark.asyncio
async def test_incremental_index_note_returns_note_result(temp_data_dir):
    """Incrementally indexed notes should be returned by search queries."""
    search = DuckDBSearchService(temp_data_dir)
    note = DailyNote.create(
        date='2026-03-07',
        content='Incremental note search target',
        timestamp=datetime(2026, 3, 7, 10, 15, 0),
    )

    await search.index_note(note)
    results = await search.search('target')

    assert any(result.entry_type == 'note' for result in results)
