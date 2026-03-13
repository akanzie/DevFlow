"""DuckDB-backed search implementation for DailyClip."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import threading
from datetime import datetime
from pathlib import Path

import duckdb
from filelock import FileLock

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
        self._lock = threading.Lock()
        self._conn = None
        
    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        """Lazily load the duckdb connection."""
        if self._conn is None:
            self._initialize_database()
        return self._conn

    def close(self) -> None:
        """Close connection to backend index storage."""
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def rebuild_index(self) -> None:
        """Rebuild the unified index from persisted content."""
        await asyncio.to_thread(self._rebuild_index_sync)
        logger.info("Rebuilt search index at %s", self.db_path)

    async def search(self, query: str, limit: int = 50) -> list[SearchResult]:
        """Query the unified index using FTS."""
        normalized_query = query.strip()
        if not normalized_query:
            return []

        return await asyncio.to_thread(self._search_sync, normalized_query, limit)

    async def index_clip(self, clip: ClipItem) -> None:
        """Incrementally index a clip."""
        await asyncio.to_thread(self._upsert_clip_sync, clip)

    async def index_note(self, note: DailyNote) -> None:
        """Incrementally index a note."""
        await asyncio.to_thread(self._upsert_note_sync, note)

    async def index_clips(self, clips: list[ClipItem]) -> None:
        """Incrementally index multiple clips."""
        if not clips:
            return
        await asyncio.to_thread(self._upsert_clips_sync, clips)

    async def index_notes(self, notes: list[DailyNote]) -> None:
        """Incrementally index multiple notes."""
        if not notes:
            return
        await asyncio.to_thread(self._upsert_notes_sync, notes)

    def _initialize_database(self) -> None:
        """Ensure the database schema exists."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        lock_path = self.db_path.with_suffix(".lock")
        
        with FileLock(lock_path):
            self._conn = duckdb.connect(str(self.db_path))
            
            self._conn.execute("INSTALL fts;")
            self._conn.execute("LOAD fts;")
            
            self._conn.execute(
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
                    score DOUBLE DEFAULT 1.0,
                    version_of VARCHAR,
                    is_deleted BOOLEAN DEFAULT FALSE
                )
                """
            )
            try:
                self._conn.execute("ALTER TABLE search_entries ADD COLUMN version_of VARCHAR")
            except duckdb.Error:
                pass

            try:
                self._conn.execute("ALTER TABLE search_entries ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE")
            except duckdb.Error:
                pass
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_search_entries_timestamp "
                "ON search_entries(timestamp)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_search_entries_date "
                "ON search_entries(date_str)"
            )
            
            self._conn.execute(
                "PRAGMA create_fts_index('search_entries', 'entry_id', 'content', 'preview', overwrite=1)"
            )

    def _rebuild_index_sync(self) -> None:
        """Synchronously rebuild the index from disk."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("PRAGMA drop_fts_index('search_entries')")
            except duckdb.Error:
                pass
            cursor.execute("DELETE FROM search_entries")

            for daily_dir in sorted(self.storage_path.iterdir()):
                if not daily_dir.is_dir() or not self._is_date_folder(daily_dir.name):
                    continue

                clips_dir = daily_dir / AppConfig.CLIPPINGS_DIRNAME
                for clip_file in sorted(clips_dir.glob("*.jsonl")):
                    self._index_clip_file(cursor, clip_file)

                note_path = (
                    daily_dir
                    / AppConfig.NOTES_DIRNAME
                    / AppConfig.get_note_filename(daily_dir.name)
                )
                if note_path.exists():
                    self._index_note_file(cursor, note_path, daily_dir.name)
                    
            cursor.execute(
                "PRAGMA create_fts_index('search_entries', 'entry_id', 'content', 'preview')"
            )
            cursor.close()

    def _search_sync(self, query: str, limit: int) -> list[SearchResult]:
        """Synchronously query the DuckDB FTS index."""
        try:
            with self._lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                rows = cursor.execute(
                    """
                    SELECT
                        entry_id,
                        entry_type,
                        timestamp,
                        content,
                        preview,
                        file_path,
                        source_url,
                        version_of,
                        is_deleted,
                        fts_main_search_entries.match_bm25(entry_id, ?) AS score
                    FROM search_entries
                    WHERE score IS NOT NULL AND is_deleted = FALSE
                    ORDER BY score DESC, timestamp DESC
                    LIMIT ?
                    """,
                    [query, limit],
                ).fetchall()
                cursor.close()
        except duckdb.Error as exc:
            raise SearchIndexError("Failed to execute search query.") from exc

        return [
            SearchResult(
                entry_id=row[0],
                entry_type=row[1],
                timestamp=row[2],
                content=row[3],
                preview=row[4],
                file_path=Path(row[5]) if row[5] else None,
                source_url=row[6],
                score=float(row[9] or 1.0),
            )
            for row in rows
        ]

    def _upsert_clip_sync(self, clip: ClipItem) -> None:
        """Synchronously upsert a clip entry."""
        self._upsert_clips_sync([clip])

    def _upsert_clips_sync(self, clips: list[ClipItem]) -> None:
        """Synchronously upsert multiple clip entries."""
        records = []
        for clip in clips:
            if not clip.content.strip():
                continue
            entry_id = self._build_clip_entry_id(clip)
            preview = self._build_preview(clip.content)
            records.append((
                entry_id,
                "clip",
                clip.timestamp,
                clip.timestamp.strftime("%Y-%m-%d"),
                clip.content,
                preview,
                str(clip.file_path) if clip.file_path else None,
                clip.source_url,
                1.0,
                clip.version_of,
                clip.is_deleted,
            ))
            
        if not records:
            return
            
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("PRAGMA drop_fts_index('search_entries')")
                except duckdb.Error:
                    pass
                cursor.executemany(
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
                        score,
                        version_of,
                        is_deleted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    records,
                )
                cursor.execute(
                    "PRAGMA create_fts_index('search_entries', 'entry_id', 'content', 'preview')"
                )
                cursor.close()
            except duckdb.Error as exc:
                raise SearchIndexError("Failed to insert clip entries.") from exc

    def _upsert_note_sync(self, note: DailyNote) -> None:
        """Synchronously upsert a note entry."""
        self._upsert_notes_sync([note])

    def _upsert_notes_sync(self, notes: list[DailyNote]) -> None:
        """Synchronously upsert multiple note entries."""
        records = []
        for note in notes:
            if not note.content.strip():
                continue
            note_path = (
                self.storage_path
                / note.date
                / AppConfig.NOTES_DIRNAME
                / AppConfig.get_note_filename(note.date)
            )
            records.append((
                f"note:{note.date}",
                "note",
                note.updated_at,
                note.date,
                note.content,
                self._build_preview(note.content),
                str(note_path),
                None,
                1.0,
                None,
                False,
            ))
            
        if not records:
            return

        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("PRAGMA drop_fts_index('search_entries')")
                except duckdb.Error:
                    pass
                cursor.executemany(
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
                        score,
                        version_of,
                        is_deleted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    records,
                )
                cursor.execute(
                    "PRAGMA create_fts_index('search_entries', 'entry_id', 'content', 'preview')"
                )
                cursor.close()
            except duckdb.Error as exc:
                raise SearchIndexError("Failed to index note entries.") from exc

    def _index_clip_file(self, cursor: duckdb.DuckDBPyConnection, clip_file: Path) -> None:
        """Read a clip file and chunk-upsert all contained entries."""
        try:
            records = []
            chunk_size = 500
            
            with clip_file.open("r", encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line:
                        continue
                    clip = ClipItem.from_dict(json.loads(line))
                    if not clip.content.strip():
                        continue
                    persisted_path = clip.file_path or clip_file
                    
                    records.append((
                        self._build_clip_entry_id(clip),
                        "clip",
                        clip.timestamp,
                        clip.timestamp.strftime("%Y-%m-%d"),
                        clip.content,
                        self._build_preview(clip.content),
                        str(persisted_path),
                        clip.source_url,
                        1.0,
                        clip.version_of,
                        clip.is_deleted,
                    ))
                    
                    if len(records) >= chunk_size:
                        cursor.executemany(
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
                                score,
                                version_of,
                                is_deleted
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            records,
                        )
                        records.clear()
                        
            if records:
                cursor.executemany(
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
                        score,
                        version_of,
                        is_deleted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    records,
                )
        except (OSError, ValueError, json.JSONDecodeError, duckdb.Error) as exc:
            logger.warning("Skipping clip file %s during reindex: %s", clip_file, exc)

    def _index_note_file(
        self,
        cursor: duckdb.DuckDBPyConnection,
        note_path: Path,
        date_str: str,
    ) -> None:
        """Read a note file and upsert its single entry."""
        try:
            content = note_path.read_text(encoding="utf-8")
            if not content.strip():
                return
            stat = note_path.stat()
            timestamp = datetime.fromtimestamp(stat.st_mtime)
            cursor.execute(
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
                    score,
                    version_of,
                    is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    f"note:{date_str}",
                    "note",
                    timestamp,
                    date_str,
                    content,
                    self._build_preview(content),
                    str(note_path),
                    None,
                    1.0,
                    None,
                    False,
                ],
            )
        except (OSError, duckdb.Error) as exc:
            logger.warning("Skipping note file %s during reindex: %s", note_path, exc)

    @staticmethod
    def _build_preview(content: str, limit: int = 120) -> str:
        """Create a compact preview string for UI rendering."""
        normalized = " ".join(content.split())
        if len(normalized) <= limit:
            return normalized
        return f"{normalized[:limit].rstrip()}..."

    @staticmethod
    def _is_date_folder(name: str) -> bool:
        """Return whether a folder name matches YYYY-MM-DD."""
        try:
            datetime.strptime(name, "%Y-%m-%d")
        except ValueError:
            return False
        return True

    @staticmethod
    def _build_clip_entry_id(clip: ClipItem) -> str:
        """Build a stable entry identifier for a clip."""
        normalized_content = "\n".join(
            line.rstrip() for line in clip.content.splitlines()
        ).strip()
        digest = hashlib.sha1(
            f"{clip.timestamp.isoformat()}:{normalized_content}".encode("utf-8")
        ).hexdigest()
        return f"clip:{digest}"
