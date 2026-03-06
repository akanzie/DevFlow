"""
Global Hotkey Service for DailyClip
Handles system-wide hotkeys (Alt+Space, Alt+N, Alt+S)
"""

import keyboard
import threading
from typing import Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from core.config import AppConfig

class GlobalHotkeyService(QObject):
    """Global hotkey manager using keyboard library"""
    
    # Signals for hotkey events
    quick_search_triggered = pyqtSignal()
    new_note_triggered = pyqtSignal()
    screenshot_triggered = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._registered_hotkeys = {}
        self._listener_thread: Optional[threading.Thread] = None
        self._running = False
        
    def register_default_hotkeys(self):
        """Register default DailyClip hotkeys"""
        self.register_hotkey(AppConfig.HOTKEY_QUICK_SEARCH, self._on_quick_search)
        self.register_hotkey(AppConfig.HOTKEY_NEW_NOTE, self._on_new_note)
        self.register_hotkey(AppConfig.HOTKEY_SCREENSHOT, self._on_screenshot)
        
        print(f"🔥 Registered hotkeys:")
        print(f"   {AppConfig.HOTKEY_QUICK_SEARCH} - Quick Search")
        print(f"   {AppConfig.HOTKEY_NEW_NOTE} - New Note")
        print(f"   {AppConfig.HOTKEY_SCREENSHOT} - Screenshot")
    
    def register_hotkey(self, key_combo: str, callback: Callable[[], None]) -> bool:
        """Register a global hotkey"""
        try:
            keyboard.add_hotkey(key_combo, callback)
            self._registered_hotkeys[key_combo] = callback
            return True
        except Exception as e:
            print(f"❌ Failed to register hotkey {key_combo}: {e}")
            return False
    
    def unregister_hotkey(self, key_combo: str) -> bool:
        """Unregister a global hotkey"""
        try:
            keyboard.remove_hotkey(key_combo)
            self._registered_hotkeys.pop(key_combo, None)
            return True
        except Exception as e:
            print(f"❌ Failed to unregister hotkey {key_combo}: {e}")
            return False
    
    def start_listener(self):
        """Start hotkey listener in background thread"""
        if self._running:
            return
        
        self._running = True
        self._listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
        self._listener_thread.start()
        print("🔥 Global hotkey listener started")
    
    def stop_listener(self):
        """Stop hotkey listener"""
        if not self._running:
            return
        
        self._running = False
        keyboard.unhook_all()
        
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=1.0)
        
        print("⏹️ Global hotkey listener stopped")
    
    def _listener_loop(self):
        """Background loop for hotkey listening"""
        try:
            # This will block until keyboard.unhook_all() is called
            keyboard.wait()
        except Exception as e:
            print(f"❌ Hotkey listener error: {e}")
    
    def _on_quick_search(self):
        """Handle quick search hotkey"""
        print("🔍 Quick search hotkey triggered")
        # Use QTimer to emit signal in main thread
        QTimer.singleShot(0, self.quick_search_triggered.emit)
    
    def _on_new_note(self):
        """Handle new note hotkey"""
        print("📝 New note hotkey triggered")
        QTimer.singleShot(0, self.new_note_triggered.emit)
    
    def _on_screenshot(self):
        """Handle screenshot hotkey"""
        print("📸 Screenshot hotkey triggered")
        QTimer.singleShot(0, self.screenshot_triggered.emit)
    
    def is_listening(self) -> bool:
        """Check if hotkey listener is running"""
        return self._running
    
    def get_registered_hotkeys(self) -> dict:
        """Get all registered hotkeys"""
        return self._registered_hotkeys.copy()
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        self.stop_listener()
