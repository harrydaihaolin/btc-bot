# 🎾 BTC Tennis Bot - Background Monitoring Guide

## Overview

The Background Monitoring Mode allows you to run the BTC Tennis Bot as a detached process that continuously monitors for available tennis courts without requiring user interaction. This is perfect for:

- **Cron Jobs**: Automated scheduling
- **Server Deployment**: Running on remote servers
- **Long-term Monitoring**: 24/7 court availability tracking
- **Hands-off Operation**: Set it and forget it

## 🚀 Quick Start

### 1. Set Up Environment Variables

```bash
export BTC_USERNAME="your_email@example.com"
export BTC_PASSWORD="your_password"
export BTC_NOTIFICATION_EMAIL="your_email@example.com"
export BTC_PHONE_NUMBER="1234567890"
export BTC_GMAIL_APP_EMAIL="your_gmail@gmail.com"
export BTC_GMAIL_APP_PASSWORD="your_gmail_app_password"
```

### 2. Start Background Monitoring

```bash
# Method 1: Simple background process
nohup python3 run_background_env.py > btc_background.log 2>&1 &

# Method 2: Using the startup script
./start_background_monitoring.sh

# Method 3: Daemon mode (completely detached)
python3 daemon_monitoring.py
```

## 📋 Available Background Scripts

### 1. `run_background_env.py` - Environment Variable Mode
**Best for**: Production environments, cron jobs, server deployment

**Features**:
- Uses environment variables for credentials
- No interactive prompts
- Headless operation
- Configurable monitoring intervals
- Limited attempts (10 cycles by default)

**Usage**:
```bash
nohup python3 run_background_env.py > btc_background.log 2>&1 &
```

### 2. `start_background_monitoring.sh` - Interactive Startup
**Best for**: Manual setup with user interaction

**Features**:
- Interactive configuration
- PID file management
- Graceful shutdown handling
- Log file management

**Usage**:
```bash
chmod +x start_background_monitoring.sh
./start_background_monitoring.sh
```

### 3. `daemon_monitoring.py` - Daemon Mode
**Best for**: System services, complete detachment

**Features**:
- Complete daemon process
- PID file management
- Separate stdout/stderr logs
- System service integration

**Usage**:
```bash
python3 daemon_monitoring.py
```

## ⚙️ Configuration Options

### Monitoring Intervals
- **Default**: 5 minutes between scans
- **Configurable**: Set in the script or via environment variables
- **Range**: 1-60 minutes recommended

### Maximum Attempts
- **Default**: 10 attempts (50 minutes total)
- **Unlimited**: Set to 0 for continuous monitoring
- **Custom**: Set any number of attempts

### Headless Mode
- **Always Enabled**: Background processes run headless
- **Chrome Options**: Optimized for server environments
- **Resource Usage**: Minimal CPU and memory usage

## 📊 Monitoring and Management

### Check Process Status
```bash
# Find the process
ps aux | grep run_background_env

# Check if it's running
pgrep -f run_background_env
```

### View Logs
```bash
# Real-time log monitoring
tail -f btc_background.log

# View specific log file
cat btc_background_env.log

# Search for specific events
grep "Found.*courts" btc_background.log
```

### Stop Background Process
```bash
# Graceful shutdown
pkill -f run_background_env

# Force stop
pkill -9 -f run_background_env

# Using PID
kill <PID_NUMBER>
```

## 📱 Notification Features

### Email Notifications
- **Multi-Date Support**: Courts organized by date
- **Rich Formatting**: Professional layout with emojis
- **Idempotency**: Prevents duplicate notifications
- **Gmail SMTP**: Secure authentication

### SMS Notifications
- **Canadian Carriers**: Rogers, Bell, Telus, Fido, Virgin, Koodo
- **Fallback Options**: Multiple gateway attempts
- **Concise Format**: Optimized for SMS limits

### Console Output
- **Real-time Logging**: All activities logged
- **Debug Information**: Screenshots and page sources saved
- **Error Handling**: Comprehensive error reporting

