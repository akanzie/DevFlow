"""
Service interfaces for DailyClip - Clean Architecture
Define contracts for infrastructure services
"""

from typing import Protocol, List, Optional
from pathlib import Path
from datetime import datetime

from .entities import ClipItem, SearchResult, DailyNote

class IStorageService(Protocol):
    """Interface for data persistence"""
    
    async def create_daily_folder(self, date_str: str) -> Path:
        """Create daily folder structure"""
        ...
    
    async def append_clip(self, clip: ClipItem) -> None:
        """Append clip to daily JSONL file"""
        ...
    
    async def get_clips_for_date(self, date_str: str) -> List[ClipItem]:
        """Get all clips for specific date"""
        ...
    
    async def save_note(self, note: DailyNote) -> None:
        """Save daily note"""
        ...
    
    async def get_note(self, date_str: str) -> Optional[DailyNote]:
        """Get daily note"""
        ...
    
    async def save_screenshot(self, image_data: bytes) -> Path:
        """Save screenshot and return file path"""
        ...

class ISearchService(Protocol):
    """Interface for search operations"""
    
    async def build_index(self) -> None:
        """Build search index from existing data"""
        ...
    
    async def search(self, query: str, limit: int = 50) -> List[SearchResult]:
        """Search clips and notes"""
        ...
    
    async def add_clip_to_index(self, clip: ClipItem) -> None:
        """Add single clip to search index"""
        ...
    
    async def remove_from_index(self, clip_id: str) -> None:
        """Remove item from search index"""
        ...

class IClipboardMonitor(Protocol):
    """Interface for clipboard monitoring"""
    
    async def start_monitoring(self) -> None:
        """Start clipboard monitoring"""
        ...
    
    async def stop_monitoring(self) -> None:
        """Stop clipboard monitoring"""
        ...
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        ...

class IHotkeyService(Protocol):
    """Interface for global hotkey management"""
    
    def register_hotkey(self, key_combo: str, callback) -> None:
        """Register global hotkey"""
        ...
    
    def unregister_hotkey(self, key_combo: str) -> None:
        """Unregister global hotkey"""
        ...
    
    def start_listener(self) -> None:
        """Start hotkey listener"""
        ...
    
    def stop_listener(self) -> None:
        """Stop hotkey listener"""
        ...

class IScreenCaptureService(Protocol):
    """Interface for screen capture"""
    
    async def capture_screenshot(self) -> bytes:
        """Capture screenshot and return image data"""
        ...
    
    async def capture_area(self, x: int, y: int, width: int, height: int) -> bytes:
        """Capture specific screen area"""
        ...
