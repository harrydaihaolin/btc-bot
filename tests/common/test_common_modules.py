#!/usr/bin/env python3
"""
Common Module Tests
Test shared base classes and utilities using concrete implementations
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


class TestBaseConfig(unittest.TestCase):
    """Test base configuration class using BTC implementation"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = BTCConfig()

    def test_facility_name(self):
        """Test facility name is set correctly"""
        self.assertEqual(self.config.facility_name, "BTC")

    def test_monitoring_config_defaults(self):
        """Test default monitoring configuration"""
        config = self.config.get_monitoring_config()
        self.assertEqual(config["monitoring_interval"], 60)  # BTC default is 60 minutes
        self.assertEqual(config["max_attempts"], 0)
        self.assertEqual(config["wait_timeout"], 15)

    def test_browser_config_defaults(self):
        """Test default browser configuration"""
        config = self.config.get_browser_config()
        self.assertTrue(config["headless"])
        self.assertEqual(config["window_size"], (1920, 1080))
        self.assertIn("Chrome", config["user_agent"])

    def test_logging_config_defaults(self):
        """Test default logging configuration"""
        config = self.config.get_logging_config()
        self.assertEqual(config["log_file"], "btc_monitoring.log")
        self.assertEqual(config["log_level"], "INFO")
        self.assertIn("%(asctime)s", config["log_format"])


class TestBaseMonitor(unittest.TestCase):
    """Test base monitor class using BTC implementation"""

    def setUp(self):
        """Set up test fixtures"""
        self.monitor = BTCMonitor()

    def test_config_assignment(self):
        """Test configuration is assigned correctly"""
        self.assertEqual(self.monitor.config.facility_name, "BTC")

    def test_previous_courts_initialization(self):
        """Test previous courts set is initialized"""
        self.assertIsInstance(self.monitor.previous_courts, set)
        self.assertEqual(len(self.monitor.previous_courts), 0)

    def test_logger_setup(self):
        """Test logger is set up correctly"""
        self.assertIsNotNone(self.monitor.logger)
        self.assertEqual(self.monitor.logger.name, "btc_monitor")


class TestBaseNotificationManager(unittest.TestCase):
    """Test base notification manager class using BTC implementation"""

    def setUp(self):
        """Set up test fixtures"""
        self.notification_manager = BTCNotificationManager()

    def test_config_assignment(self):
        """Test configuration is assigned correctly"""
        self.assertEqual(self.notification_manager.config.facility_name, "BTC")

    def test_sent_notifications_initialization(self):
        """Test sent notifications set is initialized"""
        self.assertIsInstance(self.notification_manager.sent_notifications, set)
        self.assertEqual(len(self.notification_manager.sent_notifications), 0)

    def test_logger_setup(self):
        """Test logger is set up correctly"""
        self.assertIsNotNone(self.notification_manager.logger)
        self.assertEqual(self.notification_manager.logger.name, "btc_notifications")


if __name__ == "__main__":
    unittest.main()
