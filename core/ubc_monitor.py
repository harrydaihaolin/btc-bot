#!/usr/bin/env python3
"""
UBC Tennis Court Monitor Module
Handles UBC-specific court monitoring and booking detection
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .ubc_config import UBCConfig


class UBCCourtMonitor:
    """Monitor for UBC tennis court availability"""

    def __init__(self):
        self.config = UBCConfig()
        self.driver: Optional[webdriver.Chrome] = None
        self.logger = self._setup_logger()
        self.previous_courts: Set[str] = set()
        self.booking_system_url: Optional[str] = None

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for UBC monitoring"""
        logger = logging.getLogger("ubc_monitor")
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
        """Initialize Chrome WebDriver for UBC website"""
        try:
            self.logger.info("Initializing Chrome WebDriver for UBC...")

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
                # Check if it's a connection-related error (expected when ChromeDriver is already terminated)
                error_msg = str(e).lower()
                if any(
                    keyword in error_msg
                    for keyword in [
                        "connection refused",
                        "connection broken",
                        "newconnectionerror",
                    ]
                ):
                    self.logger.debug(
                        f"WebDriver cleanup: ChromeDriver already terminated (expected): {e}"
                    )
                else:
                    self.logger.error(f"Error during WebDriver cleanup: {e}")
            finally:
                # Ensure driver reference is cleared
                self.driver = None

    def login(self) -> bool:
        """Login to UBC Recreation system"""
        try:
            credentials = self.config.get_credentials()
            self.logger.info("Attempting to login to UBC Recreation...")

            # Navigate to login page
            self.driver.get(self.config.login_url)
            time.sleep(2)

            # Wait for login form
            wait = WebDriverWait(self.driver, 10)

            # Find username field - try multiple selectors for UBC portal
            username_selectors = [
                "input[name='LoginForm[email]']",  # UBC portal specific
                "input[type='email']",
                "input[name='username']",
                "input[name='email']",
                "input[placeholder*='Email']",
            ]

            username_field = None
            for selector in username_selectors:
                try:
                    username_field = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.logger.info(f"Found username field with selector: {selector}")
                    break
                except TimeoutException:
                    continue

            if not username_field:
                raise TimeoutException("Could not find username field")

            # Find password field
            password_field = self.driver.find_element(
                By.CSS_SELECTOR, "input[type='password']"
            )

            # Fill credentials
            username_field.clear()
            username_field.send_keys(credentials["username"])

            password_field.clear()
            password_field.send_keys(credentials["password"])

            # Find and click login button - try multiple selectors
            login_selectors = [
                "input[type='submit'][value='Login']",  # UBC portal specific
                "button[type='submit']",
                "input[type='submit']",
                ".login-button",
                "button:contains('Login')",
            ]

            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found login button with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if not login_button:
                raise NoSuchElementException("Could not find login button")

            login_button.click()

            # Wait for login to complete
            time.sleep(3)

            # Check if login was successful
            if self._check_login_success():
                self.logger.info("Login successful!")
                return True
            else:
                self.logger.error(
                    "Login failed - invalid credentials or captcha required"
                )
                return False

        except TimeoutException:
            self.logger.error("Login timeout - page elements not found")
            return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False

    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            # Look for indicators of successful login
            # Could be absence of login form, presence of user menu, etc.
            current_url = self.driver.current_url

            # If we're redirected away from login page, likely successful
            if "login" not in current_url.lower():
                return True

            # Check for user menu or profile elements
            user_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".user-menu, .profile, .account, [data-testid='user-menu']",
            )
            if user_elements:
                return True

            # Check for error messages
            error_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".error, .alert-danger, .login-error"
            )
            if error_elements:
                error_text = error_elements[0].text.lower()
                if "invalid" in error_text or "incorrect" in error_text:
                    return False

            return False

        except Exception:
            return False

    def navigate_to_booking_page(self) -> bool:
        """Navigate to UBC tennis court booking page"""
        try:
            self.logger.info("Navigating to UBC tennis booking page...")

            # Navigate to tennis booking page
            self.driver.get(self.config.booking_url)
            time.sleep(3)

            # Look for "Book a Court" button
            wait = WebDriverWait(self.driver, 10)

            try:
                book_button = wait.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Book a Court"))
                )
                book_button.click()
                time.sleep(3)

                # Store the booking system URL
                self.booking_system_url = self.driver.current_url
                self.logger.info(
                    f"Successfully navigated to booking system: {self.booking_system_url}"
                )
                return True

            except TimeoutException:
                # Try alternative selectors
                book_selectors = [
                    "a[href*='book']",
                    "button:contains('Book')",
                    ".book-court",
                    "[data-testid='book-court']",
                ]

                for selector in book_selectors:
                    try:
                        book_element = self.driver.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        book_element.click()
                        time.sleep(3)
                        self.booking_system_url = self.driver.current_url
                        self.logger.info(
                            f"Found booking system via selector '{selector}': {self.booking_system_url}"
                        )
                        return True
                    except NoSuchElementException:
                        continue

                self.logger.error("Could not find 'Book a Court' button")
                return False

        except Exception as e:
            self.logger.error(f"Error navigating to booking page: {e}")
            return False

    def set_items_per_page(self) -> bool:
        """Set display to show all items per page"""
        try:
            self.logger.info("Setting items per page to 'All'...")

            # Look for pagination or items per page selector
            selectors = [
                "select[name='per_page']",
                "select[name='items_per_page']",
                ".per-page-select",
                "[data-testid='per-page']",
                "select:contains('per page')",
            ]

            for selector in selectors:
                try:
                    per_page_select = self.driver.find_element(
                        By.CSS_SELECTOR, selector
                    )

                    # Look for "All" option
                    from selenium.webdriver.support.ui import Select

                    select_obj = Select(per_page_select)

                    # Try to select "All" option
                    try:
                        select_obj.select_by_visible_text("All")
                        self.logger.info("Set items per page to 'All'")
                        time.sleep(2)
                        return True
                    except NoSuchElementException:
                        # Try alternative values
                        for option in ["100", "50", "25"]:
                            try:
                                select_obj.select_by_visible_text(option)
                                self.logger.info(f"Set items per page to '{option}'")
                                time.sleep(2)
                                return True
                            except NoSuchElementException:
                                continue

                except NoSuchElementException:
                    continue

            self.logger.warning(
                "Could not find items per page selector, continuing with default"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error setting items per page: {e}")
            return False

    def scan_available_courts(self) -> Dict[str, List[Dict]]:
        """Scan for available UBC tennis courts"""
        try:
            self.logger.info("Scanning for available UBC tennis courts...")

            # Set items per page first
            self.set_items_per_page()

            # Look for court elements
            court_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".court-item, .booking-item, [data-testid='court'], .tennis-court",
            )

            available_courts = {}
            current_date = datetime.now().strftime("%Y-%m-%d")

            if not court_elements:
                # Try alternative selectors
                court_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "tr[data-court], .court-row, .booking-row"
                )

            if court_elements:
                self.logger.info(f"Found {len(court_elements)} court elements")

                for i, court_element in enumerate(court_elements):
                    try:
                        court_info = self._extract_court_info(court_element, i)
                        if court_info:
                            if current_date not in available_courts:
                                available_courts[current_date] = []
                            available_courts[current_date].append(court_info)

                    except Exception as e:
                        self.logger.warning(
                            f"Error extracting court info from element {i}: {e}"
                        )
                        continue
            else:
                self.logger.warning("No court elements found on page")

            # Log results
            total_courts = sum(len(courts) for courts in available_courts.values())
            self.logger.info(f"Found {total_courts} available courts")

            for date, courts in available_courts.items():
                self.logger.info(f"  {date}: {len(courts)} courts")
                for court in courts:
                    self.logger.info(
                        f"    - {court.get('court_name', 'Unknown')} at {court.get('time', 'Unknown')}"
                    )

            return available_courts

        except Exception as e:
            self.logger.error(f"Error scanning courts: {e}")
            return {}

    def _extract_court_info(self, court_element, index: int) -> Optional[Dict]:
        """Extract court information from a court element"""
        try:
            court_info = {
                "court_name": f"Court {index + 1}",
                "time": "Unknown",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "price": "Unknown",
                "duration": "1 hour",
                "available": True,
                "element": court_element,
            }

            # Try to extract court name
            name_selectors = [
                ".court-name",
                ".court-number",
                '[data-testid="court-name"]',
            ]
            for selector in name_selectors:
                try:
                    name_element = court_element.find_element(By.CSS_SELECTOR, selector)
                    court_info["court_name"] = name_element.text.strip()
                    break
                except NoSuchElementException:
                    continue

            # Try to extract time
            time_selectors = [
                ".time",
                ".booking-time",
                '[data-testid="time"]',
                ".slot-time",
            ]
            for selector in time_selectors:
                try:
                    time_element = court_element.find_element(By.CSS_SELECTOR, selector)
                    court_info["time"] = time_element.text.strip()
                    break
                except NoSuchElementException:
                    continue

            # Try to extract price
            price_selectors = [
                ".price",
                ".cost",
                '[data-testid="price"]',
                ".booking-price",
            ]
            for selector in price_selectors:
                try:
                    price_element = court_element.find_element(
                        By.CSS_SELECTOR, selector
                    )
                    court_info["price"] = price_element.text.strip()
                    break
                except NoSuchElementException:
                    continue

            # Look for "Choose" or "Book" button
            choose_selectors = [
                "button:contains('Choose')",
                "button:contains('Book')",
                "a:contains('Choose')",
                "a:contains('Book')",
                ".choose-button",
                ".book-button",
            ]

            for selector in choose_selectors:
                try:
                    choose_button = court_element.find_element(
                        By.CSS_SELECTOR, selector
                    )
                    if choose_button.is_enabled():
                        court_info["choose_button"] = choose_button
                        break
                except NoSuchElementException:
                    continue

            # Only return if we found a choose/book button
            if "choose_button" in court_info:
                return court_info
            else:
                return None

        except Exception as e:
            self.logger.warning(f"Error extracting court info: {e}")
            return None

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
            self.logger.info("Starting UBC monitoring cycle...")

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
                    f"🎾 NEW UBC COURTS DETECTED! {total_new} new slots found!"
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
