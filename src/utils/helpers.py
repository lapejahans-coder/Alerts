"""Utility functions for SILVER DECK system."""

import logging
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

class SignalFormatter:
    """Format analysis results for display and notifications."""
    
    @staticmethod
    def format_signal_report(analysis_result: Dict) -> str:
        """Format complete signal report."""
        try:
            action = analysis_result.get('action', 'WAIT').value
            confidence = analysis_result.get('confidence', 'LOW')
            regime = analysis_result.get('regime', 'UNKNOWN')
            current_price = analysis_result.get('current_data', {}).get('current_price', 'N/A')
            
            scorecard = analysis_result.get('scorecard', {})
            macro = scorecard.get('macro_filter', {})
            momentum = scorecard.get('momentum', {})
            rsi_vwap = scorecard.get('rsi_vwap_atr', {})
            volume = scorecard.get('volume_confirmation', {})
            event = scorecard.get('event_risk', {})
            
            report = f"""
═══════════════════════════════════════════════════════════════
🔗 SILVER DECK SIGNAL
═══════════════════════════════════════════════════════════════

ACTION:       {action}
CONFIDENCE:   {confidence}
REGIME:       {regime}
CURRENT:      ${current_price}
TIMESTAMP:    {analysis_result.get('timestamp', 'N/A')}

───────────────────────────────────────────────────────────────
SCORECARD
───────────────────────────────────────────────────────────────

📊 MACRO FILTER
   Stance:     {macro.get('stance', 'NEUTRAL')}
   DXY:        {macro.get('dxy_change_pct', 'N/A'):+.2f}%
   Gold:       {macro.get('gold_change_pct', 'N/A'):+.2f}%
   10Y Yield:  {macro.get('yield_change_bps', 'N/A'):+.1f} bps

📈 MOMENTUM (MACD)
   Score:      {momentum.get('score', 'NEUTRAL')}
   Direction:  {momentum.get('direction', 'FLAT')}
   Histogram:  {momentum.get('histogram_expanding', False)} (expanding)

🎯 RSI + VWAP + ATR
   RSI:        {rsi_vwap.get('rsi', 'N/A'):.1f}
   VWAP:       ${rsi_vwap.get('vwap', 'N/A'):.2f}
   Distance:   {rsi_vwap.get('distance_from_vwap_pct', 0):+.2f}%
   Volatility: {rsi_vwap.get('volatility_status', 'UNKNOWN')}
   Bias:       {rsi_vwap.get('bias', 'NEUTRAL')}

📉 PRICE / VOLUME CONFIRMATION
   Score:      {volume.get('score', 'NEUTRAL')}
   Pattern:    {volume.get('confirmation', 'WEAK')}
   Closes H:   {volume.get('closes_near_highs', 0)}/5
   Closes L:   {volume.get('closes_near_lows', 0)}/5

⚠️  EVENT RISK
   Level:      {event.get('level', 'UNKNOWN')}
   Event:      {event.get('upcoming_event', 'None')}
   Minutes:    {event.get('minutes_to_event', 'N/A')}

═══════════════════════════════════════════════════════════════
"""
            return report
        except Exception as e:
            logger.error(f'Error formatting signal report: {e}')
            return 'Error formatting report'
    
    @staticmethod
    def format_macro_summary(macro_snapshot: Dict) -> str:
        """Format macro snapshot summary."""
        try:
            dxy = macro_snapshot.get('dxy', {})
            gold = macro_snapshot.get('gold', {})
            yield_data = macro_snapshot.get('usdt_10yr', {})
            vix = macro_snapshot.get('vix', 'N/A')
            
            summary = f"""
MACRO CONTEXT
─────────────
DXY:      {dxy.get('price', 'N/A'):.2f} ({dxy.get('change_pct', 0):+.2f}%)
Gold:     ${gold.get('price', 'N/A'):.2f} ({gold.get('change_pct', 0):+.2f}%)
10Y Yld:  {yield_data.get('yield', 'N/A'):.2f}% ({yield_data.get('change_bps', 0):+.1f} bps)
VIX:      {vix}
"""
            return summary
        except Exception as e:
            logger.error(f'Error formatting macro summary: {e}')
            return 'Error formatting macro summary'

class DataValidator:
    """Validate data quality and completeness."""
    
    @staticmethod
    def validate_candles(candles: pd.DataFrame) -> Tuple[bool, str]:
        """Validate candle data."""
        try:
            if candles is None or len(candles) == 0:
                return False, "No candle data available"
            
            required_cols = ['Open', 'High', 'Low', 'Close']
            missing_cols = [col for col in required_cols if col not in candles.columns]
            if missing_cols:
                return False, f"Missing columns: {missing_cols}"
            
            if len(candles) < 14:
                return False, f"Insufficient candles: {len(candles)} < 14"
            
            # Check for NaN values
            if candles[required_cols].isnull().any().any():
                return False, "Contains NaN values"
            
            return True, "Valid"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    @staticmethod
    def validate_macro_snapshot(snapshot: Dict) -> Tuple[bool, str]:
        """Validate macro snapshot."""
        try:
            required_keys = ['dxy', 'gold', 'usdt_10yr', 'vix']
            missing = [k for k in required_keys if k not in snapshot]
            
            if missing:
                return False, f"Missing macro data: {missing}"
            
            # Check if values are reasonable
            dxy = snapshot.get('dxy', {}).get('price')
            if dxy and (dxy < 50 or dxy > 150):  # DXY sanity check
                return False, f"Unrealistic DXY: {dxy}"
            
            return True, "Valid"
        except Exception as e:
            return False, f"Validation error: {e}"

