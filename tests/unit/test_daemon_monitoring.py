#!/usr/bin/env python3
"""
Unit tests for daemon_monitoring.py
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from daemon_monitoring import DaemonMonitor, setup_logging

class TestDaemonMonitor(unittest.TestCase):
    """Test cases for DaemonMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.daemon_monitor = DaemonMonitor()
    
    def test_init(self):
        """Test DaemonMonitor initialization"""
        self.assertTrue(self.daemon_monitor.running)
        self.assertIsNotNone(self.daemon_monitor.logger)
        self.assertIsNotNone(self.daemon_monitor.config_manager)
        self.assertIsNone(self.daemon_monitor.monitor)
        self.assertIsNone(self.daemon_monitor.notification_manager)
        self.assertIsNone(self.daemon_monitor.credentials)
        self.assertIsNone(self.daemon_monitor.config)
    
    def test_initialize_components_success(self):
        """Test successful component initialization"""
        # Mock config manager methods
        with patch.object(self.daemon_monitor.config_manager, 'get_credentials') as mock_get_credentials, \
             patch.object(self.daemon_monitor.config_manager, 'get_bot_config') as mock_get_bot_config, \
             patch.object(self.daemon_monitor.config_manager, 'get_monitoring_config') as mock_get_monitoring_config, \
             patch.object(self.daemon_monitor.config_manager, 'validate_credentials') as mock_validate_credentials:
            
            mock_get_credentials.return_value = {
                'username': 'test@example.com',
                'password': 'testpass',
                'notification_email': 'test@example.com',
                'phone_number': '1234567890',
                'gmail_app_email': 'test@gmail.com',
                'gmail_app_password': 'testpass'
            }
            mock_get_bot_config.return_value = {
                'base_url': 'https://test.com',
                'login_url': 'https://test.com/login',
                'booking_url': 'https://test.com/booking'
            }
            mock_get_monitoring_config.return_value = {
                'monitoring_interval': 5,
                'max_attempts': 0,
                'wait_timeout': 15
            }
            mock_validate_credentials.return_value = True
            
            # Mock CourtMonitor and NotificationManager
            with patch('daemon_monitoring.CourtMonitor') as mock_court_monitor, \
                 patch('daemon_monitoring.NotificationManager') as mock_notification_manager:
                
                result = self.daemon_monitor.initialize_components()
                
                self.assertTrue(result)
                self.assertIsNotNone(self.daemon_monitor.monitor)
                self.assertIsNotNone(self.daemon_monitor.notification_manager)
                self.assertIsNotNone(self.daemon_monitor.credentials)
                self.assertIsNotNone(self.daemon_monitor.config)
    
    def test_initialize_components_invalid_credentials(self):
        """Test component initialization with invalid credentials"""
        # Mock config manager methods
        with patch.object(self.daemon_monitor.config_manager, 'get_credentials') as mock_get_credentials, \
             patch.object(self.daemon_monitor.config_manager, 'get_bot_config') as mock_get_bot_config, \
             patch.object(self.daemon_monitor.config_manager, 'get_monitoring_config') as mock_get_monitoring_config, \
             patch.object(self.daemon_monitor.config_manager, 'validate_credentials') as mock_validate_credentials:
            
            mock_get_credentials.return_value = {
                'username': 'test@example.com',
                'password': 'testpass',
                'notification_email': 'test@example.com',
                'phone_number': '1234567890',
                'gmail_app_email': 'test@gmail.com',
                'gmail_app_password': 'testpass'
            }
            mock_get_bot_config.return_value = {
                'base_url': 'https://test.com',
                'login_url': 'https://test.com/login',
                'booking_url': 'https://test.com/booking'
            }
            mock_get_monitoring_config.return_value = {
                'monitoring_interval': 5,
                'max_attempts': 0,
                'wait_timeout': 15
            }
            mock_validate_credentials.return_value = False
            
            result = self.daemon_monitor.initialize_components()
            
            self.assertFalse(result)
            self.assertIsNone(self.daemon_monitor.monitor)
            self.assertIsNone(self.daemon_monitor.notification_manager)
    
    def test_initialize_components_exception(self):
        """Test component initialization with exception"""
        # Mock config manager to raise exception
        with patch.object(self.daemon_monitor.config_manager, 'get_credentials') as mock_get_credentials:
            mock_get_credentials.side_effect = Exception("Config error")
            
            result = self.daemon_monitor.initialize_components()
            
            self.assertFalse(result)
            self.assertIsNone(self.daemon_monitor.monitor)
            self.assertIsNone(self.daemon_monitor.notification_manager)
    
    def test_run_monitoring_cycle_success(self):
        """Test successful monitoring cycle"""
        # Set up monitor and notification_manager
        self.daemon_monitor.monitor = MagicMock()
        self.daemon_monitor.notification_manager = MagicMock()
        
        # Mock monitor methods
        self.daemon_monitor.monitor.driver = MagicMock()
        self.daemon_monitor.monitor.login.return_value = True
        self.daemon_monitor.monitor.navigate_to_booking_page.return_value = True
        self.daemon_monitor.monitor.scan_all_dates.return_value = {
            '2024-01-01': [{'text': 'Court 1', 'time': '10:00'}]
        }
        self.daemon_monitor.monitor.detect_new_courts.return_value = {
            '2024-01-01': [{'text': 'Court 1', 'time': '10:00'}]
        }
        
        # Mock notification manager methods
        self.daemon_monitor.notification_manager.send_email_notification.return_value = True
        self.daemon_monitor.notification_manager.send_sms_notification.return_value = True
        
        result = self.daemon_monitor.run_monitoring_cycle()
        
        self.assertTrue(result)
        self.daemon_monitor.monitor.login.assert_called_once()
        self.daemon_monitor.monitor.navigate_to_booking_page.assert_called_once()
        self.daemon_monitor.monitor.scan_all_dates.assert_called_once()
        self.daemon_monitor.monitor.detect_new_courts.assert_called_once()
        self.daemon_monitor.notification_manager.send_email_notification.assert_called_once()
        self.daemon_monitor.notification_manager.send_sms_notification.assert_called_once()
    
    def test_run_monitoring_cycle_no_courts(self):
        """Test monitoring cycle with no courts found"""
        # Set up monitor
        self.daemon_monitor.monitor = MagicMock()
        
        # Mock monitor methods
        self.daemon_monitor.monitor.driver = MagicMock()
        self.daemon_monitor.monitor.login.return_value = True
        self.daemon_monitor.monitor.navigate_to_booking_page.return_value = True
        self.daemon_monitor.monitor.scan_all_dates.return_value = {}
        
        result = self.daemon_monitor.run_monitoring_cycle()
        
        self.assertTrue(result)
        self.daemon_monitor.monitor.login.assert_called_once()
        self.daemon_monitor.monitor.navigate_to_booking_page.assert_called_once()
        self.daemon_monitor.monitor.scan_all_dates.assert_called_once()
    
    def test_run_monitoring_cycle_login_failed(self):
        """Test monitoring cycle with login failure"""
        # Set up monitor
        self.daemon_monitor.monitor = MagicMock()
        
        # Mock monitor methods
        self.daemon_monitor.monitor.driver = MagicMock()
        self.daemon_monitor.monitor.login.return_value = False
        self.daemon_monitor.monitor.navigate_to_booking_page.return_value = True
        self.daemon_monitor.monitor.scan_all_dates.return_value = {}
        
        result = self.daemon_monitor.run_monitoring_cycle()
        
        self.assertTrue(result)  # Should continue even if login fails
        self.daemon_monitor.monitor.login.assert_called_once()
        self.daemon_monitor.monitor.navigate_to_booking_page.assert_called_once()
        self.daemon_monitor.monitor.scan_all_dates.assert_called_once()
    
    def test_run_monitoring_cycle_navigation_failed(self):
        """Test monitoring cycle with navigation failure"""
        # Set up monitor
        self.daemon_monitor.monitor = MagicMock()
        
        # Mock monitor methods
        self.daemon_monitor.monitor.driver = MagicMock()
        self.daemon_monitor.monitor.login.return_value = True
        self.daemon_monitor.monitor.navigate_to_booking_page.return_value = False
        
        result = self.daemon_monitor.run_monitoring_cycle()
        
        self.assertFalse(result)
        self.daemon_monitor.monitor.login.assert_called_once()
        self.daemon_monitor.monitor.navigate_to_booking_page.assert_called_once()
        self.daemon_monitor.monitor.scan_all_dates.assert_not_called()
    
    def test_run_monitoring_cycle_exception(self):
        """Test monitoring cycle with exception"""
        # Set up monitor
        self.daemon_monitor.monitor = MagicMock()
        
        # Mock monitor methods
        self.daemon_monitor.monitor.driver = MagicMock()
        self.daemon_monitor.monitor.login.side_effect = Exception("Login error")
        
        result = self.daemon_monitor.run_monitoring_cycle()
        
        self.assertFalse(result)
        self.daemon_monitor.monitor.login.assert_called_once()
    
    def test_run_daemon_success(self):
        """Test successful daemon run"""
        # Mock config manager
        with patch.object(self.daemon_monitor.config_manager, 'get_monitoring_config') as mock_get_monitoring_config:
            mock_get_monitoring_config.return_value = {
                'monitoring_interval': 5,
                'max_attempts': 2
            }
            
            # Mock other methods
            with patch.object(self.daemon_monitor, 'initialize_components') as mock_initialize_components, \
                 patch.object(self.daemon_monitor, 'run_monitoring_cycle') as mock_run_monitoring_cycle, \
                 patch('daemon_monitoring.signal.signal'), \
                 patch('daemon_monitoring.time.sleep'):
                
                mock_initialize_components.return_value = True
                mock_run_monitoring_cycle.return_value = True
                
                result = self.daemon_monitor.run_daemon()
                
                self.assertTrue(result)
                mock_initialize_components.assert_called_once()
                # Should call run_monitoring_cycle multiple times (initial + 2 cycles)
                self.assertEqual(mock_run_monitoring_cycle.call_count, 3)
    
    def test_run_daemon_exception(self):
        """Test daemon run with exception"""
        # Mock config manager
        with patch.object(self.daemon_monitor.config_manager, 'get_monitoring_config') as mock_get_monitoring_config:
            mock_get_monitoring_config.return_value = {
                'monitoring_interval': 5,
                'max_attempts': 0
            }
            
            # Mock initialize_components to raise exception
            with patch.object(self.daemon_monitor, 'initialize_components') as mock_initialize_components, \
                 patch('daemon_monitoring.signal.signal'), \
                 patch('daemon_monitoring.time.sleep'):
                
                mock_initialize_components.side_effect = Exception("Initialization error")
                
                result = self.daemon_monitor.run_daemon()
                
                self.assertFalse(result)
                mock_initialize_components.assert_called_once()
    
    def test_run_daemon_max_attempts(self):
        """Test daemon run with max attempts"""
        # Mock config manager
        with patch.object(self.daemon_monitor.config_manager, 'get_monitoring_config') as mock_get_monitoring_config:
            mock_get_monitoring_config.return_value = {
                'monitoring_interval': 1,  # 1 minute for faster testing
                'max_attempts': 2
            }
            
            # Mock other methods
            with patch.object(self.daemon_monitor, 'initialize_components') as mock_initialize_components, \
                 patch.object(self.daemon_monitor, 'run_monitoring_cycle') as mock_run_monitoring_cycle, \
                 patch('daemon_monitoring.signal.signal'), \
                 patch('daemon_monitoring.time.sleep'):
                
                mock_initialize_components.return_value = True
                mock_run_monitoring_cycle.return_value = True
                
                result = self.daemon_monitor.run_daemon()
                
                self.assertTrue(result)
                mock_initialize_components.assert_called_once()
                # Should call run_monitoring_cycle 3 times (initial + 2 cycles)
                self.assertEqual(mock_run_monitoring_cycle.call_count, 3)
    
    def test_run_daemon_unlimited_attempts(self):
        """Test daemon run with unlimited attempts"""
        # Mock config manager
        with patch.object(self.daemon_monitor.config_manager, 'get_monitoring_config') as mock_get_monitoring_config:
            mock_get_monitoring_config.return_value = {
                'monitoring_interval': 1,  # 1 minute for faster testing
                'max_attempts': 0  # Unlimited
            }
            
            # Mock other methods
            with patch.object(self.daemon_monitor, 'initialize_components') as mock_initialize_components, \
                 patch.object(self.daemon_monitor, 'run_monitoring_cycle') as mock_run_monitoring_cycle, \
                 patch('daemon_monitoring.signal.signal'), \
                 patch('daemon_monitoring.time.sleep'), \
                 patch.object(self.daemon_monitor, 'running', False):  # Stop after first iteration
                
                mock_initialize_components.return_value = True
                mock_run_monitoring_cycle.return_value = True
                
                result = self.daemon_monitor.run_daemon()
                
                self.assertTrue(result)
                mock_initialize_components.assert_called_once()
                # Should call run_monitoring_cycle at least once
                self.assertGreaterEqual(mock_run_monitoring_cycle.call_count, 1)

if __name__ == '__main__':
    unittest.main()