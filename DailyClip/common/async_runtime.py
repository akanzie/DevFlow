"""Background asyncio runtime used by UI and worker threads."""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import Future
from typing import Any


class AsyncRuntime:
    """Owns a background asyncio loop for cross-thread coroutine execution."""

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()

    def start(self) -> None:
        """Start the runtime if it is not already running."""
        if self.is_running():
            return

        self._ready.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name='dailyclip-async-runtime',
            daemon=True,
        )
        self._thread.start()
        self._ready.wait(timeout=5)

    def stop(self) -> None:
        """Stop the background runtime and wait for shutdown."""
        if not self._loop:
            return

        loop = self._loop
        loop.call_soon_threadsafe(loop.stop)
        if self._thread:
            self._thread.join(timeout=5)

        self._loop = None
        self._thread = None
        self._ready.clear()

    def submit(self, coroutine: Any) -> Future[Any]:
        """Submit a coroutine object to the background loop."""
        if not self._loop:
            raise RuntimeError('AsyncRuntime is not running.')
        return asyncio.run_coroutine_threadsafe(coroutine, self._loop)

    def is_running(self) -> bool:
        """Return whether the runtime loop is available."""
        return self._loop is not None and self._loop.is_running()

    def _run_loop(self) -> None:
        """Initialize and own the asyncio loop on a background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        self._ready.set()
        try:
            loop.run_forever()
        finally:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            loop.close()
