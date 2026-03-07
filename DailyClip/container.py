"""Dependency injection container for DailyClip."""

from __future__ import annotations

from dependency_injector import containers, providers

from DailyClip.common.async_runtime import AsyncRuntime
from DailyClip.core.config import AppConfig
from DailyClip.infrastructure.clipboard import ClipboardMonitorService
from DailyClip.infrastructure.hotkey import GlobalHotkeyService
from DailyClip.infrastructure.screen_capture import ScreenCaptureService
from DailyClip.infrastructure.search import DuckDBSearchService
from DailyClip.infrastructure.storage import FileStorageService


class Container(containers.DeclarativeContainer):
    """Declarative container for core application services."""

    config = providers.Configuration()

    async_runtime = providers.Singleton(AsyncRuntime)
    storage_service = providers.Singleton(
        FileStorageService,
        data_dir=config.data_dir,
    )
    search_service = providers.Singleton(
        DuckDBSearchService,
        storage_path=config.data_dir,
    )
    clipboard_monitor = providers.Singleton(
        ClipboardMonitorService,
        storage_service=storage_service,
        search_service=search_service,
        runtime=async_runtime,
    )
    hotkey_service = providers.Singleton(GlobalHotkeyService)
    screen_capture_service = providers.Singleton(ScreenCaptureService)


def build_container() -> Container:
    """Build and configure the default application container."""
    container = Container()
    container.config.from_dict({'data_dir': str(AppConfig.get_data_dir())})
    return container
