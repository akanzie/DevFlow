"""Screenshot capture implementation for DailyClip."""

from __future__ import annotations

import asyncio
import io

from PIL import ImageGrab

from DailyClip.core.exceptions import ScreenCaptureError
from DailyClip.core.interfaces import IScreenCaptureService


class ScreenCaptureService(IScreenCaptureService):
    """Capture fullscreen screenshots using Pillow."""

    async def capture_screenshot(self) -> bytes:
        """Capture the full screen and return PNG bytes."""
        return await asyncio.to_thread(self._capture_sync)

    @staticmethod
    def _capture_sync() -> bytes:
        """Capture the screen synchronously."""
        try:
            image = ImageGrab.grab()
        except OSError as exc:
            raise ScreenCaptureError('Unable to capture the screen.') from exc

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
