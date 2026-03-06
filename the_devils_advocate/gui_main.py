"""
PyQt6 GUI for The Devil's Advocate Game
Modern desktop interface with AI integration (Gemini Free + OpenAI GPT).
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Union

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QComboBox, QProgressBar,
    QMessageBox, QDialog, QLineEdit, QTabWidget, QTableWidget,
    QTableWidgetItem, QSpinBox, QFileDialog, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap
from PyQt6.QtCore import QTimer

from game.player import Player
from game.core import GameState, Round
from game.gpt_integration import GPTIntegration, GPTConfigDialog
from game.gemini_integration import GeminiIntegration, GeminiConfigDialog
from game.utils import Colors


class AIWorker(QThread):
    """Worker thread for AI calls (Gemini or GPT) to prevent UI freezing."""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, ai: Union[GeminiIntegration, GPTIntegration], task: str, **kwargs):
        super().__init__()
        self.ai = ai
        self.task = task
        self.kwargs = kwargs

    def run(self):
        """Run AI task in background."""
        try:
            if self.task == "scenario":
                result = self.ai.generate_scenario(**self.kwargs)
            elif self.task == "counters":
                result = self.ai.generate_counter_arguments(**self.kwargs)
            elif self.task == "evaluate":
                result = self.ai.evaluate_rebuttal(**self.kwargs)
            else:
                result = {}
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class AIProviderDialog(QDialog):
    """Dialog to choose between Gemini (Free) and OpenAI GPT."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🤖 Choose AI Provider")
        self.setGeometry(100, 100, 600, 350)
        self.provider = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🤖 Select AI Provider")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Choose Gemini
        gemini_frame = QWidget()
        gemini_layout = QVBoxLayout(gemini_frame)
        gemini_btn = QPushButton("✨ Google Gemini (FREE - Khuyên dùng!)")
        gemini_btn.setStyleSheet("background-color: #4285f4; color: white; padding: 10px; font-weight: bold; font-size: 12px;")
        gemini_text = QLabel(
            "✅ FREE tier không cần credit card\n"
            "✅ 60 requests/phút (đủ cho game)\n"
            "✅ Thực hiện ngay, không cần setup"
        )
        gemini_btn.clicked.connect(lambda: self.select_provider("gemini"))
        gemini_layout.addWidget(gemini_text)
        gemini_layout.addWidget(gemini_btn)
        layout.addWidget(gemini_frame)

        # OR
        or_label = QLabel("─ hoặc ─")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(or_label)

        # Choose OpenAI
        openai_frame = QWidget()
        openai_layout = QVBoxLayout(openai_frame)
        openai_btn = QPushButton("⚡ OpenAI GPT-3.5 (Trả phí nhưng mạnh hơn)")
        openai_btn.setStyleSheet("background-color: #10a37f; color: white; padding: 10px; font-weight: bold; font-size: 12px;")
        openai_text = QLabel(
            "💰 Cần credit card + tiền ($0.0005/game)\n"
            "⚡ Nhanh + thông minh hơn một chút\n"
            "🔑 Bạn cần API key từ OpenAI"
        )
        openai_btn.clicked.connect(lambda: self.select_provider("openai"))
        openai_layout.addWidget(openai_text)
        openai_layout.addWidget(openai_btn)
        layout.addWidget(openai_frame)

        # Fallback option
        fallback_btn = QPushButton("🔧 Chỉ dùng Fallback Mode (Offline)")
        fallback_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px;")
        fallback_btn.clicked.connect(lambda: self.select_provider("fallback"))
        layout.addWidget(fallback_btn)

        self.setLayout(layout)

    def select_provider(self, provider: str):
        """Set selected provider."""
        self.provider = provider
        self.accept()


