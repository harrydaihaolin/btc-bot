#!/usr/bin/env python3
"""
UBC Tennis Court Booking Configuration Module
Handles UBC-specific configuration and settings
"""

import os
from typing import Dict, Any, Optional


class UBCConfig:
    """Configuration manager for UBC tennis court booking"""
    
    def __init__(self):
        self.base_url = "https://portal.recreation.ubc.ca"
        self.login_url = "https://portal.recreation.ubc.ca/index.php?r=public/index"
        self.booking_url = "https://recreation.ubc.ca/tennis/court-booking/"
        self.booking_system_url = None  # Will be determined dynamically
        
    def get_credentials(self) -> Dict[str, str]:
        """Get UBC login credentials from environment variables"""
        # Try UBC-specific credentials first
        username = os.getenv('UBC_USERNAME')
        password = os.getenv('UBC_PASSWORD')
        
        # Fall back to BTC credentials for testing if UBC credentials not set
        if not username:
            username = os.getenv('BTC_USERNAME')
        if not password:
            password = os.getenv('BTC_PASSWORD')
        
        if not username or not password:
            raise ValueError(
                "UBC credentials not found. Please set UBC_USERNAME and UBC_PASSWORD environment variables, "
                "or use BTC_USERNAME and BTC_PASSWORD for testing."
            )
        
        return {
            'username': username,
            'password': password
        }
    
    def get_notification_config(self) -> Dict[str, str]:
        """Get notification configuration for UBC bookings"""
        return {
            'email': os.getenv('UBC_NOTIFICATION_EMAIL', 
                              os.getenv('GMAIL_APP_EMAIL', 
                                       os.getenv('BTC_NOTIFICATION_EMAIL'))),
            'gmail_app_password': os.getenv('UBC_GMAIL_APP_PASSWORD', 
                                           os.getenv('GMAIL_APP_PASSWORD', 
                                                    os.getenv('BTC_GMAIL_APP_PASSWORD'))),
            'sms_phone': os.getenv('UBC_SMS_PHONE', 
                                  os.getenv('SMS_PHONE', 
                                           os.getenv('BTC_PHONE_NUMBER'))),
            'twilio_sid': os.getenv('TWILIO_SID'),
            'twilio_token': os.getenv('TWILIO_TOKEN'),
            'twilio_phone': os.getenv('TWILIO_PHONE')
        }
    
    def get_monitoring_config(self) -> Dict[str, int]:
        """Get monitoring configuration for UBC"""
        return {
            'monitoring_interval': int(os.getenv('UBC_MONITORING_INTERVAL', '5')),  # minutes
            'max_attempts': int(os.getenv('UBC_MAX_ATTEMPTS', '0')),  # 0 = unlimited
            'wait_timeout': int(os.getenv('UBC_WAIT_TIMEOUT', '15'))  # seconds
        }
    
    def get_booking_preferences(self) -> Dict[str, Any]:
        """Get UBC-specific booking preferences"""
        return {
            'preferred_courts': os.getenv('UBC_PREFERRED_COURTS', '').split(',') if os.getenv('UBC_PREFERRED_COURTS') else [],
            'preferred_times': os.getenv('UBC_PREFERRED_TIMES', '').split(',') if os.getenv('UBC_PREFERRED_TIMES') else [],
            'preferred_duration': os.getenv('UBC_PREFERRED_DURATION', '1'),  # hours
            'max_price': float(os.getenv('UBC_MAX_PRICE', '50.0')),
            'prime_hours_only': os.getenv('UBC_PRIME_HOURS_ONLY', 'false').lower() == 'true'
        }
    
    def validate_credentials(self) -> bool:
        """Validate that all required credentials are present"""
        try:
            creds = self.get_credentials()
            notif_config = self.get_notification_config()
            
            # Check login credentials
            if not creds['username'] or not creds['password']:
                return False
            
            # Check notification credentials (at least email or SMS)
            if not notif_config['email'] and not notif_config['sms_phone']:
                return False
            
            # If email is configured, check Gmail app password
            if notif_config['email'] and not notif_config['gmail_app_password']:
                return False
            
            # If SMS is configured, check Twilio credentials (optional)
            # SMS notifications will be skipped if Twilio credentials are missing
            if notif_config['sms_phone'] and not (notif_config['twilio_sid'] and notif_config['twilio_token'] and notif_config['twilio_phone']):
                # SMS phone is set but Twilio credentials are missing - this is OK, SMS will be skipped
                pass
            
            return True
            
        except Exception:
            return False
    
    def get_browser_config(self) -> Dict[str, Any]:
        """Get browser configuration for UBC website"""
        return {
            'headless': os.getenv('UBC_HEADLESS', 'true').lower() == 'true',
            'window_size': (1920, 1080),
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'implicit_wait': 10,
            'page_load_timeout': 30
        }
    
    def get_logging_config(self) -> Dict[str, str]:
        """Get logging configuration for UBC monitoring"""
        return {
            'log_file': os.getenv('UBC_LOG_FILE', 'ubc_monitoring.log'),
            'log_level': os.getenv('UBC_LOG_LEVEL', 'INFO'),
            'log_format': '%(asctime)s - %(levelname)s - %(message)s'
        }
