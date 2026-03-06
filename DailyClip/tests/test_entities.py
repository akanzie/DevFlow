"""
Tests for domain entities
"""

import pytest
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.entities import ClipItem, DailyNote, SearchResult

class TestClipItem:
    """Test ClipItem entity"""
    
    def test_create_text_clip(self):
        """Test text clip creation"""
        content = "Test clipboard content"
        source_url = "https://example.com"
        
        clip = ClipItem.create_text(content, source_url)
        
        assert clip.content == content
        assert clip.clip_type == "text"
        assert clip.format == "plain"
        assert clip.source_url == source_url
        assert clip.file_path is None
        assert isinstance(clip.timestamp, datetime)
    
    def test_create_image_clip(self):
        """Test image clip creation"""
        content = "base64_image_data"
        file_path = Path("test_image.png")
        
        clip = ClipItem.create_image(content, file_path)
        
        assert clip.content == content
        assert clip.clip_type == "image"
        assert clip.format == "plain"
        assert clip.file_path == file_path
        assert clip.source_url is None
        assert isinstance(clip.timestamp, datetime)
    
    def test_to_dict(self):
        """Test serialization to dictionary"""
        clip = ClipItem.create_text("Test content")
        data = clip.to_dict()
        
        assert data["content"] == "Test content"
        assert data["type"] == "text"
        assert data["format"] == "plain"
        assert "timestamp" in data
        assert data["source_url"] is None
        assert data["file_path"] is None
    
    def test_from_dict(self):
        """Test deserialization from dictionary"""
        original_clip = ClipItem.create_text("Test content")
        data = original_clip.to_dict()
        
        restored_clip = ClipItem.from_dict(data)
        
        assert restored_clip.content == original_clip.content
        assert restored_clip.clip_type == original_clip.clip_type
        assert restored_clip.format == original_clip.format
        assert restored_clip.timestamp == original_clip.timestamp
    
    def test_immutability(self):
        """Test entity immutability"""
        clip = ClipItem.create_text("Test content")
        
        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            clip.content = "Modified content"

class TestDailyNote:
    """Test DailyNote entity"""
    
    def test_create_note(self):
        """Test daily note creation"""
        date = datetime.now().strftime("%Y-%m-%d")
        content = "# Daily Note\n\nTest content"
        
        note = DailyNote.create(date, content)
        
        assert note.date == date
        assert note.content == content
        assert isinstance(note.created_at, datetime)
        assert isinstance(note.updated_at, datetime)
        assert note.created_at == note.updated_at
    
    def test_update_content(self):
        """Test note content update"""
        original_note = DailyNote.create("2024-01-01", "Original content")
        new_content = "Updated content"
        
        updated_note = original_note.update_content(new_content)
        
        assert updated_note.content == new_content
        assert updated_note.date == original_note.date
        assert updated_note.created_at == original_note.created_at
        assert updated_note.updated_at > original_note.updated_at
    
    def test_to_dict(self):
        """Test serialization to dictionary"""
        note = DailyNote.create("2024-01-01", "Test content")
        data = note.to_dict()
        
        assert data["date"] == "2024-01-01"
        assert data["content"] == "Test content"
        assert "created_at" in data
        assert "updated_at" in data

class TestSearchResult:
    """Test SearchResult entity"""
    
    def test_create_search_result(self):
        """Test search result creation"""
        clip = ClipItem.create_text("Test content")
        score = 0.95
        preview = "Test..."
        
        result = SearchResult(clip, score, preview)
        
        assert result.clip == clip
        assert result.score == score
        assert result.preview == preview
    
    def test_to_dict(self):
        """Test serialization to dictionary"""
        clip = ClipItem.create_text("Test content")
        result = SearchResult(clip, 0.95, "Test...")
        data = result.to_dict()
        
        assert "clip" in data
        assert data["score"] == 0.95
        assert data["preview"] == "Test..."
        assert data["clip"]["content"] == "Test content"
