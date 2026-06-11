# QUICK_START.md

## SILVER DECK - Quick Start Guide

Get running in 10 minutes.

---

## 1. Clone Repository

```bash
git clone https://github.com/lapejahans-coder/Alerts.git
cd Alerts
git checkout silver-deck-system
```

---

## 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 3. Configure .env

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# OANDA (get from https://developer.oanda.com)
OANDA_API_TOKEN=your_token_here
OANDA_ACCOUNT_ID=your_account_here
OANDA_ENVIRONMENT=practice

# Telegram (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Trading
MARKET_SYMBOL=XAG_USD
EXECUTION_MODE=practice
ENABLE_EXECUTION=false

# System
ANALYSIS_INTERVAL=300
LOG_LEVEL=INFO
```

---

## 4. Get Credentials

### OANDA API Token

1. Go to https://developer.oanda.com
2. Log in with your OANDA account
3. Create a practice account if needed
4. Go to Account Settings → Access Tokens
5. Generate new token → copy to `.env`

### Telegram Bot

1. Message @BotFather on Telegram
2. Send `/newbot`
3. Choose a name (e.g., "SilverDeck")
4. Get your token → copy to `.env`
5. Message your bot once
6. Get your chat ID from @userinfobot
7. Copy chat ID to `.env`

---

## 5. Run Locally

```bash
python main.py
```

You should see:
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
```

After 5 minutes (or your ANALYSIS_INTERVAL), you'll get a signal:

```
ANALYSIS RESULT: LONG
Confidence: MEDIUM
Regime: TREND_UP
Scorecard:
  - macro_filter: {'stance': 'BULLISH', ...}
  - momentum: {'score': 'PASS', ...}
  - ...
```

You should receive a Telegram notification.

---

## 6. Deploy to Railway (Optional)

For 24/7 cloud hosting:

```bash
npm install -g @railway/cli
railway login
railway init

# Set environment variables
railway variable:set OANDA_API_TOKEN=xxx
railway variable:set OANDA_ACCOUNT_ID=xxx
railway variable:set TELEGRAM_BOT_TOKEN=xxx
railway variable:set TELEGRAM_CHAT_ID=xxx

# Deploy
railway up

# Monitor
railway logs --follow
```

See `DEPLOYMENT_GUIDE.md` for full instructions.

---

## 7. Understanding Signals

### Signal Types

**LONG** - Buy signal
- Macro bullish (weaker USD, strong gold, falling yields)
- Momentum bullish (MACD crossover, expanding histogram)
- Confirmation present (strong closes, price above VWAP)
- Event risk safe (no major news nearby)

**SHORT** - Sell signal
- Macro bearish (stronger USD, weak gold, rising yields)
- Momentum bearish (MACD crossover down, expanding histogram)
- Confirmation present (weak closes, price below VWAP)
- Event risk safe (no major news nearby)

**WAIT** - No trade
- Conflicting signals
- Event risk high (CPI, NFP, FOMC coming)
- Low session quality (overnight/Asian hours)
- Insufficient data

### Confidence Levels

- **HIGH**: All factors aligned → trade with normal risk
- **MEDIUM**: Most factors aligned → reduce position size
- **LOW**: Conflicting signals → avoid trading

---

## 8. Key Concepts

### 8-Step Analysis

1. **Macro Filter**: DXY, Gold, Yields (most important)
2. **Session Quality**: Are we in active trading hours?
3. **Regime**: Trend, range, or breakout?
4. **Momentum**: Is MACD bullish/bearish?
5. **RSI/VWAP/ATR**: Is price extended or balanced?
6. **Volume/Price Confirmation**: Do candles confirm the setup?
7. **Event Risk**: Any major economic news coming?
8. **Confidence**: Do all factors align?

### Blocked Economic Events

Automatically outputs WAIT during:
- **High Impact**: CPI, NFP (30 min before/after)
- **Critical**: FOMC, Powell (60 min before/after)

Full calendar in `config/economic_events.json`.

---

## 9. Troubleshooting

### No signals generated?

Normal - SILVER DECK is designed to WAIT unless setup is very strong.

**Check**:
- Logs for errors
- Macro context (DXY, Gold, yields)
- Current session quality
- Upcoming economic events

### Telegram notifications not working?

1. Verify TELEGRAM_BOT_TOKEN in `.env`
2. Message your bot on Telegram
3. Check TELEGRAM_CHAT_ID is correct
4. Test: `curl -X POST "https://api.telegram.org/botYOUR_TOKEN/sendMessage" -d "chat_id=YOUR_CHAT_ID&text=Test"`

### OANDA API errors?

1. Verify OANDA_API_TOKEN is correct (get fresh from developer portal)
2. Check OANDA_ACCOUNT_ID matches account
3. Ensure practice account is funded
4. Check rate limits: increase ANALYSIS_INTERVAL if needed

---

## 10. Next Steps

### Learning

1. Run for 1 week, observe signals
2. Document macro conditions when each signal fires
3. Compare signals to actual price action
4. Understand why SILVER DECK says WAIT (usually correct!)

### Trading

1. **Paper trade first**: Don't enable ENABLE_EXECUTION yet
2. **Use OANDA demo**: Test entries/exits manually
3. **Journal everything**: Price action, trade results, lessons
4. **Review monthly**: What worked? What didn't?

### Advanced

1. Adjust ANALYSIS_INTERVAL for faster signals
2. Customize blocked events in `config/economic_events.json`
3. Add alerts to Slack/Discord (modify telegram_notifier.py)
4. Log trades to database (add PostgreSQL integration)

---

## 11. Important Rules

✅ **ALWAYS**:
- Start in PRACTICE mode
- Keep ENABLE_EXECUTION=false initially
- Review logs daily
- Monitor Telegram notifications
- Respect blocked economic events

❌ **NEVER**:
- Trade during WAIT signals
- Risk more than 1-2% per trade
- Use live mode without paper trading first
- Ignore event risk warnings
- Trade major pairs without macro context

---

## 12. Support

- **Questions**: Check README.md or DEPLOYMENT_GUIDE.md
- **Errors**: Search logs/ directory for details
- **Improvements**: Open GitHub issue with details
- **Feature requests**: Discuss in GitHub discussions

---

## 13. Resources

- OANDA API Docs: https://developer.oanda.com/rest-live-v20/
- TA-Lib Guide: https://ta-lib.org/
- Economic Calendar: https://investing.com/economic-calendar
- Telegram Bot API: https://core.telegram.org/bots/api

---

**Ready to analyze silver?** Run `python main.py` and wait for your first signal! 🚀

**Remember**: This is for PAPER TRADING EDUCATION ONLY. Do not risk real money until you've validated the system extensively.
