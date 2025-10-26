#!/usr/bin/env python3
"""
UBC Tennis Court Monitor - Credentials Setup Script
Interactive setup for UBC login credentials
"""

import getpass
import os
import sys


def setup_ubc_credentials():
    """Interactive setup for UBC credentials"""
    print("🎾 UBC Tennis Court Monitor - Credentials Setup")
    print("=" * 50)
    print()
    print("This script will help you set up your UBC Recreation login credentials.")
    print("You'll need your UBC CWL (Campus Wide Login) username and password.")
    print()
    print("Note: If you already have BTC credentials set up, you can use those")
    print("for testing UBC monitoring. UBC-specific credentials will take priority.")
    print()

    # Check if BTC credentials are already available
    btc_username = os.getenv("BTC_USERNAME")
    btc_password = os.getenv("BTC_PASSWORD")

    if btc_username and btc_password:
        print(f"✅ Found existing BTC credentials: {btc_username}")
        use_btc = (
            input("Use BTC credentials for UBC testing? (y/n, default: y): ")
            .strip()
            .lower()
        )
        if use_btc in ["", "y", "yes"]:
            username = btc_username
            password = btc_password
            print("✅ Using BTC credentials for UBC testing")
        else:
            username = None
            password = None
    else:
        username = None
        password = None

    # Get UBC username if not using BTC credentials
    if not username:
        while True:
            username = input(
                "Enter your UBC CWL username (e.g., student@ubc.ca): "
            ).strip()
            if username:
                break
            print("❌ Username cannot be empty. Please try again.")

    # Get UBC password if not using BTC credentials
    if not password:
        while True:
            password = getpass.getpass("Enter your UBC CWL password: ").strip()
            if password:
                break
            print("❌ Password cannot be empty. Please try again.")

    # Get notification email
    print()
    print("Notification Settings:")
    print("You can use the same email as your BTC bot or a different one.")

    while True:
        email = input(
            "Enter notification email (optional, press Enter to skip): "
        ).strip()
        if not email:
            email = os.getenv("GMAIL_APP_EMAIL", "")
            if email:
                print(f"Using existing email: {email}")
            break
        elif "@" in email:
            break
        print("❌ Please enter a valid email address.")

    # Get Gmail app password
    gmail_password = ""
    if email:
        while True:
            gmail_password = getpass.getpass(
                "Enter Gmail app password (optional, press Enter to skip): "
            ).strip()
            if not gmail_password:
                gmail_password = os.getenv("GMAIL_APP_PASSWORD", "")
                if gmail_password:
                    print("Using existing Gmail app password")
                break
            elif len(gmail_password) >= 16:
                break
            print("❌ Gmail app password should be at least 16 characters.")

    # Get SMS phone number
    print()
    sms_phone = input(
        "Enter SMS phone number (optional, press Enter to skip): "
    ).strip()
    if not sms_phone:
        sms_phone = os.getenv("SMS_PHONE", "")
        if sms_phone:
            print(f"Using existing SMS phone: {sms_phone}")

    # Generate export commands
    print()
    print("📋 Add these lines to your ~/.zshrc file:")
    print()
    print("# UBC Tennis Court Monitor Credentials")

    # Only show UBC credentials if they're different from BTC
    if username != btc_username or password != btc_password:
        print(f"export UBC_USERNAME='{username}'")
        print(f"export UBC_PASSWORD='{password}'")
    else:
        print("# Using BTC credentials for UBC testing (no additional setup needed)")

    if email:
        print(f"export UBC_NOTIFICATION_EMAIL='{email}'")

    if gmail_password:
        print(f"export UBC_GMAIL_APP_PASSWORD='{gmail_password}'")

    if sms_phone:
        print(f"export UBC_SMS_PHONE='{sms_phone}'")

    # Optional configuration
    print()
    print("# Optional UBC Configuration")
    print("export UBC_MONITORING_INTERVAL='5'  # minutes")
    print("export UBC_MAX_ATTEMPTS='0'  # 0 = unlimited")
    print("export UBC_LOG_FILE='ubc_monitoring.log'")
    print()

    # Test configuration
    print("🧪 Testing configuration...")

    # Set environment variables for testing
    os.environ["UBC_USERNAME"] = username
    os.environ["UBC_PASSWORD"] = password
    if email:
        os.environ["UBC_NOTIFICATION_EMAIL"] = email
    if gmail_password:
        os.environ["UBC_GMAIL_APP_PASSWORD"] = gmail_password
    if sms_phone:
        os.environ["UBC_SMS_PHONE"] = sms_phone

    try:
        from core.ubc_config import UBCConfig

        config = UBCConfig()

        if config.validate_credentials():
            print("✅ UBC configuration validation successful!")
            print()
            print("🎉 Setup complete! You can now run UBC monitoring:")
            print("   ./run_ubc_daemon.sh")
        else:
            print("❌ Configuration validation failed")
            return False

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

    return True


def main():
    """Main function"""
    try:
        success = setup_ubc_credentials()
        if success:
            print("\n🎾 UBC Tennis Court Monitor is ready!")
        else:
            print("\n❌ Setup failed. Please check your credentials.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
