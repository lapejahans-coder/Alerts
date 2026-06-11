# SILVER DECK - Real-Time Silver Futures Analysis Engine

**Status**: PAPER TRADING EDUCATION ONLY  
**Market**: XAG/USD (Silver via OANDA)  
**Framework**: Python + OANDA API + Yahoo Finance + Telegram  
**Deployment**: Railway.app (Paid Tier)

---

## Overview

SILVER DECK is a professional-grade real-time analysis engine designed specifically for **paper trading education** in COMEX Silver futures (XAG/USD via OANDA). It executes a rigorous 8-step analysis process that combines macro context, technical structure, momentum, and event risk management.

### Key Features

✅ **Real-Time Analysis**: 8-step SILVER DECK methodology  
✅ **Macro Integration**: DXY, Treasury yields, Gold, VIX via Yahoo Finance  
✅ **OANDA API Integration**: Live pricing & optional trade execution (disabled by default)  
✅ **Telegram Alerts**: Real-time signal notifications  
✅ **Economic Events Calendar**: 2026 blocked events with configurable windows  
✅ **Professional Logging**: Structured logs for audit trail  
✅ **Practice-First**: All defaults set to paper trading (practice mode, execution disabled)  

---

## Architecture

```
SILVER DECK/
├── src/
│   ├── __init__.py
│   ├── config.py                    # Configuration management
│   ├── data_providers/
│   │   ├── oanda_client.py         # OANDA v20 REST API client
│   │   └── yahoo_finance.py        # Macro data (DXY, Gold, yields)
│   ├── analysis/
│   │   ├── silver_deck_analyzer.py # 8-step analysis engine
│   │   └── events_manager.py       # Economic events & blocked windows
│   └── alerts/
│       └── telegram_notifier.py    # Telegram notifications
├── config/
│   └── economic_events.json        # 2026 blocked events (complete)
├── logs/                           # Application logs
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── railway.toml                    # Railway deployment config
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

---

## 8-Step SILVER DECK Analysis

### Step 1: Pull Current Data
- Fetch live XAG/USD price (bid/ask)
- Session high/low
- Overnight high/low  
- **Rule**: If data missing/stale → WAIT

### Step 2: Macro Filter (Most Important)
- **DXY**: Weaker dollar = bullish for Silver
- **Gold**: Leading indicator for Silver
- **10Y Yields**: Rising yields = bearish for Silver
- **VIX**: Elevated = safe-haven demand (bullish)
- **Output**: BULLISH / BEARISH / NEUTRAL

### Step 3: Session Quality
- HIGH: 8 AM - 5 PM ET (US/COMEX hours)
- MEDIUM: 3 AM - 8 AM ET (London overlap)
- LOW: 5 PM - 3 AM ET (thin overnight)
- **Rule**: LOW quality reduces confidence by 1 level

### Step 4: Regime
- TREND_UP: Higher highs + higher lows
- TREND_DOWN: Lower highs + lower lows
- RANGE: Oscillating between levels
- BREAKOUT: Breaking above structure
- BREAKDOWN: Breaking below structure
- CHOPPY: Headline-driven, no clear direction
- **Rule**: Don't fade strong trends

### Step 5: Momentum (MACD)
- Check MACD line vs Signal line
- Histogram expanding = momentum strengthening
- Crossovers = trend changes
- **Score**: PASS / FAIL / NEUTRAL

### Step 6: RSI + VWAP + ATR
- RSI > 70 + extended above VWAP + elevated ATR = short candidate
- RSI < 30 + extended below VWAP + elevated ATR = long candidate
- **Rule**: RSI alone is NOT enough - need VWAP stretch + volatility context

### Step 7: Price/Volume Confirmation
- Strong closes near highs = bullish confirmation
- Strong closes near lows = bearish confirmation
- Breakout without follow-through = suspect
- **Score**: PASS / FAIL / NEUTRAL

### Step 8: Event Risk
- Check against 2026 economic calendar
- Block 30-60 min before/after HIGH/CRITICAL events
- If HIGH-impact event near → WAIT
- **Rule**: Event risk = UNSAFE → WAIT (always)

---

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- OANDA account (demo/practice)
- Telegram Bot Token
- Railway.app account (paid tier)

### 2. Clone & Install

```bash
git clone https://github.com/lapejahans-coder/Alerts.git
cd Alerts

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# OANDA Configuration
OANDA_API_TOKEN=your_oanda_api_token_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here
OANDA_ENVIRONMENT=practice  # or 'live' for real trading

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Trading Configuration
MARKET_SYMBOL=XAG_USD
EXECUTION_MODE=practice
ENABLE_EXECUTION=false  # Set to 'true' only for live trading

