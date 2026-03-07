"""Merged search, browse, preview, and note UI for DailyClip."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import QThread, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.core.config import AppConfig
from DailyClip.core.entities import BrowseEntry, SearchResult
from DailyClip.core.interfaces import ISearchService, IStorageService

logger = logging.getLogger(__name__)


class WorkspaceLoadWorker(QThread):
    """Run search or browse work off the UI thread."""

    load_completed = pyqtSignal(str, str, list)
    load_failed = pyqtSignal(str, str)

    def __init__(
        self,
        runtime: AsyncRuntime,
        search_service: ISearchService,
        storage_service: IStorageService,
        mode: str,
        query: str,
        limit: int,
    ) -> None:
        super().__init__()
        self._runtime = runtime
        self._search_service = search_service
        self._storage_service = storage_service
        self._mode = mode
        self._query = query
        self._limit = limit

    def run(self) -> None:
        """Execute the requested browse/search workload."""
        try:
            if self._mode == "browse":
                items = self._runtime.submit(
                    self._storage_service.list_browse_entries(self._limit)
                ).result(timeout=10)
            else:
                items = self._runtime.submit(
                    self._search_service.search(self._query, self._limit)
                ).result(timeout=10)
        except Exception as exc:
            self.load_failed.emit(self._mode, str(exc))
            return

        self.load_completed.emit(self._mode, self._query, items)


class QuickSearchWindow(QMainWindow):
    """Unified workspace window for search, browse, preview, and notes."""

    def __init__(
        self,
        search_service: ISearchService,
        storage_service: IStorageService,
        runtime: AsyncRuntime,
        save_callback: Callable[[str, str], None],
        autosave_seconds: int,
    ) -> None:
        super().__init__()
        self._search_service = search_service
        self._storage_service = storage_service
        self._runtime = runtime
        self._save_callback = save_callback
        self._current_date = ""
        self._is_dirty = False
        self._current_image_pixmap: QPixmap | None = None
        self._active_worker: WorkspaceLoadWorker | None = None
        self._pending_request: tuple[str, str] | None = None
        self._latest_mode = "browse"
        self._latest_query = ""
        self._current_items: list[SearchResult | BrowseEntry] = []
        self._selected_entry_id: str | None = None

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._trigger_load)

        self._auto_refresh_timer = QTimer(self)
        self._auto_refresh_timer.setInterval(AppConfig.WORKSPACE_AUTO_REFRESH_MS)
        self._auto_refresh_timer.timeout.connect(self._auto_refresh_visible_data)

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(autosave_seconds * 1000)
        self._autosave_timer.timeout.connect(self.save_note_now)

        self._setup_ui()
        self._setup_shortcuts()
        self.hide()

    def show_search_view(self) -> None:
        """Show the merged window focused on search and browse."""
        self._tabs.setCurrentWidget(self._browser_tab)
        self._autosave_timer.stop()
        self._start_auto_refresh()
        self._show_window()
        self._search_input.setFocus()
        if self._search_input.text().strip():
            self._search_input.selectAll()
            self._schedule_load("search", immediate=True)
        else:
            self._schedule_load("browse", immediate=True)

    def show_note_view(self) -> None:
        """Show the merged window focused on the note editor tab."""
        self._tabs.setCurrentWidget(self._note_tab)
        self._stop_auto_refresh()
        self._show_window()
        self._editor.setFocus()
        self._autosave_timer.start()

    def set_note_content(self, date_str: str, content: str) -> None:
        """Load note content into the editor without triggering autosave."""
        self._current_date = date_str
        self._editor.blockSignals(True)
        self._editor.setPlainText(content)
        self._editor.blockSignals(False)
        self._note_status_label.setText(f"Editing {date_str}")
        self._note_title_label.setText(f"Daily note {date_str}")
        self._is_dirty = False

    def save_note_now(self) -> None:
        """Save the current note content if it changed."""
        if not self._current_date or not self._is_dirty:
            return

        self._save_callback(self._current_date, self._editor.toPlainText())
        self._note_status_label.setText(f"Saved {self._current_date}")
        self._is_dirty = False

    def keyPressEvent(self, event: Any) -> None:
        """Support keyboard navigation while the search box keeps focus."""
        if self._tabs.currentWidget() is self._browser_tab:
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

    def resizeEvent(self, event: Any) -> None:
        """Refresh image scaling when the window size changes."""
        super().resizeEvent(event)
        self._refresh_image_preview()

    def closeEvent(self, event: Any) -> None:
        """Hide instead of destroying the workspace window."""
        self.save_note_now()
        self._autosave_timer.stop()
        self._stop_auto_refresh()
        self.hide()
        event.ignore()

    def _setup_ui(self) -> None:
        """Initialize widgets and layout."""
        self.setWindowTitle(f"{AppConfig.APP_NAME} Workspace")
        self.setMinimumSize(980, 640)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)

        root = QWidget(self)
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self._tabs = QTabWidget(self)
        layout.addWidget(self._tabs, 1)

        self._browser_tab = QWidget(self)
        self._tabs.addTab(self._browser_tab, "Search and Browse")
        self._setup_browser_tab()

        self._note_tab = QWidget(self)
        self._tabs.addTab(self._note_tab, "Daily Note")
        self._setup_note_tab()
        self._tabs.currentChanged.connect(self._on_tab_changed)

        self._center_on_primary_screen()

    def _setup_browser_tab(self) -> None:
        """Build the search and browse tab widgets."""
        layout = QVBoxLayout(self._browser_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._search_input = QLineEdit(self)
        self._search_input.setPlaceholderText(
            "Search clips and notes, or leave blank to browse recent folders and files..."
        )
        self._search_input.setFont(QFont("Segoe UI", 12))
        self._search_input.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self._search_input)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        layout.addWidget(splitter, 1)

        self._results_list = QListWidget(self)
        self._results_list.currentItemChanged.connect(self._on_item_selected)
        self._results_list.itemDoubleClicked.connect(self._open_selected_item)
        splitter.addWidget(self._results_list)

        preview_panel = QWidget(self)
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(8)

        preview_label = QLabel("Preview", self)
        preview_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label)

        self._preview_stack = QStackedWidget(self)
        preview_layout.addWidget(self._preview_stack, 1)

        self._preview_text = QTextEdit(self)
        self._preview_text.setReadOnly(True)
        self._preview_text.setFont(QFont("Consolas", 10))
        self._preview_stack.addWidget(self._preview_text)

        image_scroll = QScrollArea(self)
        image_scroll.setWidgetResizable(True)
        image_host = QWidget(self)
        image_layout = QVBoxLayout(image_host)
        image_layout.setContentsMargins(0, 0, 0, 0)
        self._image_label = QLabel("No image selected", self)
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self._image_label)
        image_scroll.setWidget(image_host)
        self._preview_stack.addWidget(image_scroll)

        self._preview_meta = QLabel("", self)
        self._preview_meta.setWordWrap(True)
        preview_layout.addWidget(self._preview_meta)

        splitter.addWidget(preview_panel)
        splitter.setSizes([360, 620])

        footer = QHBoxLayout()
        layout.addLayout(footer)

        self._browser_status_label = QLabel("Ready", self)
        footer.addWidget(self._browser_status_label)
        footer.addStretch(1)

        self._refresh_button = QPushButton("Refresh", self)
        self._refresh_button.clicked.connect(self.refresh_items)
        footer.addWidget(self._refresh_button)

        open_button = QPushButton("Open", self)
        open_button.clicked.connect(self._open_selected_item)
        footer.addWidget(open_button)

        copy_button = QPushButton("Copy", self)
        copy_button.clicked.connect(self._copy_selected_item)
        footer.addWidget(copy_button)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self._hide_current_view)
        footer.addWidget(close_button)

    def _setup_note_tab(self) -> None:
        """Build the integrated note editor tab widgets."""
        layout = QVBoxLayout(self._note_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header = QHBoxLayout()
        layout.addLayout(header)

        self._note_title_label = QLabel("Daily note", self)
        self._note_title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        header.addWidget(self._note_title_label)
        header.addStretch(1)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_note_now)
        header.addWidget(save_button)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self._hide_current_view)
        header.addWidget(close_button)

        self._note_status_label = QLabel("Ready", self)
        layout.addWidget(self._note_status_label)

        self._editor = QPlainTextEdit(self)
        self._editor.setPlaceholderText("# Daily note")
        self._editor.setFont(QFont("Consolas", 11))
        self._editor.textChanged.connect(self._mark_dirty)
        layout.addWidget(self._editor, 1)

    def _setup_shortcuts(self) -> None:
        """Register keyboard shortcuts for the merged window."""
        QShortcut(QKeySequence("Escape"), self, activated=self._hide_current_view)
        QShortcut(
            QKeySequence("Ctrl+C"),
            self._browser_tab,
            activated=self._copy_selected_item,
        )
        QShortcut(
            QKeySequence("Return"),
            self._browser_tab,
            activated=self._activate_current_item,
        )
        QShortcut(QKeySequence("Ctrl+S"), self._note_tab, activated=self.save_note_now)

    def _show_window(self) -> None:
        """Show and focus the window."""
        self.show()
        self.raise_()
        self.activateWindow()

    def _start_auto_refresh(self) -> None:
        """Start the periodic background refresh for browse/search data."""
        if not self._auto_refresh_timer.isActive():
            self._auto_refresh_timer.start()

    def _stop_auto_refresh(self) -> None:
        """Stop the periodic background refresh timer."""
        self._auto_refresh_timer.stop()

    def _hide_current_view(self) -> None:
        """Persist note state when needed and hide the workspace."""
        self.save_note_now()
        self._autosave_timer.stop()
        self._stop_auto_refresh()
        self.hide()

    def _on_tab_changed(self, index: int) -> None:
        """Start or stop note autosave when the active tab changes."""
        del index
        if self._tabs.currentWidget() is self._note_tab:
            self._stop_auto_refresh()
            self._autosave_timer.start()
            self._editor.setFocus()
            return

        self.save_note_now()
        self._autosave_timer.stop()
        if self.isVisible():
            self._start_auto_refresh()
            self.refresh_items(silent=True)

    def _on_search_text_changed(self, text: str) -> None:
        """Debounce search input changes and fall back to browse mode."""
        self._latest_query = text.strip()
        if not self._latest_query:
            self._schedule_load("browse")
            return

        self._schedule_load("search")

    def refresh_items(self, silent: bool = False) -> None:
        """Reload the currently displayed browse/search data."""
        mode = "browse" if not self._latest_query else "search"
        self._schedule_load(mode, immediate=True, silent=silent)

    def _auto_refresh_visible_data(self) -> None:
        """Refresh the browser tab periodically while the window is visible."""
        if not self.isVisible() or self._tabs.currentWidget() is not self._browser_tab:
            return
        if self._search_timer.isActive():
            return
        self.refresh_items(silent=True)

    def _schedule_load(
        self,
        mode: str,
        *,
        immediate: bool = False,
        silent: bool = False,
    ) -> None:
        """Schedule browse/search work after the appropriate delay."""
        self._latest_mode = mode
        if not silent:
            if mode == "browse":
                message = "Refreshing recent files..." if immediate else "Loading recent files..."
            else:
                message = "Refreshing results..." if immediate else "Searching..."
            self._browser_status_label.setText(message)
        delay_ms = 1 if immediate or mode == "browse" else AppConfig.SEARCH_DEBOUNCE_MS
        self._search_timer.start(delay_ms)

    def _trigger_load(self) -> None:
        """Start or queue a browse/search operation."""
        mode = "browse" if not self._latest_query else self._latest_mode
        query = self._latest_query if mode == "search" else ""

        if self._active_worker and self._active_worker.isRunning():
            self._pending_request = (mode, query)
            return

        limit = (
            AppConfig.BROWSE_DEFAULT_LIMIT
            if mode == "browse"
            else AppConfig.SEARCH_DEFAULT_LIMIT
        )
        worker = WorkspaceLoadWorker(
            runtime=self._runtime,
            search_service=self._search_service,
            storage_service=self._storage_service,
            mode=mode,
            query=query,
            limit=limit,
        )
        worker.load_completed.connect(self._on_load_completed)
        worker.load_failed.connect(self._on_load_failed)
        worker.finished.connect(self._on_worker_finished)
        self._active_worker = worker
        worker.start()

    def _on_load_completed(
        self,
        mode: str,
        query: str,
        items: list[SearchResult | BrowseEntry],
    ) -> None:
        """Render browse or search items if they still match the latest state."""
        if mode == "search" and query != self._latest_query:
            return
        if mode == "browse" and self._latest_query:
            return

        selected_entry_id = self._selected_entry_id
        selected_row = 0

        self._current_items = items
        self._results_list.clear()
        for index, item_data in enumerate(items):
            item = QListWidgetItem(self._build_item_label(item_data))
            item.setData(Qt.ItemDataRole.UserRole, item_data)
            self._results_list.addItem(item)
            if item_data.entry_id == selected_entry_id:
                selected_row = index

        if items:
            self._results_list.setCurrentRow(selected_row)
        else:
            self._selected_entry_id = None

        if mode == "browse":
            self._browser_status_label.setText(f"Showing {len(items)} recent items")
        else:
            self._browser_status_label.setText(f"Found {len(items)} results")

        if not items:
            self._clear_preview("No items found.")

    def _on_load_failed(self, mode: str, message: str) -> None:
        """Show browse/search errors without crashing the UI."""
        logger.warning("%s load failed: %s", mode, message)
        self._browser_status_label.setText(f"Load failed: {message}")

    def _on_worker_finished(self) -> None:
        """Start any queued browse/search work once the current worker finishes."""
        self._active_worker = None
        queued_request = self._pending_request
        self._pending_request = None
        if queued_request is None:
            return

        self._latest_mode, queued_query = queued_request
        self._latest_query = queued_query
        self._trigger_load()

    def _on_item_selected(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None = None,
    ) -> None:
        """Update preview content when the selected item changes."""
        del previous
        if current is None:
            self._selected_entry_id = None
            self._clear_preview()
            return

        item_data = current.data(Qt.ItemDataRole.UserRole)
        if isinstance(item_data, (SearchResult, BrowseEntry)):
            self._selected_entry_id = item_data.entry_id
        if isinstance(item_data, SearchResult):
            self._render_search_result(item_data)
        elif isinstance(item_data, BrowseEntry):
            self._render_browse_entry(item_data)
        else:
            self._clear_preview()

    def _render_search_result(self, result: SearchResult) -> None:
        """Render a selected search result in the preview pane."""
        metadata = [
            f"Type: {result.entry_type}",
            f"Timestamp: {self._format_timestamp(result.timestamp)}",
            f"Score: {result.score:.2f}",
        ]
        if result.file_path:
            metadata.append(f"Path: {result.file_path}")
        if result.source_url:
            metadata.append(f"Source: {result.source_url}")

        if result.file_path and self._is_image_path(result.file_path):
            self._set_image_preview(result.file_path, metadata)
            return

        self._set_text_preview(result.content, metadata)

    def _render_browse_entry(self, entry: BrowseEntry) -> None:
        """Render a selected browse item in the preview pane."""
        metadata = [f"Type: {entry.entry_type}", f"Path: {entry.path}"]
        if entry.timestamp is not None:
            metadata.append(f"Timestamp: {self._format_timestamp(entry.timestamp)}")
        if entry.entry_type == "folder":
            metadata.append(f"Items: {entry.child_count}")

        if entry.entry_type == "image":
            self._set_image_preview(entry.path, metadata)
            return

        preview_text = entry.content or entry.preview or entry.label
        self._set_text_preview(preview_text, metadata)

    def _set_text_preview(self, text: str, metadata: list[str]) -> None:
        """Show textual content in the preview pane."""
        self._current_image_pixmap = None
        self._preview_text.setPlainText(text)
        self._preview_meta.setText("\n".join(metadata))
        self._preview_stack.setCurrentWidget(self._preview_text)
        self._image_label.setText("No image selected")
        self._image_label.setPixmap(QPixmap())

    def _set_image_preview(self, image_path: os.PathLike[str] | str, metadata: list[str]) -> None:
        """Show an image preview when the selected item points to an image file."""
        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            self._set_text_preview("Unable to load image preview.", metadata)
            return

        self._current_image_pixmap = pixmap
        self._preview_meta.setText("\n".join(metadata))
        self._preview_stack.setCurrentIndex(1)
        self._refresh_image_preview()

    def _refresh_image_preview(self) -> None:
        """Scale the selected image to fit the current preview viewport."""
        if self._current_image_pixmap is None:
            return

        viewport = self._preview_stack.currentWidget()
        width = max(200, viewport.width() - 32)
        height = max(160, viewport.height() - 32)
        scaled = self._current_image_pixmap.scaled(
            width,
            height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)
        self._image_label.setText("")

    def _clear_preview(self, message: str = "Select an item to preview.") -> None:
        """Reset the preview pane to a neutral state."""
        self._current_image_pixmap = None
        self._preview_text.setPlainText(message)
        self._preview_meta.setText("")
        self._preview_stack.setCurrentWidget(self._preview_text)
        self._image_label.setText("No image selected")
        self._image_label.setPixmap(QPixmap())

    def _copy_selected_item(self) -> None:
        """Copy the selected search/browse item to the clipboard."""
        if self._tabs.currentWidget() is not self._browser_tab:
            return

        current_item = self._results_list.currentItem()
        if current_item is None:
            return

        item_data = current_item.data(Qt.ItemDataRole.UserRole)
        text_to_copy = ""
        if isinstance(item_data, SearchResult):
            text_to_copy = item_data.content
        elif isinstance(item_data, BrowseEntry):
            if item_data.entry_type in {"note", "clip_file"}:
                text_to_copy = item_data.content or item_data.preview
            else:
                text_to_copy = str(item_data.path)

        if not text_to_copy:
            return

        QApplication.clipboard().setText(text_to_copy)
        self._browser_status_label.setText("Copied to clipboard")
        QTimer.singleShot(2000, self._restore_browser_status)

    def _restore_browser_status(self) -> None:
        """Restore a neutral status message after transient actions."""
        if self._latest_query:
            self._browser_status_label.setText(f"Found {self._results_list.count()} results")
        else:
            self._browser_status_label.setText(
                f"Showing {self._results_list.count()} recent items"
            )

    def _activate_current_item(self) -> None:
        """Activate the selected item when Return is pressed."""
        if self._tabs.currentWidget() is self._browser_tab:
            self._open_selected_item()

    def _open_selected_item(self, item: QListWidgetItem | None = None) -> None:
        """Open the selected file or folder in the OS explorer."""
        selected_item = item or self._results_list.currentItem()
        if selected_item is None:
            return

        item_data = selected_item.data(Qt.ItemDataRole.UserRole)
        target_path = None
        if isinstance(item_data, SearchResult):
            target_path = item_data.file_path
        elif isinstance(item_data, BrowseEntry):
            target_path = item_data.path

        if target_path is None:
            self._copy_selected_item()
            return

        try:
            if hasattr(os, "startfile"):
                os.startfile(target_path)  # type: ignore[attr-defined]
            else:
                logger.info("Open item: %s", target_path)
            self._browser_status_label.setText(f"Opened {target_path}")
        except OSError:
            logger.exception("Failed to open item: %s", target_path)
            self._browser_status_label.setText("Unable to open selected item")

    def _mark_dirty(self) -> None:
        """Mark the note editor as dirty after a user edit."""
        self._is_dirty = True
        if self._current_date:
            self._note_status_label.setText(f"Unsaved changes for {self._current_date}")

    def _build_item_label(self, item_data: SearchResult | BrowseEntry) -> str:
        """Return a compact label for the list view."""
        if isinstance(item_data, SearchResult):
            timestamp = item_data.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return f"[{item_data.entry_type}] {timestamp} {item_data.preview}"

        if item_data.entry_type == "folder":
            return f"[folder] {item_data.label} ({item_data.child_count} items)"

        timestamp = self._format_timestamp(item_data.timestamp)
        return f"[{item_data.entry_type}] {timestamp} {item_data.label}"

    @staticmethod
    def _is_image_path(path: os.PathLike[str] | str) -> bool:
        """Return whether the path points to a previewable image."""
        return str(path).lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))

    @staticmethod
    def _format_timestamp(value: object) -> str:
        """Format timestamps in a stable UI-friendly form."""
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return "Unknown"

    def _center_on_primary_screen(self) -> None:
        """Place the window near the top center of the main screen."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        x = geometry.x() + (geometry.width() - self.width()) // 2
        y = geometry.y() + max(40, geometry.height() // 8)
        self.move(x, y)
