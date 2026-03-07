"""Clipboard monitoring implementation for DailyClip."""

from __future__ import annotations

import hashlib
import io
import logging
import re
import threading
import time
from concurrent.futures import Future
from dataclasses import replace
from datetime import datetime, timedelta

import pyperclip
from PIL import Image, ImageGrab

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

URL_PATTERN = re.compile(r"https?://[^\s]+")


class ClipboardMonitorService(IClipboardMonitor):
    """Poll the system clipboard and persist unique text or image entries."""

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
        self._last_text_content = ""
        self._last_image_digest: str | None = None
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
            name="dailyclip-clipboard-monitor",
            daemon=True,
        )
        self._monitor_thread.start()
        logger.info("Clipboard monitoring started.")

    async def stop_monitoring(self) -> None:
        """Stop clipboard polling."""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
            self._monitor_thread = None
        logger.info("Clipboard monitoring stopped.")

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
        """Continuously read clipboard text and image payloads."""
        while not self._stop_event.is_set():
            current_text = self._read_clipboard_text()
            if current_text != self._last_text_content:
                self._last_text_content = current_text
                if current_text:
                    future = self._runtime.submit(self._process_clipboard_text(current_text))
                    future.add_done_callback(self._log_future_failure)

            image_payload = self._read_clipboard_image()
            if image_payload is None:
                self._last_image_digest = None
            else:
                image_digest = self._build_image_digest(image_payload)
                if image_digest != self._last_image_digest:
                    self._last_image_digest = image_digest
                    future = self._runtime.submit(
                        self._process_clipboard_image(image_payload, image_digest)
                    )
                    future.add_done_callback(self._log_future_failure)

            time.sleep(AppConfig.CLIPBOARD_CHECK_INTERVAL)

    async def _process_clipboard(self, content: str) -> None:
        """Backwards-compatible helper for text clipboard tests."""
        await self._process_clipboard_text(content)

    async def _process_clipboard_text(self, content: str) -> None:
        """Validate, deduplicate, persist, index, and broadcast a text clip."""
        normalized = content.strip()
        if not normalized or len(normalized) > AppConfig.MAX_CLIP_LENGTH:
            return

        digest = self._build_text_digest(normalized)
        if self._is_duplicate_digest(digest):
            logger.debug("Skipped duplicate clipboard text.")
            return

        clip = ClipItem.create_text(
            normalized,
            source_url=self._extract_source_url(normalized),
        )
        clip_path = await self._storage_service.append_clip(clip)
        persisted_clip = replace(clip, file_path=clip_path)
        await self._search_service.index_clip(persisted_clip)
        self._broadcast_clip(persisted_clip)
        logger.info("Captured clipboard text (%s chars).", len(normalized))

    async def _process_clipboard_image(
        self,
        image_data: bytes,
        digest: str | None = None,
    ) -> None:
        """Persist clipboard images so Print Screen and Win+Shift+S are captured."""
        image_digest = digest or self._build_image_digest(image_data)
        if self._is_duplicate_digest(image_digest):
            logger.debug("Skipped duplicate clipboard image.")
            return

        captured_at = datetime.now()
        image_path = await self._storage_service.save_screenshot(
            image_data,
            captured_at=captured_at,
        )
        clip = ClipItem.create_image(
            content=f"Clipboard image {image_path.name}",
            file_path=image_path,
            timestamp=captured_at,
        )
        await self._storage_service.append_clip(clip)
        await self._search_service.index_clip(clip)
        self._broadcast_clip(clip)
        logger.info("Captured clipboard image to %s.", image_path)

    def _broadcast_clip(self, clip: ClipItem) -> None:
        """Notify registered callbacks for a newly persisted clip."""
        for callback in list(self._callbacks):
            try:
                callback(clip)
            except Exception:
                logger.exception("Clipboard callback failed.")

    def _is_duplicate_digest(self, digest: str) -> bool:
        """Check whether a payload digest has already been captured recently."""
        now = datetime.now()
        self._prune_recent_hashes(now)
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
    def _read_clipboard_text() -> str:
        """Read text clipboard content when available."""
        try:
            return pyperclip.paste()
        except pyperclip.PyperclipException as exc:
            logger.debug("Clipboard text read failed: %s", exc)
            return ""

    @staticmethod
    def _read_clipboard_image() -> bytes | None:
        """Read clipboard image content and normalize it to PNG bytes."""
        try:
            clipboard_payload = ImageGrab.grabclipboard()
        except OSError as exc:
            logger.debug("Clipboard image read failed: %s", exc)
            return None

        if not isinstance(clipboard_payload, Image.Image):
            return None

        buffer = io.BytesIO()
        clipboard_payload.save(buffer, format="PNG")
        return buffer.getvalue()

    @staticmethod
    def _extract_source_url(content: str) -> str | None:
        """Extract the first URL from clipboard content."""
        match = URL_PATTERN.search(content)
        return match.group(0) if match else None

    @staticmethod
    def _build_text_digest(content: str) -> str:
        """Return a digest stable for clipboard text deduplication."""
        return f"text:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"

    @staticmethod
    def _build_image_digest(image_data: bytes) -> str:
        """Return a digest stable for clipboard image deduplication."""
        return f"image:{hashlib.sha256(image_data).hexdigest()}"

    @staticmethod
    def _log_future_failure(future: Future[object]) -> None:
        """Log unhandled background coroutine failures."""
        try:
            future.result()
        except Exception:
            logger.exception("Clipboard processing failed.")
