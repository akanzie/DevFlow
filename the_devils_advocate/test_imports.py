#!/usr/bin/env python3
"""Test all imports before launching GUI"""

import sys
try:
    print("Testing imports...")
    
    from game import Player, GameState, GeminiIntegration, GeminiConfigDialog
    print("  ✓ Game core modules")
    
    from gui_main import DebateWindow, AIProviderDialog, AIWorker
    print("  ✓ GUI modules")
    
    print("\n✅ All imports successful!")
    print("✅ Game is ready to run!\n")
    
except Exception as e:
    print(f"\n❌ Import Error: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
