"""Application configuration for DailyClip."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any


class AppConfig:
    """Centralized application defaults and naming helpers."""

    APP_NAME = 'DailyClip'
    APP_VERSION = '1.0.0'

    CLIPPINGS_DIRNAME = 'clippings'
    IMAGES_DIRNAME = 'images'
    NOTES_DIRNAME = 'notes'

    HOTKEY_QUICK_SEARCH = 'alt+space'
    HOTKEY_NEW_NOTE = 'alt+n'
    HOTKEY_SCREENSHOT = 'alt+s'

    CLIPBOARD_CHECK_INTERVAL = 0.5
    CLIPBOARD_DEDUP_SECONDS = 10
    QUICK_NOTE_AUTOSAVE_SECONDS = 5
    SEARCH_DEFAULT_LIMIT = 50
    SEARCH_DEBOUNCE_MS = 300
    MAX_CLIP_LENGTH = 10_000
    MAX_NOTE_SIZE = 100_000

    SCREENSHOT_PREFIX = 'screen_'
    SCREENSHOT_EXTENSION = '.png'
    CLIP_FILE_PREFIX = 'clips_'
    INDEX_FILENAME = 'search_index.duckdb'

    @staticmethod
    def get_data_dir() -> Path:
        """Return the application data directory."""
        app_data = os.environ.get('APPDATA')
        if app_data:
            return Path(app_data) / AppConfig.APP_NAME
        return Path.home() / '.local' / 'share' / AppConfig.APP_NAME

    @staticmethod
    def get_daily_dir(date_str: str) -> Path:
        """Return the data directory for a given day."""
        return AppConfig.get_data_dir() / date_str

    @staticmethod
    def get_note_filename(date_str: str) -> str:
        """Build the note filename for a given date."""
        return f'notes_{date_str}.md'

    @staticmethod
    def get_clip_filename(timestamp: datetime) -> str:
        """Build the clip filename for a given timestamp."""
        return f'{AppConfig.CLIP_FILE_PREFIX}{timestamp:%H-%M-%S}.jsonl'

    @staticmethod
    def get_screenshot_filename(timestamp: datetime) -> str:
        """Build the screenshot filename for a given timestamp."""
        return f'{AppConfig.SCREENSHOT_PREFIX}{timestamp:%H-%M-%S}{AppConfig.SCREENSHOT_EXTENSION}'

    @staticmethod
    def get_default_config() -> dict[str, Any]:
        """Return a serializable default configuration."""
        return {
            'app_name': AppConfig.APP_NAME,
            'app_version': AppConfig.APP_VERSION,
            'python_requires': '>=3.11',
            'data_dir': str(AppConfig.get_data_dir()),
            'hotkeys': {
                'quick_search': AppConfig.HOTKEY_QUICK_SEARCH,
                'new_note': AppConfig.HOTKEY_NEW_NOTE,
                'screenshot': AppConfig.HOTKEY_SCREENSHOT,
            },
            'clipboard': {
                'check_interval': AppConfig.CLIPBOARD_CHECK_INTERVAL,
                'deduplicate_seconds': AppConfig.CLIPBOARD_DEDUP_SECONDS,
            },
            'search': {
                'default_limit': AppConfig.SEARCH_DEFAULT_LIMIT,
                'debounce_ms': AppConfig.SEARCH_DEBOUNCE_MS,
            },
            'notes': {
                'autosave_seconds': AppConfig.QUICK_NOTE_AUTOSAVE_SECONDS,
                'max_note_size': AppConfig.MAX_NOTE_SIZE,
            },
            'limits': {
                'max_clip_length': AppConfig.MAX_CLIP_LENGTH,
            },
        }
