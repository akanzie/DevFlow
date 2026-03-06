#!/usr/bin/env python3
"""
The Devil's Advocate - GUI Version Launcher
Modern PyQt6 desktop application with GPT integration.

Run with: python gui.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gui_main import main

if __name__ == "__main__":
    main()
