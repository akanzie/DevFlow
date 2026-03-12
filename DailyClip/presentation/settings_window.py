"""Settings window for DailyClip."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QKeySequenceEdit, QPushButton, QTabWidget, QWidget, QLabel, QMessageBox
)

from DailyClip.core.config import AppConfig


class SettingsWindow(QDialog):
    """Dialog to manage application settings and hotkeys."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Initialize the settings UI with tabs."""
        self.setWindowTitle("DailyClip Settings")
        self.setMinimumWidth(400)
        self.setModal(True)

        main_layout = QVBoxLayout(self)

        # 1. Tabs
        self._tabs = QTabWidget()
        
        # Tab Hotkeys
        self._hotkey_tab = QWidget()
        self._hotkey_layout = QFormLayout(self._hotkey_tab)
        
        self._qs_hotkey_edit = QKeySequenceEdit(self)
        self._nn_hotkey_edit = QKeySequenceEdit(self)
        
        self._hotkey_layout.addRow("Quick Search:", self._qs_hotkey_edit)
        self._hotkey_layout.addRow("New Note:", self._nn_hotkey_edit)
        
        self._tabs.addTab(self._hotkey_tab, "Hotkeys")
        
        # Tab Storage (Placeholder cho tương lai)
        self._storage_tab = QWidget()
        storage_layout = QFormLayout(self._storage_tab)
        storage_layout.addRow(QLabel("Storage Path:"), QLabel(AppConfig.BASE_DIR.as_posix()))
        self._tabs.addTab(self._storage_tab, "Storage")

        main_layout.addWidget(self._tabs)

        # 2. Buttons
        button_layout = QHBoxLayout()
        self._save_btn = QPushButton("Save")
        self._save_btn.setDefault(True)
        self._save_btn.clicked.connect(self._save_settings)
        
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self._save_btn)
        button_layout.addWidget(self._cancel_btn)
        
        main_layout.addLayout(button_layout)

    def _load_settings(self) -> None:
        """Load current configurations into the widgets."""
        # Giả định AppConfig có các thuộc tính này
        qs_key = getattr(AppConfig, "HOTKEY_QUICK_SEARCH", "Alt+Space")
        nn_key = getattr(AppConfig, "HOTKEY_NEW_NOTE", "Alt+N")
        
        self._qs_hotkey_edit.setKeySequence(QKeySequence(qs_key))
        self._nn_hotkey_edit.setKeySequence(QKeySequence(nn_key))

    def _save_settings(self) -> None:
        """Save the new settings back to AppConfig and notify services."""
        new_qs = self._qs_hotkey_edit.keySequence().toString()
        new_nn = self._nn_hotkey_edit.keySequence().toString()

        if not new_qs or not new_nn:
            QMessageBox.warning(self, "Invalid Hotkey", "Hotkeys cannot be empty.")
            return

        # 1. Cập nhật AppConfig (Cần đảm bảo AppConfig có method update hoặc save)
        AppConfig.HOTKEY_QUICK_SEARCH = new_qs
        AppConfig.HOTKEY_NEW_NOTE = new_nn
        
        # 2. Ở đây bạn nên gọi một method để lưu vào file config.ini/json
        # AppConfig.save_to_disk() 

        # 3. Thông báo cho người dùng
        # Chú ý: Cần trigger HotkeyService.re_register() ở main controller sau khi accept()
        self.accept()
