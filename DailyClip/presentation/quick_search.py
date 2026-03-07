"""Quick search UI for DailyClip."""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QThread, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.core.config import AppConfig
from DailyClip.core.entities import SearchResult
from DailyClip.core.interfaces import ISearchService

logger = logging.getLogger(__name__)


class SearchWorker(QThread):
    """Run search work off the UI thread while reusing the shared async runtime."""

    search_completed = pyqtSignal(str, list)
    search_failed = pyqtSignal(str)

    def __init__(
        self,
        runtime: AsyncRuntime,
        search_service: ISearchService,
        query: str,
        limit: int,
    ) -> None:
        super().__init__()
        self._runtime = runtime
        self._search_service = search_service
        self._query = query
        self._limit = limit

    def run(self) -> None:
        """Execute the search query through the background async runtime."""
        try:
            results = self._runtime.submit(
                self._search_service.search(self._query, self._limit)
            ).result(timeout=10)
        except Exception as exc:
            self.search_failed.emit(str(exc))
            return

        self.search_completed.emit(self._query, results)


class QuickSearchWindow(QMainWindow):
    """Search window with live query results and content preview."""

    def __init__(
        self,
        search_service: ISearchService,
        runtime: AsyncRuntime,
    ) -> None:
        super().__init__()
        self._search_service = search_service
        self._runtime = runtime
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._trigger_search)
        self._active_worker: SearchWorker | None = None
        self._pending_query: str | None = None
        self._latest_query = ''
        self._current_results: list[SearchResult] = []

        self._setup_ui()
        self._setup_shortcuts()
        self.hide()

    def show_window(self) -> None:
        """Show and focus the window."""
        self.show()
        self.raise_()
        self.activateWindow()
        self._search_input.setFocus()
        self._search_input.selectAll()

    def _setup_ui(self) -> None:
        """Initialize widgets and layout."""
        self.setWindowTitle(f'{AppConfig.APP_NAME} Quick Search')
        self.setMinimumSize(820, 540)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )

        root = QWidget(self)
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self._search_input = QLineEdit(self)
        self._search_input.setPlaceholderText('Search clips and notes...')
        self._search_input.setFont(QFont('Segoe UI', 12))
        self._search_input.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self._search_input)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        layout.addWidget(splitter, 1)

        self._results_list = QListWidget(self)
        self._results_list.currentItemChanged.connect(self._on_result_selected)
        self._results_list.itemDoubleClicked.connect(self._on_result_activated)
        splitter.addWidget(self._results_list)

        preview_panel = QWidget(self)
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(8)

        preview_label = QLabel('Preview', self)
        preview_label.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label)

        self._preview_text = QTextEdit(self)
        self._preview_text.setReadOnly(True)
        self._preview_text.setFont(QFont('Consolas', 10))
        preview_layout.addWidget(self._preview_text, 1)

        self._preview_meta = QLabel('', self)
        self._preview_meta.setWordWrap(True)
        preview_layout.addWidget(self._preview_meta)

        splitter.addWidget(preview_panel)
        splitter.setSizes([320, 500])

        footer = QHBoxLayout()
        layout.addLayout(footer)

        self._status_label = QLabel('Ready', self)
        footer.addWidget(self._status_label)
        footer.addStretch(1)

        copy_button = QPushButton('Copy', self)
        copy_button.clicked.connect(self._copy_selected_result)
        footer.addWidget(copy_button)

        close_button = QPushButton('Close', self)
        close_button.clicked.connect(self.hide)
        footer.addWidget(close_button)

        self._center_on_primary_screen()

    def _setup_shortcuts(self) -> None:
        """Register keyboard shortcuts for the search window."""
        QShortcut(QKeySequence('Escape'), self, activated=self.hide)
        QShortcut(QKeySequence('Ctrl+C'), self, activated=self._copy_selected_result)
        QShortcut(QKeySequence('Return'), self, activated=self._activate_current_result)

    def _on_search_text_changed(self, text: str) -> None:
        """Debounce search input changes."""
        self._latest_query = text.strip()
        if not self._latest_query:
            self._current_results = []
            self._results_list.clear()
            self._preview_text.clear()
            self._preview_meta.clear()
            self._status_label.setText('Ready')
            return

        self._status_label.setText('Searching...')
        self._search_timer.start(AppConfig.SEARCH_DEBOUNCE_MS)

    def _trigger_search(self) -> None:
        """Start or queue a search operation."""
        query = self._latest_query
        if not query:
            return

        if self._active_worker and self._active_worker.isRunning():
            self._pending_query = query
            return

        worker = SearchWorker(
            runtime=self._runtime,
            search_service=self._search_service,
            query=query,
            limit=AppConfig.SEARCH_DEFAULT_LIMIT,
        )
        worker.search_completed.connect(self._on_search_completed)
        worker.search_failed.connect(self._on_search_failed)
        worker.finished.connect(self._on_worker_finished)
        self._active_worker = worker
        worker.start()

    def _on_search_completed(self, query: str, results: list[SearchResult]) -> None:
        """Render search results if they still match the latest query."""
        if query != self._latest_query:
            return

        self._current_results = results
        self._results_list.clear()
        for result in results:
            timestamp = result.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            label = f'[{result.entry_type}] {timestamp} {result.preview}'
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, result)
            self._results_list.addItem(item)

        if results:
            self._results_list.setCurrentRow(0)
        self._status_label.setText(f'Found {len(results)} results')

    def _on_search_failed(self, message: str) -> None:
        """Show search errors without crashing the UI."""
        logger.warning('Search failed: %s', message)
        self._status_label.setText(f'Search failed: {message}')

    def _on_worker_finished(self) -> None:
        """Start any queued search once the current worker finishes."""
        self._active_worker = None
        if self._pending_query and self._pending_query != self._latest_query:
            self._pending_query = self._latest_query
        queued_query = self._pending_query
        self._pending_query = None
        if queued_query and queued_query == self._latest_query:
            self._trigger_search()

    def _on_result_selected(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None = None,
    ) -> None:
        """Update preview content when the selected result changes."""
        del previous
        if not current:
            self._preview_text.clear()
            self._preview_meta.clear()
            return

        result = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(result, SearchResult):
            return

        self._preview_text.setPlainText(result.content)
        metadata = [
            f'Type: {result.entry_type}',
            f'Timestamp: {result.timestamp.isoformat(sep=" ", timespec="seconds")}',
            f'Score: {result.score:.2f}',
        ]
        if result.file_path:
            metadata.append(f'Path: {result.file_path}')
        if result.source_url:
            metadata.append(f'Source: {result.source_url}')
        self._preview_meta.setText(' | '.join(metadata))

    def _on_result_activated(self, item: QListWidgetItem) -> None:
        """Copy the active result and close the window."""
        self._copy_selected_result(item)
        self.hide()

    def _copy_selected_result(self, item: QListWidgetItem | None = None) -> None:
        """Copy selected result content to the clipboard."""
        selected_item = item or self._results_list.currentItem()
        if not selected_item:
            return

        result = selected_item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(result, SearchResult):
            return

        QApplication.clipboard().setText(result.content)
        self._status_label.setText('Copied to clipboard')
        QTimer.singleShot(2_000, lambda: self._status_label.setText('Ready'))

    def _activate_current_result(self) -> None:
        """Activate the currently selected result."""
        current_item = self._results_list.currentItem()
        if current_item:
            self._on_result_activated(current_item)

    def keyPressEvent(self, event: Any) -> None:
        """Support arrow-key navigation while the search box retains focus."""
        if event.key() == Qt.Key.Key_Down:
            next_row = min(
                self._results_list.currentRow() + 1,
                self._results_list.count() - 1,
            )
            self._results_list.setCurrentRow(next_row)
            return
        if event.key() == Qt.Key.Key_Up:
            next_row = max(self._results_list.currentRow() - 1, 0)
            self._results_list.setCurrentRow(next_row)
            return
        super().keyPressEvent(event)

    def _center_on_primary_screen(self) -> None:
        """Place the window near the top center of the main screen."""
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geometry = screen.availableGeometry()
        x = geometry.x() + (geometry.width() - self.width()) // 2
        y = geometry.y() + max(40, geometry.height() // 8)
        self.move(x, y)