## 🔧 Advanced Configuration

### Custom Monitoring Intervals
Edit `run_background_env.py`:
```python
self.monitoring_interval = 10  # 10 minutes
self.max_attempts = 20         # 20 attempts
```

### Environment Variable Override
```bash
export BTC_MONITORING_INTERVAL="10"  # 10 minutes
export BTC_MAX_ATTEMPTS="20"         # 20 attempts
```

### Log Rotation
```bash
# Rotate logs daily
logrotate -f btc_bot_logrotate.conf
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Process Not Starting
**Symptoms**: No process found, immediate exit
**Solutions**:
- Check environment variables: `env | grep BTC`
- Verify Python dependencies: `pip3 install -r requirements.txt`
- Check Chrome installation: `google-chrome --version`

#### 2. Login Failures
**Symptoms**: "Login failed" in logs
**Solutions**:
- Verify BTC credentials
- Check website accessibility
- Update Chrome WebDriver

#### 3. No Courts Found
**Symptoms**: "No available courts found" repeatedly
**Solutions**:
- This is normal - courts are only available when someone cancels
- Check if the website interface has changed
- Review debug screenshots

#### 4. Memory Issues
**Symptoms**: High memory usage, crashes
**Solutions**:
- Restart the process periodically
- Check for memory leaks in logs
- Reduce monitoring frequency

### Debug Information

#### Log Files
- `btc_background.log` - Main output log
- `btc_background_env.log` - Detailed process log
- `btc_booking.log` - Bot-specific log

#### Debug Files
- `btc_booking_page_*.png` - Screenshots
- `btc_booking_page_*.html` - Page sources
- `available_courts_*.json` - Court data

#### Monitoring Commands
```bash
# Check process health
ps aux | grep run_background_env | grep -v grep

# Monitor resource usage
top -p $(pgrep -f run_background_env)

# Check log file size
ls -lh btc_background*.log
```

## 📈 Performance Optimization

### Resource Management
- **Memory**: Automatic cleanup of old notifications
- **CPU**: Optimized Chrome options for headless mode
- **Network**: Efficient page loading with disabled images/CSS

### Scaling
- **Multiple Instances**: Run multiple bots for different time slots
- **Load Balancing**: Distribute monitoring across different intervals
- **Monitoring**: Use system monitoring tools

## 🔒 Security Considerations

### Credential Management
- **Environment Variables**: Store credentials securely
- **File Permissions**: Restrict access to credential files
- **Network Security**: Use secure connections

### Process Security
- **User Isolation**: Run as non-root user
- **File System**: Use dedicated directories
- **Logging**: Secure log file storage

## 📋 Best Practices

### 1. Environment Setup
- Use dedicated user account
- Set up proper file permissions
- Configure log rotation
- Monitor system resources

### 2. Monitoring Strategy
- Start with 5-minute intervals
- Monitor during peak hours
- Adjust based on court availability patterns
- Use multiple time slots

### 3. Maintenance
- Regular log review
- Process health checks
- Credential updates
- System updates

### 4. Notification Management
- Test notifications regularly
- Monitor notification delivery
- Adjust notification frequency
- Backup notification methods

## 🎯 Use Cases

### 1. Personal Use
- **Home Server**: Run on Raspberry Pi or home server
- **Laptop**: Background monitoring while working
- **Mobile**: SSH access for monitoring

### 2. Professional Use
- **Tennis Clubs**: Monitor for members
- **Coaching**: Track availability for lessons
- **Tournaments**: Court availability tracking

### 3. Development
- **Testing**: Automated testing scenarios
- **Research**: Court availability patterns
- **Integration**: API development

## 📞 Support

### Getting Help
- Check logs first: `tail -f btc_background.log`
- Review this guide
- Check GitHub issues
- Contact support

### Contributing
- Submit bug reports
- Suggest improvements
- Contribute code
- Update documentation

---

**Happy Background Monitoring! 🎾**

*The bot will work tirelessly in the background to find you the perfect tennis court!*
