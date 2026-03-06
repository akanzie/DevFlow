# 🤖 Gemini Integration Guide

**The Devil's Advocate** now supports **Google Gemini FREE Tier** in addition to OpenAI GPT!

## 🎯 What's New (v2.1.0)

### AI Provider Selection
On startup, the game now asks you to choose:

1. **✨ Google Gemini FREE (Recommended)**
   - Completely FREE (no credit card needed)
   - 60 requests per minute quota
   - Quick scenario generation
   - Works out of the box

2. **⚡ OpenAI GPT-3.5 (Paid but Powerful)**
   - Requires credit card (~$0.0005 per game)
   - Slightly faster and more intelligent
   - Alternative option

3. **🔧 Fallback Mode (Offline)**
   - No API key needed
   - Works offline with pre-loaded scenarios
   - Always available

## 🚀 Getting Your Gemini API Key (FREE!)

1. **Go to Google AI Studio:**
   - Visit: https://makersuite.google.com/app/apikey

2. **Create API Key:**
   - Click "Create API Key"
   - Select "Create API key in new project"
   - Copy the key

3. **Start Playing:**
   - Paste key when the game asks
   - Begin debating! 🎉

**Cost:** $0 (FREE for individual developers)

## 📊 Comparison

| Feature | Gemini FREE | OpenAI GPT | Fallback |
|---------|-------------|-----------|----------|
| **Cost** | $0 | $0.0005/game | $0 |
| **API Key** | Free from Google | Paid (needs card) | None |
| **Speed** | Fast | Very Fast | Instant |
| **Quality** | Excellent | Excellent | Good |
| **Requires Internet** | Yes | Yes | No |
| **Recommendation** | ✅ Best | Good | Offline only |

## 📁 New/Updated Files

- `game/gemini_integration.py` - NEW: Google Gemini wrapper
- `game/__init__.py` - UPDATED: v2.1.0 with Gemini exports
- `gui_main.py` - UPDATED: AI provider selection dialog
- `requirements.txt` - UPDATED: Added google-generativeai

## 🎮 First Run

```bash
python gui.py
```

**Dialog Flow:**
1. "Choose AI Provider" → Select Gemini
2. "Configure Google Gemini" → Paste API key (or skip for fallback)
3. Main Menu appears
4. Click "Chơi Mới" (New Game)
5. Start debating!

## ⚙️ Configuration

### Environment Variables
You can also set API keys via environment variables:

```bash
# For Gemini
set GOOGLE_API_KEY=your_key_here

# For OpenAI
set OPENAI_API_KEY=your_key_here
```

Then the game will auto-load these keys on startup.

## 🐛 Troubleshooting

**"Gemini not connecting"**
- Check: API key is correct (copy again from makersuite.google.com)
- Check: Internet connection is active
- Solution: Fall back to offline mode

**"Too many requests"**
- Gemini has a 60 requests/minute limit
- Solution: Wait a minute before next game
- Or: Switch to OpenAI GPT (higher limits)

**Slow scenario generation**
- This is normal for Gemini (slightly slower than GPT)
- First call takes ~2-3 seconds
- Subsequent calls are faster

## 📝 Implementation Details

### GeminiIntegration Class
Located in `game/gemini_integration.py`:

```python
gemini = GeminiIntegration(api_key="your_key_here")

# Generate scenario
scenario = gemini.generate_scenario(category="Technology", level=3)

# Generate counter-arguments
counters = gemini.generate_counter_arguments(thesis="AI will replace humans", count=3)

# Evaluate rebuttal
result = gemini.evaluate_rebuttal(
    rebuttal="AI augments but doesn't replace...",
    thesis="AI will replace humans",
    counter_arg="ML is replacing jobs..."
)
```

### Fallback Mode
If no API key is provided, both Gemini and GPT fall back to:
- Pre-loaded 40+ scenario database
- Template-based counter-arguments
- Random scoring (0-100 range)
- Fully functional offline

## 🔄 Migration from v2.0

If you were using v2.0:
- Nothing to change! API is backward compatible
- Old saves work with both AI providers
- Fallback mode still available
- Just update: `pip install google-generativeai`

## ✨ Next Steps

1. **Get Gemini Key:**
   - https://makersuite.google.com/app/apikey (2 minutes)

2. **Run Game:**
   ```bash
   cd the_devils_advocate
   python gui.py
   ```

3. **Select Gemini** → Paste key → Play!

Enjoy unlimited debate scenarios completely **FREE**! 🚀
