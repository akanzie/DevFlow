"""Tests for DuckDB-backed search."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

pytest.importorskip("duckdb")

from DailyClip.core.entities import ClipItem, DailyNote
from DailyClip.infrastructure.search import DuckDBSearchService
from DailyClip.infrastructure.storage import FileStorageService


@pytest.fixture()
def search_service(temp_data_dir: Path):
    """Provide a DuckDBSearchService that is always closed after each test."""
    svc = DuckDBSearchService(temp_data_dir)
    yield svc
    svc.close()


@pytest.mark.asyncio
async def test_rebuild_index_and_search_return_results(temp_data_dir, search_service: DuckDBSearchService):
    """Rebuilding the index should make clips and notes searchable."""
    storage = FileStorageService(temp_data_dir)

    clip = ClipItem.create_text(
        "async await clipboard",
        timestamp=datetime(2026, 3, 7, 9, 30, 5),
    )
    note = DailyNote.create(
        date="2026-03-07",
        content="Markdown note about async await",
        timestamp=datetime(2026, 3, 7, 10, 0, 0),
    )

    await storage.append_clip(clip)
    await storage.save_note(note)
    await search_service.rebuild_index()

    results = await search_service.search("async")

    assert len(results) >= 2
    # FTS sorts by score descending first. Both match 'async' strongly.
    assert any(r.entry_type == "note" for r in results)
    assert any(r.entry_type == "clip" for r in results)


@pytest.mark.asyncio
async def test_incremental_index_note_returns_note_result(search_service: DuckDBSearchService):
    """Incrementally indexed notes should be returned by search queries."""
    note = DailyNote.create(
        date="2026-03-07",
        content="Incremental note search target",
        timestamp=datetime(2026, 3, 7, 10, 15, 0),
    )

    await search_service.index_note(note)
    results = await search_service.search("target")

    assert any(result.entry_type == "note" for result in results)


@pytest.mark.asyncio
async def test_rebuild_index_preserves_image_clip_paths(temp_data_dir, search_service: DuckDBSearchService):
    """Image clips should keep their image file path in search results for preview."""
    storage = FileStorageService(temp_data_dir)
    captured_at = datetime(2026, 3, 7, 10, 15, 22)

    image_path = await storage.save_screenshot(b"img", captured_at=captured_at)
    image_clip = ClipItem.create_image(
        content=f"Clipboard image {image_path.name}",
        file_path=image_path,
        timestamp=captured_at,
    )
    await storage.append_clip(image_clip)
    await search_service.rebuild_index()

    results = await search_service.search("clipboard image")

    assert results
    assert any(result.file_path == image_path for result in results)


@pytest.mark.asyncio
async def test_batch_index_clips(search_service: DuckDBSearchService):
    """Batch indexing should safely upsert records."""
    clips = [
        ClipItem.create_text(
            f"batch clip {i}",
            timestamp=datetime(2026, 3, 7, 10, i, 0)
        ) for i in range(1, 6)
    ]
    await search_service.index_clips(clips)

    results = await search_service.search("batch clip")
    assert len(results) == 5


@pytest.mark.asyncio
async def test_batch_index_notes(search_service: DuckDBSearchService):
    """Batch indexing for notes should be searchable."""
    notes = [
        DailyNote.create(
            date=f"2026-03-{10+i}",
            content=f"batch note target {i}",
            timestamp=datetime(2026, 3, 10+i, 10, 0, 0)
        ) for i in range(1, 4)
    ]
    await search_service.index_notes(notes)

    results = await search_service.search("batch note target")
    assert len(results) == 3
