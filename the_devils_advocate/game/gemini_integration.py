"""
Google Gemini AI Integration for The Devil's Advocate Game
Free tier support - no credit card required!

Uses the NEW google.genai package (google-generativeai is deprecated).

Provides scenario generation, counter-argument creation, and rebuttal evaluation
using Google's Gemini API (free tier available).
"""

import os
import json
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    import google.genai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt


class GeminiIntegration:
    """
    Wrapper for Google Gemini API with fallback support.
    
    Supports both free tier and paid tiers using the new google.genai package.
    Fallback to pre-configured scenarios when API unavailable.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini integration.
        
        Args:
            api_key: Google Gemini API key (or reads from GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.available = False
        self.client = None
        self.error_message = None
        
        if not GEMINI_AVAILABLE:
            print("⚠️  google.genai not installed. Install with: pip install google-genai")
            return
        
        if self.api_key:
            try:
                # Initialize new google.genai client
                self.client = genai.Client(api_key=self.api_key)
                
                # Test connection with a simple generate_content call
                response = self.client.models.generate_content(
                    model="gemini-1.5-flash",  # Higher free tier quota
                    contents="Xin chào"  # Simple Vietnamese hello
                )
                self.available = True
                print("✓ Gemini API connected successfully (FREE TIER - google.genai)")
            except Exception as e:
                self.error_message = str(e)
                print(f"⚠ Gemini connection failed: {e}")
                self.available = False

    def is_available(self) -> bool:
        """Check if Gemini API is available."""
        return self.available

    def generate_scenario(self, category: str = "General", level: int = 1) -> Dict:
        """
        Generate an absurd debate thesis using Gemini.
        
        Args:
            category: Debate category (General, Politics, Technology, etc.)
            level: Difficulty level (1-5)
        
        Returns:
            Dict with thesis, category, hint, and level
        """
        if not self.available:
            return self._get_fallback_scenario(category, level)

        try:
            difficulty = ["simple", "medium", "complex", "absurd", "extreme"][level - 1]
            
            prompt = f"""Generate ONE absurd but debatable thesis for a debate game in {difficulty} difficulty.
Category: {category}

Requirements:
- Must be debatable (not obviously false)
- Should be funny/absurd but intellectually interesting
- One sentence only
- In Vietnamese or English (mix is OK)

Return ONLY the thesis text, nothing else."""
            
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",  # Higher free tier quota
                contents=prompt
            )
            thesis = response.text.strip()
            
            return {
                "thesis": thesis,
                "category": category,
                "hint": f"Think critically about the {category.lower()} aspect",
                "level": level
            }
        except Exception as e:
            print(f"Gemini scenario error: {e}")
            return self._get_fallback_scenario(category, level)

    def generate_counter_arguments(self, thesis: str, count: int = 3) -> List[Dict]:
        """
        Generate counter-arguments with detected fallacies using Gemini.
        
        Args:
            thesis: The debate thesis
            count: Number of arguments to generate
        
        Returns:
            List of dicts with 'argument' and 'fallacy' keys
        """
        if not self.available:
            return self._get_fallback_counter_arguments(thesis, count)

        try:
            prompt = f"""As a debate opponent, generate {count} counter-arguments against this thesis:
"{thesis}"

For EACH argument:
1. Write a convincing counter-argument (2-3 sentences)
2. Identify ONE logical fallacy used (e.g., ad hominem, straw man, false dilemma, etc.)

Format:
ARGUMENT 1: [text]
FALLACY 1: [type]
ARGUMENT 2: [text]
FALLACY 2: [type]
..."""
            
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",  # Higher free tier quota
                contents=prompt
            )
            text = response.text.strip()
            
            arguments = []
            lines = text.split('\n')
            
            current_arg = None
            for line in lines:
                line = line.strip()
                if line.startswith('ARGUMENT'):
                    if current_arg and 'fallacy' in current_arg:
                        arguments.append(current_arg)
                    current_arg = {"argument": line.split(':', 1)[1].strip() if ':' in line else ""}
                elif line.startswith('FALLACY') and current_arg:
                    current_arg["fallacy"] = line.split(':', 1)[1].strip() if ':' in line else "Logical Fallacy"
            
            if current_arg and 'fallacy' in current_arg:
                arguments.append(current_arg)
            
            if len(arguments) < count:
                arguments.extend(self._get_fallback_counter_arguments(thesis, count - len(arguments)))
            
            return arguments[:count]
        except Exception as e:
            print(f"Gemini counter-arguments error: {e}")
            return self._get_fallback_counter_arguments(thesis, count)

    def evaluate_rebuttal(self, rebuttal: str, thesis: str, counter_arg: str) -> Dict:
        """
        Evaluate user's rebuttal using Gemini.
        
        Args:
            rebuttal: User's counter-argument
            thesis: Original debate thesis
            counter_arg: Prosecutor's counter-argument
        
        Returns:
            Dict with scores and feedback
        """
        if not self.available:
            return self._get_fallback_evaluation(rebuttal, thesis, counter_arg)

        try:
            prompt = f"""Evaluate this debate rebuttal on a scale of 0-10 for each criterion.

THESIS: "{thesis}"
OPPONENT'S ARGUMENT: "{counter_arg}"
USER'S REBUTTAL: "{rebuttal}"

