#!/usr/bin/env python3
"""
Daemon Monitoring Script for BTC Tennis Bot
Default background monitoring mode with continuous court availability tracking
"""

import os
import sys
import time
import signal
import logging
import daemon
import daemon.pidfile
from datetime import datetime
from btc_tennis_bot import BTCCourtBookingBot, setup_credentials

# Configure logging for daemon process
def setup_logging():
    """Setup logging for daemon process"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('btc_daemon_monitoring.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class DaemonMonitor:
    """Daemon monitoring process for BTC Tennis Bot"""
    
    def __init__(self):
        self.running = True
        self.bot = None
        self.monitoring_interval = 5  # minutes
        self.max_attempts = 0  # 0 = unlimited for daemon mode
        self.logger = setup_logging()
        self.previous_courts = set()  # Track previous court availability
        
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
            self.logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            self.logger.error("Please set the following environment variables:")
            for var in missing_vars:
                self.logger.error(f"   export {var}='your_value'")
            return False
        
        self.logger.info("All required environment variables are set")
        return True
    
    def initialize_bot(self):
        """Initialize the BTC booking bot with environment variables"""
        try:
            self.logger.info("Initializing BTC Tennis Bot for daemon monitoring...")
            
            # Get credentials from environment variables
            username = os.getenv('BTC_USERNAME')
            password = os.getenv('BTC_PASSWORD')
            notification_email = os.getenv('BTC_NOTIFICATION_EMAIL')
            phone_number = os.getenv('BTC_PHONE_NUMBER')
            gmail_app_email = os.getenv('BTC_GMAIL_APP_EMAIL')
            gmail_app_password = os.getenv('BTC_GMAIL_APP_PASSWORD')
            
            # Initialize bot
            self.bot = BTCCourtBookingBot(
                headless=True,  # Run headless for daemon operation
                wait_timeout=15,  # Longer timeout for daemon operation
                username=username,
                password=password,
                notification_email=notification_email,
                phone_number=phone_number,
                gmail_app_email=gmail_app_email
            )
            
            self.logger.info("Bot initialized successfully for daemon monitoring")
            self.logger.info(f"Monitoring interval: {self.monitoring_interval} minutes")
            self.logger.info(f"Max attempts: {'Unlimited' if self.max_attempts == 0 else self.max_attempts}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {e}")
            return False
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle and detect new court availability"""
        try:
            self.logger.info("Running daemon monitoring cycle...")
            
            # Run booking scan
            available_courts = self.bot.run_booking_scan()
            
            # Flatten all courts for comparison
            current_courts = set()
            for date, courts in available_courts.items():
                for court in courts:
                    court_key = f"{date}_{court.get('time', '')}_{court.get('text', '')}"
                    current_courts.add(court_key)
            
            total_courts = sum(len(courts) for courts in available_courts.values())
            
            if total_courts > 0:
                # Check for new courts
                new_courts = current_courts - self.previous_courts
                
                if new_courts:
                    self.logger.info(f"🎾 NEW COURTS DETECTED! {len(new_courts)} new slots found!")
                    self.logger.info("Sending immediate notifications...")
                    
                    # Send notifications for new courts
                    self.bot.send_email_notification(available_courts)
                    self.bot.send_sms_notification(available_courts)
                    
                    # Log new court details
                    for date, courts in available_courts.items():
                        if courts:
                            date_obj = datetime.strptime(date, "%Y-%m-%d")
                            date_label = date_obj.strftime("%A, %B %d, %Y")
                            self.logger.info(f"   📅 {date_label}: {len(courts)} courts")
                            for i, court in enumerate(courts, 1):
                                self.logger.info(f"      {i}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}")
                else:
                    self.logger.info(f"Found {total_courts} courts but no new ones since last check")
                
                # Update previous courts set
                self.previous_courts = current_courts
            else:
                self.logger.info("No available courts found")
                self.previous_courts = set()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during monitoring cycle: {e}")
            return False
    
    def run_daemon(self):
        """Main daemon run method"""
        try:
            # Check environment variables
            if not self.check_environment_variables():
                self.logger.error("Environment variables not properly configured, exiting")
                return False
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Initialize bot
            if not self.initialize_bot():
                self.logger.error("Failed to initialize bot, exiting")
                return False
            
            # Run initial scan
            self.logger.info("Running initial court availability scan...")
            self.run_monitoring_cycle()
            
            # Start continuous monitoring
            self.logger.info(f"Starting daemon monitoring (every {self.monitoring_interval} minutes)")
            self.logger.info("🎾 Daemon will notify you immediately when new courts become available!")
            
            attempt = 0
            while self.running:
                try:
                    attempt += 1
                    self.logger.info(f"Daemon monitoring cycle {attempt}")
                    
                    # Run monitoring cycle
                    self.run_monitoring_cycle()
                    
                    # Check if we should continue
                    if self.max_attempts > 0 and attempt >= self.max_attempts:
                        self.logger.info(f"Reached maximum attempts ({self.max_attempts}), stopping daemon")
                        break
                    
                    if self.running and (attempt < self.max_attempts or self.max_attempts == 0):
                        self.logger.info(f"Waiting {self.monitoring_interval} minutes before next check...")
                        # Sleep in smaller intervals to allow for graceful shutdown
                        for _ in range(self.monitoring_interval * 60):
                            if not self.running:
                                break
                            time.sleep(1)
                    
                except KeyboardInterrupt:
                    self.logger.info("Daemon monitoring stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error during daemon monitoring: {e}")
                    if self.running:
                        self.logger.info("Waiting 60 seconds before retrying...")
                        for _ in range(60):
                            if not self.running:
                                break
                            time.sleep(1)
            
            self.logger.info("Daemon monitoring completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Fatal error in daemon monitoring: {e}")
            return False
        finally:
            if self.bot and self.bot.driver:
                self.bot.driver.quit()
                self.logger.info("WebDriver closed")

