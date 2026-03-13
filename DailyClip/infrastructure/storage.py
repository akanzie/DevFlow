"""File storage implementation for DailyClip."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from DailyClip.core.config import AppConfig
from DailyClip.core.entities import BrowseEntry, ClipItem, DailyNote
from DailyClip.core.exceptions import StorageError
from DailyClip.core.interfaces import IStorageService

logger = logging.getLogger(__name__)


class FileStorageService(IStorageService):
    """Persist clips, notes, screenshots, and browse-mode metadata."""

    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else AppConfig.get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._daily_dirs_cache: list[Path] | None = None

    async def create_daily_folder(self, date_str: str) -> Path:
        """Create the standard folder structure for a given day."""
        daily_dir = self.data_dir / date_str
        await asyncio.to_thread(self._create_daily_folder_sync, daily_dir)
        return daily_dir

    async def append_clip(self, clip: ClipItem) -> Path:
        """Append a clip to its per-second JSONL file."""
        clips_path = await self._get_clip_path(clip.timestamp)
        payload = json.dumps(clip.to_dict(), ensure_ascii=False)
        await asyncio.to_thread(self._append_text_line, clips_path, payload)
        logger.info("Persisted clip to %s", clips_path)

        # Enforce version limit
        if clip.version_of:
            count = await self.count_versions_sync(clip.version_of)
            if count > AppConfig.MAX_VERSIONS:
                await self.delete_oldest_version(clip.version_of)

        return clips_path

    async def get_clips_for_date(self, date_str: str) -> list[ClipItem]:
        """Load all clips for a specific date."""
        daily_dir = self.data_dir / date_str / AppConfig.CLIPPINGS_DIRNAME
        if not daily_dir.exists():
            return []

        files = sorted(daily_dir.glob("*.jsonl"))
        return await asyncio.to_thread(self._read_clip_files, files)

    async def save_note(self, note: DailyNote) -> Path:
        """Persist the note for the provided date."""
        note_path = await self._get_note_path(note.date)
        await asyncio.to_thread(self._write_text, note_path, note.content)
        logger.info("Persisted note to %s", note_path)
        return note_path

    async def get_note(self, date_str: str) -> DailyNote | None:
        """Load a daily note when it exists."""
        note_path = await self._get_note_path(date_str)
        if not note_path.exists():
            return None

        return await asyncio.to_thread(self._read_note, note_path, date_str)

    async def save_screenshot(
        self,
        image_data: bytes,
        captured_at: datetime | None = None,
    ) -> Path:
        """Persist a screenshot using the MVP filename convention."""
        timestamp = captured_at or datetime.now()
        daily_dir = await self.create_daily_folder(timestamp.strftime("%Y-%m-%d"))
        images_dir = daily_dir / AppConfig.IMAGES_DIRNAME
        image_path = await asyncio.to_thread(
            self._ensure_unique_path,
            images_dir / AppConfig.get_screenshot_filename(timestamp),
        )
        await asyncio.to_thread(self._write_bytes, image_path, image_data)
        logger.info("Persisted screenshot to %s", image_path)
        return image_path

    async def list_browse_entries(self, limit: int = 100) -> list[BrowseEntry]:
        """Return recent folders and files for browse mode."""
        return await asyncio.to_thread(self._list_browse_entries_sync, limit)

    async def find_exact_clip_match(self, entry_id: str) -> ClipItem | None:
        """Find an exact duplicate clip based on entry_id hash."""
        return await asyncio.to_thread(self._find_exact_clip_match_sync, entry_id)

    async def get_recent_clips(self, limit: int = 50, favorite_only: bool = False, tag: str | None = None) -> list[ClipItem]:
        """Return recent text clips for versioning sequence matching."""
        return await asyncio.to_thread(self._get_recent_clips_sync, limit, favorite_only, tag)

    async def update_clip_timestamp(self, entry_id: str, new_timestamp: datetime) -> None:
        """Update the last-seen timestamp of an existing clip by appending a new log entry."""
        await asyncio.to_thread(self._update_clip_timestamp_sync, entry_id, new_timestamp)

    async def count_versions_sync(self, version_group_id: str) -> int:
        """Return the count of clips grouped under a version_of tree."""
        return await asyncio.to_thread(self._count_versions_sync_impl, version_group_id)

    async def get_all_versions(self, version_group_id: str) -> list[ClipItem]:
        """Return all valid versions of a clip group (for diffing)."""
        return await asyncio.to_thread(self._get_all_versions_sync, version_group_id)

    async def delete_oldest_version(self, version_group_id: str) -> None:
        """Write a tombstone entity deleting the chronologically oldest item in a group."""
        await asyncio.to_thread(self._delete_oldest_version_sync, version_group_id)

    async def delete_clip(self, entry_id: str) -> None:
        """Write a tombstone entity deleting a clip."""
        await asyncio.to_thread(self._delete_clip_sync, entry_id)

    async def delete_note(self, date_str: str) -> None:
        """Delete a daily note from disk."""
        note_path = await self._get_note_path(date_str)
        if await asyncio.to_thread(note_path.exists):
            await asyncio.to_thread(note_path.unlink)
            logger.info("Deleted note for %s at %s", date_str, note_path)

    async def _get_clip_path(self, timestamp: datetime) -> Path:
        """Resolve the clip file path for a timestamp."""
        daily_dir = await self.create_daily_folder(timestamp.strftime("%Y-%m-%d"))
        return daily_dir / AppConfig.CLIPPINGS_DIRNAME / AppConfig.get_clip_filename(timestamp)

    async def _get_note_path(self, date_str: str) -> Path:
        """Resolve the note file path for a date."""
        daily_dir = await self.create_daily_folder(date_str)
        return daily_dir / AppConfig.NOTES_DIRNAME / AppConfig.get_note_filename(date_str)

    def _list_browse_entries_sync(self, limit: int) -> list[BrowseEntry]:
        """Build a recent folder/file list for browse mode."""
        entries: list[BrowseEntry] = []
        for daily_dir in self._iter_daily_dirs_desc():
            if len(entries) >= limit:
                break

            files = self._collect_daily_files(daily_dir)
            entries.append(self._build_folder_entry(daily_dir, files))
            if len(entries) >= limit:
                break

            for file_path in files:
                if len(entries) >= limit:
                    break
                entry = self._build_file_entry(file_path)
                if entry is not None:
                    entries.append(entry)

        return entries

    def _find_exact_clip_match_sync(self, entry_id: str) -> ClipItem | None:
        """Scan backwards locating the first active clip with the given entry_id."""
        for daily_dir in self._iter_daily_dirs_desc():
            clips_dir = daily_dir / AppConfig.CLIPPINGS_DIRNAME
            if not clips_dir.exists():
                continue

            # Read files newer first.
            files = sorted(clips_dir.glob("*.jsonl"), reverse=True)
            for file_path in files:
                try:
                    with file_path.open("r", encoding="utf-8") as handle:
                        # Since we now create one file per clip, most will have 1 line.
                        # But we still handle multi-line just in case of overlaps or legacy.
                        for line in handle:
                            if not line.strip():
                                continue
                            data = json.loads(line)
                            if data.get("entry_id") == entry_id:
                                # Found it. Check if it's deleted.
                                if data.get("is_deleted", False):
                                    return None
                                return ClipItem.from_dict(data)
                except (json.JSONDecodeError, OSError) as exc:
                    logger.warning("Error reading clip file %s: %s", file_path, exc)
                    continue
        return None

    def _update_clip_timestamp_sync(self, entry_id: str, new_timestamp: datetime) -> None:
        """Locate the most recent version of a clip and append a fresh copy with the new timestamp."""
        existing = self._find_exact_clip_match_sync(entry_id)
        if not existing:
            return

        from dataclasses import replace
        updated = replace(existing, timestamp=new_timestamp)
        # Force daily folder creation for the new timestamp
        daily_dir = self.data_dir / new_timestamp.strftime("%Y-%m-%d")
        clips_dir = daily_dir / AppConfig.CLIPPINGS_DIRNAME
        clips_dir.mkdir(parents=True, exist_ok=True)
        
        clips_path = clips_dir / AppConfig.get_clip_filename(new_timestamp)
        payload = json.dumps(updated.to_dict(), ensure_ascii=False)
        self._append_text_line(clips_path, payload)
        logger.info("Updated timestamp for %s by appending to %s", entry_id, clips_path)

    def _get_recent_clips_sync(self, limit: int, favorite_only: bool = False, tag: str | None = None) -> list[ClipItem]:
        """Return latest non-deleted clips mapped into objects."""
        active_clips: list[ClipItem] = []
        seen_ids: set[str] = set()

        for daily_dir in self._iter_daily_dirs_desc():
            if len(active_clips) >= limit:
                break

            clips_dir = daily_dir / AppConfig.CLIPPINGS_DIRNAME
            if not clips_dir.exists():
                continue

            files = sorted(clips_dir.glob("*.jsonl"), reverse=True)
            for file_path in files:
                if len(active_clips) >= limit:
                    break
                try:
                    lines = file_path.read_text(encoding="utf-8").splitlines()
                    for line in reversed(lines):
                        if not line.strip() or len(active_clips) >= limit:
                            continue
                        data = json.loads(line)
                        entry_id = data.get("entry_id")
                        if not entry_id or entry_id in seen_ids:
                            continue
                        seen_ids.add(entry_id)

                        if favorite_only and not data.get("is_favorite", False):
                            seen_ids.remove(entry_id)  # Don't mark as seen if it doesn't match filter, so we might find older versions
                            continue
                        if tag and tag not in data.get("tags", []):
                            seen_ids.remove(entry_id)
                            continue

                        if not data.get("is_deleted", False):
                            active_clips.append(ClipItem.from_dict(data))
                except (OSError, json.JSONDecodeError):
                    continue
        return active_clips

    def _count_versions_sync_impl(self, version_group_id: str) -> int:
        """Count the number of non-deleted versions belonging to a group."""
        count = 0
        seen_ids: set[str] = set()
        # The parent itself counts as 1. Wait, let's tally exact occurrences correctly.
        for daily_dir in self._iter_daily_dirs_desc():
            clips_dir = daily_dir / AppConfig.CLIPPINGS_DIRNAME
            if not clips_dir.exists():
                continue

            files = sorted(clips_dir.glob("*.jsonl"), reverse=True)
            for file_path in files:
                try:
                    lines = file_path.read_text(encoding="utf-8").splitlines()
                    for line in reversed(lines):
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        entry_id = data.get("entry_id")
                        is_deleted = data.get("is_deleted", False)

                        if not entry_id or entry_id in seen_ids:
                            continue
                        seen_ids.add(entry_id)

                        # Count the parent item or any item bound as its version_of
                        if (entry_id == version_group_id or data.get("version_of") == version_group_id) and not is_deleted:
                            count += 1
                except (OSError, json.JSONDecodeError):
                    continue
        return count

    def _get_all_versions_sync(self, version_group_id: str) -> list[ClipItem]:
        """Retrieve all versions for a given clip group, chronologically ordered."""
        versions: list[ClipItem] = []
        seen_ids: set[str] = set()

        for daily_dir in self._iter_daily_dirs_desc():
            clips_dir = daily_dir / AppConfig.CLIPPINGS_DIRNAME
            if not clips_dir.exists():
                continue

            files = sorted(clips_dir.glob("*.jsonl"), reverse=True)
            for file_path in files:
                try:
                    lines = file_path.read_text(encoding="utf-8").splitlines()
                    for line in reversed(lines):
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        entry_id = data.get("entry_id")
                        is_deleted = data.get("is_deleted", False)

                        if not entry_id or entry_id in seen_ids:
                            continue
                        seen_ids.add(entry_id)

                        if (entry_id == version_group_id or data.get("version_of") == version_group_id) and not is_deleted:
                            versions.append(ClipItem.from_dict(data))
                except (OSError, json.JSONDecodeError):
                    continue

        # Sort oldest first (chronological) for diffing
        versions.sort(key=lambda item: item.timestamp)
        return versions

    def _delete_oldest_version_sync(self, version_group_id: str) -> None:
        """Find the chronologically oldest clip within a version group and kill it via tombstone."""
        oldest_clip: ClipItem | None = None
        seen_ids: set[str] = set()

        for daily_dir in self._iter_daily_dirs_desc():
            clips_dir = daily_dir / AppConfig.CLIPPINGS_DIRNAME
            if not clips_dir.exists():
                continue

            files = sorted(clips_dir.glob("*.jsonl"), reverse=True)
            for file_path in files:
                try:
                    lines = file_path.read_text(encoding="utf-8").splitlines()
                    for line in reversed(lines):
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        entry_id = data.get("entry_id")
                        is_deleted = data.get("is_deleted", False)

                        if not entry_id or entry_id in seen_ids:
                            continue
                        seen_ids.add(entry_id)

                        if (entry_id == version_group_id or data.get("version_of") == version_group_id) and not is_deleted:
                            clip = ClipItem.from_dict(data)
                            if oldest_clip is None or clip.timestamp < oldest_clip.timestamp:
                                oldest_clip = clip
                except (OSError, json.JSONDecodeError):
                    continue

        # Write the tombstone exactly onto today's file referencing the dead entry_id
        if oldest_clip:
            tombstone = ClipItem(
                entry_id=oldest_clip.entry_id,
                timestamp=datetime.now(),
                content=oldest_clip.content,
                clip_type=oldest_clip.clip_type,
                format=oldest_clip.format,
                source_url=oldest_clip.source_url,
                file_path=oldest_clip.file_path,
                version_of=oldest_clip.version_of,
                is_deleted=True
            )
            latest_clip_path = daily_dir / AppConfig.CLIPPINGS_DIRNAME / AppConfig.get_clip_filename(tombstone.timestamp)
            payload = json.dumps(tombstone.to_dict(), ensure_ascii=False)
            self._append_text_line(latest_clip_path, payload)

    def _delete_clip_sync(self, entry_id: str) -> None:
        """Write a tombstone entity deleting a clip."""
        for daily_dir in self._iter_daily_dirs_desc():
            clips_dir = daily_dir / AppConfig.CLIPPINGS_DIRNAME
            if not clips_dir.exists():
                continue

            files = sorted(clips_dir.glob("*.jsonl"), reverse=True)
            for file_path in files:
                try:
                    lines = file_path.read_text(encoding="utf-8").splitlines()
                    for line in reversed(lines):
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        if data.get("entry_id") == entry_id:
                            if data.get("is_deleted", False):
                                return  # It's already deleted

                            tombstone = ClipItem(
                                entry_id=data.get("entry_id"),
                                timestamp=datetime.now(),
                                content=data.get("content", ""),
                                clip_type=data.get("clip_type") or data.get("type", "text"),
                                format=data.get("format"),
                                source_url=data.get("source_url"),
                                file_path=Path(data["file_path"]) if data.get("file_path") else None,
                                version_of=data.get("version_of"),
                                is_deleted=True,
                                is_favorite=data.get("is_favorite", False),
                                tags=data.get("tags", [])
                            )
                            payload = json.dumps(tombstone.to_dict(), ensure_ascii=False)
                            self._append_text_line(file_path, payload)
                            logger.info("Deleted clip %s by appending tombstone to %s", entry_id, file_path)
                            return
                except (OSError, json.JSONDecodeError):
                    continue

    def _iter_daily_dirs_desc(self) -> list[Path]:
        """Return valid daily directories ordered newest first."""
        if self._daily_dirs_cache is not None:
            # We don't invalidate fully, we just ensure newest dirs are caught
            # MVP logic: we can just re-scan or trust the cache for speed.
            # For correctness let's re-scan if needed, but since SRS says "cực nhanh"
            # We will scan and cache them, assuming new dirs are added via daily paths.
            pass

        daily_dirs = [
            path
            for path in self.data_dir.iterdir()
            if path.is_dir() and self._is_date_folder(path.name)
        ]
        self._daily_dirs_cache = sorted(daily_dirs, key=lambda path: path.name, reverse=True)
        return self._daily_dirs_cache

    def _collect_daily_files(self, daily_dir: Path) -> list[Path]:
        """Collect browseable files inside a daily folder."""
        files: list[Path] = []
        for directory, pattern in (
            (daily_dir / AppConfig.IMAGES_DIRNAME, "*.png"),
            (daily_dir / AppConfig.NOTES_DIRNAME, "*.md"),
            (daily_dir / AppConfig.CLIPPINGS_DIRNAME, "*.jsonl"),
        ):
            files.extend(directory.glob(pattern))

        return sorted(files, key=self._safe_mtime, reverse=True)

    def _build_folder_entry(self, daily_dir: Path, files: list[Path]) -> BrowseEntry:
        """Create the browse entry representing a day folder."""
        timestamp = datetime.fromtimestamp(self._safe_mtime(daily_dir))
        child_preview = ", ".join(path.name for path in files[:3])
        if not child_preview:
            child_preview = "No files yet"
        content = "\n".join(path.name for path in files[:10])
        return BrowseEntry(
            entry_id=f"folder:{daily_dir.name}",
            entry_type="folder",
            label=daily_dir.name,
            path=daily_dir,
            timestamp=timestamp,
            preview=child_preview,
            content=content,
            child_count=len(files),
        )

    def _build_file_entry(self, file_path: Path) -> BrowseEntry | None:
        """Build a browse entry for a note, clip file, or image."""
        parent_name = file_path.parent.name
        timestamp = datetime.fromtimestamp(self._safe_mtime(file_path))

        if parent_name == AppConfig.IMAGES_DIRNAME:
            return BrowseEntry(
                entry_id=f"image:{file_path}",
                entry_type="image",
                label=file_path.name,
                path=file_path,
                timestamp=timestamp,
                preview="PNG image",
                content="",
            )

        if parent_name == AppConfig.NOTES_DIRNAME:
            try:
                content = file_path.read_text(encoding="utf-8")
            except OSError as exc:
                logger.warning("Skipping unreadable note file %s: %s", file_path, exc)
                return None
            return BrowseEntry(
                entry_id=f"note:{file_path}",
                entry_type="note",
                label=file_path.name,
                path=file_path,
                timestamp=timestamp,
                preview=self._build_preview(content),
                content=content,
            )

        if parent_name == AppConfig.CLIPPINGS_DIRNAME:
            summary = self._summarize_clip_file(file_path)
            return BrowseEntry(
                entry_id=f"clip_file:{file_path}",
                entry_type="clip_file",
                label=file_path.name,
                path=file_path,
                timestamp=summary["timestamp"] or timestamp,
                preview=summary["preview"],
                content=summary["content"],
            )

        return None

    def _summarize_clip_file(self, file_path: Path) -> dict[str, object]:
        """Build preview text for a clip JSONL file."""
        preview_lines: list[str] = []
        latest_timestamp: datetime | None = None
        latest_preview = file_path.name

        try:
            with file_path.open("r", encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        clip = ClipItem.from_dict(json.loads(line))
                        latest_timestamp = clip.timestamp
                        display_value = clip.content.strip()
                        if clip.clip_type == "image" and clip.file_path:
                            display_value = clip.file_path.name
                        line_preview = display_value
                        preview_lines.append(line_preview)
                        latest_preview = line_preview
                    except (json.JSONDecodeError, KeyError, ValueError) as exc:
                        logger.warning("Skipping corrupted line in %s: %s", file_path, exc)
                        continue
        except OSError as exc:
            logger.error("Failed to summarize clip file %s: %s", file_path, exc)
            return {
                "preview": file_path.name,
                "content": "Unable to read clip file.",
                "timestamp": latest_timestamp,
            }

        content = "\n".join(preview_lines[-20:])
        return {
            "preview": self._build_preview(latest_preview),
            "content": content,
            "timestamp": latest_timestamp,
        }

    def _create_daily_folder_sync(self, daily_dir: Path) -> None:
        """Synchronously create the daily directory structure."""
        (daily_dir / AppConfig.CLIPPINGS_DIRNAME).mkdir(parents=True, exist_ok=True)
        (daily_dir / AppConfig.IMAGES_DIRNAME).mkdir(parents=True, exist_ok=True)
        (daily_dir / AppConfig.NOTES_DIRNAME).mkdir(parents=True, exist_ok=True)
        # Invalidate cache so it gets re-scanned next time
        self._daily_dirs_cache = None

    @staticmethod
    def _append_text_line(path: Path, payload: str) -> None:
        """Append a single line to a text file."""
        try:
            with path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.write("\n")
        except OSError as exc:
            logger.error("Failed to append clip payload to %s: %s", path, exc)
            raise StorageError(f"Unable to append clip to {path}.") from exc

    @staticmethod
    def _write_text(path: Path, content: str) -> None:
        """Write text content to disk."""
        try:
            path.write_text(content, encoding="utf-8", newline="\n")
        except OSError as exc:
            raise StorageError(f"Unable to write text file {path}.") from exc

    @staticmethod
    def _write_bytes(path: Path, content: bytes) -> None:
        """Write binary content to disk."""
        try:
            path.write_bytes(content)
        except OSError as exc:
            raise StorageError(f"Unable to write binary file {path}.") from exc

    @staticmethod
    def _read_note(path: Path, date_str: str) -> DailyNote:
        """Read a note file and reconstruct metadata from filesystem timestamps."""
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Unable to read note file {path}.") from exc

        stat = path.stat()
        return DailyNote(
            date=date_str,
            content=content,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            updated_at=datetime.fromtimestamp(stat.st_mtime),
        )

    @staticmethod
    def _read_clip_files(files: list[Path]) -> list[ClipItem]:
        """Read and deserialize active clips from multiple JSONL files."""
        # Using a map over `entry_id` resolves deleted supersessions automatically
        clips_map: dict[str, ClipItem] = {}
        for file_path in files:
            try:
                with file_path.open("r", encoding="utf-8") as handle:
                    for raw_line in handle:
                        line = raw_line.strip()
                        if not line:
                            continue
                        data = json.loads(line)
                        clip = ClipItem.from_dict(data)

                        if clip.is_deleted:
                            clips_map.pop(clip.entry_id, None)
                        else:
                            clips_map[clip.entry_id] = clip
            except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning("Skipping invalid clip file %s: %s", file_path, exc)

        clips = list(clips_map.values())
        clips.sort(key=lambda item: item.timestamp)
        return clips

    @staticmethod
    def _ensure_unique_path(path: Path) -> Path:
        """Return a unique path by appending a numeric suffix if required."""
        if not path.exists():
            return path

        index = 1
        while True:
            candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")
            if not candidate.exists():
                return candidate
            index += 1

    @staticmethod
    def _build_preview(content: str, limit: int = 120) -> str:
        """Create a compact preview string for browse-mode rendering."""
        normalized = " ".join(content.split())
        if len(normalized) <= limit:
            return normalized
        return f"{normalized[:limit].rstrip()}..."

    @staticmethod
    def _safe_mtime(path: Path) -> float:
        """Return the best-effort modification time for sorting."""
        try:
            return path.stat().st_mtime
        except OSError:
            return 0.0

    @staticmethod
    def _is_date_folder(name: str) -> bool:
        """Return whether a folder name matches YYYY-MM-DD."""
        try:
            datetime.strptime(name, "%Y-%m-%d")
        except ValueError:
            return False
        return True
