"""DuckDB-backed search implementation for DailyClip."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import duckdb

from DailyClip.core.config import AppConfig
from DailyClip.core.entities import ClipItem, DailyNote, SearchResult
from DailyClip.core.exceptions import SearchIndexError
from DailyClip.core.interfaces import ISearchService

logger = logging.getLogger(__name__)


class DuckDBSearchService(ISearchService):
    """Unified search index over clips and notes."""

    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = Path(storage_path) if storage_path else AppConfig.get_data_dir()
        self.db_path = self.storage_path / AppConfig.INDEX_FILENAME

    async def rebuild_index(self) -> None:
        """Rebuild the unified index from persisted content."""
        await asyncio.to_thread(self._initialize_database)
        await asyncio.to_thread(self._rebuild_index_sync)
        logger.info('Rebuilt search index at %s', self.db_path)

    async def search(self, query: str, limit: int = 50) -> list[SearchResult]:
        """Query the unified index using case-insensitive substring matching."""
        normalized_query = query.strip()
        if not normalized_query:
            return []

        await asyncio.to_thread(self._initialize_database)
        return await asyncio.to_thread(self._search_sync, normalized_query, limit)

    async def index_clip(self, clip: ClipItem) -> None:
        """Incrementally index a clip."""
        await asyncio.to_thread(self._initialize_database)
        await asyncio.to_thread(self._upsert_clip_sync, clip)

    async def index_note(self, note: DailyNote) -> None:
        """Incrementally index a note."""
        await asyncio.to_thread(self._initialize_database)
        await asyncio.to_thread(self._upsert_note_sync, note)

    def _initialize_database(self) -> None:
        """Ensure the database schema exists."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        with duckdb.connect(str(self.db_path)) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS search_entries (
                    entry_id VARCHAR PRIMARY KEY,
                    entry_type VARCHAR NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    date_str VARCHAR NOT NULL,
                    content TEXT NOT NULL,
                    preview TEXT NOT NULL,
                    file_path VARCHAR,
                    source_url VARCHAR,
                    score DOUBLE DEFAULT 1.0
                )
                """
            )
            connection.execute(
                'CREATE INDEX IF NOT EXISTS idx_search_entries_timestamp '
                'ON search_entries(timestamp)'
            )
            connection.execute(
                'CREATE INDEX IF NOT EXISTS idx_search_entries_date '
                'ON search_entries(date_str)'
            )

    def _rebuild_index_sync(self) -> None:
        """Synchronously rebuild the index from disk."""
        with duckdb.connect(str(self.db_path)) as connection:
            connection.execute('DELETE FROM search_entries')

            for daily_dir in sorted(self.storage_path.iterdir()):
                if not daily_dir.is_dir() or not self._is_date_folder(daily_dir.name):
                    continue

                clips_dir = daily_dir / AppConfig.CLIPPINGS_DIRNAME
                for clip_file in sorted(clips_dir.glob('*.jsonl')):
                    self._index_clip_file(connection, clip_file)

                note_path = (
                    daily_dir
                    / AppConfig.NOTES_DIRNAME
                    / AppConfig.get_note_filename(daily_dir.name)
                )
                if note_path.exists():
                    self._index_note_file(connection, note_path, daily_dir.name)

    def _search_sync(self, query: str, limit: int) -> list[SearchResult]:
        """Synchronously query the DuckDB index."""
        try:
            with duckdb.connect(str(self.db_path), read_only=True) as connection:
                rows = connection.execute(
                    """
                    SELECT
                        entry_id,
                        entry_type,
                        timestamp,
                        content,
                        preview,
                        file_path,
                        source_url,
                        score
                    FROM search_entries
                    WHERE lower(content) LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    [f'%{query.lower()}%', limit],
                ).fetchall()
        except duckdb.Error as exc:
            raise SearchIndexError('Failed to execute search query.') from exc

        return [
            SearchResult(
                entry_id=row[0],
                entry_type=row[1],
                timestamp=row[2],
                content=row[3],
                preview=row[4],
                file_path=Path(row[5]) if row[5] else None,
                source_url=row[6],
                score=float(row[7] or 1.0),
            )
            for row in rows
        ]

    def _upsert_clip_sync(self, clip: ClipItem) -> None:
        """Synchronously upsert a clip entry."""
        entry_id = self._build_clip_entry_id(clip)
        preview = self._build_preview(clip.content)
        with duckdb.connect(str(self.db_path)) as connection:
            try:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO search_entries (
                        entry_id,
                        entry_type,
                        timestamp,
                        date_str,
                        content,
                        preview,
                        file_path,
                        source_url,
                        score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        entry_id,
                        'clip',
                        clip.timestamp,
                        clip.timestamp.strftime('%Y-%m-%d'),
                        clip.content,
                        preview,
                        str(clip.file_path) if clip.file_path else None,
                        clip.source_url,
                        1.0,
                    ],
                )
            except duckdb.Error as exc:
                raise SearchIndexError('Failed to index clip entry.') from exc

    def _upsert_note_sync(self, note: DailyNote) -> None:
        """Synchronously upsert a note entry."""
        note_path = (
            self.storage_path
            / note.date
            / AppConfig.NOTES_DIRNAME
            / AppConfig.get_note_filename(note.date)
        )
        with duckdb.connect(str(self.db_path)) as connection:
            try:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO search_entries (
                        entry_id,
                        entry_type,
                        timestamp,
                        date_str,
                        content,
                        preview,
                        file_path,
                        source_url,
                        score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        f'note:{note.date}',
                        'note',
                        note.updated_at,
                        note.date,
                        note.content,
                        self._build_preview(note.content),
                        str(note_path),
                        None,
                        1.0,
                    ],
                )
            except duckdb.Error as exc:
                raise SearchIndexError('Failed to index note entry.') from exc

    def _index_clip_file(self, connection: duckdb.DuckDBPyConnection, clip_file: Path) -> None:
        """Read a clip file and upsert all contained entries."""
        try:
            with clip_file.open('r', encoding='utf-8') as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    clip = replace(ClipItem.from_dict(data), file_path=clip_file)
                    connection.execute(
                        """
                        INSERT OR REPLACE INTO search_entries (
                            entry_id,
                            entry_type,
                            timestamp,
                            date_str,
                            content,
                            preview,
                            file_path,
                            source_url,
                            score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            self._build_clip_entry_id(clip),
                            'clip',
                            clip.timestamp,
                            clip.timestamp.strftime('%Y-%m-%d'),
                            clip.content,
                            self._build_preview(clip.content),
                            str(clip_file),
                            clip.source_url,
                            1.0,
                        ],
                    )
        except (OSError, ValueError, json.JSONDecodeError, duckdb.Error) as exc:
            logger.warning('Skipping clip file %s during reindex: %s', clip_file, exc)

    def _index_note_file(
        self,
        connection: duckdb.DuckDBPyConnection,
        note_path: Path,
        date_str: str,
    ) -> None:
        """Read a note file and upsert its single entry."""
        try:
            content = note_path.read_text(encoding='utf-8')
            stat = note_path.stat()
            timestamp = datetime.fromtimestamp(stat.st_mtime)
            connection.execute(
                """
                INSERT OR REPLACE INTO search_entries (
                    entry_id,
                    entry_type,
                    timestamp,
                    date_str,
                    content,
                    preview,
                    file_path,
                    source_url,
                    score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    f'note:{date_str}',
                    'note',
                    timestamp,
                    date_str,
                    content,
                    self._build_preview(content),
                    str(note_path),
                    None,
                    1.0,
                ],
            )
        except (OSError, duckdb.Error) as exc:
            logger.warning('Skipping note file %s during reindex: %s', note_path, exc)

    @staticmethod
    def _build_preview(content: str, limit: int = 120) -> str:
        """Create a compact preview string for UI rendering."""
        normalized = ' '.join(content.split())
        if len(normalized) <= limit:
            return normalized
        return f'{normalized[:limit].rstrip()}...'

    @staticmethod
    def _is_date_folder(name: str) -> bool:
        """Return whether a folder name matches YYYY-MM-DD."""
        try:
            datetime.strptime(name, '%Y-%m-%d')
        except ValueError:
            return False
        return True

    @staticmethod
    def _build_clip_entry_id(clip: ClipItem) -> str:
        """Build a stable entry identifier for a clip."""
        digest = hashlib.sha1(
            f'{clip.timestamp.isoformat()}:{clip.content}'.encode('utf-8')
        ).hexdigest()
        return f'clip:{digest}'
