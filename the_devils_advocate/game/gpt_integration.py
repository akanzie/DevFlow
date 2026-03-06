"""
OpenAI GPT Integration for The Devil's Advocate Game
Handles dynamic thesis generation, counter-arguments, and fallacy detection.
"""

import os
import json
from typing import Optional, Tuple, List, Dict
from pathlib import Path

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class GPTIntegration:
    """Handles OpenAI GPT integration for the game."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (or will try env var OPENAI_API_KEY)
        """
        self.client = None
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = "gpt-3.5-turbo"  # Cost-effective model
        self.scenario_cache: Dict[str, dict] = {}

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        """Check if OpenAI integration is available."""
        return OPENAI_AVAILABLE and self.client is not None

    def generate_scenario(self, category: Optional[str] = None, level: int = 1) -> Dict:
        """
        Generate absurd scenario with thesis.
        
        Args:
            category: Optional category (food, tech, philosophy, etc.)
            level: Difficulty level (1-10)
        
        Returns:
            Dict with keys: thesis, category, fallacy_count, description
        """
        if not self.is_available():
            return self._get_fallback_scenario(category, level)

        category = category or self._get_random_category()

        prompt = f"""Generate an absurd and debatable thesis for a debate game.
        
Category: {category}
Difficulty Level: {level}/10

Requirements:
- Thesis should be absurd but defensible with creative thinking
- 1-2 sentences max
- Return ONLY JSON format:
{{
    "thesis": "The absurd statement to defend",
    "category": "{category}",
    "why_absurd": "Brief reason why it's absurd",
    "hint": "Hint about how to defend it"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=200
            )
            text = response.choices[0].message.content.strip()
            data = json.loads(text)
            return {
                "thesis": data.get("thesis", "Pizza dứa là phát minh vĩ đại"),
                "category": data.get("category", category),
                "why_absurd": data.get("why_absurd", ""),
                "hint": data.get("hint", ""),
                "level": level
            }
        except Exception as e:
            print(f"GPT Error: {e}")
            return self._get_fallback_scenario(category, level)

    def generate_counter_arguments(self, thesis: str, count: int = 3) -> List[str]:
        """
        Generate counter-arguments with fallacies injected.
        
        Args:
            thesis: The thesis to generate counters for
            count: Number of counter-arguments to generate
        
        Returns:
            List of counter-argument strings
        """
        if not self.is_available():
            return self._get_fallback_counters(thesis, count)

        fallacies = ["ad_hominem", "strawman", "appeal_emotion", "false_dichotomy", "slippery_slope"]

        prompt = f"""Generate counter-arguments against this thesis with logical fallacies:

Thesis: "{thesis}"

Generate {count} strong counter-arguments that:
1. Use logical fallacies (ad hominem, strawman, false reasoning, etc.)
2. Sound convincing but are actually flawed
3. Vary in approach and tone

Return ONLY a JSON array of strings (the counter-arguments):
["counter 1", "counter 2", "counter 3", ...]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=500
            )
            text = response.choices[0].message.content.strip()
            counters = json.loads(text)
            return counters[:count]
        except Exception as e:
            print(f"GPT Error: {e}")
            return self._get_fallback_counters(thesis, count)

    def detect_fallacies_in_text(self, text: str, reference_text: str = "") -> Dict:
        """
        Use GPT to detect fallacies in player's rebuttal.
        
        Args:
            text: Player's rebuttal
            reference_text: Reference text to check against
        
        Returns:
            Dict with keys: fallacies, score, reasoning
        """
        if not self.is_available():
            return {"fallacies": [], "score": 50, "reasoning": "Cannot analyze without GPT"}

        prompt = f"""Analyze this debate rebuttal for logical quality and fallacies:

Rebuttal: "{text}"

Evaluate:
1. What logical fallacies (if any) does it contain?
2. Logic quality score (0-100)
3. Strength of arguments (1-5 stars)

Return JSON:
{{
    "fallacies": ["list of fallacies detected"],
    "logic_score": 0-100,
    "strength": 1-5,
    "reasoning": "Brief analysis"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            text = response.choices[0].message.content.strip()
            return json.loads(text)
        except Exception as e:
            return {"fallacies": [], "score": 50, "reasoning": str(e)}

    def evaluate_rebuttal(self, rebuttal: str, thesis: str, counter: str) -> Dict:
        """
        Comprehensive evaluation of player's rebuttal.
        
        Args:
            rebuttal: Player's argument
            thesis: The thesis being defended
            counter: The counter-argument being respond to
        
        Returns:
            Dict with scoring breakdown
        """
        if not self.is_available():
            return {"total": 50, "logic": 25, "persuasion": 20, "creativity": 5}

        prompt = f"""Evaluate this debate rebuttal response:

