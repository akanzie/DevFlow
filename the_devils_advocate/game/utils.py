"""
Utility functions for The Devil's Advocate game.
Includes: ANSI colors, console formatting, input parsing.
"""

import sys
import os
from typing import Optional, Tuple


class Colors:
    """ANSI color codes for cross-platform terminal output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class ConsoleUI:
    """Console UI utilities for game display."""

    @staticmethod
    def clear_screen():
        """Clear the console screen (cross-platform)."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_colored(text: str, color: str = Colors.WHITE, bold: bool = False) -> None:
        """Print colored text to console."""
        prefix = f"{Colors.BOLD}{color}" if bold else color
        print(f"{prefix}{text}{Colors.RESET}")

    @staticmethod
    def print_header(text: str) -> None:
        """Print a formatted header."""
        ConsoleUI.print_colored("=" * 70, Colors.CYAN)
        ConsoleUI.print_colored(text, Colors.BOLD + Colors.CYAN)
        ConsoleUI.print_colored("=" * 70, Colors.CYAN)

    @staticmethod
    def print_thesis(thesis: str) -> None:
        """Print the thesis in prominent format."""
        ConsoleUI.print_colored(f"🛡️  THESIS: {thesis}", Colors.BOLD + Colors.RED)

    @staticmethod
    def print_ai_counter(counter: str) -> None:
        """Print AI counter-argument."""
        ConsoleUI.print_colored(f"🔥 AI: {counter}", Colors.YELLOW)

    @staticmethod
    def print_success(text: str) -> None:
        """Print success message (green)."""
        ConsoleUI.print_colored(f"✅ {text}", Colors.GREEN)

    @staticmethod
    def print_error(text: str) -> None:
        """Print error message (red)."""
        ConsoleUI.print_colored(f"❌ {text}", Colors.RED)

    @staticmethod
    def print_info(text: str) -> None:
        """Print info message (blue)."""
        ConsoleUI.print_colored(f"ℹ️  {text}", Colors.BLUE)

    @staticmethod
    def print_warning(text: str) -> None:
        """Print warning message (yellow)."""
        ConsoleUI.print_colored(f"⚠️  {text}", Colors.YELLOW)

    @staticmethod
    def safe_input(prompt: str = "> ") -> str:
        """Get user input with colored prompt."""
        try:
            ConsoleUI.print_colored(prompt, Colors.GREEN, bold=True)
            return input()
        except KeyboardInterrupt:
            print()
            ConsoleUI.print_warning("Game interrupted by user.")
            sys.exit(0)
        except EOFError:
            return "quit"


class InputParser:
    """Parse and validate user input."""

    VALID_COMMANDS = {
        "react",
        "fallacy",
        "evidence",
        "surrender",
        "hint",
        "help",
        "stats",
        "quit"
    }

    FALLACY_NAMES = {
        "ad hominem", "ad_hominem", "adho", "adhom",
        "strawman", "straw man", "strawman fallacy",
        "appeal to emotion", "emotion", "appeal_emotion",
        "false dichotomy", "false_dichotomy", "dichotomy",
        "slippery slope", "slippery_slope", "slope",
        "begging the question", "begging_question", "circular",
        "appeal to authority", "authority", "appeal_authority",
        "red herring", "red_herring", "herring",
        "hasty generalization", "hasty_generalization", "generalization",
        "false cause", "false_cause", "causation"
    }

    @staticmethod
    def parse_command(text: str) -> Tuple[Optional[str], str]:
        """
        Parse input and return (command, argument) or (None, text) if not a command.
        Returns tuple: (command_type, content_or_text)
        """
        text = text.strip()
        parts = text.split(maxsplit=1)

        if not parts:
            return None, ""

        first_word = parts[0].lower()

        if first_word in InputParser.VALID_COMMANDS:
            content = parts[1] if len(parts) > 1 else ""
            return first_word, content
        
        # If it's not a command, treat as free-form rebuttal
        return None, text

    @staticmethod
    def detect_fallacy(text: str) -> Optional[str]:
        """
        Detect which fallacy (if any) is mentioned in the text.
        Returns the normalized fallacy name or None.
        """
        text_lower = text.lower()
        
        # Mapping of fallacy keywords to canonical names
        fallacy_map = {
            "ad hominem": "ad_hominem",
            "ad_hominem": "ad_hominem",
            "adho": "ad_hominem",
            "adhom": "ad_hominem",
            "strawman": "strawman",
            "straw man": "strawman",
            "appeal to emotion": "appeal_emotion",
            "emotion": "appeal_emotion",
            "false dichotomy": "false_dichotomy",
            "dichotomy": "false_dichotomy",
            "slippery slope": "slippery_slope",
            "slope": "slippery_slope",
            "begging the question": "begging_question",
            "circular": "begging_question",
            "appeal to authority": "appeal_authority",
            "authority": "appeal_authority",
            "red herring": "red_herring",
            "herring": "red_herring",
            "hasty generalization": "hasty_generalization",
            "generalization": "hasty_generalization",
            "false cause": "false_cause",
            "causation": "false_cause"
        }
        
        for keyword, fallacy in fallacy_map.items():
            if keyword in text_lower:
                return fallacy
        
        return None

    @staticmethod
    def extract_logic_keywords(text: str) -> int:
        """Count logic-related keywords in text."""
        logic_keywords = [
            "vì", "do đó", "bằng chứng", "chứng minh", "logic",
            "vậy", "tức là", "nên", "rõ ràng", "theo",
            "dẫn đến", "kết quả", "hệ quả", "vì vậy",
            "evidence", "therefore", "because", "because of",
            "since", "so", "thus", "hence", "proof"
        ]
        text_lower = text.lower()
        return sum(1 for keyword in logic_keywords if keyword in text_lower)


