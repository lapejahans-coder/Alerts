"""SILVER DECK Core Analysis Engine - Multi-step technical and macro analysis."""

import logging
from typing import Dict, Tuple, Optional
from datetime import datetime
from enum import Enum
import pandas as pd
import numpy as np
from talib import MACD, RSI, ATR, BBANDS

logger = logging.getLogger(__name__)

class SignalAction(Enum):
    """Trading signal actions."""
    LONG = "LONG"
    SHORT = "SHORT"
    WAIT = "WAIT"

class SilverDeckAnalyzer:
    """Core SILVER DECK analysis engine following all 8 steps."""
    
    def __init__(self, macro_provider, oanda_client):
        self.macro_provider = macro_provider
        self.oanda_client = oanda_client
        self.analysis_results = {}
    
    def analyze(self, candles: pd.DataFrame, macro_snapshot: Dict) -> Dict:
        """Execute complete 8-step analysis."""
        
        # STEP 1: Pull current data
        current_data = self._step_1_pull_current_data(candles)
        
        # STEP 2: Macro filter
        macro_filter = self._step_2_macro_filter(macro_snapshot)
        
        # STEP 3: Session quality
        session_quality = self._step_3_session_quality()
        
        # STEP 4: Regime
        regime = self._step_4_regime(candles)
        
        # STEP 5: Momentum
        momentum_score = self._step_5_momentum(candles)
        
        # STEP 6: RSI + VWAP + ATR
        rsi_vwap_atr = self._step_6_rsi_vwap_atr(candles)
        
        # STEP 7: Price/Volume Confirmation
        volume_confirmation = self._step_7_price_volume_confirmation(candles)
        
        # STEP 8: Event Risk
        event_risk = self._step_8_event_risk()
        
        # Calculate confidence and determine action
        confidence, action = self._calculate_confidence_and_action(
            macro_filter, momentum_score, rsi_vwap_atr, 
            volume_confirmation, event_risk, session_quality, regime
        )
        
        # Build comprehensive result
        result = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'confidence': confidence,
            'current_data': current_data,
            'scorecard': {
                'macro_filter': macro_filter,
                'momentum': momentum_score,
                'rsi_vwap_atr': rsi_vwap_atr,
                'volume_confirmation': volume_confirmation,
                'event_risk': event_risk,
            },
            'session_quality': session_quality,
            'regime': regime,
            'macro_snapshot': macro_snapshot,
        }
        
        self.analysis_results = result
        return result
    
    def _step_1_pull_current_data(self, candles: pd.DataFrame) -> Dict:
        """Step 1: Pull current market data."""
        try:
            price_data = self.oanda_client.get_current_price()
            if not price_data or not candles or len(candles) == 0:
                return {'status': 'DATA_MISSING', 'action': 'WAIT'}
            
            current_price = price_data['mid']
            current_bid = price_data['bid']
            current_ask = price_data['ask']
            
            # Extract OHLC data
            session_high = float(candles['Close'].max())
            session_low = float(candles['Close'].min())
            
            data = {
                'current_price': current_price,
                'bid': current_bid,
                'ask': current_ask,
                'spread': price_data['spread'],
                'session_high': session_high,
                'session_low': session_low,
                'timestamp': datetime.now().isoformat(),
                'status': 'OK'
            }
            
            logger.info(f'Current price: {current_price}, Session H/L: {session_high}/{session_low}')
            return data
        except Exception as e:
            logger.error(f'Error in Step 1: {e}')
            return {'status': 'ERROR', 'action': 'WAIT'}
    
    def _step_2_macro_filter(self, macro_snapshot: Dict) -> Dict:
        """Step 2: Macro filter - DXY, yields, gold, inflation."""
        try:
            dxy_change = macro_snapshot.get('dxy', {}).get('change_pct', 0)
            gold_change = macro_snapshot.get('gold', {}).get('change_pct', 0)
            yield_change_bps = macro_snapshot.get('usdt_10yr', {}).get('change_bps', 0)
            
            bullish_signals = 0
            bearish_signals = 0
            
            # Weaker DXY is bullish for Silver
            if dxy_change is not None and dxy_change < -0.2:
                bullish_signals += 2
            elif dxy_change is not None and dxy_change > 0.5:
                bearish_signals += 2
            
            # Gold direction (leading indicator for Silver)
            if gold_change is not None and gold_change > 0.3:
                bullish_signals += 2
            elif gold_change is not None and gold_change < -0.3:
                bearish_signals += 2
            
            # Rising yields are bearish for Silver
            if yield_change_bps is not None and yield_change_bps > 3:
                bearish_signals += 2
            elif yield_change_bps is not None and yield_change_bps < -3:
                bullish_signals += 2
            
            if bullish_signals > bearish_signals + 1:
                macro_stance = 'BULLISH'
                confidence_boost = 'HIGH'
            elif bearish_signals > bullish_signals + 1:
                macro_stance = 'BEARISH'
                confidence_boost = 'HIGH'
            else:
                macro_stance = 'NEUTRAL'
                confidence_boost = 'LOW'
            
            return {
                'stance': macro_stance,
                'confidence': confidence_boost,
                'dxy_change_pct': dxy_change,
                'gold_change_pct': gold_change,
                'yield_change_bps': yield_change_bps,
            }
        except Exception as e:
            logger.error(f'Error in Step 2 (Macro): {e}')
            return {'stance': 'NEUTRAL', 'confidence': 'LOW'}
    
    def _step_3_session_quality(self) -> str:
        """Step 3: Determine session quality based on time of day."""
        try:
            from datetime import datetime
            import pytz
            
            et = pytz.timezone('US/Eastern')
            now = datetime.now(et)
            hour = now.hour
            
            # Active US/COMEX hours: 8 AM - 5 PM ET
            if 8 <= hour < 17:
                return 'HIGH'
            # London overlap: 3 AM - 8 AM ET
            elif 3 <= hour < 8:
                return 'MEDIUM'
            # Overnight/Asian: 5 PM - 3 AM ET
            else:
                return 'LOW'
        except Exception as e:
            logger.error(f'Error in Step 3: {e}')
            return 'UNKNOWN'
    
    def _step_4_regime(self, candles: pd.DataFrame) -> str:
        """Step 4: Identify current regime (trend/range/breakout)."""
        try:
            if len(candles) < 15:
                return 'INSUFFICIENT_DATA'
            
            # Get 15-minute and 1-hour data
            closes = candles['Close'].values
            
            # Calculate higher highs / higher lows
            recent = closes[-15:]
            mid = closes[-30:-15] if len(closes) >= 30 else closes[:15]
            
            recent_high = np.max(recent)
            recent_low = np.min(recent)
            mid_high = np.max(mid)
            mid_low = np.min(mid)
            
            if recent_high > mid_high and recent_low > mid_low:
                return 'TREND_UP'
            elif recent_high < mid_high and recent_low < mid_low:
                return 'TREND_DOWN'
            elif recent_high == mid_high and recent_low == mid_low:
                return 'RANGE'
            else:
                # Check for breakout
                if recent_high > mid_high:
                    return 'BREAKOUT'
                else:
                    return 'BREAKDOWN'
        except Exception as e:
            logger.error(f'Error in Step 4: {e}')
            return 'UNKNOWN'
    
    def _step_5_momentum(self, candles: pd.DataFrame) -> Dict:
        """Step 5: Analyze momentum using MACD."""
        try:
            if len(candles) < 26:
                return {'status': 'INSUFFICIENT_DATA', 'score': 'NEUTRAL'}
            
            closes = candles['Close'].values.astype(float)
            
            # Calculate MACD
            macd_line, signal_line, histogram = MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
            
            if np.isnan(macd_line[-1]) or np.isnan(signal_line[-1]):
                return {'status': 'INSUFFICIENT_DATA', 'score': 'NEUTRAL'}
            
            current_macd = macd_line[-1]
            current_signal = signal_line[-1]
            current_histogram = histogram[-1]
            
            # Expanding histogram = momentum strengthening
            prev_histogram = histogram[-2] if len(histogram) > 1 else 0
            histogram_expanding = abs(current_histogram) > abs(prev_histogram)
            
            # Crossover check
            crossed_up = (macd_line[-2] < signal_line[-2]) and (current_macd > current_signal)
            crossed_down = (macd_line[-2] > signal_line[-2]) and (current_macd < current_signal)
            
            if histogram_expanding:
                if current_histogram > 0:
                    score = 'PASS'  # Bullish momentum expanding
                    direction = 'BULLISH'
                else:
                    score = 'PASS'  # Bearish momentum expanding
                    direction = 'BEARISH'
            elif crossed_up:
                score = 'PASS'
                direction = 'BULLISH'
            elif crossed_down:
                score = 'PASS'
                direction = 'BEARISH'
            else:
                score = 'NEUTRAL'
                direction = 'FLAT'
            
            return {
                'score': score,
                'direction': direction,
                'macd_line': float(current_macd),
                'signal_line': float(current_signal),
                'histogram': float(current_histogram),
                'histogram_expanding': histogram_expanding,
            }
        except Exception as e:
            logger.error(f'Error in Step 5: {e}')
            return {'score': 'NEUTRAL', 'status': 'ERROR'}
    
    def _step_6_rsi_vwap_atr(self, candles: pd.DataFrame) -> Dict:
        """Step 6: RSI, VWAP, and ATR analysis."""
        try:
            if len(candles) < 14:
                return {'status': 'INSUFFICIENT_DATA', 'score': 'NEUTRAL'}
            
            closes = candles['Close'].values.astype(float)
            
            # RSI
            rsi_values = RSI(closes, timeperiod=14)
            current_rsi = rsi_values[-1]
            
            # VWAP (simplified: without volume, use price-based)
            vwap = np.mean(closes[-20:]) if len(closes) >= 20 else np.mean(closes)
            current_price = closes[-1]
            distance_from_vwap_pct = ((current_price - vwap) / vwap) * 100
            
            # ATR
            high = candles['High'].values.astype(float)
            low = candles['Low'].values.astype(float)
            atr_values = ATR(high, low, closes, timeperiod=14)
            current_atr = atr_values[-1] if not np.isnan(atr_values[-1]) else 0
            volatility_normal = current_atr < np.mean(atr_values[-20:]) * 1.2 if len(atr_values) >= 20 else True
            
            # Scoring logic
            if current_rsi > 70 and distance_from_vwap_pct > 2 and not volatility_normal:
                score = 'PASS'  # Overbought with extension - short candidate
                bias = 'OVERBOUGHT'
            elif current_rsi < 30 and distance_from_vwap_pct < -2 and not volatility_normal:
                score = 'PASS'  # Oversold with extension - long candidate
                bias = 'OVERSOLD'
            elif 40 <= current_rsi <= 60 and abs(distance_from_vwap_pct) < 1:
                score = 'NEUTRAL'  # Balanced
                bias = 'BALANCED'
            else:
                score = 'FAIL'  # No clear extreme condition
                bias = 'NEUTRAL'
            
            return {
                'score': score,
                'rsi': float(current_rsi),
                'vwap': float(vwap),
                'distance_from_vwap_pct': float(distance_from_vwap_pct),
                'atr': float(current_atr),
                'volatility_status': 'ELEVATED' if not volatility_normal else 'NORMAL',
                'bias': bias,
            }
        except Exception as e:
            logger.error(f'Error in Step 6: {e}')
            return {'score': 'NEUTRAL', 'status': 'ERROR'}
    
    def _step_7_price_volume_confirmation(self, candles: pd.DataFrame) -> Dict:
        """Step 7: Price action and volume confirmation."""
        try:
            if len(candles) < 5:
                return {'status': 'INSUFFICIENT_DATA', 'score': 'NEUTRAL'}
            
            closes = candles['Close'].values
            opens = candles['Open'].values
            highs = candles['High'].values
            lows = candles['Low'].values
            volumes = candles['Volume'].values if 'Volume' in candles.columns else None
            
            # Last 5 candles
            recent_closes = closes[-5:]
            recent_opens = opens[-5:]
            recent_highs = highs[-5:]
            recent_lows = lows[-5:]
            
            # Count closes near highs/lows
            closes_near_highs = sum(1 for i in range(len(recent_closes)) 
                                    if (recent_closes[i] - recent_lows[i]) / (recent_highs[i] - recent_lows[i]) > 0.75)
            closes_near_lows = sum(1 for i in range(len(recent_closes)) 
                                   if (recent_closes[i] - recent_lows[i]) / (recent_highs[i] - recent_lows[i]) < 0.25)
            
            # Check for strong closes
            if closes_near_highs >= 3:
                score = 'PASS'
                confirmation = 'STRONG_BULLISH'
            elif closes_near_lows >= 3:
                score = 'PASS'
                confirmation = 'STRONG_BEARISH'
            else:
                score = 'NEUTRAL'
                confirmation = 'WEAK'
            
            return {
                'score': score,
                'confirmation': confirmation,
                'closes_near_highs': closes_near_highs,
                'closes_near_lows': closes_near_lows,
            }
        except Exception as e:
            logger.error(f'Error in Step 7: {e}')
            return {'score': 'NEUTRAL', 'status': 'ERROR'}
    
    def _step_8_event_risk(self) -> Dict:
        """Step 8: Check for event risk."""
        try:
            # In real implementation, check against economic_events.json
            # For now, return SAFE unless we're close to a major event
            return {
                'level': 'SAFE',
                'upcoming_event': None,
                'minutes_to_event': None,
            }
        except Exception as e:
            logger.error(f'Error in Step 8: {e}')
            return {'level': 'UNKNOWN'}
    
    def _calculate_confidence_and_action(self, macro_filter, momentum_score, rsi_vwap_atr,
                                         volume_confirmation, event_risk, session_quality, regime) -> Tuple[str, SignalAction]:
        """Calculate overall confidence and determine trading action."""
        try:
            # Count passing signals
            passes = 0
            direction = None
            
            # Macro filter (most important)
            if macro_filter.get('stance') == 'BULLISH':
                passes += 1
                direction = 'LONG'
            elif macro_filter.get('stance') == 'BEARISH':
                passes += 1
                direction = 'SHORT'
            else:
                passes -= 0.5
            
            # Momentum
            if momentum_score.get('score') == 'PASS':
                passes += 1
                if momentum_score.get('direction') == 'BULLISH' and direction != 'SHORT':
                    direction = 'LONG'
                elif momentum_score.get('direction') == 'BEARISH' and direction != 'LONG':
                    direction = 'SHORT'
            else:
                passes -= 0.5
            
            # RSI/VWAP/ATR
            if rsi_vwap_atr.get('score') == 'PASS':
                passes += 1
                if rsi_vwap_atr.get('bias') == 'OVERBOUGHT':
                    direction = 'SHORT'
                elif rsi_vwap_atr.get('bias') == 'OVERSOLD':
                    direction = 'LONG'
            else:
                passes -= 0.5
            
            # Volume confirmation
            if volume_confirmation.get('score') == 'PASS':
                passes += 0.5
            else:
                passes -= 0.25
            
            # Event risk (must be safe to trade)
            if event_risk.get('level') != 'SAFE':
                return ('LOW', SignalAction.WAIT)
            
            # Session quality
            if session_quality == 'LOW':
                passes -= 0.5
            elif session_quality == 'MEDIUM':
                passes -= 0.25
            
            # Regime check
            if regime in ['TREND_UP', 'BREAKOUT']:
                if direction == 'SHORT':
                    passes -= 1  # Don't fade strong uptrends
            elif regime in ['TREND_DOWN', 'BREAKDOWN']:
                if direction == 'LONG':
                    passes -= 1  # Don't fade strong downtrends
            
            # Determine confidence level
            if passes >= 3:
                confidence = 'HIGH'
            elif passes >= 1.5:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'
            
            # Determine action
            if event_risk.get('level') != 'SAFE':
                action = SignalAction.WAIT
            elif confidence == 'LOW':
                action = SignalAction.WAIT
            elif direction == 'LONG':
                action = SignalAction.LONG
            elif direction == 'SHORT':
                action = SignalAction.SHORT
            else:
                action = SignalAction.WAIT
            
            return (confidence, action)
        except Exception as e:
            logger.error(f'Error calculating confidence: {e}')
            return ('LOW', SignalAction.WAIT)
