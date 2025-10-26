#!/usr/bin/env python3
"""
Modular Tennis Court Monitor - Test Script
Test the new modular structure with debug logging
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modular components
from btc.config.btc_config import BTCConfig
from btc.monitor.btc_monitor import BTCMonitor
from btc.notifications.btc_notifications import BTCNotificationManager

from ubc.config.ubc_config import UBCConfig
from ubc.monitor.ubc_monitor import UBCMonitor
from ubc.notifications.ubc_notifications import UBCNotificationManager


def setup_debug_logging():
    """Setup debug logging for testing"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("modular_test.log")],
    )


def test_btc_configuration():
    """Test BTC configuration"""
    print("🧪 Testing BTC Configuration...")

    try:
        config = BTCConfig()

        # Test credential validation
        if config.validate_credentials():
            print("✅ BTC credentials validation passed")
        else:
            print("❌ BTC credentials validation failed")
            print("   Please set BTC_USERNAME and BTC_PASSWORD environment variables")
            return False

        # Test notification config
        notif_config = config.get_notification_config()
        if notif_config["email"] or notif_config["sms_phone"]:
            print("✅ BTC notification configuration found")
        else:
            print("❌ No BTC notification method configured")
            return False

        # Test monitoring config
        monitoring_config = config.get_monitoring_config()
        print(
            f"✅ BTC monitoring config: {monitoring_config['monitoring_interval']} min interval"
        )

        return True

    except Exception as e:
        print(f"❌ BTC configuration test failed: {e}")
        return False


def test_ubc_configuration():
    """Test UBC configuration"""
    print("\n🧪 Testing UBC Configuration...")

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


def test_btc_notifications():
    """Test BTC notification system"""
    print("\n🧪 Testing BTC Notifications...")

    try:
        notification_manager = BTCNotificationManager()

        # Test notification formatting
        test_courts = {
            "2025-10-26": [
                {
                    "court_name": "Court 1",
                    "time": "10:00 AM",
                    "duration": "1 hour",
                    "price": "$25.00",
                }
            ]
        }

        # Test email formatting
        email_body = notification_manager._format_email_message(test_courts)
        if "Burnaby Tennis Club Courts Available" in email_body:
            print("✅ BTC email formatting works")
        else:
            print("❌ BTC email formatting failed")
            return False

        # Test SMS formatting
        sms_body = notification_manager._format_sms_message(test_courts)
        if "Burnaby Tennis Club" in sms_body and "Court 1" in sms_body:
            print("✅ BTC SMS formatting works")
        else:
            print("❌ BTC SMS formatting failed")
            return False

        print("✅ BTC notification system test passed")
        return True

    except Exception as e:
        print(f"❌ BTC notification test failed: {e}")
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
                }
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


def test_btc_monitor():
    """Test BTC monitor (without actual web scraping)"""
    print("\n🧪 Testing BTC Monitor...")

    try:
        monitor = BTCMonitor()

        # Test logger setup
        if monitor.logger:
            print("✅ BTC monitor logger initialized")
        else:
            print("❌ BTC monitor logger failed")
            return False

        # Test configuration access
        if monitor.config:
            print("✅ BTC monitor configuration loaded")
        else:
            print("❌ BTC monitor configuration failed")
            return False

        print("✅ BTC monitor test passed")
        return True

    except Exception as e:
        print(f"❌ BTC monitor test failed: {e}")
        return False


def test_ubc_monitor():
    """Test UBC monitor (without actual web scraping)"""
    print("\n🧪 Testing UBC Monitor...")

    try:
        monitor = UBCMonitor()

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
    """Run all modular tests"""
    print("🎾 Modular Tennis Court Monitor - Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()

    # Setup debug logging
    setup_debug_logging()

    tests_passed = 0
    total_tests = 6

    # Run tests
    if test_btc_configuration():
        tests_passed += 1

    if test_ubc_configuration():
        tests_passed += 1

    if test_btc_notifications():
        tests_passed += 1

    if test_ubc_notifications():
        tests_passed += 1

    if test_btc_monitor():
        tests_passed += 1

    if test_ubc_monitor():
        tests_passed += 1

    # Results
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All modular tests passed! Structure is working correctly.")
        print("\nModular structure:")
        print("📁 common/ - Shared base classes")
        print("📁 btc/ - Burnaby Tennis Club specific modules")
        print("📁 ubc/ - UBC Tennis Centre specific modules")
        print("\nDebug logs saved to: modular_test.log")
        return True
    else:
        print("❌ Some tests failed. Please check the debug logs.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
