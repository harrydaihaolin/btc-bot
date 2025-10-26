#!/usr/bin/env python3
"""
UBC Tennis Court Daemon Monitor
Continuous background monitoring for UBC tennis court availability
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ubc_config import UBCConfig
from core.ubc_monitor import UBCCourtMonitor
from core.ubc_notifications import UBCNotificationManager


class UBCDaemonMonitor:
    """Daemon monitor for UBC tennis court availability"""

    def __init__(self):
        self.config = UBCConfig()
        self.monitor = UBCCourtMonitor()
        self.notification_manager = UBCNotificationManager()
        self.logger = self._setup_logger()
        self.running = False
        self.attempt_count = 0

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for UBC daemon"""
        logger = logging.getLogger("ubc_daemon")
        logger.setLevel(logging.INFO)

        # Create file handler
        log_config = self.config.get_logging_config()
        file_handler = logging.FileHandler(log_config["log_file"])
        file_handler.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(log_config["log_format"])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def validate_configuration(self) -> bool:
        """Validate all required configuration"""
        try:
            self.logger.info("Validating UBC configuration...")

            # Validate credentials
            if not self.config.validate_credentials():
                self.logger.error("❌ UBC credentials validation failed")
                return False

            # Validate notification config
            notif_config = self.config.get_notification_config()
            if not notif_config["email"] and not notif_config["sms_phone"]:
                self.logger.error(
                    "❌ No notification method configured (email or SMS required)"
                )
                return False

            self.logger.info("✅ UBC configuration validation successful")
            return True

        except Exception as e:
            self.logger.error(f"❌ Configuration validation error: {e}")
            return False

    def run_initial_scan(self) -> Dict[str, List[Dict]]:
        """Run initial court availability scan"""
        try:
            self.logger.info("Running initial UBC court availability scan...")

            # Run monitoring cycle
            new_courts = self.monitor.run_monitoring_cycle()

            if new_courts:
                total_courts = sum(len(courts) for courts in new_courts.values())
                self.logger.info(
                    f"Found {total_courts} available UBC courts in initial scan!"
                )

                # Log court details
                for date, courts in new_courts.items():
                    self.logger.info(f"   {date}: {len(courts)} courts")
                    for court in courts:
                        self.logger.info(
                            f"      - {court.get('court_name', 'Unknown')} at {court.get('time', 'Unknown')}"
                        )

                # Send notifications for initial findings
                self.notification_manager.send_notifications(new_courts)
            else:
                self.logger.info("No UBC courts found in initial scan")

            return new_courts

        except Exception as e:
            self.logger.error(f"Error during initial UBC scan: {e}")
            return {}

    def run_monitoring_cycle(self) -> None:
        """Run a single monitoring cycle"""
        try:
            self.attempt_count += 1
            monitoring_config = self.config.get_monitoring_config()

            self.logger.info(f"UBC monitoring attempt {self.attempt_count}")

            # Check max attempts
            if (
                monitoring_config["max_attempts"] > 0
                and self.attempt_count > monitoring_config["max_attempts"]
            ):
                self.logger.info(
                    f"Reached max attempts ({monitoring_config['max_attempts']}), stopping monitoring"
                )
                self.running = False
                return

            # Run monitoring cycle
            new_courts = self.monitor.run_monitoring_cycle()

            if new_courts:
                total_new = sum(len(courts) for courts in new_courts.values())
                self.logger.info(
                    f"🎾 NEW UBC COURTS DETECTED! {total_new} new slots found!"
                )

                # Send notifications
                self.logger.info("Sending notifications for new UBC courts...")
                self.notification_manager.send_notifications(new_courts)
            else:
                self.logger.info("No new UBC courts detected")

            # Wait before next scan
            interval_minutes = monitoring_config["monitoring_interval"]
            self.logger.info(
                f"Waiting {interval_minutes} minutes before next UBC scan..."
            )

        except Exception as e:
            self.logger.error(f"Error in UBC monitoring cycle: {e}")

    def start_monitoring(self) -> None:
        """Start continuous UBC monitoring"""
        try:
            self.logger.info("🚀 Starting UBC Tennis Court Daemon Monitoring...")
            self.logger.info("=" * 60)

            # Validate configuration
            if not self.validate_configuration():
                self.logger.error("Configuration validation failed, exiting")
                return

            # Initialize components
            self.logger.info("Initializing UBC monitoring components...")

            # Run initial scan
            self.run_initial_scan()

            # Start continuous monitoring
            self.running = True
            monitoring_config = self.config.get_monitoring_config()

            self.logger.info(
                f"Starting continuous UBC background monitoring (every {monitoring_config['monitoring_interval']} minutes)"
            )
            self.logger.info("Press Ctrl+C to stop monitoring")

            while self.running:
                try:
                    self.run_monitoring_cycle()

                    if self.running:
                        # Sleep for the monitoring interval
                        sleep_seconds = monitoring_config["monitoring_interval"] * 60
                        time.sleep(sleep_seconds)

                except KeyboardInterrupt:
                    self.logger.info(
                        "Received keyboard interrupt, stopping UBC monitoring..."
                    )
                    break
                except Exception as e:
                    self.logger.error(f"Error in UBC monitoring loop: {e}")
                    # Continue monitoring despite errors
                    time.sleep(60)  # Wait 1 minute before retrying

            self.logger.info("UBC monitoring stopped")

        except Exception as e:
            self.logger.error(f"Fatal error in UBC monitoring: {e}")
        finally:
            # Cleanup
            try:
                self.monitor.cleanup()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")


def main():
    """Main function for UBC daemon monitoring"""
    try:
        print("🎾 UBC Tennis Court Monitor - Daemon Mode")
        print("=" * 50)

        # Create and start daemon monitor
        daemon = UBCDaemonMonitor()
        daemon.start_monitoring()

    except KeyboardInterrupt:
        print("\n👋 UBC monitoring stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
