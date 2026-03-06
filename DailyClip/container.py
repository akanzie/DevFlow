"""
Dependency injection container for DailyClip
Clean Architecture with dependency injection
"""

from dependency_injector import containers, providers
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from core.interfaces import (
    IStorageService,
    ISearchService, 
    IClipboardMonitor,
    IHotkeyService,
    IScreenCaptureService
)
from infrastructure.storage import FileStorageService
from infrastructure.search import DuckDBSearchService
from infrastructure.clipboard import ClipboardMonitorService
from infrastructure.hotkey import GlobalHotkeyService

class Container(containers.DeclarativeContainer):
    """Dependency injection container"""
    
    # Configuration
    config = providers.Configuration()
    
    # Services
    storage_service = providers.Factory(
        FileStorageService,
        data_dir=Path(config.data_dir) if config.data_dir else None
    )
    
    # Services
    search_service = providers.Factory(
        DuckDBSearchService,
        storage_path=Path(config.data_dir) if config.data_dir else None
    )
    
    clipboard_monitor = providers.Factory(
        ClipboardMonitorService,
        storage_service=storage_service,
        search_service=search_service
    )
    
    hotkey_service = providers.Factory(
        GlobalHotkeyService
    )
    
    screen_capture_service = providers.Factory(
        object  # Will be replaced with actual implementation
    )

# Global container instance
container = Container()
