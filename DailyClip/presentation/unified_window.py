"""Merged search, browse, preview, and note UI for DailyClip."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from datetime import datetime
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    QThread,
    QTimer,
    Qt,
    pyqtSignal,
    QSize
)
from PyQt6.QtGui import QFont, QKeySequence, QPixmap, QShortcut, QAction, QTextCursor, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QTextBrowser,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
import markdown

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.core.config import AppConfig
from DailyClip.core.entities import BrowseEntry, SearchResult
from DailyClip.core.interfaces import IClipboardMonitor, ISearchService, IStorageService

logger = logging.getLogger(__name__)

# Window geometry constants
_COMPACT_HEIGHT = 60      # Height when only search bar is visible
_EXPANDED_HEIGHT = 680    # Height when full panel is open
_WINDOW_WIDTH = 860
_ANIM_DURATION_MS = 220


class WorkspaceLoadWorker(QThread):
    """Run search or browse work off the UI thread."""

    load_completed = pyqtSignal(str, str, list)
    load_failed = pyqtSignal(str, str)

    def __init__(
        self,
        runtime: AsyncRuntime,
        search_service: ISearchService,
        storage_service: IStorageService,
        clipboard_monitor: IClipboardMonitor | None,
        mode: str,
        query: str,
        limit: int,
    ) -> None:
        super().__init__()
        self._runtime = runtime
        self._search_service = search_service
        self._storage_service = storage_service
        self._clipboard_monitor = clipboard_monitor
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

class UnifiedMainWindow(QWidget):
    """Unified workspace window for search, browse, preview, and notes.

    The window has two visual states:
      - Compact: only the search bar is visible (Spotlight-style floating bar)
      - Expanded: search bar + full list/preview/note pane is visible

    Call show_compact() to raise the window in compact mode.
    Press Esc to dismiss: expanded→compact first, then compact→hide.
    """

    def __init__(
        self,
        search_service: ISearchService,
        storage_service: IStorageService,
        runtime: AsyncRuntime,
        save_callback: Callable[[str, str], None],
        autosave_seconds: int,
        clipboard_monitor: IClipboardMonitor | None = None,
    ) -> None:
        # Frameless + always on top
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._search_service = search_service
        self._storage_service = storage_service
        self._clipboard_monitor = clipboard_monitor
        self._runtime = runtime
        self._save_callback = save_callback
        self._autosave_seconds = autosave_seconds
        self._current_date = ""
        self._is_dirty = False
        self._current_image_pixmap: QPixmap | None = None
        self._active_worker: WorkspaceLoadWorker | None = None
        self._pending_request: tuple[str, str] | None = None
        self._latest_mode = "browse"
        self._latest_query = ""
        self._current_items: list[SearchResult | BrowseEntry] = []
        self._selected_entry_id: str | None = None
        self._is_expanded = False
        self._always_on_top = True
        self._drag_pos: Any = None

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

    # ------------------------------------------------------------------
    # Public API — state control
    # ------------------------------------------------------------------

    def show_compact(self) -> None:
        """Show the window in compact (Spotlight bar) mode and focus search."""
        self._center_on_primary_screen()
        self._set_expanded(False, animate=False)
        self._show_window()
        self._search_bar.setFocus()
        self._search_bar.selectAll()

    def show_search_view(self) -> None:
        """Expand the window and show the search/browse view (legacy API)."""
        self._stack.setCurrentWidget(self._search_widget)
        self._autosave_timer.stop()
        self._start_auto_refresh()
        self._set_expanded(True)
        self._show_window()
        self._search_bar.setFocus()
        if self._search_bar.text().strip():
            self._search_bar.selectAll()
            self._schedule_load("search", immediate=True)
        else:
            self._schedule_load("browse", immediate=True)

    def show_note_view(self) -> None:
        """Expand the window and show the note editor view."""
        self._stack.setCurrentWidget(self._note_widget)
        self._stop_auto_refresh()
        self._set_expanded(True)
        self._show_window()
        self._note_widget.setFocus()
        self._autosave_timer.start()

    def dismiss(self) -> None:
        """Two-level dismiss: expanded→compact, then compact→hide."""
        if self._is_expanded:
            self._set_expanded(False)
            self._search_bar.setFocus()
        else:
            self.save_note_now()
            self._autosave_timer.stop()
            self._stop_auto_refresh()
            self.hide()


    def set_note_content(self, date_str: str, content: str) -> None:
        """Load note content into the editor without triggering autosave."""
        self._current_date = date_str
        self._note_widget.set_content(date_str, content) # Delegate to NoteWidget

    def save_note_now(self) -> None:
        """Save the current note content if it changed."""
        self._note_widget.save_now() # Delegate to NoteWidget

    def keyPressEvent(self, event: Any) -> None:
        """Support keyboard navigation while the search box keeps focus."""
        if self._stack.currentWidget() is self._search_widget:
            if event.key() == Qt.Key.Key_Down:
                self._search_widget.navigate_results(1)
                return
            if event.key() == Qt.Key.Key_Up:
                self._search_widget.navigate_results(-1)
                return
        super().keyPressEvent(event)

    def resizeEvent(self, event: Any) -> None:
        """Refresh image scaling when the window size changes."""
        super().resizeEvent(event)
        if self._stack.currentWidget() is self._search_widget:
            self._search_widget._refresh_image_preview()

    def closeEvent(self, event: Any) -> None:
        """Hide instead of destroying the workspace window."""
        self.save_note_now()
        self._autosave_timer.stop()
        self._stop_auto_refresh()
        self.hide()
        event.ignore()

    def focusOutEvent(self, event: Any) -> None:  # type: ignore[override]
        """Auto-dismiss when the window loses focus (click-away)."""
        # Small delay so clicks on our own child widgets don't trigger dismiss
        QTimer.singleShot(80, self._dismiss_if_unfocused)
        super().focusOutEvent(event)

    def _dismiss_if_unfocused(self) -> None:
        """Hide only if no child widget holds focus."""
        if not self.isAncestorOf(QApplication.focusWidget() or self):  # type: ignore[arg-type]
            pass  # Re-enable auto-dismiss here if desired in future

    def _setup_ui(self) -> None:
        """Initialize widgets and layout (compact bar + expandable panel)."""
        self.setWindowTitle(AppConfig.APP_NAME)
        self.setFixedWidth(_WINDOW_WIDTH)
        self.setMinimumHeight(_COMPACT_HEIGHT)

        # Drop shadow effect via stylesheet
        self.setStyleSheet("""
            UnifiedMainWindow {
                border-radius: 10px;
                border: 1px solid #444;
            }
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Compact header bar ──────────────────────────────────────────
        header = QFrame(self)
        header.setObjectName("SpotlightHeader")
        header.setStyleSheet("""
            QFrame#SpotlightHeader {
                background: #1e1e2e;
                border-radius: 10px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        header.setFixedHeight(_COMPACT_HEIGHT)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 8, 10, 8)
        header_layout.setSpacing(8)

        # 🔍 Search icon label
        icon_lbl = QLabel("🔍")
        icon_lbl.setStyleSheet("color: #888; font-size: 16px;")
        header_layout.addWidget(icon_lbl)

        # Main search input shared across compact & expanded
        self._search_bar = QLineEdit(self)
        self._search_bar.setPlaceholderText("Search clips, notes… (type 'note' to open editor)")
        self._search_bar.setFont(QFont("Segoe UI", 13))
        self._search_bar.setStyleSheet("""
            QLineEdit {
                border: none; background: transparent;
                color: #e0e0e0; padding: 2px 0;
            }
        """)
        header_layout.addWidget(self._search_bar, 1)

        # Always-on-top pin button
        self._pin_btn = QPushButton("📌")
        self._pin_btn.setCheckable(True)
        self._pin_btn.setChecked(True)
        self._pin_btn.setFixedSize(28, 28)
        self._pin_btn.setToolTip("Toggle always on top")
        self._pin_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; font-size: 14px; }"
            "QPushButton:checked { color: #7aa2f7; }"
            "QPushButton:!checked { color: #555; }"
        )
        self._pin_btn.clicked.connect(self._toggle_always_on_top)
        header_layout.addWidget(self._pin_btn)

        # Close / dismiss button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Close (Esc)")
        close_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: #888; font-size: 14px; }"
            "QPushButton:hover { color: #e06c75; }"
        )
        close_btn.clicked.connect(self.dismiss)
        header_layout.addWidget(close_btn)

        root_layout.addWidget(header)

        # ── Expandable panel ───────────────────────────────────────────
        self._expanded_panel = QWidget(self)
        self._expanded_panel.setObjectName("ExpandedPanel")
        self._expanded_panel.setStyleSheet(
            "QWidget#ExpandedPanel { background: #181825; "
            "border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; }"
        )
        panel_layout = QVBoxLayout(self._expanded_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget(self._expanded_panel)
        panel_layout.addWidget(self._stack)

        # Search / Browse widget
        self._search_widget = SearchWidget(self._expanded_panel)
        self._search_widget._search_input.hide()   # duplicate — we use _search_bar
        self._search_widget._results_list.currentItemChanged.connect(self._on_item_selected)
        self._search_widget._results_list.itemDoubleClicked.connect(self._open_selected_item)
        self._search_widget._refresh_button.clicked.connect(self.refresh_items)
        self._search_widget._open_button.clicked.connect(self._open_selected_item)
        self._search_widget._copy_button.clicked.connect(self._copy_selected_item)
        self._search_widget._close_button.clicked.connect(self.dismiss)
        self._stack.addWidget(self._search_widget)

        # Note widget
        self._note_widget = NoteWidget(self._save_callback, self._autosave_seconds, self._expanded_panel)
        self._note_widget.back_requested.connect(self.show_search_view)
        self._stack.addWidget(self._note_widget)

        self._expanded_panel.setFixedHeight(0)   # starts collapsed
        root_layout.addWidget(self._expanded_panel)

        # Animation
        self._anim = QPropertyAnimation(self._expanded_panel, b"maximumHeight")
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setDuration(_ANIM_DURATION_MS)
        self._anim.finished.connect(self._on_anim_finished)

        self._center_on_primary_screen()
        self._search_bar.textChanged.connect(self._on_search_text_changed)

    def _setup_shortcuts(self) -> None:
        """Register keyboard shortcuts for the merged window."""
        QShortcut(QKeySequence("Escape"), self, activated=self.dismiss)
        QShortcut(
            QKeySequence("Ctrl+C"),
            self._search_widget,
            activated=self._copy_selected_item,
        )
        QShortcut(
            QKeySequence("Return"),
            self._search_widget,
            activated=self._activate_current_item,
        )
        QShortcut(QKeySequence("Enter"), self._search_widget,
                  activated=self._activate_current_item)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save_current_edit)

    def _set_expanded(self, expand: bool, animate: bool = True) -> None:
        """Animate the expandable panel open or shut."""
        target_h = (_EXPANDED_HEIGHT - _COMPACT_HEIGHT) if expand else 0
        if animate:
            self._anim.stop()
            current_h = self._expanded_panel.maximumHeight()
            if current_h >= 16_777_215:   # Qt QWIDGETSIZE_MAX — treat as 0 start
                current_h = 0
            self._anim.setStartValue(current_h)
            self._anim.setEndValue(target_h)
            self._anim.start()
        else:
            self._expanded_panel.setMaximumHeight(target_h)
            self._expanded_panel.setMinimumHeight(target_h)
        self._is_expanded = expand
        if expand:
            self.setFixedHeight(_EXPANDED_HEIGHT)
        else:
            self.setFixedHeight(_COMPACT_HEIGHT)

    def _on_anim_finished(self) -> None:
        """Finalize layout after animation completes."""
        if self._is_expanded:
            self._expanded_panel.setMinimumHeight(_EXPANDED_HEIGHT - _COMPACT_HEIGHT)
        else:
            self._expanded_panel.setMinimumHeight(0)

    def _toggle_always_on_top(self, checked: bool) -> None:
        """Toggle the window always-on-top flag."""
        self._always_on_top = checked
        if checked:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
            )
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.show()   # must re-show after setWindowFlags

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

    # Drag support for frameless window
    def mousePressEvent(self, event: Any) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event: Any) -> None:  # type: ignore[override]
        self._drag_pos = None


    def _on_search_text_changed(self, text: str) -> None:
        """Debounce search input and expand window on first keystroke."""
        self._latest_query = text.strip()
        # Expand window as soon as user starts typing
        if not self._is_expanded:
            self._stack.setCurrentWidget(self._search_widget)
            self._start_auto_refresh()
            self._set_expanded(True)
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
        if not self.isVisible() or self._stack.currentWidget() is not self._search_widget:
            return
        if self._search_timer.isActive():
            return
        # Skip refresh if currently editing
        if self._search_widget._editing_entry_id is not None:
            return
        self.refresh_items(silent=True)

    def create_new_version(self, original_id: str, new_content: str) -> None:
        """Create a new clip version and persist it via the storage service."""
        from DailyClip.core.entities import ClipItem
        new_clip = ClipItem.create_text(
            content=new_content,
            timestamp=datetime.now(),
            version_of=original_id,
        )
        try:
            self._runtime.submit(self._storage_service.append_clip(new_clip)).result(timeout=10)
            self._runtime.submit(self._search_service.index_clip(new_clip)).result(timeout=10)
            logger.info("Saved new version of %s.", original_id)
            self._search_widget._browser_status_label.setText("Version saved.")
        except Exception:
            logger.exception("Failed to save new version of %s.", original_id)
            self._search_widget._browser_status_label.setText("Save failed — check logs.")
        finally:
            self.refresh_items(silent=False)

    def delete_item(self, entry_id: str) -> None:
        """Soft-delete a clip via tombstone and refresh the view."""
        try:
            self._runtime.submit(self._storage_service.delete_clip(entry_id)).result(timeout=10)
            logger.info("Deleted clip %s.", entry_id)
            self._search_widget._browser_status_label.setText("Item deleted.")
        except Exception:
            logger.exception("Failed to delete clip %s.", entry_id)
            self._search_widget._browser_status_label.setText("Delete failed — check logs.")
        finally:
            self.refresh_items(silent=False)



    def _save_current_edit(self) -> None:
        """If in search widget and editing, trigger save."""
        if self._stack.currentWidget() is self._search_widget:
            self._search_widget._save_edit()

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
            self._search_widget._browser_status_label.setText(message)
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
            clipboard_monitor=self._clipboard_monitor,
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
        self._search_widget._results_list.clear()
        for index, item_data in enumerate(items):
            item = QListWidgetItem(self._build_item_label(item_data))
            item.setData(Qt.ItemDataRole.UserRole, item_data)
            self._search_widget._results_list.addItem(item)
            if item_data.entry_id == selected_entry_id:
                selected_row = index

        if items:
            self._search_widget._results_list.setCurrentRow(selected_row)
        else:
            self._selected_entry_id = None

        if mode == "browse":
            self._search_widget._browser_status_label.setText(f"Showing {len(items)} recent items")
        else:
            self._search_widget._browser_status_label.setText(f"Found {len(items)} results")

        if not items:
            self._search_widget._clear_preview("No items found.")

    def _on_load_failed(self, mode: str, message: str) -> None:
        """Show browse/search errors without crashing the UI."""
        logger.warning("%s load failed: %s", mode, message)
        self._search_widget._browser_status_label.setText(f"Load failed: {message}")

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
            self._search_widget._clear_preview()
            return

        item_data = current.data(Qt.ItemDataRole.UserRole)
        if isinstance(item_data, (SearchResult, BrowseEntry)):
            self._selected_entry_id = item_data.entry_id
        if isinstance(item_data, SearchResult):
            self._search_widget._render_search_result(item_data)
        elif isinstance(item_data, BrowseEntry):
            self._search_widget._render_browse_entry(item_data)
        else:
            self._search_widget._clear_preview()

    def _copy_selected_item(self) -> None:
        """Copy the selected search/browse item to the clipboard."""
        current_item = self._search_widget._results_list.currentItem()
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

        try:
            if hasattr(self, '_clipboard_monitor') and self._clipboard_monitor and hasattr(self._clipboard_monitor, 'copy_to_clipboard'):
                self._runtime.submit(self._clipboard_monitor.copy_to_clipboard(text_to_copy))
            else:
                import pyperclip
                pyperclip.copy(text_to_copy)
        except Exception as e:
            logger.exception("Copy failed")

        self._search_widget._browser_status_label.setText("Copied to clipboard")
        QTimer.singleShot(2000, self._restore_browser_status)

    def _restore_browser_status(self) -> None:
        """Restore a neutral status message after transient actions."""
        if self._latest_query:
            self._search_widget._browser_status_label.setText(f"Found {self._search_widget._results_list.count()} results")
        else:
            self._search_widget._browser_status_label.setText(
                f"Showing {self._search_widget._results_list.count()} recent items"
            )

    def _activate_current_item(self) -> None:
        """Activate the selected item or switch to note view."""
        if self._search_bar.text().strip().lower() == "note":
            self.show_note_view()
        else:
            self._open_selected_item()


    def _open_selected_item(self, item: QListWidgetItem | None = None) -> None:
        """Open the selected file or folder in the OS explorer."""
        selected_item = item or self._search_widget._results_list.currentItem()
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
            self._search_widget._browser_status_label.setText(f"Opened {target_path}")
        except OSError:
            logger.exception("Failed to open item: %s", target_path)
            self._search_widget._browser_status_label.setText("Unable to open selected item")

    def _mark_dirty(self) -> None:
        """Mark the note editor as dirty after a user edit."""
        self._is_dirty = True
        # if self._current_date:
        #     self._note_status_label.setText(f"Unsaved changes for {self._current_date}")

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


class SearchWidget(QWidget):
    """Widget for search, browsing, and previewing results."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_image_pixmap: QPixmap | None = None
        self._editing_entry_id: str | None = None
        self._original_content: str = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the search and browse tab widgets."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self._search_input = QLineEdit(self)
        self._search_input.setPlaceholderText(
            "Search clips and notes, or type 'new note' to create a new note..."
        )
        self._search_input.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self._search_input)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        layout.addWidget(splitter, 1)

        self._results_list = QListWidget(self)
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
        self._preview_text.setReadOnly(False)
        self._preview_text.setFont(QFont("Consolas", 10))
        self._preview_stack.addWidget(self._preview_text)

        self._preview_text.textChanged.connect(self._on_preview_text_changed)


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

        self._fav_button = QPushButton("⭐", self)
        self._fav_button.setToolTip("Favorite (not implemented)")
        self._fav_button.setEnabled(False)
        footer.addWidget(self._fav_button)

        self._delete_button = QPushButton("🗑️", self)
        self._delete_button.setToolTip("Delete item")
        self._delete_button.clicked.connect(self._delete_selected_item)
        footer.addWidget(self._delete_button)

        self._tag_button = QPushButton("✏️", self)
        self._tag_button.setToolTip("Rename/Tag (not implemented)")
        self._tag_button.setEnabled(False)
        footer.addWidget(self._tag_button)

        self._save_edit_button = QPushButton("💾", self)
        self._save_edit_button.setToolTip("Save edit (Ctrl+S)")
        self._save_edit_button.clicked.connect(self._save_edit)
        self._save_edit_button.setVisible(False)             # hidden by default
        footer.addWidget(self._save_edit_button)

        self._diff_button = QPushButton("📊", self)
        self._diff_button.setToolTip("Show diff")
        self._diff_button.clicked.connect(self._show_diff)
        self._diff_button.setVisible(False)
        footer.addWidget(self._diff_button)

        self._browser_status_label = QLabel("Ready", self)
        footer.addWidget(self._browser_status_label)
        footer.addStretch(1)

        self._refresh_button = QPushButton("Refresh", self)
        footer.addWidget(self._refresh_button)

        self._open_button = QPushButton("Open", self)
        footer.addWidget(self._open_button)

        self._copy_button = QPushButton("Copy", self)
        footer.addWidget(self._copy_button)

        self._close_button = QPushButton("Close", self)
        footer.addWidget(self._close_button)

        self._gallery_button = QPushButton("🖼️ Grid", self)
        self._gallery_button.setCheckable(True)
        self._gallery_button.toggled.connect(self._toggle_gallery_mode)
        footer.insertWidget(0, self._gallery_button)  # put at left

    def _on_preview_text_changed(self) -> None:
        """Enable edit mode when user types in preview."""
        if not self._editing_entry_id:
            # First change: set edit lock and show save/diff buttons
            current_item = self._results_list.currentItem()
            if current_item:
                item_data = current_item.data(Qt.ItemDataRole.UserRole)
                if isinstance(item_data, (SearchResult, BrowseEntry)):
                    self._editing_entry_id = item_data.entry_id
                    self._original_content = self._preview_text.toPlainText()
                    self._save_edit_button.setVisible(True)
                    self._diff_button.setVisible(True)
                    self._fav_button.setEnabled(False)   # disable while editing
                    self._delete_button.setEnabled(False)
        # else already editing

    def _save_edit(self) -> None:
        """Save edited text as a new version."""
        if not self._editing_entry_id:
            return
        new_content = self._preview_text.toPlainText()
        # Call parent window to create new version
        main_window = self.window()
        if isinstance(main_window, UnifiedMainWindow):
            main_window.create_new_version(self._editing_entry_id, new_content)
        # Exit edit mode
        self._exit_edit_mode()

    def _exit_edit_mode(self) -> None:
        """Reset edit flags and hide edit buttons."""
        self._editing_entry_id = None
        self._original_content = ""
        self._save_edit_button.setVisible(False)
        self._diff_button.setVisible(False)
        self._fav_button.setEnabled(True)
        self._delete_button.setEnabled(True)

    def _show_diff(self) -> None:
        """Display unified diff between original and edited content."""
        if not self._editing_entry_id:
            return
        from difflib import unified_diff
        original = self._original_content.splitlines(keepends=True)
        edited = self._preview_text.toPlainText().splitlines(keepends=True)
        diff_lines = list(unified_diff(original, edited,
                                       fromfile='Original',
                                       tofile='Edited',
                                       lineterm=''))
        if not diff_lines:
            diff_lines = ["(No changes)"]
        diff_text = ''.join(diff_lines)
        # Show in a simple dialog
        from PyQt6.QtWidgets import QDialog, QTextEdit, QVBoxLayout
        dlg = QDialog(self)
        dlg.setWindowTitle("Diff")
        dlg.resize(600, 400)
        layout = QVBoxLayout(dlg)
        text = QTextEdit()
        text.setPlainText(diff_text)
        text.setReadOnly(True)
        text.setFont(QFont("Consolas", 10))
        layout.addWidget(text)
        dlg.exec()

    def _delete_selected_item(self) -> None:
        """Delete the selected clip after confirmation."""
        current_item = self._results_list.currentItem()
        if not current_item:
            return
        item_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(item_data, (SearchResult, BrowseEntry)):
            return
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{item_data.preview}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            main_window = self.window()
            if isinstance(main_window, UnifiedMainWindow):
                main_window.delete_item(item_data.entry_id)

    def _toggle_gallery_mode(self, checked: bool) -> None:
        """Switch between list and grid (icon) view."""
        if checked:
            self._results_list.setViewMode(QListWidget.ViewMode.IconMode)
            self._results_list.setIconSize(QSize(120, 90))
            self._results_list.setGridSize(QSize(140, 120))
            self._gallery_button.setText("📋 List")
            # Repopulate with thumbnails for images
            self._refresh_thumbnails()
        else:
            self._results_list.setViewMode(QListWidget.ViewMode.ListMode)
            self._gallery_button.setText("🖼️ Grid")
            # Reload without thumbnails (refresh from parent)
            main_window = self.window()
            if isinstance(main_window, UnifiedMainWindow):
                main_window.refresh_items(silent=True)

    def _refresh_thumbnails(self) -> None:
        """Replace items with thumbnail icons for images."""
        # For simplicity, we just reload the same items but add icons for images.
        # This is a placeholder; a real implementation would generate thumbnails.
        for i in range(self._results_list.count()):
            item = self._results_list.item(i)
            item_data = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(item_data, BrowseEntry) and item_data.entry_type == "image":
                pixmap = QPixmap(str(item_data.path)).scaled(
                    100, 70, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                item.setIcon(QIcon(pixmap))
            else:
                item.setIcon(QIcon())  # no icon for non-images

    # Override mouse release to handle edit exit when selection changes
    def mouseReleaseEvent(self, event: Any) -> None:
        super().mouseReleaseEvent(event)
        # If editing and user clicks elsewhere, maybe exit edit mode?
        # But we might want to keep edit mode until explicitly saved.
        # We'll leave as is for now.
        pass

    def navigate_results(self, delta: int) -> None:
        """Move selection in the results list."""
        current_row = self._results_list.currentRow()
        next_row = max(0, min(current_row + delta, self._results_list.count() - 1))
        self._results_list.setCurrentRow(next_row)

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

        if result.file_path and UnifiedMainWindow._is_image_path(result.file_path):
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
        self._editing_entry_id = None          # lock for auto-refresh
        self._original_content = ""                    # for diff
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
            width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
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

    @staticmethod
    def _format_timestamp(value: object) -> str:
        """Format timestamps in a stable UI-friendly form."""
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return "Unknown"


class NoteWidget(QWidget):
    """Widget for note taking with Markdown preview."""
    back_requested = pyqtSignal()

    def __init__(
        self,
        save_callback: Callable[[str, str], None],
        autosave_seconds: int,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._save_callback = save_callback
        self._current_date = ''
        self._is_dirty = False

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(autosave_seconds * 1_000)
        self._autosave_timer.timeout.connect(self.save_now)

        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(300)
        self._preview_timer.timeout.connect(self._update_preview)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize the enhanced UI with split view and toolbar."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        self._status_label = QLabel('Ready', self)
        layout.addWidget(self._status_label)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        self._editor = QTextEdit(self)
        self._editor.setAcceptRichText(False)
        self._editor.setPlaceholderText('# Type your Markdown here...')
        self._editor.setFont(QFont('Consolas', 11))
        self._editor.textChanged.connect(self._on_text_changed)

        self._preview = QTextBrowser(self)
        self._preview.setOpenExternalLinks(True)
        self._apply_preview_style()

        self._splitter.addWidget(self._editor)
        self._splitter.addWidget(self._preview)
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 1)

        layout.addWidget(self._splitter)

    def _create_toolbar(self) -> QToolBar:
        """Create toolbar with Markdown formatting actions."""
        toolbar = QToolBar("Formatting")

        bold_act = QAction("B", self)
        bold_act.setShortcut(QKeySequence("Ctrl+B"))
        bold_act.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        bold_act.triggered.connect(lambda: self._wrap_selection("**", "**"))
        toolbar.addAction(bold_act)

        italic_act = QAction("I", self)
        italic_act.setShortcut(QKeySequence("Ctrl+I"))
        italic_act.setFont(QFont("Arial", 10, italic=True))
        italic_act.triggered.connect(lambda: self._wrap_selection("*", "*"))
        toolbar.addAction(italic_act)

        link_act = QAction("Link", self)
        link_act.setShortcut(QKeySequence("Ctrl+K"))
        link_act.triggered.connect(lambda: self._wrap_selection("[", "](https://)"))
        toolbar.addAction(link_act)

        back_button = QPushButton("Back to Search")
        back_button.clicked.connect(self.back_requested.emit)
        toolbar.addWidget(back_button)

        return toolbar

    def _apply_preview_style(self) -> None:
        """Dark mode CSS for the preview window."""
        css = """
            QTextBrowser {
                background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333;
                padding: 10px; line-height: 1.5;
            }
            h1, h2, h3 { color: #569cd6; } a { color: #4ec9b0; }
            code { background-color: #2d2d2d; padding: 2px; border-radius: 3px; }
        """
        self._preview.setStyleSheet(css)

    def _wrap_selection(self, prefix: str, suffix: str) -> None:
        """Wrap selected text with Markdown syntax."""
        cursor = self._editor.textCursor()
        if not cursor.hasSelection():
            cursor.insertText(f"{prefix}{suffix}")
            if "]" in suffix:
                cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(suffix) - 1)
        else:
            selected_text = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected_text}{suffix}")
        self._editor.setFocus()

    def _on_text_changed(self) -> None:
        """Handle text change: mark dirty and trigger debounced preview."""
        self._is_dirty = True
        if self._current_date:
            self._status_label.setText(f'Unsaved changes for {self._current_date}')
        self._preview_timer.start()

    def _update_preview(self) -> None:
        """Convert Markdown to HTML and update preview window."""
        text = self._editor.toPlainText()
        html = markdown.markdown(text, extensions=['extra', 'codehilite'])
        self._preview.setHtml(html)

    def set_content(self, date_str: str, content: str) -> None:
        self._current_date = date_str
        self._editor.blockSignals(True)
        self._editor.setPlainText(content)
        self._editor.blockSignals(False)
        self._update_preview()
        self._status_label.setText(f'Editing {date_str}')
        self._is_dirty = False
        self._autosave_timer.start()

    def save_now(self) -> None:
        if not self._current_date or not self._is_dirty:
            return
        self._save_callback(self._current_date, self._editor.toPlainText())
        self._status_label.setText(f'Saved {self._current_date}')
        self._is_dirty = False

    def keyPressEvent(self, event: Any) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.back_requested.emit()
        else:
            super().keyPressEvent(event)
