#!/bin/bash
"""
🎾 BTC Tennis Bot - Credential Setup Script 🎾

This script helps you set up environment variables for the tennis booking bot.
Run this script to configure your credentials interactively.
"""

echo "🎾 BTC Tennis Bot - Credential Setup"
echo "======================================"
echo "Setting up your credentials for the tennis booking bot..."
echo ""

# Function to read password securely
read_password() {
    local prompt="$1"
    local password=""
    echo -n "$prompt"
    read -s password
    echo ""
    echo "$password"
}

# Get credentials
echo "Enter your BTC login credentials:"
read -p "BTC Login Email: " BTC_USERNAME
BTC_PASSWORD=$(read_password "BTC Login Password: ")
read -p "Notification Email (default: same as login): " BTC_NOTIFICATION_EMAIL
read -p "Phone Number (e.g., 6479370971): " BTC_PHONE_NUMBER
read -p "Gmail App Email (default: same as notification email): " BTC_GMAIL_APP_EMAIL
read -p "Booking Date (default: tomorrow, or use YYYY-MM-DD): " BTC_BOOKING_DATE

# Use login email as default for notification email
if [ -z "$BTC_NOTIFICATION_EMAIL" ]; then
    BTC_NOTIFICATION_EMAIL="$BTC_USERNAME"
fi

# Use notification email as default for Gmail app email
if [ -z "$BTC_GMAIL_APP_EMAIL" ]; then
    BTC_GMAIL_APP_EMAIL="$BTC_NOTIFICATION_EMAIL"
fi

# Use tomorrow as default for booking date
if [ -z "$BTC_BOOKING_DATE" ]; then
    BTC_BOOKING_DATE="tomorrow"
fi

echo ""
echo "📧 Gmail App Password Setup:"
echo "1. Go to Google Account > Security > 2-Step Verification > App passwords"
echo "2. Generate a new app password for 'Mail'"
echo "3. Copy the 16-character password (e.g., 'abcd efgh ijkl mnop')"
echo ""
BTC_GMAIL_APP_PASSWORD=$(read_password "Gmail App Password: ")

echo ""
echo "✅ Credentials configured!"
echo ""
echo "💡 To use these credentials, run:"
echo "export BTC_USERNAME='$BTC_USERNAME'"
echo "export BTC_PASSWORD='$BTC_PASSWORD'"
echo "export BTC_NOTIFICATION_EMAIL='$BTC_NOTIFICATION_EMAIL'"
echo "export BTC_PHONE_NUMBER='$BTC_PHONE_NUMBER'"
echo "export BTC_GMAIL_APP_EMAIL='$BTC_GMAIL_APP_EMAIL'"
echo "export BTC_GMAIL_APP_PASSWORD='$BTC_GMAIL_APP_PASSWORD'"
echo "export BTC_BOOKING_DATE='$BTC_BOOKING_DATE'"
echo ""
echo "Then run: python3 btc.py"
echo ""
echo "🎾 Ready to book some tennis courts! 🎾"
