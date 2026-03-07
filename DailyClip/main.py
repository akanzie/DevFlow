"""DailyClip application bootstrap."""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication

from DailyClip.application.controller import AppController
from DailyClip.common.logging_config import configure_logging
from DailyClip.container import build_container

logger = logging.getLogger(__name__)


def main() -> int:
    """Create the Qt application, start the controller, and run the event loop."""
    configure_logging()

    app = QApplication(sys.argv)
    app.setApplicationName('DailyClip')
    app.setQuitOnLastWindowClosed(False)

    container = build_container()
    controller = AppController(
        app=app,
        runtime=container.async_runtime(),
        storage_service=container.storage_service(),
        search_service=container.search_service(),
        clipboard_monitor=container.clipboard_monitor(),
        hotkey_service=container.hotkey_service(),
        screen_capture_service=container.screen_capture_service(),
    )

    app.aboutToQuit.connect(controller.stop)

    try:
        controller.start()
        return app.exec()
    except Exception:
        logger.exception('DailyClip failed to start.')
        controller.stop()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
