"""
Pytest configuration for DailyClip
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.entities import ClipItem, DailyNote

@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_clip():
    """Sample clip item for testing"""
    return ClipItem.create_text(
        content="Test clipboard content",
        source_url="https://example.com"
    )

@pytest.fixture
def sample_note():
    """Sample daily note for testing"""
    return DailyNote.create(
        date=datetime.now().strftime("%Y-%m-%d"),
        content="# Daily Note\n\nTest content"
    )

@pytest.fixture
def sample_image_clip():
    """Sample image clip for testing"""
    return ClipItem(
        timestamp=datetime.now(),
        content="base64_image_data",
        clip_type="image",
        format="plain",
        file_path=Path("test_image.png")
    )
