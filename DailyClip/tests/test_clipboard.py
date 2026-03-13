"""Tests for clipboard monitoring logic."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.infrastructure.clipboard import ClipboardMonitorService
import io
from PIL import Image


@pytest.mark.asyncio
async def test_process_clipboard_persists_and_indexes_clip(sample_clip):
    """New clipboard content should be persisted and indexed once."""
    storage_service = AsyncMock()
    storage_service.append_clip.return_value = Path("clips_09-30-05.jsonl")
    storage_service.find_exact_clip_match.return_value = None
    storage_service.get_recent_clips.return_value = []
    search_service = AsyncMock()
    runtime = AsyncRuntime()
    monitor = ClipboardMonitorService(storage_service, search_service, runtime)

    await monitor._process_clipboard(sample_clip.content)

    storage_service.append_clip.assert_called_once()
    search_service.index_clip.assert_called_once()
    persisted_clip = storage_service.append_clip.await_args.args[0]
    assert persisted_clip.source_url == "https://example.com"


@pytest.mark.asyncio
async def test_process_clipboard_skips_duplicate_within_dedup_window():
    """Duplicate clipboard content should be ignored within the dedup window."""
    storage_service = AsyncMock()
    storage_service.append_clip.return_value = Path("clips_09-30-05.jsonl")
    storage_service.find_exact_clip_match.return_value = None
    storage_service.get_recent_clips.return_value = []
    search_service = AsyncMock()
    runtime = AsyncRuntime()
    monitor = ClipboardMonitorService(storage_service, search_service, runtime)

    await monitor._process_clipboard("duplicate text")
    await monitor._process_clipboard("duplicate text")

    storage_service.append_clip.assert_awaited_once()
    search_service.index_clip.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_clipboard_image_saves_and_indexes_screenshot():
    """Clipboard images should be persisted as screenshots and indexed once."""
    storage_service = AsyncMock()
    storage_service.save_screenshot.return_value = Path("images/screen_10-15-22.png")
    storage_service.append_clip.return_value = Path("clips_10-15-22.jsonl")
    storage_service.find_exact_clip_match.return_value = None
    search_service = AsyncMock()
    runtime = AsyncRuntime()
    monitor = ClipboardMonitorService(storage_service, search_service, runtime)

    img = Image.new('RGB', (64, 64), color = 'red')
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    valid_image_bytes = buffer.getvalue()

    await monitor._process_clipboard_image(valid_image_bytes)

    storage_service.save_screenshot.assert_awaited_once()
    storage_service.append_clip.assert_awaited_once()
    search_service.index_clip.assert_awaited_once()
    image_clip = storage_service.append_clip.await_args.args[0]
    assert image_clip.clip_type == "image"
    assert image_clip.file_path == Path("images/screen_10-15-22.png")
