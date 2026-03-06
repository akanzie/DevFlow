"""
DuckDB search service implementation for DailyClip
Full-text search with indexing capabilities
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import duckdb
import json
from typing import List, Optional
from datetime import datetime
import asyncio
import aiofiles

from core.entities import ClipItem, SearchResult, DailyNote
from core.interfaces import ISearchService
from core.config import AppConfig

class DuckDBSearchService(ISearchService):
    """DuckDB-based search implementation with full-text indexing"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or AppConfig.get_data_dir()
        self.db_path = self.storage_path / "search_index.duckdb"
        self.conn = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize DuckDB connection and tables"""
        if self._initialized:
            return
            
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create connection in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._setup_database)
        
        self._initialized = True
        
    def _setup_database(self):
        """Setup database tables (synchronous)"""
        self.conn = duckdb.connect(str(self.db_path))
        
        # Create clips table with full-text search
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS clips (
                id VARCHAR PRIMARY KEY,
                timestamp TIMESTAMP,
                content TEXT,
                clip_type VARCHAR,
                format VARCHAR,
                source_url VARCHAR,
                file_path VARCHAR,
                date_str VARCHAR
            )
        """)
        
        # Create notes table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id VARCHAR PRIMARY KEY,
                date_str VARCHAR,
                content TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Create full-text search index
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_clips_content ON clips USING fts(content)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_notes_content ON notes USING fts(content)
        """)
        
        # Create timestamp indexes for performance
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_clips_timestamp ON clips(timestamp DESC)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_clips_date ON clips(date_str)
        """)
        
    async def build_index(self) -> None:
        """Build search index from existing data"""
        await self.initialize()
        
        print("🔍 Building search index from existing data...")
        
        # Scan all daily folders for clips and notes
        tasks = []
        for item in self.storage_path.iterdir():
            if item.is_dir() and self._is_date_folder(item.name):
                tasks.append(self._index_date_folder(item.name))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"✅ Search index built successfully")
        
    def _is_date_folder(self, name: str) -> bool:
        """Check if folder name is a date (YYYY-MM-DD format)"""
        try:
            datetime.strptime(name, "%Y-%m-%d")
            return True
        except ValueError:
            return False
            
    async def _index_date_folder(self, date_str: str) -> None:
        """Index all data for a specific date"""
        try:
            daily_dir = self.storage_path / date_str
            
            # Index clips
            clips_file = daily_dir / "clippings" / AppConfig.CLIPS_FILENAME
            if clips_file.exists():
                async with aiofiles.open(clips_file, 'r', encoding='utf-8') as f:
                    async for line in f:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                clip = ClipItem.from_dict(data)
                                await self.add_clip_to_index(clip)
                            except (json.JSONDecodeError, KeyError):
                                continue
            
            # Index notes
            notes_file = daily_dir / "notes" / AppConfig.NOTES_FILENAME.format(date=date_str)
            if notes_file.exists():
                async with aiofiles.open(notes_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if content.strip():
                        note = DailyNote(
                            date=date_str,
                            content=content,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        await self.add_note_to_index(note)
                        
        except Exception as e:
            print(f"⚠️ Error indexing {date_str}: {e}")
    
    async def search(self, query: str, limit: int = 50) -> List[SearchResult]:
        """Search clips and notes"""
        await self.initialize()
        
        if not query.strip():
            return []
        
        # Escape query for safety
        safe_query = query.replace("'", "''")
        
        # Search clips
        clips_query = f"""
            SELECT id, timestamp, content, clip_type, format, source_url, file_path, 
                   fts_main_clips.match_bm25(id, ?) as score
            FROM clips
            WHERE content LIKE '%{safe_query}%'
            ORDER BY score DESC, timestamp DESC
            LIMIT ?
        """
        
        # Search notes  
        notes_query = f"""
            SELECT id, date_str, content, created_at, updated_at,
                   fts_main_notes.match_bm25(id, ?) as score
            FROM notes
            WHERE content LIKE '%{safe_query}%'
            ORDER BY score DESC, updated_at DESC
            LIMIT ?
        """
        
        results = []
        
        try:
            # Execute searches in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Search clips
            clips_results = await loop.run_in_executor(
                None, 
                lambda: self.conn.execute(clips_query, [query, limit]).fetchall()
            )
            
            for row in clips_results:
                clip = ClipItem(
                    timestamp=row[1],
                    content=row[2],
                    clip_type=row[3],
                    format=row[4],
                    source_url=row[5],
                    file_path=Path(row[6]) if row[6] else None
                )
                
                # Create preview (first 100 chars)
                preview = row[2][:100] + ("..." if len(row[2]) > 100 else "")
                
                results.append(SearchResult(
                    clip=clip,
                    score=float(row[7]) if row[7] else 0.0,
                    preview=preview
                ))
            
            # Search notes
            notes_results = await loop.run_in_executor(
                None,
                lambda: self.conn.execute(notes_query, [query, limit]).fetchall()
            )
            
            for row in notes_results:
                note = DailyNote(
                    date=row[1],
                    content=row[2],
                    created_at=row[3],
                    updated_at=row[4]
                )
                
                # Create preview
                preview = row[2][:100] + ("..." if len(row[2]) > 100 else "")
                
                # Convert note to clip-like format for unified results
                clip_item = ClipItem(
                    timestamp=row[4],  # Use updated_at as timestamp
                    content=row[2],
                    clip_type="text",
                    format="markdown",
                    source_url=None,
                    file_path=None
                )
                
                results.append(SearchResult(
                    clip=clip_item,
                    score=float(row[5]) if row[5] else 0.0,
                    preview=f"[Note] {preview}"
                ))
            
            # Sort by score and timestamp
            results.sort(key=lambda x: (-x.score, -x.clip.timestamp.timestamp()))
            
            # Remove duplicates and limit
            seen = set()
            unique_results = []
            for result in results:
                key = (result.clip.content[:50], result.clip.timestamp)
                if key not in seen:
                    seen.add(key)
                    unique_results.append(result)
                    if len(unique_results) >= limit:
                        break
            
            return unique_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    async def add_clip_to_index(self, clip: ClipItem) -> None:
        """Add single clip to search index"""
        await self.initialize()
        
        try:
            clip_id = f"clip_{clip.timestamp.isoformat()}"
            date_str = clip.timestamp.strftime("%Y-%m-%d")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.conn.execute("""
                INSERT OR REPLACE INTO clips 
                (id, timestamp, content, clip_type, format, source_url, file_path, date_str)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                clip_id,
                clip.timestamp,
                clip.content,
                clip.clip_type,
                clip.format,
                clip.source_url,
                str(clip.file_path) if clip.file_path else None,
                date_str
            ]))
            
        except Exception as e:
            print(f"⚠️ Error adding clip to index: {e}")
    
    async def add_note_to_index(self, note: DailyNote) -> None:
        """Add note to search index"""
        await self.initialize()
        
        try:
            note_id = f"note_{note.date}"
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.conn.execute("""
                INSERT OR REPLACE INTO notes 
                (id, date_str, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, [
                note_id,
                note.date,
                note.content,
                note.created_at,
                note.updated_at
            ]))
            
        except Exception as e:
            print(f"⚠️ Error adding note to index: {e}")
    
    async def remove_from_index(self, item_id: str) -> None:
        """Remove item from search index"""
        await self.initialize()
        
        try:
            if item_id.startswith("clip_"):
                table = "clips"
            elif item_id.startswith("note_"):
                table = "notes"
            else:
                return
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.conn.execute(f"""
                DELETE FROM {table} WHERE id = ?
            """, [item_id]))
            
        except Exception as e:
            print(f"⚠️ Error removing from index: {e}")
    
    async def get_stats(self) -> dict:
        """Get search index statistics"""
        await self.initialize()
        
        try:
            loop = asyncio.get_event_loop()
            
            clips_count = await loop.run_in_executor(
                None, 
                lambda: self.conn.execute("SELECT COUNT(*) FROM clips").fetchone()[0]
            )
            
            notes_count = await loop.run_in_executor(
                None,
                lambda: self.conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
            )
            
            return {
                "clips_indexed": clips_count,
                "notes_indexed": notes_count,
                "total_items": clips_count + notes_count,
                "index_path": str(self.db_path)
            }
            
        except Exception as e:
            print(f"⚠️ Error getting stats: {e}")
            return {"error": str(e)}
    
    def __del__(self):
        """Cleanup database connection"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
