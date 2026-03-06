# 🚀 The Devil's Advocate - Complete Installation Guide

## 📋 Lựa Chọn Phiên Bản

Hiện tại có 2 phiên bản trò chơi:

| Phiên Bản | Loại | Chạy Lệnh | Yêu Cầu |
|-----------|------|-----------|---------|
| **Console** | Text-based CLI | `python main.py` | Python 3.8+ |
| **GUI (Mới)** | PyQt6 Desktop + GPT | `python gui.py` | Python 3.8+ + PyQt6 + OpenAI key |

---

## 🎯 Cài Đặt Nhanh (GUI + GPT)

### Bước 1: Cài Đặt Python

Tải Python từ: https://www.python.org/downloads/

**Windows:**
```bash
# Chạy installer và chọn "Add Python to PATH"
python --version  # Kiểm tra cài đặt thành công
```

**Mac:**
```bash
brew install python3
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
```

### Bước 2: Cài Đặt Thư Viện

```bash
# Di chuyển đến thư mục game
cd the_devils_advocate

# Cài đặt tất cả dependencies
pip install -r requirements.txt
```

Hoặc cài từng cái:
```bash
pip install PyQt6 openai python-dotenv
```

### Bước 3: Chạy Game

```bash
python gui.py
```

**Nếu lỗi "module not found":**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python gui.py
```

---

## 🔑 Thiết Lập OpenAI API Key

### Cách 1: Interactive Setup (Khuyến Khích)

Khi chạy `python gui.py`, game sẽ hỏi:

```
🔑 OpenAI API Configuration
Nhập API key của bạn (hoặc nhấn Enter để bỏ qua):
```

Dán API key và Enter.

### Cách 2: Environment Variable

Tạo file `.env` trong thư mục `the_devils_advocate`:

```
OPENAI_API_KEY=sk-xxxxx...xxxxx
```

### Cách 3: Vĩnh Viễn (Biến Môi Trường Hệ Thống)

**Windows:**
1. Nhấn `Win + X` → "System"
2. "Advanced system settings" → "Environment variables"
3. New → Tên: `OPENAI_API_KEY`, Giá trị: `sk-xxxxx...`
4. Restart terminal

**Mac/Linux:**
```bash
echo 'export OPENAI_API_KEY="sk-xxxxx...xxxxx"' >> ~/.bashrc
source ~/.bashrc
```

---

## ⚙️ Thiết Lập OpenAI Account

### 1. Tạo Tài Khoản

1. Truy cập: https://openai.com/signup
2. Đăng ký email hoặc Google account
3. Xác thực email

### 2. Thêm Phương Thức Thanh Toán

1. Đăng nhập: https://platform.openai.com
2. Chọn "Billing" → "Payment methods"
3. Thêm thẻ credit/debit

### 3. Tạo API Key

1. Chọn "API keys" từ sidebar: https://platform.openai.com/api-keys
2. Nhấn "+ Create new secret key"
3. Copy key (chỉ hiển thị một lần!)
4. Paste vào game hoặc `.env` file

### 4. (Tùy Chọn) Đặt Usage Limits

Để tránh chi phí bất ngờ:

1. Truy cập: https://platform.openai.com/account/billing/limits
2. Đặt "Hard limit" (ví dụ: $5/tháng)
3. Đặt "Soft limit" (ví dụ: $2/ngày)

---

## 💰 Chi Phí Sử Dụng

### Giá Model

| Model | Chi Phí (per 1K tokens) |
|-------|------------------------|
| gpt-3.5-turbo | $0.5/$1.5 (input/output) |
| gpt-4 | $30/$60 (input/output) |

### Chi Phí Dự Tính

Per Round:
- Input: ~200 tokens = $0.0001
- Output: ~300 tokens = $0.00045
- **Total: ~$0.0005**

Scenarios:
- 100 rounds = ~$0.05
- 1000 rounds = ~$0.50
- 10,000 rounds = ~$5

**Khuyến Khích:**
- Sử dụng `gpt-3.5-turbo` (mặc định)
- Đặt usage limit ở bảng điều khiển OpenAI
- Monitor chi phí hàng ngày

---

## 🎮 Chạy Game Lần Đầu

### GUI Version
```bash
python gui.py
```

**Màn hình khởi động:**
```
⚙️ OpenAI API Configuration

Để sử dụng tính năng GPT, bạn cần API key từ OpenAI.

1. Truy cập: https://platform.openai.com/api-keys
2. Tạo mới API key
3. Paste vào ô dưới đây

