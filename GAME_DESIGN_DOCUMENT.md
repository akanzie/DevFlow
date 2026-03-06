# Tài Liệu Thiết Kế Game: The Devil's Advocate (Luật Sư Của Quỷ)

**Phiên bản tài liệu**: 1.0  
**Ngày tạo**: 03/03/2026  
**Tác giả**: Grok (dựa trên ý tưởng của Kiệt)  
**Platform**: Console text-based (Swift trên Windows/Mac/Linux)  
**Thời lượng phát triển MVP**: 3-5 ngày (cho dev cá nhân)  
**Mục tiêu**: Rèn luyện **tư duy phản biện** (critical thinking) & **thuyết phục** (persuasion) qua việc bào chữa cho các lập luận "vô lý".

---

## 1. Overview / Tổng Quan

### Mô Tả Ngắn Gọn
Người chơi đóng vai **Luật sư của Quỷ** – phải bào chữa cho những tình huống **không thể bào chữa được** (absurd arguments). Ví dụ: "Chứng minh pizza dứa là phát minh vĩ đại nhất nhân loại" hoặc "Bào chữa cho việc ngủ muộn là bí quyết thành công".  

**AI đối thủ** đưa ra **luận điểm phản bác** (counter-arguments) với ngụy biện (fallacies). Người chơi phải **phản bác bằng logic chặt chẽ**, dùng **bằng chứng giả định**, và **phát hiện ngụy biện** để thắng round.

### Genre
Text-based Debate Simulator (Trò chơi tranh luận turn-based).

### Target Audience
- Sinh viên, dev, nhân viên văn phòng (18-35 tuổi) muốn rèn tư duy logic & thuyết phục.
- Người yêu thích debate, philosophy, hoặc game như "The Stanley Parable" nhưng text-only.

### Core Loop (Vòng Lặp Chính)
1. Nhận **thesis absurd** (luận điểm vô lý để bào chữa).
2. AI đưa **counter-argument** (với ngụy biện ẩn).
3. Người chơi **input phản bác** (text tự do).
4. **AI chấm điểm** & feedback → Score + next round.

### Unique Selling Point (USP)
- **Scoring thông minh**: Phát hiện tự động ngụy biện (ad hominem, strawman...) trong counter của AI, thưởng điểm nếu người chơi chỉ ra.
- **Procedural generation**: Thesis & counter vô tận từ bank templates.
- **Replayability cao**: Levels khó dần, achievements (e.g., "Master Fallacy Hunter").