class DebateWindow(QMainWindow):
    """Main game window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚖️  The Devil's Advocate - Luật Sư Của Quỷ")
        self.setGeometry(100, 100, 1200, 800)

        self.player: Optional[Player] = None
        self.game_state: Optional[GameState] = None
        self.ai: Union[GeminiIntegration, GPTIntegration, None] = None
        self.ai_type: str = "fallback"
        self.current_scenario: Dict = {}
        
        # Initialize with fallback first (safe default)
        self.ai = GeminiIntegration()
        self.ai_type = "fallback"

        self.init_ui()
        self.show_main_menu()

    def show_ai_setup_dialog(self):
        """Show AI provider selection dialog."""
        try:
            provider_dialog = AIProviderDialog(self)
            result = provider_dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                provider = provider_dialog.provider or "fallback"
                
                if provider == "gemini":
                    try:
                        gemini_dialog = GeminiConfigDialog(self)
                        if gemini_dialog.exec() == QDialog.DialogCode.Accepted:
                            api_key = gemini_dialog.get_api_key()
                            if api_key:
                                self.ai = GeminiIntegration(api_key)
                                self.ai_type = "gemini"
                                if self.ai.is_available():
                                    self.statusBar().showMessage("✅ Gemini FREE Tier Connected!")
                                    QMessageBox.information(self, "✅ Success", "Gemini connected successfully!")
                                else:
                                    QMessageBox.warning(self, "⚠️  Warning", "Gemini không kết nối được, sẽ dùng fallback mode.")
                                    self.ai = GeminiIntegration()
                                    self.ai_type = "fallback"
                            else:
                                self.ai = GeminiIntegration()
                                self.statusBar().showMessage("ℹ️  Fallback Mode (Offline)")
                                self.ai_type = "fallback"
                        else:
                            self.ai = GeminiIntegration()
                            self.statusBar().showMessage("ℹ️  Fallback Mode (Offline)")
                            self.ai_type = "fallback"
                    except Exception as e:
                        print(f"Gemini dialog error: {e}")
                        QMessageBox.warning(self, "❌ Lỗi", f"Lỗi cấu hình Gemini: {str(e)}")
                        self.ai = GeminiIntegration()
                        self.ai_type = "fallback"
                        
                elif provider == "openai":
                    try:
                        openai_dialog = GPTConfigDialog(self)
                        if openai_dialog.exec() == QDialog.DialogCode.Accepted:
                            api_key = openai_dialog.get_api_key()
                            if api_key:
                                self.ai = GPTIntegration(api_key)
                                self.ai_type = "openai"
                                if self.ai.is_available():
                                    self.statusBar().showMessage("✅ OpenAI GPT Connected!")
                                    QMessageBox.information(self, "✅ Success", "OpenAI GPT connected successfully!")
                                else:
                                    QMessageBox.warning(self, "⚠️  Warning", "GPT không kết nối được, sẽ dùng fallback mode.")
                                    self.ai = GPTIntegration()
                                    self.ai_type = "fallback"
                            else:
                                self.ai = GPTIntegration()
                                self.statusBar().showMessage("ℹ️  Fallback Mode (Offline)")
                                self.ai_type = "fallback"
                        else:
                            self.ai = GPTIntegration()
                            self.statusBar().showMessage("ℹ️  Fallback Mode (Offline)")
                            self.ai_type = "fallback"
                    except Exception as e:
                        print(f"GPT dialog error: {e}")
                        QMessageBox.warning(self, "❌ Lỗi", f"Lỗi cấu hình GPT: {str(e)}")
                        self.ai = GPTIntegration()
                        self.ai_type = "fallback"
                        
                else:  # fallback
                    self.ai = GeminiIntegration()
                    self.statusBar().showMessage("ℹ️  Fallback Mode (Offline - AI disabled)")
                    self.ai_type = "fallback"
            else:
                self.ai = GeminiIntegration()
                self.statusBar().showMessage("ℹ️  Fallback Mode (Offline)")
                self.ai_type = "fallback"
        except Exception as e:
            print(f"AI setup error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "❌ Lỗi", f"Lỗi cấu hình AI: {str(e)}\n\nSử dụng Fallback Mode.")
            self.ai = GeminiIntegration()
            self.statusBar().showMessage("ℹ️  Fallback Mode (Offline)")
            self.ai_type = "fallback"

    def init_ui(self):
        """Initialize UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Create status bar
        self.status_label = QLabel("Chọn một lựa chọn từ menu")
        self.statusBar().addWidget(self.status_label)

    def show_main_menu(self):
        """Display main menu."""
        self.clear_layout()

        layout = QVBoxLayout()

        # Title
        title = QLabel("⚖️  LUẬT SƯ CỦA QUỶ")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(
            "Trò chơi tranh luận để rèn luyện tư duy phản biện\n"
            "Bào chữa cho những lập luận vô lý & phát hiện ngụy biện"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)

        layout.addSpacing(40)

        # Buttons
        btn_font = QFont()
        btn_font.setPointSize(12)

        new_game_btn = QPushButton("🎮 Chơi Mới")
        new_game_btn.setFont(btn_font)
        new_game_btn.setMinimumHeight(60)
        new_game_btn.clicked.connect(self.show_new_game_dialog)
        layout.addWidget(new_game_btn)

        load_game_btn = QPushButton("💾 Tải Trò Chơi")
        load_game_btn.setFont(btn_font)
        load_game_btn.setMinimumHeight(60)
        load_game_btn.clicked.connect(self.load_game)
        layout.addWidget(load_game_btn)

        help_btn = QPushButton("❓ Hướng Dẫn")
        help_btn.setFont(btn_font)
        help_btn.setMinimumHeight(60)
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)

        stats_btn = QPushButton("📊 Thống Kê Toàn Cục")
        stats_btn.setFont(btn_font)
        stats_btn.setMinimumHeight(60)
        stats_btn.clicked.connect(self.show_global_stats)
        layout.addWidget(stats_btn)

        ai_btn = QPushButton("🤖 Cấu Hình AI")
        ai_btn.setFont(btn_font)
        ai_btn.setMinimumHeight(60)
        ai_btn.clicked.connect(self.show_ai_setup_dialog)
        layout.addWidget(ai_btn)

        layout.addSpacing(20)

        quit_btn = QPushButton("❌ Thoát")
        quit_btn.setFont(btn_font)
        quit_btn.setMinimumHeight(50)
        quit_btn.setStyleSheet("background-color: #ff6b6b;")
        quit_btn.clicked.connect(self.close)
        layout.addWidget(quit_btn)

        layout.addStretch()

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_new_game_dialog(self):
        """Show dialog to start new game."""
        dialog = QDialog(self)
        dialog.setWindowTitle("🎮 Trò Chơi Mới")
        dialog.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nhập tên của bạn:"))
        name_input = QLineEdit()
        name_input.setText("Luật Sư Vô Danh")
        layout.addWidget(name_input)

        layout.addWidget(QLabel("Chọn độ khó:"))
        difficulty_combo = QComboBox()
        difficulty_combo.addItems(["Level 1 (Dễ)", "Level 5 (Trung bình)", "Level 10 (Khó)"])
        layout.addWidget(difficulty_combo)

        layout.addWidget(QLabel("Chọn loại (Category):"))
        category_combo = QComboBox()
        category_combo.addItems([
            "Random", "Food & Cuisine", "Technology", "Philosophy",
            "Pop Culture", "Sports", "Education", "Entertainment"
        ])
        layout.addWidget(category_combo)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("✓ Bắt Đầu")
        cancel_btn = QPushButton("✗ Hủy")

        def start_game():
            name = name_input.text().strip() or "Luật Sư Vô Danh"
            level = int(difficulty_combo.currentText().split()[1])
            category = None if category_combo.currentText() == "Random" else category_combo.currentText()

            self.player = Player(name)
            self.player.level = level
            self.game_state = GameState(self.player)

            self.show_game_screen(category)
            dialog.close()

        ok_btn.clicked.connect(start_game)
        cancel_btn.clicked.connect(dialog.close)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        dialog.setLayout(layout)
        dialog.exec()

    def show_game_screen(self, category: Optional[str] = None):
        """Display main game screen."""
        self.clear_layout()

        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        player_info = QLabel(
            f"👤 {self.player.name} | 💰 Score: {self.player.score}/1000 | "
            f"🎯 Level: {self.player.level} | ❤️  Lives: {self.player.lives}"
        )
        player_info.setFont(self.get_font(11, bold=True))
        header_layout.addWidget(player_info)
        layout.addLayout(header_layout)

        # Generate new scenario
        self.statusBar().showMessage("⏳ Generating scenario...")
        scenario = self.ai.generate_scenario(category, self.player.level)
        self.current_scenario = scenario

        # Thesis display
        thesis_label = QLabel("🛡️  THESIS:")
        thesis_label.setFont(self.get_font(10, bold=True))
        layout.addWidget(thesis_label)

        thesis_display = QTextEdit()
        thesis_display.setText(scenario["thesis"])
        thesis_display.setReadOnly(True)
        thesis_display.setMinimumHeight(80)
        thesis_display.setStyleSheet("background-color: #fff3cd; color: #000;")
        layout.addWidget(thesis_display)

        # Scenario info
        info_text = f"📂 Category: {scenario['category']} | 🆚 Level: {scenario['level']}"
        if scenario.get("hint"):
            info_text += f"\n💡 Hint: {scenario['hint']}"
        info_label = QLabel(info_text)
        layout.addWidget(info_label)

        # Generate counter-arguments
        self.statusBar().showMessage("⏳ Generating AI counter-arguments...")
        counters = self.ai.generate_counter_arguments(scenario["thesis"], count=3)

        # Counter selection
        layout.addWidget(QLabel("🔥 AI Counter-Arguments:"))
        counter_combo = QComboBox()
        for i, counter in enumerate(counters, 1):
            counter_combo.addItem(f"Counter {i}", counter)
        layout.addWidget(counter_combo)

        counter_display = QTextEdit()
        counter_display.setText(counter_combo.currentData())
        counter_display.setReadOnly(True)
        counter_display.setMinimumHeight(100)
        counter_display.setStyleSheet("background-color: #ffe0e0; color: #000;")
        layout.addWidget(counter_display)

        counter_combo.currentIndexChanged.connect(
            lambda: counter_display.setText(counter_combo.currentData())
        )

        # Player rebuttal input
        layout.addWidget(QLabel("\n💬 Phản bác của bạn:"))
        self.rebuttal_input = QTextEdit()
        self.rebuttal_input.setMinimumHeight(120)
        self.rebuttal_input.setPlaceholderText(
            "Viết phản bác của bạn ở đây...\n\n"
            "Gợi ý: Nêu rõ lập luận, dùng từ khóa logic (vì, do đó, bằng chứng), "
            "hoặc chỉ ra ngụy biện AI dùng."
        )
        layout.addWidget(self.rebuttal_input)

        # Buttons
        btn_layout = QHBoxLayout()

        def submit_rebuttal():
            text = self.rebuttal_input.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "⚠️  Warning", "Vui lòng nhập phản bác!")
                return

            self.statusBar().showMessage("⏳ Evaluating your rebuttal...")

            counter_text = counter_combo.currentData()
            result = self.ai.evaluate_rebuttal(text, scenario["thesis"], counter_text)

            self.show_scoring_result(result, scenario)

        submit_btn = QPushButton("✓ Gửi Phản Bác")
        submit_btn.setMinimumHeight(50)
        submit_btn.setStyleSheet("background-color: #51cf66;")
        submit_btn.clicked.connect(submit_rebuttal)
        btn_layout.addWidget(submit_btn)

        hint_btn = QPushButton("💡 Gợi Ý (-10 pts)")
        hint_btn.setMinimumHeight(50)
        hint_btn.clicked.connect(lambda: self.show_hint(scenario))
        btn_layout.addWidget(hint_btn)

        menu_btn = QPushButton("📋 Menu")
        menu_btn.setMinimumHeight(50)
        menu_btn.clicked.connect(self.show_main_menu)
        btn_layout.addWidget(menu_btn)

        layout.addLayout(btn_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.statusBar().showMessage("✅ Ready to play!")

    def show_scoring_result(self, result: Dict, scenario: Dict):
        """Display scoring result."""
        self.clear_layout()
        layout = QVBoxLayout()

        # Score display
        score = result.get("total", 0)
        self.player.add_score(int(score))

        title = QLabel("📊 KẾT QUẢ ĐÁNH GIÁ")
        title.setFont(self.get_font(14, bold=True))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Scoring breakdown
        scores_text = f"""
Logic Score:         {result.get('logic', 0)}/100
Persuasion Score:    {result.get('persuasion', 0)}/100
Creativity Score:    {result.get('creativity', 0)}/100
Relevance Score:     {result.get('relevance', 0)}/100

TOTAL SCORE:         {score:.0f}/100 💰 +{score:.0f} pts
"""
        scores_label = QLabel(scores_text)
        scores_label.setFont(self.get_font(11, family="Courier"))
        layout.addWidget(scores_label)

        # Feedback
        if result.get("feedback"):
            feedback_label = QLabel("💭 Feedback:")
            feedback_label.setFont(self.get_font(10, bold=True))
            layout.addWidget(feedback_label)

            feedback_display = QTextEdit()
            feedback_display.setText(result["feedback"])
            feedback_display.setReadOnly(True)
            feedback_display.setMinimumHeight(100)
            layout.addWidget(feedback_display)

        # Player stats
        stats_text = f"""
👤 {self.player.name}
💰 Total Score: {self.player.score}/1000
🎯 Level: {self.player.level}
❤️  Lives: {self.player.lives}
🔥 Streak: {self.player.streak}
"""
        stats_label = QLabel(stats_text)
        stats_label.setFont(self.get_font(10))
        layout.addWidget(stats_label)

        # Win/Lose check
        won_this_round = score >= 80

        if won_this_round:
            self.player.add_round(won=True)
            msg = "🎉 EXCELLENT rebuttal! You won this round!"
            result_color = "#c8e6c9"
        else:
            self.player.add_round(won=False)
            msg = "❌ Not bad, but could be better. Try again!"
            result_color = "#ffcdd2"

        result_label = QLabel(msg)
        result_label.setFont(self.get_font(12, bold=True))
        result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_label.setStyleSheet(f"background-color: {result_color}; padding: 10px; border-radius: 5px;")
        layout.addWidget(result_label)

        layout.addSpacing(20)

        # Buttons
        btn_layout = QHBoxLayout()

        next_btn = QPushButton("➡️  Màn Tiếp Theo")
        next_btn.setMinimumHeight(50)
        next_btn.setStyleSheet("background-color: #51cf66;")
        if self.player.score >= 1000:
            QMessageBox.information(self, "🏆 VICTORY!", f"Bạn đã trở thành Luật sư vĩ đại của Quỷ!\nTotal Score: {self.player.score}")
            self.show_main_menu()
            return
        elif self.player.lives <= 0:
            QMessageBox.information(self, "💀 GAME OVER", f"Bạn đã thua!\nFinal Score: {self.player.score}")
            self.show_main_menu()
            return
        else:
            next_btn.clicked.connect(self.show_game_screen)

        menu_btn = QPushButton("📋 Menu")
        menu_btn.setMinimumHeight(50)
        menu_btn.clicked.connect(lambda: self.show_main_menu())

        btn_layout.addWidget(next_btn)
        btn_layout.addWidget(menu_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.player.save()

    def show_hint(self, scenario: Dict):
        """Show hint for current scenario."""
        hint = scenario.get("hint", "No hint available")
        QMessageBox.information(self, "💡 Gợi Ý", f"{hint}\n\nTrừ 10 điểm")
        self.player.add_score(-10)

    def show_help(self):
        """Show help dialog."""
        help_text = """⚖️  LUẬT SƯ CỦA QUỶ - HƯỚNG DẪN

🎯 MỤC TIÊU:
- Đạt 1000 điểm để trở thành Luật sư vĩ đại của Quỷ
- Bào chữa cho các lập luận vô lý
- Phát hiện ngụy biện trong lập luận của AI

📊 ĐIỂM SỐ:
- Logic:        0-100 (dựa trên sự hợp lý)
- Persuasion:   0-100 (sức thuyết phục)
- Creativity:   0-100 (sáng tạo & ý tưởng mới)
- Relevance:    0-100 (liên quan đến câu hỏi)

🎮 CÁCH CHƠI:
1. Nhận một thesis vô lý để bào chữa
2. AI sẽ đưa ra 3 counter-arguments
3. Chọn counter-argument & luận về nó
4. Viết phản bác của bạn
5. Hoàn thành & nhận điểm!

⚠️  LƯU Ý:
- Thua 3 rounds liên tiếp = Game Over
- Dùng gợi ý = trừ 10 điểm
- Lập luận dài hơn = điểm cao hơn
- Sử dụng từ khóa logic: "vì", "do đó", "bằng chứng"

🤖 GPT AI:
- Tạo ra hàng ngàn tình huống
- Đánh giá phản bác của bạn
- Thích ứng với độ khó

🏆 ĐẠT ĐƯỢC:
- Fallacy Slayer: Phát hiện 50 ngụy biện
- Persuasion God: 1000 điểm
- On Fire: Thắng 5 rounds liên tiếp
"""
        QMessageBox.information(self, "❓ Hướng Dẫn", help_text)

    def show_global_stats(self):
        """Show global statistics."""
        stats_text = f"""
📊 THỐNG KÊ TOÀN CỤC

Người chơi tốt nhất:
Chưa có dữ liệu

Thống kê game:
- Tổng rounds chơi: ?
- Tỷ lệ thắng: ?%
- Ngụy biện phát hiện: 0

Ghi chú: Dữ liệu sẽ được cập nhật khi chơi nhiều hơn.
"""
        QMessageBox.information(self, "📊 Thống Kê", stats_text)

    def load_game(self):
        """Load saved game."""
        saved_player = Player.load()
        if saved_player:
            self.player = saved_player
            self.game_state = GameState(self.player)
            QMessageBox.information(self, "✅ Tải thành công", f"Tiếp tục với {saved_player.name}")
            self.show_game_screen()
        else:
            QMessageBox.warning(self, "⚠️  Warning", "Không có trò chơi đã lưu!")

    def clear_layout(self):
        """Clear current layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

    @staticmethod
    def get_font(size: int = 10, bold: bool = False, family: str = "Arial") -> QFont:
        """Get formatted font."""
        font = QFont(family)
        font.setPointSize(size)
        if bold:
            font.setBold(True)
        return font


def main():
    """Main entry point for GUI."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    window = DebateWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
