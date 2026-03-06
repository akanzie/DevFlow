"""
The Devil's Advocate - Game Package
A console-based debate simulator to train critical thinking and persuasion skills.
Version 2.1: Now with GUI + AI Integration (OpenAI GPT & Google Gemini)!
"""

__version__ = "2.1.0"
__author__ = "Grok (based on Kiệt's concept)"

from .player import Player
from .core import Round, GameState
from .prosecutor import ProsecutorAI
from .scorer import Scorer
from .utils import ConsoleUI, InputParser, print_welcome_screen, print_help
from .gpt_integration import GPTIntegration, GPTConfigDialog
from .gemini_integration import GeminiIntegration, GeminiConfigDialog

__all__ = [
    "Player", "Round", "GameState", "ProsecutorAI", "Scorer",
    "ConsoleUI", "InputParser", "print_welcome_screen", "print_help",
    "GPTIntegration", "GPTConfigDialog",
    "GeminiIntegration", "GeminiConfigDialog"
]
