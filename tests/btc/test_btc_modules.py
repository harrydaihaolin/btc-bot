#!/usr/bin/env python3
"""
BTC Module Tests
Test Burnaby Tennis Club specific modules
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from btc.config.btc_config import BTCConfig
from btc.monitor.btc_monitor import BTCMonitor
from btc.notifications.btc_notifications import BTCNotificationManager


class TestBTCConfig(unittest.TestCase):
    """Test BTC configuration class"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = BTCConfig()

    def test_facility_name(self):
        """Test facility name is set correctly"""
        self.assertEqual(self.config.facility_name, "BTC")

    def test_urls(self):
        """Test URLs are set correctly"""
        self.assertEqual(self.config.base_url, "https://www.burnabytennis.ca")
        self.assertEqual(self.config.login_url, "https://www.burnabytennis.ca/login")
        self.assertEqual(
            self.config.booking_url, "https://www.burnabytennis.ca/app/bookings/grid"
        )

    @patch.dict(
        os.environ,
        {"BTC_USERNAME": "test@example.com", "BTC_PASSWORD": "testpass"},
        clear=True,
    )
    def test_get_credentials(self):
        """Test credential retrieval"""
        creds = self.config.get_credentials()
        self.assertEqual(creds["username"], "test@example.com")
        self.assertEqual(creds["password"], "testpass")

    def test_get_credentials_missing(self):
        """Test credential retrieval when missing"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                self.config.get_credentials()

    @patch.dict(
        os.environ,
        {
            "BTC_USERNAME": "test@example.com",
            "BTC_PASSWORD": "testpass",
            "BTC_NOTIFICATION_EMAIL": "notify@example.com",
            "BTC_GMAIL_APP_PASSWORD": "apppass",
        },
        clear=True,
    )
    def test_validate_credentials_success(self):
        """Test successful credential validation"""
        self.assertTrue(self.config.validate_credentials())

    def test_validate_credentials_failure(self):
        """Test failed credential validation"""
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(self.config.validate_credentials())


class TestBTCMonitor(unittest.TestCase):
    """Test BTC monitor class"""

    def setUp(self):
        """Set up test fixtures"""
        self.monitor = BTCMonitor()

    def test_config_type(self):
        """Test configuration is BTCConfig type"""
        self.assertIsInstance(self.monitor.config, BTCConfig)

    def test_facility_name(self):
        """Test facility name is BTC"""
        self.assertEqual(self.monitor.config.facility_name, "BTC")

    def test_logger_name(self):
        """Test logger name includes BTC"""
        self.assertIn("btc", self.monitor.logger.name)


class TestBTCNotificationManager(unittest.TestCase):
    """Test BTC notification manager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.notification_manager = BTCNotificationManager()

    def test_config_type(self):
        """Test configuration is BTCConfig type"""
        self.assertIsInstance(self.notification_manager.config, BTCConfig)

    def test_facility_name(self):
        """Test facility name is BTC"""
        self.assertEqual(self.notification_manager.config.facility_name, "BTC")

    def test_email_formatting(self):
        """Test email message formatting"""
        test_courts = {
            "2025-10-26": [
                {
                    "court_name": "Court 1",
                    "time": "10:00 AM",
                    "duration": "1 hour",
                    "price": "$25.00",
                }
            ]
        }

        email_body = self.notification_manager._format_email_message(test_courts)
        self.assertIn("Burnaby Tennis Club Courts Available", email_body)
        self.assertIn("Court 1", email_body)
        self.assertIn("10:00 AM", email_body)

    def test_sms_formatting(self):
        """Test SMS message formatting"""
        test_courts = {
            "2025-10-26": [
                {
                    "court_name": "Court 1",
                    "time": "10:00 AM",
                    "duration": "1 hour",
                    "price": "$25.00",
                }
            ]
        }

        sms_body = self.notification_manager._format_sms_message(test_courts)
        self.assertIn("Burnaby Tennis Club", sms_body)
        self.assertIn("Court 1", sms_body)
        self.assertIn("10:00 AM", sms_body)


if __name__ == "__main__":
    unittest.main()
