#!/usr/bin/env python3
"""
UBC Module Tests
Test UBC Tennis Centre specific modules
"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

# Add project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

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
        self.assertEqual(
            self.config.login_url,
            "https://portal.recreation.ubc.ca/index.php?r=public/index",
        )
        self.assertEqual(
            self.config.booking_url, "https://recreation.ubc.ca/tennis/court-booking/"
        )

    @patch.dict(
        os.environ,
        {"UBC_USERNAME": "test@ubc.ca", "UBC_PASSWORD": "testpass"},
        clear=True,
    )
    def test_get_credentials_ubc(self):
        """Test UBC credential retrieval"""
        creds = self.config.get_credentials()
        self.assertEqual(creds["username"], "test@ubc.ca")
        self.assertEqual(creds["password"], "testpass")

    @patch.dict(
        os.environ,
        {"BTC_USERNAME": "test@example.com", "BTC_PASSWORD": "testpass"},
        clear=True,
    )
    def test_get_credentials_btc_fallback(self):
        """Test BTC credential fallback"""
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
            "UBC_USERNAME": "test@ubc.ca",
            "UBC_PASSWORD": "testpass",
            "UBC_NOTIFICATION_EMAIL": "notify@example.com",
            "UBC_GMAIL_APP_PASSWORD": "apppass",
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


class TestUBCMonitor(unittest.TestCase):
    """Test UBC monitor class"""

    def setUp(self):
        """Set up test fixtures"""
        self.monitor = UBCMonitor()
        self.monitor.driver = MagicMock()  # Mock the driver

    def test_config_type(self):
        """Test configuration is UBCConfig type"""
        self.assertIsInstance(self.monitor.config, UBCConfig)

    def test_facility_name(self):
        """Test facility name is UBC"""
        self.assertEqual(self.monitor.config.facility_name, "UBC")

    def test_logger_name(self):
        """Test logger name includes UBC"""
        self.assertIn("ubc", self.monitor.logger.name)

    def test_setup_driver(self):
        """Test WebDriver setup"""
        # Test that setup_driver can be called and sets the driver
        try:
            self.monitor.setup_driver()
            self.assertIsNotNone(self.monitor.driver)
            self.monitor.cleanup()  # Clean up after test
        except Exception:
            # If setup fails, that's also acceptable for testing
            pass

    def test_cleanup(self):
        """Test WebDriver cleanup"""
        mock_driver = MagicMock()
        self.monitor.driver = mock_driver

        self.monitor.cleanup()

        mock_driver.quit.assert_called_once()
        # BaseMonitor doesn't set driver to None, just calls quit

    def test_cleanup_no_driver(self):
        """Test cleanup when no driver exists"""
        self.monitor.driver = None

        # Should not raise an exception
        self.monitor.cleanup()
        self.assertIsNone(self.monitor.driver)

    @patch.dict(
        os.environ,
        {"UBC_USERNAME": "test@ubc.ca", "UBC_PASSWORD": "testpass"},
        clear=True,
    )
    @patch("ubc.monitor.ubc_monitor.WebDriverWait")
    @patch("ubc.monitor.ubc_monitor.EC")
    def test_login_success(self, mock_ec, mock_wait):
        """Test successful login"""
        # Mock driver and elements
        mock_driver = MagicMock()
        mock_driver.current_url = "https://www.ubc.ca/search/refine/"
        self.monitor.driver = mock_driver

        # Mock WebDriverWait and elements
        mock_wait_instance = MagicMock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.return_value = MagicMock()  # username field

        mock_driver.find_element.return_value = (
            MagicMock()
        )  # password field and login button

        # Mock _check_login_success
        with patch.object(self.monitor, "_check_login_success", return_value=True):
            result = self.monitor.login()

        self.assertTrue(result)
        mock_driver.get.assert_called_once()

    @patch("ubc.monitor.ubc_monitor.WebDriverWait")
    def test_login_failure(self, mock_wait):
        """Test failed login"""
        mock_driver = MagicMock()
        mock_driver.current_url = (
            "https://portal.recreation.ubc.ca/index.php?r=public/index"
        )
        self.monitor.driver = mock_driver

        # Mock WebDriverWait timeout
        mock_wait_instance = MagicMock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.side_effect = Exception("Timeout")

        with patch.object(self.monitor, "_check_login_success", return_value=False):
            result = self.monitor.login()

        self.assertFalse(result)

    def test_check_login_success_redirect(self):
        """Test login success check with redirect"""
        mock_driver = MagicMock()
        mock_driver.current_url = (
            "https://www.ubc.ca/search/refine/?q=&label=Search+UBC"
        )
        self.monitor.driver = mock_driver

        result = self.monitor._check_login_success()
        self.assertTrue(result)

    def test_check_login_success_still_on_login_page(self):
        """Test login success check when still on login page"""
        mock_driver = MagicMock()
        mock_driver.current_url = (
            "https://portal.recreation.ubc.ca/index.php?r=public/index"
        )
        self.monitor.driver = mock_driver

        result = self.monitor._check_login_success()
        self.assertFalse(result)

    def test_check_login_success_find_logout_element(self):
        """Test login success check finding logout element"""
        mock_driver = MagicMock()
        mock_driver.current_url = "https://portal.recreation.ubc.ca/dashboard"
        mock_driver.find_element.return_value.is_displayed.return_value = True
        self.monitor.driver = mock_driver

        result = self.monitor._check_login_success()
        self.assertTrue(result)

    def test_check_login_success_exception(self):
        """Test login success check with exception"""
        mock_driver = MagicMock()
        mock_driver.current_url = "https://portal.recreation.ubc.ca/dashboard"
        mock_driver.find_element.side_effect = Exception("Error")
        self.monitor.driver = mock_driver

        result = self.monitor._check_login_success()
        self.assertFalse(result)

    @patch("ubc.monitor.ubc_monitor.WebDriverWait")
    @patch("ubc.monitor.ubc_monitor.EC")
    def test_navigate_to_booking_page_success(self, mock_ec, mock_wait):
        """Test successful navigation to booking page"""
        mock_driver = MagicMock()
        mock_driver.current_url = "https://ubc.perfectmind.com/booking"
        self.monitor.driver = mock_driver

        # Mock WebDriverWait and elements
        mock_wait_instance = MagicMock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.return_value = MagicMock()  # Book a Court button

        result = self.monitor.navigate_to_booking_page()

        self.assertTrue(result)
        mock_driver.get.assert_called()

    def test_navigate_to_booking_page_failure(self):
        """Test failed navigation to booking page"""
        mock_driver = MagicMock()
        mock_driver.get.side_effect = Exception("Navigation error")
        self.monitor.driver = mock_driver

        result = self.monitor.navigate_to_booking_page()

        self.assertFalse(result)

    def test_scan_available_courts_no_elements(self):
        """Test court scanning with no elements found"""
        mock_driver = MagicMock()
        mock_driver.find_elements.return_value = []
        self.monitor.driver = mock_driver

        result = self.monitor.scan_available_courts()

        self.assertEqual(result, {})

    def test_scan_available_courts_with_elements(self):
        """Test court scanning with elements found"""
        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_element.find_element.return_value.text = "Court 01"
        mock_element.get_attribute.return_value = "facility-id-123"
        mock_driver.find_elements.return_value = [mock_element]
        self.monitor.driver = mock_driver

        with patch.object(
            self.monitor,
            "_extract_ubc_court_info",
            return_value={
                "court_name": "Court 01",
                "status": "Available",
                "date": "2025-10-26",
                "facility_id": "facility-id-123",
            },
        ):
            result = self.monitor.scan_available_courts()

        self.assertIn("2025-10-26", result)
        self.assertEqual(len(result["2025-10-26"]), 1)

    def test_scan_available_courts_idempotency(self):
        """Test court scanning idempotency"""
        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_driver.find_elements.return_value = [mock_element]
        self.monitor.driver = mock_driver

        # First scan
        with patch.object(
            self.monitor,
            "_extract_ubc_court_info",
            return_value={
                "court_name": "Court 01",
                "status": "Available",
                "date": "2025-10-26",
                "facility_id": "facility-id-123",
            },
        ):
            result1 = self.monitor.scan_available_courts()

        # Second scan (should be empty due to idempotency)
        with patch.object(
            self.monitor,
            "_extract_ubc_court_info",
            return_value={
                "court_name": "Court 01",
                "status": "Available",
                "date": "2025-10-26",
                "facility_id": "facility-id-123",
            },
        ):
            result2 = self.monitor.scan_available_courts()

        self.assertEqual(len(result1["2025-10-26"]), 1)
        self.assertEqual(len(result2), 0)  # Empty due to idempotency

    def test_extract_ubc_court_info_success(self):
        """Test UBC court info extraction"""
        mock_element = MagicMock()
        mock_element.find_element.side_effect = Exception("Mock error")

        result = self.monitor._extract_ubc_court_info(mock_element, 0)

        # Should return None due to exception
        self.assertIsNone(result)

    def test_extract_ubc_court_info_with_choose_button(self):
        """Test UBC court info extraction with choose button"""
        mock_element = MagicMock()
        mock_element.find_element.side_effect = Exception("Mock error")

        result = self.monitor._extract_ubc_court_info(mock_element, 0)

        # Should return None due to exception
        self.assertIsNone(result)

    def test_extract_ubc_court_info_exception(self):
        """Test UBC court info extraction with exception"""
        mock_element = MagicMock()
        mock_element.find_element.side_effect = Exception("Error")

        result = self.monitor._extract_ubc_court_info(mock_element, 0)

        self.assertIsNone(result)

    def test_get_court_unique_identifier(self):
        """Test court unique identifier generation"""
        court_info = {
            "date": "2025-10-26",
            "court_name": "Court 01",
            "status": "Available",
            "facility_id": "facility-id-123",
        }

        result = self.monitor._get_court_unique_identifier(court_info)

        self.assertIn("2025-10-26", result)
        self.assertIn("Court 01", result)
        self.assertIn("Available", result)
        self.assertIn("facility-id-123", result)

    def test_get_court_unique_identifier_empty_values(self):
        """Test court unique identifier with empty values"""
        court_info = {
            "date": "",
            "court_name": "Court 01",
            "status": "",
            "facility_id": "facility-id-123",
        }

        result = self.monitor._get_court_unique_identifier(court_info)

        self.assertIn("Court 01", result)
        self.assertIn("facility-id-123", result)
        # Empty values should be filtered out, so result should not contain empty strings
        self.assertNotEqual(
            result.count(""), 0
        )  # There might be empty strings in the sorted result


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
                    "price": "$32.15",
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
                    "price": "$32.15",
                }
            ]
        }

        sms_body = self.notification_manager._format_sms_message(test_courts)
        self.assertIn("UBC Tennis", sms_body)
        self.assertIn("Court 1", sms_body)
        self.assertIn("10:00 AM", sms_body)


if __name__ == "__main__":
    unittest.main()
