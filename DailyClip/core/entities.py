"""Domain entities for DailyClip."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal


ClipType = Literal["text", "image", "html"]
ClipFormat = Literal["plain", "markdown", "code"]
SearchEntryType = Literal["clip", "note"]
BrowseEntryType = Literal["folder", "note", "clip_file", "image"]


@dataclass(frozen=True, slots=True)
class ClipItem:
    """Represents a persisted clipboard item."""

    timestamp: datetime
    content: str
    clip_type: ClipType
    format: ClipFormat = "plain"
    source_url: str | None = None
    file_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a JSON-serializable dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "type": self.clip_type,
            "format": self.format,
            "source_url": self.source_url,
            "file_path": str(self.file_path) if self.file_path else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClipItem":
        """Create a clip item from persisted JSON data."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            content=data["content"],
            clip_type=data["type"],
            format=data.get("format", "plain"),
            source_url=data.get("source_url"),
            file_path=Path(data["file_path"]) if data.get("file_path") else None,
        )

    @classmethod
    def create_text(
        cls,
        content: str,
        source_url: str | None = None,
        timestamp: datetime | None = None,
    ) -> "ClipItem":
        """Build a text clip using sensible defaults."""
        return cls(
            timestamp=timestamp or datetime.now(),
            content=content,
            clip_type="text",
            format="plain",
            source_url=source_url,
        )

    @classmethod
    def create_image(
        cls,
        content: str,
        file_path: Path,
        timestamp: datetime | None = None,
    ) -> "ClipItem":
        """Build an image clip using sensible defaults."""
        return cls(
            timestamp=timestamp or datetime.now(),
            content=content,
            clip_type="image",
            format="plain",
            file_path=file_path,
        )


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Represents a search result independent from clipboard storage."""

    entry_id: str
    entry_type: SearchEntryType
    timestamp: datetime
    content: str
    preview: str
    file_path: Path | None
    source_url: str | None
    score: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a JSON-serializable dictionary."""
        return {
            "entry_id": self.entry_id,
            "entry_type": self.entry_type,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "preview": self.preview,
            "file_path": str(self.file_path) if self.file_path else None,
            "source_url": self.source_url,
            "score": self.score,
        }


@dataclass(frozen=True, slots=True)
class BrowseEntry:
    """Represents a folder or file shown in browse mode."""

    entry_id: str
    entry_type: BrowseEntryType
    label: str
    path: Path
    timestamp: datetime | None
    preview: str
    content: str = ""
    child_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a JSON-serializable dictionary."""
        return {
            "entry_id": self.entry_id,
            "entry_type": self.entry_type,
            "label": self.label,
            "path": str(self.path),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "preview": self.preview,
            "content": self.content,
            "child_count": self.child_count,
        }


@dataclass(frozen=True, slots=True)
class DailyNote:
    """Represents a daily Markdown note."""

    date: str
    content: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a JSON-serializable dictionary."""
        return {
            "date": self.date,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def create(
        cls,
        date: str,
        content: str,
        timestamp: datetime | None = None,
    ) -> "DailyNote":
        """Build a daily note using sensible defaults."""
        now = timestamp or datetime.now()
        return cls(
            date=date,
            content=content,
            created_at=now,
            updated_at=now,
        )

    def update_content(
        self,
        new_content: str,
        timestamp: datetime | None = None,
    ) -> "DailyNote":
        """Return a new immutable note with updated content."""
        return DailyNote(
            date=self.date,
            content=new_content,
            created_at=self.created_at,
            updated_at=timestamp or datetime.now(),
        )