def main():
    """Main function for daemon monitoring"""
    print("🎾 BTC Tennis Bot - Daemon Monitoring Mode (DEFAULT)")
    print("=" * 70)
    print("This is the RECOMMENDED mode for continuous court monitoring")
    print("Features:")
    print("  ✅ Immediate email notifications when new courts become available")
    print("  ✅ SMS alerts for urgent court releases")
    print("  ✅ 24/7 background monitoring")
    print("  ✅ Detects new bookings as they're released")
    print("  ✅ Runs completely detached from terminal")
    print("=" * 70)
    
    # Get monitoring configuration
    try:
        interval_input = input("Enter monitoring interval in minutes (default 5): ").strip()
        monitoring_interval = int(interval_input) if interval_input else 5
        
        max_attempts_input = input("Enter maximum number of scans (0 for unlimited, default 0): ").strip()
        max_attempts = int(max_attempts_input) if max_attempts_input else 0
        
    except (EOFError, KeyboardInterrupt):
        print("\nUsing default settings: 5 minutes interval, unlimited scans")
        monitoring_interval = 5
        max_attempts = 0
    
    # Create daemon monitor
    monitor = DaemonMonitor()
    monitor.monitoring_interval = monitoring_interval
    monitor.max_attempts = max_attempts
    
    # Setup daemon context
    pidfile_path = f"btc_daemon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pid"
    
    print(f"\n🚀 Starting daemon process...")
    print(f"   PID file: {pidfile_path}")
    print(f"   Log file: btc_daemon_monitoring.log")
    print(f"   Monitoring interval: {monitoring_interval} minutes")
    print(f"   Max attempts: {'Unlimited' if max_attempts == 0 else max_attempts}")
    print("\n💡 To stop the daemon: kill $(cat {pidfile_path})")
    print("💡 To view logs: tail -f btc_daemon_monitoring.log")
    print("\n🎾 Daemon is now monitoring for new court availability!")
    
    with daemon.DaemonContext(
        pidfile=daemon.pidfile.PIDLockFile(pidfile_path),
        stdout=open('btc_daemon_stdout.log', 'w'),
        stderr=open('btc_daemon_stderr.log', 'w')
    ):
        success = monitor.run_daemon()
        
        if success:
            print("✅ Daemon monitoring completed successfully")
        else:
            print("❌ Daemon monitoring encountered errors")
            sys.exit(1)

if __name__ == "__main__":
    main()
