"""Main application entry point for SILVER DECK."""

import logging
import asyncio
from datetime import datetime
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/silver_deck.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from src.config import Config
from src.data_providers.oanda_client import OANDAClient
from src.data_providers.yahoo_finance import YahooFinanceProvider
from src.analysis.silver_deck_analyzer import SilverDeckAnalyzer, SignalAction
from src.analysis.events_manager import EventsManager
from src.alerts.telegram_notifier import TelegramNotifier

async def main():
    """Main application loop."""
    
    logger.info('═' * 60)
    logger.info('SILVER DECK - Real-time Silver Futures Analysis Engine')
    logger.info('Paper Trading Education Only')
    logger.info('═' * 60)
    
    # Validate configuration
    if not Config.validate():
        logger.error('Configuration validation failed. Exiting.')
        sys.exit(1)
    
    logger.info(f'Configuration: {Config.OANDA_ENVIRONMENT.upper()} mode')
    logger.info(f'Trading symbol: {Config.MARKET_SYMBOL}')
    logger.info(f'Execution enabled: {Config.ENABLE_EXECUTION}')
    
    # Initialize components
    try:
        oanda_client = OANDAClient()
        macro_provider = YahooFinanceProvider()
        analyzer = SilverDeckAnalyzer(macro_provider, oanda_client)
        events_manager = EventsManager()
        notifier = TelegramNotifier()
        
        logger.info('All components initialized successfully')
    except Exception as e:
        logger.error(f'Failed to initialize components: {e}')
        sys.exit(1)
    
    # Main analysis loop
    iteration = 0
    
    while True:
        try:
            iteration += 1
            logger.info(f'\n--- Analysis Iteration {iteration} ---')
            logger.info(f'Time: {datetime.now().isoformat()}')
            
            # Check event risk
            is_safe, safety_message = events_manager.is_safe_to_trade()
            logger.info(f'Event Risk Status: {safety_message}')
            
            if not is_safe:
                logger.warning(f'WAIT - {safety_message}')
                await asyncio.sleep(Config.ANALYSIS_INTERVAL)
                continue
            
            # Fetch current data
            account_info = oanda_client.get_account_info()
            if not account_info:
                logger.error('Failed to fetch account info')
                await asyncio.sleep(Config.ANALYSIS_INTERVAL)
                continue
            
            # Get candle data (15 minutes)
            candles_data = oanda_client.get_candles(granularity='M15', count=100)
            if not candles_data:
                logger.error('Failed to fetch candle data')
                await asyncio.sleep(Config.ANALYSIS_INTERVAL)
                continue
            
            # Convert to DataFrame
            import pandas as pd
            candles_df = pd.DataFrame([
                {
                    'Time': c['time'],
                    'Open': float(c['mid']['o']),
                    'High': float(c['mid']['h']),
                    'Low': float(c['mid']['l']),
                    'Close': float(c['mid']['c']),
                    'Volume': int(c.get('volume', 0)),
                } for c in candles_data
            ])
            
            # Get macro snapshot
            macro_snapshot = macro_provider.get_macro_snapshot()
            logger.info(f'Macro: DXY {macro_snapshot["dxy"]["change_pct"]:+.2f}%, Gold {macro_snapshot["gold"]["change_pct"]:+.2f}%')
            
            # Run analysis
            result = analyzer.analyze(candles_df, macro_snapshot)
            
            # Log results
            logger.info(f"\nANALYSIS RESULT: {result['action'].value}")
            logger.info(f"Confidence: {result['confidence']}")
            logger.info(f"Regime: {result['regime']}")
            logger.info(f"Scorecard:")
            for key, value in result['scorecard'].items():
                logger.info(f"  - {key}: {value}")
            
            # Send Telegram notification if signal generated
            if result['action'] in [SignalAction.LONG, SignalAction.SHORT]:
                signal_data = {
                    'ACTION': result['action'].value,
                    'MARKET': Config.MARKET_SYMBOL,
                    'PRICE': result['current_data'].get('current_price', 'N/A'),
                    'CONFIDENCE': result['confidence'],
                    'REGIME': result['regime'],
                    'ENTRY': {},
                    'SCORECARD': {
                        'macro': result['scorecard']['macro_filter'].get('stance', 'NEUTRAL'),
                    }
                }
                
                try:
                    await notifier.send_signal(signal_data)
                except Exception as e:
                    logger.error(f'Failed to send Telegram notification: {e}')
            
            # Sleep before next analysis
            logger.info(f'Next analysis in {Config.ANALYSIS_INTERVAL} seconds')
            await asyncio.sleep(Config.ANALYSIS_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info('Received interrupt signal. Shutting down gracefully...')
            break
        except Exception as e:
            logger.error(f'Error in main loop: {e}', exc_info=True)
            await asyncio.sleep(Config.ANALYSIS_INTERVAL)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)
