"""Clipboard monitoring implementation for DailyClip."""

from __future__ import annotations

import hashlib
import logging
import re
import threading
import time
from dataclasses import replace
from datetime import datetime, timedelta
from concurrent.futures import Future

import pyperclip

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.core.config import AppConfig
from DailyClip.core.entities import ClipItem
from DailyClip.core.interfaces import (
    ClipCallback,
    IClipboardMonitor,
    ISearchService,
    IStorageService,
)

logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(r'https?://[^\s]+')


class ClipboardMonitorService(IClipboardMonitor):
    """Poll the system clipboard and persist unique text entries."""

    def __init__(
        self,
        storage_service: IStorageService,
        search_service: ISearchService,
        runtime: AsyncRuntime,
    ) -> None:
        self._storage_service = storage_service
        self._search_service = search_service
        self._runtime = runtime
        self._callbacks: list[ClipCallback] = []
        self._last_content = ''
        self._recent_hashes: dict[str, datetime] = {}
        self._monitor_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    async def start_monitoring(self) -> None:
        """Start clipboard polling on a background thread."""
        if self.is_monitoring():
            return

        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name='dailyclip-clipboard-monitor',
            daemon=True,
        )
        self._monitor_thread.start()
        logger.info('Clipboard monitoring started.')

    async def stop_monitoring(self) -> None:
        """Stop clipboard polling."""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
            self._monitor_thread = None
        logger.info('Clipboard monitoring stopped.')

    def is_monitoring(self) -> bool:
        """Return whether the clipboard monitor is active."""
        return self._monitor_thread is not None and self._monitor_thread.is_alive()

    def register_callback(self, callback: ClipCallback) -> None:
        """Register a callback invoked for every new clip."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback: ClipCallback) -> None:
        """Remove a callback from the notification list."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _monitor_loop(self) -> None:
        """Continuously read clipboard text and submit processing work."""
        while not self._stop_event.is_set():
            try:
                current_content = pyperclip.paste()
            except pyperclip.PyperclipException as exc:
                logger.warning('Clipboard read failed: %s', exc)
                time.sleep(AppConfig.CLIPBOARD_CHECK_INTERVAL)
                continue

            if current_content != self._last_content:
                self._last_content = current_content
                future = self._runtime.submit(self._process_clipboard(current_content))
                future.add_done_callback(self._log_future_failure)

            time.sleep(AppConfig.CLIPBOARD_CHECK_INTERVAL)

    async def _process_clipboard(self, content: str) -> None:
        """Validate, deduplicate, persist, index, and broadcast a clip."""
        normalized = content.strip()
        if not normalized or len(normalized) > AppConfig.MAX_CLIP_LENGTH:
            return

        if self._is_duplicate(normalized):
            logger.debug('Skipped duplicate clipboard content.')
            return

        clip = ClipItem.create_text(
            normalized,
            source_url=self._extract_source_url(normalized),
        )
        clip_path = await self._storage_service.append_clip(clip)
        persisted_clip = replace(clip, file_path=clip_path)
        await self._search_service.index_clip(persisted_clip)

        for callback in list(self._callbacks):
            try:
                callback(persisted_clip)
            except Exception:
                logger.exception('Clipboard callback failed.')

        logger.info('Captured clipboard text (%s chars).', len(normalized))

    def _is_duplicate(self, content: str) -> bool:
        """Check whether content has already been captured recently."""
        now = datetime.now()
        self._prune_recent_hashes(now)
        digest = hashlib.sha256(content.encode('utf-8')).hexdigest()
        last_seen = self._recent_hashes.get(digest)
        if last_seen and now - last_seen < timedelta(seconds=AppConfig.CLIPBOARD_DEDUP_SECONDS):
            return True
        self._recent_hashes[digest] = now
        return False

    def _prune_recent_hashes(self, now: datetime) -> None:
        """Drop expired deduplication entries."""
        cutoff = timedelta(seconds=AppConfig.CLIPBOARD_DEDUP_SECONDS)
        expired = [
            digest
            for digest, seen_at in self._recent_hashes.items()
            if now - seen_at >= cutoff
        ]
        for digest in expired:
            self._recent_hashes.pop(digest, None)

    @staticmethod
    def _extract_source_url(content: str) -> str | None:
        """Extract the first URL from clipboard content."""
        match = URL_PATTERN.search(content)
        return match.group(0) if match else None

    @staticmethod
    def _log_future_failure(future: Future[object]) -> None:
        """Log unhandled background coroutine failures."""
        try:
            future.result()
        except Exception:
            logger.exception('Clipboard processing failed.')
