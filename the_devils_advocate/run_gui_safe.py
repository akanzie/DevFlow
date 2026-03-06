#!/usr/bin/env python3
"""Test GUI startup without AI dialogs"""

import sys
from PyQt6.QtWidgets import QApplication
from gui_main import DebateWindow

print("Starting GUI application...")
print("AI setup dialog will only show if you click '🤖 Cấu Hình AI' button")
print("(It's safe to use Fallback Mode by default)")

app = QApplication(sys.argv)
window = DebateWindow()
print("✅ Window created successfully!")
print("Click buttons to navigate:")
print("  - 🎮 Chơi Mới: Start new game")
print("  - 🤖 Cấu Hình AI: Configure AI provider")
print("  - ❌ Thoát: Exit")

sys.exit(app.exec())
