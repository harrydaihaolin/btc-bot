"""
Notification system for BTC Tennis Bot
"""

import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Set


class NotificationManager:
    """Manages all notification types for the BTC Tennis Bot"""

    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
        self.sent_notifications: Set[str] = set()

    def create_notification_id(self, courts: List[Dict], date_str: str) -> str:
        """Create a unique notification ID based on court details and date"""
        if not courts:
            return None

        # Create a unique identifier based on court details
        court_signatures = []
        for court in courts:
            signature = f"{court.get('time', '')}_{court.get('court_number', '')}_{court.get('text', '')}"
            court_signatures.append(signature)

        # Sort to ensure consistent ordering
        court_signatures.sort()
        notification_id = f"{date_str}_{'_'.join(court_signatures)}"
        return notification_id

    def clear_old_notifications(self):
        """Clear old notifications to prevent memory buildup"""
        if len(self.sent_notifications) > 100:
            # Keep only the most recent 50 notifications
            notifications_list = list(self.sent_notifications)
            self.sent_notifications = set(notifications_list[-50:])
            self.logger.info("Cleared old notifications to prevent memory buildup")

    def send_email_notification(self, all_courts: Dict[str, List[Dict]]) -> bool:
        """Send email notification when courts become available"""
        try:
            # Flatten all courts for idempotency check
            all_courts_flat = []
            for date, courts in all_courts.items():
                all_courts_flat.extend(courts)

            if not all_courts_flat:
                return True

            # Check for idempotency
            notification_id = self.create_notification_id(all_courts_flat, "multi_date")
            if notification_id in self.sent_notifications:
                self.logger.info(
                    f"Email notification already sent for this court combination: {notification_id}"
                )
                return True

            total_courts = sum(len(courts) for courts in all_courts.values())
            self.logger.info(
                f"Sending notification for {total_courts} available courts across all dates"
            )

            # Create notification message
            message = self._create_email_message(all_courts, total_courts)

            # Send email
            success = self._send_email(message, total_courts)

            if success and notification_id:
                self.sent_notifications.add(notification_id)

            return success

        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False

    def send_sms_notification(self, all_courts: Dict[str, List[Dict]]) -> bool:
        """Send SMS notification when courts become available"""
        if not self.credentials.get("phone_number"):
            self.logger.warning("No phone number provided for SMS notifications")
            return False

        try:
            # Flatten all courts for idempotency check
            all_courts_flat = []
            for date, courts in all_courts.items():
                all_courts_flat.extend(courts)

            if not all_courts_flat:
                return True

            # Check for idempotency
            notification_id = self.create_notification_id(all_courts_flat, "multi_date")
            if notification_id in self.sent_notifications:
                self.logger.info(
                    f"SMS notification already sent for this court combination: {notification_id}"
                )
                return True

            total_courts = sum(len(courts) for courts in all_courts.values())
            self.logger.info(
                f"Sending SMS notification for {total_courts} available courts across all dates"
            )

            # Create SMS message
            sms_message = self._create_sms_message(all_courts, total_courts)

            # Send SMS
            success = self._send_sms(sms_message)

            if success and notification_id:
                self.sent_notifications.add(notification_id)

            return success

        except Exception as e:
            self.logger.error(f"Failed to send SMS notification: {e}")
            return False

    def _create_email_message(
        self, all_courts: Dict[str, List[Dict]], total_courts: int
    ) -> str:
        """Create email message content"""
        message = f"""
🎾 BURNABY TENNIS CLUB - COURTS AVAILABLE! 🎾

Great news! {total_courts} tennis court slots have become available across multiple dates:

"""

        court_counter = 1
        for date, courts in all_courts.items():
            if courts:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                date_label = date_obj.strftime("%A, %B %d, %Y")
                message += f"\n📅 {date_label}:\n"
                for court in courts:
                    message += f"   {court_counter}. {court.get('text', 'N/A')} - {court.get('time', 'N/A')}\n"
                    court_counter += 1

        message += f"""
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Booking URL: https://www.burnabytennis.ca/app/bookings/grid

Hurry up and book your court! 🏃‍♂️

---
BTC Booking Bot 🤖
        """

        return message

    def _create_sms_message(
        self, all_courts: Dict[str, List[Dict]], total_courts: int
    ) -> str:
        """Create SMS message content"""
        sms_message = f"🎾 BTC: {total_courts} courts available! "

        # Add first few courts from all dates
        court_count = 0
        for date, courts in all_courts.items():
            if courts and court_count < 3:
                for court in courts[:2]:
                    if court_count < 3:
                        sms_message += f"{court.get('time', 'N/A')} "
                        court_count += 1

        if total_courts > 3:
            sms_message += f"+{total_courts-3} more"

        sms_message += f"Book: https://www.burnabytennis.ca/app/bookings/grid"

        return sms_message

    def _send_email(self, message: str, total_courts: int) -> bool:
        """Send email via Gmail SMTP"""
        try:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = self.credentials.get(
                "gmail_app_email"
            ) or self.credentials.get("notification_email")

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = self.credentials.get("notification_email")
            msg["Subject"] = (
                f"🎾 BTC Tennis Courts Available - {total_courts} slots found!"
            )

            msg.attach(MIMEText(message, "plain"))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            app_password = self.credentials.get("gmail_app_password")
            server.login(sender_email, app_password)
            text = msg.as_string()
            server.sendmail(
                sender_email, self.credentials.get("notification_email"), text
            )
            server.quit()

            self.logger.info("Email notification sent successfully!")
            return True

        except Exception as e:
            self.logger.warning(f"Gmail SMTP failed: {e}")
            return False

    def _send_sms(self, sms_message: str) -> bool:
        """Send SMS via email-to-SMS gateway"""
        try:
            phone_number = self.credentials.get("phone_number")

            # Email-to-SMS gateways for Canadian carriers
            sms_gateways = {
                "rogers": f"{phone_number}@pcs.rogers.com",
                "bell": f"{phone_number}@txt.bell.ca",
                "telus": f"{phone_number}@msg.telus.com",
                "fido": f"{phone_number}@fido.ca",
                "virgin": f"{phone_number}@vmobile.ca",
                "koodo": f"{phone_number}@msg.koodomobile.com",
            }

            # Try each carrier gateway
            for carrier, sms_email in sms_gateways.items():
                try:
                    self.logger.info(f"Trying SMS via {carrier} gateway: {sms_email}")

                    msg = MIMEMultipart()
                    msg["From"] = self.credentials.get("notification_email")
                    msg["To"] = sms_email
                    msg["Subject"] = ""

                    msg.attach(MIMEText(sms_message, "plain"))

                    # Send via Gmail SMTP
                    smtp_server = "smtp.gmail.com"
                    smtp_port = 587

                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    app_password = self.credentials.get("gmail_app_password")
                    server.login(
                        self.credentials.get("gmail_app_email")
                        or self.credentials.get("notification_email"),
                        app_password,
                    )
                    text = msg.as_string()
                    server.sendmail(
                        self.credentials.get("notification_email"), sms_email, text
                    )
                    server.quit()

                    self.logger.info(f"SMS sent successfully via {carrier} gateway!")
                    return True

                except Exception as e:
                    self.logger.warning(f"SMS via {carrier} failed: {e}")
                    continue

            # Fallback: Console SMS simulation
            self.logger.info("SMS gateway failed, using console simulation...")
            print(f"\n📱 SMS SIMULATION TO {phone_number}:")
            print("=" * 50)
            print(sms_message)
            print("=" * 50)
            return True

        except Exception as e:
            self.logger.error(f"Failed to send SMS notification: {e}")
            return False
