# SILVER DECK - Complete Setup Instructions

## 🚀 Step-by-Step Setup Guide

**Estimated Time**: 30-45 minutes  
**Difficulty**: Beginner-Friendly  
**Cost**: ~$5/month (Railway.app paid tier)

---

## PART 1: Prerequisites & Accounts

### Step 1.1: Create OANDA Account

**Purpose**: Get live silver prices and optional trade execution

1. Go to https://www.oanda.com
2. Click "Open Account"
3. Choose "Practice Account" (for paper trading)
4. Fill in details (name, email, password)
5. Verify email
6. Log in and go to **Account Settings**
7. Click **API & Tokens**
8. Click **Generate Token**
9. Name: "SILVER_DECK"
10. Click **Generate**
11. **COPY THE TOKEN** (you'll only see it once)
12. Go back to Account Settings
13. Find your **Account ID** (format: 123456789-001)
14. **COPY THE ACCOUNT ID**

✅ **Save**: You now have:
- `OANDA_API_TOKEN` (long string)
- `OANDA_ACCOUNT_ID` (9 digits-3 digits)

---

### Step 1.2: Create Telegram Bot

**Purpose**: Receive trading signals on your phone in real-time

1. Open Telegram app (or web: https://web.telegram.org)
2. Search for **@BotFather**
3. Click Start / Send `/newbot`
4. **BotFather asks**: "Alright, a new bot. How are we calling it? Please choose a name for your bot."
5. Type: `SilverDeckBot` (or any name ending in "Bot")
6. **BotFather asks**: "Good. Now let's choose a username for your bot. It must end in `bot`."
7. Type: `SilverDeck_Bot_XXXXXXX` (replace XXXXXXX with random numbers)
8. ✅ **BotFather sends you the token** - Copy it
   - Format: `123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdef`

✅ **Save**: `TELEGRAM_BOT_TOKEN`

---

### Step 1.3: Get Your Telegram Chat ID

**Purpose**: Tell the bot where to send signals (to YOUR chat)

1. In Telegram, search for **@userinfobot**
2. Click Start
3. It immediately sends you your User ID
   - "Your user id is: 123456789"
4. **COPY THIS NUMBER**

✅ **Save**: `TELEGRAM_CHAT_ID` (just the numbers)

---

### Step 1.4: Create Railway Account

**Purpose**: Host SILVER DECK 24/7 in the cloud (5 min per month cost)

1. Go to https://railway.app
2. Click **Sign Up**
3. Choose GitHub (easiest)
4. Authorize Railway to access your GitHub
5. Create account
6. Go to **Billing** tab
7. Add a payment method (credit/debit card)
8. Choose **Hobby plan** (~$7/month with $5 credit = ~$2)

✅ **Account ready for deployment**

---

## PART 2: Local Testing (Your Computer)

### Step 2.1: Clone Repository

**Purpose**: Get the code on your computer

```bash
# Open Terminal/PowerShell
# Navigate to where you want the folder
cd Desktop

# Clone the repository
git clone https://github.com/lapejahans-coder/Alerts.git

# Go into the folder
cd Alerts

# Switch to the correct branch
git checkout silver-deck-system
```

✅ **Folder created**: `Alerts/silver-deck-system`

---

### Step 2.2: Install Python Dependencies

**Purpose**: Install required libraries (OANDA client, Telegram, data analysis, etc.)

```bash
# You should be in the Alerts folder
# Create virtual environment (isolated Python setup)
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# You should see (venv) at the start of your terminal line

# Install all dependencies
pip install -r requirements.txt
```

⏳ **This takes 2-3 minutes** (downloading ~200 MB)

✅ **All packages installed**

---

### Step 2.3: Create .env File with Your Credentials

**Purpose**: Store your API tokens safely (local file, never upload to GitHub)

```bash
# Copy the template
cp .env.example .env

# Open .env in your editor (VS Code, Notepad, etc.)
# On Windows: start .env
# On Mac: open .env
# On Linux: nano .env
```

**Edit the .env file with your credentials:**

```env
# OANDA Configuration - From Step 1.1
OANDA_API_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdef
OANDA_ACCOUNT_ID=123456789-001
OANDA_ENVIRONMENT=practice

# Telegram Configuration - From Steps 1.2 & 1.3
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdef
TELEGRAM_CHAT_ID=123456789

# Trading Configuration
MARKET_SYMBOL=XAG_USD
EXECUTION_MODE=practice
ENABLE_EXECUTION=false

# System Configuration
LOG_LEVEL=INFO
ANALYSIS_INTERVAL=300
VERBOSE_MODE=false
```

**Save the file.**

✅ **.env file configured with YOUR credentials**

---

### Step 2.4: Test Telegram Bot

**Purpose**: Verify your Telegram setup works

```bash
# Make sure virtual environment is active (venv)

# Run a quick Python test
python
```

In the Python terminal, type:

```python
import telegram
import asyncio
import os

bot = telegram.Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
async def test():
    await bot.send_message(chat_id=os.getenv('TELEGRAM_CHAT_ID'), text="✅ SILVER DECK is working!")

asyncio.run(test())
print("Message sent!")
exit()
```

**Check Telegram**: You should receive a message on your chat saying "✅ SILVER DECK is working!"

✅ **Telegram integration verified**

---

### Step 2.5: Run SILVER DECK Locally

**Purpose**: Test the entire system before deploying to cloud

```bash
# Make sure you're in the Alerts folder
# Make sure virtual environment is active (venv)

# Run the main application
python main.py
```

**You should see:**

```
════════════════════════════════════════════════════════════════
SILVER DECK - Real-time Silver Futures Analysis Engine
Paper Trading Education Only
════════════════════════════════════════════════════════════════
Configuration: PRACTICE mode
Trading symbol: XAG_USD
Execution enabled: False
All components initialized successfully

--- Analysis Iteration 1 ---
Time: 2026-06-11T14:30:00.123456
Event Risk Status: Safe to trade
Account info fetched successfully
```

**Wait 5 minutes** (ANALYSIS_INTERVAL=300 seconds):

You'll see the first analysis:

```
ANALYSIS RESULT: LONG
Confidence: MEDIUM
Regime: TREND_UP
Scorecard:
  - macro_filter: {'stance': 'BULLISH', ...}
  - momentum: {'score': 'PASS', ...}
  - ...

SIGNAL SENT via Telegram
```

**Check Telegram**: You should receive a signal notification

✅ **Local testing successful!**

---

### Step 2.6: Stop Local Testing

```bash
# Press Ctrl+C to stop
```

---

## PART 3: Deploy to Railway (Cloud 24/7)

### Step 3.1: Install Railway CLI

**Purpose**: Deploy code to Railway from your terminal

```bash
# Install Node.js first if you don't have it
# Download from https://nodejs.org (LTS version)

# Then install Railway CLI
npm install -g @railway/cli

# Verify installation
railway --version
```

✅ **Railway CLI installed**

---

### Step 3.2: Login to Railway

```bash
# This opens a browser window
railway login

# Select "Sign in with GitHub"
# Authorize Railway
# Browser shows: "You are logged in"
```

✅ **Logged into Railway**

---

### Step 3.3: Initialize Railway Project

```bash
# Make sure you're in the Alerts folder
# Make sure you're NOT in the virtual environment (exit venv)

deactivate  # Exit virtual environment

# Initialize Railway project
railway init
```

**Railway asks you questions:**

1. "Would you like to create a new project or select an existing one?"
   - Select: **Create a new project**

2. "Name of the project?"
   - Type: `SILVER DECK` or `silver-deck`

3. "Which plugin would you like to add?"
   - Click "Skip" (we don't need plugins, only Python)

✅ **Railway project created**

---

### Step 3.4: Add Your Credentials to Railway

**Purpose**: Store API tokens securely on Railway (never in GitHub)

```bash
# Set each environment variable
railway variable:set OANDA_API_TOKEN="your_oanda_token_here"
railway variable:set OANDA_ACCOUNT_ID="your_account_id_here"
railway variable:set OANDA_ENVIRONMENT="practice"
railway variable:set TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
railway variable:set TELEGRAM_CHAT_ID="your_telegram_chat_id"
railway variable:set MARKET_SYMBOL="XAG_USD"
railway variable:set EXECUTION_MODE="practice"
railway variable:set ENABLE_EXECUTION="false"
railway variable:set LOG_LEVEL="INFO"
railway variable:set ANALYSIS_INTERVAL="300"
railway variable:set VERBOSE_MODE="false"
```

**Replace**:
- `your_oanda_token_here` → Your actual OANDA token
- `your_account_id_here` → Your actual OANDA Account ID
- `your_telegram_bot_token` → Your actual Telegram bot token
- `your_telegram_chat_id` → Your actual Telegram chat ID

✅ **All credentials stored on Railway**

---

### Step 3.5: Deploy to Railway

```bash
# This uploads your code and starts the service
railway up

# Wait for deployment to complete (2-3 minutes)
# You should see: "✓ Deployment successful"
```

✅ **Code deployed to Railway cloud servers**

---

### Step 3.6: Monitor Deployment

```bash
# View live logs in real-time
railway logs --follow

# You should see:
# SILVER DECK - Real-time Silver Futures Analysis Engine
# Configuration: PRACTICE mode
# All components initialized successfully
# --- Analysis Iteration 1 ---
```

**Wait 5 minutes** for the first analysis.

**Check Telegram**: You should receive a signal!

✅ **SILVER DECK is now running 24/7 on Railway!**

---

## PART 4: Verify Everything Works

### Step 4.1: Check You're Receiving Signals

1. Wait 5-10 minutes
2. Check Telegram for signal notifications
3. Each signal should show:
   - 🟢 **ACTION**: LONG / SHORT / WAIT
   - 📊 **MARKET**: XAG_USD
   - 💰 **PRICE**: Current silver price
   - 🎯 **CONFIDENCE**: HIGH / MEDIUM / LOW
   - 📈 **REGIME**: TREND_UP / TREND_DOWN / etc.

✅ **Signals confirmed**

---

### Step 4.2: View Detailed Logs

```bash
# In your terminal, view Railway logs
railway logs --follow

# You should see detailed analysis output:
# Macro: DXY -0.35%, Gold +0.22%, 10Y Yield -2.5 bps
# MOMENTUM: PASS - MACD bullish, histogram expanding
# RSI: 55.2, VWAP: 31.18, Distance: +0.22%
```

✅ **Analysis running correctly**

---

### Step 4.3: Access Your Dashboard

1. Go to https://railway.app
2. Click on your **SILVER DECK** project
3. View **Deployments** tab (shows running status)
4. View **Logs** tab (real-time output)
5. View **Variables** tab (your credentials - masked)

✅ **Dashboard accessible**

---

## PART 5: Common Setup Issues & Fixes

### Issue: "OANDA API token invalid"

**Solution**:
1. Go to https://developer.oanda.com
2. Log in with your OANDA account
3. Generate a NEW token (old one may have expired)
4. Update on Railway:
   ```bash
   railway variable:set OANDA_API_TOKEN="new_token_here"
   ```
5. Redeploy:
   ```bash
   railway up
   ```

---

### Issue: "No Telegram messages received"

**Solution**:
1. Verify TELEGRAM_BOT_TOKEN is correct:
   ```bash
   railway variable:get TELEGRAM_BOT_TOKEN
   ```
2. Check TELEGRAM_CHAT_ID is correct (just numbers, no special characters)
3. Message your bot on Telegram (send any text)
4. Check logs:
   ```bash
   railway logs --follow
   ```
   Look for "SIGNAL SENT via Telegram" or error messages

---

### Issue: "Service keeps restarting / error logs"

**Solution**:
1. View logs:
   ```bash
   railway logs --follow
   ```
2. Check for missing environment variables
3. Ensure all 11 variables are set:
   ```bash
   railway variable:list
   ```
4. If missing, add them:
   ```bash
   railway variable:set MISSING_VAR="value"
   ```
5. Redeploy:
   ```bash
   railway up
   ```

---

### Issue: "Running locally but not getting signals"

**Solution**:
1. Check ANALYSIS_INTERVAL (default 300 = 5 min)
2. Wait at least 5 minutes before first signal
3. Check macro conditions (if DXY/Gold/Yields are conflicting, system may WAIT)
4. Check economic calendar - if high-impact event is close, system outputs WAIT
5. View logs to see reasoning:
   ```bash
   tail -f logs/silver_deck.log
   ```

---

## PART 6: Using SILVER DECK

### Understanding Signals

**🟢 LONG Signal**
- Buy silver
- Macro bullish (weaker USD, strong gold, falling yields)
- Momentum positive (MACD bullish)
- Price above VWAP
- Event risk safe (no major news)

**🔴 SHORT Signal**
- Sell silver / short
- Macro bearish (stronger USD, weak gold, rising yields)
- Momentum negative (MACD bearish)
- Price below VWAP
- Event risk safe

**🟡 WAIT Signal**
- Don't trade
- System uncertain (conflicting signals)
- Event risk high (CPI/NFP/FOMC coming)
- Session quality low (Asian/overnight hours)
- Not enough data

---

### Paper Trading (Recommended First Step)

1. **Use OANDA Practice Account** (you already have it)
2. Receive SILVER DECK signals via Telegram
3. Manually enter trades in OANDA (don't use automation yet)
4. Track results: entry, exit, profit/loss
5. Journal: what worked, what didn't
6. Run for 1-4 weeks to validate

---

### Enable Automated Execution (Advanced - Not Recommended for Beginners)

**Only after 4+ weeks of successful paper trading:**

```bash
# ONLY change this if you're confident
railway variable:set ENABLE_EXECUTION="true"

# Redeploy
railway up
```

⚠️ **WARNING**: Trades will execute automatically. Start with small position sizes.

---

## PART 7: Daily Monitoring

### Morning Checklist

1. **Check Telegram**: Review overnight signals
2. **Check Silver Price**: Compare to SILVER DECK signals
3. **Review Logs**:
   ```bash
   railway logs --follow
   ```
4. **Check Economic Calendar**: Any events today?

### Weekly Review

1. Count signals generated
2. How many LONG vs SHORT vs WAIT?
3. Compare to actual silver price movement
4. Journal observations
5. Adjust ANALYSIS_INTERVAL if needed

---

## PART 8: Next Steps

### Learn the System

- Read `README.md` - Full documentation
- Read `QUICK_START.md` - Quick reference
- Check `SYSTEM_IMPROVEMENTS.md` - What's included

### Customize (Optional)

1. **Change analysis interval**:
   ```bash
   railway variable:set ANALYSIS_INTERVAL="60"  # 1 minute instead of 5
   ```

2. **Change blocked events**:
   - Edit `config/economic_events.json`
   - Push to GitHub
   - Railway auto-redeploys

3. **Add more alerts**:
   - Modify `src/alerts/telegram_notifier.py`
   - Add Slack, Discord, email
   - Push changes

---

## Summary

✅ **You now have:**

1. **OANDA practice account** - Live silver prices
2. **Telegram bot** - Receive signals on your phone
3. **Local testing** - Code running on your computer
4. **Cloud deployment** - 24/7 SILVER DECK running on Railway
5. **Real-time signals** - LONG/SHORT/WAIT every 5 minutes
6. **Paper trading** - Safe way to test before real money

✅ **Everything is:**

- Automated (no manual checks needed)
- Safe (execution disabled by default)
- Professional (full audit trail & logging)
- Educational (learn macro analysis + risk management)
- Affordable (~$5/month)

---

## Cost Breakdown

| Item | Cost | Notes |
|------|------|-------|
| OANDA Account | Free | Practice mode only |
| Telegram Bot | Free | Unlimited messages |
| Railway.app | ~$2/month | $7/mo plan - $5 credit = $2 actual |
| Yahoo Finance | Free | Macro data |
| **TOTAL** | **~$2/month** | Cheapest trading setup possible |

---

## Support

- **Questions?** Check README.md
- **Errors?** View logs: `railway logs --follow`
- **Feature requests?** Open GitHub issue
- **Want to contribute?** Create pull request

---

## Remember

⚠️ **PAPER TRADING EDUCATION ONLY**

This system is for learning, not real money trading. Even after validation:

- Start with small position sizes
- Never risk more than 1-2% per trade
- Always use stop losses
- Respect risk management rules
- Remember: Past performance ≠ future results

---

**🚀 You're now ready to analyze silver futures like a professional!**

Send your first signal and start paper trading! 📊

**Questions?** Review the full README.md or reach out.
