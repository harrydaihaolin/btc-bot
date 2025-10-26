#!/usr/bin/env python3
"""
UBC Tennis Court Notification Manager
Handles notifications for UBC tennis court availability
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from twilio.rest import Client

from .ubc_config import UBCConfig


class UBCNotificationManager:
    """Notification manager for UBC tennis court availability"""

    def __init__(self):
        self.config = UBCConfig()
        self.notification_config = self.config.get_notification_config()
        self.logger = self._setup_logger()
        self.sent_notifications: set = set()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for UBC notifications"""
        logger = logging.getLogger("ubc_notifications")
        logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        # Add handler
        logger.addHandler(console_handler)

        return logger

    def send_notifications(self, available_courts: Dict[str, List[Dict]]) -> bool:
        """Send notifications for available UBC courts"""
        try:
            if not available_courts:
                self.logger.info("No courts to notify about")
                return True

            total_courts = sum(len(courts) for courts in available_courts.values())
            self.logger.info(
                f"Sending notifications for {total_courts} available UBC courts"
            )

            # Send email notification
            email_sent = self._send_email_notification(available_courts)

            # Send SMS notification
            sms_sent = self._send_sms_notification(available_courts)

            return email_sent and sms_sent

        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")
            return False

    def _send_email_notification(self, available_courts: Dict[str, List[Dict]]) -> bool:
        """Send email notification for UBC courts"""
        try:
            email = self.notification_config.get("email")
            gmail_password = self.notification_config.get("gmail_app_password")

            if not email or not gmail_password:
                self.logger.warning(
                    "Email credentials not configured, skipping email notification"
                )
                return True

            # Create message
            subject = "🎾 UBC Tennis Courts Available!"
            body = self._format_email_message(available_courts)

            # Create email
            msg = MIMEMultipart()
            msg["From"] = email
            msg["To"] = email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "html"))

            # Send email
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(email, gmail_password)
            text = msg.as_string()
            server.sendmail(email, email, text)
            server.quit()

            self.logger.info("UBC email notification sent successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Error sending UBC email notification: {e}")
            return False

    def _send_sms_notification(self, available_courts: Dict[str, List[Dict]]) -> bool:
        """Send SMS notification for UBC courts"""
        try:
            phone = self.notification_config.get("sms_phone")
            twilio_sid = self.notification_config.get("twilio_sid")
            twilio_token = self.notification_config.get("twilio_token")
            twilio_phone = self.notification_config.get("twilio_phone")

            if not all([phone, twilio_sid, twilio_token, twilio_phone]):
                self.logger.warning(
                    "SMS credentials not configured, skipping SMS notification"
                )
                return True

            # Create message
            message = self._format_sms_message(available_courts)

            # Create unique key for this notification
            notification_key = self._create_notification_key(available_courts)

            if notification_key in self.sent_notifications:
                self.logger.info(
                    "SMS notification already sent for this court combination"
                )
                return True

            # Send SMS
            client = Client(twilio_sid, twilio_token)
            message_obj = client.messages.create(
                body=message, from_=twilio_phone, to=phone
            )

            self.sent_notifications.add(notification_key)
            self.logger.info(
                f"UBC SMS notification sent successfully! SID: {message_obj.sid}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error sending UBC SMS notification: {e}")
            return False

    def _format_email_message(self, available_courts: Dict[str, List[Dict]]) -> str:
        """Format email message for UBC courts"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #003366; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .court-item { background-color: #f0f8ff; margin: 10px 0; padding: 15px; border-left: 4px solid #003366; }
                .court-name { font-weight: bold; color: #003366; font-size: 16px; }
                .court-details { margin: 5px 0; }
                .price { color: #006600; font-weight: bold; }
                .footer { background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; }
                .book-link { background-color: #003366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎾 UBC Tennis Courts Available!</h1>
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
                    <a href="https://recreation.ubc.ca/tennis/court-booking/" class="book-link">
                        🎾 Book Now at UBC Tennis Centre
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>This notification was sent by your UBC Tennis Court Monitor</p>
                <p>UBC Recreation - Tennis Centre</p>
            </div>
        </body>
        </html>
        """

        return html

    def _format_sms_message(self, available_courts: Dict[str, List[Dict]]) -> str:
        """Format SMS message for UBC courts"""
        total_courts = sum(len(courts) for courts in available_courts.values())

        message = f"🎾 UBC Tennis: {total_courts} court(s) available!\n"

        for date, courts in available_courts.items():
            message += f"\n📅 {date}:\n"
            for court in courts:
                court_name = court.get("court_name", "Unknown")
                time_slot = court.get("time", "Unknown")
                price = court.get("price", "Unknown")
                message += f"• {court_name} at {time_slot} ({price})\n"

        message += "\nBook now: https://recreation.ubc.ca/tennis/court-booking/"

        return message

    def _create_notification_key(self, available_courts: Dict[str, List[Dict]]) -> str:
        """Create unique key for notification deduplication"""
        court_strings = []

        for date, courts in available_courts.items():
            for court in courts:
                court_str = (
                    f"{date}_{court.get('court_name', '')}_{court.get('time', '')}"
                )
                court_strings.append(court_str)

        return "_".join(sorted(court_strings))

    def send_test_notification(self) -> bool:
        """Send a test notification to verify configuration"""
        try:
            # Create test court data
            test_courts = {
                "2025-10-26": [
                    {
                        "court_name": "Court 1",
                        "time": "10:00 AM",
                        "duration": "1 hour",
                        "price": "$32.15",
                    }
                ]
            }

            self.logger.info("Sending test UBC notification...")
            return self.send_notifications(test_courts)

        except Exception as e:
            self.logger.error(f"Error sending test UBC notification: {e}")
            return False
