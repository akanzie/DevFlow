"""
Core game logic for The Devil's Advocate.
Manages round state and game state machine.
"""

from typing import List, Dict, Optional
from .player import Player
from .prosecutor import ProsecutorAI
from .scorer import Scorer
from .utils import ConsoleUI, InputParser, Colors


class Round:
    """Represents a single debate round."""

    def __init__(self, thesis: str, ai_counter: str, hidden_fallacies: List[str]):
        self.thesis: str = thesis
        self.ai_counter: str = ai_counter
        self.hidden_fallacies: List[str] = hidden_fallacies
        self.turns_taken: int = 0
        self.max_turns: int = 5
        self.player_rebuttals: List[str] = []
        self.scores: List[Dict] = []

    def add_turn(self, rebuttal: str, score_dict: Dict) -> None:
        """Record a turn in this round."""
        self.turns_taken += 1
        self.player_rebuttals.append(rebuttal)
        self.scores.append(score_dict)

    def is_complete(self) -> bool:
        """Check if round reached max turns."""
        return self.turns_taken >= self.max_turns

    def get_total_score(self) -> int:
        """Get total score for this round."""
        return sum(s.get("total", 0) for s in self.scores)


class GameState:
    """Manages overall game state and flow."""

    # Win/Lose conditions
    SCORE_TO_WIN = 1000
    CONSECUTIVE_LOSSES_TO_LOSE = 3

    def __init__(self, player: Player):
        self.player: Player = player
        self.ai: ProsecutorAI = ProsecutorAI()
        self.scorer: Scorer = Scorer()
        self.current_round: Optional[Round] = None
        self.consecutive_losses: int = 0
        self.game_over: bool = False
        self.win: bool = False

    def start_new_round(self) -> None:
        """Initialize a new round."""
        thesis = self.ai.generate_thesis(self.player.level)
        counter, fallacies = self.ai.generate_counter(
            thesis,
            self.player.level,
            self.player.streak
        )
        self.current_round = Round(thesis, counter, fallacies)

    def process_rebuttal(self, rebuttal: str, command: Optional[str] = None, arg: str = "") -> Dict:
        """
        Process player rebuttal and calculate score.

        Returns dict with keys: success, score_dict, feedback, detected_fallacy
        """
        if not self.current_round:
            return {"success": False, "message": "No active round"}

        detected_fallacy = None

        # Parse command if present
        if command == "fallacy":
            detected_fallacy = InputParser.detect_fallacy(arg)
        elif command == "evidence":
            # Evidence is added to rebuttal for scoring
            rebuttal = rebuttal + " " + arg
        else:
            # Free-form rebuttal (or if no command)
            detected_fallacy = InputParser.detect_fallacy(rebuttal)

        # Calculate score
        score_dict = self.scorer.calculate_score(
            rebuttal,
            self.current_round.hidden_fallacies,
            detected_fallacy
        )

        # Track fallacy detection
        if detected_fallacy and detected_fallacy in self.current_round.hidden_fallacies:
            self.player.add_detected_fallacy()

        # Add points to player
        self.player.add_score(score_dict["total"])
        self.current_round.add_turn(rebuttal, score_dict)

        # Check if round won (score >= 80 in this turn)
        round_won = score_dict["total"] >= 80

        return {
            "success": True,
            "score_dict": score_dict,
            "feedback": Scorer.get_feedback_string(score_dict),
            "detected_fallacy": detected_fallacy,
            "round_won": round_won
        }

    def end_round(self, won: bool) -> None:
        """End current round with win/loss result."""
        if won:
            self.consecutive_losses = 0
            self.player.add_round(won=True)
        else:
            self.consecutive_losses += 1
            self.player.add_round(won=False)

        # Check lose condition
        if self.consecutive_losses >= self.CONSECUTIVE_LOSSES_TO_LOSE:
            self.game_over = True
            self.win = False
            return

        # Check win condition
        if self.player.score >= self.SCORE_TO_WIN:
            self.game_over = True
            self.win = True
            return

        # Level up every 2 consecutive wins
        if self.player.streak >= 2:
            self.player.level_up()

    def surrender_round(self) -> None:
        """Player surrenders current round."""
        self.player.lose_life()
        self.consecutive_losses += 1
        self.player.add_round(won=False)

        if self.consecutive_losses >= self.CONSECUTIVE_LOSSES_TO_LOSE:
            self.game_over = True
            self.win = False

    def use_hint(self) -> str:
        """Player uses hint (costs 10 points)."""
        if self.player.score >= 10:
            self.player.add_score(-10)
        hint = self.ai.get_hint(self.current_round.hidden_fallacies)
        return hint

    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self.game_over or self.player.lives <= 0

    def get_status_string(self) -> str:
        """Get current game status as formatted string."""
        status = f"""
╔════════════════════════════════════════╗
║           TRẠNG THÁI TRÂN ĐẤU          ║
╚════════════════════════════════════════╝
📊 Điểm: {self.player.score}/{self.SCORE_TO_WIN}
🎯 Cấp độ: {self.player.level}
❤️  Mạng sống: {self.player.lives}
🔥 Streak: {self.player.streak}
🐛 Ngụy biện phát hiện: {self.player.detected_fallacies}
❌ Thua liên tiếp: {self.consecutive_losses}/{self.CONSECUTIVE_LOSSES_TO_LOSE}
        """
        return status.strip()

    def get_end_screen(self) -> str:
        """Get game end screen."""
        if self.win:
            screen = f"""
╔════════════════════════════════════════╗
║      🎉 BẠN VỊ THẮNG CUỘC! 🎉         ║
╚════════════════════════════════════════╝

Chúc mừng! Bạn đã trở thành Luật sư vĩ đại của Quỷ!

📊 KẾT QUẢ CUỐI CÙNG:
  Tổng điểm: {self.player.score}
  Cấp độ: {self.player.level}
  Ngụy biện phát hiện: {self.player.detected_fallacies}
  Rounds thắng: {self.player.rounds_won}/{self.player.rounds_played}
  Win rate: {(self.player.rounds_won / max(1, self.player.rounds_played) * 100):.1f}%

🏅 ACHIEVEMENTS:
  {', '.join(self.player.achievements) if self.player.achievements else 'Không có'}
            """
        else:
            screen = f"""
╔════════════════════════════════════════╗
║    💀 BƠI CẬT! BẠN ĐÃ TỮA CUỘC 💀    ║
╚════════════════════════════════════════╝

Bạn đã thua 3 rounds liên tiếp. Luật sư của Quỷ cần bạn
phải bào chữa tốt hơn lần sau!

📊 KẾT QUẢ CUỐI CÙNG:
  Tổng điểm: {self.player.score}
  Cấp độ: {self.player.level}
  Ngụy biện phát hiện: {self.player.detected_fallacies}
  Rounds thắng: {self.player.rounds_won}/{self.player.rounds_played}
  Win rate: {(self.player.rounds_won / max(1, self.player.rounds_played) * 100):.1f}%

🏅 ACHIEVEMENTS:
  {', '.join(self.player.achievements) if self.player.achievements else 'Không có'}
            """

        return screen.strip()
