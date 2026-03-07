"""Global hotkey implementation for DailyClip."""

from __future__ import annotations

import logging

import keyboard

from DailyClip.core.interfaces import HotkeyCallback, IHotkeyService

logger = logging.getLogger(__name__)


class GlobalHotkeyService(IHotkeyService):
    """Register and manage system-wide hotkeys using the keyboard package."""

    def __init__(self) -> None:
        self._callbacks: dict[str, HotkeyCallback] = {}
        self._hotkey_refs: dict[str, int] = {}
        self._listening = False

    def register_hotkey(self, key_combo: str, callback: HotkeyCallback) -> None:
        """Register a hotkey callback and activate it immediately if needed."""
        self._callbacks[key_combo] = callback
        if self._listening:
            self._activate_hotkey(key_combo, callback)

    def unregister_hotkey(self, key_combo: str) -> None:
        """Unregister a configured hotkey."""
        hotkey_ref = self._hotkey_refs.pop(key_combo, None)
        if hotkey_ref is not None:
            keyboard.remove_hotkey(hotkey_ref)
        self._callbacks.pop(key_combo, None)

    def start_listener(self) -> None:
        """Activate all configured hotkeys."""
        if self._listening:
            return

        self._listening = True
        for key_combo, callback in self._callbacks.items():
            self._activate_hotkey(key_combo, callback)
        logger.info('Global hotkey listener started.')

    def stop_listener(self) -> None:
        """Deactivate all configured hotkeys."""
        if not self._listening:
            return

        for hotkey_ref in self._hotkey_refs.values():
            keyboard.remove_hotkey(hotkey_ref)
        self._hotkey_refs.clear()
        self._listening = False
        logger.info('Global hotkey listener stopped.')

    def _activate_hotkey(self, key_combo: str, callback: HotkeyCallback) -> None:
        """Register a hotkey with the keyboard backend."""
        try:
            hotkey_ref = keyboard.add_hotkey(key_combo, callback, suppress=False)
        except Exception as exc:
            logger.warning('Unable to register hotkey %s: %s', key_combo, exc)
            return

        previous_ref = self._hotkey_refs.get(key_combo)
        if previous_ref is not None and previous_ref != hotkey_ref:
            keyboard.remove_hotkey(previous_ref)
        self._hotkey_refs[key_combo] = hotkey_ref
