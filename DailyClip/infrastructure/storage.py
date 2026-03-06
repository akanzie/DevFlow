"""
Storage service implementation for DailyClip
Handles file-based persistence with JSONL format
"""

import json
import aiofiles
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.entities import ClipItem, DailyNote
from core.interfaces import IStorageService
from core.config import AppConfig

class FileStorageService(IStorageService):
    """File-based storage implementation using JSONL format"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or AppConfig.get_data_dir()
        self._ensure_data_dir()
    
    def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_daily_folder(self, date_str: str) -> Path:
        """Create daily folder structure"""
        daily_dir = self.data_dir / date_str
        
        # Create subdirectories
        (daily_dir / "clippings").mkdir(parents=True, exist_ok=True)
        (daily_dir / "images").mkdir(parents=True, exist_ok=True)
        (daily_dir / "notes").mkdir(parents=True, exist_ok=True)
        (daily_dir / "index").mkdir(parents=True, exist_ok=True)
        
        return daily_dir
    
    async def append_clip(self, clip: ClipItem) -> None:
        """Append clip to daily JSONL file"""
        date_str = clip.timestamp.strftime("%Y-%m-%d")
        daily_dir = await self.create_daily_folder(date_str)
        
        clips_file = daily_dir / "clippings" / AppConfig.CLIPS_FILENAME
        
        # Append to JSONL file
        async with aiofiles.open(clips_file, 'a', encoding='utf-8') as f:
            json_line = json.dumps(clip.to_dict(), ensure_ascii=False)
            await f.write(json_line + '\n')
    
    async def get_clips_for_date(self, date_str: str) -> List[ClipItem]:
        """Get all clips for specific date"""
        daily_dir = self.data_dir / date_str
        clips_file = daily_dir / "clippings" / AppConfig.CLIPS_FILENAME
        
        if not clips_file.exists():
            return []
        
        clips = []
        async with aiofiles.open(clips_file, 'r', encoding='utf-8') as f:
            async for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        clip = ClipItem.from_dict(data)
                        clips.append(clip)
                    except (json.JSONDecodeError, KeyError) as e:
                        # Log error but continue processing
                        print(f"Error parsing clip: {e}")
                        continue
        
        return clips
    
    async def save_note(self, note: DailyNote) -> None:
        """Save daily note"""
        daily_dir = await self.create_daily_folder(note.date)
        notes_dir = daily_dir / "notes"
        
        note_filename = AppConfig.NOTES_FILENAME.format(date=note.date)
        note_file = notes_dir / note_filename
        
        async with aiofiles.open(note_file, 'w', encoding='utf-8') as f:
            await f.write(note.content)
    
    async def get_note(self, date_str: str) -> Optional[DailyNote]:
        """Get daily note"""
        daily_dir = self.data_dir / date_str
        notes_dir = daily_dir / "notes"
        
        note_filename = AppConfig.NOTES_FILENAME.format(date=date_str)
        note_file = notes_dir / note_filename
        
        if not note_file.exists():
            return None
        
        async with aiofiles.open(note_file, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        file_stat = os.stat(note_file)
        created_at = datetime.fromtimestamp(file_stat.st_ctime)
        updated_at = datetime.fromtimestamp(file_stat.st_mtime)
        
        return DailyNote(
            date=date_str,
            content=content,
            created_at=created_at,
            updated_at=updated_at
        )
    
    async def save_screenshot(self, image_data: bytes) -> Path:
        """Save screenshot and return file path"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        daily_dir = await self.create_daily_folder(date_str)
        images_dir = daily_dir / "images"
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%H-%M-%S-%f")[:-3]
        filename = f"{AppConfig.SCREENSHOT_PREFIX}{timestamp}.png"
        image_file = images_dir / filename
        
        async with aiofiles.open(image_file, 'wb') as f:
            await f.write(image_data)
        
        return image_file
