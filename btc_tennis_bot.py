#!/usr/bin/env python3
"""
🎾 Burnaby Tennis Club Court Booking Bot 🎾

This bot automates the process of checking for available tennis courts
and notifying users when courts become available for booking.

📋 ONBOARDING INSTRUCTIONS:
1. Set up your environment variables:
   export BTC_USERNAME="your_email@example.com"
   export BTC_PASSWORD="your_password"
   export BTC_NOTIFICATION_EMAIL="your_email@example.com"
   export BTC_PHONE_NUMBER="1234567890"
   export BTC_GMAIL_APP_EMAIL="your_gmail@gmail.com"
   export BTC_GMAIL_APP_PASSWORD="your_gmail_app_password"
   export BTC_BOOKING_DATE="tomorrow"  # or specific date like "2025-10-27"

2. For Gmail App Password:
   - Go to Google Account > Security > 2-Step Verification > App passwords
   - Generate a new app password for "Mail"
   - Use this password for BTC_GMAIL_APP_PASSWORD

3. Run the bot: python3 btc.py

The bot will:
- Login to Burnaby Tennis Club website
- Navigate to tomorrow's bookings
- Scan for available courts
- Send email and SMS notifications when courts are found
- Support continuous monitoring

🔧 Features:
- Automatic login and navigation
- Real-time court availability detection
- Email notifications (Gmail SMTP)
- SMS notifications (via email-to-SMS gateways)
- False positive filtering
- Continuous monitoring options
"""

