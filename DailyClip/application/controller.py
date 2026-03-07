"""Application controller for DailyClip."""

from __future__ import annotations

import logging
import os
from concurrent.futures import Future
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.core.config import AppConfig
from DailyClip.core.entities import ClipItem, DailyNote
from DailyClip.core.interfaces import (
    IClipboardMonitor,
    IHotkeyService,
    IScreenCaptureService,
    ISearchService,
    IStorageService,
)
from DailyClip.presentation.quick_search import QuickSearchWindow

logger = logging.getLogger(__name__)


class AppController(QObject):
    """Coordinate services, windows, tray actions, and application shutdown."""

    show_search_requested = pyqtSignal()
    show_note_requested = pyqtSignal()
    take_screenshot_requested = pyqtSignal()
    screenshot_saved = pyqtSignal(str)
    screenshot_failed = pyqtSignal(str)

    def __init__(
        self,
        app: QApplication,
        runtime: AsyncRuntime,
        storage_service: IStorageService,
        search_service: ISearchService,
        clipboard_monitor: IClipboardMonitor,
        hotkey_service: IHotkeyService,
        screen_capture_service: IScreenCaptureService,
    ) -> None:
        super().__init__()
        self._app = app
        self._runtime = runtime
        self._storage_service = storage_service
        self._search_service = search_service
        self._clipboard_monitor = clipboard_monitor
        self._hotkey_service = hotkey_service
        self._screen_capture_service = screen_capture_service

        self._workspace_window = QuickSearchWindow(
            search_service=self._search_service,
            storage_service=self._storage_service,
            runtime=self._runtime,
            save_callback=self.queue_note_save,
            autosave_seconds=AppConfig.QUICK_NOTE_AUTOSAVE_SECONDS,
        )
        self._tray_icon: QSystemTrayIcon | None = None
        self._note_created_at: dict[str, datetime] = {}
        self._last_note_future: Future[object] | None = None
        self._started = False

        self.show_search_requested.connect(self.show_quick_search)
        self.show_note_requested.connect(self.show_quick_note)
        self.take_screenshot_requested.connect(self.take_screenshot)
        self.screenshot_saved.connect(self._show_screenshot_saved)
        self.screenshot_failed.connect(self._show_screenshot_failed)

    def start(self) -> None:
        """Start runtime, services, hotkeys, and tray integration."""
        if self._started:
            return

        self._runtime.start()
        today = self._today()
        self._runtime.submit(self._bootstrap(today)).result(timeout=30)

        self._clipboard_monitor.register_callback(self._on_clip_captured)
        self._hotkey_service.register_hotkey(
            AppConfig.HOTKEY_QUICK_SEARCH,
            self.show_search_requested.emit,
        )
        self._hotkey_service.register_hotkey(
            AppConfig.HOTKEY_NEW_NOTE,
            self.show_note_requested.emit,
        )
        self._hotkey_service.register_hotkey(
            AppConfig.HOTKEY_SCREENSHOT,
            self.take_screenshot_requested.emit,
        )
        self._hotkey_service.start_listener()
        self._runtime.submit(self._clipboard_monitor.start_monitoring()).result(timeout=5)
        self._setup_tray_icon()

        self._started = True
        logger.info("DailyClip started successfully.")

    def stop(self) -> None:
        """Stop background services and release application resources."""
        if not self._started and not self._runtime.is_running():
            return

        try:
            self._workspace_window.save_note_now()
            if self._last_note_future:
                self._last_note_future.result(timeout=5)
            self._clipboard_monitor.unregister_callback(self._on_clip_captured)
            self._hotkey_service.stop_listener()
            if self._runtime.is_running():
                self._runtime.submit(self._clipboard_monitor.stop_monitoring()).result(timeout=5)
        finally:
            if self._tray_icon:
                self._tray_icon.hide()
                self._tray_icon = None
            self._workspace_window.hide()
            self._runtime.stop()
            self._started = False
            logger.info("DailyClip stopped.")

    def show_quick_search(self) -> None:
        """Show and focus the merged workspace on the search tab."""
        self._workspace_window.show_search_view()

    def show_quick_note(self) -> None:
        """Show and focus the merged workspace on the note tab."""
        date_str = self._today()
        note = self._runtime.submit(self._storage_service.get_note(date_str)).result(timeout=5)
        if note:
            self._note_created_at[date_str] = note.created_at
            self._workspace_window.set_note_content(date_str, note.content)
        else:
            self._workspace_window.set_note_content(date_str, "")
        self._workspace_window.show_note_view()

    def take_screenshot(self) -> None:
        """Capture and persist a fullscreen screenshot."""
        future = self._runtime.submit(self._capture_screenshot())
        future.add_done_callback(self._notify_screenshot_result)

    def open_today_folder(self) -> None:
        """Open today's data folder in the OS file explorer."""
        folder = AppConfig.get_daily_dir(self._today())
        if hasattr(os, "startfile"):
            os.startfile(folder)  # type: ignore[attr-defined]
        else:
            logger.info("Today folder: %s", folder)

    def queue_note_save(self, date_str: str, content: str) -> None:
        """Queue a note save without blocking the UI thread."""
        if len(content) > AppConfig.MAX_NOTE_SIZE:
            logger.warning("Skipped note save because content exceeded the size limit.")
            return

        future = self._runtime.submit(self._save_note(date_str, content))
        self._last_note_future = future
        future.add_done_callback(self._log_background_failure)

    async def _bootstrap(self, today: str) -> None:
        """Prepare storage and the search index at startup."""
        await self._storage_service.create_daily_folder(today)
        await self._search_service.rebuild_index()

    async def _save_note(self, date_str: str, content: str) -> None:
        """Persist and index note content for a specific day."""
        now = datetime.now()
        created_at = self._note_created_at.get(date_str, now)
        note = DailyNote(
            date=date_str,
            content=content,
            created_at=created_at,
            updated_at=now,
        )
        await self._storage_service.save_note(note)
        await self._search_service.index_note(note)
        self._note_created_at[date_str] = created_at
        logger.info("Saved note for %s.", date_str)

    async def _capture_screenshot(self) -> str:
        """Capture and persist a screenshot."""
        image_data = await self._screen_capture_service.capture_screenshot()
        screenshot_path = await self._storage_service.save_screenshot(image_data)
        return str(screenshot_path)

    def _setup_tray_icon(self) -> None:
        """Create the system tray menu used for background operation."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray is not available on this machine.")
            return

        tray_icon = QSystemTrayIcon(
            self._app.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView),
            self._app,
        )
        tray_icon.setToolTip(f"{AppConfig.APP_NAME} {AppConfig.APP_VERSION}")

        menu = QMenu()
        search_action = QAction("Quick Search", tray_icon)
        search_action.triggered.connect(self.show_quick_search)
        menu.addAction(search_action)

        note_action = QAction("New Note", tray_icon)
        note_action.triggered.connect(self.show_quick_note)
        menu.addAction(note_action)

        folder_action = QAction("Open Today Folder", tray_icon)
        folder_action.triggered.connect(self.open_today_folder)
        menu.addAction(folder_action)

        menu.addSeparator()

        exit_action = QAction("Exit", tray_icon)
        exit_action.triggered.connect(self._app.quit)
        menu.addAction(exit_action)

        tray_icon.setContextMenu(menu)
        tray_icon.show()
        self._tray_icon = tray_icon

    def _on_clip_captured(self, clip: ClipItem) -> None:
        """Handle new clipboard content captured in the background."""
        logger.info("Clipboard item indexed from %s", clip.timestamp.isoformat())
        if clip.clip_type == "image" and self._tray_icon:
            self._tray_icon.showMessage(
                AppConfig.APP_NAME,
                f"Saved clipboard image: {clip.file_path}",
            )

    def _notify_screenshot_result(self, future: Future[str]) -> None:
        """Display screenshot status feedback in the tray."""
        try:
            screenshot_path = future.result()
        except Exception:
            logger.exception("Screenshot capture failed.")
            self.screenshot_failed.emit("Screenshot capture failed.")
            return

        self.screenshot_saved.emit(screenshot_path)

    @staticmethod
    def _log_background_failure(future: Future[object]) -> None:
        """Log failures from fire-and-forget background tasks."""
        try:
            future.result()
        except Exception:
            logger.exception("Background operation failed.")

    @staticmethod
    def _today() -> str:
        """Return today's date string."""
        return datetime.now().strftime("%Y-%m-%d")

    def _show_screenshot_saved(self, screenshot_path: str) -> None:
        """Show a tray notification for a saved screenshot."""
        if self._tray_icon:
            self._tray_icon.showMessage(
                AppConfig.APP_NAME,
                f"Saved screenshot: {screenshot_path}",
            )

    def _show_screenshot_failed(self, message: str) -> None:
        """Show a tray notification when screenshot capture fails."""
        if self._tray_icon:
            self._tray_icon.showMessage(AppConfig.APP_NAME, message)
