# Release Notes

## Version 1.1.0 - Interactive Background Monitoring Mode
*Released: October 25, 2025*

### 🎯 Major Features

#### Interactive Background Monitoring Mode
- **Enhanced User Experience**: The bot now gracefully handles both interactive and non-interactive environments
- **Production-Ready**: Perfect for cron jobs and automated deployments while maintaining interactive capabilities
- **Smart Mode Detection**: Automatically detects environment and adjusts behavior accordingly

#### Multi-Date Scanning System
- **Comprehensive Coverage**: Automatically scans today, tomorrow, and day after tomorrow in a single run
- **Efficient Monitoring**: No need to specify booking dates - the bot checks all available dates
- **Enhanced Notifications**: Email and SMS notifications now organize courts by date for better clarity

### 🔧 Technical Improvements

#### Robust Error Handling
- **EOF Error Fix**: Resolved EOFError issues when running with environment variables
- **Graceful Degradation**: Bot continues to function even when interactive input is not available
- **Clear Messaging**: Better user guidance for interactive vs non-interactive modes

#### Enhanced Notification System
- **Idempotency**: Prevents duplicate notifications across all channels
- **Multi-Date Support**: Notifications now handle courts from multiple dates efficiently
- **Improved Formatting**: Better organized email and SMS messages with date-based grouping

#### Code Quality Improvements
- **Simplified Configuration**: Removed complex booking_date parameter - now always checks all dates
- **Better Data Structure**: Enhanced JSON saving with date-based organization
- **Memory Management**: Automatic cleanup of old notifications to prevent memory buildup

### 🚀 New Capabilities

#### Monitoring Options
1. **Continuous Monitoring**: Every 5 minutes (configurable)
2. **Timeslot Monitoring**: Every 30 seconds for rapid changes
3. **Single Scan Mode**: One-time comprehensive check

#### Enhanced User Interface
- **Interactive Setup**: Easy credential configuration with fallback to environment variables
- **Progress Indicators**: Clear feedback during scanning and monitoring
- **Debug Information**: Comprehensive logging and debug file generation

### 🛡️ Reliability Improvements

#### Production Readiness
- **Cron Job Compatible**: Works perfectly in automated environments
- **Environment Variable Support**: Secure credential management
- **Error Recovery**: Robust error handling with automatic retries

#### Performance Optimizations
- **Memory Efficiency**: Automatic cleanup of old notification data
- **Faster Scanning**: Optimized multi-date scanning process
- **Reduced False Positives**: Improved court detection algorithms

### 📱 Notification Enhancements

#### Email Notifications
- **Date-Organized**: Courts grouped by date for better readability
- **Rich Formatting**: Professional layout with emojis and clear structure
- **Multi-Date Support**: Handles courts from all scanned dates

#### SMS Notifications
- **Canadian Carrier Support**: Rogers, Bell, Telus, Fido, Virgin, Koodo
- **Fallback Options**: Multiple gateway attempts for reliability
- **Concise Format**: Optimized for SMS character limits

### 🔍 Debug and Monitoring

#### Enhanced Debugging
- **Screenshot Capture**: Automatic screenshots for troubleshooting
- **Page Source Saving**: HTML source saved for analysis
- **Comprehensive Logging**: Detailed logs for all operations

#### File Management
- **Automatic Cleanup**: Old debug files are managed efficiently
- **Structured Data**: JSON output with proper date organization
- **Notification Tracking**: Prevents duplicate notifications

### 🎾 User Experience

#### Simplified Usage
- **One-Command Operation**: `python3 btc_tennis_bot.py` does everything
- **Interactive Prompts**: Clear guidance for first-time setup
- **Environment Variable Support**: Secure credential management

#### Monitoring Flexibility
- **Multiple Intervals**: Choose between 5-minute or 30-second monitoring
- **Configurable Limits**: Set maximum scan attempts
- **Easy Exit**: Clean shutdown with Ctrl+C

### 🐛 Bug Fixes

- Fixed EOFError when running with environment variables
- Resolved email notification errors with multi-date data
- Improved court detection accuracy
- Enhanced error handling for network issues
- Fixed memory leaks in long-running monitoring

### 📋 Migration Guide

#### From v1.0 to v1.1
- **No Breaking Changes**: All existing functionality preserved
- **Enhanced Features**: New capabilities are additive
- **Environment Variables**: Existing setup continues to work
- **Improved Reliability**: Better error handling and recovery

#### New Environment Variables (Optional)
```bash
export BTC_GMAIL_APP_EMAIL="your_gmail@gmail.com"  # For SMTP authentication
export BTC_BOOKING_DATE="1"  # Now automatically checks all dates
```

### 🎯 What's Next

- **Advanced Filtering**: Court preference settings
- **Webhook Support**: Integration with external services
- **Mobile App**: Companion mobile application
- **Analytics Dashboard**: Usage statistics and trends

---

**Full Changelog**: [v1.0.0...v1.1.0](https://github.com/your-repo/btc-bot/compare/v1.0.0...v1.1.0)

**Download**: [v1.1.0 Release](https://github.com/your-repo/btc-bot/releases/tag/v1.1.0)

---

*Happy Tennis Booking! 🎾*
