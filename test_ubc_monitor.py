#!/usr/bin/env python3
"""
UBC Tennis Court Monitor - Test Script
Quick test to verify UBC monitoring functionality
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ubc_config import UBCConfig
from core.ubc_monitor import UBCCourtMonitor
from core.ubc_notifications import UBCNotificationManager


def test_ubc_configuration():
    """Test UBC configuration"""
    print("🧪 Testing UBC Configuration...")

    try:
        config = UBCConfig()

        # Test credential validation
        if config.validate_credentials():
            print("✅ UBC credentials validation passed")
        else:
            print("❌ UBC credentials validation failed")
            print("   Please set UBC_USERNAME and UBC_PASSWORD environment variables")
            return False

        # Test notification config
        notif_config = config.get_notification_config()
        if notif_config["email"] or notif_config["sms_phone"]:
            print("✅ UBC notification configuration found")
        else:
            print("❌ No UBC notification method configured")
            return False

        # Test monitoring config
        monitoring_config = config.get_monitoring_config()
        print(
            f"✅ UBC monitoring config: {monitoring_config['monitoring_interval']} min interval"
        )

        return True

    except Exception as e:
        print(f"❌ UBC configuration test failed: {e}")
        return False


def test_ubc_notifications():
    """Test UBC notification system"""
    print("\n🧪 Testing UBC Notifications...")

    try:
        notification_manager = UBCNotificationManager()

        # Test notification formatting
        test_courts = {
            "2025-10-26": [
                {
                    "court_name": "Court 1",
                    "time": "10:00 AM",
                    "duration": "1 hour",
                    "price": "$32.15",
                },
                {
                    "court_name": "Court 2",
                    "time": "2:00 PM",
                    "duration": "1 hour",
                    "price": "$28.05",
                },
            ]
        }

        # Test email formatting
        email_body = notification_manager._format_email_message(test_courts)
        if "UBC Tennis Courts Available" in email_body:
            print("✅ UBC email formatting works")
        else:
            print("❌ UBC email formatting failed")
            return False

        # Test SMS formatting
        sms_body = notification_manager._format_sms_message(test_courts)
        if "UBC Tennis" in sms_body and "Court 1" in sms_body:
            print("✅ UBC SMS formatting works")
        else:
            print("❌ UBC SMS formatting failed")
            return False

        print("✅ UBC notification system test passed")
        return True

    except Exception as e:
        print(f"❌ UBC notification test failed: {e}")
        return False


def test_ubc_monitor():
    """Test UBC monitor (without actual web scraping)"""
    print("\n🧪 Testing UBC Monitor...")

    try:
        monitor = UBCCourtMonitor()

        # Test logger setup
        if monitor.logger:
            print("✅ UBC monitor logger initialized")
        else:
            print("❌ UBC monitor logger failed")
            return False

        # Test configuration access
        if monitor.config:
            print("✅ UBC monitor configuration loaded")
        else:
            print("❌ UBC monitor configuration failed")
            return False

        print("✅ UBC monitor test passed")
        return True

    except Exception as e:
        print(f"❌ UBC monitor test failed: {e}")
        return False


def main():
    """Run all UBC tests"""
    print("🎾 UBC Tennis Court Monitor - Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    print()

    tests_passed = 0
    total_tests = 3

    # Run tests
    if test_ubc_configuration():
        tests_passed += 1

    if test_ubc_notifications():
        tests_passed += 1

    if test_ubc_monitor():
        tests_passed += 1

    # Results
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All UBC tests passed! Ready for monitoring.")
        print("\nTo start UBC monitoring:")
        print("1. Set environment variables:")
        print("   export UBC_USERNAME='your_ubc_username'")
        print("   export UBC_PASSWORD='your_ubc_password'")
        print("   export UBC_NOTIFICATION_EMAIL='your_email@gmail.com'")
        print("   export GMAIL_APP_PASSWORD='your_gmail_app_password'")
        print("\n2. Run daemon:")
        print("   ./run_ubc_daemon.sh")
        return True
    else:
        print("❌ Some tests failed. Please fix configuration before monitoring.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
