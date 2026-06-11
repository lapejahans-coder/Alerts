"""Configuration management for SILVER DECK system."""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Core configuration class."""
    
    # OANDA Configuration
    OANDA_API_TOKEN: str = os.getenv('OANDA_API_TOKEN', '')
    OANDA_ACCOUNT_ID: str = os.getenv('OANDA_ACCOUNT_ID', '')
    OANDA_ENVIRONMENT: str = os.getenv('OANDA_ENVIRONMENT', 'practice')  # practice or live
    OANDA_BASE_URL: str = (
        'https://api-fxpractice.oanda.com' if OANDA_ENVIRONMENT == 'practice'
        else 'https://api-fxtrade.oanda.com'
    )
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Trading Configuration
    MARKET_SYMBOL: str = os.getenv('MARKET_SYMBOL', 'XAG_USD')
    EXECUTION_MODE: str = os.getenv('EXECUTION_MODE', 'practice')  # practice or live
    ENABLE_EXECUTION: bool = os.getenv('ENABLE_EXECUTION', 'false').lower() == 'true'
    
    # System Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    ANALYSIS_INTERVAL: int = int(os.getenv('ANALYSIS_INTERVAL', '300'))  # seconds
    VERBOSE_MODE: bool = os.getenv('VERBOSE_MODE', 'false').lower() == 'true'
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    LOGS_DIR = PROJECT_ROOT / 'logs'
    DATA_DIR = PROJECT_ROOT / 'data'
    CONFIG_DIR = PROJECT_ROOT / 'config'
    
    # Create directories if they don't exist
    LOGS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    CONFIG_DIR.mkdir(exist_ok=True)
    
    # Validation
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration."""
        errors = []
        
        if not cls.OANDA_API_TOKEN:
            errors.append('OANDA_API_TOKEN is required')
        if not cls.OANDA_ACCOUNT_ID:
            errors.append('OANDA_ACCOUNT_ID is required')
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append('TELEGRAM_BOT_TOKEN is required')
        if not cls.TELEGRAM_CHAT_ID:
            errors.append('TELEGRAM_CHAT_ID is required')
        
        if errors:
            print('Configuration errors:')
            for error in errors:
                print(f'  - {error}')
            return False
        
        return True
