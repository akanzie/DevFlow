"""File storage implementation for DailyClip."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from DailyClip.core.config import AppConfig
from DailyClip.core.entities import ClipItem, DailyNote
from DailyClip.core.exceptions import StorageError
from DailyClip.core.interfaces import IStorageService

logger = logging.getLogger(__name__)


class FileStorageService(IStorageService):
    """Persist clips, notes, and screenshots using the SRS folder layout."""

    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else AppConfig.get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)

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
        logger.info('Persisted clip to %s', clips_path)
        return clips_path

    async def get_clips_for_date(self, date_str: str) -> list[ClipItem]:
        """Load all clips for a specific date."""
        daily_dir = self.data_dir / date_str / AppConfig.CLIPPINGS_DIRNAME
        if not daily_dir.exists():
            return []

        files = sorted(daily_dir.glob('*.jsonl'))
        return await asyncio.to_thread(self._read_clip_files, files)

    async def save_note(self, note: DailyNote) -> Path:
        """Persist the note for the provided date."""
        note_path = await self._get_note_path(note.date)
        await asyncio.to_thread(self._write_text, note_path, note.content)
        logger.info('Persisted note to %s', note_path)
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
        daily_dir = await self.create_daily_folder(timestamp.strftime('%Y-%m-%d'))
        images_dir = daily_dir / AppConfig.IMAGES_DIRNAME
        image_path = await asyncio.to_thread(
            self._ensure_unique_path,
            images_dir / AppConfig.get_screenshot_filename(timestamp),
        )
        await asyncio.to_thread(self._write_bytes, image_path, image_data)
        logger.info('Persisted screenshot to %s', image_path)
        return image_path

    async def _get_clip_path(self, timestamp: datetime) -> Path:
        """Resolve the clip file path for a timestamp."""
        daily_dir = await self.create_daily_folder(timestamp.strftime('%Y-%m-%d'))
        return daily_dir / AppConfig.CLIPPINGS_DIRNAME / AppConfig.get_clip_filename(timestamp)

    async def _get_note_path(self, date_str: str) -> Path:
        """Resolve the note file path for a date."""
        daily_dir = await self.create_daily_folder(date_str)
        return daily_dir / AppConfig.NOTES_DIRNAME / AppConfig.get_note_filename(date_str)

    @staticmethod
    def _create_daily_folder_sync(daily_dir: Path) -> None:
        """Synchronously create the daily directory structure."""
        (daily_dir / AppConfig.CLIPPINGS_DIRNAME).mkdir(parents=True, exist_ok=True)
        (daily_dir / AppConfig.IMAGES_DIRNAME).mkdir(parents=True, exist_ok=True)
        (daily_dir / AppConfig.NOTES_DIRNAME).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _append_text_line(path: Path, payload: str) -> None:
        """Append a single line to a text file."""
        try:
            with path.open('a', encoding='utf-8', newline='\n') as handle:
                handle.write(payload)
                handle.write('\n')
        except OSError as exc:
            raise StorageError(f'Unable to append clip to {path}.') from exc

    @staticmethod
    def _write_text(path: Path, content: str) -> None:
        """Write text content to disk."""
        try:
            path.write_text(content, encoding='utf-8', newline='\n')
        except OSError as exc:
            raise StorageError(f'Unable to write text file {path}.') from exc

    @staticmethod
    def _write_bytes(path: Path, content: bytes) -> None:
        """Write binary content to disk."""
        try:
            path.write_bytes(content)
        except OSError as exc:
            raise StorageError(f'Unable to write binary file {path}.') from exc

    @staticmethod
    def _read_note(path: Path, date_str: str) -> DailyNote:
        """Read a note file and reconstruct metadata from filesystem timestamps."""
        try:
            content = path.read_text(encoding='utf-8')
        except OSError as exc:
            raise StorageError(f'Unable to read note file {path}.') from exc

        stat = path.stat()
        return DailyNote(
            date=date_str,
            content=content,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            updated_at=datetime.fromtimestamp(stat.st_mtime),
        )

    @staticmethod
    def _read_clip_files(files: list[Path]) -> list[ClipItem]:
        """Read and deserialize clips from multiple JSONL files."""
        clips: list[ClipItem] = []
        for file_path in files:
            try:
                with file_path.open('r', encoding='utf-8') as handle:
                    for raw_line in handle:
                        line = raw_line.strip()
                        if not line:
                            continue
                        data = json.loads(line)
                        clip = ClipItem.from_dict(data)
                        clips.append(clip)
            except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning('Skipping invalid clip file %s: %s', file_path, exc)
        clips.sort(key=lambda item: item.timestamp)
        return clips

    @staticmethod
    def _ensure_unique_path(path: Path) -> Path:
        """Return a unique path by appending a numeric suffix if required."""
        if not path.exists():
            return path

        index = 1
        while True:
            candidate = path.with_name(f'{path.stem}_{index}{path.suffix}')
            if not candidate.exists():
                return candidate
            index += 1
