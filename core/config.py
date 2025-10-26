"""
Configuration management for BTC Tennis Bot
"""

import os
import logging
from typing import Dict, Optional

class BTCConfig:
    """Configuration manager for BTC Tennis Bot"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_credentials(self) -> Dict[str, Optional[str]]:
        """Get credentials from environment variables"""
        return {
            'username': os.getenv('BTC_USERNAME'),
            'password': os.getenv('BTC_PASSWORD'),
            'notification_email': os.getenv('BTC_NOTIFICATION_EMAIL'),
            'phone_number': os.getenv('BTC_PHONE_NUMBER'),
            'gmail_app_email': os.getenv('BTC_GMAIL_APP_EMAIL'),
            'gmail_app_password': os.getenv('BTC_GMAIL_APP_PASSWORD')
        }
    
    def validate_credentials(self, credentials: Dict[str, Optional[str]]) -> bool:
        """Validate that all required credentials are present"""
        required_vars = [
            'username', 'password', 'notification_email', 
            'phone_number', 'gmail_app_email', 'gmail_app_password'
        ]
        
        missing_vars = [var for var in required_vars if not credentials.get(var)]
        
        if missing_vars:
            self.logger.error(f"Missing required credentials: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def get_monitoring_config(self) -> Dict[str, int]:
        """Get monitoring configuration"""
        return {
            'monitoring_interval': int(os.getenv('BTC_MONITORING_INTERVAL', '5')),
            'max_attempts': int(os.getenv('BTC_MAX_ATTEMPTS', '0')),
            'wait_timeout': int(os.getenv('BTC_WAIT_TIMEOUT', '15'))
        }
    
    def get_bot_config(self) -> Dict[str, any]:
        """Get bot configuration"""
        return {
            'headless': os.getenv('BTC_HEADLESS', 'true').lower() == 'true',
            'base_url': 'https://www.burnabytennis.ca/app/bookings/grid',
            'login_url': 'https://www.burnabytennis.ca/login'
        }
