"""
Unit tests for core/monitor.py
"""

import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from core.monitor import CourtMonitor


class TestCourtMonitor:
    """Test cases for CourtMonitor class"""

    def setup_method(self):
        """Setup for each test method"""
        self.config = {
            "headless": True,
            "base_url": "https://www.burnabytennis.ca/app/bookings/grid",
            "login_url": "https://www.burnabytennis.ca/login",
        }
        self.credentials = {"username": "test@example.com", "password": "testpass"}
        self.monitor = CourtMonitor(self.config, self.credentials)

    def test_init(self):
        """Test CourtMonitor initialization"""
        assert self.monitor.config == self.config
        assert self.monitor.credentials == self.credentials
        assert self.monitor.driver is None
        assert self.monitor.wait is None
        assert self.monitor.logger is not None
        assert isinstance(self.monitor.previous_courts, set)

    @patch("core.monitor.webdriver")
    @patch("core.monitor.ChromeDriverManager")
    def test_setup_driver_success(self, mock_driver_manager, mock_webdriver):
        """Test successful driver setup"""
        mock_driver_instance = MagicMock()
        mock_webdriver.Chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"

        # setup_driver doesn't return anything, it just sets up the driver
        self.monitor.setup_driver()

        assert self.monitor.driver == mock_driver_instance
        assert self.monitor.wait is not None
        mock_webdriver.Chrome.assert_called_once()

    @patch("core.monitor.webdriver")
    @patch("core.monitor.ChromeDriverManager")
    def test_setup_driver_exception(self, mock_driver_manager, mock_webdriver):
        """Test driver setup with exception"""
        mock_webdriver.Chrome.side_effect = Exception("Driver setup failed")

        with pytest.raises(Exception, match="Driver setup failed"):
            self.monitor.setup_driver()

        assert self.monitor.driver is None
        assert self.monitor.wait is None

    def test_cleanup_with_driver(self):
        """Test cleanup with active driver"""
        mock_driver = MagicMock()
        self.monitor.driver = mock_driver

        self.monitor.cleanup()

        mock_driver.quit.assert_called_once()
        # Note: cleanup doesn't set driver to None in the actual implementation

    def test_cleanup_without_driver(self):
        """Test cleanup without driver"""
        self.monitor.driver = None

        # Should not raise exception
        self.monitor.cleanup()

        assert self.monitor.driver is None

    def test_login_no_credentials(self):
        """Test login with no credentials"""
        monitor = CourtMonitor(self.config, {})

        result = monitor.login()

        assert result is True

    @patch.object(CourtMonitor, "setup_driver")
    def test_login_success(self, mock_setup_driver):
        """Test successful login"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait

        # Mock successful login attempt
        with patch.object(self.monitor, "_attempt_login", return_value=True):
            result = self.monitor.login()

        assert result is True
        mock_driver.get.assert_called()

    @patch.object(CourtMonitor, "setup_driver")
    def test_login_failure(self, mock_setup_driver):
        """Test login failure"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait

        # Mock failed login attempt
        with patch.object(self.monitor, "_attempt_login", return_value=False):
            result = self.monitor.login()

        assert result is True  # Returns True even on failure

    @patch.object(CourtMonitor, "setup_driver")
    def test_login_exception(self, mock_setup_driver):
        """Test login with exception"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_driver.get.side_effect = Exception("Login failed")

        result = self.monitor.login()

        # Login method returns True even on failure in some cases
        assert result is True

    @patch.object(CourtMonitor, "setup_driver")
    def test_navigate_to_booking_page_success(self, mock_setup_driver):
        """Test successful navigation to booking page"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        mock_element = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_wait.until.return_value = mock_element
        mock_driver.current_url = "https://www.burnabytennis.ca/app/bookings/grid"

        result = self.monitor.navigate_to_booking_page()

        assert result is True
        mock_driver.get.assert_called_with(
            "https://www.burnabytennis.ca/app/bookings/grid"
        )

    @patch.object(CourtMonitor, "setup_driver")
    def test_navigate_to_booking_page_timeout(self, mock_setup_driver):
        """Test navigation with timeout"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_wait.until.side_effect = TimeoutException("Timeout")

        result = self.monitor.navigate_to_booking_page()

        assert result is False

    @patch.object(CourtMonitor, "setup_driver")
    def test_navigate_to_booking_page_wrong_url(self, mock_setup_driver):
        """Test navigation with wrong URL"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        mock_element = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_wait.until.return_value = mock_element
        mock_driver.current_url = "https://wrong.url.com"

        result = self.monitor.navigate_to_booking_page()

        assert result is False

    @patch.object(CourtMonitor, "setup_driver")
    def test_detect_available_courts_success(self, mock_setup_driver):
        """Test successful court detection"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        # Mock button elements
        mock_button1 = MagicMock()
        mock_button1.text = "Book 6:00 am as 48hr"
        mock_button1.get_attribute.return_value = "button-class"
        mock_button1.is_displayed.return_value = True
        mock_button1.is_enabled.return_value = True

        mock_button2 = MagicMock()
        mock_button2.text = "Unavailable"
        mock_button2.get_attribute.return_value = "unavailable-class"
        mock_button2.is_displayed.return_value = True
        mock_button2.is_enabled.return_value = False

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_driver.find_elements.return_value = [mock_button1, mock_button2]

        courts = self.monitor._detect_available_courts()

        assert len(courts) == 1
        assert courts[0]["text"] == "Book 6:00 am as 48hr"
        assert courts[0]["time"] == "6:00 am"
        assert courts[0]["clickable"] is True

    @patch.object(CourtMonitor, "setup_driver")
    def test_detect_available_courts_no_courts(self, mock_setup_driver):
        """Test court detection with no available courts"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_driver.find_elements.return_value = []

        courts = self.monitor._detect_available_courts()

        assert len(courts) == 0

    @patch.object(CourtMonitor, "setup_driver")
    def test_detect_available_courts_exception(self, mock_setup_driver):
        """Test court detection with exception"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_driver.find_elements.side_effect = Exception("Detection failed")

        courts = self.monitor._detect_available_courts()

        assert len(courts) == 0

    @patch.object(CourtMonitor, "setup_driver")
    def test_navigate_to_specific_date_success(self, mock_setup_driver):
        """Test successful date navigation"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        mock_element = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_driver.find_element.return_value = mock_element
        mock_element.is_displayed.return_value = True
        mock_element.is_enabled.return_value = True

        target_date = datetime.now() + timedelta(days=1)
        result = self.monitor._navigate_to_specific_date(target_date)

        assert result is True
        mock_driver.find_element.assert_called()
        mock_element.click.assert_called_once()

    @patch.object(CourtMonitor, "setup_driver")
    def test_navigate_to_specific_date_no_toggle(self, mock_setup_driver):
        """Test date navigation with no date toggle found"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_driver.find_element.side_effect = NoSuchElementException(
            "No element found"
        )

        target_date = datetime.now() + timedelta(days=1)
        result = self.monitor._navigate_to_specific_date(target_date)

        assert result is False

    @patch.object(CourtMonitor, "setup_driver")
    def test_navigate_to_specific_date_exception(self, mock_setup_driver):
        """Test date navigation with exception"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait
        mock_driver.find_element.side_effect = Exception("Navigation failed")

        target_date = datetime.now() + timedelta(days=1)
        result = self.monitor._navigate_to_specific_date(target_date)

        assert result is False

    @patch.object(CourtMonitor, "_navigate_to_specific_date")
    @patch.object(CourtMonitor, "_detect_available_courts")
    @patch.object(CourtMonitor, "setup_driver")
    def test_scan_all_dates_success(
        self, mock_setup_driver, mock_detect_courts, mock_navigate
    ):
        """Test successful scanning of all dates"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait

        # Mock successful date navigation
        mock_navigate.return_value = True

        # Mock court detection
        mock_detect_courts.return_value = [
            {"time": "6:00 AM", "text": "Book 6:00 am as 48hr", "court_number": "1"}
        ]

        all_courts = self.monitor.scan_all_dates()

        assert len(all_courts) == 3  # today, tomorrow, day after tomorrow
        assert mock_navigate.call_count == 3
        assert mock_detect_courts.call_count == 3

    @patch.object(CourtMonitor, "_navigate_to_specific_date")
    @patch.object(CourtMonitor, "_detect_available_courts")
    @patch.object(CourtMonitor, "setup_driver")
    def test_scan_all_dates_fallback(
        self, mock_setup_driver, mock_detect_courts, mock_navigate
    ):
        """Test scanning with fallback to current page"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait

        # Mock failed date navigation
        mock_navigate.return_value = False

        # Mock court detection on current page
        mock_detect_courts.return_value = [
            {"time": "6:00 AM", "text": "Book 6:00 am as 48hr", "court_number": "1"}
        ]

        all_courts = self.monitor.scan_all_dates()

        # Should have 3 dates (today, tomorrow, day after) with fallback courts in today
        assert len(all_courts) == 3
        assert mock_navigate.call_count == 3
        assert mock_detect_courts.call_count == 1  # Only 1 fallback call

        # Check that fallback courts are in today's date
        today_key = datetime.now().strftime("%Y-%m-%d")
        assert today_key in all_courts
        assert len(all_courts[today_key]) == 1
        assert all_courts[today_key][0]["time"] == "6:00 AM"

    @patch.object(CourtMonitor, "_detect_available_courts")
    @patch.object(CourtMonitor, "setup_driver")
    def test_scan_all_dates_no_courts(self, mock_setup_driver, mock_detect_courts):
        """Test scanning with no courts found"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait

        # Mock no courts found
        mock_detect_courts.return_value = []

        all_courts = self.monitor.scan_all_dates()

        # Should have 3 dates (today, tomorrow, day after) all empty
        assert len(all_courts) == 3
        for date_courts in all_courts.values():
            assert len(date_courts) == 0

    @patch.object(CourtMonitor, "setup_driver")
    def test_detect_new_courts(self, mock_setup_driver):
        """Test new court detection"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait

        # Mock previous courts (as set of strings)
        self.monitor.previous_courts = {"2025-10-26_6:00 AM_Book 6:00 am as 48hr"}

        # Mock current courts with new addition
        current_courts = {
            "2025-10-26": [
                {
                    "time": "6:00 AM",
                    "text": "Book 6:00 am as 48hr",
                    "court_number": "1",
                },
                {
                    "time": "8:00 AM",
                    "text": "Book 8:00 am as 48hr",
                    "court_number": "2",
                },
            ]
        }

        new_courts = self.monitor.detect_new_courts(current_courts)

        assert len(new_courts) == 1
        assert new_courts["2025-10-26"][0]["time"] == "8:00 AM"

    @patch.object(CourtMonitor, "setup_driver")
    def test_detect_new_courts_no_new(self, mock_setup_driver):
        """Test new court detection with no new courts"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait

        # Mock previous courts (as set of strings)
        self.monitor.previous_courts = {"2025-10-26_6:00 AM_Book 6:00 am as 48hr"}

        # Mock current courts (same as previous)
        current_courts = {
            "2025-10-26": [
                {"time": "6:00 AM", "text": "Book 6:00 am as 48hr", "court_number": "1"}
            ]
        }

        new_courts = self.monitor.detect_new_courts(current_courts)

        assert len(new_courts) == 0

    @patch.object(CourtMonitor, "setup_driver")
    def test_detect_new_courts_first_run(self, mock_setup_driver):
        """Test new court detection on first run (no previous courts)"""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        self.monitor.driver = mock_driver
        self.monitor.wait = mock_wait

        # Mock no previous courts
        self.monitor.previous_courts = set()

        # Mock current courts
        current_courts = {
            "2025-10-26": [
                {"time": "6:00 AM", "text": "Book 6:00 am as 48hr", "court_number": "1"}
            ]
        }

        new_courts = self.monitor.detect_new_courts(current_courts)

        assert len(new_courts) == 1
        assert new_courts["2025-10-26"][0]["time"] == "6:00 AM"
