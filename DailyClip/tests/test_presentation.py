"""Presentation tests for the merged workspace window."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QListWidgetItem

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.core.entities import BrowseEntry, SearchResult
from DailyClip.presentation.unified_window import UnifiedMainWindow

class DummySearchService:
    """Provide deterministic search responses for UI tests."""

    async def search(self, query: str, limit: int = 50):  # noqa: ARG002
        return [
            SearchResult(
                entry_id="clip:1",
                entry_type="clip",
                timestamp=datetime(2026, 3, 7, 9, 30, 5),
                content="example result",
                preview="example result",
                file_path=None,
                source_url=None,
                score=1.0,
            )
        ]


class DummyStorageService:
    """Provide deterministic browse responses for UI tests."""

    async def list_browse_entries(self, limit: int = 100):  # noqa: ARG002
        return [
            BrowseEntry(
                entry_id="folder:2026-03-07",
                entry_type="folder",
                label="2026-03-07",
                path=Path("2026-03-07"),
                timestamp=datetime(2026, 3, 7, 11, 0, 0),
                preview="notes_2026-03-07.md",
                content="notes_2026-03-07.md",
                child_count=1,
            )
        ]


@pytest.fixture
def qapp():
    """Create a QApplication when tests need UI widgets."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_workspace_note_save_now_calls_callback(qapp):
    """The merged workspace should still save note content through the callback."""
    del qapp
    captured = {}
    runtime = AsyncRuntime()
    window = UnifiedMainWindow(
        search_service=DummySearchService(),
        storage_service=DummyStorageService(),
        runtime=runtime,
        save_callback=lambda date_str, content: captured.update(
            {"date": date_str, "content": content}
        ),
        autosave_seconds=5,
    )

    window.set_note_content("2026-03-07", "Initial")
    window._note_widget._editor.setPlainText("Updated note")
    window._note_widget._is_dirty = True # Manually set for test
    window.save_note_now()

    assert captured == {"date": "2026-03-07", "content": "Updated note"}


def test_workspace_renders_completed_search_results(qapp):
    """Search results should still populate the list view."""
    del qapp
    runtime = AsyncRuntime()
    window = UnifiedMainWindow(
        search_service=DummySearchService(),
        storage_service=DummyStorageService(),
        runtime=runtime,
        save_callback=lambda *_args: None,
        autosave_seconds=5,
    )

    window._latest_query = "example"
    window._on_load_completed(
        "search",
        "example",
        [
            SearchResult(
                entry_id="clip:1",
                entry_type="clip",
                timestamp=datetime(2026, 3, 7, 9, 30, 5),
                content="example result",
                preview="example result",
                file_path=None,
                source_url=None,
                score=1.0,
            )
        ],
    )

    assert window._search_widget._results_list.count() == 1


def test_workspace_renders_browse_entries_when_query_is_empty(qapp):
    """Browse mode should show folder/file entries when there is no query."""
    del qapp
    runtime = AsyncRuntime()
    window = UnifiedMainWindow(
        search_service=DummySearchService(),
        storage_service=DummyStorageService(),
        runtime=runtime,
        save_callback=lambda *_args: None,
        autosave_seconds=5,
    )

    window._latest_query = ""
    window._on_load_completed(
        "browse",
        "",
        [
            BrowseEntry(
                entry_id="folder:2026-03-07",
                entry_type="folder",
                label="2026-03-07",
                path=Path("2026-03-07"),
                timestamp=datetime(2026, 3, 7, 11, 0, 0),
                preview="notes_2026-03-07.md",
                content="notes_2026-03-07.md",
                child_count=1,
            )
        ],
    )

    assert window._search_widget._results_list.count() == 1
    assert "[folder]" in window._search_widget._results_list.item(0).text()


def test_workspace_refresh_items_uses_current_mode(qapp):
    """Manual refresh should reuse the current browse/search mode asynchronously."""
    del qapp
    runtime = AsyncRuntime()
    window = UnifiedMainWindow(
        search_service=DummySearchService(),
        storage_service=DummyStorageService(),
        runtime=runtime,
        save_callback=lambda *_args: None,
        autosave_seconds=5,
    )

    calls: list[tuple[str, bool, bool]] = []
    window._schedule_load = (  # type: ignore[method-assign]
        lambda mode, immediate=False, silent=False: calls.append((mode, immediate, silent))
    )

    window._latest_query = ""
    window.refresh_items()
    window._latest_query = "async"
    window.refresh_items(silent=True)

    assert calls == [("browse", True, False), ("search", True, True)]
    assert window._search_widget._refresh_button.text() == "Refresh"


def test_workspace_auto_refresh_only_runs_for_visible_browser_tab(qapp):
    """Auto refresh should only trigger while the browser tab is visible."""
    runtime = AsyncRuntime()
    window = UnifiedMainWindow(
        search_service=DummySearchService(),
        storage_service=DummyStorageService(),
        runtime=runtime,
        save_callback=lambda *_args: None,
        autosave_seconds=5,
    )

    calls: list[bool] = []
    window.refresh_items = lambda silent=False: calls.append(silent)  # type: ignore[method-assign]

    window.show()
    qapp.processEvents()
    window._stack.setCurrentWidget(window._search_widget)
    window._auto_refresh_visible_data()

    assert calls == [True]

    calls.clear()
    window._stack.setCurrentWidget(window._note_widget)
    window._auto_refresh_visible_data()

    assert calls == []
    window.hide()


def test_workspace_switches_to_image_preview_for_image_entries(qapp, tmp_path):
    """Selecting an image entry should switch the preview pane to image mode."""
    del qapp
    image_path = tmp_path / "screen_10-15-22.png"
    pixmap = QPixmap(2, 2)
    pixmap.fill(Qt.GlobalColor.white)
    assert pixmap.save(str(image_path), "PNG")
    runtime = AsyncRuntime()
    window = UnifiedMainWindow(
        search_service=DummySearchService(),
        storage_service=DummyStorageService(),
        runtime=runtime,
        save_callback=lambda *_args: None,
        autosave_seconds=5,
    )

    entry = BrowseEntry(
        entry_id="image:screen",
        entry_type="image",
        label=image_path.name,
        path=image_path,
        timestamp=datetime(2026, 3, 7, 10, 15, 22),
        preview="PNG image",
    )
    item = QListWidgetItem("image")
    item.setData(Qt.ItemDataRole.UserRole, entry)

    window._on_item_selected(item)

    assert window._search_widget._preview_stack.currentIndex() == 1
