#!/usr/bin/env python3
"""
Common Notification Manager Base Class
Shared notification functionality for all tennis court monitors
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from twilio.rest import Client

from common.config.base_config import BaseConfig


class BaseNotificationManager(ABC):
    """Base notification manager for tennis court availability"""
    
    def __init__(self, config: BaseConfig):
        self.config = config
        self.notification_config = config.get_notification_config()
        self.logger = self._setup_logger()
        self.sent_notifications: set = set()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for notifications"""
        logger = logging.getLogger(f'{self.config.facility_name.lower()}_notifications')
        logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add handler
        logger.addHandler(console_handler)
        
        return logger
    
    def send_notifications(self, available_courts: Dict[str, List[Dict]]) -> bool:
        """Send notifications for available courts"""
        try:
            if not available_courts:
                self.logger.info("No courts to notify about")
                return True
            
            total_courts = sum(len(courts) for courts in available_courts.values())
            self.logger.info(f"Sending notifications for {total_courts} available {self.config.facility_name} courts")
            
            # Send email notification
            email_sent = self._send_email_notification(available_courts)
            
            # Send SMS notification
            sms_sent = self._send_sms_notification(available_courts)
            
            return email_sent and sms_sent
            
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")
            return False
    
    def _send_email_notification(self, available_courts: Dict[str, List[Dict]]) -> bool:
        """Send email notification for courts"""
        try:
            email = self.notification_config.get('email')
            gmail_password = self.notification_config.get('gmail_app_password')
            
            if not email or not gmail_password:
                self.logger.warning("Email credentials not configured, skipping email notification")
                return True
            
            # Create message
            subject = f"🎾 {self.config.facility_name.upper()} Tennis Courts Available!"
            body = self._format_email_message(available_courts)
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email, gmail_password)
            text = msg.as_string()
            server.sendmail(email, email, text)
            server.quit()
            
            self.logger.info(f"{self.config.facility_name} email notification sent successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending {self.config.facility_name} email notification: {e}")
            return False
    
    def _send_sms_notification(self, available_courts: Dict[str, List[Dict]]) -> bool:
        """Send SMS notification for courts"""
        try:
            phone = self.notification_config.get('sms_phone')
            twilio_sid = self.notification_config.get('twilio_sid')
            twilio_token = self.notification_config.get('twilio_token')
            twilio_phone = self.notification_config.get('twilio_phone')
            
            if not all([phone, twilio_sid, twilio_token, twilio_phone]):
                self.logger.warning("SMS credentials not configured, skipping SMS notification")
                return True
            
            # Create message
            message = self._format_sms_message(available_courts)
            
            # Create unique key for this notification
            notification_key = self._create_notification_key(available_courts)
            
            if notification_key in self.sent_notifications:
                self.logger.info("SMS notification already sent for this court combination")
                return True
            
            # Send SMS
            client = Client(twilio_sid, twilio_token)
            message_obj = client.messages.create(
                body=message,
                from_=twilio_phone,
                to=phone
            )
            
            self.sent_notifications.add(notification_key)
            self.logger.info(f"{self.config.facility_name} SMS notification sent successfully! SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending {self.config.facility_name} SMS notification: {e}")
            return False
    
    @abstractmethod
    def _format_email_message(self, available_courts: Dict[str, List[Dict]]) -> str:
        """Format email message for courts"""
        pass
    
    @abstractmethod
    def _format_sms_message(self, available_courts: Dict[str, List[Dict]]) -> str:
        """Format SMS message for courts"""
        pass
    
    def _create_notification_key(self, available_courts: Dict[str, List[Dict]]) -> str:
        """Create unique key for notification deduplication"""
        court_strings = []
        
        for date, courts in available_courts.items():
            for court in courts:
                court_str = f"{date}_{court.get('court_name', '')}_{court.get('time', '')}"
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
                        "price": "$32.15"
                    }
                ]
            }
            
            self.logger.info(f"Sending test {self.config.facility_name} notification...")
            return self.send_notifications(test_courts)
            
        except Exception as e:
            self.logger.error(f"Error sending test {self.config.facility_name} notification: {e}")
            return False
