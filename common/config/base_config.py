#!/usr/bin/env python3
"""
Common Configuration Base Class
Shared configuration functionality for all tennis court monitors
"""

import os
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseConfig(ABC):
    """Base configuration class for tennis court monitors"""

    def __init__(self, facility_name: str):
        self.facility_name = facility_name
        self.base_url = ""
        self.login_url = ""
        self.booking_url = ""
        self.booking_system_url: Optional[str] = None

    @abstractmethod
    def get_credentials(self) -> Dict[str, str]:
        """Get login credentials from environment variables"""
        pass

    @abstractmethod
    def get_notification_config(self) -> Dict[str, str]:
        """Get notification configuration"""
        pass

    def get_monitoring_config(self) -> Dict[str, int]:
        """Get monitoring configuration"""
        prefix = self.facility_name.upper()
        return {
            "monitoring_interval": int(
                os.getenv(f"{prefix}_MONITORING_INTERVAL", "5")
            ),  # minutes
            "max_attempts": int(
                os.getenv(f"{prefix}_MAX_ATTEMPTS", "0")
            ),  # 0 = unlimited
            "wait_timeout": int(os.getenv(f"{prefix}_WAIT_TIMEOUT", "15")),  # seconds
        }

    def get_browser_config(self) -> Dict[str, Any]:
        """Get browser configuration"""
        prefix = self.facility_name.upper()
        return {
            "headless": os.getenv(f"{prefix}_HEADLESS", "true").lower() == "true",
            "window_size": (1920, 1080),
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "implicit_wait": 10,
            "page_load_timeout": 30,
        }

    def get_logging_config(self) -> Dict[str, str]:
        """Get logging configuration"""
        prefix = self.facility_name.upper()
        return {
            "log_file": os.getenv(
                f"{prefix}_LOG_FILE", f"{self.facility_name.lower()}_monitoring.log"
            ),
            "log_level": os.getenv(f"{prefix}_LOG_LEVEL", "INFO"),
            "log_format": "%(asctime)s - %(levelname)s - %(message)s",
        }

    def validate_credentials(self) -> bool:
        """Validate that all required credentials are present"""
        try:
            creds = self.get_credentials()
            notif_config = self.get_notification_config()

            # Check login credentials
            if not creds["username"] or not creds["password"]:
                return False

            # Check notification credentials (at least email or SMS)
            if not notif_config["email"] and not notif_config["sms_phone"]:
                return False

            # If email is configured, check Gmail app password
            if notif_config["email"] and not notif_config["gmail_app_password"]:
                return False

            # SMS credentials are optional - SMS will be skipped if Twilio credentials are missing
            return True

        except Exception:
            return False

    def get_booking_preferences(self) -> Dict[str, Any]:
        """Get facility-specific booking preferences"""
        prefix = self.facility_name.upper()
        return {
            "preferred_courts": (
                os.getenv(f"{prefix}_PREFERRED_COURTS", "").split(",")
                if os.getenv(f"{prefix}_PREFERRED_COURTS")
                else []
            ),
            "preferred_times": (
                os.getenv(f"{prefix}_PREFERRED_TIMES", "").split(",")
                if os.getenv(f"{prefix}_PREFERRED_TIMES")
                else []
            ),
            "preferred_duration": os.getenv(
                f"{prefix}_PREFERRED_DURATION", "1"
            ),  # hours
            "max_price": float(os.getenv(f"{prefix}_MAX_PRICE", "50.0")),
            "prime_hours_only": os.getenv(f"{prefix}_PRIME_HOURS_ONLY", "false").lower()
            == "true",
        }
