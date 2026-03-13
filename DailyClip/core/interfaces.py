"""Service contracts for DailyClip."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Protocol

from .entities import BrowseEntry, ClipItem, DailyNote, SearchResult

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

    async def list_browse_entries(self, limit: int = 100) -> list[BrowseEntry]:
        """Return recent folders and files for browse mode."""

    async def find_exact_clip_match(self, entry_id: str) -> ClipItem | None:
        """Find an exact duplicate clip based on entry_id hash."""

    async def get_recent_clips(self, limit: int = 50, favorite_only: bool = False, tag: str | None = None) -> list[ClipItem]:
        """Return recent text clips for versioning sequence matching."""

    async def get_all_versions(self, version_group_id: str) -> list[ClipItem]:
        """Return all valid versions of a clip group (for diffing)."""

    async def count_versions_sync(self, version_group_id: str) -> int:
        """Return the count of clips grouped under a version_of tree."""

    async def delete_oldest_version(self, version_group_id: str) -> None:
        """Write a tombstone entity deleting the chronologically oldest item in a group."""

    async def delete_clip(self, entry_id: str) -> None:
        """Write a tombstone entity deleting a clip."""


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

    async def index_clips(self, clips: list[ClipItem]) -> None:
        """Index multiple clips incrementally."""

    async def index_notes(self, notes: list[DailyNote]) -> None:
        """Index multiple notes incrementally."""

    def close(self) -> None:
        """Close connection to backend index storage."""


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
