# 🎮 The Devil's Advocate - GUI & GPT版本 (新功能！)

## ✨ 新增功能 - GUI + GPT集成版

### 🚀 快速开始

#### 1️⃣  安装依赖

```bash
cd the_devils_advocate
pip install -r requirements.txt
```

**需要安装的包:**
- `PyQt6` - 现代化GUI界面
- `openai` - GPT API集成
- `python-dotenv` - 环境变量管理

#### 2️⃣  运行GUI版本

```bash
python gui.py
```

或者:
```bash
python3 gui.py
```

---

## 🎯 GUI 特点

### ✅ 现代化界面
- 专业的PyQt6桌面应用
- 跨平台运行 (Windows/Mac/Linux)
- 直观的用户体验
- 实时反馈和评分

### ✅ GPT AI集成
- **动态情景生成** - 无限多个论题
- **AI对手** - 真实的反驳论证
- **智能评分** - GPT评估你的论证
- **多种类别** - 食物、科技、哲学、流行文化等

### ✅ 高级功能
- 📊 详细的评分分析 (Logic, Persuasion, Creativity, Relevance)
- 💡 智能提示系统
- 💾 自动保存游戏进度
- 🏆 成就系统
- 🔥 难度自适应

---

## 🔑 OpenAI API 设置

### 获取 API Key

1. 访问: https://platform.openai.com/api-keys
2. 登录或注册 OpenAI 账户
3. 创建新的 API key
4. 复制 key

### 首次运行时

游戏启动时会弹出对话框要求输入 API key:

```
🔑 OpenAI API Configuration
请输入您的 OpenAI API key (或按 Enter 跳过):
```

### 成本说明

- **gpt-3.5-turbo** - 非常便宜 (推荐)
  - ~$0.0005 per 1K tokens
  - 每个情景约 $0.001-0.003

- **使用成本**:
  - 100 局游戏 ≈ $0.3-1.0
  - 1000 局游戏 ≈ $3-10

### 免费模式

如果没有 API key，游戏仍然可以玩，但会使用 **Fallback 模式**:
- 预设的情景库
- 后备论点
- 基础评分系统

---

## 🎮 GUI 游戏流程

### 主菜单
```
⚖️ LUẬT SƯ CỦA QUỶ

[🎮 Chơi Mới]
[💾 Tải Trò Chơi]
[❓ Hướng Dẫn]
[📊 Thống Kê Toàn Cục]
[❌ Thoát]
```

### 新游戏设置
```
🎮 Trò Chơi Mới

👤 Nhập tên của bạn:
   [Luật Sư Vô Danh]

🎯 Chọn độ khó:
   [Level 1 (Dễ) ▼]

📂 Chọn loại (Category):
   [Random ▼]
   - Food & Cuisine
   - Technology
   - Philosophy
   - Pop Culture
   - Sports
   - Education
   - Entertainment
```

### 游戏界面
```
👤 Kiệt | 💰 Score: 500/1000 | 🎯 Level: 5 | ❤️ Lives: 3

[生成情景] ⏳ Generating scenario...

🛡️ THESIS:
┌─────────────────────────────────┐
│ Pizza with pineapple is the     │
│ greatest culinary invention     │
└─────────────────────────────────┘

📂 Category: Food & Cuisine | 🆚 Level: 5
💡 Hint: Think about tropical fruits and fusion cuisine

🔥 AI Counter-Arguments:
[Counter 1 ▼]

┌─────────────────────────────────┐
│ You only believe that because   │
│ you're not educated about real  │
│ cuisine!                        │
└─────────────────────────────────┘

💬 Phản bác của bạn:
┌─────────────────────────────────┐
│ [输入你的反驳...]              │
│                                 │
│ Gợi ý: 使用逻辑关键词,         │
│ 或指出AI使用的谬论              │
└─────────────────────────────────┘

[✓ 提交反驳] [💡 提示] [📋 菜单]
```

### 评分结果
```
📊 KẾT QUẢ ĐÁNH GIÁ

Logic Score:         75/100
Persuasion Score:    82/100
Creativity Score:    88/100
Relevance Score:     90/100

TOTAL SCORE:        83.75/100 💰 +84 pts

👤 Kiệt
💰 Total Score: 584/1000
🎯 Level: 5
❤️ Lives: 3
🔥 Streak: 1

🎉 EXCELLENT rebuttal! You won this round!

[➡️ Màn Tiếp Theo] [📋 Menu]
```

---

## 📊 评分系统 (GPT 驱动)

### 4 个维度评分

| 维度 | 解释 | 满分 |
|------|------|------|
| **Logic** | 论证的逻辑严密性 | 100 |
| **Persuasion** | 论证的说服力 | 100 |
| **Creativity** | 创意和原创性 | 100 |
| **Relevance** | 回应对手论点的相关性 | 100 |

### 勋章系统

🏆 **Persuasion God** - 达到 1000 分
🐛 **Fallacy Slayer** - 发现 50 个谬论
🔥 **On Fire** - 5 连胜
📈 **Level Master** - 达到 10 级

---

## 🤖 GPT 功能说明

### 1. 动态情景生成
```
GPT 为每场比赛生成:
- 独特的论题
- 论题类别
- 玩家提示
- 论题背景
```

示例提示词:
```
Generate an absurd debate thesis for a game.
Difficulty Level: 5/10

Return JSON:
{
  "thesis": "...",
  "category": "...",
  "hint": "...",
  "why_absurd": "..."
}
```

