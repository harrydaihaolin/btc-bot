#!/usr/bin/env python3
"""
BTC Tennis Club Monitor
Burnaby Tennis Club specific monitoring logic
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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.monitor.base_monitor import BaseMonitor
from btc.config.btc_config import BTCConfig


class BTCMonitor(BaseMonitor):
    """Monitor for Burnaby Tennis Club court availability"""
    
    def __init__(self):
        config = BTCConfig()
        super().__init__(config)
    
    def login(self) -> bool:
        """Login to BTC booking system"""
        try:
            credentials = self.config.get_credentials()
            self.logger.info("Attempting to login to BTC...")
            
            # Navigate to login page
            self.driver.get(self.config.login_url)
            time.sleep(2)
            
            # Wait for login form
            wait = WebDriverWait(self.driver, 10)
            
            # Find username field
            username_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='username'], input[name='email']"))
            )
            
            # Find password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            # Fill credentials
            username_field.clear()
            username_field.send_keys(credentials['username'])
            
            password_field.clear()
            password_field.send_keys(credentials['password'])
            
            # Find and click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .login-button")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(3)
            
            # Check if login was successful
            if self._check_login_success():
                self.logger.info("Login successful!")
                return True
            else:
                self.logger.error("Login failed - invalid credentials or captcha required")
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
            current_url = self.driver.current_url
            
            # If we're redirected away from login page, likely successful
            if 'login' not in current_url.lower():
                return True
            
            # Check for user menu or profile elements
            user_elements = self.driver.find_elements(By.CSS_SELECTOR, ".user-menu, .profile, .account, [data-testid='user-menu']")
            if user_elements:
                return True
            
            # Check for error messages
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, .login-error")
            if error_elements:
                error_text = error_elements[0].text.lower()
                if 'invalid' in error_text or 'incorrect' in error_text:
                    return False
            
            return False
            
        except Exception:
            return False
    
    def navigate_to_booking_page(self) -> bool:
        """Navigate to BTC booking page"""
        try:
            self.logger.info("Navigating to BTC booking page...")
            
            # Navigate to booking page
            self.driver.get(self.config.booking_url)
            time.sleep(3)
            
            # Check if we're on the booking page
            if "bookings/grid" in self.driver.current_url:
                self.logger.info("Successfully navigated to BTC booking page")
                return True
            else:
                self.logger.error("Failed to navigate to BTC booking page")
                return False
                
        except Exception as e:
            self.logger.error(f"Error navigating to booking page: {e}")
            return False
    
    def scan_available_courts(self) -> Dict[str, List[Dict]]:
        """Scan for available BTC courts"""
        try:
            self.logger.info("Scanning for available BTC courts...")
            
            # Check today, tomorrow, and day after tomorrow
            dates_to_check = [
                (0, "today"),
                (1, "tomorrow"),
                (2, "day after tomorrow")
            ]
            
            all_courts = {}
            date_navigation_successful = False
            
            for days_offset, date_label in dates_to_check:
                try:
                    self.logger.info(f"Checking {date_label} (offset: {days_offset} days)")
                    
                    # Calculate target date
                    target_date = datetime.now() + timedelta(days=days_offset)
                    date_str = target_date.strftime("%Y-%m-%d")
                    
                    # Navigate to specific date
                    if self._navigate_to_specific_date(target_date):
                        date_navigation_successful = True
                        # Detect available courts for this date
                        courts = self._detect_available_courts()
                        if courts:
                            # Add date information to each court
                            for court in courts:
                                court['date'] = target_date.strftime("%Y-%m-%d")
                                court['date_label'] = date_label
                            
                            all_courts[date_str] = courts
                            self.logger.info(f"Found {len(courts)} courts for {date_label}")
                        else:
                            self.logger.info(f"No courts available for {date_label}")
                            all_courts[date_str] = []
                    else:
                        self.logger.warning(f"Failed to navigate to {date_label}")
                        all_courts[date_str] = []
                        
                except Exception as e:
                    self.logger.error(f"Error checking {date_label}: {e}")
                    all_courts[date_str] = []
            
            # If date navigation failed completely, fall back to scanning current page
            if not date_navigation_successful:
                self.logger.warning("Date navigation failed for all dates, falling back to current page scan")
                try:
                    courts = self._detect_available_courts()
                    if courts:
                        # Use today's date for current page courts
                        today = datetime.now()
                        date_str = today.strftime("%Y-%m-%d")
                        
                        # Add date information to each court
                        for court in courts:
                            court['date'] = date_str
                            court['date_label'] = "current page"
                        
                        all_courts[date_str] = courts
                        self.logger.info(f"Found {len(courts)} courts on current page (fallback mode)")
                    else:
                        self.logger.info("No courts found on current page (fallback mode)")
                except Exception as e:
                    self.logger.error(f"Error in fallback court detection: {e}")
            
            # Log results
            total_courts = sum(len(courts) for courts in all_courts.values())
            self.logger.info(f"Found {total_courts} available BTC courts")
            
            for date, courts in all_courts.items():
                self.logger.info(f"  {date}: {len(courts)} courts")
                for court in courts:
                    self.logger.info(f"    - {court.get('court_name', 'Unknown')} at {court.get('time', 'Unknown')}")
            
            return all_courts
            
        except Exception as e:
            self.logger.error(f"Error scanning BTC courts: {e}")
            return {}
    
    def _navigate_to_specific_date(self, target_date: datetime) -> bool:
        """Navigate to a specific date on the BTC booking page"""
        try:
            # Look for date navigation elements
            date_selectors = [
                f"button:contains('{target_date.strftime('%B %d, %Y')}')",
                f"button:contains('{target_date.strftime('%b %d')}')",
                f"[data-date='{target_date.strftime('%Y-%m-%d')}']",
                ".date-picker button",
                ".calendar button"
            ]
            
            for selector in date_selectors:
                try:
                    date_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    date_button.click()
                    time.sleep(2)
                    return True
                except NoSuchElementException:
                    continue
            
            self.logger.warning("Could not find date toggle")
            return False
            
        except Exception as e:
            self.logger.error(f"Error navigating to date: {e}")
            return False
    
    def _detect_available_courts(self) -> List[Dict]:
        """Detect available courts on the current page"""
        try:
            self.logger.info("Scanning for available courts...")
            
            # Look for "Book" buttons
            book_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button:contains('Book'), a:contains('Book')")
            
            courts = []
            for i, button in enumerate(book_buttons):
                try:
                    button_text = button.text.strip()
                    if 'Book' in button_text and button.is_enabled():
                        court_info = {
                            'court_name': f"Court {i + 1}",
                            'time': 'Unknown',
                            'date': datetime.now().strftime("%Y-%m-%d"),
                            'price': 'Unknown',
                            'duration': '1 hour',
                            'available': True,
                            'element': button
                        }
                        
                        # Try to extract time from button text
                        if ':' in button_text:
                            time_part = button_text.split(':')[0].split()[-1]
                            court_info['time'] = time_part
                        
                        courts.append(court_info)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing court button {i}: {e}")
                    continue
            
            self.logger.info(f"Found {len(courts)} available courts")
            return courts
            
        except Exception as e:
            self.logger.error(f"Error detecting courts: {e}")
            return []
