"""OANDA API client for live pricing and trade execution."""

import logging
import requests
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from src.config import Config

logger = logging.getLogger(__name__)

class OANDAClient:
    """OANDA v20 REST API client for XAG_USD trading."""
    
    def __init__(self):
        self.base_url = Config.OANDA_BASE_URL
        self.account_id = Config.OANDA_ACCOUNT_ID
        self.token = Config.OANDA_API_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'AcceptDatetimeFormat': 'UNIX'
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to OANDA API."""
        url = f'{self.base_url}{endpoint}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data, timeout=10)
            else:
                logger.error(f'Unsupported HTTP method: {method}')
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f'OANDA API error: {response.status_code} - {response.text}')
                return None
        
        except requests.exceptions.RequestException as e:
            logger.error(f'Request error to OANDA: {e}')
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account summary."""
        endpoint = f'/v3/accounts/{self.account_id}'
        return self._request('GET', endpoint)
    
    def get_current_price(self, instrument: str = 'XAG_USD') -> Optional[Dict]:
        """Get current bid/ask price for instrument."""
        endpoint = f'/v3/accounts/{self.account_id}/pricing?instruments={instrument}'
        response = self._request('GET', endpoint)
        
        if response and 'prices' in response and len(response['prices']) > 0:
            price_data = response['prices'][0]
            return {
                'instrument': instrument,
                'bid': float(price_data['bids'][0]['price']),
                'ask': float(price_data['asks'][0]['price']),
                'timestamp': price_data['time'],
                'mid': (float(price_data['bids'][0]['price']) + float(price_data['asks'][0]['price'])) / 2,
                'spread': abs(float(price_data['asks'][0]['price']) - float(price_data['bids'][0]['price']))
            }
        return None
    
    def get_candles(self, instrument: str = 'XAG_USD', granularity: str = 'M5', count: int = 100) -> Optional[List[Dict]]:
        """Get historical candle data."""
        endpoint = f'/v3/instruments/{instrument}/candles?granularity={granularity}&count={count}"
        response = self._request('GET', endpoint)
        
        if response and 'candles' in response:
            return response['candles']
        return None
    
    def place_market_order(self, instrument: str, units: int, take_profit: Optional[float] = None, 
                          stop_loss: Optional[float] = None) -> Optional[Dict]:
        """Place a market order."""
        if not Config.ENABLE_EXECUTION:
            logger.warning('Trade execution is disabled. Skipping order placement.')
            return None
        
        order_data = {
            'order': {
                'instrument': instrument,
                'units': str(units),
                'type': 'MARKET',
                'positionFill': 'DEFAULT'
            }
        }
        
        # Add stop loss if provided
        if stop_loss is not None:
            order_data['order']['stopLossOnFill'] = {
                'price': str(stop_loss),
                'timeInForce': 'GTC'
            }
        
        # Add take profit if provided
        if take_profit is not None:
            order_data['order']['takeProfitOnFill'] = {
                'price': str(take_profit),
                'timeInForce': 'GTC'
            }
        
        endpoint = f'/v3/accounts/{self.account_id}/orders'
        return self._request('POST', endpoint, order_data)
    
    def place_limit_order(self, instrument: str, price: float, units: int, 
                         take_profit: Optional[float] = None, 
                         stop_loss: Optional[float] = None) -> Optional[Dict]:
        """Place a limit order."""
        if not Config.ENABLE_EXECUTION:
            logger.warning('Trade execution is disabled. Skipping order placement.')
            return None
        
        order_data = {
            'order': {
                'instrument': instrument,
                'price': str(price),
                'units': str(units),
                'type': 'LIMIT',
                'positionFill': 'DEFAULT',
                'timeInForce': 'GTC'
            }
        }
        
        if stop_loss is not None:
            order_data['order']['stopLossOnFill'] = {
                'price': str(stop_loss),
                'timeInForce': 'GTC'
            }
        
        if take_profit is not None:
            order_data['order']['takeProfitOnFill'] = {
                'price': str(take_profit),
                'timeInForce': 'GTC'
            }
        
        endpoint = f'/v3/accounts/{self.account_id}/orders'
        return self._request('POST', endpoint, order_data)
    
    def close_position(self, instrument: str) -> Optional[Dict]:
        """Close all positions for an instrument."""
        if not Config.ENABLE_EXECUTION:
            logger.warning('Trade execution is disabled. Skipping position closure.')
            return None
        
        endpoint = f'/v3/accounts/{self.account_id}/positions/{instrument}/close'
        order_data = {
            'longUnits': 'ALL',
            'shortUnits': 'ALL'
        }
        return self._request('PUT', endpoint, order_data)
    
    def get_open_positions(self) -> Optional[List[Dict]]:
        """Get all open positions."""
        endpoint = f'/v3/accounts/{self.account_id}/openPositions'
        response = self._request('GET', endpoint)
        
        if response and 'positions' in response:
            return response['positions']
        return None
    
    def get_open_trades(self) -> Optional[List[Dict]]:
        """Get all open trades."""
        endpoint = f'/v3/accounts/{self.account_id}/openTrades'
        response = self._request('GET', endpoint)
        
        if response and 'trades' in response:
            return response['trades']
        return None
