# 🔐 GitHub Actions Credential Setup Guide

## Overview
This guide shows you how to securely store and use your tennis court booking credentials in GitHub Actions for automated monitoring.

## 🚨 Security Best Practices

### ✅ DO:
- Use GitHub Secrets for all sensitive data
- Use environment-specific secrets
- Rotate credentials regularly
- Use least-privilege access
- Monitor secret usage

### ❌ DON'T:
- Store credentials in code or config files
- Use the same credentials across environments
- Share secrets in logs or outputs
- Use weak or default passwords

## 🔧 Setup Methods

### Method 1: GitHub Repository Secrets (Recommended)

#### Step 1: Navigate to Repository Settings
1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**

#### Step 2: Add Required Secrets
Click **New repository secret** for each credential:

```
Name: BTC_USERNAME
Value: your_btc_email@example.com

Name: BTC_PASSWORD  
Value: your_btc_password

Name: BTC_NOTIFICATION_EMAIL
Value: your_notification_email@gmail.com

Name: BTC_GMAIL_APP_PASSWORD
Value: your_gmail_app_password

Name: BTC_SMS_PHONE
Value: +1234567890

Name: UBC_USERNAME
Value: your_ubc_email@ubc.ca

Name: UBC_PASSWORD
Value: your_ubc_password

Name: UBC_NOTIFICATION_EMAIL
Value: your_notification_email@gmail.com

Name: UBC_GMAIL_APP_PASSWORD
Value: your_gmail_app_password

Name: UBC_SMS_PHONE
Value: +1234567890

Name: TWILIO_SID
Value: your_twilio_sid

Name: TWILIO_TOKEN
Value: your_twilio_token

Name: TWILIO_PHONE
Value: +1234567890
```

#### Step 3: Verify Secrets
```bash
# Check if secrets are properly set (won't show values)
gh secret list
```

### Method 2: GitHub CLI Setup

#### Install GitHub CLI
```bash
# macOS
brew install gh

# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/github-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/github-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Windows
winget install GitHub.cli
```

#### Authenticate and Set Secrets
```bash
# Login to GitHub
gh auth login

# Set secrets via CLI
gh secret set BTC_USERNAME --body "your_btc_email@example.com"
gh secret set BTC_PASSWORD --body "your_btc_password"
gh secret set BTC_NOTIFICATION_EMAIL --body "your_notification_email@gmail.com"
gh secret set BTC_GMAIL_APP_PASSWORD --body "your_gmail_app_password"
gh secret set BTC_SMS_PHONE --body "+1234567890"

# UBC credentials
gh secret set UBC_USERNAME --body "your_ubc_email@ubc.ca"
gh secret set UBC_PASSWORD --body "your_ubc_password"
gh secret set UBC_NOTIFICATION_EMAIL --body "your_notification_email@gmail.com"
gh secret set UBC_GMAIL_APP_PASSWORD --body "your_gmail_app_password"
gh secret set UBC_SMS_PHONE --body "+1234567890"

# Twilio credentials
gh secret set TWILIO_SID --body "your_twilio_sid"
gh secret set TWILIO_TOKEN --body "your_twilio_token"
gh secret set TWILIO_PHONE --body "+1234567890"
```

### Method 3: Environment-Specific Secrets

#### For Different Environments
```bash
# Development environment
gh secret set BTC_USERNAME --env dev --body "dev_btc_email@example.com"

# Production environment  
gh secret set BTC_USERNAME --env prod --body "prod_btc_email@example.com"

# Staging environment
gh secret set BTC_USERNAME --env staging --body "staging_btc_email@example.com"
```

## 🧪 Testing Credential Setup

### Test GitHub Actions Workflow
```bash
# Trigger the periodic monitoring workflow manually
gh workflow run periodic-monitoring.yml

# Check workflow status
gh run list --workflow=periodic-monitoring.yml

# View workflow logs
gh run view <run-id> --log
```

### Test Locally with Docker
```bash
# Create test environment file
cp env.example .env.test

# Add your credentials to .env.test
echo "BTC_USERNAME=your_btc_email@example.com" >> .env.test
echo "BTC_PASSWORD=your_btc_password" >> .env.test
# ... add other credentials

# Test with Docker Compose
docker-compose --env-file .env.test up -d
docker-compose --env-file .env.test logs -f
docker-compose --env-file .env.test down
```

## 🔍 Monitoring and Debugging

### Check Secret Usage
```bash
# List all secrets (names only)
gh secret list

# Check if specific secret exists
gh secret get BTC_USERNAME
```

### Debug Workflow Issues
1. **Check GitHub Actions logs**:
   - Go to Actions tab in repository
   - Click on failed workflow run
   - Review step-by-step logs

2. **Common Issues**:
   - Missing secrets: Add required secrets
   - Wrong secret names: Check workflow file for exact names
   - Invalid credentials: Verify credentials work locally

3. **Test Individual Components**:
   ```bash
   # Test BTC bot
   python3 -c "
   from btc.config.btc_config import BTCConfig
   config = BTCConfig()
   print('BTC config loaded successfully')
   "
   
   # Test UBC bot
   python3 -c "
   from ubc.config.ubc_config import UBCConfig
   config = UBCConfig()
   print('UBC config loaded successfully')
   "
   ```

## 🛡️ Security Considerations

### Credential Rotation
```bash
# Rotate credentials regularly
gh secret set BTC_PASSWORD --body "new_password"
gh secret set BTC_GMAIL_APP_PASSWORD --body "new_app_password"
```

### Access Control
- Use repository-level secrets for single-repo access
- Use organization-level secrets for multiple repos
- Use environment-specific secrets for different stages

### Monitoring
- Enable audit logs in GitHub
- Monitor secret usage in Actions
- Set up alerts for failed authentication attempts

## 📋 Checklist

### Before Setting Up:
- [ ] Have valid tennis club credentials
- [ ] Have Gmail app password for notifications
- [ ] Have Twilio credentials (optional)
- [ ] Have GitHub CLI installed (optional)

### After Setting Up:
- [ ] All required secrets are set
- [ ] Periodic monitoring workflow runs successfully
- [ ] No credential errors in logs
- [ ] Notifications are received
- [ ] Health checks pass

### Ongoing Maintenance:
- [ ] Rotate credentials every 90 days
- [ ] Monitor workflow runs regularly
- [ ] Update secrets when credentials change
- [ ] Review security logs monthly

## 🆘 Troubleshooting

### Common Error Messages:
```
Error: BTC_USERNAME not found
Solution: Add BTC_USERNAME secret to repository

Error: Invalid credentials
Solution: Verify credentials work locally first

Error: Gmail authentication failed
Solution: Check Gmail app password is correct
```

### Getting Help:
1. Check GitHub Actions documentation
2. Review workflow logs for specific errors
3. Test credentials locally first
4. Contact support if issues persist

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review GitHub Actions logs
3. Test credentials locally
4. Create an issue in the repository with:
   - Error message
   - Workflow logs (without sensitive data)
   - Steps to reproduce
