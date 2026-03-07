"""Infrastructure exports for DailyClip."""

from __future__ import annotations

from importlib import import_module

__all__ = [
    'ClipboardMonitorService',
    'DuckDBSearchService',
    'FileStorageService',
    'GlobalHotkeyService',
    'ScreenCaptureService',
]


def __getattr__(name: str):
    """Lazily resolve infrastructure exports to avoid optional import coupling."""
    module_map = {
        'ClipboardMonitorService': 'DailyClip.infrastructure.clipboard',
        'DuckDBSearchService': 'DailyClip.infrastructure.search',
        'FileStorageService': 'DailyClip.infrastructure.storage',
        'GlobalHotkeyService': 'DailyClip.infrastructure.hotkey',
        'ScreenCaptureService': 'DailyClip.infrastructure.screen_capture',
    }
    if name not in module_map:
        raise AttributeError(name)
    module = import_module(module_map[name])
    return getattr(module, name)
