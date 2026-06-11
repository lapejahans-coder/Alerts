"""Yahoo Finance data provider for macro analysis."""

import yfinance as yf
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

class YahooFinanceProvider:
    """Fetch macro data from Yahoo Finance for analysis."""
    
    # Macro instrument mappings
    MACRO_INSTRUMENTS = {
        'DXY': 'DX=F',           # US Dollar Index
        'TLT': 'TLT',            # 20-Year Treasury ETF
        'IEF': 'IEF',            # 7-10 Year Treasury ETF
        'SHY': 'SHY',            # 1-3 Year Treasury ETF
        'GOLD': 'GC=F',          # Gold futures
        'UST10Y': '^TNX',        # 10-Year Treasury Yield
        'VIX': '^VIX',           # Volatility Index
    }
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if len(data) > 0:
                return float(data['Close'].iloc[-1])
        except Exception as e:
            logger.error(f'Error fetching {symbol} from Yahoo Finance: {e}')
        return None
    
    def get_dxy(self) -> Optional[float]:
        """Get current DXY (US Dollar Index) price."""
        return self._get_cached('DXY', self.MACRO_INSTRUMENTS['DXY'])
    
    def get_dxy_change(self) -> Optional[float]:
        """Get DXY change percentage today."""
        try:
            ticker = yf.Ticker(self.MACRO_INSTRUMENTS['DXY'])
            data = ticker.history(period='5d')
            if len(data) >= 2:
                close_today = data['Close'].iloc[-1]
                close_prev = data['Close'].iloc[-2]
                return ((close_today - close_prev) / close_prev) * 100
        except Exception as e:
            logger.error(f'Error calculating DXY change: {e}')
        return None
    
    def get_gold_price(self) -> Optional[float]:
        """Get current Gold futures price."""
        return self._get_cached('GOLD', self.MACRO_INSTRUMENTS['GOLD'])
    
    def get_gold_change(self) -> Optional[float]:
        """Get Gold change percentage today."""
        try:
            ticker = yf.Ticker(self.MACRO_INSTRUMENTS['GOLD'])
            data = ticker.history(period='5d')
            if len(data) >= 2:
                close_today = data['Close'].iloc[-1]
                close_prev = data['Close'].iloc[-2]
                return ((close_today - close_prev) / close_prev) * 100
        except Exception as e:
            logger.error(f'Error calculating Gold change: {e}')
        return None
    
    def get_10yr_yield(self) -> Optional[float]:
        """Get current 10-year Treasury yield."""
        return self._get_cached('UST10Y', self.MACRO_INSTRUMENTS['UST10Y'])
    
    def get_10yr_yield_change(self) -> Optional[float]:
        """Get 10-year yield change in basis points today."""
        try:
            ticker = yf.Ticker(self.MACRO_INSTRUMENTS['UST10Y'])
            data = ticker.history(period='5d')
            if len(data) >= 2:
                yield_today = data['Close'].iloc[-1]
                yield_prev = data['Close'].iloc[-2]
                return (yield_today - yield_prev)  # in basis points
        except Exception as e:
            logger.error(f'Error calculating 10Y yield change: {e}')
        return None
    
    def get_vix(self) -> Optional[float]:
        """Get current VIX level."""
        return self._get_cached('VIX', self.MACRO_INSTRUMENTS['VIX'])
    
    def get_historical_data(self, symbol: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """Get historical OHLCV data."""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.history(period=period)
        except Exception as e:
            logger.error(f'Error fetching historical data for {symbol}: {e}')
        return None
    
    def _get_cached(self, key: str, symbol: str) -> Optional[float]:
        """Get cached value or fetch fresh data."""
        now = datetime.now()
        
        if key in self.cache:
            cache_age = (now - self.cache_time[key]).total_seconds()
            if cache_age < self.cache_ttl:
                return self.cache[key]
        
        price = self.get_current_price(symbol)
        if price is not None:
            self.cache[key] = price
            self.cache_time[key] = now
        
        return price
    
    def get_macro_snapshot(self) -> Dict:
        """Get a snapshot of all macro data."""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'dxy': {
                'price': self.get_dxy(),
                'change_pct': self.get_dxy_change(),
            },
            'gold': {
                'price': self.get_gold_price(),
                'change_pct': self.get_gold_change(),
            },
            'usdt_10yr': {
                'yield': self.get_10yr_yield(),
                'change_bps': self.get_10yr_yield_change(),
            },
            'vix': self.get_vix(),
        }
        return snapshot
