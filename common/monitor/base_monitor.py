#!/usr/bin/env python3
"""
Common Monitor Base Class
Shared monitoring functionality for all tennis court monitors
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from common.config.base_config import BaseConfig


class BaseMonitor(ABC):
    """Base monitor class for tennis court availability"""

    def __init__(self, config: BaseConfig):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.logger = self._setup_logger()
        self.previous_courts: Set[str] = set()
        self.booking_system_url: Optional[str] = None

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for monitoring"""
        logger = logging.getLogger(f"{self.config.facility_name.lower()}_monitor")
        logger.setLevel(getattr(logging, self.config.get_logging_config()["log_level"]))

        # Create file handler
        file_handler = logging.FileHandler(self.config.get_logging_config()["log_file"])
        file_handler.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(self.config.get_logging_config()["log_format"])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def setup_driver(self) -> None:
        """Initialize Chrome WebDriver"""
        try:
            self.logger.info(
                f"Initializing Chrome WebDriver for {self.config.facility_name}..."
            )

            # Setup Chrome options
            chrome_options = webdriver.ChromeOptions()
            browser_config = self.config.get_browser_config()

            if browser_config["headless"]:
                chrome_options.add_argument("--headless")

            chrome_options.add_argument(
                f'--window-size={browser_config["window_size"][0]},{browser_config["window_size"][1]}'
            )
            chrome_options.add_argument(f'--user-agent={browser_config["user_agent"]}')
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")

            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Set timeouts
            self.driver.implicitly_wait(browser_config["implicit_wait"])
            self.driver.set_page_load_timeout(browser_config["page_load_timeout"])

            self.logger.info("Chrome WebDriver initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def cleanup(self) -> None:
        """Clean up WebDriver resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver cleaned up successfully")
            except Exception as e:
                self.logger.error(f"Error during WebDriver cleanup: {e}")

    @abstractmethod
    def login(self) -> bool:
        """Login to the facility's booking system"""
        pass

    @abstractmethod
    def navigate_to_booking_page(self) -> bool:
        """Navigate to the facility's booking page"""
        pass

    @abstractmethod
    def scan_available_courts(self) -> Dict[str, List[Dict]]:
        """Scan for available courts"""
        pass

    def get_new_courts(
        self, current_courts: Dict[str, List[Dict]]
    ) -> Dict[str, List[Dict]]:
        """Compare current courts with previous scan to find new availability"""
        new_courts = {}

        for date, courts in current_courts.items():
            new_courts_for_date = []

            for court in courts:
                # Create unique identifier for court
                court_id = (
                    f"{date}_{court.get('court_name', '')}_{court.get('time', '')}"
                )

                if court_id not in self.previous_courts:
                    new_courts_for_date.append(court)
                    self.previous_courts.add(court_id)

            if new_courts_for_date:
                new_courts[date] = new_courts_for_date

        return new_courts

    def run_monitoring_cycle(self) -> Dict[str, List[Dict]]:
        """Run a complete monitoring cycle"""
        try:
            self.logger.info(
                f"Starting {self.config.facility_name} monitoring cycle..."
            )

            # Setup driver if not already done
            if not self.driver:
                self.setup_driver()

            # Login
            if not self.login():
                raise Exception("Login failed")

            # Navigate to booking page
            if not self.navigate_to_booking_page():
                raise Exception("Failed to navigate to booking page")

            # Scan for available courts
            available_courts = self.scan_available_courts()

            # Find new courts
            new_courts = self.get_new_courts(available_courts)

            if new_courts:
                total_new = sum(len(courts) for courts in new_courts.values())
                self.logger.info(
                    f"🎾 NEW {self.config.facility_name.upper()} COURTS DETECTED! {total_new} new slots found!"
                )
            else:
                self.logger.info("No new courts detected")

            return new_courts

        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {e}")
            return {}
        finally:
            # Cleanup driver
            self.cleanup()
            self.driver = None
