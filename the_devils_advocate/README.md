# The Devil's Advocate - Luật Sư Của Quỷ

**Trò chơi tranh luận console text-based để rèn luyện tư duy phản biện & kỹ năng thuyết phục**

## 🎮 Giới thiệu

Trong game này, bạn đóng vai **Luật sư của Quỷ** – phải bào chữa cho những lập luận vô lý nhất. Mục tiêu: đạt 1000 điểm để trở thành **Luật sư vĩ đại của Quỷ**!

### Cơ chế chơi:
1. 🛡️ Nhận một thesis absurd (lập luận vô lý)
2. 🔥 AI sẽ tấn công bằng counter-arguments với ngụy biện
3. 💬 Bạn phải phản bác bằng logic chặt chẽ
4. 🐛 Phát hiện ngụy biện AI dùng để được điểm bonus
5. 📈 Tích lũy 1000 điểm để thắng

---

## 📋 Yêu cầu

- **Python 3.8+** (Windows, macOS, Linux)
- Không cần thư viện ngoài (chỉ dùng standard library)

---

## 🚀 Cài đặt & Chạy

### 1. Clone hoặc tải code
```bash
cd the_devils_advocate
```

### 2. Chạy game
```bash
python main.py
```

(Hoặc trên Windows: `python main.py`)

### 3. Enjoy! 🎉

---

## 🎯 Cách chơi

### Lệnh chính:

| Lệnh | Mô tả | Ví dụ |
|------|-------|-------|
| `react <lập luận>` | Phản bác tự do | `react Pizza dứa là fusion nguồn gốc hiện đại` |
| `fallacy <tên>` | Chỉ ra ngụy biện | `fallacy ad_hominem` |
| `evidence <bằng chứng>` | Đưa bằng chứng | `evidence Pizza dứa bán 1 tỷ chiếc/năm` |
| `hint` | Xin gợi ý (-10 pts) | `hint` |
| `stats` | Xem điểm số | `stats` |
| `surrender` | Bỏ cuộc round | `surrender` |
| `help` | Hiển thị trợ giúp | `help` |
| `quit` | Thoát game | `quit` |

### Ngụy biện (Fallacies):

Game dạy bạn nhận diện 10 loại ngụy biện chính:

1. **ad_hominem** - Tấn công cá nhân, không ý kiến
2. **strawman** - Bóp méo lập luận đối phương
3. **appeal_emotion** - Kêu gọi cảm xúc thay vì logic
4. **false_dichotomy** - Nhị nguyên giả (A hoặc B)
5. **slippery_slope** - Dốc trơn (1 bước dẫn đến thảm họa)
6. **begging_question** - Lập luận tròn
7. **appeal_authority** - Tin chuyên gia mù quáng
8. **red_herring** - Xao nhãng, ẩn vấn đề chính
9. **hasty_generalization** - Kết luận quá nhanh
10. **false_cause** - Nhầm tương quan = nhân quả

### Điểm được tính từ:
- **Logic** (0-50): Độ vừng vạng & từ khóa logic
- **Phát hiện ngụy biện** (0-30): Chỉ ra đúng loại ngụy biện
- **Sáng tạo** (0-20): Từ vựng đa dạng & ý tưởng độc đáo
- **Bonus**: +20 nếu phản bác hoàn hảo (tổng ≥ 90)

---

## 🎓 Ví dụ gameplay

```
╔════════════════════════════════════════╗
║           TRẠNG THÁI TRÂN ĐẤU          ║
╚════════════════════════════════════════╝
📊 Điểm: 150/1000
🎯 Cấp độ: 1
❤️  Mạng sống: 3
🔥 Streak: 0

🛡️ THESIS: Ăn pizza kèm dứa là phát minh vĩ đại nhất nhân loại!

🔥 AI: Bạn chỉ ủng hộ vì bạn không biết ăn uống!

Turn 1/5

> Không, pizza Hawaii là fusion cuisine kết hợp nhuộm ngọt-mặn như phong cách modern cooking hiện tại.

✅ Lập luận tốt! +75 điểm
Logic: 35/50 | Sáng tạo: 8/20

🔥 AI: Hoặc bạn sống theo cách này, hoặc bạn không tôn trọng bản thân! Vậy bạn bỏ qua những điều khác rồi?

Turn 2/5

> fallacy false_dichotomy Bạn dùng nhị nguyên giả. Có nhiều cách để thưởng thức đồ ăn mà không cần bỏ qua có thứ khác!

✅ Lập luận tốt! +85 điểm
Logic: 40/50 | Ngụy biện: 30/30 | Sáng tạo: 15/20 | Bonus: +20

✓ Phát hiện ngụy biện: False Dichotomy

🎉 Bạn đã thắng round này!
```

