"""
Unit tests for core/notifications.py
"""
import pytest
from unittest.mock import patch, MagicMock, call
import smtplib
from core.notifications import NotificationManager


class TestNotificationManager:
    """Test cases for NotificationManager class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.credentials = {
            'notification_email': 'test@example.com',
            'phone_number': '1234567890',
            'gmail_app_email': 'gmail@gmail.com',
            'gmail_app_password': 'apppass'
        }
        self.notification_manager = NotificationManager(self.credentials)
    
    def test_init(self):
        """Test NotificationManager initialization"""
        assert self.notification_manager.credentials == self.credentials
        assert self.notification_manager.logger is not None
        assert isinstance(self.notification_manager.sent_notifications, set)
    
    def test_init_missing_credentials(self):
        """Test NotificationManager initialization with missing credentials"""
        incomplete_credentials = {
            'notification_email': 'test@example.com',
            'phone_number': '1234567890'
        }
        manager = NotificationManager(incomplete_credentials)
        
        assert manager.credentials == incomplete_credentials
        assert manager.logger is not None
        assert isinstance(manager.sent_notifications, set)
    
    def test_create_notification_id_with_courts(self):
        """Test notification ID creation with courts"""
        courts = [
            {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'},
            {'time': '8:00 AM', 'text': 'Book 8:00 am as 48hr', 'court_number': '2'}
        ]
        
        notification_id = self.notification_manager.create_notification_id(courts, "2025-10-26")
        
        assert notification_id is not None
        assert "2025-10-26" in notification_id
        assert "6:00 AM" in notification_id
        assert "8:00 AM" in notification_id
    
    def test_create_notification_id_empty_courts(self):
        """Test notification ID creation with empty courts"""
        courts = []
        
        notification_id = self.notification_manager.create_notification_id(courts, "2025-10-26")
        
        assert notification_id is None
    
    def test_clear_old_notifications(self):
        """Test clearing old notifications"""
        # Add many notifications
        for i in range(150):
            self.notification_manager.sent_notifications.add(f"notification_{i}")
        
        assert len(self.notification_manager.sent_notifications) == 150
        
        self.notification_manager.clear_old_notifications()
        
        assert len(self.notification_manager.sent_notifications) == 50
    
    def test_clear_old_notifications_not_needed(self):
        """Test clearing old notifications when not needed"""
        # Add few notifications
        for i in range(50):
            self.notification_manager.sent_notifications.add(f"notification_{i}")
        
        assert len(self.notification_manager.sent_notifications) == 50
        
        self.notification_manager.clear_old_notifications()
        
        assert len(self.notification_manager.sent_notifications) == 50
    
    @patch.object(NotificationManager, '_send_email')
    def test_send_email_notification_success(self, mock_send_email):
        """Test successful email notification"""
        mock_send_email.return_value = True
        
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'}
            ]
        }
        
        result = self.notification_manager.send_email_notification(courts)
        
        assert result is True
        mock_send_email.assert_called_once()
    
    @patch.object(NotificationManager, '_send_email')
    def test_send_email_notification_empty_courts(self, mock_send_email):
        """Test email notification with empty courts"""
        courts = {}
        
        result = self.notification_manager.send_email_notification(courts)
        
        assert result is True
        mock_send_email.assert_not_called()
    
    @patch.object(NotificationManager, '_send_email')
    def test_send_email_notification_deduplication(self, mock_send_email):
        """Test email notification deduplication"""
        mock_send_email.return_value = True
        
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'}
            ]
        }
        
        # First call
        result1 = self.notification_manager.send_email_notification(courts)
        assert result1 is True
        
        # Second call with same courts should be deduplicated
        result2 = self.notification_manager.send_email_notification(courts)
        assert result2 is True
        
        # Should only be called once due to deduplication
        assert mock_send_email.call_count == 1
    
    @patch.object(NotificationManager, '_send_email')
    def test_send_email_notification_exception(self, mock_send_email):
        """Test email notification with exception"""
        mock_send_email.side_effect = Exception("Email failed")
        
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'}
            ]
        }
        
        result = self.notification_manager.send_email_notification(courts)
        
        assert result is False
    
    @patch.object(NotificationManager, '_send_sms')
    def test_send_sms_notification_success(self, mock_send_sms):
        """Test successful SMS notification"""
        mock_send_sms.return_value = True
        
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'}
            ]
        }
        
        result = self.notification_manager.send_sms_notification(courts)
        
        assert result is True
        mock_send_sms.assert_called_once()
    
    def test_send_sms_notification_no_phone(self):
        """Test SMS notification with no phone number"""
        incomplete_credentials = {
            'notification_email': 'test@example.com'
        }
        manager = NotificationManager(incomplete_credentials)
        
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'}
            ]
        }
        
        result = manager.send_sms_notification(courts)
        
        assert result is False
    
    @patch.object(NotificationManager, '_send_sms')
    def test_send_sms_notification_empty_courts(self, mock_send_sms):
        """Test SMS notification with empty courts"""
        courts = {}
        
        result = self.notification_manager.send_sms_notification(courts)
        
        assert result is True
        mock_send_sms.assert_not_called()
    
    @patch.object(NotificationManager, '_send_sms')
    def test_send_sms_notification_deduplication(self, mock_send_sms):
        """Test SMS notification deduplication"""
        mock_send_sms.return_value = True
        
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'}
            ]
        }
        
        # First call
        result1 = self.notification_manager.send_sms_notification(courts)
        assert result1 is True
        
        # Second call with same courts should be deduplicated
        result2 = self.notification_manager.send_sms_notification(courts)
        assert result2 is True
        
        # Should only be called once due to deduplication
        assert mock_send_sms.call_count == 1
    
    @patch.object(NotificationManager, '_send_sms')
    def test_send_sms_notification_exception(self, mock_send_sms):
        """Test SMS notification with exception"""
        mock_send_sms.side_effect = Exception("SMS failed")
        
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'}
            ]
        }
        
        result = self.notification_manager.send_sms_notification(courts)
        
        assert result is False
    
    def test_create_email_message(self):
        """Test email message creation"""
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'},
                {'time': '8:00 AM', 'text': 'Book 8:00 am as 48hr', 'court_number': '2'}
            ]
        }
        
        message = self.notification_manager._create_email_message(courts, 2)
        
        assert 'BURNABY TENNIS CLUB' in message
        assert '2 tennis court slots' in message
        assert '6:00 am as 48hr' in message
        assert '8:00 am as 48hr' in message
        assert 'Booking URL' in message
    
    def test_create_sms_message(self):
        """Test SMS message creation"""
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'},
                {'time': '8:00 AM', 'text': 'Book 8:00 am as 48hr', 'court_number': '2'}
            ]
        }
        
        message = self.notification_manager._create_sms_message(courts, 2)
        
        assert 'BTC: 2 courts available!' in message
        assert '6:00 AM' in message
        assert '8:00 AM' in message
        assert 'Book:' in message
    
    def test_create_sms_message_many_courts(self):
        """Test SMS message creation with many courts"""
        courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'},
                {'time': '8:00 AM', 'text': 'Book 8:00 am as 48hr', 'court_number': '2'},
                {'time': '10:00 AM', 'text': 'Book 10:00 am as 48hr', 'court_number': '3'},
                {'time': '12:00 PM', 'text': 'Book 12:00 pm as 48hr', 'court_number': '4'}
            ]
        }
        
        message = self.notification_manager._create_sms_message(courts, 4)
        
        assert 'BTC: 4 courts available!' in message
        assert '+1 more' in message
        assert 'Book:' in message
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        message = "Test email message"
        result = self.notification_manager._send_email(message, 1)
        
        assert result is True
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp):
        """Test email sending with SMTP error"""
        mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")
        
        message = "Test email message"
        result = self.notification_manager._send_email(message, 1)
        
        assert result is False
    
    @patch('smtplib.SMTP')
    def test_send_sms_success(self, mock_smtp):
        """Test successful SMS sending"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        sms_message = "Test SMS message"
        result = self.notification_manager._send_sms(sms_message)
        
        assert result is True
        # Should try multiple carriers
        assert mock_smtp.call_count >= 1
    
    @patch('smtplib.SMTP')
    def test_send_sms_all_carriers_fail(self, mock_smtp):
        """Test SMS sending when all carriers fail"""
        mock_smtp.side_effect = smtplib.SMTPException("All carriers failed")
        
        sms_message = "Test SMS message"
        result = self.notification_manager._send_sms(sms_message)
        
        # Should fall back to console simulation
        assert result is True
        assert mock_smtp.call_count >= 6  # All carriers tried