"""
Application configuration for DailyClip
Centralized configuration management
"""

import os
from pathlib import Path
from typing import Dict, Any

class AppConfig:
    """Application configuration constants"""
    
    # App info
    APP_NAME = "DailyClip"
    APP_VERSION = "1.0.0"
    
    # Paths
    @staticmethod
    def get_data_dir() -> Path:
        """Get application data directory"""
        app_data = os.environ.get("APPDATA")
        if not app_data:
            app_data = Path.home() / ".local" / "share"
        return Path(app_data) / "DailyClip"
    
    @staticmethod
    def get_daily_dir(date_str: str) -> Path:
        """Get daily data directory"""
        return AppConfig.get_data_dir() / date_str
    
    # File naming
    CLIPS_FILENAME = "clips_current.jsonl"
    NOTES_FILENAME = "notes_{date}.md"
    SCREENSHOT_PREFIX = "screen_"
    INDEX_FILENAME = "daily_index.duckdb"
    
    # Hotkeys
    HOTKEY_QUICK_SEARCH = "alt+space"
    HOTKEY_NEW_NOTE = "alt+n"
    HOTKEY_SCREENSHOT = "alt+s"
    
    # Timing
    CLIPBOARD_CHECK_INTERVAL = 0.5  # seconds
    INDEX_BUILD_INTERVAL = 300      # 5 minutes
    CLEANUP_OLDER_THAN_DAYS = 30
    
    # Search
    SEARCH_DEFAULT_LIMIT = 50
    SEARCH_MIN_SCORE = 0.1
    
    # Image
    SCREENSHOT_QUALITY = 85
    SCREENSHOT_FORMAT = "PNG"
    MAX_IMAGE_SIZE = 1920  # pixels
    
    # Content limits
    MAX_CLIP_LENGTH = 10000  # characters
    MAX_NOTE_SIZE = 100000   # characters
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration dictionary"""
        return {
            "app_name": AppConfig.APP_NAME,
            "app_version": AppConfig.APP_VERSION,
            "data_dir": str(AppConfig.get_data_dir()),
            "hotkeys": {
                "quick_search": AppConfig.HOTKEY_QUICK_SEARCH,
                "new_note": AppConfig.HOTKEY_NEW_NOTE,
                "screenshot": AppConfig.HOTKEY_SCREENSHOT
            },
            "timing": {
                "clipboard_check_interval": AppConfig.CLIPBOARD_CHECK_INTERVAL,
                "index_build_interval": AppConfig.INDEX_BUILD_INTERVAL,
                "cleanup_older_than_days": AppConfig.CLEANUP_OLDER_THAN_DAYS
            },
            "search": {
                "default_limit": AppConfig.SEARCH_DEFAULT_LIMIT,
                "min_score": AppConfig.SEARCH_MIN_SCORE
            },
            "image": {
                "screenshot_quality": AppConfig.SCREENSHOT_QUALITY,
                "screenshot_format": AppConfig.SCREENSHOT_FORMAT,
                "max_image_size": AppConfig.MAX_IMAGE_SIZE
            },
            "limits": {
                "max_clip_length": AppConfig.MAX_CLIP_LENGTH,
                "max_note_size": AppConfig.MAX_NOTE_SIZE
            }
        }
