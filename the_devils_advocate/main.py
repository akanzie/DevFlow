#!/usr/bin/env python3
"""
The Devil's Advocate - Main Game Entry Point
A console-based debate simulator to train critical thinking and persuasion skills.

Run with: python main.py
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import game module
sys.path.insert(0, str(Path(__file__).parent))

from game import (
    Player, GameState, ConsoleUI, InputParser,
    print_welcome_screen, print_help
)
from game.utils import Colors


def load_or_create_player() -> Player:
    """Load existing player or create new one."""
    saved_player = Player.load()

    if saved_player:
        ConsoleUI.print_info(f"Tìm thấy người chơi cũ: {saved_player.name}")
        response = ConsoleUI.safe_input("Tiếp tục chơi? (y/n): ").lower()

        if response in ["y", "yes"]:
            return saved_player

    # Create new player
    name = ConsoleUI.safe_input("Nhập tên của bạn: ").strip()
    if not name:
        name = "Luật sư Vô danh"

    return Player(name)


def display_round_start(game_state: GameState) -> None:
    """Display round start screen."""
    print()
    ConsoleUI.print_header(f"ROUND {game_state.player.rounds_played + 1}")
    print(game_state.get_status_string())
    print()
    ConsoleUI.print_thesis(game_state.current_round.thesis)
    print()
    ConsoleUI.print_ai_counter(game_state.current_round.ai_counter)
    print()
    ConsoleUI.print_info("Phản bác lập luận này của AI. (Gõ 'help' để xem lệnh)")
    print()


def play_round(game_state: GameState) -> bool:
    """
    Play a single round with multiple turns.
    Returns True if round won, False if round lost.
    """
    max_turns = 5

    for turn in range(1, max_turns + 1):
        ConsoleUI.print_info(f"Turn {turn}/{max_turns}")

        # Get player input
        user_input = ConsoleUI.safe_input("> ").strip()

        if not user_input:
            ConsoleUI.print_warning("Vui lòng nhập lệnh hoặc lập luận!")
            continue

        # Parse input
        command, arg = InputParser.parse_command(user_input)

        # Handle special commands
        if command == "quit":
            ConsoleUI.print_warning("Bạn đã thoát trò chơi.")
            return False

        if command == "help":
            print_help()
            continue

        if command == "stats":
            print(game_state.player.get_stats_string())
            continue

        if command == "hint":
            hint_text = game_state.use_hint()
            ConsoleUI.print_info(hint_text)
            continue

        if command == "surrender":
            ConsoleUI.print_warning("Bạn đã bỏ cuộc round này!")
            game_state.surrender_round()
            return False

        # Process rebuttal
        if command == "fallacy":
            result = game_state.process_rebuttal(arg, command="fallacy", arg=arg)
        elif command == "evidence":
            rebuttal = user_input.replace("evidence", "").strip()
            result = game_state.process_rebuttal(rebuttal, command="evidence", arg=arg)
        else:
            # Free-form rebuttal (or treat entire input as rebuttal)
            result = game_state.process_rebuttal(user_input)

        if not result["success"]:
            ConsoleUI.print_error(result.get("message", "Lỗi xử lý đầu vào!"))
            continue

        # Display feedback
        print()
        if result["score_dict"]["total"] >= 60:
            ConsoleUI.print_success(f"Lập luận tốt! +{result['score_dict']['total']} điểm")
        else:
            ConsoleUI.print_warning(f"Có thể làm tốt hơn... +{result['score_dict']['total']} điểm")

        ConsoleUI.print_colored(result["feedback"], Colors.CYAN)

        if result["detected_fallacy"]:
            ConsoleUI.print_success(f"✓ Phát hiện ngụy biện: {result['detected_fallacy'].replace('_', ' ').title()}")

        print()

        # Check round result
        if result["round_won"]:
            ConsoleUI.print_success("🎉 Bạn đã thắng round này!")
            game_state.end_round(won=True)
            return True

    # If reaches max turns without winning
    ConsoleUI.print_warning("❌ Hết lượt! Bạn không thể bào chữa thành công lần này.")
    game_state.end_round(won=False)
    return False


def main_game_loop() -> bool:
    """Main game loop. Returns True if player won, False if lost."""
    # Create/load player
    player = load_or_create_player()
    print()

    # Create game state
    game_state = GameState(player)

    # Main loop
    while not game_state.is_game_over():
        # Start new round
        game_state.start_new_round()
        display_round_start(game_state)

        # Play round
        won = play_round(game_state)

        print()

        # Check game over
        if game_state.is_game_over():
            break

    # Save player state
    player.save()

    # Display end screen
    print()
    print(game_state.get_end_screen())
    print()

    return game_state.win


def main():
    """Main entry point."""
    ConsoleUI.clear_screen()
    print_welcome_screen()
    print()

    # Ask to start or view help
    while True:
        choice = ConsoleUI.safe_input(
            "Bạn muốn gì? (play/help/quit): "
        ).lower().strip()

        if choice in ["play", "p", ""]:
            break
        elif choice in ["help", "h"]:
            print_help()
            print()
        elif choice in ["quit", "q"]:
            ConsoleUI.print_warning("Cảm ơn đã chơi Luật sư của Quỷ!")
            sys.exit(0)
        else:
            ConsoleUI.print_error("Lựa chọn không hợp lệ. Vui lòng nhập: play, help, hoặc quit")

    print()
    ConsoleUI.clear_screen()
    ConsoleUI.print_header("BẮT ĐẦU TRÒ CHƠI")
    print()

    # Play game
    try:
        won = main_game_loop()

        # Ending
        print()
        ConsoleUI.print_header("KẾT THÚC TRÒ CHƠI")
        print()

        if won:
            ConsoleUI.print_success("Chúc mừng bạn! Bạn là một Luật sư vĩ đại của Quỷ!")
        else:
            ConsoleUI.print_warning("Hãy thử lại và làm tốt hơn lần tiếp theo!")

        print()
        ConsoleUI.safe_input("Nhấn Enter để thoát...")

    except KeyboardInterrupt:
        print()
        ConsoleUI.print_warning("Trò chơi đã bị ngắt bởi người dùng.")
        sys.exit(0)


if __name__ == "__main__":
    main()
