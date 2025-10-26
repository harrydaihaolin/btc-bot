# 🎾 GitHub Gist Setup Guide

## How to Create a Shareable GitHub Gist

### Method 1: Manual Creation (Recommended)

1. **Go to GitHub Gists**: Visit [https://gist.github.com/](https://gist.github.com/)

2. **Sign in**: Use your GitHub account (harry442930583@gmail.com)

3. **Create New Gist**:
   - **Description**: `🎾 Burnaby Tennis Club Court Booking Bot - Automated tennis court booking with email/SMS notifications`
   - **Visibility**: Select "Public" to make it shareable

4. **Add Files**:
   - **Filename**: `btc_tennis_bot.py`
   - **Content**: Copy the entire content from `btc_tennis_bot.py`
   
   - **Filename**: `requirements.txt`
   - **Content**: Copy the content from `requirements.txt`
   
   - **Filename**: `setup_credentials.sh`
   - **Content**: Copy the content from `setup_credentials.sh`
   
   - **Filename**: `README.md`
   - **Content**: Copy the content from `README.md`

5. **Create Public Gist**: Click "Create public gist"

6. **Share**: Copy the Gist URL and share it!

### Method 2: Using the Python Script

1. **Install requests**: `pip3 install requests`

2. **Run the script**: `python3 create_gist.py`

3. **Follow the prompts** to enter your GitHub credentials

### Files to Include in Gist

- ✅ `btc_tennis_bot.py` - Main bot script
- ✅ `requirements.txt` - Python dependencies  
- ✅ `setup_credentials.sh` - Credential setup script
- ✅ `README.md` - Documentation

### Gist Description

```
🎾 Burnaby Tennis Club Court Booking Bot - Automated tennis court booking with email/SMS notifications

Features:
- Automatic login and navigation
- Real-time court availability detection  
- Email notifications via Gmail SMTP
- SMS notifications via email-to-SMS gateways
- Continuous monitoring options
- Environment variable support
- Interactive credential setup

Perfect for tennis players who want to be notified when courts become available!
```

### After Creating the Gist

1. **Copy the Gist URL** (e.g., `https://gist.github.com/username/gist-id`)
2. **Share the URL** with others
3. **Users can download** individual files or clone the entire gist
4. **Users can fork** the gist to create their own version

### Usage Instructions for Users

1. **Visit the Gist URL**
2. **Download all files** to a folder
3. **Run setup**: `chmod +x setup_credentials.sh && ./setup_credentials.sh`
4. **Install dependencies**: `pip3 install -r requirements.txt`
5. **Run the bot**: `python3 btc_tennis_bot.py`

---

**Your tennis bot will be shareable and ready for others to use! 🎾**
