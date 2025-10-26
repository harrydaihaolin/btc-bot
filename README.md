# 🎾 Burnaby Tennis Club Court Booking Bot

An automated bot that monitors Burnaby Tennis Club's booking system and sends notifications when courts become available.

## 🚀 Features

- **Automatic Login**: Logs into the BTC website using your credentials
- **Real-time Monitoring**: Scans for available courts on tomorrow's bookings
- **Smart Detection**: Finds "Book" buttons and filters out false positives
- **Multi-channel Notifications**: 
  - Email notifications via Gmail SMTP
  - SMS notifications via email-to-SMS gateways
- **Continuous Monitoring**: Options for 5-minute or 30-second monitoring
- **Environment Variable Support**: Secure credential management
- **Interactive Setup**: Easy credential configuration

## 📋 Prerequisites

1. **Python 3.7+** with pip
2. **Chrome browser** (for Selenium WebDriver)
3. **Gmail account** with App Password enabled
4. **BTC account** with login credentials

## 🛠️ Installation

1. **Clone or download** the bot files
2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

## 🔧 Setup

### Option 1: Interactive Setup (Recommended)

Run the setup script:
```bash
chmod +x setup_credentials.sh
./setup_credentials.sh
```

### Option 2: Manual Environment Variables

Set these environment variables:
```bash
export BTC_USERNAME="your_email@example.com"
export BTC_PASSWORD="your_password"
export BTC_NOTIFICATION_EMAIL="your_email@example.com"
export BTC_PHONE_NUMBER="1234567890"
export BTC_GMAIL_APP_EMAIL="your_gmail@gmail.com"
export BTC_GMAIL_APP_PASSWORD="your_gmail_app_password"
export BTC_BOOKING_DATE="1"  # days ahead: "1" (tomorrow), "2" (day after), or specific date like "2025-10-27"
```

### Gmail App Password Setup

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Go to **App passwords**
4. Generate a new app password for **"Mail"**
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

## 🎯 Usage

### Basic Usage
```bash
python3 btc_tennis_bot.py
```

### With Environment Variables
```bash
export BTC_USERNAME="your_email@example.com"
export BTC_PASSWORD="your_password"
export BTC_NOTIFICATION_EMAIL="your_email@example.com"
export BTC_PHONE_NUMBER="1234567890"
export BTC_GMAIL_APP_EMAIL="your_gmail@gmail.com"
export BTC_GMAIL_APP_PASSWORD="your_gmail_app_password"
export BTC_BOOKING_DATE="1"
python3 btc_tennis_bot.py
```

## 📱 Notification Features

### Email Notifications
- Sent via Gmail SMTP
- Includes court details and booking URL
- Professional formatting with emojis

### SMS Notifications
- Supports Canadian carriers (Rogers, Bell, Telus, etc.)
- Uses email-to-SMS gateways
- Fallback to console output if SMS fails

## 🔍 How It Works

1. **Login**: Automatically logs into BTC website
2. **Navigate**: Goes to tomorrow's booking page
3. **Scan**: Finds all "Book" buttons on the page
4. **Filter**: Removes false positives like "Booking Grid - None"
5. **Notify**: Sends email and SMS when courts are found
6. **Monitor**: Optional continuous monitoring

## 📊 Monitoring Options

After the initial scan, you can choose:

1. **Continuous Monitoring** (every 5 minutes)
2. **Timeslot Monitoring** (every 30 seconds)
3. **Exit**

## 🛡️ Security

- Credentials are stored in environment variables
- Passwords are hidden during input
- Gmail App Passwords provide secure SMTP access
- No hardcoded credentials in the code

## 🐛 Troubleshooting

### Common Issues

1. **"Interactive input not available"**
   - Set environment variables instead
   - Use the setup script: `./setup_credentials.sh`

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
- `btc_mon27_page_source_*.html` - Tomorrow's page source
- `btc_notification_*.txt` - Notification logs
- `available_courts_*.json` - Court data

## 📝 Example Output

```
🎾 Burnaby Tennis Club Court Booking Bot
==================================================
✅ All credentials found in environment variables!
   Username: your_email@example.com
   Notification Email: your_email@example.com
   Phone: 1234567890

Running court availability scan...

Found 3 available courts!
1. Book 6:00 am as 48hr
2. Book 8:00 am as 48hr  
3. Book 4:00 pm as 48hr

✅ Notifications sent! Check your email and phone.
```

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the bot!

## 📄 License

This project is for personal use. Please respect the Burnaby Tennis Club's terms of service.

---

**Happy Tennis Booking! 🎾**
