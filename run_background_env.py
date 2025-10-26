#!/usr/bin/env python3
"""
Background Monitoring Script for BTC Tennis Bot (Environment Variables)
Runs the bot in background using environment variables for credentials
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime
from core.config import BTCConfig
from core.monitor import CourtMonitor
from core.notifications import NotificationManager

# Configure logging for background process
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('btc_background_env.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackgroundMonitor:
    """Background monitoring process for BTC Tennis Bot"""
    
    def __init__(self):
        self.running = True
        self.logger = logging.getLogger(__name__)
        self.config_manager = BTCConfig()
        self.monitor = None
        self.notification_manager = None
        self.credentials = None
        self.config = None
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def check_environment_variables(self):
        """Check if required environment variables are set"""
        if not self.config_manager.validate_credentials(self.credentials):
            self.logger.error("Environment variables not properly configured")
            return False
        
        self.logger.info("All required environment variables are set")
        return True
    
    def initialize_components(self):
        """Initialize all components"""
        try:
            # Get configuration
            self.credentials = self.config_manager.get_credentials()
            self.config = self.config_manager.get_bot_config()
            monitoring_config = self.config_manager.get_monitoring_config()
            
            # Validate credentials
            if not self.config_manager.validate_credentials(self.credentials):
                self.logger.error("Invalid credentials configuration")
                return False
            
            # Initialize monitor
            self.monitor = CourtMonitor(self.config, self.credentials)
            
            # Initialize notification manager
            self.notification_manager = NotificationManager(self.credentials)
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False
    
    def run_initial_scan(self):
        """Run initial scan to check for available courts"""
        try:
            self.logger.info("Running initial court availability scan...")
            
            # Setup driver
            self.monitor.setup_driver()
            
            # Login
            if not self.monitor.login():
                self.logger.warning("Login failed, continuing anyway...")
            
            # Navigate to booking page
            if not self.monitor.navigate_to_booking_page():
                self.logger.error("Failed to navigate to booking page")
                return {}
            
            # Scan all dates
            all_courts = self.monitor.scan_all_dates()
            
            total_courts = sum(len(courts) for courts in all_courts.values())
            
            if total_courts > 0:
                self.logger.info(f"Found {total_courts} available courts in initial scan!")
                for date, courts in all_courts.items():
                    if courts:
                        date_obj = datetime.strptime(date, "%Y-%m-%d")
                        date_label = date_obj.strftime("%A, %B %d, %Y")
                        self.logger.info(f"   {date_label}: {len(courts)} courts")
                        for i, court in enumerate(courts, 1):
                            self.logger.info(f"      {i}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}")
            else:
                self.logger.info("No available courts found in initial scan")
            
            return all_courts
            
        except Exception as e:
            self.logger.error(f"Error during initial scan: {e}")
            return {}
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring with configurable intervals"""
        monitoring_config = self.config_manager.get_monitoring_config()
        monitoring_interval = monitoring_config['monitoring_interval']
        max_attempts = monitoring_config['max_attempts']
        
        self.logger.info(f"Starting continuous background monitoring (every {monitoring_interval} minutes)")
        self.logger.info("Press Ctrl+C to stop monitoring")
        
        attempt = 0
        while self.running and (attempt < max_attempts or max_attempts == 0):
            try:
                attempt += 1
                self.logger.info(f"Background monitoring attempt {attempt}")
                
                # Run booking scan
                all_courts = self.run_initial_scan()
                
                total_courts = sum(len(courts) for courts in all_courts.values())
                
                if total_courts > 0:
                    self.logger.info(f"Found {total_courts} available courts!")
                    
                    # Detect new courts
                    new_courts = self.monitor.detect_new_courts(all_courts)
                    
                    if new_courts:
                        self.logger.info("Sending notifications for new courts...")
                        self.notification_manager.send_email_notification(new_courts)
                        self.notification_manager.send_sms_notification(new_courts)
                    else:
                        self.logger.info("No new courts detected")
                else:
                    self.logger.info("No available courts found")
                
                # Check if we should continue
                if max_attempts > 0 and attempt >= max_attempts:
                    self.logger.info(f"Reached maximum attempts ({max_attempts}), stopping monitoring")
                    break
                
                if self.running and (attempt < max_attempts or max_attempts == 0):
                    self.logger.info(f"Waiting {monitoring_interval} minutes before next scan...")
                    # Sleep in smaller intervals to allow for graceful shutdown
                    for _ in range(monitoring_interval * 60):
                        if not self.running:
                            break
                        time.sleep(1)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error during background monitoring: {e}")
                if self.running and (attempt < max_attempts or max_attempts == 0):
                    self.logger.info("Waiting 60 seconds before retrying...")
                    for _ in range(60):
                        if not self.running:
                            break
                        time.sleep(1)
        
        self.logger.info("Background monitoring completed")
    
    def run(self):
        """Main run method for background monitoring"""
        try:
            # Initialize components
            if not self.initialize_components():
                self.logger.error("Failed to initialize components, exiting")
                return False
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Run initial scan
            self.run_initial_scan()
            
            # Start continuous monitoring
            self.run_continuous_monitoring()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fatal error in background monitoring: {e}")
            return False
        finally:
            if self.monitor:
                self.monitor.cleanup()

def main():
    """Main function for background monitoring"""
    print("🎾 BTC Tennis Bot - Background Monitoring Mode (Environment Variables)")
    print("=" * 80)
    print("This will run the bot in background using environment variables")
    print("Make sure you have set the required environment variables:")
    print("   BTC_USERNAME, BTC_PASSWORD, BTC_NOTIFICATION_EMAIL")
    print("   BTC_PHONE_NUMBER, BTC_GMAIL_APP_EMAIL, BTC_GMAIL_APP_PASSWORD")
    print("=" * 80)
    
    # Create and run background monitor
    monitor = BackgroundMonitor()
    
    success = monitor.run()
    
    if success:
        print("✅ Background monitoring completed successfully")
    else:
        print("❌ Background monitoring encountered errors")
        sys.exit(1)

if __name__ == "__main__":
    main()