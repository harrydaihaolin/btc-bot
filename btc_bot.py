#!/usr/bin/env python3
"""
🎾 BTC Tennis Court Booking Bot 🎾

A specialized tennis court booking bot for Burnaby Tennis Club (BTC).
This bot automates the process of checking for available tennis courts
and notifying users when courts become available for booking.
"""

import getpass
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import BTC-specific components
from btc.config.btc_config import BTCConfig
from btc.monitor.btc_monitor import BTCMonitor
from btc.notifications.btc_notifications import BTCNotificationManager


class BTCTennisBot:
    """BTC Tennis Court Booking Bot"""

    def __init__(self):
        self.config = BTCConfig()
        self.monitor = BTCMonitor(self.config)
        self.notifications = BTCNotificationManager(self.config)
        self.setup_logging()

    def setup_logging(self):
        """Set up logging configuration"""
        log_config = self.config.get_logging_config()
        logging.basicConfig(
            level=getattr(logging, log_config["log_level"]),
            format=log_config["log_format"],
            handlers=[
                logging.FileHandler(log_config["log_file"]),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def setup_credentials(self) -> Dict[str, str]:
        """Set up credentials interactively or from environment"""
        try:
            credentials = self.config.get_credentials()
            self.logger.info("✅ Using credentials from environment variables")
            return credentials
        except ValueError as e:
            self.logger.warning(f"⚠️  {e}")
            self.logger.info("🔐 Please enter your BTC credentials:")
            
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ").strip()
            
            return {"username": username, "password": password}

    def run_single_scan(self):
        """Run a single court availability scan"""
        self.logger.info("🔍 Starting single court scan...")
        
        try:
            credentials = self.setup_credentials()
            
            # Use the base monitor's monitoring cycle which handles login
            available_courts = self.monitor.run_monitoring_cycle()
            
            if available_courts:
                self.logger.info(f"🎾 Found {len(available_courts)} available courts!")
                for date, courts in available_courts.items():
                    self.logger.info(f"  - {date}: {len(courts)} courts")
                
                # Send notifications
                self.notifications.send_notifications(available_courts)
                self.logger.info("📧 Notifications sent!")
            else:
                self.logger.info("😔 No available courts found")
                
        except Exception as e:
            self.logger.error(f"❌ Error during scan: {e}")
        finally:
            self.monitor.cleanup()

    def run_continuous_monitoring(self):
        """Run continuous monitoring"""
        self.logger.info("🔄 Starting continuous monitoring...")
        
        try:
            credentials = self.setup_credentials()
            monitoring_config = self.config.get_monitoring_config()
            interval = monitoring_config["monitoring_interval"]
            
            self.logger.info(f"⏰ Monitoring every {interval} minutes")
            
            while True:
                try:
                    # Use the base monitor's monitoring cycle which handles login
                    available_courts = self.monitor.run_monitoring_cycle()
                    
                    if available_courts:
                        total_courts = sum(len(courts) for courts in available_courts.values())
                        self.logger.info(f"🎾 Found {total_courts} available courts!")
                        for date, courts in available_courts.items():
                            self.logger.info(f"  - {date}: {len(courts)} courts")
                        
                        # Send notifications
                        self.notifications.send_notifications(available_courts)
                        self.logger.info("📧 Notifications sent!")
                    else:
                        self.logger.info("😔 No available courts found")
                    
                    self.logger.info(f"⏳ Waiting {interval} minutes before next scan...")
                    time.sleep(interval * 60)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error during monitoring cycle: {e}")
                    self.logger.info("⏳ Waiting 5 minutes before retry...")
                    time.sleep(300)  # Wait 5 minutes before retry
                    
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {e}")
        finally:
            self.monitor.cleanup()

    def run_timeslot_monitoring(self):
        """Run monitoring for specific timeslots"""
        self.logger.info("🎯 Starting timeslot monitoring...")
        
        try:
            credentials = self.setup_credentials()
            monitoring_config = self.config.get_monitoring_config()
            interval = monitoring_config["monitoring_interval"]
            
            # Get preferred timeslots from user
            self.logger.info("📅 Enter your preferred timeslots (format: HH:MM, one per line, empty line to finish):")
            timeslots = []
            while True:
                timeslot = input("Timeslot: ").strip()
                if not timeslot:
                    break
                timeslots.append(timeslot)
            
            if not timeslots:
                self.logger.warning("⚠️  No timeslots specified, monitoring all available courts")
                self.run_continuous_monitoring()
                return
            
            self.logger.info(f"🎯 Monitoring timeslots: {', '.join(timeslots)}")
            self.logger.info(f"⏰ Checking every {interval} minutes")
            
            while True:
                try:
                    available_courts = self.monitor.scan_available_courts()
                    
                    # Filter courts by preferred timeslots
                    preferred_courts = []
                    for court in available_courts:
                        for timeslot in timeslots:
                            if timeslot in court:
                                preferred_courts.append(court)
                                break
                    
                    if preferred_courts:
                        self.logger.info(f"🎾 Found {len(preferred_courts)} courts in preferred timeslots!")
                        for court in preferred_courts:
                            self.logger.info(f"  - {court}")
                        
                        # Send notifications
                        self.notifications.send_notifications(preferred_courts)
                        self.logger.info("📧 Notifications sent!")
                    else:
                        self.logger.info("😔 No courts available in preferred timeslots")
                    
                    self.logger.info(f"⏳ Waiting {interval} minutes before next scan...")
                    time.sleep(interval * 60)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error during monitoring cycle: {e}")
                    self.logger.info("⏳ Waiting 5 minutes before retry...")
                    time.sleep(300)  # Wait 5 minutes before retry
                    
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {e}")
        finally:
            self.monitor.cleanup()


def main():
    """Main entry point for BTC Tennis Bot"""
    print("🎾 BTC Tennis Court Booking Bot 🎾")
    print("=" * 40)
    
    bot = BTCTennisBot()
    
    # Check if running in non-interactive mode (e.g., Docker)
    is_docker = os.getenv("IS_DOCKER", "false").lower() == "true"
    force_interactive = os.getenv("FORCE_INTERACTIVE", "false").lower() == "true"
    
    if is_docker and not force_interactive:
        bot.logger.info("🐳 Running in non-interactive mode (Docker)")
        bot.run_continuous_monitoring()
        return
    
    # Interactive mode
    while True:
        print("\n📋 Choose monitoring mode:")
        print("1. Single scan")
        print("2. Continuous monitoring")
        print("3. Timeslot monitoring")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            bot.run_single_scan()
        elif choice == "2":
            bot.run_continuous_monitoring()
        elif choice == "3":
            bot.run_timeslot_monitoring()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
