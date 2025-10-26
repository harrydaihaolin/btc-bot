#!/usr/bin/env python3
"""
🎾 Unified Tennis Court Booking Bot 🎾

A generalized tennis court booking bot that supports multiple facilities:
- Burnaby Tennis Club (BTC)
- UBC Tennis Centre (UBC)

This bot automates the process of checking for available tennis courts
and notifying users when courts become available for booking.
"""

import os
import sys
import time
import logging
import getpass
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modular components
from btc.config.btc_config import BTCConfig
from btc.monitor.btc_monitor import BTCMonitor
from btc.notifications.btc_notifications import BTCNotificationManager

from ubc.config.ubc_config import UBCConfig
from ubc.monitor.ubc_monitor import UBCMonitor
from ubc.notifications.ubc_notifications import UBCNotificationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tennis_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TennisCourtBot:
    """Unified tennis court booking bot supporting multiple facilities"""
    
    def __init__(self, facility: str = "BTC"):
        """
        Initialize the tennis court bot
        
        Args:
            facility: "BTC" for Burnaby Tennis Club or "UBC" for UBC Tennis Centre
        """
        self.facility = facility.upper()
        
        if self.facility == "BTC":
            self.config = BTCConfig()
            self.monitor = BTCMonitor()
            self.notification_manager = BTCNotificationManager()
        elif self.facility == "UBC":
            self.config = UBCConfig()
            self.monitor = UBCMonitor()
            self.notification_manager = UBCNotificationManager()
        else:
            raise ValueError(f"Unsupported facility: {facility}. Supported facilities: BTC, UBC")
        
        logger.info(f"Initialized {self.facility} Tennis Court Bot")
    
    def setup_credentials(self) -> Dict[str, str]:
        """Interactive credential setup"""
        print(f"🎾 {self.facility} Tennis Bot - Credential Setup")
        print("=" * 50)
        print(f"Setting up your credentials for the {self.facility} tennis booking bot...")
        print()
        
        # Check if environment variables are already set
        try:
            credentials = self.config.get_credentials()
            notif_config = self.config.get_notification_config()
            
            if self.config.validate_credentials():
                print("✅ All credentials found in environment variables!")
                print(f"   Username: {credentials['username']}")
                print(f"   Notification Email: {notif_config['email']}")
                print(f"   SMS Phone: {notif_config['sms_phone'] or 'Not set'}")
                print()
                return credentials
        except Exception as e:
            logger.info(f"Environment variables not complete: {e}")
        
        print("🔧 Interactive Credential Setup")
        print("Please provide your login credentials:")
        print()
        
        # Get username
        while True:
            username = input(f"Enter your {self.facility} username/email: ").strip()
            if username:
                break
            print("❌ Username cannot be empty. Please try again.")
        
        # Get password
        while True:
            password = getpass.getpass(f"Enter your {self.facility} password: ").strip()
            if password:
                break
            print("❌ Password cannot be empty. Please try again.")
        
        # Get notification email
        print()
        print("Notification Settings:")
        email = input("Enter your notification email: ").strip()
        
        # Get Gmail App Password if email is Gmail
        gmail_password = None
        if email and email.endswith('@gmail.com'):
            print("Since you're using Gmail, you'll need a Gmail App Password.")
            print("Generate one here: https://myaccount.google.com/apppasswords")
            gmail_password = getpass.getpass("Enter your Gmail App Password: ").strip()
        
        # Get SMS phone number (optional)
        print()
        print("SMS Notifications (Optional):")
        sms_phone = input("Enter your SMS phone number (e.g., +1234567890): ").strip()
        
        # Generate export commands
        print()
        print("📋 Add these lines to your ~/.zshrc file:")
        print()
        print(f"# {self.facility} Tennis Court Monitor Credentials")
        
        if self.facility == "BTC":
            print(f"export BTC_USERNAME='{username}'")
            print(f"export BTC_PASSWORD='{password}'")
            if email:
                print(f"export BTC_NOTIFICATION_EMAIL='{email}'")
            if gmail_password:
                print(f"export BTC_GMAIL_APP_PASSWORD='{gmail_password}'")
            if sms_phone:
                print(f"export BTC_SMS_PHONE='{sms_phone}'")
        elif self.facility == "UBC":
            print(f"export UBC_USERNAME='{username}'")
            print(f"export UBC_PASSWORD='{password}'")
            if email:
                print(f"export UBC_NOTIFICATION_EMAIL='{email}'")
            if gmail_password:
                print(f"export UBC_GMAIL_APP_PASSWORD='{gmail_password}'")
            if sms_phone:
                print(f"export UBC_SMS_PHONE='{sms_phone}'")
        
        print()
        print("After adding, run 'source ~/.zshrc' to apply changes.")
        
        return {
            'username': username,
            'password': password,
            'email': email,
            'gmail_password': gmail_password,
            'sms_phone': sms_phone
        }
    
    def run_single_scan(self) -> Dict[str, List[Dict]]:
        """Run a single court availability scan"""
        try:
            logger.info(f"Starting {self.facility} court booking scan...")
            
            # Run monitoring cycle
            available_courts = self.monitor.run_monitoring_cycle()
            
            if available_courts:
                total_courts = sum(len(courts) for courts in available_courts.values())
                logger.info(f"Found {total_courts} available {self.facility} courts")
                
                # Send notifications
                self.notification_manager.send_notifications(available_courts)
                
                return available_courts
            else:
                logger.info(f"No available {self.facility} courts found")
                return {}
                
        except Exception as e:
            logger.error(f"Error during {self.facility} scan: {e}")
            return {}
    
    def run_continuous_monitoring(self, interval_minutes: int = 5, max_attempts: int = 0):
        """Run continuous monitoring"""
        logger.info(f"Starting continuous {self.facility} monitoring (every {interval_minutes} minutes)")
        
        attempt_count = 0
        while True:
            try:
                attempt_count += 1
                logger.info(f"Monitoring attempt #{attempt_count}")
                
                # Run scan
                available_courts = self.run_single_scan()
                
                # Check if we should stop
                if max_attempts > 0 and attempt_count >= max_attempts:
                    logger.info(f"Reached maximum attempts ({max_attempts}), stopping monitoring")
                    break
                
                # Wait for next scan
                logger.info(f"Waiting {interval_minutes} minutes until next scan...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def run_timeslot_monitoring(self, interval_seconds: int = 30, max_attempts: int = 0):
        """Run timeslot monitoring (faster scanning)"""
        logger.info(f"Starting timeslot {self.facility} monitoring (every {interval_seconds} seconds)")
        
        attempt_count = 0
        while True:
            try:
                attempt_count += 1
                logger.info(f"Timeslot monitoring attempt #{attempt_count}")
                
                # Run scan
                available_courts = self.run_single_scan()
                
                # Check if we should stop
                if max_attempts > 0 and attempt_count >= max_attempts:
                    logger.info(f"Reached maximum attempts ({max_attempts}), stopping monitoring")
                    break
                
                # Wait for next scan
                logger.info(f"Waiting {interval_seconds} seconds until next scan...")
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Timeslot monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in timeslot monitoring cycle: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying


def main():
    """Main function for the unified tennis bot"""
    print("🎾 Unified Tennis Court Booking Bot")
    print("=" * 50)
    print("Supported facilities:")
    print("  BTC - Burnaby Tennis Club")
    print("  UBC - UBC Tennis Centre")
    print()
    
    # Get facility choice
    while True:
        facility_choice = input("Choose facility (BTC/UBC): ").strip().upper()
        if facility_choice in ["BTC", "UBC"]:
            break
        print("❌ Please enter BTC or UBC")
    
    # Initialize bot
    try:
        bot = TennisCourtBot(facility_choice)
    except Exception as e:
        print(f"❌ Error initializing {facility_choice} bot: {e}")
        return
    
    # Setup credentials
    try:
        credentials = bot.setup_credentials()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        return
    except Exception as e:
        print(f"❌ Error during credential setup: {e}")
        return
    
    # Run single scan
    print()
    print("Running court availability scan...")
    available_courts = bot.run_single_scan()
    
    if available_courts:
        total_courts = sum(len(courts) for courts in available_courts.values())
        print(f"\nFound {total_courts} available {facility_choice} courts!")
        
        for date, courts in available_courts.items():
            print(f"\n📅 {date}: {len(courts)} courts")
            for i, court in enumerate(courts, 1):
                print(f"   {i}. {court.get('court_name', 'Unknown')} at {court.get('time', 'Unknown')}")
        
        print("\n✅ Notifications sent! Check your email and phone.")
    else:
        print(f"\nNo available {facility_choice} courts found.")
    
    # Ask for monitoring options
    print()
    print("Monitoring options:")
    print("1. Run continuous monitoring (every 5 minutes)")
    print("2. Run timeslot monitoring (every 30 seconds)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("Enter your choice (1/2/3): ").strip()
            
            if choice == "1":
                interval = input("Enter monitoring interval in minutes (default 5): ").strip()
                interval = int(interval) if interval else 5
                bot.run_continuous_monitoring(interval)
                break
            elif choice == "2":
                interval = input("Enter monitoring interval in seconds (default 30): ").strip()
                interval = int(interval) if interval else 30
                bot.run_timeslot_monitoring(interval)
                break
            elif choice == "3":
                print("Exiting...")
                break
            else:
                print("❌ Please enter 1, 2, or 3")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except ValueError:
            print("❌ Please enter a valid number")
        except Exception as e:
            print(f"❌ Error: {e}")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