### Win/Lose Conditions
- **Win**: Đạt 1000 điểm (Master Devil's Advocate).
- **Lose**: 3 rounds thua liên tiếp (AI "thẩm phán" kết án).

---

## 2. Gameplay Mechanics / Cơ Chế Chơi

### Rules Chi Tiết
- Mỗi **round** (debate case): 3-5 turns trao đổi.
- Người chơi **bào chữa** (defend thesis) → AI **tấn công** → Người chơi **phản bác**.
- Input: Text tự do (1-2 câu ngắn), parse bằng keyword + length.
- **Ngụy biện (Fallacies)**: 10 loại chính (xem bảng dưới), AI random inject.

### Fallacies Table

| Loại Ngụy Biện | Mô Tả | Ví Dụ Trong Game |
|---|---|---|
| Ad Hominem | Tấn công cá nhân | "Bạn ủng hộ pizza dứa vì bạn béo ú!" |
| Strawman | Bóp méo lập luận | "Vậy bạn bảo pizza dứa ngon hơn mẹ bạn nấu?" |
| Appeal to Emotion | Kêu gọi cảm xúc | "Dứa trên pizza làm tôi buồn vì ký ức tuổi thơ!" |
| False Dichotomy | Nhị nguyên giả | "Hoặc pizza dứa, hoặc bạn ghét Ý!" |
| Slippery Slope | Dốc trơn | "Pizza dứa → Ngày mai ăn pizza mèo!" |

### Actions/Commands

| Command/Input Style | Mô Tả | Ví Dụ |
|---|---|---|
| `react <text>` | Phản bác tự do | "react Pizza dứa kết hợp ngọt-mặn như fusion cuisine hiện đại." |
| `fallacy <tên>` | Chỉ ra ngụy biện | "fallacy ad hominem – Tập trung vào ý kiến, không cá nhân." |
| `evidence` | Đưa bằng chứng giả định | "evidence Hawaii pizza bán 1 tỷ chiếc/năm." |
| `surrender` | Bỏ cuộc round | "surrender" |
| `hint` | Gợi ý (trừ 10 điểm) | "hint" |

### Scoring System
- **Logic Tightness**: 0-50 (dựa độ dài + keywords logic: "vì", "do đó", "bằng chứng").
- **Fallacy Detection**: 0-30 (nếu chỉ đúng loại → +full).
- **Creativity**: 0-20 (từ mới, humor detect đơn giản).
- **Total per round**: 0-100. Bonus: Perfect rebuttal (+20).

---

## 3. Game Structure / Cấu Trúc Game

### Progression
- **Level 1-3**: Thesis dễ (food, daily life). AI weak fallacies.
- **Level 4-7**: Thesis absurd hơn (politics, science fake). AI multi-fallacies.
- **Level 8+**: Free mode – Custom thesis từ người chơi.

| Level | Độ Khó | Số Turns/Round | Thesis Examples |
|---|---|---|---|
| 1 | Dễ | 3 | Pizza dứa vĩ đại |
| 5 | Trung | 4 | Ngủ muộn = thành công |
| 10 | Khó | 5 | Trái đất phẳng là sự thật |

### World/Map
Không có map – **Menu-driven**: Main menu → New Game → Rounds → Stats.

### Endgame & Replayability
- **Achievements**: "Fallacy Slayer" (detect 50), "Persuasion God" (1000 pts).
- **Seeds**: Random seed cho thesis/counter.
- **Daily Challenge**: Thesis mới mỗi ngày (local time-based).

---

## 4. Characters/Entities & AI

### Player
- Stats: Score (Int), Streak (Int), Detected Fallacies (Int).

### AI Opponents
- **Prosecutor AI**: Rule-based state machine.
  - States: Neutral → Aggressive → Desperate (inject more fallacies).
  - Logic: Random thesis từ bank (50+ templates) + counter với 1-3 fallacies.

### Pseudocode AI

```
func generateCounter(thesis: String) -> String {
  let fallacies = ["ad hominem", "strawman"]
  return "Counter: \(randomFallacyText()) \(thesis twist)"
}
```

---

## 5. UI/UX & Input/Output

### Output Format (ANSI Colors for Windows Swift)
- **Prompt**: `> ` (xanh lá).
- **Thesis**: Bold đỏ.
- **AI Counter**: Vàng, highlight fallacy (ẩn cho người chơi phát hiện).
- **Feedback**: Xanh (đúng) / Đỏ (sai).

### Example Session

```
🛡️ THESIS: Pizza dứa là phát minh vĩ đại nhất!
🔥 AI: Bạn chỉ nói vậy vì bạn không biết nấu ăn!
> react Không, đây là fusion Ý-Hawaii, bán triệu chiếc!
✅ Logic: 40/50 | Fallacy (Ad Hominem detected!): 30/30
Score: +90
```

### Input Parser
- Swift: `readLine()` → split words → match keywords.
- Fuzzy: "adho" → "ad hominem".

### Help System
`help` → Liệt kê commands + top fallacies.

---

## 6. Balancing & Economy

### Numbers Tuning

| Metric | Easy | Medium | Hard |
|---|---|---|---|
| AI Fallacies/Round | 1 | 2 | 3+ |
| Required Score/Level | 70 | 80 | 90 |
| Hint Cost | 10 pts | 20 | 30 |

### Difficulty Curve
- Win rate target: 70% level 1 → 40% level 10.
- Playtesting: 10-15 phút/session.

---

## 7. Technical Specifications

### Language/Engine
- **Swift 6.x** (console, Windows toolchain via WinGet).
- **No external libs**: Chỉ built-in (String, Array, Dictionary, Random).

### Data Structures

```swift
struct Player { 
  var score: Int = 0
  var streak: Int = 0 
}

struct Round { 
  var thesis: String
  var aiCounter: String
  var fallacies: [String] 
}

let thesisBank: [String] = ["Pizza dứa...", ...] // 50+
let fallacyTemplates: [String: [String]] = ["ad hominem": ["Bạn chỉ... vì..."]]
```

### Key Functions
- `parseInput(_ input: String) -> (logicScore: Int, fallacyDetected: String?)`
- `generateThesis() -> String`
- `colorPrint(_ text: String, color: Color)`

### Performance
- <1s/turn. Max 100 rounds/session.

### Save/Load
JSON local: `score`, `achievements`.

---

## 8. Testing & Roadmap

### Test Cases
- Edge: Invalid input → "Try again".
- Logic: Parser accuracy 90%+.
- Balancing: Manual 10 sessions/level.

### Milestones
- **MVP (Day 1-2)**: Core loop + 10 theses.
- **Polish (Day 3)**: Scoring + fallacies detect.
- **Release (Day 4-5)**: Achievements, save, levels.
- **Future**: Multiplayer (local turn-based), VN/Eng i18n.

### Risks
- Parser quá strict → Giảm fuzzy matching.
- Scoring unfair → Playtest với 5 người.

---

## Appendix: Quick Reference

### Command Cheat Sheet
```
react <text>           - Respond freely
fallacy <name>         - Identify fallacy
evidence <proof>       - Provide evidence
hint                   - Get hint (-10 pts)
surrender              - Give up round
help                   - Show help
stats                  - View player stats
```

### Fallacy Types Quick Reference
1. **Ad Hominem** - Attack the person, not argument
2. **Strawman** - Misrepresent opposing view
3. **Appeal to Emotion** - Use feelings instead of logic
4. **False Dichotomy** - Present only two options
5. **Slippery Slope** - Assume one leads to extreme
6. **Begging the Question** - Circular reasoning
7. **Appeal to Authority** - Trust authority blindly
8. **Red Herring** - Distract from main issue
9. **Hasty Generalization** - Draw conclusions too quickly
10. **False Cause** - Assume correlation = causation

---

**End of Document**
