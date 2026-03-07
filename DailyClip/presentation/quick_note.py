"""Quick note UI for DailyClip."""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import QLabel, QMainWindow, QPlainTextEdit, QVBoxLayout, QWidget

from DailyClip.core.config import AppConfig


class QuickNoteWindow(QMainWindow):
    """Floating Markdown editor with periodic autosave."""

    def __init__(
        self,
        save_callback: Callable[[str, str], None],
        autosave_seconds: int,
    ) -> None:
        super().__init__()
        self._save_callback = save_callback
        self._current_date = ''
        self._is_dirty = False

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(autosave_seconds * 1_000)
        self._autosave_timer.timeout.connect(self.save_now)

        self._setup_ui()
        self.hide()

    def set_note_content(self, date_str: str, content: str) -> None:
        """Load note content into the editor without triggering autosave."""
        self._current_date = date_str
        self._editor.blockSignals(True)
        self._editor.setPlainText(content)
        self._editor.blockSignals(False)
        self._status_label.setText(f'Editing {date_str}')
        self._is_dirty = False

    def show_window(self) -> None:
        """Show and focus the note window."""
        self.show()
        self.raise_()
        self.activateWindow()
        self._editor.setFocus()
        self._autosave_timer.start()

    def save_now(self) -> None:
        """Save the current note content if it changed."""
        if not self._current_date or not self._is_dirty:
            return

        self._save_callback(self._current_date, self._editor.toPlainText())
        self._status_label.setText(f'Saved {self._current_date}')
        self._is_dirty = False

    def keyPressEvent(self, event) -> None:
        """Save and hide the editor when Escape is pressed."""
        if event.matches(QKeySequence.StandardKey.Cancel):
            self.save_now()
            self.hide()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        """Hide instead of destroying the note window."""
        self.save_now()
        self.hide()
        event.ignore()

    def _setup_ui(self) -> None:
        """Initialize the note editor UI."""
        self.setWindowTitle(f'{AppConfig.APP_NAME} Quick Note')
        self.setMinimumSize(720, 520)

        root = QWidget(self)
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self._status_label = QLabel('Ready', self)
        layout.addWidget(self._status_label)

        self._editor = QPlainTextEdit(self)
        self._editor.setPlaceholderText('# Daily note')
        self._editor.setFont(QFont('Consolas', 11))
        self._editor.textChanged.connect(self._mark_dirty)
        layout.addWidget(self._editor, 1)

        QShortcut(QKeySequence('Escape'), self, activated=self._hide_with_save)

    def _hide_with_save(self) -> None:
        """Save the note and hide the window."""
        self.save_now()
        self.hide()

    def _mark_dirty(self) -> None:
        """Mark the editor as dirty after a user edit."""
        self._is_dirty = True
        if self._current_date:
            self._status_label.setText(f'Unsaved changes for {self._current_date}')
