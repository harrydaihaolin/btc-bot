#!/usr/bin/env python3
"""
Script to create a GitHub Gist with the BTC Tennis Bot files
"""

import os
import json
import requests
from getpass import getpass

def create_gist():
    """Create a GitHub Gist with the tennis bot files"""
    
    print("🎾 Creating GitHub Gist for BTC Tennis Bot")
    print("=" * 50)
    
    # Get GitHub credentials
    username = input("GitHub Username: ").strip()
    password = getpass("GitHub Password (or Personal Access Token): ")
    
    # Prepare files for the gist
    files = {}
    
    # Read the main bot file
    try:
        with open('btc_tennis_bot.py', 'r', encoding='utf-8') as f:
            files['btc_tennis_bot.py'] = {'content': f.read()}
    except FileNotFoundError:
        print("❌ btc_tennis_bot.py not found in current directory")
        return
    
    # Read requirements.txt
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            files['requirements.txt'] = {'content': f.read()}
    except FileNotFoundError:
        print("❌ requirements.txt not found in current directory")
        return
    
    # Read setup script
    try:
        with open('setup_credentials.sh', 'r', encoding='utf-8') as f:
            files['setup_credentials.sh'] = {'content': f.read()}
    except FileNotFoundError:
        print("❌ setup_credentials.sh not found in current directory")
        return
    
    # Read README
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            files['README.md'] = {'content': f.read()}
    except FileNotFoundError:
        print("❌ README.md not found in current directory")
        return
    
    # Create gist data
    gist_data = {
        "description": "🎾 Burnaby Tennis Club Court Booking Bot - Automated tennis court booking with email/SMS notifications",
        "public": True,
        "files": files
    }
    
    # Create the gist
    try:
        print("📤 Creating GitHub Gist...")
        
        response = requests.post(
            'https://api.github.com/gists',
            auth=(username, password),
            headers={'Accept': 'application/vnd.github.v3+json'},
            data=json.dumps(gist_data)
        )
        
        if response.status_code == 201:
            gist_info = response.json()
            gist_url = gist_info['html_url']
            gist_id = gist_info['id']
            
            print("✅ Gist created successfully!")
            print(f"🔗 Gist URL: {gist_url}")
            print(f"🆔 Gist ID: {gist_id}")
            print(f"📁 Files included: {', '.join(files.keys())}")
            
            # Save the URL for reference
            with open('gist_url.txt', 'w') as f:
                f.write(f"Gist URL: {gist_url}\n")
                f.write(f"Gist ID: {gist_id}\n")
            
            print(f"\n💾 Gist details saved to gist_url.txt")
            print("\n🎾 Your tennis bot is now shareable!")
            
        else:
            print(f"❌ Failed to create gist: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating gist: {e}")

if __name__ == "__main__":
    create_gist()
