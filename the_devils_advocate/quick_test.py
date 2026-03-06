#!/usr/bin/env python3
"""Quick test to verify the fixes"""

import sys
print("Testing imports...")

try:
    print("✓ Importing PyQt6...")
    from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel
    
    print("✓ Importing Game modules...")
    from game.player import Player
    from game.core import GameState
    from game.gemini_integration import GeminiIntegration, GeminiConfigDialog
    from game.gpt_integration import GPTIntegration, GPTConfigDialog
    
    print("✓ Importing GUI modules...")
    from gui_main import DebateWindow, AIProviderDialog, AIWorker
    
    print("\n✅ All imports successful!")
    print("\nTesting GeminiConfigDialog instantiation...")
    app = QApplication(sys.argv)
    dialog = GeminiConfigDialog()
    print(f"✅ GeminiConfigDialog: {dialog.__class__.__name__}")
    
    print("Testing GPTConfigDialog instantiation...")
    dialog2 = GPTConfigDialog()
    print(f"✅ GPTConfigDialog: {dialog2.__class__.__name__}")
    
    print("\n✅ All tests passed! GUI should work now.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
