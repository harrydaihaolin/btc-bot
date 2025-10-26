#!/usr/bin/env python3
"""
Debug script for court detection
"""

import os
import sys
import time
import logging
from datetime import datetime
from core.config import BTCConfig
from core.monitor import CourtMonitor
from core.notifications import NotificationManager

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_court_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def debug_court_detection():
    """Debug court detection with detailed logging"""
    print("🔍 Starting debug court detection...")
    
    # Load configuration
    config_manager = BTCConfig()
    credentials = config_manager.get_credentials()
    config = config_manager.get_bot_config()
    
    print(f"✅ Credentials loaded: {credentials.get('username', 'Not set')}")
    
    # Initialize monitor
    monitor = CourtMonitor(config, credentials)
    
    try:
        # Setup driver
        print("🚀 Setting up WebDriver...")
        monitor.setup_driver()
        
        # Login
        print("🔐 Attempting login...")
        login_success = monitor.login()
        print(f"   Login result: {'SUCCESS' if login_success else 'FAILED'}")
        
        # Navigate to booking page
        print("🌐 Navigating to booking page...")
        nav_success = monitor.navigate_to_booking_page()
        print(f"   Navigation result: {'SUCCESS' if nav_success else 'FAILED'}")
        
        if nav_success:
            # Take screenshot for debugging
            screenshot_path = f"debug_booking_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            monitor.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Save page source for debugging
            page_source_path = f"debug_booking_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(page_source_path, 'w', encoding='utf-8') as f:
                f.write(monitor.driver.page_source)
            print(f"📄 Page source saved: {page_source_path}")
            
            # Try to detect courts on current page (without date navigation)
            print("🔍 Detecting courts on current page...")
            courts = monitor._detect_available_courts()
            print(f"   Courts found: {len(courts)}")
            
            if courts:
                print("🎾 Available courts:")
                for i, court in enumerate(courts, 1):
                    print(f"   {i}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}")
            else:
                print("❌ No courts detected on current page")
                
                # Debug: Look for any buttons on the page
                print("🔍 Debugging: Looking for all buttons on page...")
                all_buttons = monitor.driver.find_elements("tag name", "button")
                print(f"   Total buttons found: {len(all_buttons)}")
                
                # Look for buttons with "Book" text
                book_buttons = []
                for button in all_buttons:
                    try:
                        if 'book' in button.text.lower():
                            book_buttons.append(button)
                            print(f"   Found button with 'book': '{button.text}'")
                    except:
                        continue
                
                print(f"   Buttons with 'book' text: {len(book_buttons)}")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        logger.error(f"Debug error: {e}", exc_info=True)
    
    finally:
        if monitor.driver:
            monitor.cleanup()
            print("🧹 WebDriver cleaned up")

if __name__ == "__main__":
    debug_court_detection()
