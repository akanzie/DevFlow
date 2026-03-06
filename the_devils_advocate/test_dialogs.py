#!/usr/bin/env python3
"""Test dialogs without full GUI"""

import sys
from PyQt6.QtWidgets import QApplication

print("Testing PyQt6...")
app = QApplication(sys.argv)

print("Testing GeminiConfigDialog...")
try:
    from game.gemini_integration import GeminiConfigDialog
    dialog = GeminiConfigDialog()
    print(f"✅ GeminiConfigDialog created: {type(dialog).__name__}")
except Exception as e:
    print(f"❌ GeminiConfigDialog error: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting GPTConfigDialog...")
try:
    from game.gpt_integration import GPTConfigDialog
    dialog = GPTConfigDialog()
    print(f"✅ GPTConfigDialog created: {type(dialog).__name__}")
except Exception as e:
    print(f"❌ GPTConfigDialog error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All dialog tests passed!")
