#!/usr/bin/env python3
"""
BTC Tennis Club Notification Manager
Burnaby Tennis Club specific notification formatting
"""

import os
import sys
from typing import Dict, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.notifications.base_notifications import BaseNotificationManager
from btc.config.btc_config import BTCConfig


class BTCNotificationManager(BaseNotificationManager):
    """Notification manager for Burnaby Tennis Club court availability"""
    
    def __init__(self):
        config = BTCConfig()
        super().__init__(config)
    
    def _format_email_message(self, available_courts: Dict[str, List[Dict]]) -> str:
        """Format email message for BTC courts"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #2E8B57; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .court-item { background-color: #f0f8ff; margin: 10px 0; padding: 15px; border-left: 4px solid #2E8B57; }
                .court-name { font-weight: bold; color: #2E8B57; font-size: 16px; }
                .court-details { margin: 5px 0; }
                .price { color: #006600; font-weight: bold; }
                .footer { background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; }
                .book-link { background-color: #2E8B57; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎾 Burnaby Tennis Club Courts Available!</h1>
                <p>New tennis court bookings have been detected</p>
            </div>
            
            <div class="content">
        """
        
        total_courts = sum(len(courts) for courts in available_courts.values())
        html += f"<h2>Found {total_courts} available court(s):</h2>"
        
        for date, courts in available_courts.items():
            html += f"<h3>📅 {date}</h3>"
            
            for court in courts:
                html += f"""
                <div class="court-item">
                    <div class="court-name">🏟️ {court.get('court_name', 'Unknown Court')}</div>
                    <div class="court-details">⏰ Time: {court.get('time', 'Unknown')}</div>
                    <div class="court-details">⏱️ Duration: {court.get('duration', '1 hour')}</div>
                    <div class="court-details price">💰 Price: {court.get('price', 'Unknown')}</div>
                </div>
                """
        
        html += """
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://www.burnabytennis.ca/app/bookings/grid" class="book-link">
                        🎾 Book Now at Burnaby Tennis Club
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>This notification was sent by your Burnaby Tennis Club Monitor</p>
                <p>Burnaby Tennis Club - Court Booking System</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_sms_message(self, available_courts: Dict[str, List[Dict]]) -> str:
        """Format SMS message for BTC courts"""
        total_courts = sum(len(courts) for courts in available_courts.values())
        
        message = f"🎾 Burnaby Tennis Club: {total_courts} court(s) available!\n"
        
        for date, courts in available_courts.items():
            message += f"\n📅 {date}:\n"
            for court in courts:
                court_name = court.get('court_name', 'Unknown')
                time_slot = court.get('time', 'Unknown')
                price = court.get('price', 'Unknown')
                message += f"• {court_name} at {time_slot} ({price})\n"
        
        message += "\nBook now: https://www.burnabytennis.ca/app/bookings/grid"
        
        return message
