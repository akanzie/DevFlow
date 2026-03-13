"""Clipboard monitoring implementation for DailyClip."""

from __future__ import annotations

import difflib
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
STRUCTURED_PATTERN = re.compile(r"(https?://|\{|\[|\(|\=|^[A-Fa-f0-9]{2,}$)")


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
        self._is_internal_copy = False
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

    async def copy_to_clipboard(self, content: str) -> None:
        """Nút Copy trên UI sẽ gọi hàm này thay vì gọi trực tiếp pyperclip."""
        self._is_internal_copy = True
        try:
            pyperclip.copy(content)
            # Cập nhật last_content để monitor loop không nhận nhầm là thay đổi
            self._last_text_content = content
            logger.info("Internal copy: Monitor bypassed.")
        finally:
            # Giải phóng cờ sau một khoảng ngắn
            self._is_internal_copy = False

    async def _process_clipboard_text(self, content: str) -> None:
        """Validate, deduplicate, persist, index, and broadcast a text clip."""
        if getattr(self, "_is_internal_copy", False):
            return
        # 1. Chuẩn hóa nội dung (Xóa khoảng trắng thừa từng dòng)
        clean_content = "\n".join(line.rstrip() for line in content.splitlines()).strip()

        # 2. Validation
        if not clean_content or len(clean_content) > AppConfig.MAX_CLIP_LENGTH:
            return

        if len(clean_content) < 3 and not STRUCTURED_PATTERN.search(clean_content):
            return

        # 3. Check trùng ngắn hạn trong RAM (Dùng clean_content thay cho normalized)
        digest = self._build_text_digest(clean_content)
        if self._is_duplicate_digest(digest):
            logger.debug("Skipped duplicate clipboard text (RAM check).")
            return

        # 4. Tạo ID dựa trên nội dung (Content-addressable ID)
        content_hash = hashlib.sha1(clean_content.encode("utf-8")).hexdigest()
        entry_id = f"clip:{content_hash}"

        # 5. Kiểm tra trong Database/Storage
        existing_clip = await self._storage_service.find_exact_clip_match(entry_id)

        if existing_clip:
            logger.info("Nội dung đã tồn tại, chỉ cập nhật timestamp cho ID: %s", entry_id)
            # Cập nhật thời gian để bản ghi cũ "nhảy" lên đầu danh sách
            await self._storage_service.update_clip_timestamp(entry_id, datetime.now())
            # Nếu bạn có UI, có thể cần broadcast để UI biết mà move item này lên top
            self._broadcast_clip(existing_clip)
            return

        # REQ-104c - Similarity Versioning
        version_of = None
        recent_clips = await self._storage_service.get_recent_clips(limit=50)
        recent_texts = [
            c for c in recent_clips
            if c.clip_type == "text" and (datetime.now() - c.timestamp) < timedelta(hours=24)
        ]

        for older in recent_texts:
            similarity = difflib.SequenceMatcher(None, clean_content, older.content).ratio()
            if similarity > 0.80:
                version_of = older.version_of or older.entry_id

                # Checking constraints removing oldest child if counts max out
                count = await self._storage_service.count_versions_sync(version_of)
                if count >= 10:
                    await self._storage_service.delete_oldest_version(version_of)
                break

        clip = ClipItem.create_text(
            clean_content,
            source_url=self._extract_source_url(clean_content),
            timestamp=datetime.now(),
            version_of=version_of
        )
        clip_path = await self._storage_service.append_clip(clip)
        persisted_clip = replace(clip, file_path=clip_path)
        await self._search_service.index_clip(persisted_clip)
        self._broadcast_clip(persisted_clip)
        logger.info("Captured clipboard text (%s chars).", len(clean_content))

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

        try:
            with Image.open(io.BytesIO(image_data)) as img:
                if img.width < 64 or img.height < 64:
                    return
        except Exception as exc:
            logger.warning("Corrupted clipboard image payload: %s", exc)
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

        # Exact Duplicate check
        exact_match = await self._storage_service.find_exact_clip_match(clip.entry_id)
        if exact_match:
            new_clip = replace(exact_match, timestamp=datetime.now(), file_path=image_path, is_deleted=False)
            tombstone = replace(exact_match, timestamp=datetime.now(), is_deleted=True)
            await self._storage_service.append_clip(tombstone)
            await self._storage_service.append_clip(new_clip)
            await self._search_service.index_clip(new_clip)
            self._broadcast_clip(new_clip)
            logger.info("Silently updated clipboard image to %s.", image_path)
            return

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
