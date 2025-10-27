# 🎾 Tennis Court Booking Bot

[![CI Tests](https://github.com/username/btc-bot/workflows/CI%20Tests/badge.svg)](https://github.com/username/btc-bot/actions/workflows/ci.yml)
[![Security Scan](https://github.com/username/btc-bot/workflows/Security%20and%20Code%20Quality/badge.svg)](https://github.com/username/btc-bot/actions/workflows/security.yml)
[![Docker Build](https://github.com/username/btc-bot/workflows/Docker%20Build%20and%20Push/badge.svg)](https://github.com/username/btc-bot/actions/workflows/docker-release.yml)
[![Coverage](https://codecov.io/gh/username/btc-bot/branch/main/graph/badge.svg)](https://codecov.io/gh/username/btc-bot)

An automated bot that monitors tennis court booking systems and sends notifications when courts become available.

## 🏟️ Supported Facilities

### 🎾 Burnaby Tennis Club (BTC)
Monitors Burnaby Tennis Club's booking system for court availability.

### 🎓 UBC Tennis Centre
Monitors UBC Recreation's tennis court booking system for court availability.

## 🚀 Quick Start

### Docker Mode (Recommended for Production)
```bash
# One-command Docker experience
./scripts/docker-manage.sh start

# Check status
./scripts/docker-manage.sh status

# View logs
./scripts/docker-manage.sh logs

# Stop containers
./scripts/docker-manage.sh stop
```

### Daemon Mode (Local Development)
```bash
# One-command daemon experience
./scripts/run_daemon.sh

# Check status
./scripts/run_daemon.sh status

# Stop daemon
./scripts/run_daemon.sh stop
```

### GitHub Actions (Automated Monitoring)
```bash
# Set up GitHub Secrets for automated monitoring
# Go to Settings → Secrets and variables → Actions
# Add your credentials (see .github/README.md for details)

# Manual trigger
gh workflow run periodic-monitoring.yml
```

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

## 🐳 Docker Setup (Production Ready)

### Prerequisites
- Docker and Docker Compose installed
- Credentials configured in `.env` file

### 1. Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Start Both Bots
```bash
# Start BTC and UBC bots
./scripts/docker-manage.sh start

# Check status
./scripts/docker-manage.sh status

# View logs
./scripts/docker-manage.sh logs
```

### 3. Docker Management Commands
```bash
# Start bots
./scripts/docker-manage.sh start

# Stop bots
./scripts/docker-manage.sh stop

# Restart bots
./scripts/docker-manage.sh restart

# View logs
./scripts/docker-manage.sh logs          # Both bots
./scripts/docker-manage.sh logs btc      # BTC bot only
./scripts/docker-manage.sh logs ubc      # UBC bot only

# Check status
./scripts/docker-manage.sh status

# Rebuild containers
./scripts/docker-manage.sh build
```

### 4. Docker Features
- **Automatic Restart**: Containers restart automatically on failure
- **Health Checks**: Built-in health monitoring
- **Log Management**: Centralized logging with volume mounting
- **Security**: Non-root user execution
- **Resource Optimization**: Shared memory for Chrome performance

## 🔄 CI/CD & Automated Monitoring

### GitHub Actions Workflows

#### 1. Continuous Integration (`ci.yml`)
- **Triggers**: Push to main/develop, Pull Requests
- **Features**:
  - Unit tests with coverage reporting (84% overall coverage)
  - Docker image building and testing
  - Integration tests with Docker Compose
  - Code linting (Black, isort, flake8, mypy)
  - Coverage upload to Codecov

#### 2. Periodic Court Monitoring (`periodic-monitoring.yml`)
- **Schedule**: Every 2 hours (9 AM - 9 PM PST)
- **Features**:
  - Automated court monitoring using Docker containers
  - Health checks for both BTC and UBC bots
  - Log artifact upload for debugging
  - Manual trigger support

#### 3. Docker Release (`docker-release.yml`)
- **Triggers**: Version tags, Manual dispatch
- **Features**:
  - Multi-platform Docker builds
  - Automated Docker Hub publishing
  - GitHub Release creation
  - Docker layer caching

#### 4. Security Scanning (`security.yml`)
- **Schedule**: Weekly + Push/PR triggers
- **Features**:
  - Trivy vulnerability scanning
  - Bandit security linting
  - Dependency vulnerability checks
  - Code quality analysis

### Setup Automated Monitoring

1. **Configure GitHub Secrets**:
   ```
   Settings → Secrets and variables → Actions
   Add: BTC_USERNAME, BTC_PASSWORD, BTC_NOTIFICATION_EMAIL, etc.
   ```

2. **Enable Workflows**:
   ```bash
   # Workflows are automatically enabled when pushed to GitHub
   git push origin main
   ```

3. **Monitor Status**:
   - Go to Actions tab in GitHub repository
   - View workflow runs and logs
   - Download monitoring artifacts

### Manual Triggers

```bash
# Trigger periodic monitoring
gh workflow run periodic-monitoring.yml

# Trigger security scan
gh workflow run security.yml

# Create new release
git tag v1.4.0
git push origin v1.4.0
```

## 🎾 Burnaby Tennis Club (BTC) Setup

### 2. Set Up BTC Credentials
```bash
# Option A: Interactive setup
./scripts/setup_credentials.sh

# Option B: Manual environment variables
export BTC_USERNAME="your_email@example.com"
export BTC_PASSWORD="your_password"
export BTC_NOTIFICATION_EMAIL="your_email@example.com"
export BTC_PHONE_NUMBER="1234567890"
export BTC_GMAIL_APP_EMAIL="your_gmail@gmail.com"
export BTC_GMAIL_APP_PASSWORD="your_gmail_app_password"
```

### 3. Start BTC Daemon Monitoring (RECOMMENDED)
```bash
# One-command daemon startup (default: 60 minutes)
./scripts/run_daemon.sh

# Custom interval (e.g., 30 minutes)
./scripts/run_daemon.sh 30
```

### 4. BTC Alternative Modes
```bash
# Interactive mode (for testing)
python3 btc_tennis_bot.py

# Monitor logs in real-time
tail -f btc_daemon.log

# Stop daemon when needed
kill $(cat btc_daemon.pid)
```

## 🎓 UBC Tennis Centre Setup

### 2. Set Up UBC Credentials
```bash
# Interactive setup for UBC credentials
python3 scripts/setup_ubc_credentials.py

# Manual environment variables (UBC-specific)
export UBC_USERNAME="your_ubc_cwl@ubc.ca"
export UBC_PASSWORD="your_ubc_password"
export UBC_NOTIFICATION_EMAIL="your_email@gmail.com"
export UBC_GMAIL_APP_PASSWORD="your_gmail_app_password"
export UBC_SMS_PHONE="1234567890"  # optional

# OR use BTC credentials for testing (fallback)
# If UBC credentials are not set, UBC monitoring will use BTC credentials
```

### 3. Start UBC Daemon Monitoring
```bash
# One-command UBC daemon startup (default: 5 minutes)
./run_ubc_daemon.sh

# Custom interval (e.g., 10 minutes)
./run_ubc_daemon.sh 10
```

### 4. UBC Alternative Modes
```bash
# Test UBC configuration
python3 test_ubc_monitor.py

# Monitor UBC logs in real-time
tail -f ubc_daemon.log

# Stop UBC daemon when needed
kill $(cat ubc_daemon.pid)
```

## 🎯 Key Features

### 🚨 **Instant Notifications**
- **Immediate Email Alerts**: Get notified the moment new courts become available
- **SMS Notifications**: Urgent alerts sent to your phone
- **New Booking Detection**: Monitors for court releases and cancellations
- **24/7 Monitoring**: Continuous background monitoring without interruption

### 🎾 **Smart Court Detection**
- **Multi-Date Scanning**: Automatically checks today, tomorrow, and day after tomorrow
- **Smart Detection**: Finds "Book" buttons and filters out false positives
- **Real-time Updates**: Detects new court availability as it happens
- **Comprehensive Coverage**: Monitors all available time slots

### 🖥️ **Background Processing**
- **Daemon Mode**: Runs completely detached from terminal
- **Production Ready**: Perfect for servers and automated deployments
- **Process Management**: PID files and graceful shutdown handling
- **Resource Efficient**: Minimal CPU and memory usage

### 🏗️ **Modular Architecture (v1.2)**
- **Core Modules**: Separated into `core/config.py`, `core/monitor.py`, `core/notifications.py`
- **Clean Integration**: Daemon and interactive modes share the same core components
- **Easy Extension**: Add new features by extending core modules
- **Better Testing**: Individual components can be tested independently
- **Maintainable Code**: Clear separation of concerns and responsibilities

### 🎓 **UBC Tennis Centre Support (v1.3)**
- **UBC-Specific Monitoring**: Dedicated UBC court booking system integration
- **CWL Login Support**: Compatible with UBC Campus Wide Login system
- **24-Hour Advance Booking**: Monitors UBC's 24-hour advance booking window
- **UBC-Specific Notifications**: Tailored email/SMS formatting for UBC courts
- **Facility-Specific Configuration**: Separate configs for BTC and UBC monitoring
- **Multi-Facility Support**: Monitor both BTC and UBC simultaneously
- **Credential Fallback**: Uses BTC credentials for UBC testing if UBC credentials not set

## 📱 Usage Modes

### 🚀 **Daemon Mode (RECOMMENDED)**
Perfect for continuous monitoring and instant notifications:
```bash
# One-command daemon startup (default: 60 minutes)
./scripts/run_daemon.sh

# Custom interval (e.g., 30 minutes)
./scripts/run_daemon.sh 30

# Monitor logs in real-time
tail -f btc_daemon.log

# Stop daemon when needed
kill $(cat btc_daemon.pid)
```
**Features:**
- ✅ **One-Command Setup**: Simple `./scripts/run_daemon.sh` to start
- ✅ **Configurable Intervals**: Set custom monitoring intervals
- ✅ **Instant Notifications**: Immediate email/SMS when new courts appear
- ✅ **24/7 Monitoring**: Runs completely detached from terminal
- ✅ **New Booking Detection**: Monitors for court releases and cancellations
- ✅ **Process Management**: PID files and graceful shutdown
- ✅ **Comprehensive Logging**: Detailed logs for debugging

### 🖥️ **Background Mode**
Simple background monitoring for basic use:
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

### 🎮 **Interactive Mode**
Perfect for testing and manual use:
```bash
python3 btc_tennis_bot.py
```
- Prompts for credentials if not set
- Shows real-time progress
- Offers monitoring options after initial scan

### Process Management
```bash
# Check daemon status
ps aux | grep daemon_monitoring

# View daemon logs
tail -f btc_daemon_monitoring.log

# Stop daemon
kill $(cat btc_daemon_*.pid)

# Check background process
ps aux | grep run_background_env

# View background logs
tail -f btc_background.log

# Stop background process
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

## 🖥️ Daemon Monitoring (DEFAULT)

### Why Daemon Mode?
The daemon mode is the **recommended default** because it provides:
- **🚨 Instant Notifications**: Get notified immediately when new courts become available
- **📧 Email Alerts**: Receive detailed email notifications with court information
- **📱 SMS Alerts**: Get urgent SMS notifications for time-sensitive bookings
- **🔄 Continuous Monitoring**: 24/7 background monitoring without interruption
- **🎯 New Booking Detection**: Monitors for court releases and cancellations in real-time

### Available Scripts
- **`daemon_monitoring.py`** - **RECOMMENDED**: Full daemon mode with instant notifications
- **`run_background_env.py`** - Simple background mode for basic monitoring
- **`start_background_monitoring.sh`** - Interactive startup script

### Daemon Configuration
- **Monitoring Interval**: 5 minutes (configurable)
- **Max Attempts**: Unlimited (runs continuously)
- **Headless Mode**: Always enabled for background operation
- **New Court Detection**: Compares with previous scans to detect new availability
- **Instant Notifications**: Sends alerts immediately when new courts are found

### Daemon Commands
```bash
# Start daemon monitoring (RECOMMENDED)
python3 daemon_monitoring.py

# Check daemon status
ps aux | grep daemon_monitoring

# View daemon logs
tail -f btc_daemon_monitoring.log

# Stop daemon
kill $(cat btc_daemon_*.pid)

# Alternative: Simple background monitoring
nohup python3 run_background_env.py > btc_background.log 2>&1 &
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

### Daemon Mode (RECOMMENDED)
```
🎾 BTC Tennis Bot - Daemon Monitoring Mode (DEFAULT)
======================================================================
This is the RECOMMENDED mode for continuous court monitoring
Features:
  ✅ Immediate email notifications when new courts become available
  ✅ SMS alerts for urgent court releases
  ✅ 24/7 background monitoring
  ✅ Detects new bookings as they're released
  ✅ Runs completely detached from terminal
======================================================================

🚀 Starting daemon process...
   PID file: btc_daemon_20251025_220000.pid
   Log file: btc_daemon_monitoring.log
   Monitoring interval: 5 minutes
   Max attempts: Unlimited

💡 To stop the daemon: kill $(cat btc_daemon_20251025_220000.pid)
💡 To view logs: tail -f btc_daemon_monitoring.log

🎾 Daemon is now monitoring for new court availability!

[Background monitoring starts...]

🎾 NEW COURTS DETECTED! 3 new slots found!
Sending immediate notifications...
   📅 Tomorrow, October 26, 2025: 2 courts
      1. Book 4:00 pm as 48hr
      2. Book 6:00 pm as 48hr
   📅 Day after tomorrow, October 27, 2025: 1 court
      1. Book 2:00 pm as 48hr
```

### Interactive Mode
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

### v1.3.0 - UBC Tennis Centre Support
- **Multi-Facility Support**: Added UBC Tennis Centre monitoring alongside BTC
- **UBC-Specific Modules**: Created dedicated UBC config, monitor, and notification modules
- **CWL Login Integration**: Compatible with UBC Campus Wide Login system
- **24-Hour Advance Booking**: Monitors UBC's unique booking window system
- **Facility-Specific Configuration**: Separate environment variables for BTC and UBC
- **UBC Daemon Monitoring**: Dedicated daemon script for UBC court monitoring
- **Interactive UBC Setup**: Easy credential setup script for UBC users
- **Comprehensive UBC Testing**: Test suite for UBC monitoring functionality

### v1.2.4 - Comprehensive Test Suite
- **84% Code Coverage**: Excellent production-level test coverage
- **111 Unit Tests**: Comprehensive testing of all core functionality
- **Realistic Expectations**: 80% coverage threshold (industry standard)
- **Fast Test Execution**: ~34 seconds for full test suite
- **Production Ready**: Robust testing ensures reliability

### v1.2.3 - One-Command Daemon Experience
- **Simplified Startup**: Single command `./scripts/run_daemon.sh` to start daemon monitoring
- **Configurable Intervals**: Easy custom monitoring intervals (e.g., `./scripts/run_daemon.sh 30`)
- **User-Friendly**: Streamlined experience with clear status messages
- **Better Documentation**: Updated README with simple one-command instructions
- **Production Ready**: Perfect for users who want immediate daemon functionality

### v1.2.2 - Daemon Monitoring & Process Management
- **Process Management**: Added start_daemon.sh and stop_daemon.sh scripts
- **Easy Startup**: One-command daemon startup with proper input handling
- **PID Tracking**: Process management with PID file tracking
- **Production Ready**: 24/7 background monitoring with 5-minute intervals
- **User Experience**: Simple commands for monitoring and process control

### v1.2.1 - Critical Court Detection Fix
- **Bug Fix**: Fixed court detection in background monitoring mode
- **Fallback Mechanism**: Added fallback to current page scan when date navigation fails
- **E2E Verified**: Confirmed working with real credentials and notifications
- **Reliability**: Ensures courts are detected regardless of website interface changes
- **Production Ready**: Background monitoring now fully operational

### v1.2.0 - Modular Architecture & Enhanced Integration
- **Modular Design**: Completely refactored into reusable core modules
- **Core Components**: Separate modules for configuration, monitoring, and notifications
- **Better Integration**: Clean separation between daemon and interactive modes
- **Improved Maintainability**: Easier to extend and modify individual components
- **Enhanced Error Handling**: Better error management across all modules
- **Code Reusability**: Shared components between different execution modes

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

## 🏗️ Project Structure

```
btc-bot/
├── core/                           # 🏗️ Core modular components
│   ├── __init__.py                 # Core module initialization
│   ├── config.py                   # Configuration management
│   ├── monitor.py                  # Court monitoring functionality
│   └── notifications.py            # Email and SMS notifications
├── btc_tennis_bot.py              # 🎮 Interactive mode (main bot)
├── daemon_monitoring.py           # 🚀 Daemon mode (recommended)
├── run_background_env.py          # 🖥️ Simple background mode
├── start_background_monitoring.sh # 🚀 Interactive startup script
├── setup_credentials.sh           # 🔧 Credential setup helper
├── requirements.txt               # 📦 Python dependencies
├── .gitignore                     # 🚫 Git ignore rules
└── README.md                      # 📚 This file
```

### Core Modules
- **`core/config.py`**: Handles environment variables and configuration
- **`core/monitor.py`**: WebDriver management, login, and court detection
- **`core/notifications.py`**: Email and SMS notification system

## 🧪 Testing

The project includes a comprehensive test suite with **84% code coverage** - an excellent level for production applications.

### Running Tests
```bash
# Run all tests
python3 run_tests.py

# Run specific test modules
python3 -m pytest tests/unit/test_config.py -v
python3 -m pytest tests/unit/test_monitor.py -v
python3 -m pytest tests/unit/test_notifications.py -v

# Run with coverage report
python3 -m pytest --cov=./core --cov-report=term-missing tests/unit/
```

### Test Coverage
- **Core Modules**: 84% coverage (459/546 statements)
- **111 unit tests** covering all critical functionality
- **Comprehensive edge case testing**
- **Proper mocking** for external dependencies

### Coverage Breakdown
- **`core/config.py`**: 100% coverage ✅
- **`core/notifications.py`**: 98% coverage ✅  
- **`core/monitor.py`**: 75% coverage ✅
- **Main scripts**: 78-91% coverage ✅

The missing 16% consists mainly of:
- Edge cases in Selenium WebDriver interactions
- Error handling paths difficult to trigger in tests
- Complex date navigation logic

This level of coverage ensures production reliability while maintaining realistic expectations for real-world applications.

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the bot!

## 📄 License

This project is for personal use. Please respect the Burnaby Tennis Club's terms of service.

---

**Happy Tennis Booking! 🎾**