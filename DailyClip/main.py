"""
DailyClip - Clipboard Manager & Productivity Tool
Main application entry point - Phase 2 MVP Integration
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon

from core import AppConfig
from container import container
from infrastructure import (
    FileStorageService,
    DuckDBSearchService,
    ClipboardMonitorService,
    GlobalHotkeyService
)
from presentation.quick_search import QuickSearchWindow

class DailyClipApp(QObject):
    """Main application class with Phase 2 MVP features"""
    
    # Signals for inter-service communication
    clipboard_updated = pyqtSignal(object)  # ClipItem
    
    def __init__(self):
        super().__init__()
        self.config = AppConfig()
        
        # Services
        self.storage_service = None
        self.search_service = None
        self.clipboard_monitor = None
        self.hotkey_service = None
        self.quick_search_window = None
        
        # PyQt application
        self.app = None
        self.tray_icon = None
        
        # Application state
        self.is_running = False
        
    async def initialize_services(self):
        """Initialize all Phase 2 services"""
        print(f"🚀 Starting {self.config.APP_NAME} v{self.config.APP_VERSION}")
        print(f"📁 Data directory: {self.config.get_data_dir()}")
        
        try:
            # Initialize storage service
            self.storage_service = FileStorageService()
            
            # Initialize search service
            self.search_service = DuckDBSearchService(
                storage_path=self.config.get_data_dir()
            )
            
            # Build search index from existing data
            print("🔍 Building search index...")
            await self.search_service.build_index()
            
            # Initialize clipboard monitor
            self.clipboard_monitor = ClipboardMonitorService(
                storage_service=self.storage_service,
                search_service=self.search_service
            )
            
            # Connect clipboard updates
            self.clipboard_monitor.clipboard_changed.connect(self.on_clipboard_changed)
            
            # Initialize hotkey service
            self.hotkey_service = GlobalHotkeyService()
            self.hotkey_service.quick_search_triggered.connect(self.show_quick_search)
            
            # Initialize UI
            self.quick_search_window = QuickSearchWindow(
                search_service=self.search_service,
                storage_service=self.storage_service
            )
            
            # Ensure today's folder exists
            today = datetime.now().strftime("%Y-%m-%d")
            await self.storage_service.create_daily_folder(today)
            
            print(f"✅ All services initialized successfully")
            
        except Exception as e:
            print(f"❌ Service initialization failed: {e}")
            raise
    
    def setup_gui(self):
        """Setup PyQt6 GUI with system tray"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(self.config.APP_NAME)
        self.app.setApplicationVersion(self.config.APP_VERSION)
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("⚠️ System tray is not available")
            return False
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setToolTip(f"{self.config.APP_NAME} - Clipboard Manager")
        
        # Create context menu
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        
        # Add menu actions
        search_action = menu.addAction("🔍 Quick Search (Alt+Space)")
        search_action.triggered.connect(self.show_quick_search)
        
        note_action = menu.addAction("📝 New Note (Alt+N)")
        note_action.triggered.connect(self.create_new_note)
        
        screenshot_action = menu.addAction("📸 Screenshot (Alt+S)")
        screenshot_action.triggered.connect(self.take_screenshot)
        
        menu.addSeparator()
        
        quit_action = menu.addAction("❌ Quit")
        quit_action.triggered.connect(self.quit_app)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
        print("✅ GUI setup completed")
        return True
    
    def on_clipboard_changed(self, clip_item):
        """Handle clipboard change events"""
        print(f"📋 New clip: {clip_item.content[:50]}...")
        self.clipboard_updated.emit(clip_item)
    
    def show_quick_search(self):
        """Show quick search window"""
        if self.quick_search_window:
            self.quick_search_window.show_window()
            print("🔍 Quick search activated")
    
    def create_new_note(self):
        """Create new daily note"""
        print("📝 Creating new note...")
        # TODO: Implement note creation dialog
        
    def take_screenshot(self):
        """Take screenshot"""
        print("📸 Taking screenshot...")
        # TODO: Implement screenshot functionality
    
    async def start_services(self):
        """Start all background services"""
        if self.clipboard_monitor:
            await self.clipboard_monitor.start_monitoring()
            print("📋 Clipboard monitoring started")
        
        if self.hotkey_service:
            self.hotkey_service.start_listener()
            print("⌨️ Global hotkeys activated")
        
        self.is_running = True
    
    async def stop_services(self):
        """Stop all background services"""
        self.is_running = False
        
        if self.clipboard_monitor:
            await self.clipboard_monitor.stop_monitoring()
            print("📋 Clipboard monitoring stopped")
        
        if self.hotkey_service:
            self.hotkey_service.stop_listener()
            print("⌨️ Global hotkeys deactivated")
    
    def quit_app(self):
        """Quit application"""
        print("👋 Shutting down DailyClip...")
        
        # Stop services asynchronously
        if self.is_running:
            asyncio.create_task(self.stop_services())
        
        # Hide UI
        if self.quick_search_window:
            self.quick_search_window.hide()
        
        if self.tray_icon:
            self.tray_icon.hide()
        
        # Quit Qt application
        if self.app:
            self.app.quit()
    
    async def run(self):
        """Main application loop"""
        try:
            # Initialize services
            await self.initialize_services()
            
            # Setup GUI
            if not self.setup_gui():
                print("❌ Failed to setup GUI")
                return
            
            # Start background services
            await self.start_services()
            
            # Show welcome message
            print("🎯 DailyClip is running!")
            print("🔍 Quick Search: Alt+Space")
            print("📝 New Note: Alt+N")
            print("📸 Screenshot: Alt+S")
            print("📋 Monitoring clipboard...")
            
            # Run Qt event loop
            if self.app:
                self.app.exec()
                
        except KeyboardInterrupt:
            print("\n⏹️ User interrupted")
        except Exception as e:
            print(f"❌ Application error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.stop_services()
            self.quit_app()

async def main():
    """Async main function"""
    app = DailyClipApp()
    await app.run()

if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
