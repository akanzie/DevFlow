"""Custom exceptions for DailyClip."""


class DailyClipError(Exception):
    """Base exception for DailyClip."""


class ClipboardMonitorError(DailyClipError):
    """Raised when clipboard monitoring fails."""


class SearchIndexError(DailyClipError):
    """Raised when search indexing or querying fails."""


class StorageError(DailyClipError):
    """Raised when persistence operations fail."""


class ScreenCaptureError(DailyClipError):
    """Raised when screenshot capture fails."""