---

## 📊 Progress & Save

Game tự động **lưu tiến độ** vào file `save/player_save.json`:
- Điểm số
- Cấp độ
- Achievements
- Stats (rounds chơi, thắng/thua)

Lần chơi tiếp theo, bạn sẽ được hỏi có tiếp tục từ nơi dừng không.

---

## 🏆 Win/Lose Conditions

### **WIN** 🎉
- Đạt **1000 điểm** → Trở thành **Luật sư vĩ đại của Quỷ**

### **LOSE** 💀
- Thua **3 rounds liên tiếp** → Game Over (Luật sư của Quỷ cảm thấy thất vọng)

---

## 🎯 Progression & Levels

| Cấp độ | Độ khó | Số ngụy biện/turn | Lập luận |
|--------|--------|-----------------|---------|
| 1-3 | Dễ | 1 | Vấn đề hàng ngày |
| 4-7 | Trung | 2 | Lập luận absurd |
| 8+ | Khó | 3+ | Lập luận ngu xuẩn |

Bạn tự động **level up** mỗi khi **thắng 2 rounds liên tiếp**.

---

## 🏅 Achievements

Mở khóa các thành tích:
- 🏆 **"Persuasion God"** - Đạt 1000 điểm
- 🐛 **"Fallacy Slayer"** - Phát hiện 50 ngụy biện
- 🐛 **"Fallacy Master"** - Phát hiện 100 ngụy biện
- 🔥 **"On Fire"** - Thắng 5 rounds liên tiếp
- 📈 **"Level 10"** - Đạt cấp độ 10

---

## 📂 Cấu trúc thư mục

```
the_devils_advocate/
├── main.py                    # Entry point
├── README.md                  # File này
├── game/
│   ├── __init__.py           # Package init
│   ├── core.py               # Game state & round logic
│   ├── player.py             # Player class & save/load
│   ├── scorer.py             # Scoring system
│   ├── prosecutor.py         # AI opponent
│   └── utils.py              # UI, colors, parsing
├── data/
│   ├── thesis_bank.json      # 40+ absurd theses
│   └── fallacies.json        # 10 fallacy types + templates
└── save/
    └── player_save.json      # Auto-saved progress (created on first run)
```

---

## 🛠️ Development Info

### Kiến trúc:
- **Layered Architecture**: Presentation → Application → Domain → Data
- **Cross-platform**: Dùng ANSI escape codes cho màu sắc (Windows/Mac/Linux)
- **No dependencies**: Chỉ standard library Python

### Key Modules:
- `Scorer`: Tính điểm logic, phát hiện ngụy biện, sáng tạo
- `ProsecutorAI`: Generate thesis & counter-arguments
- `InputParser`: Parse commands & detect fallacies
- `GameState`: Quản lý round, player, game over conditions

---

## 🐛 Debugging / Troubleshooting

### **Vấn đề: Không thấy màu sắc trên Windows**
→ Cài đặt Python 3.10+ hoặc dùng Windows Terminal

### **Vấn đề: File JSON không tìm thấy**
→ Đảm bảo chạy từ thư mục `the_devils_advocate/`

### **Vấn đề: Lỗi "No module named 'game'"**
→ Chạy: `python main.py` từ thư mục gốc (contain `main.py`)

---

## 📝 Lưu ý

- Game hoàn toàn **offline** - không cần internet
- **Responsive** - ngay cả trên máy chậm (<0.5s/turn)
- **Replayable** - 40+ theses + procedural AI = vô tận combinations
- **Educational** - Rèn luyện tư duy logic & nhận diện ngụy biện

---

## 🚀 Future Ideas (Roadmap)

- [ ] Multiplayer (local turn-based)
- [ ] Vietnamese/English i18n
- [ ] Daily challenge (thesis mới mỗi ngày)
- [ ] Custom thesis mode
- [ ] Discord bot version
- [ ] Web version (Streamlit)

---

## 📧 Liên hệ / Feedback

Có ý kiến hoặc bug report? Hãy cho tôi biết! 🙏

---

**The Devil's Advocate v1.0** - Hãy bào chữa cho Quỷ! 🔥⚖️

Good luck, và hãy thử phá kỷ lục! 💪