Score each:
1. Logic (0-10): Does the argument follow sound reasoning?
2. Persuasion (0-10): How convincing is it?
3. Creativity (0-10): Is it original and clever?
4. Relevance (0-10): Does it address the opponent's point?

Format:
LOGIC: [0-10]
PERSUASION: [0-10]
CREATIVITY: [0-10]
RELEVANCE: [0-10]
FEEDBACK: [2-3 sentences of constructive feedback]"""
            
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",  # Higher free tier quota
                contents=prompt
            )
            text = response.text.strip()
            
            scores = {}
            feedback = ""
            
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('LOGIC:'):
                    try:
                        scores['logic'] = int(line.split(':')[1].strip().split()[0])
                    except:
                        scores['logic'] = 5
                elif line.startswith('PERSUASION:'):
                    try:
                        scores['persuasion'] = int(line.split(':')[1].strip().split()[0])
                    except:
                        scores['persuasion'] = 5
                elif line.startswith('CREATIVITY:'):
                    try:
                        scores['creativity'] = int(line.split(':')[1].strip().split()[0])
                    except:
                        scores['creativity'] = 5
                elif line.startswith('RELEVANCE:'):
                    try:
                        scores['relevance'] = int(line.split(':')[1].strip().split()[0])
                    except:
                        scores['relevance'] = 5
                elif line.startswith('FEEDBACK:'):
                    feedback = line.split(':', 1)[1].strip()
            
            # Normalize scores to 0-50, 0-30, 0-20, 0-20 ranges
            return {
                "logic": min(50, max(0, (scores.get('logic', 5) * 5))),
                "persuasion": min(30, max(0, (scores.get('persuasion', 5) * 3))),
                "creativity": min(20, max(0, (scores.get('creativity', 5) * 2))),
                "relevance": min(20, max(0, (scores.get('relevance', 5) * 2))),
                "feedback": feedback or "Good attempt at defending your position!",
                "total": 0  # Will be calculated by game engine
            }
        except Exception as e:
            print(f"Gemini evaluation error: {e}")
            return self._get_fallback_evaluation(rebuttal, thesis, counter_arg)

    # ==================== FALLBACK METHODS ====================

    def _get_fallback_scenario(self, category: str = "General", level: int = 1) -> Dict:
        """Get fallback scenario from local data."""
        fallback_theses = [
            "Pizza with pineapple is the greatest invention",
            "Sleeping late is the secret to success",
            "Cats are superior to dogs in every way",
            "Everyone should work only 3 hours per day",
            "Video games are better than books",
            "Social media has improved human relationships",
            "Mobile phones should be banned in schools",
            "AI will completely replace human jobs by 2030",
            "Learning to code is more important than learning history",
            "The internet has made us smarter, not dumber",
            "Remote work is better than office work",
            "Comic books are serious literature",
            "Breakfast is unnecessary",
            "Emojis are ruining written communication",
            "Everyone should be a vegetarian",
        ]
        
        return {
            "thesis": random.choice(fallback_theses),
            "category": category,
            "hint": f"Think about the {category.lower()} implications",
            "level": level
        }

    def _get_fallback_counter_arguments(self, thesis: str, count: int = 3) -> List[Dict]:
        """Get fallback counter-arguments."""
        fallacies = [
            ("This is just a generalization", "Hasty Generalization"),
            ("Everyone believes differently", "Appeal to Common Belief"),
            ("That's a slippery slope argument", "Slippery Slope"),
            ("You're just being emotional about this", "Ad Hominem"),
            ("This contradicts historical facts", "False Comparison"),
        ]
        
        arguments = []
        for i in range(count):
            arg, fallacy = random.choice(fallacies)
            arguments.append({
                "argument": arg,
                "fallacy": fallacy
            })
        
        return arguments

    def _get_fallback_evaluation(self, rebuttal: str, thesis: str, counter_arg: str) -> Dict:
        """Get fallback evaluation score."""
        logic_score = random.randint(20, 40)
        persuasion_score = random.randint(10, 25)
        creativity_score = random.randint(5, 15)
        relevance_score = random.randint(5, 15)
        
        return {
            "logic": logic_score,
            "persuasion": persuasion_score,
            "creativity": creativity_score,
            "relevance": relevance_score,
            "feedback": "Keep practicing your debate skills!",
            "total": 0
        }


class GeminiConfigDialog(QDialog):
    """Dialog for configuring Gemini API key."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_key = None
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("🔑 Configure Google Gemini API")
        self.setGeometry(100, 100, 500, 300)
        layout = QVBoxLayout()

        # Info label
        info = QLabel(
            "Google Gemini Free Tier (No credit card required!)\n\n"
            "Get your FREE API key:\n"
            "1. Visit: https://aistudio.google.com/api-keys (NEW!)\n"
            "2. Click 'Create API Key'\n"
            "3. Paste it below"
        )
        info.setStyleSheet("color: #2ecc71; font-size: 11px;")
        layout.addWidget(info)

        # Key input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Paste your Gemini API key here...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.key_input)

        # Buttons
        button_layout = QVBoxLayout()

        use_btn = QPushButton("✓ Use Gemini Free")
        use_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        use_btn.clicked.connect(self.accept)
        button_layout.addWidget(use_btn)

        skip_btn = QPushButton("⊗ Use Fallback (Offline)")
        skip_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_api_key(self) -> Optional[str]:
        """Get the entered API key."""
        return self.key_input.text().strip() or None
