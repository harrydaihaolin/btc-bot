# 🎾 Tennis Court Booking Bot

An automated bot that monitors tennis court booking systems and sends email notifications when courts become available.

## 🏟️ Supported Facilities

- **🎾 Burnaby Tennis Club (BTC)** - Monitors BTC's booking system
- **🎓 UBC Tennis Centre** - Monitors UBC Recreation's tennis courts

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Set Up Credentials
```bash
# Set up BTC credentials
./scripts/setup_credentials.sh

# Set up UBC credentials (optional - will fallback to BTC if not set)
python3 scripts/setup_ubc_credentials.py
```

### 3. Start Monitoring

#### Option A: Local Daemon (Recommended)
```bash
# One-command daemon experience
./scripts/run_daemon.sh

# Check status
./scripts/run_daemon.sh status

# Stop daemon
./scripts/run_daemon.sh stop
```

#### Option B: Docker (Alternative)
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

## 🔧 Configuration

### Environment Variables
Create a `.env` file with your credentials:

```bash
# BTC Tennis Club Credentials
BTC_USERNAME=your_btc_email@example.com
BTC_PASSWORD=your_btc_password
BTC_NOTIFICATION_EMAIL=your_notification_email@gmail.com
BTC_GMAIL_APP_PASSWORD=your_gmail_app_password
BTC_RECIPIENT_EMAILS=user1@example.com,user2@example.com,user3@example.com

# UBC Tennis Centre Credentials (optional)
UBC_USERNAME=your_ubc_email@ubc.ca
UBC_PASSWORD=your_ubc_password
UBC_NOTIFICATION_EMAIL=your_notification_email@gmail.com
UBC_GMAIL_APP_PASSWORD=your_gmail_app_password
UBC_RECIPIENT_EMAILS=user1@example.com,user2@example.com,user3@example.com

# Monitoring Settings
BTC_MONITORING_INTERVAL=60  # minutes
UBC_MONITORING_INTERVAL=60  # minutes
```

### Gmail App Password
To send email notifications, you need a Gmail App Password:
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password for "Mail"
3. Use this password in `BTC_GMAIL_APP_PASSWORD` and `UBC_GMAIL_APP_PASSWORD`

## 📋 Features

- **Multi-Facility Support**: Monitor both BTC and UBC tennis courts
- **Email Notifications**: Get instant alerts when courts become available
- **Multi-Date Scanning**: Checks today, tomorrow, and day after tomorrow
- **Idempotency**: Prevents duplicate notifications
- **Docker Support**: Easy containerized deployment
- **Daemon Mode**: Background monitoring with process management
- **Configurable Intervals**: Custom monitoring frequencies

## 🛠️ Management Commands

### Docker Management
```bash
./scripts/docker-manage.sh start     # Start both bots
./scripts/docker-manage.sh stop      # Stop both bots
./scripts/docker-manage.sh restart   # Restart both bots
./scripts/docker-manage.sh logs      # View logs
./scripts/docker-manage.sh status    # Check status
./scripts/docker-manage.sh build     # Rebuild containers
```

### Daemon Management
```bash
./scripts/run_daemon.sh              # Start daemon monitoring
./scripts/run_daemon.sh 30           # Start with 30-minute intervals
./scripts/run_daemon.sh status       # Check daemon status
./scripts/run_daemon.sh stop         # Stop daemon
```

## 📁 Project Structure

```
btc-bot/
├── btc/                    # BTC-specific modules
│   ├── config/            # BTC configuration
│   ├── monitor/           # BTC monitoring logic
│   └── notifications/     # BTC notification formatting
├── ubc/                   # UBC-specific modules
│   ├── config/            # UBC configuration
│   ├── monitor/           # UBC monitoring logic
│   └── notifications/     # UBC notification formatting
├── common/                # Shared modules
│   ├── config/            # Base configuration classes
│   ├── monitor/           # Base monitoring classes
│   └── notifications/     # Base notification classes
├── scripts/               # Utility scripts
│   ├── docker-manage.sh   # Docker management
│   ├── run_daemon.sh      # Daemon management
│   ├── setup_credentials.sh # Credential setup
│   └── setup_ubc_credentials.py # UBC credential setup
├── tests/                 # Unit tests
├── btc_bot.py            # BTC bot entry point
├── ubc_bot.py            # UBC bot entry point
├── docker-compose.yml    # Docker Compose configuration
└── requirements.txt      # Python dependencies
```

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest

# Run with coverage
python3 -m pytest --cov=btc --cov=ubc --cov=common

# Test modular structure
python3 scripts/test_modular_structure.py
```

## 🔄 Automated Monitoring (GitHub Actions)

The bot can run automatically in GitHub Actions for continuous monitoring:

### Setup GitHub Secrets
1. Go to your repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `BTC_USERNAME` - Your BTC login email
   - `BTC_PASSWORD` - Your BTC password
   - `BTC_NOTIFICATION_EMAIL` - Email to send notifications from
   - `BTC_GMAIL_APP_PASSWORD` - Gmail App Password
   - `BTC_RECIPIENT_EMAILS` - Comma-separated list of emails to notify (e.g., "user1@example.com,user2@example.com")
   - `UBC_USERNAME` - Your UBC login email (optional)
   - `UBC_PASSWORD` - Your UBC password (optional)
   - `UBC_NOTIFICATION_EMAIL` - Email to send UBC notifications from (optional)
   - `UBC_GMAIL_APP_PASSWORD` - Gmail App Password for UBC (optional)
   - `UBC_RECIPIENT_EMAILS` - Comma-separated list of emails for UBC notifications (optional)

### Manual Trigger
```bash
# Trigger monitoring manually
gh workflow run periodic-monitoring.yml
```

### Schedule
- **Automatic**: Runs every hour from 9 AM to 9 PM PST
- **Manual**: Can be triggered anytime via GitHub CLI or web interface

## 📝 Version History

- **v1.3.1** - UBC Tennis Centre Support with credential fallback
- **v1.3.0** - UBC Tennis Centre Support
- **v1.2.4** - Comprehensive Test Suite (84% coverage)
- **v1.2.3** - One-Command Daemon Experience
- **v1.2.2** - Daemon Monitoring & Process Management
- **v1.2.1** - Critical Court Detection Fix
- **v1.2.0** - Modular Architecture & Enhanced Integration
- **v1.1.0** - Multi-Date Scanning & Interactive Background Monitoring
- **v1.0.0** - Initial Release

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python3 -m pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**WebDriver Issues**: Make sure Chrome is installed and up to date
```bash
# On macOS
brew install --cask google-chrome

# On Ubuntu
sudo apt-get install google-chrome-stable
```

**Permission Issues**: Make sure scripts are executable
```bash
chmod +x scripts/*.sh
```

**Email Notifications Not Working**: Verify Gmail App Password is correct and 2FA is enabled

**Docker Issues**: Make sure Docker and Docker Compose are installed and running (if using Docker option)

### Getting Help

- Check daemon logs: `tail -f btc_daemon.log` or `tail -f ubc_daemon.log`
- Check daemon status: `ps aux | grep btc_bot.py` or `ps aux | grep ubc_bot.py`
- Run tests to verify setup: `python3 scripts/test_modular_structure.py`
- Check environment variables: `env | grep BTC` or `env | grep UBC`