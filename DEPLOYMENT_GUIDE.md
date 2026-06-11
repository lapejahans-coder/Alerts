# DEPLOYMENT_GUIDE.md

## Deploying SILVER DECK to Railway.app

### Prerequisites

- Railway.app account (paid tier recommended for 24/7 uptime)
- GitHub account with repository access
- OANDA API credentials
- Telegram Bot Token and Chat ID
- Node.js + npm (for Railway CLI)

---

## Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

Or use the Railway Dashboard UI (no CLI needed).

---

## Step 2: Authenticate with Railway

```bash
railway login
```

This opens a browser window for authentication.

---

## Step 3: Create Project on Railway

### Option A: Via CLI

```bash
cd your-alerts-repo
railway init
```

Choose:
- Create a new project
- Name: "Silver Deck" or similar
- Select Python as the service

### Option B: Via Dashboard

1. Go to [railway.app](https://railway.app)
2. Click "Create Project"
3. Select "Deploy from GitHub"
4. Connect your GitHub account
5. Select `lapejahans-coder/Alerts` repository
6. Select branch: `silver-deck-system`
7. Configure environment variables (next step)

---

## Step 4: Configure Environment Variables

### Via CLI

```bash
railway variable:set OANDA_API_TOKEN=your_token_here
railway variable:set OANDA_ACCOUNT_ID=your_account_id
railway variable:set OANDA_ENVIRONMENT=practice
railway variable:set TELEGRAM_BOT_TOKEN=your_bot_token
railway variable:set TELEGRAM_CHAT_ID=your_chat_id
railway variable:set MARKET_SYMBOL=XAG_USD
railway variable:set EXECUTION_MODE=practice
railway variable:set ENABLE_EXECUTION=false
railway variable:set LOG_LEVEL=INFO
railway variable:set ANALYSIS_INTERVAL=300
railway variable:set VERBOSE_MODE=false
```

### Via Dashboard

1. Go to your project on Railway.app
2. Click on the service
3. Go to "Variables" tab
4. Add each variable from the .env.example file
5. Make sure `ENABLE_EXECUTION=false` for practice mode

---

## Step 5: Deploy

### Via CLI

```bash
railway up
```

This deploys the code from your GitHub repository.

### Via Dashboard

Railway automatically deploys when you push to the selected branch.

To trigger manual deployment:
1. Go to Deployments tab
2. Click "Deploy" button

---

## Step 6: Monitor Deployment

### View Logs

```bash
railway logs --follow
```

Or via Dashboard:
1. Select your service
2. Go to "Logs" tab
3. Watch real-time output

### Check Status

```bash
railway status
```

---

## Step 7: Verify Telegram Notifications

1. Open Telegram and message your bot
2. Wait for the first scheduled analysis (5 minutes from deployment)
3. You should receive a signal notification

Example message:
```
🔗 SILVER DECK SIGNAL
Action: LONG
Market: XAG_USD
Price: 31.25
Confidence: MEDIUM
Regime: TREND_UP
```

---

## Step 8: Production Settings (Optional)

### Enable Live Trading (ADVANCED)

**⚠️ WARNING: Only after extensive paper trading validation**

1. Create a new OANDA live account (not recommended for beginners)
2. Update variables:
   ```bash
   railway variable:set OANDA_ENVIRONMENT=live
   railway variable:set EXECUTION_MODE=live
   railway variable:set ENABLE_EXECUTION=true
   ```
3. Deploy and monitor carefully
4. Start with small position sizes

### Increase Analysis Frequency

For more frequent signals (default 5 min):

```bash
railway variable:set ANALYSIS_INTERVAL=60  # 1 minute
```

Note: Shorter intervals = higher CPU usage

---

## Troubleshooting

### Build Fails

**Problem**: "Python version not supported"

**Solution**:
Add `runtime.txt` to repo root:
```
python-3.11.x
```

### Service Won't Start

**Problem**: Exit code 1 or service keeps restarting

**Solution**:
1. Check logs: `railway logs --follow`
2. Look for missing environment variables
3. Verify all required vars are set
4. Check OANDA API token is correct

### No Telegram Notifications

**Problem**: Bot token works locally but not on Railway

**Solution**:
1. Test from Railway shell:
   ```bash
   railway shell
   python -c "import telegram; print('OK')"
   ```
2. Verify TELEGRAM_BOT_TOKEN is set correctly
3. Check Telegram bot still active

### High Memory Usage

**Problem**: Service uses >512 MB memory

**Solution**:
1. Increase ANALYSIS_INTERVAL (fewer analyses = less memory)
2. Reduce candle history (fewer candles in memory)
3. Upgrade to Railway Pro plan for more resources

### API Rate Limiting

**Problem**: "429 Too Many Requests" from OANDA

**Solution**:
1. Increase ANALYSIS_INTERVAL
2. Reduce number of candles fetched
3. Contact OANDA support for higher rate limits

---

## Cost Management

### Railway Pricing

- **Free tier**: ~$5 credit/month (not enough for 24/7)
- **Hobby plan**: $7/month (includes $5 credit, so ~$2 actual cost)
- **Pro plan**: Pay-as-you-go, typically $5-20/month for trading bot

### Optimize Costs

1. **Increase analysis interval**: 5 min → 10 min = 50% less computation
2. **Disable non-essential logs**: Set LOG_LEVEL=WARNING
3. **Use Railway's free tier for testing**: Deploy to free tier first
4. **Monitor usage**: Railway Dashboard → Usage tab

---

## GitHub Integration

### Auto-Deploy on Push

Once connected, Railway automatically deploys when you push to `silver-deck-system` branch.

```bash
git add .
git commit -m "Update SILVER DECK configuration"
git push origin silver-deck-system
```

Railway detects the push and redeploys automatically (~2 min delay).

### Rollback to Previous Deployment

Via Dashboard:
1. Go to Deployments
2. Click on previous deployment
3. Click "Rollback" button

This redeploys the previous version without code changes.

---

## Advanced Configuration

### Custom Domain (Optional)

If you want to expose an API endpoint:

1. Go to Service Settings
2. Click "Generate Domain"
3. Add custom domain (requires DNS configuration)

### Database Integration (Optional)

For persistent trade logging:

1. Add PostgreSQL plugin from Railway Marketplace
2. Update code to connect: `postgresql://user:pass@host:port/db`
3. Deploy

### Webhook Notifications

Instead of Telegram, post signals to external service:

1. Update `src/alerts/` to include HTTP webhook notifier
2. Set webhook URL in environment variable
3. Deploy

---

## Maintenance

### Regular Checks

- **Daily**: Review logs for errors
- **Weekly**: Verify Telegram notifications received
- **Monthly**: Check Railway billing and resource usage
- **Quarterly**: Review and update trading rules

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

Then commit and push:

```bash
git add requirements.txt
git commit -m "Update dependencies"
git push origin silver-deck-system
```

---

## Scaling

### When to Scale Up

If you experience:
- Memory warnings in logs
- Slow response times
- Analysis taking >30 seconds

**Solution**: Upgrade to Railway Pro plan

### Horizontal Scaling

For multiple symbols (not recommended for education):

1. Deploy separate instances per symbol
2. Each instance monitors one market
3. Centralized Telegram channel for all signals

---

## Security Best Practices

✅ **DO**:
- Keep API tokens in environment variables (never in code)
- Rotate tokens quarterly
- Use "practice" mode by default
- Review logs for suspicious activity
- Keep ENABLE_EXECUTION=false unless actively trading

❌ **DON'T**:
- Commit `.env` file to GitHub
- Share Railway URL publicly
- Use same token across multiple projects
- Enable execution on untested strategies
- Deploy from random branches

---

## Support

- **Railway Docs**: https://docs.railway.app
- **OANDA API Issues**: https://developer.oanda.com
- **Telegram Bot Issues**: https://core.telegram.org/bots/api-sdk
- **GitHub Issues**: Create issue in your repository

---

## Next Steps After Deployment

1. **Monitor for 24 hours**: Watch for errors, verify signals
2. **Paper trade signals**: Use OANDA demo to test entries
3. **Review performance**: Check logs daily for first week
4. **Adjust parameters**: Fine-tune analysis_interval, block windows
5. **Document results**: Keep journal of signals vs. actual price action
6. **Plan expansion**: Consider adding more symbols or features

---

**Last Updated**: 2026-06-11
**Status**: Production Ready
