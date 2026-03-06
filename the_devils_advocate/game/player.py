"""
Player class for The Devil's Advocate game.
Tracks player stats, progress, and achievements.
"""

import json
from pathlib import Path
from typing import Optional, Dict


class Player:
    """Represents the player in the game."""

    def __init__(self, name: str = "Player"):
        self.name: str = name
        self.score: int = 0
        self.streak: int = 0  # consecutive wins
        self.detected_fallacies: int = 0
        self.level: int = 1
        self.lives: int = 3  # lose 3 rounds in a row → game over
        self.rounds_played: int = 0
        self.rounds_won: int = 0
        self.achievements: set = set()
        self.last_round_score: int = 0

    def add_score(self, points: int) -> None:
        """Add points to player score."""
        self.score += max(0, points)

    def add_detected_fallacy(self) -> None:
        """Increment detected fallacies count."""
        self.detected_fallacies += 1

    def reset_streak(self) -> None:
        """Reset win streak."""
        self.streak = 0

    def increment_streak(self) -> None:
        """Increment win streak."""
        self.streak += 1
        self._check_achievements()

    def lose_life(self) -> bool:
        """
        Lose one life.
        Returns True if still alive, False if game over (0 lives).
        """
        self.lives = max(0, self.lives - 1)
        self.reset_streak()
        return self.lives > 0

    def level_up(self) -> None:
        """Increase level."""
        self.level += 1

    def add_round(self, won: bool = False) -> None:
        """Increment round counter."""
        self.rounds_played += 1
        if won:
            self.rounds_won += 1
            self.increment_streak()
        else:
            self.reset_streak()

    def _check_achievements(self) -> None:
        """Check and unlock achievements."""
        if self.score >= 1000 and "master_advocate" not in self.achievements:
            self.achievements.add("master_advocate")

        if self.detected_fallacies >= 50 and "fallacy_slayer" not in self.achievements:
            self.achievements.add("fallacy_slayer")

        if self.detected_fallacies >= 100 and "fallacy_master" not in self.achievements:
            self.achievements.add("fallacy_master")

        if self.streak >= 5 and "on_fire" not in self.achievements:
            self.achievements.add("on_fire")

        if self.level >= 10 and "level_10" not in self.achievements:
            self.achievements.add("level_10")

    def get_stats_string(self) -> str:
        """Return formatted player stats."""
        stats = f"""
╔═══════════════════════════════════════╗
║          THỐNG KÊ NGƯỜI CHƠI          ║
╚═══════════════════════════════════════╝
📊 Tên: {self.name}
💰 Điểm: {self.score}
🎯 Cấp độ: {self.level}
❤️  Mạng sống: {self.lives}
🔥 Streak (liên tiếp thắng): {self.streak}
🎪 Rounds chơi: {self.rounds_played}
🏆 Rounds thắng: {self.rounds_won}
🐛 Ngụy biện phát hiện: {self.detected_fallacies}
🏅 Achievements: {', '.join(self.achievements) if self.achievements else 'Chưa có'}
        """
        return stats.strip()

    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving."""
        return {
            "name": self.name,
            "score": self.score,
            "streak": self.streak,
            "detected_fallacies": self.detected_fallacies,
            "level": self.level,
            "lives": self.lives,
            "rounds_played": self.rounds_played,
            "rounds_won": self.rounds_won,
            "achievements": list(self.achievements),
        }

    @staticmethod
    def from_dict(data: Dict) -> "Player":
        """Create player from dictionary (loading from save)."""
        player = Player(data.get("name", "Player"))
        player.score = data.get("score", 0)
        player.streak = data.get("streak", 0)
        player.detected_fallacies = data.get("detected_fallacies", 0)
        player.level = data.get("level", 1)
        player.lives = data.get("lives", 3)
        player.rounds_played = data.get("rounds_played", 0)
        player.rounds_won = data.get("rounds_won", 0)
        player.achievements = set(data.get("achievements", []))
        return player

    def save(self, filepath: Optional[Path] = None) -> None:
        """Save player state to JSON file."""
        if filepath is None:
            filepath = Path(__file__).parent.parent / "save" / "player_save.json"

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(filepath: Optional[Path] = None) -> Optional["Player"]:
        """Load player state from JSON file."""
        if filepath is None:
            filepath = Path(__file__).parent.parent / "save" / "player_save.json"

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Player.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None