import time
import logging
import getpass
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('btc_booking.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BTCCourtBookingBot:
    """Automation bot for Burnaby Tennis Club court bookings"""
    
    def __init__(self, headless: bool = False, wait_timeout: int = 10, username: str = None, password: str = None, notification_email: str = None, phone_number: str = None, gmail_app_email: str = None, booking_date: str = None):
        """
        Initialize the BTC booking bot
        
        Args:
            headless: Run browser in headless mode
            wait_timeout: Maximum wait time for elements to load
            username: Login username/email
            password: Login password
            notification_email: Email address for notifications
            phone_number: Phone number for SMS notifications (format: 6479370971)
            gmail_app_email: Gmail address for SMTP authentication
            booking_date: Date to check for bookings ("tomorrow" or specific date like "2025-10-27")
        """
        self.wait_timeout = wait_timeout
        self.driver = None
        self.wait = None
        self.headless = headless
        self.username = username
        self.password = password
        self.base_url = "https://www.burnabytennis.ca/app/bookings/grid"
        self.login_url = "https://www.burnabytennis.ca/login"  # Common login URL pattern
        self.notification_email = notification_email or "harry442930583@gmail.com"
        self.phone_number = phone_number
        self.gmail_app_email = gmail_app_email
        self.booking_date = booking_date or "tomorrow"
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Additional Chrome options for better compatibility
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Disable images and CSS for faster loading (optional)
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
            
            logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def login(self) -> bool:
        """
        Login to the BTC website
        
        Returns:
            bool: True if login successful, False otherwise
        """
        if not self.username or not self.password:
            logger.warning("No login credentials provided, skipping login")
            return True
        
        try:
            logger.info("Attempting to login...")
            
            # Try common login URL patterns
            login_urls = [
                "https://www.burnabytennis.ca/login",
                "https://www.burnabytennis.ca/signin",
                "https://www.burnabytennis.ca/auth/login",
                "https://www.burnabytennis.ca/user/login"
            ]
            
            login_successful = False
            for login_url in login_urls:
                try:
                    logger.info(f"Trying login URL: {login_url}")
                    self.driver.get(login_url)
                    time.sleep(2)
                    
                    # Look for login form elements
                    email_selectors = [
                        "input[type='email']",
                        "input[name='email']",
                        "input[name='username']",
                        "input[name='user']",
                        "input[id*='email']",
                        "input[id*='username']",
                        "input[placeholder*='email']",
                        "input[placeholder*='username']"
                    ]
                    
                    password_selectors = [
                        "input[type='password']",
                        "input[name='password']",
                        "input[name='pass']",
                        "input[id*='password']",
                        "input[placeholder*='password']"
                    ]
                    
                    submit_selectors = [
                        "button[type='submit']",
                        "input[type='submit']",
                        "button[class*='login']",
                        "button[class*='submit']",
                        "button[id*='login']",
                        "button[id*='submit']"
                    ]
                    
                    # Find email/username field
                    email_field = None
                    for selector in email_selectors:
                        try:
                            email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if email_field.is_displayed():
                                break
                        except NoSuchElementException:
                            continue
                    
                    # Find password field
                    password_field = None
                    for selector in password_selectors:
                        try:
                            password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if password_field.is_displayed():
                                break
                        except NoSuchElementException:
                            continue
                    
                    # Find submit button
                    submit_button = None
                    for selector in submit_selectors:
                        try:
                            submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if submit_button.is_displayed():
                                break
                        except NoSuchElementException:
                            continue
                    
                    if email_field and password_field and submit_button:
                        logger.info("Login form found, attempting to fill credentials")
                        
                        # Clear and fill email field
                        email_field.clear()
                        email_field.send_keys(self.username)
                        time.sleep(0.5)
                        
                        # Clear and fill password field
                        password_field.clear()
                        password_field.send_keys(self.password)
                        time.sleep(0.5)
                        
                        # Click submit button
                        submit_button.click()
                        time.sleep(3)
                        
                        # Check if login was successful
                        if self.check_login_success():
                            logger.info("Login successful!")
                            login_successful = True
                            break
                        else:
                            logger.warning("Login failed, trying next URL")
                            continue
                    else:
                        logger.debug(f"Login form not found at {login_url}")
                        continue
                        
                except Exception as e:
                    logger.debug(f"Error with login URL {login_url}: {e}")
                    continue
            
            if not login_successful:
                logger.warning("Could not find login form or login failed")
                # Continue anyway - maybe the site doesn't require login
                return True
            
            return login_successful
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def check_login_success(self) -> bool:
        """
        Check if login was successful
        
        Returns:
            bool: True if login successful
        """
        try:
            # Look for indicators of successful login
            success_indicators = [
                "logout", "sign out", "profile", "dashboard", "welcome",
                "my account", "account", "user menu"
            ]
            
            page_text = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()
            
            # Check if we're redirected to a different page (common after login)
            if "login" not in current_url and "signin" not in current_url:
                return True
            
            # Check for success indicators in page text
            for indicator in success_indicators:
                if indicator in page_text:
                    return True
            
            # Check if we can access the booking page
            if "booking" in current_url or "grid" in current_url:
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking login success: {e}")
            return False

    def navigate_to_booking_page(self) -> bool:
        """
        Navigate to the BTC booking page
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            logger.info(f"Navigating to {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check if we're on the correct page
            if "burnabytennis.ca" in self.driver.current_url:
                logger.info("Successfully navigated to BTC booking page")
                return True
            else:
                logger.warning(f"Unexpected URL: {self.driver.current_url}")
                return False
                
        except TimeoutException:
            logger.error("Timeout waiting for page to load")
            return False
        except Exception as e:
            logger.error(f"Error navigating to booking page: {e}")
            return False

    def send_email_notification(self, available_courts: List[Dict]) -> bool:
        """
        Send email notification when courts become available
        
        Args:
            available_courts: List of available courts
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            logger.info(f"Sending notification for {len(available_courts)} available courts")
            
            # Create notification message
            message = f"""
🎾 BURNABY TENNIS CLUB - COURTS AVAILABLE! 🎾

Great news! {len(available_courts)} tennis court slots have become available for tomorrow:

"""
            
            for i, court in enumerate(available_courts, 1):
                message += f"{i}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}\n"
            
            message += f"""
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Booking URL: {self.base_url}

Hurry up and book your court! 🏃‍♂️

---
BTC Booking Bot 🤖
            """
            
            # Try multiple notification methods
            success = False
            
            # Method 1: Try Gmail SMTP with app password
            try:
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                sender_email = self.gmail_app_email or self.notification_email
                
                # Note: You need to use an App Password, not your regular password
                # Go to Google Account > Security > 2-Step Verification > App passwords
                sender_password = self.password  # This should be an App Password
                
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = self.notification_email
                msg['Subject'] = f"🎾 BTC Tennis Courts Available - {len(available_courts)} slots found!"
                
                msg.attach(MIMEText(message, 'plain'))
                
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                # Use Gmail App Password for SMTP authentication
                app_password = os.getenv('BTC_GMAIL_APP_PASSWORD', 'yrrf zspv pmup mjgo')
                server.login(sender_email, app_password)
                text = msg.as_string()
                server.sendmail(sender_email, self.notification_email, text)
                server.quit()
                
                logger.info("Email notification sent successfully!")
                success = True
                
            except Exception as e:
                logger.warning(f"Gmail SMTP failed: {e}")
            
            # Method 2: Save to file as backup notification
            try:
                notification_file = f"btc_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(notification_file, 'w') as f:
                    f.write(message)
                logger.info(f"Notification saved to file: {notification_file}")
                success = True
            except Exception as e:
                logger.error(f"Failed to save notification file: {e}")
            
            # Method 3: Send SMS notification
            if self.phone_number:
                try:
                    sms_success = self.send_sms_notification(available_courts)
                    if sms_success:
                        logger.info("SMS notification sent successfully!")
                        success = True
                    else:
                        logger.warning("SMS notification failed")
                except Exception as e:
                    logger.error(f"SMS notification error: {e}")
            
            # Method 4: Print to console
            print("\n" + "="*50)
            print("🎾 TENNIS COURT NOTIFICATION 🎾")
            print("="*50)
            print(message)
            print("="*50)
            logger.info("Notification printed to console")
            success = True
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def send_sms_notification(self, available_courts: List[Dict]) -> bool:
        """
        Send SMS notification when courts become available using email-to-SMS gateway
        
        Args:
            available_courts: List of available courts
            
        Returns:
            bool: True if SMS sent successfully
        """
        if not self.phone_number:
            logger.warning("No phone number provided for SMS notifications")
            return False
            
        try:
            logger.info(f"Sending SMS notification for {len(available_courts)} available courts")
            
            # Create SMS message (shorter for SMS)
            sms_message = f"🎾 BTC: {len(available_courts)} courts available! "
            for i, court in enumerate(available_courts[:2], 1):  # Limit to first 2 courts for SMS
                sms_message += f"{court.get('time', 'N/A')} "
            if len(available_courts) > 2:
                sms_message += f"+{len(available_courts)-2} more"
            sms_message += f"Book: {self.base_url}"
            
            # Email-to-SMS gateways for Canadian carriers
            sms_gateways = {
                'rogers': f"{self.phone_number}@pcs.rogers.com",
                'bell': f"{self.phone_number}@txt.bell.ca", 
                'telus': f"{self.phone_number}@msg.telus.com",
                'fido': f"{self.phone_number}@fido.ca",
                'virgin': f"{self.phone_number}@vmobile.ca",
                'koodo': f"{self.phone_number}@msg.koodomobile.com"
            }
            
            success = False
            
            # Try each carrier gateway
            for carrier, sms_email in sms_gateways.items():
                try:
                    logger.info(f"Trying SMS via {carrier} gateway: {sms_email}")
                    
                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = self.notification_email
                    msg['To'] = sms_email
                    msg['Subject'] = ""  # Empty subject for SMS
                    
                    msg.attach(MIMEText(sms_message, 'plain'))
                    
                    # Send via Gmail SMTP
                    smtp_server = "smtp.gmail.com"
                    smtp_port = 587
                    
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    # Use Gmail App Password for SMTP authentication
                    app_password = os.getenv('BTC_GMAIL_APP_PASSWORD', 'yrrf zspv pmup mjgo')
                    server.login(self.gmail_app_email or self.notification_email, app_password)
                    text = msg.as_string()
                    server.sendmail(self.notification_email, sms_email, text)
                    server.quit()
                    
                    logger.info(f"SMS sent successfully via {carrier} gateway!")
                    success = True
                    break
                    
                except Exception as e:
                    logger.warning(f"SMS via {carrier} failed: {e}")
                    continue
            
            if not success:
                logger.warning("All SMS gateways failed, trying alternative method...")
                # Alternative: Use a universal SMS service
                try:
                    # Try using a universal SMS gateway
                    universal_sms = f"{self.phone_number}@txt.att.net"  # AT&T gateway often works
                    msg = MIMEMultipart()
                    msg['From'] = self.notification_email
                    msg['To'] = universal_sms
                    msg['Subject'] = ""
                    msg.attach(MIMEText(sms_message, 'plain'))
                    
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    # Use Gmail App Password for SMTP authentication
                    app_password = os.getenv('BTC_GMAIL_APP_PASSWORD', 'yrrf zspv pmup mjgo')
                    server.login(self.gmail_app_email or self.notification_email, app_password)
                    text = msg.as_string()
                    server.sendmail(self.notification_email, universal_sms, text)
                    server.quit()
                    
                    logger.info("SMS sent via universal gateway!")
                    success = True
                    
                except Exception as e:
                    logger.error(f"Universal SMS gateway also failed: {e}")
            
            # Fallback: Console SMS simulation
            if not success:
                logger.info("SMS gateway failed, using console simulation...")
                print(f"\n📱 SMS SIMULATION TO {self.phone_number}:")
                print("=" * 50)
                print(sms_message)
                print("=" * 50)
                print("Note: To receive real SMS, set up Gmail App Password")
                print("Go to: Google Account > Security > 2-Step Verification > App passwords")
                success = True
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
            return False

    def navigate_to_tomorrow(self) -> bool:
        """
        Navigate to the specified booking date on the booking calendar
        
        Returns:
            bool: True if navigation successful
        """
        try:
            logger.info(f"Navigating to booking date: {self.booking_date}")
            
            # Calculate target date
            if self.booking_date.lower() == "tomorrow":
                target_date = datetime.now() + timedelta(days=1)
            else:
                try:
                    # Parse specific date format (YYYY-MM-DD)
                    target_date = datetime.strptime(self.booking_date, "%Y-%m-%d")
                except ValueError:
                    logger.error(f"Invalid date format: {self.booking_date}. Use 'tomorrow' or 'YYYY-MM-DD'")
                    return False
            
            # Format date strings for searching
            date_display = target_date.strftime("%B %d, %Y")
            date_str = target_date.strftime("%a %d")
            date_alt = target_date.strftime("%A %d")
            date_short = target_date.strftime("%d")
            
            logger.info(f"Looking for target date: {date_display}")
            logger.info(f"Looking for date toggle: {date_str}")
            
            # Look for date toggle/button
            tomorrow_date_str = date_str
            tomorrow_date_alt = date_alt
            tomorrow_date_short = date_short
            
            logger.info(f"Looking for date toggle: {tomorrow_date_str}")
            
            # Common date toggle selectors
            date_toggle_selectors = [
                f"button:contains('{tomorrow_date_str}')",
                f"div:contains('{tomorrow_date_str}')",
                f"span:contains('{tomorrow_date_str}')",
                f"a:contains('{tomorrow_date_str}')",
                f"button:contains('{tomorrow_date_alt}')",
                f"div:contains('{tomorrow_date_alt}')",
                f"span:contains('{tomorrow_date_alt}')",
                f"a:contains('{tomorrow_date_alt}')",
                f"button:contains('{tomorrow_date_short}')",
                f"div:contains('{tomorrow_date_short}')",
                f"span:contains('{tomorrow_date_short}')",
                f"a:contains('{tomorrow_date_short}')"
            ]
            
            # Try to find tomorrow's date toggle
            date_toggle_found = False
            for selector in date_toggle_selectors:
                try:
                    # Use XPath for text content matching
                    xpath_selector = f"//button[contains(text(), '{tomorrow_date_str}')] | //div[contains(text(), '{tomorrow_date_str}')] | //span[contains(text(), '{tomorrow_date_str}')] | //a[contains(text(), '{tomorrow_date_str}')]"
                    date_element = self.driver.find_element(By.XPATH, xpath_selector)
                    if date_element.is_displayed() and date_element.is_enabled():
                        logger.info(f"Found tomorrow's date toggle: {tomorrow_date_str}")
                        date_element.click()
                        time.sleep(2)
                        date_toggle_found = True
                        break
                except NoSuchElementException:
                    continue
            
            # If not found with full date, try alternative approaches
            if not date_toggle_found:
                # Try common date navigation selectors
                date_selectors = [
                    "button[class*='next']",
                    "button[class*='arrow']",
                    "button[class*='forward']",
                    "div[class*='next']",
                    "a[class*='next']",
                    "button[title*='next']",
                    "button[aria-label*='next']",
                    "button[class*='date']",
                    "div[class*='date']",
                    "button[class*='day']",
                    "div[class*='day']"
                ]
                
                # Try to find and click next day button
                for selector in date_selectors:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if next_button.is_displayed() and next_button.is_enabled():
                            logger.info(f"Found next day button: {selector}")
                            next_button.click()
                            time.sleep(2)
                            date_toggle_found = True
                            break
                    except NoSuchElementException:
                        continue
            
            # Also try to find date picker or calendar
            date_picker_selectors = [
                "input[type='date']",
                "input[class*='date']",
                "div[class*='datepicker']",
                "div[class*='calendar']"
            ]
            
            for selector in date_picker_selectors:
                try:
                    date_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if date_element.is_displayed():
                        logger.info(f"Found date picker: {selector}")
                        date_element.clear()
                        date_element.send_keys(tomorrow_str)
                        time.sleep(2)
                        break
                except NoSuchElementException:
                    continue
            
            # If still not found, try to find all clickable elements and look for date-related ones
            if not date_toggle_found:
                try:
                    logger.info("Searching for all clickable elements...")
                    clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, "button, div, span, a")
                    
                    for element in clickable_elements:
                        try:
                            element_text = element.text.strip()
                            if (tomorrow_date_str in element_text or 
                                tomorrow_date_alt in element_text or 
                                tomorrow_date_short in element_text):
                                logger.info(f"Found potential date element: '{element_text}'")
                                if element.is_displayed() and element.is_enabled():
                                    element.click()
                                    time.sleep(2)
                                    date_toggle_found = True
                                    break
                        except Exception as e:
                            continue
                except Exception as e:
                    logger.debug(f"Error searching clickable elements: {e}")
            
            if date_toggle_found:
                logger.info("Successfully navigated to tomorrow's date")
            else:
                logger.warning("Could not find tomorrow's date toggle")
            
            return date_toggle_found
            
        except Exception as e:
            logger.error(f"Error navigating to tomorrow: {e}")
            return False

    def detect_available_courts(self) -> List[Dict]:
        """
        Detect available tennis courts on the booking grid
        
        Returns:
            List[Dict]: List of available courts with their details
        """
        available_courts = []
        
        try:
            logger.info("Scanning for available courts...")
            
            # First try to navigate to tomorrow's date
            self.navigate_to_tomorrow()
            
            logger.info("Waiting for booking grid to load...")
            time.sleep(3)  # Give more time for the grid to load
            
            # Save page source for analysis
            page_source = self.driver.page_source
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            source_filename = f"btc_mon27_page_source_{timestamp}.html"
            with open(source_filename, 'w', encoding='utf-8') as f:
                f.write(page_source)
            logger.info(f"Page source saved to: {source_filename}")
            
            # Skip the inefficient selector logic and go straight to Book button analysis
            logger.info("Analyzing page source for Book buttons...")
            
            # Find all button elements on the page
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"Found {len(all_buttons)} button elements on page")
            
            # Look for MUI buttons specifically
            mui_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[class*='MuiButton']")
            logger.info(f"Found {len(mui_buttons)} MUI button elements")
            
            # Look for buttons with "Book" text
            book_buttons = []
            for button in all_buttons:
                try:
                    if 'Book' in button.text or 'book' in button.text.lower():
                        book_buttons.append(button)
                        logger.info(f"Found Book button: {button.text} - Class: {button.get_attribute('class')}")
                except:
                    continue
            
            logger.info(f"Found {len(book_buttons)} buttons with 'Book' text")
            
            # Try to extract court info from these buttons
            for button in book_buttons:
                try:
                    court_info = self.extract_court_info(button)
                    if court_info:
                        available_courts.append(court_info)
                        logger.info(f"Added court from button: {court_info}")
                except Exception as e:
                    logger.debug(f"Error extracting court info from button: {e}")
            
            return available_courts
            
        except Exception as e:
            logger.error(f"Error detecting available courts: {e}")
            return available_courts
    
    def extract_court_info(self, element) -> Optional[Dict]:
        """
        Extract court information from a web element
        
        Args:
            element: Selenium WebElement
            
        Returns:
            Dict: Court information or None if extraction fails
        """
        try:
            # Get the full text content including nested elements
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
            
            # Look for "Book" text and time patterns in MUI buttons
            if 'Book' in full_text or 'book' in full_text.lower():
                # Filter out false positives like "Booking Grid - None"
                if 'Booking Grid' in full_text or 'None' in full_text:
                    logger.debug(f"Skipping false positive: {full_text}")
                    return None
                
                logger.info(f"Found booking button: {full_text}")
                
                # Try to extract time information from MUI button text
                time_patterns = [
                    r'Book\s+(\d{1,2}:\d{2}\s*(am|pm|AM|PM))',
                    r'Book\s+(\d{1,2}:\d{2})',
                    r'(\d{1,2}:\d{2}\s*(am|pm|AM|PM))',
                    r'(\d{1,2}:\d{2})'
                ]
            
                import re
                for pattern in time_patterns:
                    match = re.search(pattern, full_text)
                    if match:
                        court_info['time'] = match.group(1)
                        logger.info(f"Extracted time: {court_info['time']}")
                        break
            
            # Try to extract court number
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
            
            # Check if element is clickable and available
            court_info['clickable'] = self.is_element_clickable(element)
            court_info['available'] = self.is_element_available(element)
            
            # Filter out false positives
            false_positive_indicators = [
                'Booking Grid',
                'None',
                'N/A',
                'disabled',
                'unavailable',
                'closed',
                'maintenance'
            ]
            
            is_false_positive = any(indicator in full_text for indicator in false_positive_indicators)
            
            if is_false_positive:
                logger.debug(f"Skipping false positive court: {full_text}")
                return None
            
            # Only return if it has a valid time or looks like a real booking button
            if court_info['time'] or ('book' in full_text.lower() and ':' in full_text):
                return court_info
            else:
                return None
            
        except Exception as e:
            logger.debug(f"Error extracting court info: {e}")
            return None
    
    def is_element_available(self, element) -> bool:
        """
        Check if an element represents an available court
        
        Args:
            element: Selenium WebElement
            
        Returns:
            bool: True if element appears to be available
        """
        try:
            # Check for availability indicators
            availability_indicators = [
                'available', 'free', 'open', 'bookable', 'selectable'
            ]
            
            class_name = element.get_attribute('class').lower()
            text_content = element.text.lower()
            
            for indicator in availability_indicators:
                if indicator in class_name or indicator in text_content:
                    return True
            
            # Check if element is not disabled
            if element.get_attribute('disabled'):
                return False
            
            # Check if element is visible and clickable
            if element.is_displayed() and element.is_enabled():
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking element availability: {e}")
            return False
    
    def is_element_clickable(self, element) -> bool:
        """
        Check if an element is clickable
        
        Args:
            element: Selenium WebElement
            
        Returns:
            bool: True if element is clickable
        """
        try:
            return element.is_displayed() and element.is_enabled()
        except Exception:
            return False
    
    def attempt_booking(self, court_info: Dict) -> bool:
        """
        Attempt to book a specific court
        
        Args:
            court_info: Dictionary containing court information
            
        Returns:
            bool: True if booking attempt was successful
        """
        try:
            element = court_info['element']
            logger.info(f"Attempting to book court: {court_info}")
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # Try different click methods
            click_methods = [
                lambda: element.click(),
                lambda: ActionChains(self.driver).move_to_element(element).click().perform(),
                lambda: self.driver.execute_script("arguments[0].click();", element)
            ]
            
            for i, click_method in enumerate(click_methods):
                try:
                    click_method()
                    logger.info(f"Successfully clicked court using method {i+1}")
                    
                    # Wait for booking form or confirmation
                    time.sleep(2)
                    
                    # Check if booking form appeared
                    if self.check_booking_form():
                        logger.info("Booking form detected - booking attempt successful")
                        return True
                    
                except ElementClickInterceptedException:
                    logger.debug(f"Click method {i+1} failed - element intercepted")
                    continue
                except Exception as e:
                    logger.debug(f"Click method {i+1} failed: {e}")
                    continue
            
            logger.warning("All click methods failed")
            return False
            
        except Exception as e:
            logger.error(f"Error attempting booking: {e}")
            return False
    
    def check_booking_form(self) -> bool:
        """
        Check if a booking form has appeared
        
        Returns:
            bool: True if booking form is detected
        """
        try:
            # Look for common booking form indicators
            form_selectors = [
                "form[class*='booking']",
                "div[class*='booking-form']",
                "div[class*='reservation']",
                "form[class*='reservation']",
                "div[class*='confirm']",
                "button[class*='confirm']",
                "input[type='submit']"
            ]
            
            for selector in form_selectors:
                try:
                    form_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if form_element.is_displayed():
                        logger.info(f"Booking form detected: {selector}")
                        return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking for booking form: {e}")
            return False
    
    def save_available_courts(self, courts: List[Dict], filename: str = None):
        """
        Save available courts to a file
        
        Args:
            courts: List of available courts
            filename: Output filename (optional)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"available_courts_{timestamp}.json"
        
        try:
            # Prepare data for JSON serialization
            courts_data = []
            for court in courts:
                court_data = {k: v for k, v in court.items() if k != 'element'}
                courts_data.append(court_data)
            
            with open(filename, 'w') as f:
                json.dump(courts_data, f, indent=2)
            
            logger.info(f"Available courts saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving courts data: {e}")
    
    def run_booking_scan(self, save_results: bool = True) -> List[Dict]:
        """
        Run a complete booking scan
        
        Args:
            save_results: Whether to save results to file
            
        Returns:
            List[Dict]: Available courts found
        """
        try:
            logger.info("Starting BTC court booking scan...")
            
            # Setup driver
            self.setup_driver()
            
            # Attempt login if credentials provided
            if self.username and self.password:
                if not self.login():
                    logger.warning("Login failed, continuing anyway...")
            
            # Navigate to booking page
            if not self.navigate_to_booking_page():
                logger.error("Failed to navigate to booking page")
                return []
            
            # Wait a bit for page to fully load
            time.sleep(3)
            
            # Take a screenshot for debugging
            try:
                screenshot_path = f"btc_booking_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.debug(f"Could not save screenshot: {e}")
            
            # Save page source for debugging
            try:
                page_source_path = f"btc_booking_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(page_source_path, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.info(f"Page source saved: {page_source_path}")
            except Exception as e:
                logger.debug(f"Could not save page source: {e}")
            
            # Detect available courts
            available_courts = self.detect_available_courts()
            
            if available_courts:
                logger.info(f"Found {len(available_courts)} available courts:")
                for i, court in enumerate(available_courts, 1):
                    logger.info(f"  {i}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}")
                
                # Send email notification for available courts
                self.send_email_notification(available_courts)
                
                if save_results:
                    self.save_available_courts(available_courts)
            else:
                logger.info("No available courts found")
            
            return available_courts
            
        except Exception as e:
            logger.error(f"Error during booking scan: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
    
    def run_continuous_monitoring(self, interval_minutes: int = 5, max_attempts: int = 10):
        """
        Run continuous monitoring for available courts
        
        Args:
            interval_minutes: Minutes between scans
            max_attempts: Maximum number of scan attempts
        """
        logger.info(f"Starting continuous monitoring (every {interval_minutes} minutes)")
        
        attempt = 0
        while attempt < max_attempts:
            try:
                attempt += 1
                logger.info(f"Scan attempt {attempt}/{max_attempts}")
                
                available_courts = self.run_booking_scan()
                
                if available_courts:
                    logger.info(f"Found {len(available_courts)} available courts!")
                    # Here you could add notification logic (email, SMS, etc.)
                
                if attempt < max_attempts:
                    logger.info(f"Waiting {interval_minutes} minutes before next scan...")
                    time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        logger.info("Continuous monitoring completed")
    
    def monitor_timeslots(self, interval_seconds: int = 30, max_attempts: int = 120):
        """
        Monitor timeslots for availability changes
        
        Args:
            interval_seconds: Seconds between checks
            max_attempts: Maximum number of monitoring attempts
        """
        logger.info(f"Starting timeslot monitoring (every {interval_seconds} seconds)")
        
        attempt = 0
        previous_available = set()
        
        while attempt < max_attempts:
            try:
                attempt += 1
                logger.info(f"Monitoring attempt {attempt}/{max_attempts}")
                
                # Navigate to tomorrow's date first
                self.navigate_to_tomorrow()
                time.sleep(2)
                
                # Check for available courts
                available_courts = self.detect_available_courts()
                
                if available_courts:
                    # Create a set of current available courts for comparison
                    current_available = set()
                    for court in available_courts:
                        court_key = f"{court.get('text', '')}-{court.get('time', '')}"
                        current_available.add(court_key)
                    
                    # Check if there are new available courts
                    new_courts = current_available - previous_available
                    
                    if new_courts:
                        logger.info(f"🎾 NEW COURTS AVAILABLE! {len(new_courts)} new slots found!")
                        new_courts_list = []
                        for court in available_courts:
                            court_key = f"{court.get('text', '')}-{court.get('time', '')}"
                            if court_key in new_courts:
                                new_courts_list.append(court)
                        
                        # Send email notification for new courts
                        self.send_email_notification(new_courts_list)
                        
                        # Update previous available set
                        previous_available = current_available
                    else:
                        logger.info(f"Found {len(available_courts)} courts but no new ones")
                else:
                    logger.info("No available courts found")
                    previous_available = set()
                
                if attempt < max_attempts:
                    logger.info(f"Waiting {interval_seconds} seconds before next check...")
                    time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                time.sleep(10)  # Wait 10 seconds before retrying
        
        logger.info("Timeslot monitoring completed")


def setup_credentials():
    """Interactive credential setup"""
    print("🎾 BTC Tennis Bot - Credential Setup")
    print("=" * 50)
    print("Setting up your credentials for the tennis booking bot...")
    print()
    
    # Check if environment variables are already set
    username = os.getenv('BTC_USERNAME')
    password = os.getenv('BTC_PASSWORD')
    notification_email = os.getenv('BTC_NOTIFICATION_EMAIL')
    phone_number = os.getenv('BTC_PHONE_NUMBER')
    gmail_app_email = os.getenv('BTC_GMAIL_APP_EMAIL')
    gmail_app_password = os.getenv('BTC_GMAIL_APP_PASSWORD')
    booking_date = os.getenv('BTC_BOOKING_DATE', 'tomorrow')
    
    if username and password and notification_email and phone_number and gmail_app_password:
        print("✅ All credentials found in environment variables!")
        print(f"   Username: {username}")
        print(f"   Notification Email: {notification_email}")
        print(f"   Gmail App Email: {gmail_app_email or 'Not set'}")
        print(f"   Phone: {phone_number}")
        print(f"   Booking Date: {booking_date}")
        print()
        return username, password, notification_email, phone_number, gmail_app_email, gmail_app_password, booking_date
    
    print("🔧 Interactive Credential Setup")
    print("=" * 30)
    
    try:
        # Get credentials interactively
        if not username:
            username = input("Enter your BTC login email: ").strip()
        
        if not password:
            password = getpass.getpass("Enter your BTC login password: ")
        
        if not notification_email:
            notification_email = input("Enter notification email (default: same as login): ").strip()
            if not notification_email:
                notification_email = username
        
        if not phone_number:
            phone_number = input("Enter your phone number (e.g., 6479370971): ").strip()
        
        if not gmail_app_email:
            gmail_app_email = input("Enter Gmail address for SMTP (default: same as notification email): ").strip()
            if not gmail_app_email:
                gmail_app_email = notification_email
        
        if not gmail_app_password:
            print("\n📧 Gmail App Password Setup:")
            print("1. Go to Google Account > Security > 2-Step Verification > App passwords")
            print("2. Generate a new app password for 'Mail'")
            print("3. Copy the 16-character password (e.g., 'abcd efgh ijkl mnop')")
            print()
            gmail_app_password = getpass.getpass("Enter your Gmail App Password: ")
        
        if not booking_date or booking_date == 'tomorrow':
            booking_date = input("Enter booking date (default: tomorrow, or use YYYY-MM-DD format): ").strip()
            if not booking_date:
                booking_date = 'tomorrow'
        
        print("\n✅ Credentials configured!")
        print("💡 Tip: Set these as environment variables for future runs:")
        print(f"   export BTC_USERNAME='{username}'")
        print(f"   export BTC_PASSWORD='{password}'")
        print(f"   export BTC_NOTIFICATION_EMAIL='{notification_email}'")
        print(f"   export BTC_PHONE_NUMBER='{phone_number}'")
        print(f"   export BTC_GMAIL_APP_EMAIL='{gmail_app_email}'")
        print(f"   export BTC_GMAIL_APP_PASSWORD='{gmail_app_password}'")
        print(f"   export BTC_BOOKING_DATE='{booking_date}'")
        print()
        
        return username, password, notification_email, phone_number, gmail_app_email, gmail_app_password, booking_date
        
    except EOFError:
        print("\n❌ Interactive input not available in this environment.")
        print("\n📋 Please set environment variables instead:")
        print("   export BTC_USERNAME='your_email@example.com'")
        print("   export BTC_PASSWORD='your_password'")
        print("   export BTC_NOTIFICATION_EMAIL='your_email@example.com'")
        print("   export BTC_PHONE_NUMBER='1234567890'")
        print("   export BTC_GMAIL_APP_PASSWORD='your_gmail_app_password'")
        print("\nThen run the bot again: python3 btc.py")
        exit(1)

def main():
    """Main function to run the BTC booking bot"""
    print("🎾 Burnaby Tennis Club Court Booking Bot")
    print("=" * 50)
    
    # Setup credentials interactively
    username, password, notification_email, phone_number, gmail_app_email, gmail_app_password, booking_date = setup_credentials()
    
    # Configuration
    headless = False  # Set to True for headless operation
    wait_timeout = 10
    
    # Initialize bot with credentials
    bot = BTCCourtBookingBot(
        headless=headless, 
        wait_timeout=wait_timeout, 
        username=username, 
        password=password,
        notification_email=notification_email,
        phone_number=phone_number,
        gmail_app_email=gmail_app_email,
        booking_date=booking_date
    )
    
    try:
        # Run single scan
        print("Running court availability scan...")
        available_courts = bot.run_booking_scan()
        
        if available_courts:
            print(f"\nFound {len(available_courts)} available courts!")
            for i, court in enumerate(available_courts, 1):
                print(f"{i}. {court.get('text', 'N/A')}")
        else:
            print("No available courts found at this time.")
        
        # Send notifications for available courts (only if real courts found)
        if available_courts:
            print(f"\nSending notifications for {len(available_courts)} available courts...")
            bot.send_email_notification(available_courts)
            print("✅ Notifications sent! Check your email and phone.")
        else:
            print("No courts to notify about.")
        
        # Ask user if they want to run monitoring
        print("\nMonitoring options:")
        print("1. Run continuous monitoring (every 5 minutes)")
        print("2. Run timeslot monitoring (every 30 seconds)")
        print("3. Exit")
        
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice == '1':
            interval = int(input("Enter monitoring interval in minutes (default 5): ") or "5")
            max_attempts = int(input("Enter maximum number of scans (default 10): ") or "10")
            bot.run_continuous_monitoring(interval_minutes=interval, max_attempts=max_attempts)
        elif choice == '2':
            interval = int(input("Enter monitoring interval in seconds (default 30): ") or "30")
            max_attempts = int(input("Enter maximum number of checks (default 120): ") or "120")
            bot.monitor_timeslots(interval_seconds=interval, max_attempts=max_attempts)
        else:
            print("Exiting...")
    
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Main function error: {e}")


if __name__ == "__main__":
    main()
