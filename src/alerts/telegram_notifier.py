"""Telegram notification system for trading signals."""

import logging
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from src.config import Config

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Send trading signals and alerts via Telegram."""
    
    def __init__(self):
        self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.chat_id = Config.TELEGRAM_CHAT_ID
    
    async def send_signal(self, signal_data: Dict) -> bool:
        """Send a trading signal alert."""
        try:
            message = self._format_signal_message(signal_data)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f'Signal sent via Telegram: {signal_data["ACTION"]}')
            return True
        except TelegramError as e:
            logger.error(f'Telegram error sending signal: {e}')
            return False
    
    async def send_alert(self, title: str, message: str, alert_type: str = 'INFO') -> bool:
        """Send a general alert."""
        try:
            emoji = self._get_emoji(alert_type)
            full_message = f'{emoji} <b>{title}</b>\n\n{message}'
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=full_message,
                parse_mode='HTML'
            )
            logger.info(f'Alert sent via Telegram: {title}')
            return True
        except TelegramError as e:
            logger.error(f'Telegram error sending alert: {e}')
            return False
    
    def _format_signal_message(self, signal_data: Dict) -> str:
        """Format signal data for Telegram message."""
        message = f"""<b>🎯 SILVER DECK SIGNAL</b>

<b>Action:</b> {signal_data.get('ACTION', 'WAIT')}
<b>Market:</b> {signal_data.get('MARKET', 'XAG_USD')}
<b>Price:</b> ${signal_data.get('PRICE', 'N/A')}
<b>Confidence:</b> {signal_data.get('CONFIDENCE', 'N/A')}
<b>Regime:</b> {signal_data.get('REGIME', 'N/A')}

<b>Entry Plan:</b>
├─ Entry: ${signal_data.get('ENTRY', {}).get('price', 'N/A')}
├─ Stop: ${signal_data.get('ENTRY', {}).get('stop', 'N/A')}
├─ Target 1: ${signal_data.get('ENTRY', {}).get('target1', 'N/A')}
├─ Target 2: ${signal_data.get('ENTRY', {}).get('target2', 'N/A')}
└─ Risk/Reward: {signal_data.get('ENTRY', {}).get('risk_reward', 'N/A')}

<b>Macro:</b> {signal_data.get('SCORECARD', {}).get('macro', 'N/A')}

#SilverFutures #XAG_USD #TradingSignal
"""
        return message
    
    def _get_emoji(self, alert_type: str) -> str:
        """Get emoji for alert type."""
        emojis = {
            'LONG': '🟢',
            'SHORT': '🔴',
            'WAIT': '🟡',
            'ERROR': '⚠️',
            'INFO': 'ℹ️',
            'SUCCESS': '✅'
        }
        return emojis.get(alert_type, 'ℹ️')
