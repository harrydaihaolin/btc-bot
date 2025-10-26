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
from btc_tennis_bot import BTCCourtBookingBot

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
        self.bot = None
        self.monitoring_interval = 5  # minutes
        self.max_attempts = 10  # Limited attempts for background operation
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def check_environment_variables(self):
        """Check if required environment variables are set"""
        required_vars = [
            'BTC_USERNAME',
            'BTC_PASSWORD', 
            'BTC_NOTIFICATION_EMAIL',
            'BTC_PHONE_NUMBER',
            'BTC_GMAIL_APP_EMAIL',
            'BTC_GMAIL_APP_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please set the following environment variables:")
            for var in missing_vars:
                logger.error(f"   export {var}='your_value'")
            return False
        
        logger.info("All required environment variables are set")
        return True
    
    def initialize_bot(self):
        """Initialize the BTC booking bot with environment variables"""
        try:
            logger.info("Initializing BTC Tennis Bot for background monitoring...")
            
            # Get credentials from environment variables
            username = os.getenv('BTC_USERNAME')
            password = os.getenv('BTC_PASSWORD')
            notification_email = os.getenv('BTC_NOTIFICATION_EMAIL')
            phone_number = os.getenv('BTC_PHONE_NUMBER')
            gmail_app_email = os.getenv('BTC_GMAIL_APP_EMAIL')
            gmail_app_password = os.getenv('BTC_GMAIL_APP_PASSWORD')
            
            # Initialize bot
            self.bot = BTCCourtBookingBot(
                headless=True,  # Run headless for background operation
                wait_timeout=15,  # Longer timeout for background operation
                username=username,
                password=password,
                notification_email=notification_email,
                phone_number=phone_number,
                gmail_app_email=gmail_app_email
            )
            
            logger.info("Bot initialized successfully for background monitoring")
            logger.info(f"Monitoring interval: {self.monitoring_interval} minutes")
            logger.info(f"Max attempts: {self.max_attempts}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
    def run_initial_scan(self):
        """Run initial scan to check for available courts"""
        try:
            logger.info("Running initial court availability scan...")
            available_courts = self.bot.run_booking_scan()
            
            total_courts = sum(len(courts) for courts in available_courts.values())
            
            if total_courts > 0:
                logger.info(f"Found {total_courts} available courts in initial scan!")
                for date, courts in available_courts.items():
                    if courts:
                        date_obj = datetime.strptime(date, "%Y-%m-%d")
                        date_label = date_obj.strftime("%A, %B %d, %Y")
                        logger.info(f"   {date_label}: {len(courts)} courts")
                        for i, court in enumerate(courts, 1):
                            logger.info(f"      {i}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}")
            else:
                logger.info("No available courts found in initial scan")
            
            return available_courts
            
        except Exception as e:
            logger.error(f"Error during initial scan: {e}")
            return {}
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring with configurable intervals"""
        logger.info(f"Starting continuous background monitoring (every {self.monitoring_interval} minutes)")
        logger.info("Press Ctrl+C to stop monitoring")
        
        attempt = 0
        while self.running and attempt < self.max_attempts:
            try:
                attempt += 1
                logger.info(f"Background monitoring attempt {attempt}/{self.max_attempts}")
                
                # Run booking scan
                available_courts = self.bot.run_booking_scan()
                
                total_courts = sum(len(courts) for courts in available_courts.values())
                
                if total_courts > 0:
                    logger.info(f"Found {total_courts} available courts!")
                    for date, courts in available_courts.items():
                        if courts:
                            date_obj = datetime.strptime(date, "%Y-%m-%d")
                            date_label = date_obj.strftime("%A, %B %d, %Y")
                            logger.info(f"   {date_label}: {len(courts)} courts")
                else:
                    logger.info("No available courts found")
                
                # Check if we should continue
                if attempt < self.max_attempts and self.running:
                    logger.info(f"Waiting {self.monitoring_interval} minutes before next scan...")
                    # Sleep in smaller intervals to allow for graceful shutdown
                    for _ in range(self.monitoring_interval * 60):
                        if not self.running:
                            break
                        time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error during background monitoring: {e}")
                if self.running and attempt < self.max_attempts:
                    logger.info("Waiting 60 seconds before retrying...")
                    for _ in range(60):
                        if not self.running:
                            break
                        time.sleep(1)
        
        logger.info("Background monitoring completed")
    
    def run(self):
        """Main run method for background monitoring"""
        try:
            # Check environment variables
            if not self.check_environment_variables():
                logger.error("Environment variables not properly configured, exiting")
                return False
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Initialize bot
            if not self.initialize_bot():
                logger.error("Failed to initialize bot, exiting")
                return False
            
            # Run initial scan
            self.run_initial_scan()
            
            # Start continuous monitoring
            self.run_continuous_monitoring()
            
            return True
            
        except Exception as e:
            logger.error(f"Fatal error in background monitoring: {e}")
            return False
        finally:
            if self.bot and self.bot.driver:
                self.bot.driver.quit()
                logger.info("WebDriver closed")

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
