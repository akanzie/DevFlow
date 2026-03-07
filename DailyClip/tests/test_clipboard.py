"""Tests for clipboard monitoring logic."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.infrastructure.clipboard import ClipboardMonitorService


@pytest.mark.asyncio
async def test_process_clipboard_persists_and_indexes_clip(sample_clip):
    """New clipboard content should be persisted and indexed once."""
    storage_service = AsyncMock()
    storage_service.append_clip.return_value = Path('clips_09-30-05.jsonl')
    search_service = AsyncMock()
    runtime = AsyncRuntime()
    monitor = ClipboardMonitorService(storage_service, search_service, runtime)

    await monitor._process_clipboard(sample_clip.content)

    storage_service.append_clip.assert_called_once()
    search_service.index_clip.assert_called_once()
    persisted_clip = storage_service.append_clip.await_args.args[0]
    assert persisted_clip.source_url == 'https://example.com'


@pytest.mark.asyncio
async def test_process_clipboard_skips_duplicate_within_dedup_window():
    """Duplicate clipboard content should be ignored within the dedup window."""
    storage_service = AsyncMock()
    storage_service.append_clip.return_value = Path('clips_09-30-05.jsonl')
    search_service = AsyncMock()
    runtime = AsyncRuntime()
    monitor = ClipboardMonitorService(storage_service, search_service, runtime)

    await monitor._process_clipboard('duplicate text')
    await monitor._process_clipboard('duplicate text')

    storage_service.append_clip.assert_awaited_once()
    search_service.index_clip.assert_awaited_once()
