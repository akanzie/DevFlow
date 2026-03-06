"""
Domain entities for DailyClip - Clipboard manager
Clean Architecture approach with immutable data structures
"""

from datetime import datetime
from typing import Optional, Literal
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass(frozen=True, slots=True)
class ClipItem:
    """Represents a clipboard item with metadata"""
    timestamp: datetime
    content: str
    clip_type: Literal["text", "image", "html"]
    format: Literal["plain", "markdown", "code"] = "plain"
    source_url: Optional[str] = None
    file_path: Optional[Path] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "type": self.clip_type,
            "format": self.format,
            "source_url": self.source_url,
            "file_path": str(self.file_path) if self.file_path else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ClipItem":
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            content=data["content"],
            clip_type=data["type"],
            format=data.get("format", "plain"),
            source_url=data.get("source_url"),
            file_path=Path(data["file_path"]) if data.get("file_path") else None
        )
    
    @classmethod
    def create_text(cls, content: str, source_url: Optional[str] = None) -> "ClipItem":
        """Factory method for text clips"""
        return cls(
            timestamp=datetime.now(),
            content=content,
            clip_type="text",
            format="plain",
            source_url=source_url
        )
    
    @classmethod
    def create_image(cls, content: str, file_path: Path) -> "ClipItem":
        """Factory method for image clips"""
        return cls(
            timestamp=datetime.now(),
            content=content,
            clip_type="image",
            format="plain",
            file_path=file_path
        )

@dataclass(frozen=True, slots=True)
class SearchResult:
    """Represents a search result"""
    clip: ClipItem
    score: float
    preview: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "clip": self.clip.to_dict(),
            "score": self.score,
            "preview": self.preview
        }

@dataclass(frozen=True, slots=True)
class DailyNote:
    """Represents a daily note entry"""
    date: str  # YYYY-MM-DD format
    content: str
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "date": self.date,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def create(cls, date: str, content: str) -> "DailyNote":
        """Factory method for daily notes"""
        now = datetime.now()
        return cls(
            date=date,
            content=content,
            created_at=now,
            updated_at=now
        )
    
    def update_content(self, new_content: str) -> "DailyNote":
        """Create updated note with new content"""
        return DailyNote(
            date=self.date,
            content=new_content,
            created_at=self.created_at,
            updated_at=datetime.now()
        )