def print_welcome_screen():
    """Display game welcome screen."""
    ConsoleUI.print_header("CHÀO MỪNG ĐẾN VỚI LUẬT SƯ CỦA QUỶ")
    print()
    ConsoleUI.print_colored("The Devil's Advocate - Trò chơi tranh luận khiêu khích!", Colors.CYAN)
    print()
    print("Bạn sẽ bào chữa cho những lập luận vô lý...")
    print("AI sẽ tấn công bằng những ngụy biện!")
    print("Canh bạc: Tư duy logic + Kỹ năng thuyết phục")
    print()
    ConsoleUI.print_warning("Nhiệm vụ: Đạt 1000 điểm để trở thành Luật sư vĩ đại của Quỷ!")
    print()


def print_help():
    """Display help information."""
    ConsoleUI.print_header("HƯỚNG DẪN CHƠI")
    print()
    print("LỆNH CHỦ YẾU:")
    ConsoleUI.print_colored("  react <lập luận>", Colors.GREEN, bold=True)
    print("    - Phản bác tự do (mặc định nếu không có lệnh)")
    print()
    ConsoleUI.print_colored("  fallacy <tên ngụy biện>", Colors.GREEN, bold=True)
    print("    - Chỉ ra AI dùng ngụy biện nào (ad_hominem, strawman, vv)")
    print()
    ConsoleUI.print_colored("  evidence <bằng chứng>", Colors.GREEN, bold=True)
    print("    - Đưa bằng chứng hỗ trợ lập luận")
    print()
    ConsoleUI.print_colored("  hint", Colors.GREEN, bold=True)
    print("    - Xin gợi ý (trừ 10 điểm)")
    print()
    ConsoleUI.print_colored("  surrender", Colors.GREEN, bold=True)
    print("    - Bỏ cuộc round này (trừ 1 mạng)")
    print()
    ConsoleUI.print_colored("  stats", Colors.GREEN, bold=True)
    print("    - Xem điểm số & thống kê")
    print()
    ConsoleUI.print_colored("  help", Colors.GREEN, bold=True)
    print("    - Hiển thị trợ giúp này")
    print()
    ConsoleUI.print_colored("  quit", Colors.GREEN, bold=True)
    print("    - Thoát trò chơi")
    print()
    print("ĐIỂM ĐƯỢC TÍNH TỪ:")
    print("  - Logic: 0-50 điểm (dựa độ cho dài & từ khóa logic)")
    print("  - Phát hiện ngụy biện: 0-30 điểm (chỉ ra ngụy biện AI dùng)")
    print("  - Sáng tạo: 0-20 điểm (ý tưởng độc đáo)")
    print("  - Thưởng: +20 điểm nếu phản bác hoàn hảo!")
    print()