💰 Ghi chú: Sử dụng GPT sẽ tốn tiền (rẻ với gpt-3.5-turbo)

API Key:
[________________]

[✓ Lưu & Tiếp tục]  [✗ Bỏ qua (Dùng fallback)]
```

Chọn một:
1. **Paste API key** → Dùng GPT (tự động tạo thêm lập luận)
2. **Skip (Bỏ qua)** → Dùng fallback mode (kích bản cố định)

---

## ✅ Danh Sách Kiểm Tra Cài Đặt

- [ ] Python 3.8+ cài đặt thành công
- [ ] `pip install -r requirements.txt` chạy không lỗi
- [ ] OpenAI API key (tùy chọn, có thể để trống)
- [ ] `python gui.py` khởi động không lỗi
- [ ] Cửa sổ GUI hiển thị

---

## 🐛 Xử Lý Sự Cố

### "ModuleNotFoundError: No module named 'PyQt6'"

**Giải quyết:**
```bash
pip install PyQt6
```

### "ModuleNotFoundError: No module named 'openai'"

**Giải quyết:**
```bash
pip install openai
```

### "openai.AuthenticationError: Invalid API key"

**Giải quyết:**
1. Kiểm tra API key có đúng không (bắt đầu bằng `sk-`)
2. Kiểm tra OpenAI account có active không
3. Kiểm tra account có đủ credit không
4. Đăng xuất/đăng nhập lại OpenAI dashboard

### "Max retries exceeded" hoặc "Connection timeout"

**Giải quyết:**
1. Kiểm tra kết nối internet
2. Thử vô hiệu hóa VPN/Proxy
3. Chờ vài phút rồi thử lại
4. Sử dụng fallback mode

### GUI không hiển thị hoặc crash

**Giải quyết:**
```bash
# Update PyQt6
pip install --upgrade PyQt6

# Thử chạy console version
python main.py
```

### Game chạy rất chậm

**Giải quyết:**
1. Kiểm tra kết nối internet
2. Giảm độ khó trong game
3. Đóng ứng dụng khác chạy nền
4. Cập nhật Python và các thư viện

---

## 📱 So Sánh: Console vs GUI

| Tính Năng | Console | GUI + GPT |
|-----------|---------|-----------|
| **Giao diện** | Text/ANSI | Professional PyQt6 |
| **Thesis** | 40 cố định | Vô hạn (GPT) |
| **AI Counters** | Template cố định | GPT tạo động |
| **Scoring** | Rule-based | GPT analysis |
| **Tốc độ** | Nhanh | Phụ thuộc network |
| **Cài đặt** | Đơn giản | Cần API key |
| **Chi phí** | Miễn phí | ~$0.0005 per round |
| **Multiple Dialogues** | Giới hạn | Không giới hạn |

---

## 🎯 Khuyến Nghị

**Cho người mới bắt đầu:**
1. Chạy console version trước: `python main.py`
2. Quen thuộc với game mechanics
3. Sau đó chuyển sang GUI: `python gui.py`

**Cho người muốn trải nghiệm đầy đủ:**
1. Cài đặt PyQt6 & OpenAI key từ đầu
2. Chạy GUI version: `python gui.py`
3. Dùng fallback nếu không có API key

**Cho developer/advanced users:**
1. Clone repo
2. Tùy chỉnh `gpt_integration.py` (đổi model, prompt, etc.)
3. Chiếu code vào dự án riêng

---

## 📞 Cần Giúp Đỡ?

### Các Lỗi Phổ Biến

| Lỗi | Nguyên Nhân | Giải Quyết |
|-----|-------------|-----------|
| `SyntaxError` | Code có lỗi | Cập nhật Python hoặc file |
| `ImportError` | Thiếu library | `pip install -r requirements.txt` |
| `ConnectionError` | Không có internet | Kiểm tra network |
| `AuthenticationError` | API key sai | Tạo key mới từ OpenAI |

### Liên Hệ

- Bug report: Check GitHub issues
- Tính năng mới: Hãy đề xuất!
- Tối ưu hóa: Pull requests welcome!

---

## 📚 Tài Liệu Thêm

- **README.md** - Tổng quan game
- **GUI_GPT_GUIDE.md** - Hướng dẫn chi tiết GUI
- **START_HERE.md** - Quick start
- **GAME_DESIGN_DOCUMENT.md** - Design doc gốc

---

## 🎉 Bạn Đã Sẵn Sàng!

```bash
# One command to start!
python gui.py

# Hoặc console version
python main.py
```

**Chúc bạn chơi vui và trở thành Luật sư vĩ đại của Quỷ! 🔥⚖️**
