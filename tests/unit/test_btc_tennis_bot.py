"""
Unit tests for btc_tennis_bot.py
"""

import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from btc_tennis_bot import (
    main,
    run_continuous_monitoring,
    run_single_scan,
    setup_credentials,
)


class TestBTCTennisBot:
    """Test cases for btc_tennis_bot.py"""

    def setup_method(self):
        """Setup for each test method"""
        pass

    @patch("btc_tennis_bot.BTCConfig")
    def test_setup_credentials_with_env_vars(self, mock_config_class):
        """Test setup_credentials with existing environment variables"""
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        mock_credentials = {
            "username": "test@example.com",
            "password": "testpass",
            "notification_email": "test@example.com",
            "phone_number": "1234567890",
            "gmail_app_email": "test@gmail.com",
            "gmail_app_password": "apppass",
        }
        mock_config.get_credentials.return_value = mock_credentials
        mock_config.validate_credentials.return_value = True

        credentials = setup_credentials()

        assert credentials == mock_credentials
        mock_config.validate_credentials.assert_called_once_with(mock_credentials)

    @patch("btc_tennis_bot.BTCConfig")
    @patch("btc_tennis_bot.input")
    @patch("btc_tennis_bot.getpass.getpass")
    def test_setup_credentials_interactive(
        self, mock_getpass, mock_input, mock_config_class
    ):
        """Test setup_credentials with interactive input"""
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        mock_credentials = {
            "username": None,
            "password": None,
            "notification_email": None,
            "phone_number": None,
            "gmail_app_email": None,
            "gmail_app_password": None,
        }
        mock_config.get_credentials.return_value = mock_credentials
        mock_config.validate_credentials.return_value = False

        # Mock user input
        mock_input.side_effect = [
            "test@example.com",  # username
            "test@example.com",  # notification_email
            "1234567890",  # phone_number
            "test@gmail.com",  # gmail_app_email
        ]
        mock_getpass.side_effect = [
            "testpass",  # password
            "apppass",  # gmail_app_password
        ]

        credentials = setup_credentials()

        assert credentials["username"] == "test@example.com"
        assert credentials["password"] == "testpass"
        assert credentials["notification_email"] == "test@example.com"
        assert credentials["phone_number"] == "1234567890"
        assert credentials["gmail_app_email"] == "test@gmail.com"
        assert credentials["gmail_app_password"] == "apppass"

    @patch("btc_tennis_bot.BTCConfig")
    @patch("btc_tennis_bot.input")
    @patch("btc_tennis_bot.getpass.getpass")
    def test_setup_credentials_interactive_empty_notification_email(
        self, mock_getpass, mock_input, mock_config_class
    ):
        """Test interactive credential setup with empty notification email"""
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        mock_credentials = {
            "username": None,
            "password": None,
            "notification_email": None,
            "phone_number": None,
            "gmail_app_email": None,
            "gmail_app_password": None,
        }
        mock_config.get_credentials.return_value = mock_credentials
        mock_config.validate_credentials.return_value = False

        # Mock user input with empty notification_email
        mock_input.side_effect = [
            "test@example.com",  # username
            "",  # notification_email (empty)
            "1234567890",  # phone_number
            "test@gmail.com",  # gmail_app_email
        ]
        mock_getpass.side_effect = [
            "testpass",  # password
            "apppass",  # gmail_app_password
        ]

        credentials = setup_credentials()

        assert credentials["username"] == "test@example.com"
        assert (
            credentials["notification_email"] == "test@example.com"
        )  # Should default to username
        assert credentials["phone_number"] == "1234567890"
        assert credentials["gmail_app_email"] == "test@gmail.com"
        assert credentials["gmail_app_password"] == "apppass"

    @patch("btc_tennis_bot.BTCConfig")
    @patch("btc_tennis_bot.input")
    @patch("btc_tennis_bot.getpass.getpass")
    def test_setup_credentials_interactive_empty_gmail_app_email(
        self, mock_getpass, mock_input, mock_config_class
    ):
        """Test interactive credential setup with empty gmail app email"""
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        mock_credentials = {
            "username": None,
            "password": None,
            "notification_email": None,
            "phone_number": None,
            "gmail_app_email": None,
            "gmail_app_password": None,
        }
        mock_config.get_credentials.return_value = mock_credentials
        mock_config.validate_credentials.return_value = False

        # Mock user input with empty gmail_app_email
        mock_input.side_effect = [
            "test@example.com",  # username
            "notify@example.com",  # notification_email
            "1234567890",  # phone_number
            "",  # gmail_app_email (empty)
        ]
        mock_getpass.side_effect = [
            "testpass",  # password
            "apppass",  # gmail_app_password
        ]

        credentials = setup_credentials()

        assert credentials["username"] == "test@example.com"
        assert credentials["notification_email"] == "notify@example.com"
        assert credentials["phone_number"] == "1234567890"
        assert (
            credentials["gmail_app_email"] == "notify@example.com"
        )  # Should default to notification_email
        assert credentials["gmail_app_password"] == "apppass"

    @patch("btc_tennis_bot.BTCConfig")
    def test_setup_credentials_eof_error(self, mock_config_class):
        """Test setup_credentials with EOFError (non-interactive)"""
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        mock_credentials = {
            "username": None,
            "password": None,
            "notification_email": None,
            "phone_number": None,
            "gmail_app_email": None,
            "gmail_app_password": None,
        }
        mock_config.get_credentials.return_value = mock_credentials
        mock_config.validate_credentials.return_value = False

        with patch("btc_tennis_bot.input", side_effect=EOFError):
            with pytest.raises(SystemExit):
                setup_credentials()

    @patch("btc_tennis_bot.CourtMonitor")
    @patch("btc_tennis_bot.NotificationManager")
    def test_run_single_scan_success(self, mock_notification_class, mock_monitor_class):
        """Test successful single scan"""
        mock_monitor = MagicMock()
        mock_notification_manager = MagicMock()

        mock_monitor_class.return_value = mock_monitor
        mock_notification_class.return_value = mock_notification_manager

        mock_monitor.setup_driver.return_value = None
        mock_monitor.login.return_value = True
        mock_monitor.navigate_to_booking_page.return_value = True

        mock_courts = {
            "2025-10-26": [
                {"time": "6:00 AM", "text": "Book 6:00 am as 48hr", "court_number": "1"}
            ]
        }
        mock_monitor.scan_all_dates.return_value = mock_courts

        result = run_single_scan(mock_monitor, mock_notification_manager)

        assert result == mock_courts
        mock_monitor.setup_driver.assert_called_once()
        mock_monitor.login.assert_called_once()
        mock_monitor.navigate_to_booking_page.assert_called_once()
        mock_monitor.scan_all_dates.assert_called_once()
        mock_monitor.cleanup.assert_called_once()

    @patch("btc_tennis_bot.CourtMonitor")
    @patch("btc_tennis_bot.NotificationManager")
    def test_run_single_scan_login_failed(
        self, mock_notification_class, mock_monitor_class
    ):
        """Test single scan with login failure"""
        mock_monitor = MagicMock()
        mock_notification_manager = MagicMock()

        mock_monitor_class.return_value = mock_monitor
        mock_notification_class.return_value = mock_notification_manager

        mock_monitor.setup_driver.return_value = None
        mock_monitor.login.return_value = False
        mock_monitor.navigate_to_booking_page.return_value = True

        mock_courts = {}
        mock_monitor.scan_all_dates.return_value = mock_courts

        result = run_single_scan(mock_monitor, mock_notification_manager)

        assert result == mock_courts
        mock_monitor.login.assert_called_once()
        mock_monitor.navigate_to_booking_page.assert_called_once()

    @patch("btc_tennis_bot.CourtMonitor")
    @patch("btc_tennis_bot.NotificationManager")
    def test_run_single_scan_navigation_failed(
        self, mock_notification_class, mock_monitor_class
    ):
        """Test single scan with navigation failure"""
        mock_monitor = MagicMock()
        mock_notification_manager = MagicMock()

        mock_monitor_class.return_value = mock_monitor
        mock_notification_class.return_value = mock_notification_manager

        mock_monitor.setup_driver.return_value = None
        mock_monitor.login.return_value = True
        mock_monitor.navigate_to_booking_page.return_value = False

        result = run_single_scan(mock_monitor, mock_notification_manager)

        assert result == {}
        mock_monitor.login.assert_called_once()
        mock_monitor.navigate_to_booking_page.assert_called_once()
        mock_monitor.cleanup.assert_called_once()

    @patch("btc_tennis_bot.CourtMonitor")
    @patch("btc_tennis_bot.NotificationManager")
    def test_run_single_scan_exception(
        self, mock_notification_class, mock_monitor_class
    ):
        """Test single scan with exception"""
        mock_monitor = MagicMock()
        mock_notification_manager = MagicMock()

        mock_monitor_class.return_value = mock_monitor
        mock_notification_class.return_value = mock_notification_manager

        mock_monitor.setup_driver.side_effect = Exception("Setup failed")

        result = run_single_scan(mock_monitor, mock_notification_manager)

        assert result == {}
        mock_monitor.cleanup.assert_called_once()

    @patch("btc_tennis_bot.run_single_scan")
    @patch("btc_tennis_bot.time.sleep")
    def test_run_continuous_monitoring_success(self, mock_sleep, mock_run_single_scan):
        """Test successful continuous monitoring"""
        mock_monitor = MagicMock()
        mock_notification_manager = MagicMock()

        mock_courts = {
            "2025-10-26": [
                {"time": "6:00 AM", "text": "Book 6:00 am as 48hr", "court_number": "1"}
            ]
        }
        mock_run_single_scan.return_value = mock_courts

        # Mock sleep to raise KeyboardInterrupt after first call
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        run_continuous_monitoring(mock_monitor, mock_notification_manager, 1, 1)

        mock_run_single_scan.assert_called_once()
        mock_notification_manager.send_email_notification.assert_called_once_with(
            mock_courts
        )
        mock_notification_manager.send_sms_notification.assert_called_once_with(
            mock_courts
        )

    @patch("btc_tennis_bot.run_single_scan")
    @patch("btc_tennis_bot.time.sleep")
    def test_run_continuous_monitoring_no_courts(
        self, mock_sleep, mock_run_single_scan
    ):
        """Test continuous monitoring with no courts"""
        mock_monitor = MagicMock()
        mock_notification_manager = MagicMock()

        mock_run_single_scan.return_value = {}

        # Mock sleep to raise KeyboardInterrupt after first call
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        run_continuous_monitoring(mock_monitor, mock_notification_manager, 1, 1)

        mock_run_single_scan.assert_called_once()
        mock_notification_manager.send_email_notification.assert_not_called()
        mock_notification_manager.send_sms_notification.assert_not_called()

    @patch("btc_tennis_bot.run_single_scan")
    @patch("btc_tennis_bot.time.sleep")
    def test_run_continuous_monitoring_exception(
        self, mock_sleep, mock_run_single_scan
    ):
        """Test continuous monitoring with exception"""
        mock_monitor = MagicMock()
        mock_notification_manager = MagicMock()

        mock_run_single_scan.side_effect = Exception("Scan failed")

        # Mock sleep to raise KeyboardInterrupt after first call
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        run_continuous_monitoring(mock_monitor, mock_notification_manager, 1, 1)

        mock_run_single_scan.assert_called_once()

    @patch("btc_tennis_bot.run_single_scan")
    @patch("btc_tennis_bot.time.sleep")
    def test_run_continuous_monitoring_max_attempts(
        self, mock_sleep, mock_run_single_scan
    ):
        """Test continuous monitoring reaching max attempts"""
        mock_monitor = MagicMock()
        mock_notification_manager = MagicMock()

        mock_run_single_scan.return_value = {}

        run_continuous_monitoring(mock_monitor, mock_notification_manager, 1, 2)

        assert mock_run_single_scan.call_count == 2
        assert mock_sleep.call_count == 1  # Only one sleep between attempts

    @patch("btc_tennis_bot.NotificationManager")
    @patch("btc_tennis_bot.CourtMonitor")
    @patch("btc_tennis_bot.BTCConfig")
    @patch("btc_tennis_bot.setup_credentials")
    @patch("btc_tennis_bot.run_single_scan")
    def test_main_success(
        self,
        mock_run_single_scan,
        mock_setup_credentials,
        mock_config_class,
        mock_monitor_class,
        mock_notification_class,
    ):
        """Test main function with successful scan"""
        # Mock credentials
        mock_credentials = {
            "username": "test@example.com",
            "password": "testpass",
            "notification_email": "test@example.com",
            "phone_number": "1234567890",
            "gmail_app_email": "test@gmail.com",
            "gmail_app_password": "testpass",
        }
        mock_setup_credentials.return_value = mock_credentials

        # Mock config
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_config.get_bot_config.return_value = {
            "base_url": "https://test.com",
            "login_url": "https://test.com/login",
            "booking_url": "https://test.com/booking",
        }

        # Mock monitor and notification manager
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        mock_notification_manager = MagicMock()
        mock_notification_class.return_value = mock_notification_manager

        # Mock scan results
        mock_courts = {
            "2024-01-01": [
                {
                    "time": "10:00 AM",
                    "text": "Book 10:00 am as 48hr",
                    "court_number": "1",
                }
            ]
        }
        mock_run_single_scan.return_value = mock_courts

        # Mock input for continuous monitoring choice
        with patch("btc_tennis_bot.input", return_value="n"):
            main()

        mock_setup_credentials.assert_called_once()
        mock_config.get_bot_config.assert_called_once()
        mock_monitor_class.assert_called_once()
        mock_notification_class.assert_called_once()
        mock_run_single_scan.assert_called_once()

    @patch("btc_tennis_bot.NotificationManager")
    @patch("btc_tennis_bot.CourtMonitor")
    @patch("btc_tennis_bot.BTCConfig")
    @patch("btc_tennis_bot.setup_credentials")
    @patch("btc_tennis_bot.run_single_scan")
    def test_main_no_courts(
        self,
        mock_run_single_scan,
        mock_setup_credentials,
        mock_config_class,
        mock_monitor_class,
        mock_notification_class,
    ):
        """Test main function with no courts found"""
        # Mock credentials
        mock_credentials = {
            "username": "test@example.com",
            "password": "testpass",
            "notification_email": "test@example.com",
            "phone_number": "1234567890",
            "gmail_app_email": "test@gmail.com",
            "gmail_app_password": "testpass",
        }
        mock_setup_credentials.return_value = mock_credentials

        # Mock config
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_config.get_bot_config.return_value = {
            "base_url": "https://test.com",
            "login_url": "https://test.com/login",
            "booking_url": "https://test.com/booking",
        }

        # Mock monitor and notification manager
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        mock_notification_manager = MagicMock()
        mock_notification_class.return_value = mock_notification_manager

        # Mock scan results - no courts
        mock_run_single_scan.return_value = {}

        # Mock input for continuous monitoring choice
        with patch("btc_tennis_bot.input", return_value="n"):
            main()

        mock_setup_credentials.assert_called_once()
        mock_config.get_bot_config.assert_called_once()
        mock_monitor_class.assert_called_once()
        mock_notification_class.assert_called_once()
        mock_run_single_scan.assert_called_once()

    @patch("btc_tennis_bot.NotificationManager")
    @patch("btc_tennis_bot.CourtMonitor")
    @patch("btc_tennis_bot.BTCConfig")
    @patch("btc_tennis_bot.setup_credentials")
    @patch("btc_tennis_bot.run_continuous_monitoring")
    def test_main_continuous_monitoring(
        self,
        mock_run_continuous_monitoring,
        mock_setup_credentials,
        mock_config_class,
        mock_monitor_class,
        mock_notification_class,
    ):
        """Test main function with continuous monitoring choice"""
        # Mock credentials
        mock_credentials = {
            "username": "test@example.com",
            "password": "testpass",
            "notification_email": "test@example.com",
            "phone_number": "1234567890",
            "gmail_app_email": "test@gmail.com",
            "gmail_app_password": "testpass",
        }
        mock_setup_credentials.return_value = mock_credentials

        # Mock config
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_config.get_bot_config.return_value = {
            "base_url": "https://test.com",
            "login_url": "https://test.com/login",
            "booking_url": "https://test.com/booking",
        }

        # Mock monitor and notification manager
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        mock_notification_manager = MagicMock()
        mock_notification_class.return_value = mock_notification_manager

        # Mock scan results
        mock_courts = {
            "2024-01-01": [
                {
                    "time": "10:00 AM",
                    "text": "Book 10:00 am as 48hr",
                    "court_number": "1",
                }
            ]
        }

        # Mock input for continuous monitoring choice
        with patch("btc_tennis_bot.input", side_effect=["1", "5", "10"]):
            with patch("btc_tennis_bot.run_single_scan", return_value=mock_courts):
                main()

        mock_setup_credentials.assert_called_once()
        mock_config.get_bot_config.assert_called_once()
        mock_monitor_class.assert_called_once()
        mock_notification_class.assert_called_once()
        mock_run_continuous_monitoring.assert_called_once()
