"""
Tests for storage service
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from infrastructure.storage import FileStorageService
from core.entities import ClipItem, DailyNote

@pytest.mark.asyncio
async def test_create_daily_folder(temp_data_dir):
    """Test daily folder creation"""
    storage = FileStorageService(temp_data_dir)
    
    date_str = "2024-01-01"
    daily_dir = await storage.create_daily_folder(date_str)
    
    assert daily_dir.exists()
    assert (daily_dir / "clippings").exists()
    assert (daily_dir / "images").exists()
    assert (daily_dir / "notes").exists()
    assert (daily_dir / "index").exists()

@pytest.mark.asyncio
async def test_append_and_get_clips(temp_data_dir):
    """Test clip storage and retrieval"""
    storage = FileStorageService(temp_data_dir)
    
    # Create test clips with specific date to avoid conflicts
    from datetime import datetime
    test_date = datetime(2024, 1, 1, 12, 0, 0)
    
    clip1 = ClipItem(
        timestamp=test_date,
        content="First clip content",
        clip_type="text"
    )
    clip2 = ClipItem(
        timestamp=test_date,
        content="Second clip content", 
        clip_type="text"
    )
    
    # Store clips
    await storage.append_clip(clip1)
    await storage.append_clip(clip2)
    
    # Retrieve clips
    date_str = clip1.timestamp.strftime("%Y-%m-%d")
    retrieved_clips = await storage.get_clips_for_date(date_str)
    
    assert len(retrieved_clips) == 2
    assert retrieved_clips[0].content == "First clip content"
    assert retrieved_clips[1].content == "Second clip content"

@pytest.mark.asyncio
async def test_save_and_get_note(temp_data_dir):
    """Test note storage and retrieval"""
    storage = FileStorageService(temp_data_dir)
    
    # Create test note
    date_str = "2024-01-01"
    note = DailyNote.create(date_str, "# Test Note\n\nThis is a test note.")
    
    # Save note
    await storage.save_note(note)
    
    # Retrieve note
    retrieved_note = await storage.get_note(date_str)
    
    assert retrieved_note is not None
    assert retrieved_note.date == date_str
    assert retrieved_note.content == "# Test Note\n\nThis is a test note."

@pytest.mark.asyncio
async def test_get_note_nonexistent(temp_data_dir):
    """Test retrieving non-existent note"""
    storage = FileStorageService(temp_data_dir)
    
    retrieved_note = await storage.get_note("2024-01-02")
    assert retrieved_note is None

@pytest.mark.asyncio
async def test_save_screenshot(temp_data_dir):
    """Test screenshot saving"""
    storage = FileStorageService(temp_data_dir)
    
    # Create dummy image data
    image_data = b"fake_image_data"
    
    # Save screenshot
    image_path = await storage.save_screenshot(image_data)
    
    assert image_path.exists()
    assert image_path.suffix == ".png"
    assert "screen_" in image_path.name
    
    # Verify content
    with open(image_path, 'rb') as f:
        saved_data = f.read()
    assert saved_data == image_data
