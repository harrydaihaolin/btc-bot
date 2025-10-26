# 🎾 Burnaby Tennis Club Court Booking Bot

An automated bot that monitors Burnaby Tennis Club's booking system and sends notifications when courts become available.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Set Up Credentials
```bash
# Option A: Interactive setup
./setup_credentials.sh

# Option B: Manual environment variables
export BTC_USERNAME="your_email@example.com"
export BTC_PASSWORD="your_password"
export BTC_NOTIFICATION_EMAIL="your_email@example.com"
export BTC_PHONE_NUMBER="1234567890"
export BTC_GMAIL_APP_EMAIL="your_gmail@gmail.com"
export BTC_GMAIL_APP_PASSWORD="your_gmail_app_password"
```

### 3. Run the Bot
```bash
# Interactive mode
python3 btc_tennis_bot.py

# Background monitoring (production)
nohup python3 run_background_env.py > btc_background.log 2>&1 &
```

## 🎯 Features

- **Multi-Date Scanning**: Automatically checks today, tomorrow, and day after tomorrow
- **Smart Detection**: Finds "Book" buttons and filters out false positives
- **Background Monitoring**: Run as detached processes for 24/7 monitoring
- **Multi-channel Notifications**: 
  - Email notifications via Gmail SMTP
  - SMS notifications via email-to-SMS gateways
- **Production Ready**: Perfect for cron jobs and automated deployments

## 📱 Usage Modes

### Interactive Mode
Perfect for manual use and testing:
```bash
python3 btc_tennis_bot.py
```
- Prompts for credentials if not set
- Shows real-time progress
- Offers monitoring options after initial scan

### Background Mode
Perfect for production and automation:
```bash
# Set environment variables first
export BTC_USERNAME="your_email@example.com"
export BTC_PASSWORD="your_password"
export BTC_NOTIFICATION_EMAIL="your_email@example.com"
export BTC_PHONE_NUMBER="1234567890"
export BTC_GMAIL_APP_EMAIL="your_gmail@gmail.com"
export BTC_GMAIL_APP_PASSWORD="your_gmail_app_password"

# Start background monitoring
nohup python3 run_background_env.py > btc_background.log 2>&1 &
```

### Process Management
```bash
# Check if running
ps aux | grep run_background_env

# View logs
tail -f btc_background.log

# Stop process
pkill -f run_background_env
```

## 🔧 Setup Guide

### Gmail App Password Setup
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Go to **App passwords**
4. Generate a new app password for **"Mail"**
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Environment Variables
```bash
BTC_USERNAME="your_email@example.com"           # BTC login email
BTC_PASSWORD="your_password"                     # BTC login password
BTC_NOTIFICATION_EMAIL="your_email@example.com" # Email for notifications
BTC_PHONE_NUMBER="1234567890"                   # Phone for SMS (10 digits)
BTC_GMAIL_APP_EMAIL="your_gmail@gmail.com"      # Gmail for SMTP
BTC_GMAIL_APP_PASSWORD="your_gmail_app_password" # Gmail app password
```

## 📊 How It Works

1. **Login**: Automatically logs into BTC website
2. **Multi-Date Scan**: Checks today, tomorrow, and day after tomorrow
3. **Smart Detection**: Finds all "Book" buttons across all dates
4. **Filter**: Removes false positives like "Booking Grid - None"
5. **Organize**: Groups courts by date for clear notifications
6. **Notify**: Sends email and SMS when courts are found
7. **Monitor**: Optional continuous monitoring with configurable intervals

## 📱 Notifications

### Email Notifications
- Sent via Gmail SMTP
- Includes court details and booking URL
- Professional formatting with emojis
- Date-organized court listings

### SMS Notifications
- Supports Canadian carriers (Rogers, Bell, Telus, etc.)
- Uses email-to-SMS gateways
- Concise format optimized for SMS
- Fallback to console output if SMS fails

## 🖥️ Background Monitoring

### Available Scripts
- **`run_background_env.py`** - Production mode with environment variables
- **`start_background_monitoring.sh`** - Interactive startup script

### Configuration
- **Monitoring Interval**: 5 minutes (configurable)
- **Max Attempts**: 10 cycles (50 minutes total)
- **Headless Mode**: Always enabled for background operation
- **Logging**: Comprehensive logs for debugging

### Monitoring Commands
```bash
# Start background monitoring
nohup python3 run_background_env.py > btc_background.log 2>&1 &

# Check process status
ps aux | grep run_background_env

# View real-time logs
tail -f btc_background.log

# Stop monitoring
pkill -f run_background_env
```

## 🐛 Troubleshooting

### Common Issues

1. **"Interactive input not available"**
   - Set environment variables instead
   - Use: `export BTC_USERNAME="your_email"` etc.

2. **"Login failed"**
   - Check your BTC credentials
   - Ensure the website is accessible

3. **"Email sending failed"**
   - Verify Gmail App Password
   - Check 2-Step Verification is enabled

4. **"No courts found"**
   - This is normal - courts are only available when someone cancels
   - The bot will notify you when courts become available

### Debug Files
The bot creates several debug files:
- `btc_booking_page_*.png` - Screenshots
- `btc_booking_page_*.html` - Page source
- `btc_notification_*.txt` - Notification logs
- `available_courts_*.json` - Court data

## 📝 Example Output

```
🎾 Burnaby Tennis Club Court Booking Bot
==================================================
✅ All credentials found in environment variables!

Running court availability scan...

Found 5 available courts across all dates!

📅 Today, October 25, 2025: 2 courts
   1. Book 6:00 am as 48hr
   2. Book 8:00 am as 48hr

📅 Tomorrow, October 26, 2025: 2 courts
   1. Book 4:00 pm as 48hr
   2. Book 6:00 pm as 48hr

📅 Day after tomorrow, October 27, 2025: 1 court
   1. Book 2:00 pm as 48hr

✅ Notifications sent! Check your email and phone.

Monitoring options:
1. Run continuous monitoring (every 5 minutes)
2. Run timeslot monitoring (every 30 seconds)
3. Exit
```

## 📋 Version History

### v1.1.0 - Interactive Background Monitoring Mode
- **Multi-Date Scanning**: Automatically checks today, tomorrow, and day after tomorrow
- **Background Monitoring**: Run as detached processes for 24/7 monitoring
- **Enhanced Notifications**: Date-organized email and SMS notifications
- **Production Ready**: Perfect for cron jobs and automated deployments
- **Process Management**: PID files, graceful shutdown, and monitoring tools

### v1.0.0 - Initial Release
- Basic court monitoring and notification system
- Single-date scanning (tomorrow only)
- Email and SMS notifications
- Interactive setup and credential management

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the bot!

## 📄 License

This project is for personal use. Please respect the Burnaby Tennis Club's terms of service.

---

**Happy Tennis Booking! 🎾**