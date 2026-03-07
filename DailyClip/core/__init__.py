"""Core exports for DailyClip."""

from .config import AppConfig
from .entities import ClipItem, DailyNote, SearchResult
from .exceptions import (
    ClipboardMonitorError,
    DailyClipError,
    ScreenCaptureError,
    SearchIndexError,
    StorageError,
)
from .interfaces import (
    IClipboardMonitor,
    IHotkeyService,
    IScreenCaptureService,
    ISearchService,
    IStorageService,
)

__all__ = [
    'AppConfig',
    'ClipItem',
    'ClipboardMonitorError',
    'DailyClipError',
    'DailyNote',
    'IClipboardMonitor',
    'IHotkeyService',
    'IScreenCaptureService',
    'ISearchService',
    'IStorageService',
    'ScreenCaptureError',
    'SearchIndexError',
    'SearchResult',
    'StorageError',
]
