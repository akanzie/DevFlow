"""
AI Prosecutor for The Devil's Advocate game.
Generates absurd theses and counter-arguments with fallacies.
"""

import random
import json
from pathlib import Path
from typing import Tuple, List, Optional


class ProsecutorAI:
    """AI opponent that generates debates with fallacies."""

    def __init__(self):
        self.thesis_bank: List[str] = []
        self.fallacy_templates: dict = {}
        self.state: str = "neutral"  # neutral, aggressive, desperate
        self.rounds_played: int = 0
        self._load_data()

    def _load_data(self) -> None:
        """Load thesis and fallacy data from JSON files."""
        data_dir = Path(__file__).parent.parent / "data"

        # Load thesis bank
        thesis_file = data_dir / "thesis_bank.json"
        if thesis_file.exists():
            try:
                with open(thesis_file, "r", encoding="utf-8") as f:
                    self.thesis_bank = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Could not load thesis_bank.json")
                self.thesis_bank = []

        # Load fallacy templates
        fallacy_file = data_dir / "fallacies.json"
        if fallacy_file.exists():
            try:
                with open(fallacy_file, "r", encoding="utf-8") as f:
                    self.fallacy_templates = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Could not load fallacies.json")
                self.fallacy_templates = {}

        # Fallback defaults if files don't exist
        if not self.thesis_bank:
            self.thesis_bank = self._get_default_theses()

        if not self.fallacy_templates:
            self.fallacy_templates = self._get_default_fallacies()

    def _get_default_theses(self) -> List[str]:
        """Return default thesis list."""
        return [
            "Ăn pizza kèm dứa là phát minh vĩ đại nhất nhân loại",
            "Ngủ muộn là bí quyết để thành công trong cuộc sống",
            "Trái đất phẳng và chúng ta đang bị lừa",
            "Cà phê nóng tốt hơn trà lạnh",
            "Phim Marvel tốt hơn phim DC",
            "Lập trình Python tốt hơn JavaScript",
            "Game console tốt hơn PC gaming",
            "Anime Nhật hay hơn anime Trung Quốc",
            "Meme là một hình thức nghệ thuật cao cấp",
            "Lập trình tương lai là AI, không phải Web3",
        ]

    def _get_default_fallacies(self) -> dict:
        """Return default fallacy templates."""
        return {
            "ad_hominem": [
                "Bạn chỉ ủng hộ điều đó vì bạn không hiểu gì!",
                "Bạn nói vậy vì bạn chưa bao giờ thử!",
                "Người như bạn không thể hiểu được vấn đề này!",
                "Rõ ràng bạn bị thiên vị!"
            ],
            "strawman": [
                "Vậy ý bạn là bạn hoàn toàn ghét điều đối lập?",
                "Bạn đang nói rằng sẽ bỏ qua tất cả những điều khác?",
                "Điều đó có nghĩa là bạn không quan tâm đến sức khỏe?",
                "Vậy bạn cho rằng chúng ta nên bỏ qua mọi thứ?"
            ],
            "appeal_emotion": [
                "Điều này làm tôi cảm thấy buồn vì những ký ức tuổi thơ!",
                "Tất cả mọi người tôi yêu sẽ đau lòng nếu nghe bạn nói!",
                "Đây là nỗi đau của thế hệ chúng ta!",
                "Cảm xúc của chúng ta quan trọng hơn sự thật!"
            ],
            "false_dichotomy": [
                "Hoặc bạn sống theo cách này, hoặc bạn không tôn trọng bản thân!",
                "Hoặc bạn đồng ý với tôi, hoặc bạn là kẻ thù!",
                "Không có cách nào giữa đen và trắng!",
                "Bạn phải chọn: cái này hoặc cái kia!"
            ],
            "slippery_slope": [
                "Nếu chúng ta cho phép điều này, ngày mai sẽ là tình huống tồi tệ!",
                "Đây là con đường dốc trơn tới tận cùng!",
                "Một bước nhỏ hôm nay sẽ dẫn đến thảm họa ngày mai!",
                "Nếu bạn cho phép điều này, không gì có thể dừng lại!"
            ],
            "begging_question": [
                "Rõ ràng là đúng như tôi nói!",
                "Ai có thể phủ nhận được sự hiển nhiên này?",
                "Mọi người đều biết điều tôi nói là đúng!",
                "Đó là hiển nhiên không cần chứng minh!"
            ],
            "appeal_authority": [
                "Chuyên gia nổi tiếng đã nói vậy nên nó phải đúng!",
                "Nhà vô địch thế giới tin tưởng như vậy!",
                "Người giàu nhất thế giới sẽ đồng ý với tôi!",
                "Tất cả những người thông minh đều nghĩ điều này!"
            ],
            "red_herring": [
                "Nhưng bạn có biết rằng vấn đề thực sự là cái khác?",
                "Tất cả những điều bạn nói không liên quan đến vấn đề chính!",
                "Bạn đang cố che giấu sự thật rằng...",
                "Chúng ta nên tập trung vào vấn đề khác quan trọng hơn!"
            ],
            "hasty_generalization": [
                "Tôi gặp một người như vậy nên tất cả họ đều giống!",
                "Cái gì xảy ra lần này sẽ lặp lại mãi mãi!",
                "Một trường hợp chứng minh mọi trường hợp!",
                "Tôi thấy hai lần giống nhau nên luôn luôn giống!"
            ],
            "false_cause": [
                "Vì A xảy ra trước B nên A gây ra B!",
                "Hai sự việc này cùng xảy ra nên chúng liên quan!",
                "Người hút thuốc sống lâu hơn nên thuốc tốt!",
                "Trời mưa rồi tôi bị ốm nên mưa gây ốm!"
            ]
        }

    def _update_state(self, level: int, streak: int) -> None:
        """Update AI state based on game progression."""
        if level >= 8 or streak >= 5:
            self.state = "desperate"
        elif level >= 5:
            self.state = "aggressive"
        else:
            self.state = "neutral"

    def generate_thesis(self, level: int = 1) -> str:
        """Generate a thesis for the player to defend."""
        if not self.thesis_bank:
            return "Pizza dứa là phát minh vĩ đại nhất"

        return random.choice(self.thesis_bank)

    def generate_counter(self, thesis: str, level: int = 1, streak: int = 0) -> Tuple[str, List[str]]:
        """
        Generate AI counter-argument with fallacies.

        Returns:
            Tuple of (counter_text, list of fallacy types used)
        """
        self._update_state(level, streak)

        # Determine number of fallacies to inject
        if self.state == "desperate":
            num_fallacies = min(3, level // 3 + 2)
        elif self.state == "aggressive":
            num_fallacies = min(2, level // 3 + 1)
        else:
            num_fallacies = min(1, level // 3 + 1)

        # Select random fallacies
        available_fallacies = list(self.fallacy_templates.keys())
        selected_fallacies = random.sample(available_fallacies, min(num_fallacies, len(available_fallacies)))

        # Build counter by combining fallacy templates
        counter_parts = []
        for fallacy_type in selected_fallacies:
            templates = self.fallacy_templates.get(fallacy_type, [])
            if templates:
                counter_parts.append(random.choice(templates))

        counter_text = " ".join(counter_parts)

        self.rounds_played += 1

        return counter_text, selected_fallacies

    def get_hint(self, hidden_fallacies: List[str]) -> str:
        """Get a hint about the hidden fallacies."""
        if not hidden_fallacies:
            return "Không có ngụy biện ở đây!"

        # Capitalize and format fallacy names
        formatted = ", ".join(f.replace("_", " ").title() for f in hidden_fallacies)
        return f"💡 Gợi ý: AI sử dụng những ngụy biện này: {formatted}"

    def reset(self) -> None:
        """Reset AI state for new game."""
        self.state = "neutral"
        self.rounds_played = 0