class RiskCalculator:
    """Calculate risk/reward ratios and position sizing."""
    
    @staticmethod
    def calculate_risk_reward(entry: float, stop: float, target: float) -> float:
        """Calculate risk/reward ratio."""
        try:
            if stop == entry or entry == target:
                return 0
            
            risk = abs(entry - stop)
            reward = abs(target - entry)
            
            if risk == 0:
                return 0
            
            return reward / risk
        except Exception as e:
            logger.error(f'Error calculating R/R: {e}')
            return 0
    
    @staticmethod
    def validate_trade_setup(entry: float, stop: float, target: float, 
                             account_size: float = 10000, 
                             risk_pct: float = 1.0) -> Dict:
        """Validate complete trade setup."""
        try:
            risk_reward = RiskCalculator.calculate_risk_reward(entry, stop, target)
            
            if risk_reward < 1.0:
                return {
                    'valid': False,
                    'reason': f'Risk/Reward {risk_reward:.2f}:1 is too low (min 1:1)',
                    'rr': risk_reward
                }
            
            # Calculate position size
            risk_amount = account_size * (risk_pct / 100)
            risk_per_unit = abs(entry - stop)
            units = int(risk_amount / risk_per_unit) if risk_per_unit > 0 else 0
            
            return {
                'valid': True,
                'rr': risk_reward,
                'risk_amount': risk_amount,
                'units': units,
                'total_risk': units * risk_per_unit,
            }
        except Exception as e:
            logger.error(f'Error validating trade setup: {e}')
            return {'valid': False, 'reason': str(e)}

class TimeHelper:
    """Time-related utility functions."""
    
    @staticmethod
    def get_market_session() -> str:
        """Get current market session."""
        import pytz
        from datetime import datetime
        
        et = pytz.timezone('US/Eastern')
        now = datetime.now(et)
        hour = now.hour
        
        if 8 <= hour < 17:
            return 'NY_SESSION'
        elif 3 <= hour < 8:
            return 'LONDON_OVERLAP'
        elif 23 <= hour or hour < 3:
            return 'ASIAN_SESSION'
        else:
            return 'OFF_MARKET'
    
    @staticmethod
    def is_within_trading_hours() -> bool:
        """Check if within COMEX trading hours."""
        import pytz
        from datetime import datetime
        
        et = pytz.timezone('US/Eastern')
        now = datetime.now(et)
        
        # COMEX Silver: Sun 6 PM - Fri 5 PM ET
        weekday = now.weekday()
        hour = now.hour
        
        if weekday >= 5:  # Saturday/Sunday
            if weekday == 5:  # Saturday
                return hour < 5  # Only before 5 PM Friday (markets close)
            else:  # Sunday
                return hour >= 18  # After 6 PM Sunday
        else:  # Weekday
            return 18 <= hour or hour < 17  # 6 PM previous day OR before 5 PM

class PerformanceMetrics:
    """Track system performance metrics."""
    
    def __init__(self):
        self.signals_generated = 0
        self.longs = 0
        self.shorts = 0
        self.waits = 0
        self.high_confidence = 0
        self.medium_confidence = 0
        self.low_confidence = 0
        self.macro_bullish = 0
        self.macro_bearish = 0
        self.macro_neutral = 0
    
    def record_signal(self, action: str, confidence: str, macro_stance: str):
        """Record signal generation."""
        self.signals_generated += 1
        
        if action == 'LONG':
            self.longs += 1
        elif action == 'SHORT':
            self.shorts += 1
        else:
            self.waits += 1
        
        if confidence == 'HIGH':
            self.high_confidence += 1
        elif confidence == 'MEDIUM':
            self.medium_confidence += 1
        else:
            self.low_confidence += 1
        
        if macro_stance == 'BULLISH':
            self.macro_bullish += 1
        elif macro_stance == 'BEARISH':
            self.macro_bearish += 1
        else:
            self.macro_neutral += 1
    
    def get_summary(self) -> Dict:
        """Get summary metrics."""
        total = self.signals_generated
        if total == 0:
            return {'total': 0}
        
        return {
            'total': total,
            'longs': self.longs,
            'shorts': self.shorts,
            'waits': self.waits,
            'high_confidence_pct': (self.high_confidence / total) * 100,
            'macro_bullish_pct': (self.macro_bullish / total) * 100,
            'macro_bearish_pct': (self.macro_bearish / total) * 100,
        }
