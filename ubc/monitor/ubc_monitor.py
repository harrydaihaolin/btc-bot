#!/usr/bin/env python3
"""
UBC Tennis Centre Monitor
UBC Recreation specific monitoring logic
"""

import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from common.monitor.base_monitor import BaseMonitor
from ubc.config.ubc_config import UBCConfig


class UBCMonitor(BaseMonitor):
    """Monitor for UBC Tennis Centre court availability"""

    def __init__(self):
        config = UBCConfig()
        super().__init__(config)

    def login(self) -> bool:
        """Login to UBC Recreation system"""
        try:
            credentials = self.config.get_credentials()
            self.logger.info("Attempting to login to UBC Recreation...")

            # Navigate to login page
            self.driver.get(self.config.login_url)
            time.sleep(2)

            # Wait for login form
            wait = WebDriverWait(self.driver, 5)

            # Find username field - try multiple selectors for UBC portal
            username_selectors = [
                "input[name='CredentialForm[email]']",  # UBC portal specific
                "input[id='inputEmail']",  # UBC portal specific
                "input[name='LoginForm[email]']",
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
                By.CSS_SELECTOR,
                "input[name='CredentialForm[password_curr]'], input[id='inputPassword'], input[type='password']",
            )

            # Wait for elements to be interactable
            wait.until(EC.element_to_be_clickable(username_field))
            wait.until(EC.element_to_be_clickable(password_field))

            # Scroll to make sure elements are visible
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                username_field,
            )
            time.sleep(1)

            # Fill credentials with JavaScript to avoid interaction issues
            self.driver.execute_script("arguments[0].value = '';", username_field)
            self.driver.execute_script(
                "arguments[0].value = arguments[1];",
                username_field,
                credentials["username"],
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
                username_field,
            )

            # Scroll to password field
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                password_field,
            )
            time.sleep(1)

            self.driver.execute_script("arguments[0].value = '';", password_field)
            self.driver.execute_script(
                "arguments[0].value = arguments[1];",
                password_field,
                credentials["password"],
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
                password_field,
            )

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

            # Scroll to login button and try to make it clickable
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                login_button,
            )
            time.sleep(1)

            # Try to make button clickable if it's not already
            try:
                wait.until(EC.element_to_be_clickable(login_button))
            except TimeoutException:
                self.logger.warning(
                    "Button not clickable, proceeding with form submission attempts"
                )

            # Try multiple approaches to submit the form
            form_submitted = False

            # Approach 1: Try regular click first
            try:
                login_button.click()
                form_submitted = True
                self.logger.info("Form submitted using regular click")
            except Exception as e:
                self.logger.warning(f"Regular click failed: {e}")

            # Approach 2: Try JavaScript click
            if not form_submitted:
                try:
                    self.driver.execute_script("arguments[0].click();", login_button)
                    form_submitted = True
                    self.logger.info("Form submitted using JavaScript click")
                except Exception as e:
                    self.logger.warning(f"JavaScript click failed: {e}")

            # Approach 3: Try form.submit()
            if not form_submitted:
                try:
                    form = login_button.find_element(By.XPATH, "./ancestor::form")
                    self.driver.execute_script("arguments[0].submit();", form)
                    form_submitted = True
                    self.logger.info("Form submitted using form.submit()")
                except Exception as e:
                    self.logger.warning(f"Form.submit() failed: {e}")

            # Approach 4: Try dispatching submit event
            if not form_submitted:
                try:
                    form = login_button.find_element(By.XPATH, "./ancestor::form")
                    self.driver.execute_script(
                        """
                        var form = arguments[0];
                        var event = new Event('submit', {bubbles: true, cancelable: true});
                        form.dispatchEvent(event);
                    """,
                        form,
                    )
                    form_submitted = True
                    self.logger.info("Form submitted using dispatch submit event")
                except Exception as e:
                    self.logger.warning(f"Dispatch submit event failed: {e}")

            # Approach 5: Try Enter key on password field
            if not form_submitted:
                try:
                    password_field.send_keys("\n")  # Send Enter key
                    form_submitted = True
                    self.logger.info("Form submitted using Enter key on password field")
                except Exception as e:
                    self.logger.warning(f"Enter key submission failed: {e}")

            if not form_submitted:
                self.logger.error("All form submission methods failed")
                return False

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

        except TimeoutException as e:
            self.logger.warning(
                f"Login timeout - checking if login actually succeeded: {e}"
            )
            # Even if there's a timeout, check if login was successful
            if self._check_login_success():
                self.logger.info("Login successful despite timeout!")
                return True
            else:
                self.logger.error("Login failed - timeout and no success indicators")
                return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False

    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            # Wait a bit for the page to load after login
            time.sleep(2)

            current_url = self.driver.current_url
            self.logger.info(f"Current URL after login attempt: {current_url}")

            # If we're still on the login page, login likely failed
            if (
                "login" in current_url.lower()
                or "index.php?r=public/index" in current_url
            ):
                self.logger.warning("Still on login page, login likely failed")
                return False

            # UBC-specific: If we're redirected to UBC search or main site, login was successful
            if "ubc.ca" in current_url and "search" in current_url:
                self.logger.info("Redirected to UBC search page, login successful")
                return True

            # Look for elements that indicate successful login
            success_indicators = [
                "//a[contains(text(), 'Logout')]",
                "//a[contains(text(), 'Sign Out')]",
                "//button[contains(text(), 'Logout')]",
                "//*[contains(@class, 'user-menu')]",
                "//*[contains(@class, 'profile')]",
                "//*[contains(text(), 'Welcome')]",
                "//*[contains(text(), 'Dashboard')]",
            ]

            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        self.logger.info(f"Found login success indicator: {indicator}")
                        return True
                except NoSuchElementException:
                    continue

            # If we're on a different page and no explicit logout found,
            # but we're not on login page, consider it successful
            if current_url != self.config.login_url:
                self.logger.info(
                    "Redirected away from login page, considering login successful"
                )
                return True

            self.logger.warning("No clear login success indicators found")
            return False

        except Exception as e:
            self.logger.error(f"Error checking login success: {e}")
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

    def scan_available_courts(self) -> Dict[str, List[Dict]]:
        """Scan for available UBC tennis courts with idempotency"""
        try:
            self.logger.info("Scanning for available UBC tennis courts...")

            available_courts = {}
            current_date = datetime.now().strftime("%Y-%m-%d")

            # Look for court facility elements (UBC uses facility list)
            court_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".facility-details"
            )

            if not court_elements:
                # Try alternative selectors for court containers
                court_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "[data-facilityid], .facility-item, .court-container",
                )

            if court_elements:
                self.logger.info(f"Found {len(court_elements)} court facility elements")

                for i, court_element in enumerate(court_elements):
                    try:
                        court_info = self._extract_ubc_court_info(court_element, i)
                        if court_info:
                            # Generate unique identifier for idempotency
                            court_id = self._get_court_unique_identifier(court_info)

                            # Only add if we haven't seen this court before
                            if court_id not in self.previous_courts:
                                if current_date not in available_courts:
                                    available_courts[current_date] = []
                                available_courts[current_date].append(court_info)
                                self.previous_courts.add(court_id)
                                self.logger.info(
                                    f"New UBC court detected: {court_info['court_name']} - {court_info['status']}"
                                )
                            else:
                                self.logger.debug(
                                    f"UBC court already seen: {court_info['court_name']} - {court_info['status']}"
                                )

                    except Exception as e:
                        self.logger.warning(
                            f"Error extracting court info from element {i}: {e}"
                        )
                        continue
            else:
                self.logger.warning("No court facility elements found on page")

            # Log results
            total_courts = sum(len(courts) for courts in available_courts.values())
            if total_courts > 0:
                self.logger.info(f"Found {total_courts} NEW available UBC courts")
                for date, courts in available_courts.items():
                    self.logger.info(f"  {date}: {len(courts)} courts")
                    for court in courts:
                        self.logger.info(
                            f"    - {court.get('court_name', 'Unknown')} - {court.get('status', 'Available')}"
                        )
            else:
                self.logger.info("No NEW UBC courts detected (all previously seen)")

            return available_courts

        except Exception as e:
            self.logger.error(f"Error scanning UBC courts: {e}")
            return {}

    def _set_items_per_page(self) -> bool:
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

    def _extract_ubc_court_info(self, court_element, index: int) -> Optional[Dict]:
        """Extract UBC court information from a facility element"""
        try:
            court_info = {
                "court_name": f"Court {index + 1:02d}",  # UBC uses Court 01, Court 02 format
                "time": "Available",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "price": "Unknown",
                "duration": "1 hour",
                "available": True,
                "status": "Available",
                "element": court_element,
            }

            # Try to extract court name from h2 element
            try:
                name_element = court_element.find_element(By.TAG_NAME, "h2")
                court_name = name_element.text.strip()
                if court_name:
                    court_info["court_name"] = court_name
            except NoSuchElementException:
                pass

            # Try to extract facility ID
            try:
                facility_id = court_element.get_attribute("data-facilityid")
                if facility_id:
                    court_info["facility_id"] = facility_id
            except Exception:
                pass

            # Look for Choose button to determine availability
            try:
                choose_button = court_element.find_element(
                    By.CSS_SELECTOR, "a[onclick*='onChooseClick']"
                )
                if choose_button and choose_button.is_displayed():
                    court_info["available"] = True
                    court_info["status"] = "Available for booking"
                    court_info["element"] = choose_button
                else:
                    court_info["available"] = False
                    court_info["status"] = "Not available"
            except NoSuchElementException:
                court_info["available"] = False
                court_info["status"] = "No booking option found"

            # Try to extract location information
            try:
                location_element = court_element.find_element(
                    By.CSS_SELECTOR, ".facility-location"
                )
                location_text = location_element.text.strip()
                if location_text:
                    court_info["location"] = location_text
            except NoSuchElementException:
                pass

            self.logger.info(
                f"Extracted UBC court info: {court_info['court_name']} - {court_info['status']}"
            )
            return court_info

        except Exception as e:
            self.logger.warning(f"Error extracting UBC court info: {e}")
            return None

    def _get_court_unique_identifier(self, court_info: Dict[str, Any]) -> str:
        """Generate unique identifier for UBC court to prevent duplicate notifications"""
        court_strings = [
            court_info.get("date", ""),
            court_info.get("court_name", ""),
            court_info.get("status", ""),
            court_info.get("facility_id", ""),
        ]
        # Filter out empty strings and join
        court_strings = [s for s in court_strings if s]
        return "_".join(sorted(court_strings))