Thesis to defend: "{thesis}"
AI counter-argument: "{counter}"
Player's rebuttal: "{rebuttal}"

Score each aspect (0-100):
1. Logic: How logically sound is the rebuttal?
2. Persuasion: How convincing is it?
3. Creativity: How novel/original?
4. Relevance: Does it address the counter?

Return JSON:
{{
    "logic": 0-100,
    "persuasion": 0-100,
    "creativity": 0-100,
    "relevance": 0-100,
    "total": 0-100,
    "feedback": "Brief feedback"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            text = response.choices[0].message.content.strip()
            data = json.loads(text)
            return {
                "logic": data.get("logic", 50),
                "persuasion": data.get("persuasion", 50),
                "creativity": data.get("creativity", 50),
                "relevance": data.get("relevance", 50),
                "total": data.get("total", 50),
                "feedback": data.get("feedback", "")
            }
        except Exception as e:
            return {
                "logic": 50, "persuasion": 50, "creativity": 50,
                "relevance": 50, "total": 50, "feedback": str(e)
            }

    def _get_random_category(self) -> str:
        """Get a random debate category."""
        categories = [
            "Food & Cuisine", "Technology", "Philosophy", "Pop Culture",
            "Sports", "Education", "Work & Career", "Travel & Culture",
            "Entertainment", "Social Media", "Gaming", "Environmental"
        ]
        import random
        return random.choice(categories)

    def _get_fallback_scenario(self, category: Optional[str] = None, level: int = 1) -> Dict:
        """Return fallback scenario when GPT unavailable."""
        fallback_theses = [
            "Pizza with pineapple is the greatest culinary invention ever",
            "Sleeping late is the secret to success",
            "Video games improve critical thinking better than books",
            "Social media should be required for everyone",
            "Working 4 days a week increases productivity",
            "Fast food is healthier than home cooking if you choose right",
            "AI will make programmers obsolete by 2030",
            "Cats are superior to dogs in every way",
            "Procrastination is actually a sign of genius",
            "Climate change is not as urgent as we think"
        ]
        import random
        return {
            "thesis": random.choice(fallback_theses),
            "category": category or "General",
            "why_absurd": "Debatable and absurd",
            "hint": "Think creatively!",
            "level": level
        }

    def _get_fallback_counters(self, thesis: str, count: int = 3) -> List[str]:
        """Return fallback counter-arguments when GPT unavailable."""
        fallback_counters = [
            "You only believe that because you're not educated enough to understand the real issues!",
            "So you're saying we should completely ignore all scientific evidence?",
            "Everyone I know disagrees with you, so obviously you're wrong!",
            "That's just what big corporations want you to think!",
            "Either you agree with me or you're clearly against progress!",
            "If we let this happen, the entire society will collapse!",
            "This is common sense, and only fools disagree!",
            "Experts have already proven you wrong on this!",
            "You're just saying this to distract from the real problem!",
            "People who think like you are the problem with the world!"
        ]
        import random
        return random.sample(fallback_counters, min(count, len(fallback_counters)))


class GPTConfigDialog(QDialog):
    """Dialog for configuring OpenAI GPT API key."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_key = None
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("🔑 Configure OpenAI GPT API")
        self.setGeometry(100, 100, 500, 300)
        layout = QVBoxLayout()

        # Info label
        info = QLabel(
            "OpenAI GPT-3.5 Turbo Configuration\n\n"
            "Get your API key:\n"
            "1. Visit: https://platform.openai.com/api-keys\n"
            "2. Create a new API key\n"
            "3. Paste it below\n\n"
            "⚠️  Note: This service requires payment (usually ~$0.0005 per request)"
        )
        info.setStyleSheet("color: #e74c3c; font-size: 11px;")
        layout.addWidget(info)

        # Key input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Paste your OpenAI API key here...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.key_input)

        # Buttons
        button_layout = QVBoxLayout()

        use_btn = QPushButton("✓ Use OpenAI GPT")
        use_btn.setStyleSheet("background-color: #10a37f; color: white; font-weight: bold;")
        use_btn.clicked.connect(self.accept)
        button_layout.addWidget(use_btn)

        skip_btn = QPushButton("⊗ Use Fallback (Offline)")
        skip_btn.setStyleSheet("background-color: #95a5a6; color: white;")
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_api_key(self) -> Optional[str]:
        """Get the entered API key."""
        return self.key_input.text().strip() or None
