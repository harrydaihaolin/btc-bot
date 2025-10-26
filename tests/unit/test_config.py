"""
Unit tests for core/config.py
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from core.config import BTCConfig


class TestBTCConfig:
    """Test cases for BTCConfig class"""

    def setup_method(self):
        """Setup for each test method"""
        self.config = BTCConfig()

    def test_init(self):
        """Test BTCConfig initialization"""
        assert self.config is not None
        assert hasattr(self.config, "logger")

    @patch.dict(
        os.environ,
        {
            "BTC_USERNAME": "test@example.com",
            "BTC_PASSWORD": "testpass",
            "BTC_NOTIFICATION_EMAIL": "notify@example.com",
            "BTC_PHONE_NUMBER": "1234567890",
            "BTC_GMAIL_APP_EMAIL": "gmail@gmail.com",
            "BTC_GMAIL_APP_PASSWORD": "apppass",
        },
    )
    def test_get_credentials_success(self):
        """Test getting credentials from environment variables"""
        credentials = self.config.get_credentials()

        assert credentials["username"] == "test@example.com"
        assert credentials["password"] == "testpass"
        assert credentials["notification_email"] == "notify@example.com"
        assert credentials["phone_number"] == "1234567890"
        assert credentials["gmail_app_email"] == "gmail@gmail.com"
        assert credentials["gmail_app_password"] == "apppass"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_credentials_empty(self):
        """Test getting credentials when environment variables are not set"""
        credentials = self.config.get_credentials()

        assert credentials["username"] is None
        assert credentials["password"] is None
        assert credentials["notification_email"] is None
        assert credentials["phone_number"] is None
        assert credentials["gmail_app_email"] is None
        assert credentials["gmail_app_password"] is None

    @patch.dict(
        os.environ,
        {
            "BTC_USERNAME": "test@example.com",
            "BTC_PASSWORD": "testpass",
            "BTC_NOTIFICATION_EMAIL": "notify@example.com",
            "BTC_PHONE_NUMBER": "1234567890",
            "BTC_GMAIL_APP_EMAIL": "gmail@gmail.com",
            "BTC_GMAIL_APP_PASSWORD": "apppass",
        },
    )
    def test_validate_credentials_success(self):
        """Test credential validation with all required fields"""
        credentials = self.config.get_credentials()
        result = self.config.validate_credentials(credentials)

        assert result is True

    @patch.dict(
        os.environ,
        {
            "BTC_USERNAME": "test@example.com",
            "BTC_PASSWORD": "testpass",
            "BTC_NOTIFICATION_EMAIL": "notify@example.com",
            "BTC_PHONE_NUMBER": "1234567890",
            "BTC_GMAIL_APP_EMAIL": "gmail@gmail.com",
            # Missing BTC_GMAIL_APP_PASSWORD
        },
        clear=True,
    )
    def test_validate_credentials_missing_field(self):
        """Test credential validation with missing required field"""
        credentials = self.config.get_credentials()
        result = self.config.validate_credentials(credentials)

        assert result is False

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_credentials_all_missing(self):
        """Test credential validation with all fields missing"""
        credentials = self.config.get_credentials()
        result = self.config.validate_credentials(credentials)

        assert result is False

    @patch.dict(
        os.environ,
        {
            "BTC_MONITORING_INTERVAL": "30",
            "BTC_MAX_ATTEMPTS": "10",
            "BTC_WAIT_TIMEOUT": "20",
        },
    )
    def test_get_monitoring_config_custom(self):
        """Test getting custom monitoring configuration"""
        config = self.config.get_monitoring_config()

        assert config["monitoring_interval"] == 30
        assert config["max_attempts"] == 10
        assert config["wait_timeout"] == 20

    @patch.dict(os.environ, {}, clear=True)
    def test_get_monitoring_config_defaults(self):
        """Test getting default monitoring configuration"""
        config = self.config.get_monitoring_config()

        assert config["monitoring_interval"] == 5
        assert config["max_attempts"] == 0
        assert config["wait_timeout"] == 15

    @patch.dict(
        os.environ,
        {
            "BTC_HEADLESS": "false",
            "BTC_BASE_URL": "https://custom.example.com",
            "BTC_LOGIN_URL": "https://custom.example.com/login",
        },
        clear=True,
    )
    def test_get_bot_config_custom(self):
        """Test getting custom bot configuration"""
        config = self.config.get_bot_config()

        assert config["headless"] is False
        # Note: Implementation doesn't support custom URLs, uses hardcoded values
        assert config["base_url"] == "https://www.burnabytennis.ca/app/bookings/grid"
        assert config["login_url"] == "https://www.burnabytennis.ca/login"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_bot_config_defaults(self):
        """Test getting default bot configuration"""
        config = self.config.get_bot_config()

        assert config["headless"] is True
        assert config["base_url"] == "https://www.burnabytennis.ca/app/bookings/grid"
        assert config["login_url"] == "https://www.burnabytennis.ca/login"

    @patch.dict(os.environ, {"BTC_HEADLESS": "true"})
    def test_get_bot_config_headless_true(self):
        """Test headless configuration with 'true' string"""
        config = self.config.get_bot_config()
        assert config["headless"] is True

    @patch.dict(os.environ, {"BTC_HEADLESS": "True"})
    def test_get_bot_config_headless_true_capitalized(self):
        """Test headless configuration with 'True' string"""
        config = self.config.get_bot_config()
        assert config["headless"] is True

    @patch.dict(os.environ, {"BTC_HEADLESS": "false"})
    def test_get_bot_config_headless_false(self):
        """Test headless configuration with 'false' string"""
        config = self.config.get_bot_config()
        assert config["headless"] is False

    @patch.dict(os.environ, {"BTC_HEADLESS": "0"})
    def test_get_bot_config_headless_zero(self):
        """Test headless configuration with '0' string"""
        config = self.config.get_bot_config()
        assert config["headless"] is False

    def test_validate_credentials_empty_dict(self):
        """Test credential validation with empty dictionary"""
        result = self.config.validate_credentials({})
        assert result is False

    def test_validate_credentials_none_values(self):
        """Test credential validation with None values"""
        credentials = {
            "username": None,
            "password": None,
            "notification_email": None,
            "phone_number": None,
            "gmail_app_email": None,
            "gmail_app_password": None,
        }
        result = self.config.validate_credentials(credentials)
        assert result is False

    def test_validate_credentials_empty_strings(self):
        """Test credential validation with empty strings"""
        credentials = {
            "username": "",
            "password": "",
            "notification_email": "",
            "phone_number": "",
            "gmail_app_email": "",
            "gmail_app_password": "",
        }
        result = self.config.validate_credentials(credentials)
        assert result is False
