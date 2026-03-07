"""Presentation tests for the MVP windows."""

from __future__ import annotations

from datetime import datetime

import pytest

pytest.importorskip('PyQt6')

from PyQt6.QtWidgets import QApplication

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.core.entities import SearchResult
from DailyClip.presentation.quick_note import QuickNoteWindow
from DailyClip.presentation.quick_search import QuickSearchWindow


class DummySearchService:
    """Provide deterministic search responses for UI tests."""

    async def search(self, query: str, limit: int = 50):  # noqa: ARG002
        return [
            SearchResult(
                entry_id='clip:1',
                entry_type='clip',
                timestamp=datetime(2026, 3, 7, 9, 30, 5),
                content='example result',
                preview='example result',
                file_path=None,
                source_url=None,
                score=1.0,
            )
        ]


@pytest.fixture
def qapp():
    """Create a QApplication when tests need UI widgets."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_quick_note_save_now_calls_callback(qapp):
    """Quick note should call the save callback when save_now is invoked."""
    del qapp
    captured = {}
    window = QuickNoteWindow(
        save_callback=lambda date_str, content: captured.update(
            {'date': date_str, 'content': content}
        ),
        autosave_seconds=5,
    )

    window.set_note_content('2026-03-07', 'Initial')
    window._editor.setPlainText('Updated note')
    window.save_now()

    assert captured == {'date': '2026-03-07', 'content': 'Updated note'}


def test_quick_search_renders_completed_results(qapp):
    """Quick search should render results passed back from the worker."""
    del qapp
    runtime = AsyncRuntime()
    window = QuickSearchWindow(DummySearchService(), runtime)

    window._on_search_completed(
        'example',
        [
            SearchResult(
                entry_id='clip:1',
                entry_type='clip',
                timestamp=datetime(2026, 3, 7, 9, 30, 5),
                content='example result',
                preview='example result',
                file_path=None,
                source_url=None,
                score=1.0,
            )
        ],
    )

    assert window._results_list.count() == 1
