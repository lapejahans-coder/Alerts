"""Economic events calendar and event risk management."""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class EventsManager:
    """Manage economic events and determine trading windows."""
    
    def __init__(self, events_file: Path = None):
        if events_file is None:
            events_file = Path(__file__).parent.parent.parent / 'config' / 'economic_events.json'
        
        self.events_file = events_file
        self.events = self._load_events()
        self.blocked_windows = []
        self.et = pytz.timezone('US/Eastern')
    
    def _load_events(self) -> Dict:
        """Load economic events from JSON file."""
        try:
            if self.events_file.exists():
                with open(self.events_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f'Error loading events file: {e}')
        return {'events': []}
    
    def get_upcoming_events(self, hours_ahead: int = 24) -> List[Dict]:
        """Get high-impact events in the next N hours."""
        try:
            now = datetime.now(self.et)
            cutoff = now + timedelta(hours=hours_ahead)
            
            upcoming = []
            for event in self.events.get('events', []):
                if 'date' not in event or 'time' not in event:
                    continue
                
                try:
                    event_dt = datetime.strptime(
                        f"{event['date']} {event['time']}",
                        '%Y-%m-%d %H:%M'
                    )
                    event_dt = self.et.localize(event_dt)
                    
                    if now <= event_dt <= cutoff and event.get('impact') in ['HIGH', 'CRITICAL']:
                        upcoming.append({
                            **event,
                            'datetime': event_dt.isoformat(),
                            'minutes_away': int((event_dt - now).total_seconds() / 60),
                        })
                except ValueError:
                    continue
            
            return sorted(upcoming, key=lambda x: x['minutes_away'])
        except Exception as e:
            logger.error(f'Error getting upcoming events: {e}')
            return []
    
    def is_in_blocked_window(self, safety_margin_minutes: int = 30) -> Tuple[bool, Optional[Dict]]:
        """Check if we're in a blocked trading window."""
        try:
            upcoming = self.get_upcoming_events(hours_ahead=4)
            now = datetime.now(self.et)
            
            for event in upcoming:
                event_dt = datetime.fromisoformat(event['datetime'])
                
                before_block = event_dt - timedelta(minutes=event.get('block_before_minutes', safety_margin_minutes))
                after_block = event_dt + timedelta(minutes=event.get('block_after_minutes', safety_margin_minutes))
                
                if before_block <= now <= after_block:
                    return True, event
            
            return False, None
        except Exception as e:
            logger.error(f'Error checking blocked window: {e}')
            return False, None
    
    def is_safe_to_trade(self, check_blackout_period: bool = True) -> Tuple[bool, str]:
        """Determine if it's safe to trade based on events."""
        try:
            blocked, event = self.is_in_blocked_window()
            
            if blocked:
                return False, f"In blocked window: {event.get('name')} at {event.get('time')}"
            
            # Check for upcoming critical events
            upcoming = self.get_upcoming_events(hours_ahead=2)
            if upcoming and upcoming[0].get('impact') == 'CRITICAL':
                minutes_away = upcoming[0].get('minutes_away', 0)
                if minutes_away < 120:  # Within 2 hours
                    return False, f"Critical event {upcoming[0].get('name')} in {minutes_away} minutes"
            
            return True, "Safe to trade"
        except Exception as e:
            logger.error(f'Error checking trade safety: {e}')
            return False, f"Error checking safety: {e}"
    
    def get_daily_blocked_periods(self, date: datetime = None) -> List[Tuple[datetime, datetime]]:
        """Get all blocked periods for a given day."""
        if date is None:
            date = datetime.now(self.et)
        
        blocked_periods = []
        
        try:
            for event in self.events.get('events', []):
                if 'date' not in event or 'time' not in event:
                    continue
                
                try:
                    event_dt = datetime.strptime(
                        f"{event['date']} {event['time']}",
                        '%Y-%m-%d %H:%M'
                    )
                    event_dt = self.et.localize(event_dt)
                    
                    if event_dt.date() == date.date():
                        before = event_dt - timedelta(minutes=event.get('block_before_minutes', 30))
                        after = event_dt + timedelta(minutes=event.get('block_after_minutes', 30))
                        blocked_periods.append((before, after))
                except ValueError:
                    continue
            
            return sorted(blocked_periods, key=lambda x: x[0])
        except Exception as e:
            logger.error(f'Error getting daily blocked periods: {e}')
            return []
    
    def get_event_summary(self) -> Dict:
        """Get summary of all events."""
        return {
            'total_events': len(self.events.get('events', [])),
            'high_impact': len([e for e in self.events.get('events', []) if e.get('impact') == 'HIGH']),
            'critical_impact': len([e for e in self.events.get('events', []) if e.get('impact') == 'CRITICAL']),
            'loaded_year': self.events.get('year'),
        }
