#!/usr/bin/env python3
"""
UBC Module Tests
Test UBC Tennis Centre specific modules
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ubc.config.ubc_config import UBCConfig
from ubc.monitor.ubc_monitor import UBCMonitor
from ubc.notifications.ubc_notifications import UBCNotificationManager


class TestUBCConfig(unittest.TestCase):
    """Test UBC configuration class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = UBCConfig()
    
    def test_facility_name(self):
        """Test facility name is set correctly"""
        self.assertEqual(self.config.facility_name, "UBC")
    
    def test_urls(self):
        """Test URLs are set correctly"""
        self.assertEqual(self.config.base_url, "https://portal.recreation.ubc.ca")
        self.assertEqual(self.config.login_url, "https://portal.recreation.ubc.ca/index.php?r=public/index")
        self.assertEqual(self.config.booking_url, "https://recreation.ubc.ca/tennis/court-booking/")
    
    @patch.dict(os.environ, {'UBC_USERNAME': 'test@ubc.ca', 'UBC_PASSWORD': 'testpass'}, clear=True)
    def test_get_credentials_ubc(self):
        """Test UBC credential retrieval"""
        creds = self.config.get_credentials()
        self.assertEqual(creds['username'], 'test@ubc.ca')
        self.assertEqual(creds['password'], 'testpass')
    
    @patch.dict(os.environ, {'BTC_USERNAME': 'test@example.com', 'BTC_PASSWORD': 'testpass'}, clear=True)
    def test_get_credentials_btc_fallback(self):
        """Test BTC credential fallback"""
        creds = self.config.get_credentials()
        self.assertEqual(creds['username'], 'test@example.com')
        self.assertEqual(creds['password'], 'testpass')
    
    def test_get_credentials_missing(self):
        """Test credential retrieval when missing"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                self.config.get_credentials()
    
    @patch.dict(os.environ, {
        'UBC_USERNAME': 'test@ubc.ca', 
        'UBC_PASSWORD': 'testpass',
        'UBC_NOTIFICATION_EMAIL': 'notify@example.com',
        'UBC_GMAIL_APP_PASSWORD': 'apppass'
    }, clear=True)
    def test_validate_credentials_success(self):
        """Test successful credential validation"""
        self.assertTrue(self.config.validate_credentials())
    
    def test_validate_credentials_failure(self):
        """Test failed credential validation"""
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(self.config.validate_credentials())


class TestUBCMonitor(unittest.TestCase):
    """Test UBC monitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = UBCMonitor()
    
    def test_config_type(self):
        """Test configuration is UBCConfig type"""
        self.assertIsInstance(self.monitor.config, UBCConfig)
    
    def test_facility_name(self):
        """Test facility name is UBC"""
        self.assertEqual(self.monitor.config.facility_name, "UBC")
    
    def test_logger_name(self):
        """Test logger name includes UBC"""
        self.assertIn('ubc', self.monitor.logger.name)


class TestUBCNotificationManager(unittest.TestCase):
    """Test UBC notification manager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.notification_manager = UBCNotificationManager()
    
    def test_config_type(self):
        """Test configuration is UBCConfig type"""
        self.assertIsInstance(self.notification_manager.config, UBCConfig)
    
    def test_facility_name(self):
        """Test facility name is UBC"""
        self.assertEqual(self.notification_manager.config.facility_name, "UBC")
    
    def test_email_formatting(self):
        """Test email message formatting"""
        test_courts = {
            "2025-10-26": [
                {
                    "court_name": "Court 1",
                    "time": "10:00 AM",
                    "duration": "1 hour",
                    "price": "$32.15"
                }
            ]
        }
        
        email_body = self.notification_manager._format_email_message(test_courts)
        self.assertIn("UBC Tennis Courts Available", email_body)
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
                    "price": "$32.15"
                }
            ]
        }
        
        sms_body = self.notification_manager._format_sms_message(test_courts)
        self.assertIn("UBC Tennis", sms_body)
        self.assertIn("Court 1", sms_body)
        self.assertIn("10:00 AM", sms_body)


if __name__ == '__main__':
    unittest.main()
