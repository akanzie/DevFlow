"""
Clipboard monitoring service for DailyClip
Monitors system clipboard and captures content
"""

import asyncio
import pyperclip
from typing import Optional, Callable
from datetime import datetime
import threading
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.entities import ClipItem
from core.interfaces import IStorageService, ISearchService, IClipboardMonitor
from core.config import AppConfig

class ClipboardMonitorService(IClipboardMonitor):
    """Clipboard monitoring implementation"""
    
    def __init__(self, storage_service: IStorageService, search_service: ISearchService):
        self.storage_service = storage_service
        self.search_service = search_service
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._last_clipboard_content = ""
        self._clip_callbacks: list[Callable[[ClipItem], None]] = []
    
    def add_clip_callback(self, callback: Callable[[ClipItem], None]) -> None:
        """Add callback for new clips"""
        self._clip_callbacks.append(callback)
    
    def remove_clip_callback(self, callback: Callable[[ClipItem], None]) -> None:
        """Remove callback"""
        if callback in self._clip_callbacks:
            self._clip_callbacks.remove(callback)
    
    async def start_monitoring(self) -> None:
        """Start clipboard monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("📝 Clipboard monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop clipboard monitoring"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        print("📝 Clipboard monitoring stopped")
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self._monitoring
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self._monitoring:
            try:
                # Get current clipboard content
                current_content = pyperclip.paste()
                
                # Check if content changed
                if current_content != self._last_clipboard_content:
                    self._last_clipboard_content = current_content
                    
                    # Process new clipboard content
                    asyncio.run(self._process_clipboard(current_content))
                
                # Wait before next check
                time.sleep(AppConfig.CLIPBOARD_CHECK_INTERVAL)
                
            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
                time.sleep(AppConfig.CLIPBOARD_CHECK_INTERVAL)
    
    async def _process_clipboard(self, content: str) -> None:
        """Process new clipboard content"""
        try:
            # Validate content
            if not content or len(content) > AppConfig.MAX_CLIP_LENGTH:
                return
            
            # Create clip item
            clip = ClipItem.create_text(content)
            
            # Store to file
            await self.storage_service.append_clip(clip)
            
            # Add to search index
            await self.search_service.add_clip_to_index(clip)
            
            # Notify callbacks
            for callback in self._clip_callbacks:
                try:
                    callback(clip)
                except Exception as e:
                    print(f"Error in clip callback: {e}")
            
            print(f"📋 Captured clip: {content[:50]}...")
            
        except Exception as e:
            print(f"Error processing clipboard: {e}")
    
    async def get_recent_clips(self, limit: int = 10) -> list[ClipItem]:
        """Get recent clips from today"""
        today = datetime.now().strftime("%Y-%m-%d")
        clips = await self.storage_service.get_clips_for_date(today)
        return clips[-limit:]  # Return last N clips
