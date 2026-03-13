"""Controller smoke tests."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication

from DailyClip.application.controller import AppController
from DailyClip.common.async_runtime import AsyncRuntime


class DummyStorageService:
    """Minimal async storage stub for controller tests."""

    def __init__(self) -> None:
        self.created_dates: list[str] = []

    async def create_daily_folder(self, date_str: str) -> Path:
        self.created_dates.append(date_str)
        return Path(date_str)

    async def get_note(self, date_str: str):  # noqa: ANN001
        return None

    async def save_note(self, note):  # noqa: ANN001
        return Path(f"{note.date}.md")

    async def save_screenshot(self, image_data: bytes, captured_at=None):  # noqa: ANN001, ARG002
        return Path("screen.png")

    async def list_browse_entries(self, limit: int = 100):  # noqa: ARG002
        return []


class DummySearchService:
    """Minimal async search stub for controller tests."""

    def __init__(self) -> None:
        self.rebuild_calls = 0

    async def rebuild_index(self) -> None:
        self.rebuild_calls += 1

    async def index_note(self, note) -> None:  # noqa: ANN001
        return None

    async def search(self, query: str, limit: int = 50):  # noqa: ARG002
        return []


class DummyClipboardMonitor:
    """Minimal clipboard monitor stub for controller tests."""

    def __init__(self) -> None:
        self.started = False
        self.callbacks = []

    async def start_monitoring(self) -> None:
        self.started = True

    async def stop_monitoring(self) -> None:
        self.started = False

    def register_callback(self, callback) -> None:  # noqa: ANN001
        self.callbacks.append(callback)

    def unregister_callback(self, callback) -> None:  # noqa: ANN001
        if callback in self.callbacks:
            self.callbacks.remove(callback)


class DummyHotkeyService:
    """Minimal hotkey service stub for controller tests."""

    def __init__(self) -> None:
        self.registered: dict[str, object] = {}
        self.listening = False

    def register_hotkey(self, key_combo: str, callback) -> None:  # noqa: ANN001
        self.registered[key_combo] = callback

    def unregister_hotkey(self, key_combo: str) -> None:
        self.registered.pop(key_combo, None)

    def start_listener(self) -> None:
        self.listening = True

    def stop_listener(self) -> None:
        self.listening = False


class DummyScreenCaptureService:
    """Minimal screenshot stub for controller tests."""

    async def capture_screenshot(self) -> bytes:
        return b"image"


@pytest.fixture
def qapp():
    """Create or reuse QApplication for controller tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_controller_start_and_stop_wire_services(qapp):
    """Controller should bootstrap services, register hotkeys, and stop cleanly."""
    storage_service = DummyStorageService()
    search_service = DummySearchService()
    clipboard_monitor = DummyClipboardMonitor()
    hotkey_service = DummyHotkeyService()
    runtime = AsyncRuntime()
    controller = AppController(
        app=qapp,
        runtime=runtime,
        storage_service=storage_service,
        search_service=search_service,
        clipboard_monitor=clipboard_monitor,
        hotkey_service=hotkey_service,
        screen_capture_service=DummyScreenCaptureService(),
    )

    controller.start()

    assert search_service.rebuild_calls == 1
    assert clipboard_monitor.started is True
    assert hotkey_service.listening is True
    assert len(hotkey_service.registered) == 2

    controller.stop()

    assert clipboard_monitor.started is False
    assert hotkey_service.listening is False


def test_controller_opens_note_tab_in_merged_workspace(qapp):
    """Showing quick note should switch the merged workspace to the note tab."""
    controller = AppController(
        app=qapp,
        runtime=AsyncRuntime(),
        storage_service=DummyStorageService(),
        search_service=DummySearchService(),
        clipboard_monitor=DummyClipboardMonitor(),
        hotkey_service=DummyHotkeyService(),
        screen_capture_service=DummyScreenCaptureService(),
    )

    controller._runtime.start()
    try:
        controller.show_quick_note()
        assert controller._workspace_window._stack.currentWidget() is controller._workspace_window._note_widget
    finally:
        controller._runtime.stop()
