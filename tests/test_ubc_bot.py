#!/usr/bin/env python3
"""
Unit tests for UBC Tennis Bot
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ubc_bot import UBCTennisBot


class TestUBCTennisBot(unittest.TestCase):
    """Test cases for UBC Tennis Bot"""

    def setUp(self):
        """Set up test fixtures"""
        with patch('ubc_bot.UBCConfig') as mock_config, \
             patch('ubc_bot.UBCMonitor') as mock_monitor, \
             patch('ubc_bot.UBCNotificationManager') as mock_notifications, \
             patch('ubc_bot.logging.basicConfig'):
            # Configure mock config to return proper values
            mock_config.return_value.get_logging_config.return_value = {
                "log_level": "INFO",
                "log_format": "%(asctime)s - %(levelname)s - %(message)s",
                "log_file": "test.log"
            }
            self.bot = UBCTennisBot()

    def test_init(self):
        """Test bot initialization"""
        self.assertIsNotNone(self.bot.config)
        self.assertIsNotNone(self.bot.monitor)
        self.assertIsNotNone(self.bot.notifications)
        self.assertIsNotNone(self.bot.logger)

    @patch('ubc_bot.getpass.getpass')
    @patch('ubc_bot.input')
    def test_setup_credentials_from_env(self, mock_input, mock_getpass):
        """Test credential setup from environment variables"""
        # Mock successful credential retrieval from environment
        self.bot.config.get_credentials.return_value = {
            "username": "test_user",
            "password": "test_pass"
        }
        
        credentials = self.bot.setup_credentials()
        
        self.assertEqual(credentials["username"], "test_user")
        self.assertEqual(credentials["password"], "test_pass")
        self.bot.config.get_credentials.assert_called_once()

    @patch('ubc_bot.getpass.getpass')
    @patch('ubc_bot.input')
    def test_setup_credentials_interactive(self, mock_input, mock_getpass):
        """Test interactive credential setup"""
        # Mock environment credential failure
        self.bot.config.get_credentials.side_effect = ValueError("No credentials")
        mock_input.return_value = "test_user"
        mock_getpass.return_value = "test_pass"
        
        credentials = self.bot.setup_credentials()
        
        self.assertEqual(credentials["username"], "test_user")
        self.assertEqual(credentials["password"], "test_pass")
        mock_input.assert_called_once_with("Username: ")
        mock_getpass.assert_called_once_with("Password: ")

    @patch('ubc_bot.time.sleep')
    def test_run_single_scan_success(self, mock_sleep):
        """Test successful single scan"""
        # Mock successful scan
        self.bot.monitor.scan_available_courts.return_value = [
            "Court 1 - 2024-01-01 10:00-11:00",
            "Court 2 - 2024-01-01 14:00-15:00"
        ]
        self.bot.setup_credentials = Mock(return_value={"username": "test", "password": "test"})
        
        self.bot.run_single_scan()
        
        self.bot.monitor.scan_available_courts.assert_called_once()
        self.bot.notifications.send_notifications.assert_called_once()
        self.bot.monitor.cleanup.assert_called_once()

    @patch('ubc_bot.time.sleep')
    def test_run_single_scan_no_courts(self, mock_sleep):
        """Test single scan with no available courts"""
        # Mock no courts found
        self.bot.monitor.scan_available_courts.return_value = []
        self.bot.setup_credentials = Mock(return_value={"username": "test", "password": "test"})
        
        self.bot.run_single_scan()
        
        self.bot.monitor.scan_available_courts.assert_called_once()
        self.bot.notifications.send_notifications.assert_not_called()
        self.bot.monitor.cleanup.assert_called_once()

    @patch('ubc_bot.time.sleep')
    def test_run_single_scan_error(self, mock_sleep):
        """Test single scan with error"""
        # Mock scan error
        self.bot.monitor.scan_available_courts.side_effect = Exception("Scan failed")
        self.bot.setup_credentials = Mock(return_value={"username": "test", "password": "test"})
        
        self.bot.run_single_scan()
        
        self.bot.monitor.scan_available_courts.assert_called_once()
        self.bot.notifications.send_notifications.assert_not_called()
        self.bot.monitor.cleanup.assert_called_once()

    @patch('ubc_bot.time.sleep')
    def test_run_continuous_monitoring(self, mock_sleep):
        """Test continuous monitoring"""
        # Mock monitoring config
        self.bot.config.get_monitoring_config.return_value = {"monitoring_interval": 1}
        self.bot.setup_credentials = Mock(return_value={"username": "test", "password": "test"})
        
        # Mock scan to return courts first time, then KeyboardInterrupt
        self.bot.monitor.scan_available_courts.side_effect = [
            ["Court 1 - 2024-01-01 10:00-11:00"],
            KeyboardInterrupt()
        ]
        
        self.bot.run_continuous_monitoring()
        
        # Should have called scan twice (once for initial scan, once before interrupt)
        self.assertEqual(self.bot.monitor.scan_available_courts.call_count, 2)
        self.bot.notifications.send_notifications.assert_called_once()
        self.bot.monitor.cleanup.assert_called_once()

    @patch('ubc_bot.time.sleep')
    def test_run_timeslot_monitoring(self, mock_sleep):
        """Test timeslot monitoring"""
        # Mock monitoring config
        self.bot.config.get_monitoring_config.return_value = {"monitoring_interval": 1}
        self.bot.setup_credentials = Mock(return_value={"username": "test", "password": "test"})
        
        # Mock scan to return courts with specific timeslots
        self.bot.monitor.scan_available_courts.side_effect = [
            [
                "Court 1 - 2024-01-01 10:00-11:00",
                "Court 2 - 2024-01-01 14:00-15:00",
                "Court 3 - 2024-01-01 16:00-17:00"
            ],
            KeyboardInterrupt()
        ]
        
        # Mock user input for timeslots
        with patch('ubc_bot.input') as mock_input:
            mock_input.side_effect = ["10:00", "14:00", ""]  # Empty string to finish
            
            self.bot.run_timeslot_monitoring()
        
        # Should have called scan twice
        self.assertEqual(self.bot.monitor.scan_available_courts.call_count, 2)
        # Should have sent notifications for preferred timeslots
        self.bot.notifications.send_notifications.assert_called_once()
        self.bot.monitor.cleanup.assert_called_once()

    @patch('ubc_bot.sys.stdin.isatty')
    def test_main_non_interactive_mode(self, mock_isatty):
        """Test main function in non-interactive mode (Docker)"""
        mock_isatty.return_value = False
        
        with patch('ubc_bot.UBCTennisBot') as mock_bot_class:
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            from ubc_bot import main
            main()
            
            mock_bot.run_continuous_monitoring.assert_called_once()

    @patch('ubc_bot.sys.stdin.isatty')
    @patch('ubc_bot.input')
    def test_main_interactive_mode(self, mock_input, mock_isatty):
        """Test main function in interactive mode"""
        mock_isatty.return_value = True
        mock_input.side_effect = ["4"]  # Exit choice
        
        with patch('ubc_bot.UBCTennisBot') as mock_bot_class:
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            from ubc_bot import main
            main()
            
            # Should not call any monitoring methods since we chose exit
            mock_bot.run_single_scan.assert_not_called()
            mock_bot.run_continuous_monitoring.assert_not_called()
            mock_bot.run_timeslot_monitoring.assert_not_called()


if __name__ == "__main__":
    unittest.main()
