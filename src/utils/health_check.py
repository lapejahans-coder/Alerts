"""Health check and monitoring utilities."""

import logging
from datetime import datetime
from typing import Dict, List
import psutil

logger = logging.getLogger(__name__)

class HealthCheck:
    """System health monitoring."""
    
    def __init__(self):
        self.last_analysis = None
        self.last_error = None
        self.error_count = 0
        self.consecutive_errors = 0
    
    def check_system_resources(self) -> Dict:
        """Check CPU, memory, and disk usage."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu = psutil.cpu_percent(interval=1)
            
            return {
                'cpu_percent': cpu,
                'memory_percent': memory.percent,
                'memory_mb': memory.used / (1024 * 1024),
                'disk_percent': disk.percent,
                'status': 'HEALTHY' if (cpu < 80 and memory.percent < 85) else 'WARNING'
            }
        except Exception as e:
            logger.error(f'Error checking system resources: {e}')
            return {'status': 'ERROR'}
    
    def record_successful_analysis(self):
        """Record successful analysis execution."""
        self.last_analysis = datetime.now()
        self.consecutive_errors = 0
    
    def record_error(self, error: str):
        """Record error occurrence."""
        self.last_error = error
        self.error_count += 1
        self.consecutive_errors += 1
        
        if self.consecutive_errors > 10:
            logger.critical(f'Too many consecutive errors: {self.consecutive_errors}')
    
    def get_health_status(self) -> Dict:
        """Get overall system health status."""
        resources = self.check_system_resources()
        
        status = 'HEALTHY'
        if self.consecutive_errors > 5:
            status = 'CRITICAL'
        elif resources.get('status') == 'WARNING':
            status = 'WARNING'
        elif self.error_count > 20:
            status = 'DEGRADED'
        
        return {
            'status': status,
            'resources': resources,
            'last_analysis': self.last_analysis.isoformat() if self.last_analysis else None,
            'last_error': self.last_error,
            'error_count': self.error_count,
            'consecutive_errors': self.consecutive_errors,
        }
