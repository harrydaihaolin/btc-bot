#!/usr/bin/env python3
"""
BTC Tennis Club Configuration
Burnaby Tennis Club specific configuration
"""

import os
import sys
from typing import Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.config.base_config import BaseConfig


class BTCConfig(BaseConfig):
    """Configuration manager for Burnaby Tennis Club"""
    
    def __init__(self):
        super().__init__("BTC")
        self.base_url = "https://www.burnabytennis.ca"
        self.login_url = "https://www.burnabytennis.ca/login"
        self.booking_url = "https://www.burnabytennis.ca/app/bookings/grid"
        self.booking_system_url = None  # Will be determined dynamically
        
    def get_credentials(self) -> Dict[str, str]:
        """Get BTC login credentials from environment variables"""
        username = os.getenv('BTC_USERNAME')
        password = os.getenv('BTC_PASSWORD')
        
        if not username or not password:
            raise ValueError(
                "BTC credentials not found. Please set BTC_USERNAME and BTC_PASSWORD environment variables."
            )
        
        return {
            'username': username,
            'password': password
        }
    
    def get_notification_config(self) -> Dict[str, str]:
        """Get notification configuration for BTC bookings"""
        return {
            'email': os.getenv('BTC_NOTIFICATION_EMAIL', os.getenv('GMAIL_APP_EMAIL')),
            'gmail_app_password': os.getenv('BTC_GMAIL_APP_PASSWORD', os.getenv('GMAIL_APP_PASSWORD')),
            'sms_phone': os.getenv('BTC_SMS_PHONE', os.getenv('SMS_PHONE', os.getenv('BTC_PHONE_NUMBER'))),
            'twilio_sid': os.getenv('TWILIO_SID'),
            'twilio_token': os.getenv('TWILIO_TOKEN'),
            'twilio_phone': os.getenv('TWILIO_PHONE')
        }
