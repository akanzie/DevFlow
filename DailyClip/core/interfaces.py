"""Service contracts for DailyClip."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Protocol

from .entities import ClipItem, DailyNote, SearchResult

ClipCallback = Callable[[ClipItem], None]
HotkeyCallback = Callable[[], None]


class IStorageService(Protocol):
    """Interface for data persistence."""

    async def create_daily_folder(self, date_str: str) -> Path:
        """Create the standard folder structure for a day."""

    async def append_clip(self, clip: ClipItem) -> Path:
        """Append a clip to its per-second JSONL file and return the file path."""

    async def get_clips_for_date(self, date_str: str) -> list[ClipItem]:
        """Return all persisted clips for the provided date."""

    async def save_note(self, note: DailyNote) -> Path:
        """Persist a daily note and return the note file path."""

    async def get_note(self, date_str: str) -> DailyNote | None:
        """Load a daily note when it exists."""

    async def save_screenshot(
        self,
        image_data: bytes,
        captured_at: datetime | None = None,
    ) -> Path:
        """Persist a screenshot using the MVP naming convention."""


class ISearchService(Protocol):
    """Interface for search operations."""

    async def rebuild_index(self) -> None:
        """Rebuild the unified search index from persisted files."""

    async def search(self, query: str, limit: int = 50) -> list[SearchResult]:
        """Search indexed clips and notes."""

    async def index_clip(self, clip: ClipItem) -> None:
        """Index a single clip incrementally."""

    async def index_note(self, note: DailyNote) -> None:
        """Index a single note incrementally."""


class IClipboardMonitor(Protocol):
    """Interface for clipboard monitoring."""

    async def start_monitoring(self) -> None:
        """Start clipboard polling."""

    async def stop_monitoring(self) -> None:
        """Stop clipboard polling."""

    def is_monitoring(self) -> bool:
        """Return whether the monitor is active."""

    def register_callback(self, callback: ClipCallback) -> None:
        """Register a callback invoked for each new clip."""

    def unregister_callback(self, callback: ClipCallback) -> None:
        """Remove a previously registered callback."""


class IHotkeyService(Protocol):
    """Interface for global hotkey management."""

    def register_hotkey(self, key_combo: str, callback: HotkeyCallback) -> None:
        """Register a system-wide hotkey."""

    def unregister_hotkey(self, key_combo: str) -> None:
        """Unregister a previously configured hotkey."""

    def start_listener(self) -> None:
        """Activate global hotkeys."""

    def stop_listener(self) -> None:
        """Deactivate global hotkeys."""


class IScreenCaptureService(Protocol):
    """Interface for screen capture."""

    async def capture_screenshot(self) -> bytes:
        """Capture the full screen and return image bytes."""