# System Configuration
LOG_LEVEL=INFO
ANALYSIS_INTERVAL=300  # seconds (5 minutes)
VERBOSE_MODE=false
```

### 4. Create Telegram Bot

1. Message @BotFather on Telegram
2. `/newbot` → choose name → get token
3. Message your bot once to enable chat history
4. Get your CHAT_ID from @userinfobot or `/start` in your bot

### 5. Get OANDA Credentials

1. Open [OANDA developer portal](https://developer.oanda.com)
2. Log in with your OANDA account
3. Create API token in Account Settings
4. Get your Account ID from dashboard

### 6. Run Locally (Testing)

```bash
python main.py
```

### 7. Deploy to Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variable:set OANDA_API_TOKEN=xxx
railway variable:set OANDA_ACCOUNT_ID=xxx
railway variable:set TELEGRAM_BOT_TOKEN=xxx
railway variable:set TELEGRAM_CHAT_ID=xxx
railway variable:set ENABLE_EXECUTION=false

# Deploy
railway up

# View logs
railway logs
```

---

## Economic Events Calendar (2026)

All blocked events are pre-configured in `config/economic_events.json`:

### Blocked 30-60 Minutes Before/After:

**High Impact (Monthly)**:
- NFP (Non-Farm Payrolls) - 1st Friday, 8:30 AM ET
- CPI (Consumer Price Index) - 2nd week, 8:30 AM ET

**Critical Impact (8x per year)**:
- FOMC Decision & Powell Press Conference - 2:00 PM ET

