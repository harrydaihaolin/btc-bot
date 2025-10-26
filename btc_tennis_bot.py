#!/usr/bin/env python3
"""
🎾 Burnaby Tennis Club Court Booking Bot 🎾

This bot automates the process of checking for available tennis courts
and notifying users when courts become available for booking.
"""

import os
import sys
import time
import logging
import getpass
from datetime import datetime
from core.config import BTCConfig
from core.monitor import CourtMonitor
from core.notifications import NotificationManager

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

def setup_credentials():
    """Interactive credential setup"""
    print("🎾 BTC Tennis Bot - Credential Setup")
    print("=" * 50)
    print("Setting up your credentials for the tennis booking bot...")
    print()
    
    # Check if environment variables are already set
    config_manager = BTCConfig()
    credentials = config_manager.get_credentials()
    
    if config_manager.validate_credentials(credentials):
        print("✅ All credentials found in environment variables!")
        print(f"   Username: {credentials['username']}")
        print(f"   Notification Email: {credentials['notification_email']}")
        print(f"   Gmail App Email: {credentials['gmail_app_email'] or 'Not set'}")
        print(f"   Phone: {credentials['phone_number']}")
        print()
        return credentials
    
    print("🔧 Interactive Credential Setup")
    print("=" * 30)
    
    try:
        # Get credentials interactively
        if not credentials['username']:
            credentials['username'] = input("Enter your BTC login email: ").strip()
        
        if not credentials['password']:
            credentials['password'] = getpass.getpass("Enter your BTC login password: ")
        
        if not credentials['notification_email']:
            credentials['notification_email'] = input("Enter notification email (default: same as login): ").strip()
            if not credentials['notification_email']:
                credentials['notification_email'] = credentials['username']
        
        if not credentials['phone_number']:
            credentials['phone_number'] = input("Enter your phone number (e.g., 6479370971): ").strip()
        
        if not credentials['gmail_app_email']:
            credentials['gmail_app_email'] = input("Enter Gmail address for SMTP (default: same as notification email): ").strip()
            if not credentials['gmail_app_email']:
                credentials['gmail_app_email'] = credentials['notification_email']
        
        if not credentials['gmail_app_password']:
            print("\n📧 Gmail App Password Setup:")
            print("1. Go to Google Account > Security > 2-Step Verification > App passwords")
            print("2. Generate a new app password for 'Mail'")
            print("3. Copy the 16-character password (e.g., 'abcd efgh ijkl mnop')")
            print()
            credentials['gmail_app_password'] = getpass.getpass("Enter your Gmail App Password: ")
        
        print("\n✅ Credentials configured!")
        print("💡 Tip: Set these as environment variables for future runs:")
        print(f"   export BTC_USERNAME='{credentials['username']}'")
        print(f"   export BTC_PASSWORD='{credentials['password']}'")
        print(f"   export BTC_NOTIFICATION_EMAIL='{credentials['notification_email']}'")
        print(f"   export BTC_PHONE_NUMBER='{credentials['phone_number']}'")
        print(f"   export BTC_GMAIL_APP_EMAIL='{credentials['gmail_app_email']}'")
        print(f"   export BTC_GMAIL_APP_PASSWORD='{credentials['gmail_app_password']}'")
        print()
        
        return credentials
        
    except EOFError:
        print("\n❌ Interactive input not available in this environment.")
        print("\n📋 Please set environment variables instead:")
        print("   export BTC_USERNAME='your_email@example.com'")
        print("   export BTC_PASSWORD='your_password'")
        print("   export BTC_NOTIFICATION_EMAIL='your_email@example.com'")
        print("   export BTC_PHONE_NUMBER='1234567890'")
        print("   export BTC_GMAIL_APP_PASSWORD='your_gmail_app_password'")
        print("\nThen run the bot again: python3 btc_tennis_bot.py")
        sys.exit(1)

