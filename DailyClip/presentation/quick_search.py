"""
PyQt6 Quick Search Window for DailyClip
Global search interface with hotkey activation (Alt+Space)
"""

import sys
from typing import List, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QTextEdit, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QKeySequence, QShortcut, QFont, QPalette, QColor

from core.entities import ClipItem, SearchResult
from core.interfaces import ISearchService, IStorageService
from core.config import AppConfig

class SearchWorker(QThread):
    """Background worker for search operations"""
    search_completed = pyqtSignal(list)
    search_error = pyqtSignal(str)
    
    def __init__(self, search_service: ISearchService):
        super().__init__()
        self.search_service = search_service
        self.query = ""
        self.limit = 50
    
    def set_query(self, query: str, limit: int = 50):
        """Set search query"""
        self.query = query
        self.limit = limit
    
    def run(self):
        """Execute search in background"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(
                self.search_service.search(self.query, self.limit)
            )
            loop.close()
            self.search_completed.emit(results)
        except Exception as e:
            self.search_error.emit(str(e))

class QuickSearchWindow(QMainWindow):
    """Quick search window for DailyClip"""
    
    def __init__(self, search_service: ISearchService, storage_service: IStorageService):
        super().__init__()
        self.search_service = search_service
        self.storage_service = storage_service
        self.search_worker = SearchWorker(search_service)
        self.current_results: List[SearchResult] = []
        
        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()
        
        # Hide initially, will be shown by hotkey
        self.hide()
    
    def _setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("DailyClip - Quick Search")
        self.setFixedSize(800, 600)
        
        # Make window frameless and always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set dark theme
        self._apply_dark_theme()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search clipboard history...")
        self.search_input.setFont(QFont("Segoe UI", 12))
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)
        
        # Results splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setFont(QFont("Segoe UI", 10))
        self.results_list.itemClicked.connect(self._on_result_selected)
        self.results_list.itemDoubleClicked.connect(self._on_result_activated)
        splitter.addWidget(self.results_list)
        
        # Preview panel
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # Preview header
        preview_header = QLabel("Preview")
        preview_header.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        preview_layout.addWidget(preview_header)
        
        # Preview content
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 10))
        preview_layout.addWidget(self.preview_text)
        
        # Preview metadata
        self.preview_meta = QLabel()
        self.preview_meta.setFont(QFont("Segoe UI", 9))
        preview_layout.addWidget(self.preview_meta)
        
        splitter.addWidget(preview_widget)
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        # Bottom panel
        bottom_panel = QHBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready")
        bottom_panel.addWidget(self.status_label)
        
        bottom_panel.addStretch()
        
        # Action buttons
        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self._copy_selected)
        bottom_panel.addWidget(self.copy_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.hide)
        bottom_panel.addWidget(self.close_button)
        
        layout.addLayout(bottom_panel)
        
        # Center window on screen
        self._center_on_screen()
    
    def _apply_dark_theme(self):
        """Apply dark theme to the window"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Escape to close
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.hide)
        
        # Ctrl+C to copy selected
        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        copy_shortcut.activated.connect(self._copy_selected)
        
        # Enter to activate selected
        enter_shortcut = QShortcut(QKeySequence("Return"), self)
        enter_shortcut.activated.connect(self._activate_selected)
    
    def _connect_signals(self):
        """Connect worker signals"""
        self.search_worker.search_completed.connect(self._on_search_completed)
        self.search_worker.search_error.connect(self._on_search_error)
    
    def _center_on_screen(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 3  # Upper third
        self.move(x, y)
    
    def show_window(self):
        """Show and focus the search window"""
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    @pyqtSlot(str)
    def _on_search_changed(self, text: str):
        """Handle search input changes"""
        if not text.strip():
            self.results_list.clear()
            self.preview_text.clear()
            self.preview_meta.clear()
            self.status_label.setText("Ready")
            return
        
        # Debounce search
        QTimer.singleShot(300, lambda: self._perform_search(text))
    
    def _perform_search(self, query: str):
        """Perform search if query hasn't changed"""
        if query != self.search_input.text():
            return  # Query changed, ignore
        
        self.status_label.setText("Searching...")
        self.search_worker.set_query(query)
        if not self.search_worker.isRunning():
            self.search_worker.start()
    
    @pyqtSlot(list)
    def _on_search_completed(self, results: List[SearchResult]):
        """Handle search completion"""
        self.current_results = results
        self._update_results_list()
        self.status_label.setText(f"Found {len(results)} results")
    
    @pyqtSlot(str)
    def _on_search_error(self, error: str):
        """Handle search errors"""
        self.status_label.setText(f"Search error: {error}")
        print(f"Search error: {error}")
    
    def _update_results_list(self):
        """Update results list widget"""
        self.results_list.clear()
        
        for result in self.current_results:
            clip = result.clip
            
            # Create display text
            timestamp = clip.timestamp.strftime("%H:%M")
            preview = result.preview[:100] + "..." if len(result.preview) > 100 else result.preview
            
            item_text = f"[{timestamp}] {preview}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, result)
            
            self.results_list.addItem(item)
        
        # Select first item if available
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
            self._on_result_selected(self.results_list.item(0))
    
    @pyqtSlot()
    def _on_result_selected(self, item: QListWidgetItem):
        """Handle result selection"""
        if not item:
            return
        
        result: SearchResult = item.data(Qt.ItemDataRole.UserRole)
        clip = result.clip
        
        # Update preview
        self.preview_text.setPlainText(clip.content)
        
        # Update metadata
        meta_text = f"Type: {clip.clip_type} | Format: {clip.format} | Score: {result.score:.2f}"
        if clip.source_url:
            meta_text += f" | Source: {clip.source_url}"
        self.preview_meta.setText(meta_text)
    
    @pyqtSlot()
    def _on_result_activated(self, item: QListWidgetItem):
        """Handle result double-click/activation"""
        self._copy_selected()
        self.hide()
    
    @pyqtSlot()
    def _copy_selected(self):
        """Copy selected result to clipboard"""
        current_item = self.results_list.currentItem()
        if not current_item:
            return
        
        result: SearchResult = current_item.data(Qt.ItemDataRole.UserRole)
        clip = result.clip
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(clip.content)
        
        self.status_label.setText("Copied to clipboard!")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
    
    @pyqtSlot()
    def _activate_selected(self):
        """Activate selected item (Enter key)"""
        current_item = self.results_list.currentItem()
        if current_item:
            self._on_result_activated(current_item)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Down:
            # Move to next item
            current_row = self.results_list.currentRow()
            if current_row < self.results_list.count() - 1:
                self.results_list.setCurrentRow(current_row + 1)
        elif event.key() == Qt.Key.Key_Up:
            # Move to previous item
            current_row = self.results_list.currentRow()
            if current_row > 0:
                self.results_list.setCurrentRow(current_row - 1)
        else:
            super().keyPressEvent(event)
