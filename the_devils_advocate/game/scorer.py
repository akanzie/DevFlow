"""
Scoring system for The Devil's Advocate game.
Calculates scores based on logic, fallacy detection, and creativity.
"""

from typing import Dict, Tuple, Optional


class Scorer:
    """Calculate and manage game scoring."""

    # Logic keywords (Vietnamese & English)
    LOGIC_KEYWORDS = {
        "vì", "do đó", "bằng chứng", "chứng minh", "logic",
        "vậy", "tức là", "nên", "rõ ràng", "theo",
        "dẫn đến", "kết quả", "hệ quả", "vì vậy", "vì thế",
        "evidence", "therefore", "because", "because of",
        "since", "so", "thus", "hence", "proof", "demonstrated",
        "logically", "consequently", "reasoning"
    }

    # Creativity bonus: diverse words
    COMMON_WORDS = {
        "và", "là", "cái", "cái gì", "không", "có", "bạn", "tôi",
        "that", "is", "the", "this", "that", "and", "or", "not",
        "you", "i", "we", "he", "she", "it"
    }

    @staticmethod
    def calculate_score(
        rebuttal: str,
        hidden_fallacies: list,
        detected_fallacy: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Calculate score for a rebuttal.

        Args:
            rebuttal: Player's rebuttal text
            hidden_fallacies: List of fallacies AI used
            detected_fallacy: Fallacy player claimed to detect (if any)

        Returns:
            Dict with keys: logic, fallacy_detection, creativity, total, bonus
        """

        scores = {
            "logic": 0,
            "fallacy_detection": 0,
            "creativity": 0,
            "bonus": 0,
            "total": 0
        }

        # 1. Logic Score (0-50)
        scores["logic"] = Scorer._calculate_logic_score(rebuttal)

        # 2. Fallacy Detection Score (0-30)
        if detected_fallacy:
            scores["fallacy_detection"] = Scorer._calculate_fallacy_detection_score(
                detected_fallacy, hidden_fallacies
            )

        # 3. Creativity Score (0-20)
        scores["creativity"] = Scorer._calculate_creativity_score(rebuttal)

        # Calculate total
        scores["total"] = scores["logic"] + scores["fallacy_detection"] + scores["creativity"]

        # 4. Bonus: Perfect rebuttal (+20)
        if scores["total"] >= 90:
            scores["bonus"] = 20

        scores["total"] += scores["bonus"]
        scores["total"] = min(scores["total"], 120)  # Cap at 120

        return scores

    @staticmethod
    def _calculate_logic_score(rebuttal: str) -> int:
        """Calculate logic score based on text characteristics."""
        if not rebuttal or len(rebuttal) < 5:
            return 0

        score = 0

        # Base score from length (longer = more thought)
        score += min(15, len(rebuttal) // 8)

        # Count logic keywords
        rebuttal_lower = rebuttal.lower()
        logic_count = sum(1 for keyword in Scorer.LOGIC_KEYWORDS if keyword in rebuttal_lower)
        score += min(20, logic_count * 5)

        # Check for specific patterns (strong logic indicators)
        if "do đó" in rebuttal_lower or "therefore" in rebuttal_lower:
            score += 5
        if "bằng chứng" in rebuttal_lower or "evidence" in rebuttal_lower:
            score += 5
        if "tức là" in rebuttal_lower or "that is" in rebuttal_lower:
            score += 3

        # Check for examples or specific references
        if any(char.isdigit() for char in rebuttal):
            score += 5  # Uses numbers/statistics

        # Cap at 50
        return min(50, score)

    @staticmethod
    def _calculate_fallacy_detection_score(
        detected_fallacy: str,
        hidden_fallacies: list
    ) -> int:
        """Calculate score for fallacy detection."""
        if not hidden_fallacies or not detected_fallacy:
            return 0

        detected_lower = detected_fallacy.lower()

        # Normalize fallacy names
        for fallacy in hidden_fallacies:
            fallacy_lower = fallacy.lower().replace("_", " ")
            detected_normalized = detected_lower.replace("_", " ")

            # Check exact match or partial match
            if fallacy_lower in detected_normalized or detected_normalized in fallacy_lower:
                # Award points equally if multiple fallacies
                return max(15, 30 // len(hidden_fallacies))

        return 0  # Incorrect fallacy detection

    @staticmethod
    def _calculate_creativity_score(rebuttal: str) -> int:
        """Calculate creativity score based on vocabulary variety."""
        if not rebuttal:
            return 0

        score = 0
        words = rebuttal.lower().split()
        total_words = len(words)

        if total_words < 3:
            return 0

        # Count unique non-common words
        unique_words = set(words) - Scorer.COMMON_WORDS
        diversity = len(unique_words) / total_words
        score += int(diversity * 15)

        # Bonus for unusual words (length > 8 chars)
        long_words = [w for w in words if len(w) > 8]
        score += min(5, len(long_words))

        return min(20, score)

    @staticmethod
    def get_feedback_string(scores: Dict[str, int]) -> str:
        """Generate human-readable feedback for scores."""
        feedback = []

        if scores["logic"] > 0:
            feedback.append(f"Logic: {scores['logic']}/50")

        if scores["fallacy_detection"] > 0:
            feedback.append(f"Ngụy biện: {scores['fallacy_detection']}/30")

        if scores["creativity"] > 0:
            feedback.append(f"Sáng tạo: {scores['creativity']}/20")

        if scores["bonus"] > 0:
            feedback.append(f"Bonus: +{scores['bonus']}")

        return " | ".join(feedback)
