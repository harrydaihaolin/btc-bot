#!/usr/bin/env python3
"""
UBC Tennis Centre Configuration
UBC Recreation specific configuration
"""

import os
import sys
from typing import Dict

# Add project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from common.config.base_config import BaseConfig


class UBCConfig(BaseConfig):
    """Configuration manager for UBC Tennis Centre"""

    def __init__(self):
        super().__init__("UBC")
        self.base_url = "https://portal.recreation.ubc.ca"
        self.login_url = "https://portal.recreation.ubc.ca/index.php?r=public/index"
        self.booking_url = "https://recreation.ubc.ca/tennis/court-booking/"
        self.booking_system_url = None  # Will be determined dynamically

    def get_credentials(self) -> Dict[str, str]:
        """Get UBC login credentials from environment variables"""
        # Try UBC-specific credentials first
        username = os.getenv("UBC_USERNAME")
        password = os.getenv("UBC_PASSWORD")

        # Fall back to BTC credentials for testing if UBC credentials not set
        if not username:
            username = os.getenv("BTC_USERNAME")
        if not password:
            password = os.getenv("BTC_PASSWORD")

        if not username or not password:
            raise ValueError(
                "UBC credentials not found. Please set UBC_USERNAME and UBC_PASSWORD environment variables, "
                "or use BTC_USERNAME and BTC_PASSWORD for testing."
            )

        return {"username": username, "password": password}

    def get_notification_config(self) -> Dict[str, str]:
        """Get notification configuration for UBC bookings"""
        return {
            "email": os.getenv(
                "UBC_NOTIFICATION_EMAIL",
                os.getenv("GMAIL_APP_EMAIL", os.getenv("BTC_NOTIFICATION_EMAIL")),
            ),
            "gmail_app_password": os.getenv(
                "UBC_GMAIL_APP_PASSWORD",
                os.getenv("GMAIL_APP_PASSWORD", os.getenv("BTC_GMAIL_APP_PASSWORD")),
            ),
            "sms_phone": os.getenv(
                "UBC_SMS_PHONE", os.getenv("SMS_PHONE", os.getenv("BTC_PHONE_NUMBER"))
            ),
            "twilio_sid": os.getenv("TWILIO_SID"),
            "twilio_token": os.getenv("TWILIO_TOKEN"),
            "twilio_phone": os.getenv("TWILIO_PHONE"),
        }
