#!/usr/bin/env python3
"""
Daemon Monitoring Script for BTC Tennis Bot
Default background monitoring mode with continuous court availability tracking
"""

import logging
import os
import signal
import sys
import time
from datetime import datetime

import daemon
import daemon.pidfile

from core.config import BTCConfig
from core.monitor import CourtMonitor
from core.notifications import NotificationManager


# Configure logging for daemon process
def setup_logging():
    """Setup logging for daemon process"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("btc_daemon_monitoring.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


class DaemonMonitor:
    """Daemon monitoring process for BTC Tennis Bot"""

    def __init__(self):
        self.running = True
        self.logger = setup_logging()
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

    def run_monitoring_cycle(self):
        """Run one monitoring cycle and detect new court availability"""
        try:
            self.logger.info("Running daemon monitoring cycle...")

            # Setup driver if not already done
            if not self.monitor.driver:
                self.monitor.setup_driver()

            # Login
            if not self.monitor.login():
                self.logger.warning("Login failed, continuing anyway...")

            # Navigate to booking page
            if not self.monitor.navigate_to_booking_page():
                self.logger.error("Failed to navigate to booking page")
                return False

            # Scan all dates
            all_courts = self.monitor.scan_all_dates()

            total_courts = sum(len(courts) for courts in all_courts.values())

            if total_courts > 0:
                # Detect new courts
                new_courts = self.monitor.detect_new_courts(all_courts)

                if new_courts:
                    self.logger.info(
                        "Sending immediate notifications for new courts..."
                    )

                    # Send notifications for new courts
                    self.notification_manager.send_email_notification(new_courts)
                    self.notification_manager.send_sms_notification(new_courts)

                    # Log new court details
                    for date, courts in new_courts.items():
                        if courts:
                            date_obj = datetime.strptime(date, "%Y-%m-%d")
                            date_label = date_obj.strftime("%A, %B %d, %Y")
                            self.logger.info(
                                f"   📅 {date_label}: {len(courts)} courts"
                            )
                            for i, court in enumerate(courts, 1):
                                self.logger.info(
                                    f"      {i}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}"
                                )
                else:
                    self.logger.info(
                        f"Found {total_courts} courts but no new ones since last check"
                    )
            else:
                self.logger.info("No available courts found")

            return True

        except Exception as e:
            self.logger.error(f"Error during monitoring cycle: {e}")
            return False

    def run_daemon(self):
        """Main daemon run method"""
        try:
            # Setup signal handlers
            self.setup_signal_handlers()

            # Initialize components
            if not self.initialize_components():
                self.logger.error("Failed to initialize components, exiting")
                return False

            # Get monitoring configuration
            monitoring_config = self.config_manager.get_monitoring_config()
            monitoring_interval = monitoring_config["monitoring_interval"]
            max_attempts = monitoring_config["max_attempts"]

            # Run initial scan
            self.logger.info("Running initial court availability scan...")
            self.run_monitoring_cycle()

            # Start continuous monitoring
            self.logger.info(
                f"Starting daemon monitoring (every {monitoring_interval} minutes)"
            )
            self.logger.info(
                "🎾 Daemon will notify you immediately when new courts become available!"
            )

            attempt = 0
            while self.running:
                try:
                    attempt += 1
                    self.logger.info(f"Daemon monitoring cycle {attempt}")

                    # Run monitoring cycle
                    self.run_monitoring_cycle()

                    # Check if we should continue
                    if max_attempts > 0 and attempt >= max_attempts:
                        self.logger.info(
                            f"Reached maximum attempts ({max_attempts}), stopping daemon"
                        )
                        break

                    if self.running and (attempt < max_attempts or max_attempts == 0):
                        self.logger.info(
                            f"Waiting {monitoring_interval} minutes before next check..."
                        )
                        # Sleep in smaller intervals to allow for graceful shutdown
                        for _ in range(monitoring_interval * 60):
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
            if self.monitor:
                self.monitor.cleanup()


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
        interval_input = input(
            "Enter monitoring interval in minutes (default 5): "
        ).strip()
        monitoring_interval = int(interval_input) if interval_input else 5

        max_attempts_input = input(
            "Enter maximum number of scans (0 for unlimited, default 0): "
        ).strip()
        max_attempts = int(max_attempts_input) if max_attempts_input else 0

        # Set environment variables for this session
        os.environ["BTC_MONITORING_INTERVAL"] = str(monitoring_interval)
        os.environ["BTC_MAX_ATTEMPTS"] = str(max_attempts)

    except (EOFError, KeyboardInterrupt):
        print("\nUsing default settings: 5 minutes interval, unlimited scans")
        monitoring_interval = 5
        max_attempts = 0

    # Create daemon monitor
    monitor = DaemonMonitor()

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
        stdout=open("btc_daemon_stdout.log", "w"),
        stderr=open("btc_daemon_stderr.log", "w"),
    ):
        success = monitor.run_daemon()

        if success:
            print("✅ Daemon monitoring completed successfully")
        else:
            print("❌ Daemon monitoring encountered errors")
            sys.exit(1)


if __name__ == "__main__":
    main()
