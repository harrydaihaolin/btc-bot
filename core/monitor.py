"""
Core monitoring functionality for BTC Tennis Bot
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

class CourtMonitor:
    """Core monitoring functionality for tennis court availability"""
    
    def __init__(self, config: Dict, credentials: Dict[str, str]):
        self.config = config
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.wait = None
        self.previous_courts: Set[str] = set()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            if self.config.get('headless', True):
                chrome_options.add_argument("--headless")
            
            # Additional Chrome options for better compatibility
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Disable images and CSS for faster loading
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.config.get('wait_timeout', 15))
            
            self.logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def login(self) -> bool:
        """Login to the BTC website"""
        if not self.credentials.get('username') or not self.credentials.get('password'):
            self.logger.warning("No login credentials provided, skipping login")
            return True
        
        try:
            self.logger.info("Attempting to login...")
            
            # Try common login URL patterns
            login_urls = [
                "https://www.burnabytennis.ca/login",
                "https://www.burnabytennis.ca/signin",
                "https://www.burnabytennis.ca/auth/login",
                "https://www.burnabytennis.ca/user/login"
            ]
            
            for login_url in login_urls:
                try:
                    self.logger.info(f"Trying login URL: {login_url}")
                    self.driver.get(login_url)
                    time.sleep(2)
                    
                    if self._attempt_login():
                        self.logger.info("Login successful!")
                        return True
                    else:
                        self.logger.warning("Login failed, trying next URL")
                        continue
                        
                except Exception as e:
                    self.logger.debug(f"Error with login URL {login_url}: {e}")
                    continue
            
            self.logger.warning("Could not find login form or login failed")
            return True  # Continue anyway
            
        except Exception as e:
            self.logger.error(f"Error during login: {e}")
            return False
    
    def _attempt_login(self) -> bool:
        """Attempt to login with current page"""
        try:
            # Find login form elements
            email_selectors = [
                "input[type='email']", "input[name='email']", "input[name='username']",
                "input[name='user']", "input[id*='email']", "input[id*='username']",
                "input[placeholder*='email']", "input[placeholder*='username']"
            ]
            
            password_selectors = [
                "input[type='password']", "input[name='password']", "input[name='pass']",
                "input[id*='password']", "input[placeholder*='password']"
            ]
            
            submit_selectors = [
                "button[type='submit']", "input[type='submit']", "button[class*='login']",
                "button[class*='submit']", "button[id*='login']", "button[id*='submit']"
            ]
            
            # Find form elements
            email_field = self._find_element(email_selectors)
            password_field = self._find_element(password_selectors)
            submit_button = self._find_element(submit_selectors)
            
            if email_field and password_field and submit_button:
                self.logger.info("Login form found, attempting to fill credentials")
                
                # Fill credentials
                email_field.clear()
                email_field.send_keys(self.credentials['username'])
                time.sleep(0.5)
                
                password_field.clear()
                password_field.send_keys(self.credentials['password'])
                time.sleep(0.5)
                
                submit_button.click()
                time.sleep(3)
                
                return self._check_login_success()
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error during login attempt: {e}")
            return False
    
    def _find_element(self, selectors: List[str]):
        """Find first available element from list of selectors"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except NoSuchElementException:
                continue
        return None
    
    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            success_indicators = [
                "logout", "sign out", "profile", "dashboard", "welcome",
                "my account", "account", "user menu"
            ]
            
            page_text = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()
            
            # Check if we're redirected to a different page
            if "login" not in current_url and "signin" not in current_url:
                return True
            
            # Check for success indicators
            for indicator in success_indicators:
                if indicator in page_text:
                    return True
            
            # Check if we can access the booking page
            if "booking" in current_url or "grid" in current_url:
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking login success: {e}")
            return False
    
    def navigate_to_booking_page(self) -> bool:
        """Navigate to the BTC booking page"""
        try:
            base_url = self.config.get('base_url', 'https://www.burnabytennis.ca/app/bookings/grid')
            self.logger.info(f"Navigating to {base_url}")
            self.driver.get(base_url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            if "burnabytennis.ca" in self.driver.current_url:
                self.logger.info("Successfully navigated to BTC booking page")
                return True
            else:
                self.logger.warning(f"Unexpected URL: {self.driver.current_url}")
                return False
                
        except TimeoutException:
            self.logger.error("Timeout waiting for page to load")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to booking page: {e}")
            return False
    
    def scan_all_dates(self) -> Dict[str, List[Dict]]:
        """Scan all three dates (today, tomorrow, day after tomorrow) for available courts"""
        all_courts = {}
        date_navigation_successful = False
        
        # Check today, tomorrow, and day after tomorrow
        dates_to_check = [
            (0, "today"),
            (1, "tomorrow"), 
            (2, "day after tomorrow")
        ]
        
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
        
        return all_courts
    
    def _navigate_to_specific_date(self, target_date: datetime) -> bool:
        """Navigate to the specified booking date on the booking calendar"""
        try:
            self.logger.info(f"Navigating to date: {target_date.strftime('%A, %B %d, %Y')}")
            
            # Format date strings for searching
            date_display = target_date.strftime("%B %d, %Y")
            date_str = target_date.strftime("%a %d")
            date_alt = target_date.strftime("%A %d")
            date_short = target_date.strftime("%d")
            
            # Look for date toggle/button
            date_toggle_found = False
            
            # Try to find tomorrow's date toggle
            for date_format in [date_str, date_alt, date_short]:
                try:
                    xpath_selector = f"//button[contains(text(), '{date_format}')] | //div[contains(text(), '{date_format}')] | //span[contains(text(), '{date_format}')] | //a[contains(text(), '{date_format}')]"
                    date_element = self.driver.find_element(By.XPATH, xpath_selector)
                    if date_element.is_displayed() and date_element.is_enabled():
                        self.logger.info(f"Found date toggle: {date_format}")
                        date_element.click()
                        time.sleep(2)
                        date_toggle_found = True
                        break
                except NoSuchElementException:
                    continue
            
            if not date_toggle_found:
                self.logger.warning("Could not find date toggle")
            
            return date_toggle_found
            
        except Exception as e:
            self.logger.error(f"Error navigating to specific date: {e}")
            return False
    
    def _detect_available_courts(self) -> List[Dict]:
        """Detect available tennis courts on the booking grid"""
        available_courts = []
        
        try:
            self.logger.info("Scanning for available courts...")
            time.sleep(3)  # Give time for the grid to load
            
            # Find all button elements on the page
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            self.logger.info(f"Found {len(all_buttons)} button elements on page")
            
            # Look for buttons with "Book" text
            book_buttons = []
            for button in all_buttons:
                try:
                    if 'Book' in button.text or 'book' in button.text.lower():
                        book_buttons.append(button)
                        self.logger.info(f"Found Book button: {button.text}")
                except:
                    continue
            
            self.logger.info(f"Found {len(book_buttons)} buttons with 'Book' text")
            
            # Extract court info from these buttons
            for button in book_buttons:
                try:
                    court_info = self._extract_court_info(button)
                    if court_info:
                        available_courts.append(court_info)
                        self.logger.info(f"Added court from button: {court_info}")
                except Exception as e:
                    self.logger.debug(f"Error extracting court info from button: {e}")
            
            return available_courts
            
        except Exception as e:
            self.logger.error(f"Error detecting available courts: {e}")
            return available_courts
    
    def _extract_court_info(self, element) -> Optional[Dict]:
        """Extract court information from a web element"""
        try:
            full_text = element.text.strip()
            
            court_info = {
                'element': element,
                'text': full_text,
                'class': element.get_attribute('class'),
                'id': element.get_attribute('id'),
                'time': None,
                'court_number': None,
                'date': None,
                'clickable': True
            }
            
            # Look for "Book" text and time patterns
            if 'Book' in full_text or 'book' in full_text.lower():
                # Filter out false positives
                if 'Booking Grid' in full_text or 'None' in full_text:
                    self.logger.debug(f"Skipping false positive: {full_text}")
                    return None
                
                # Extract time information
                import re
                time_patterns = [
                    r'Book\s+(\d{1,2}:\d{2}\s*(am|pm|AM|PM))',
                    r'Book\s+(\d{1,2}:\d{2})',
                    r'(\d{1,2}:\d{2}\s*(am|pm|AM|PM))',
                    r'(\d{1,2}:\d{2})'
                ]
            
                for pattern in time_patterns:
                    match = re.search(pattern, full_text)
                    if match:
                        court_info['time'] = match.group(1)
                        break
            
            # Extract court number
            court_patterns = [
                r'Court\s*(\d+)',
                r'Court\s*([A-Z]\d+)',
                r'(\d+)\s*Court'
            ]
            
            for pattern in court_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    court_info['court_number'] = match.group(1)
                    break
            
            # Check if element is clickable
            court_info['clickable'] = element.is_displayed() and element.is_enabled()
            
            # Filter out false positives
            false_positive_indicators = [
                'Booking Grid', 'None', 'N/A', 'disabled',
                'unavailable', 'closed', 'maintenance'
            ]
            
            is_false_positive = any(indicator in full_text for indicator in false_positive_indicators)
            
            if is_false_positive:
                self.logger.debug(f"Skipping false positive court: {full_text}")
                return None
            
            # Only return if it has a valid time or looks like a real booking button
            if court_info['time'] or ('book' in full_text.lower() and ':' in full_text):
                return court_info
            else:
                return None
            
        except Exception as e:
            self.logger.debug(f"Error extracting court info: {e}")
            return None
    
    def detect_new_courts(self, all_courts: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Detect new courts by comparing with previous scan"""
        # Flatten all courts for comparison
        current_courts = set()
        for date, courts in all_courts.items():
            for court in courts:
                court_key = f"{date}_{court.get('time', '')}_{court.get('text', '')}"
                current_courts.add(court_key)
        
        # Find new courts
        new_courts = current_courts - self.previous_courts
        
        if new_courts:
            self.logger.info(f"🎾 NEW COURTS DETECTED! {len(new_courts)} new slots found!")
            
            # Filter all_courts to only include new courts
            new_courts_dict = {}
            for date, courts in all_courts.items():
                new_courts_for_date = []
                for court in courts:
                    court_key = f"{date}_{court.get('time', '')}_{court.get('text', '')}"
                    if court_key in new_courts:
                        new_courts_for_date.append(court)
                
                if new_courts_for_date:
                    new_courts_dict[date] = new_courts_for_date
            
            # Update previous courts
            self.previous_courts = current_courts
            return new_courts_dict
        else:
            self.logger.info(f"Found courts but no new ones since last check")
            self.previous_courts = current_courts
            return {}
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")
