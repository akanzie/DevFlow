"""Tests for the global hotkey service."""

from __future__ import annotations

from unittest.mock import patch

import pytest

pytest.importorskip('keyboard')

from DailyClip.infrastructure.hotkey import GlobalHotkeyService


def test_start_listener_registers_hotkeys_once():
    """Starting the listener should register configured hotkeys."""
    with patch('DailyClip.infrastructure.hotkey.keyboard.add_hotkey', return_value=1) as add_hotkey:
        service = GlobalHotkeyService()
        service.register_hotkey('alt+space', lambda: None)
        service.start_listener()

    add_hotkey.assert_called_once()