### 2. AI 对手论证
```
GPT 生成多个对手论证,
包含логические обо谬论:
- Ad Hominem
- Straw Man
- Appeal to Emotion
- False Dichotomy
- Slippery Slope
```

### 3. 论证评估
```
GPT 评估玩家的反驳:
- 检查逻辑清晰度
- 评估说服力
- 检测创意程度
- 验证相关性
```

### 4. 实时反馈
```
GPT 提供:
- 详细的分数分析
- 改进建议
- 不同方面的反馈
- 学习提示
```

---

## 💡 游戏技巧

### 赢得比赛的秘诀

✅ **高分核心要素:**
1. **使用逻辑关键词** - "因为(vì)", "所以(do đó)", "证据(bằng chứng)"
2. **结构清晰** - 开头、主体、结论
3. **举例说明** - 提供具体的例子或统计数据
4. **指出谬论** - "这是 ad hominem 谬论"
5. **创意思维** - 想出新颖的辩论角度

❌ **避免:**
- 太短的反驳 (少于 30 个字)
- 只说"不对"而不说为什么
- 忽视对手论点
- 使用侮辱性语言
- 无关的扯淡

### 谬论识别技巧

学会识别这些常见谬论:

| 谬论 | 特征 | 例子 |
|------|------|------|
| **Ad Hominem** | 攻击人而不是论点 | "你只这么说是因为你是个白痴!" |
| **Strawman** | 歪曲对手观点 | "所以你说我们应该吃掉所有的猫?" |
| **False Cause** | 错把相关当因果 | "因为下雨所以我生病了" |
| **False Dichotomy** | 假二分法 | "要么同意我,要么你是我的敌人" |

---

## 🔧 高级配置

### 环境变量配置

创建 `.env` 文件:
```
OPENAI_API_KEY=sk-xxxxx...
```

### 自定义模型

编辑 `game/gpt_integration.py`:
```python
self.model = "gpt-4"  # 改用 GPT-4 (更贵但更强)
```

### 调整难度

编辑 `gui_main.py`:
```python
# 改变 AI 的积极性
num_fallacies = min(3, level // 3 + 2)  # 增加谬论数量
```

---

## 📱 系统要求

### 最低配置
- Python 3.8+
- Windows 10+ / macOS 10.14+ / Linux (任意)
- 4GB RAM
- 网络连接 (用于 GPT API)

### 推荐配置
- Python 3.10+
- Windows 11 / macOS 12+ / Ubuntu 20.04+
- 8GB RAM
- 稳定的网络连接

---

## 🆘 故障排除

### 问题 1: ImportError: No module named 'PyQt6'

**解决:**
```bash
pip install PyQt6
```

### 问题 2: API Key 无效

**解决:**
1. 检查 OpenAI 账户状态
2. 验证 key 是否正确
3. 确保账户有余额
4. 访问 https://platform.openai.com/account/billing/overview

### 问题 3: 无法连接 GPT

**解决:**
1. 检查网络连接
2. 禁用 VPN/代理
3. 检查防火墙设置
4. 切换到 Fallback 模式 (跳过 API key)

### 问题 4: GUI 界面显示不完整

**解决:**
- 更新 PyQt6: `pip install --upgrade PyQt6`
- 使用不同的主题: 在 gui_main.py 中修改 `app.setStyle()`

### 问题 5: 游戏运行缓慢

**解决:**
- 降低游戏难度
- 减少 AI 生成的计数
- 清除缓存数据
- 升级网络连接

---

## 📚 文件结构更新

```
the_devils_advocate/
├── main.py                   # 原始控制台版本
├── gui.py                    # GUI 启动器 ✨ 新文件
├── gui_main.py               # GUI 主程序 ✨ 新文件
├── requirements.txt          # 项目依赖 ✨ 新文件
│
├── game/
│   ├── core.py              # 游戏逻辑
│   ├── player.py            # 玩家类
│   ├── scorer.py            # 评分系统
│   ├── prosecutor.py        # AI 对手
│   ├── utils.py             # 工具函数
│   └── gpt_integration.py   # GPT 集成 ✨ 新文件
│
├── data/
│   ├── thesis_bank.json     # 论题库
│   └── fallacies.json       # 谬论库
│
└── save/
    └── player_save.json     # 保存游戏
```

---

## 🎓 学到的东西

通过玩这个游戏,你将学到:

📚 **逻辑思维**
- 识别和避免逻辑谬误
- 构建有说服力的论证
- 批判性思维和分析

🎯 **修辞技巧**
- 如何有效地说服他人
- 论证的结构和策略
- 反驳技巧

🧠 **认知能力**
- 快速思考
- 问题解决
- 语言表达

---

## 🚀 下一步

1. **安装依赖**: `pip install -r requirements.txt`
2. **获取 API Key**: https://platform.openai.com/api-keys
3. **启动 GUI**: `python gui.py`
4. **开始游戏**: 点击"Chơi Mới" 并享受!

---

## 📝 示例对话

### Round 1:
```
THESIS: Pizza with pineapple is the greatest culinary invention ever

AI COUNTER: You only like pineapple pizza because you have no taste!

PLAYER REBUTTAL: 
That's ad hominem reasoning. My preference for Hawaiian pizza is based on:
(1) The fruit-savory combination matches modern fusion cuisine styles
(2) Over 1 billion Hawaiian pizzas are sold annually worldwide
(3) Professional chefs recognize it as a valid culinary style
Therefore, pizza with pineapple is indeed an innovative invention.

SCORE: 92/100 🎉 EXCELLENT REBUTTAL!
```

---

**Enjoy the game and become the Master Devil's Advocate! 🔥⚖️**