**Medium Impact**:
- ISM Manufacturing/Services PMI
- Initial Jobless Claims (weekly)
- Retail Sales
- PPI (Producer Price Index)
- Core PCE (Fed's inflation target)

**Special Events**:
- ECB, BOE, BOJ decisions (regional impact on cross rates)
- Fed blackout periods (1 week before FOMC)

---

## Trading Rules

### Confidence Levels

**HIGH**: All factors align (macro + momentum + confirmation + safe event risk + HIGH session quality)
- Entry allowed with tight risk management

**MEDIUM**: Most factors align, one mixed  
- Proceed with caution, reduced position size

**LOW**: Multiple mixed factors or weak session quality  
- **OUTPUT: WAIT** (unless setup is exceptional)

### Entry Rules

Any trade must have:

1. **Clear trigger** - Specific price level or pattern
2. **Logical stop** - Based on structure, not arbitrary
3. **Risk/Reward** - Minimum 1:2 preferred
4. **Time invalidation** - Max N bars at resistance/support
5. **Setup reason** - Continuation vs. mean reversion vs. breakout

### Exit Rules

- **Take Profit**: Partial profit at 1:1 RR, let runner go for 1:3 RR
- **Stop Loss**: Hard stop below structure invalidation
- **Time-based**: Exit if no progress after N bars
- **Macro reversal**: Exit if major macro driver reverses

---

## Allowed Setups

Choose **ONE** per signal:

1. **Breakout Continuation LONG** - Price breaks above resistance with momentum
2. **Breakout Continuation SHORT** - Price breaks below support with momentum
3. **Pullback LONG** - Pullback within uptrend, buy support
4. **Pullback SHORT** - Pullback within downtrend, sell resistance
5. **Mean Reversion LONG** - Oversold extreme (RSI < 30, extended below VWAP)
6. **Mean Reversion SHORT** - Overbought extreme (RSI > 70, extended above VWAP)
7. **WAIT** - If no clear setup or event risk elevated

---

## Signal Output Format

```
═══════════════════════════════════════
SILVER FUTURES SIGNAL
═════════════════════════════════���═════
ACTION: LONG / SHORT / WAIT
MARKET: XAG_USD
PRICE: 31.25
SESSION: HIGH
REGIME: TREND_UP
SETUP TYPE: BREAKOUT
CONFIDENCE: HIGH

ENTRY PLAN
- Entry: 31.26
- Stop: 31.15
- Target 1: 31.50
- Target 2: 31.75
- Risk/Reward: 1:2.2

SCORECARD
- Macro Filter: BULLISH — DXY weak, Gold strength, yields falling
- Momentum: PASS — MACD bullish crossover with expanding histogram
- RSI + VWAP + ATR: PASS — Price above VWAP, RSI 55 (balanced), normal volatility
- Price/Volume Confirmation: PASS — Strong closes above prior highs
- Event Risk: SAFE — No major events in next 4 hours

REASONING
[2-4 sentences]

EXIT TRIGGERS
[Conditions for profit-taking and early exit]

INVALIDATION
[Exact conditions that invalidate the trade]

NEWS IMPACT
[Most relevant macro headline]
```

---

## Telegram Notifications

Receive:

✅ **Trading Signals** - LONG / SHORT / WAIT decisions  
✅ **Macro Updates** - DXY, Gold, Yield changes  
✅ **Event Alerts** - Upcoming high-impact economic events  
✅ **Error Logs** - Critical system errors  

---

## Logging & Audit Trail

All analysis results logged to `logs/silver_deck.log`:

```
2026-06-11 14:30:00 - ANALYSIS: Action=LONG, Confidence=HIGH
2026-06-11 14:30:01 - MACRO: DXY -0.35%, Gold +0.22%, 10Y Yield -2.5 bps
2026-06-11 14:30:02 - MOMENTUM: PASS - MACD bullish, histogram expanding
2026-06-11 14:30:03 - RSI: 55.2, VWAP: 31.18, Distance: +0.22%
2026-06-11 14:30:04 - SIGNAL SENT via Telegram
```

---

## Performance & Deployment

### Railway Configuration

- **Plan**: Paid tier (minimum ~$5/month for 24/7 uptime)
- **Runtime**: Always-on 24/5 (markets close weekends)
- **Scaling**: Auto-sleep disabled
- **Logs**: Streamed to Railway dashboard
- **Health Check**: Manual restart if needed

### System Requirements

- **Memory**: ~256 MB (base) + ~100 MB per analysis loop
- **CPU**: Minimal (only analysis every 5 minutes)
- **Network**: ~1 API call/5 min = ~8 KB/day = negligible bandwidth

### Cost Breakdown (Monthly)

- Railway.app: ~$5
- OANDA API: Free (practice)
- Yahoo Finance: Free
- Telegram: Free
- **Total**: ~$5/month

---

## Disclaimer

⚠️ **PAPER TRADING EDUCATION ONLY**

This system is designed for educational purposes and PAPER TRADING ONLY.

- **NOT financial advice** - Do not use for real-money trading without professional guidance
- **No guarantees** - Markets are unpredictable; past performance ≠ future results
- **Educational tool** - Learn risk management, technical analysis, macro context
- **Enable execution only after extensive paper trading validation**
- **All trades should be simulated first** using OANDA practice mode

---

## Support & Troubleshooting

### Issue: WAIT signal constantly

**Causes**:
- Event risk = UNSAFE (check economic calendar)
- Session quality = LOW (Asian/overnight hours)
- Macro filter = NEUTRAL (conflicting signals)
- Volatility elevated

**Solution**: Wait for better macro setup + HIGH session quality

### Issue: No Telegram messages

**Causes**:
- Token/Chat ID incorrect
- Internet connection issue
- Bot not started

**Solution**:
1. Test bot: `curl -X GET "https://api.telegram.org/botYOUR_TOKEN/getMe"`
2. Send test message in chat
3. Check logs: `tail -f logs/silver_deck.log`

### Issue: OANDA API errors

**Causes**:
- Invalid token (expired or wrong account)
- Rate limiting (too many requests)
- Account not funded (practice)

**Solution**:
1. Verify token at OANDA developer portal
2. Check account balance
3. Increase `ANALYSIS_INTERVAL` if rate-limited

---

## Contributing

To improve SILVER DECK:

1. Test on paper trading only
2. Document changes in commit messages
3. Submit pull requests with clear explanations
4. Update `.env.example` if adding new config
5. Update `README.md` with significant changes

---

## License

Educational use only. See LICENSE file.

---

## Additional Resources

- [OANDA Developer Documentation](https://developer.oanda.com/rest-live-v20/introduction/)
- [Yahoo Finance API](https://finance.yahoo.com)
- [Railway.app Docs](https://docs.railway.app)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Technical Analysis Library (TA-Lib)](https://ta-lib.org/)

---

**Last Updated**: 2026-06-11  
**Version**: 1.0.0  
**Status**: Active Development  