def run_single_scan(monitor, notification_manager):
    """Run a single court availability scan"""
    try:
        logger.info("Starting BTC court booking scan...")
        
        # Setup driver
        monitor.setup_driver()
        
        # Login
        if not monitor.login():
            logger.warning("Login failed, continuing anyway...")
        
        # Navigate to booking page
        if not monitor.navigate_to_booking_page():
            logger.error("Failed to navigate to booking page")
            return {}
        
        # Wait a bit for page to fully load
        time.sleep(3)
        
        # Take a screenshot for debugging
        try:
            screenshot_path = f"btc_booking_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            monitor.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.debug(f"Could not save screenshot: {e}")
        
        # Scan all available dates
        all_courts = monitor.scan_all_dates()
        
        # Count total courts across all dates
        total_courts = sum(len(courts) for courts in all_courts.values())
        
        if total_courts > 0:
            logger.info(f"Found {total_courts} available courts across all dates:")
            for date, courts in all_courts.items():
                if courts:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    date_label = date_obj.strftime("%A, %B %d, %Y")
                    logger.info(f"   {date_label}: {len(courts)} courts")
                    for i, court in enumerate(courts, 1):
                        logger.info(f"      {i}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}")
        else:
            logger.info("No available courts found across all dates")
        
        return all_courts
        
    except Exception as e:
        logger.error(f"Error during booking scan: {e}")
        return {}
    finally:
        if monitor.driver:
            monitor.cleanup()

def run_continuous_monitoring(monitor, notification_manager, interval_minutes=5, max_attempts=10):
    """Run continuous monitoring for available courts"""
    logger.info(f"Starting continuous monitoring (every {interval_minutes} minutes)")
    
    attempt = 0
    while attempt < max_attempts:
        try:
            attempt += 1
            logger.info(f"Scan attempt {attempt}/{max_attempts}")
            
            available_courts = run_single_scan(monitor, notification_manager)
            
            if available_courts:
                total_courts = sum(len(courts) for courts in available_courts.values())
                logger.info(f"Found {total_courts} available courts!")
                
                # Send notifications
                notification_manager.send_email_notification(available_courts)
                notification_manager.send_sms_notification(available_courts)
            
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

def main():
    """Main function to run the BTC booking bot"""
    print("🎾 Burnaby Tennis Club Court Booking Bot")
    print("=" * 50)
    
    # Setup credentials
    credentials = setup_credentials()
    
    # Get configuration
    config_manager = BTCConfig()
    config = config_manager.get_bot_config()
    
    # Initialize components
    monitor = CourtMonitor(config, credentials)
    notification_manager = NotificationManager(credentials)
    
    try:
        # Run single scan
        print("Running court availability scan...")
        available_courts = run_single_scan(monitor, notification_manager)
        
        # Count total courts across all dates
        total_courts = sum(len(courts) for courts in available_courts.values())
        
        if total_courts > 0:
            print(f"\nFound {total_courts} available courts across all dates!")
            for date, courts in available_courts.items():
                if courts:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    date_label = date_obj.strftime("%A, %B %d, %Y")
                    print(f"\n📅 {date_label}: {len(courts)} courts")
                    for i, court in enumerate(courts, 1):
                        print(f"   {i}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}")
        else:
            print("No available courts found across all dates.")
        
        # Send notifications for available courts
        if total_courts > 0:
            print(f"\nSending notifications for {total_courts} available courts...")
            notification_manager.send_email_notification(available_courts)
            notification_manager.send_sms_notification(available_courts)
            print("✅ Notifications sent! Check your email and phone.")
        else:
            print("No courts to notify about.")
        
        # Ask user if they want to run monitoring
        try:
            print("\nMonitoring options:")
            print("1. Run continuous monitoring (every 5 minutes)")
            print("2. Run timeslot monitoring (every 30 seconds)")
            print("3. Exit")
            
            choice = input("Enter your choice (1/2/3): ").strip()
            
            if choice == '1':
                interval = int(input("Enter monitoring interval in minutes (default 5): ") or "5")
                max_attempts = int(input("Enter maximum number of scans (default 10): ") or "10")
                run_continuous_monitoring(monitor, notification_manager, interval, max_attempts)
            elif choice == '2':
                interval = int(input("Enter monitoring interval in seconds (default 30): ") or "30")
                max_attempts = int(input("Enter maximum number of checks (default 120): ") or "120")
                # Convert seconds to minutes for the monitoring function
                run_continuous_monitoring(monitor, notification_manager, interval/60, max_attempts)
            else:
                print("Exiting...")
        except EOFError:
            print("\n✅ Single scan completed successfully!")
            print("💡 To run continuous monitoring, use the bot in interactive mode.")
            print("   (Run without environment variables to enable interactive mode)")
    
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Main function error: {e}")

if __name__ == "__main__":
    main()