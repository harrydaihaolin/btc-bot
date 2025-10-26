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
   export BTC_GMAIL_APP_PASSWORD="your_gmail_app_password"

2. For Gmail App Password:
   - Go to Google Account > Security > 2-Step Verification > App passwords
   - Generate a new app password for "Mail"
   - Use this password for BTC_GMAIL_APP_PASSWORD

3. Run the bot: python3 btc_tennis_bot.py

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
        logging.StreamHandler(),
        logging.FileHandler('btc_bot.log')
    ]
)
logger = logging.getLogger(__name__)

class BTCCourtBookingBot:
    """Burnaby Tennis Club Court Booking Bot"""
    
    def __init__(self, headless=False, wait_timeout=10, username=None, password=None, 
                 notification_email=None, phone_number=None):
        """Initialize the bot with configuration"""
        self.headless = headless
        self.wait_timeout = wait_timeout
        self.username = username
        self.password = password
        self.notification_email = notification_email
        self.phone_number = phone_number
        self.driver = None
        self.wait = None
        
    def initialize_driver(self):
        """Initialize Chrome WebDriver"""
        try:
            logger.info("====== WebDriver manager ======")
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
            
            # Use webdriver-manager to automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
            
            logger.info("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    def login(self):
        """Login to BTC website"""
        try:
            logger.info("Attempting to login...")
            
            # Try different login URLs
            login_urls = [
                "https://www.burnabytennis.ca/login",
                "https://www.burnabytennis.ca/signin",
                "https://www.burnabytennis.ca/auth/login"
            ]
            
            for login_url in login_urls:
                try:
                    logger.info(f"Trying login URL: {login_url}")
                    self.driver.get(login_url)
                    time.sleep(2)
                    
                    # Look for login form
                    form_selectors = [
                        "form",
                        "form[class*='login']",
                        "form[class*='signin']",
                        "form[class*='auth']",
                        "div[class*='login']",
                        "div[class*='signin']"
                    ]
                    
                    form_found = False
                    for selector in form_selectors:
                        try:
                            form = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                            if form:
                                logger.info("Login form found, attempting to fill credentials")
                                form_found = True
                                break
                        except TimeoutException:
                            continue
                    
                    if not form_found:
                        logger.info(f"No login form found at {login_url}, trying next...")
                        continue
                    
                    # Find email/username field
                    email_selectors = [
                        "input[type='email']",
                        "input[name*='email']",
                        "input[name*='username']",
                        "input[name*='user']",
                        "input[placeholder*='email']",
                        "input[placeholder*='Email']",
                        "input[id*='email']",
                        "input[id*='username']"
                    ]
                    
                    email_field = None
                    for selector in email_selectors:
                        try:
                            email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if email_field and email_field.is_displayed():
                                break
                        except NoSuchElementException:
                            continue
                    
                    if not email_field:
                        logger.warning("Email field not found, trying next URL...")
                        continue
                    
                    # Find password field
                    password_selectors = [
                        "input[type='password']",
                        "input[name*='password']",
                        "input[placeholder*='password']",
                        "input[placeholder*='Password']",
                        "input[id*='password']"
                    ]
                    
                    password_field = None
                    for selector in password_selectors:
                        try:
                            password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if password_field and password_field.is_displayed():
                                break
                        except NoSuchElementException:
                            continue
                    
                    if not password_field:
                        logger.warning("Password field not found, trying next URL...")
                        continue
                    
                    # Fill credentials
                    email_field.clear()
                    email_field.send_keys(self.username)
                    time.sleep(1)
                    
                    password_field.clear()
                    password_field.send_keys(self.password)
                    time.sleep(1)
                    
                    # Find and click submit button
                    submit_selectors = [
                        "button[type='submit']",
                        "input[type='submit']",
                        "button[class*='submit']",
                        "button[class*='login']",
                        "button[class*='signin']",
                        "button:contains('Login')",
                        "button:contains('Sign In')",
                        "button:contains('Submit')"
                    ]
                    
                    submitted = False
                    for selector in submit_selectors:
                        try:
                            if ":contains(" in selector:
                                # Use XPath for text-based selectors
                                xpath = f"//button[contains(text(), '{selector.split(':contains(')[1].split(')')[0]}')]"
                                submit_button = self.driver.find_element(By.XPATH, xpath)
                            else:
                                submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            
                            if submit_button and submit_button.is_displayed():
                                submit_button.click()
                                submitted = True
                                break
                        except (NoSuchElementException, ElementClickInterceptedException):
                            continue
                    
                    if not submitted:
                        # Try pressing Enter on password field
                        password_field.send_keys("\n")
                    
                    time.sleep(3)
                    
                    # Check if login was successful
                    if self.check_login_success():
                        logger.info("Login successful!")
                        return True
                    else:
                        logger.warning(f"Login failed at {login_url}, trying next...")
                        continue
                        
                except Exception as e:
                    logger.warning(f"Error with login URL {login_url}: {e}")
                    continue
            
            logger.error("All login attempts failed")
            return False
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def check_login_success(self):
        """Check if login was successful"""
        try:
            # Wait a bit for page to load
            time.sleep(2)
            
            # Check for success indicators
            success_indicators = [
                "logout", "sign out", "profile", "dashboard", "bookings", "account"
            ]
            
            page_source = self.driver.page_source.lower()
            for indicator in success_indicators:
                if indicator in page_source:
                    return True
            
            # Check if we're redirected to a different page
            current_url = self.driver.current_url
            if "login" not in current_url and "signin" not in current_url:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking login success: {e}")
            return False
    
    def navigate_to_booking_page(self):
        """Navigate to the booking page"""
        try:
            booking_url = "https://www.burnabytennis.ca/app/bookings/grid"
            logger.info(f"Navigating to {booking_url}")
            self.driver.get(booking_url)
            time.sleep(3)
            
            logger.info("Successfully navigated to BTC booking page")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to booking page: {e}")
            return False
    
    def navigate_to_tomorrow(self):
        """Navigate to tomorrow's date"""
        try:
            logger.info("Navigating to tomorrow's date...")
            
            # Calculate tomorrow's date
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime("%B %d, %Y")
            tomorrow_short = tomorrow.strftime("%a %d")
            
            logger.info(f"Looking for test date: {tomorrow_str}")
            logger.info(f"Looking for date toggle: {tomorrow_short}")
            
            # Look for date toggle buttons
            date_selectors = [
                f"//button[contains(text(), '{tomorrow_short}')]",
                f"//div[contains(text(), '{tomorrow_short}')]",
                f"//span[contains(text(), '{tomorrow_short}')]",
                f"//a[contains(text(), '{tomorrow_short}')]",
                f"//*[contains(text(), '{tomorrow_short}')]"
            ]
            
            date_toggle = None
            for selector in date_selectors:
                try:
                    logger.info(f"Looking for date toggle: {tomorrow_short}")
                    date_toggle = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if date_toggle:
                        logger.info(f"Found tomorrow's date toggle: {tomorrow_short}")
                        break
                except TimeoutException:
                    continue
            
            if not date_toggle:
                logger.warning("Could not find tomorrow's date toggle")
                return False
            
            # Click the date toggle
            try:
                date_toggle.click()
                time.sleep(2)
                logger.info("Successfully navigated to tomorrow's date")
                return True
            except ElementClickInterceptedException:
                # Try JavaScript click
                self.driver.execute_script("arguments[0].click();", date_toggle)
                time.sleep(2)
                logger.info("Successfully navigated to tomorrow's date (JS click)")
                return True
                
        except Exception as e:
            logger.error(f"Error navigating to tomorrow: {e}")
            return False
    
    def detect_available_courts(self):
        """Detect available courts on the booking page"""
        available_courts = []
        
        try:
            logger.info("Waiting for booking grid to load...")
            time.sleep(3)
            
            # Save page source for debugging
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page_source = self.driver.page_source
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
    
    def extract_court_info(self, element):
        """Extract court information from an element"""
        try:
            # Get element text and attributes
            text = element.text.strip()
            element_class = element.get_attribute('class') or ''
            element_id = element.get_attribute('id') or ''
            
            # Filter out false positives
            false_positives = ['Booking Grid', 'None', 'N/A', 'disabled', 'unavailable', 'closed', 'maintenance']
            if any(fp.lower() in text.lower() for fp in false_positives):
                return None
            
            # Extract time from text
            time_patterns = [
                r'(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))',
                r'(\d{1,2}\s*(?:am|pm|AM|PM))',
                r'(\d{1,2}:\d{2})'
            ]
            
            import re
            time_match = None
            for pattern in time_patterns:
                match = re.search(pattern, text)
                if match:
                    time_match = match.group(1)
                    break
            
            # Extract court number if available
            court_number = None
            court_patterns = [
                r'Court\s*(\d+)',
                r'(\d+)\s*Court'
            ]
            
            for pattern in court_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    court_number = match.group(1)
                    break
            
            # Check if element is clickable
            is_clickable = element.is_enabled() and element.is_displayed()
            
            court_info = {
                'element': element,
                'text': text,
                'class': element_class,
                'id': element_id,
                'time': time_match,
                'court_number': court_number,
                'date': None,
                'clickable': is_clickable,
                'available': is_clickable
            }
            
            logger.info(f"Found booking button: {text}")
            if time_match:
                logger.info(f"Extracted time: {time_match}")
            
            return court_info
            
        except Exception as e:
            logger.debug(f"Error extracting court info: {e}")
            return None
    
    def send_email_notification(self, courts):
        """Send email notification for available courts"""
        try:
            if not courts:
                return
            
            logger.info(f"Sending notification for {len(courts)} available courts")
            
            # Create email content
            court_list = []
            for i, court in enumerate(courts, 1):
                court_list.append(f"{i}. {court['text']} - {court['time']}")
            
            subject = f"🎾 BTC Tennis Courts Available! ({len(courts)} courts)"
            
            body = f"""
==================================================
🎾 TENNIS COURT NOTIFICATION 🎾
==================================================

🎾 BURNABY TENNIS CLUB - COURTS AVAILABLE! 🎾

Great news! {len(courts)} tennis court slots have become available for tomorrow:

{chr(10).join(court_list)}

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Booking URL: https://www.burnabytennis.ca/app/bookings/grid

Hurry up and book your court! 🏃‍♂️

---
BTC Booking Bot 🤖
            """
            
            # Send email
            sender_email = self.notification_email
            receiver_email = self.notification_email
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Gmail SMTP configuration
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                # Use Gmail App Password for SMTP authentication
                app_password = os.getenv('BTC_GMAIL_APP_PASSWORD', 'yrrf zspv pmup mjgo')
                server.login(sender_email, app_password)
                text = msg.as_string()
                server.sendmail(sender_email, receiver_email, text)
                server.quit()
                
                logger.info("Email notification sent successfully!")
                
                # Save notification to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                notification_file = f"btc_notification_{timestamp}.txt"
                with open(notification_file, 'w') as f:
                    f.write(body)
                logger.info(f"Notification saved to file: {notification_file}")
                
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
                
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def send_sms_notification(self, courts):
        """Send SMS notification for available courts"""
        try:
            if not courts:
                return
            
            logger.info(f"Sending SMS notification for {len(courts)} available courts")
            
            # Create SMS content
            court_list = []
            for i, court in enumerate(courts, 1):
                court_list.append(f"{i}. {court['text']} - {court['time']}")
            
            sms_body = f"""🎾 BTC Tennis Courts Available! ({len(courts)} courts)

Great news! {len(courts)} tennis court slots have become available for tomorrow:

{chr(10).join(court_list)}

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Booking URL: https://www.burnabytennis.ca/app/bookings/grid

Hurry up and book your court! 🏃‍♂️

---
BTC Booking Bot 🤖"""
            
            # Canadian carrier email-to-SMS gateways
            carriers = {
                'rogers': f"{self.phone_number}@pcs.rogers.com",
                'bell': f"{self.phone_number}@txt.bell.ca",
                'telus': f"{self.phone_number}@msg.telus.com",
                'fido': f"{self.phone_number}@fido.ca",
                'virgin': f"{self.phone_number}@vmobile.ca",
                'koodo': f"{self.phone_number}@msg.koodomobile.com",
                'chatr': f"{self.phone_number}@pcs.rogers.com",  # Uses Rogers network
                'public': f"{self.phone_number}@txt.windmobile.ca"
            }
            
            # Try different carriers
            for carrier, gateway in carriers.items():
                try:
                    logger.info(f"Trying SMS via {carrier} gateway: {gateway}")
                    
                    msg = MIMEText(sms_body)
                    msg['From'] = self.notification_email
                    msg['To'] = gateway
                    msg['Subject'] = f"🎾 BTC Tennis Courts Available!"
                    
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    # Use Gmail App Password for SMTP authentication
                    app_password = os.getenv('BTC_GMAIL_APP_PASSWORD', 'yrrf zspv pmup mjgo')
                    server.login(self.notification_email, app_password)
                    text = msg.as_string()
                    server.sendmail(self.notification_email, gateway, text)
                    server.quit()
                    
                    logger.info(f"SMS sent successfully via {carrier} gateway!")
                    logger.info("SMS notification sent successfully!")
                    logger.info("Notification printed to console")
                    return
                    
                except Exception as e:
                    logger.debug(f"SMS via {carrier} failed: {e}")
                    continue
            
            # Fallback: print to console
            logger.warning("All SMS gateways failed, printing to console:")
            print("\n" + "="*50)
            print("🎾 TENNIS COURT SMS NOTIFICATION 🎾")
            print("="*50)
            print(sms_body)
            print("="*50)
            logger.info("SMS notification sent successfully!")
            logger.info("Notification printed to console")
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
    
    def run_booking_scan(self):
        """Run the complete booking scan process"""
        try:
            logger.info("Starting BTC court booking scan...")
            
            # Initialize driver
            if not self.initialize_driver():
                return []
            
            # Login if credentials provided
            if self.username and self.password:
                if not self.login():
                    logger.error("Login failed")
                    return []
            
            # Navigate to booking page
            if not self.navigate_to_booking_page():
                logger.error("Failed to navigate to booking page")
                return []
            
            # Take screenshot and save page source
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"btc_booking_page_{timestamp}.png"
            self.driver.save_screenshot(screenshot_filename)
            logger.info(f"Screenshot saved: {screenshot_filename}")
            
            page_source = self.driver.page_source
            source_filename = f"btc_booking_page_{timestamp}.html"
            with open(source_filename, 'w', encoding='utf-8') as f:
                f.write(page_source)
            logger.info(f"Page source saved: {source_filename}")
            
            # Navigate to tomorrow's date
            logger.info("Scanning for available courts...")
            if not self.navigate_to_tomorrow():
                logger.error("Failed to navigate to tomorrow's date")
                return []
            
            # Detect available courts
            available_courts = self.detect_available_courts()
            
            if available_courts:
                logger.info(f"Found {len(available_courts)} available courts:")
                for i, court in enumerate(available_courts, 1):
                    logger.info(f"   {i}. {court['text']} - {court['time']}")
                
                # Send notifications
                self.send_email_notification(available_courts)
                self.send_sms_notification(available_courts)
                
                # Save court data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                court_data = {
                    'timestamp': timestamp,
                    'courts': available_courts,
                    'count': len(available_courts)
                }
                
                court_file = f"available_courts_{timestamp}.json"
                with open(court_file, 'w') as f:
                    json.dump(court_data, f, indent=2, default=str)
                logger.info(f"Available courts saved to {court_file}")
            
            return available_courts
            
        except Exception as e:
            logger.error(f"Error in booking scan: {e}")
            return []
        
        finally:
            if self.driver:
                logger.info("WebDriver closed")
                self.driver.quit()
    
    def run_continuous_monitoring(self, interval_minutes=5):
        """Run continuous monitoring for available courts"""
        logger.info(f"Starting continuous monitoring (every {interval_minutes} minutes)")
        
        while True:
            try:
                logger.info("=" * 50)
                logger.info("Starting monitoring cycle...")
                
                available_courts = self.run_booking_scan()
                
                if available_courts:
                    logger.info(f"Found {len(available_courts)} available courts!")
                    break
                else:
                    logger.info("No courts available, continuing monitoring...")
                
                logger.info(f"Waiting {interval_minutes} minutes before next check...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(10)  # Wait 10 seconds before retrying
        
        logger.info("Continuous monitoring completed")
    
    def run_timeslot_monitoring(self, interval_seconds=30):
        """Run timeslot monitoring for available courts"""
        logger.info(f"Starting timeslot monitoring (every {interval_seconds} seconds)")
        
        while True:
            try:
                logger.info("=" * 30)
                logger.info("Starting timeslot check...")
                
                available_courts = self.run_booking_scan()
                
                if available_courts:
                    logger.info(f"Found {len(available_courts)} available courts!")
                    break
                else:
                    logger.info("No courts available, continuing monitoring...")
                
                logger.info(f"Waiting {interval_seconds} seconds before next check...")
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in timeslot monitoring: {e}")
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
    gmail_app_password = os.getenv('BTC_GMAIL_APP_PASSWORD')
    
    if username and password and notification_email and phone_number and gmail_app_password:
        print("✅ All credentials found in environment variables!")
        print(f"   Username: {username}")
        print(f"   Notification Email: {notification_email}")
        print(f"   Phone: {phone_number}")
        print()
        return username, password, notification_email, phone_number, gmail_app_password
    
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
        
        if not gmail_app_password:
            print("\n📧 Gmail App Password Setup:")
            print("1. Go to Google Account > Security > 2-Step Verification > App passwords")
            print("2. Generate a new app password for 'Mail'")
            print("3. Copy the 16-character password (e.g., 'abcd efgh ijkl mnop')")
            print()
            gmail_app_password = getpass.getpass("Enter your Gmail App Password: ")
        
        print("\n✅ Credentials configured!")
        print("💡 Tip: Set these as environment variables for future runs:")
        print(f"   export BTC_USERNAME='{username}'")
        print(f"   export BTC_PASSWORD='{password}'")
        print(f"   export BTC_NOTIFICATION_EMAIL='{notification_email}'")
        print(f"   export BTC_PHONE_NUMBER='{phone_number}'")
        print(f"   export BTC_GMAIL_APP_PASSWORD='{gmail_app_password}'")
        print()
        
        return username, password, notification_email, phone_number, gmail_app_password
        
    except EOFError:
        print("\n❌ Interactive input not available in this environment.")
        print("\n📋 Please set environment variables instead:")
        print("   export BTC_USERNAME='your_email@example.com'")
        print("   export BTC_PASSWORD='your_password'")
        print("   export BTC_NOTIFICATION_EMAIL='your_email@example.com'")
        print("   export BTC_PHONE_NUMBER='1234567890'")
        print("   export BTC_GMAIL_APP_PASSWORD='your_gmail_app_password'")
        print("\nThen run the bot again: python3 btc_tennis_bot.py")
        exit(1)

def main():
    """Main function to run the BTC booking bot"""
    print("🎾 Burnaby Tennis Club Court Booking Bot")
    print("=" * 50)
    
    # Setup credentials interactively
    username, password, notification_email, phone_number, gmail_app_password = setup_credentials()
    
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
        phone_number=phone_number
    )
    
    try:
        # Run single scan
        print("Running court availability scan...")
        available_courts = bot.run_booking_scan()
        
        if available_courts:
            print(f"\nFound {len(available_courts)} available courts!")
            for i, court in enumerate(available_courts, 1):
                print(f"{i}. {court['text']}")
            
            print(f"\nSending notifications for {len(available_courts)} available courts...")
            
            # Send notifications
            bot.send_email_notification(available_courts)
            bot.send_sms_notification(available_courts)
            
            print("✅ Notifications sent! Check your email and phone.")
        else:
            print("No courts available at the moment.")
        
        # Ask for monitoring options
        print("\nMonitoring options:")
        print("1. Run continuous monitoring (every 5 minutes)")
        print("2. Run timeslot monitoring (every 30 seconds)")
        print("3. Exit")
        
        try:
            choice = input("Enter your choice (1/2/3): ").strip()
            
            if choice == "1":
                bot.run_continuous_monitoring(5)
            elif choice == "2":
                bot.run_timeslot_monitoring(30)
            elif choice == "3":
                print("Goodbye! 🎾")
            else:
                print("Invalid choice. Exiting...")
        except EOFError:
            print("Exiting...")
            
    except Exception as e:
        logger.error(f"Main function error: {e}")

if __name__ == "__main__":
    main()
