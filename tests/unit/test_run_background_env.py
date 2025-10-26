"""
Unit tests for run_background_env.py
"""
import pytest
from unittest.mock import patch, MagicMock
import signal
from run_background_env import BackgroundMonitor


class TestBackgroundMonitor:
    """Test cases for BackgroundMonitor class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.monitor = BackgroundMonitor()
    
    def test_init(self):
        """Test BackgroundMonitor initialization"""
        assert self.monitor.running is True
        assert self.monitor.logger is not None
        assert self.monitor.config_manager is not None
        assert self.monitor.monitor is None
        assert self.monitor.notification_manager is None
        assert self.monitor.credentials is None
        assert self.monitor.config is None
    
    def test_signal_handler(self):
        """Test signal handler"""
        self.monitor.signal_handler(signal.SIGTERM, None)
        assert self.monitor.running is False
    
    @patch('run_background_env.signal.signal')
    def test_setup_signal_handlers(self, mock_signal):
        """Test signal handler setup"""
        self.monitor.setup_signal_handlers()
        
        assert mock_signal.call_count == 2
        mock_signal.assert_any_call(signal.SIGINT, self.monitor.signal_handler)
        mock_signal.assert_any_call(signal.SIGTERM, self.monitor.signal_handler)
    
    def test_check_environment_variables_success(self):
        """Test environment variable check with success"""
        with patch.object(self.monitor.config_manager, 'validate_credentials', return_value=True):
            result = self.monitor.check_environment_variables()
            assert result is True
    
    def test_check_environment_variables_failure(self):
        """Test environment variable check with failure"""
        with patch.object(self.monitor.config_manager, 'validate_credentials', return_value=False):
            result = self.monitor.check_environment_variables()
            assert result is False
    
    @patch('run_background_env.CourtMonitor')
    @patch('run_background_env.NotificationManager')
    def test_initialize_components_success(self, mock_notification_class, mock_monitor_class):
        """Test successful component initialization"""
        with patch.object(self.monitor.config_manager, 'get_credentials', return_value={'username': 'test@example.com'}):
            with patch.object(self.monitor.config_manager, 'get_bot_config', return_value={'headless': True}):
                with patch.object(self.monitor.config_manager, 'get_monitoring_config', return_value={'monitoring_interval': 5}):
                    with patch.object(self.monitor.config_manager, 'validate_credentials', return_value=True):
                        mock_monitor_instance = MagicMock()
                        mock_notification_instance = MagicMock()
                        mock_monitor_class.return_value = mock_monitor_instance
                        mock_notification_class.return_value = mock_notification_instance
                        
                        result = self.monitor.initialize_components()
                        
                        assert result is True
                        assert self.monitor.credentials == {'username': 'test@example.com'}
                        assert self.monitor.config == {'headless': True}
                        assert self.monitor.monitor == mock_monitor_instance
                        assert self.monitor.notification_manager == mock_notification_instance
    
    def test_initialize_components_invalid_credentials(self):
        """Test component initialization with invalid credentials"""
        with patch.object(self.monitor.config_manager, 'get_credentials', return_value={'username': 'test@example.com'}):
            with patch.object(self.monitor.config_manager, 'get_bot_config', return_value={'headless': True}):
                with patch.object(self.monitor.config_manager, 'get_monitoring_config', return_value={'monitoring_interval': 5}):
                    with patch.object(self.monitor.config_manager, 'validate_credentials', return_value=False):
                        result = self.monitor.initialize_components()
                        assert result is False
    
    def test_initialize_components_exception(self):
        """Test component initialization with exception"""
        with patch.object(self.monitor.config_manager, 'get_credentials', side_effect=Exception("Config error")):
            result = self.monitor.initialize_components()
            assert result is False
    
    def test_run_initial_scan_success(self):
        """Test successful initial scan"""
        mock_monitor = MagicMock()
        self.monitor.monitor = mock_monitor
        mock_monitor.setup_driver.return_value = None
        mock_monitor.login.return_value = True
        mock_monitor.navigate_to_booking_page.return_value = True
        
        mock_courts = {
            '2025-10-26': [
                {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'}
            ]
        }
        mock_monitor.scan_all_dates.return_value = mock_courts
        
        result = self.monitor.run_initial_scan()
        
        assert result == mock_courts
        mock_monitor.setup_driver.assert_called_once()
        mock_monitor.login.assert_called_once()
        mock_monitor.navigate_to_booking_page.assert_called_once()
        mock_monitor.scan_all_dates.assert_called_once()
    
    def test_run_initial_scan_login_failed(self):
        """Test initial scan with login failure"""
        mock_monitor = MagicMock()
        self.monitor.monitor = mock_monitor
        mock_monitor.setup_driver.return_value = None
        mock_monitor.login.return_value = False
        mock_monitor.navigate_to_booking_page.return_value = True
        
        mock_courts = {}
        mock_monitor.scan_all_dates.return_value = mock_courts
        
        result = self.monitor.run_initial_scan()
        
        assert result == mock_courts
        mock_monitor.login.assert_called_once()
        mock_monitor.navigate_to_booking_page.assert_called_once()
    
    def test_run_initial_scan_navigation_failed(self):
        """Test initial scan with navigation failure"""
        mock_monitor = MagicMock()
        self.monitor.monitor = mock_monitor
        mock_monitor.setup_driver.return_value = None
        mock_monitor.login.return_value = True
        mock_monitor.navigate_to_booking_page.return_value = False
        
        result = self.monitor.run_initial_scan()
        
        assert result == {}
        mock_monitor.login.assert_called_once()
        mock_monitor.navigate_to_booking_page.assert_called_once()
    
    def test_run_initial_scan_exception(self):
        """Test initial scan with exception"""
        mock_monitor = MagicMock()
        self.monitor.monitor = mock_monitor
        mock_monitor.setup_driver.side_effect = Exception("Setup failed")
        
        result = self.monitor.run_initial_scan()
        
        assert result == {}
    
    def test_run_continuous_monitoring_success(self):
        """Test successful continuous monitoring"""
        mock_monitor = MagicMock()
        mock_notification_manager = MagicMock()
        
        self.monitor.monitor = mock_monitor
        self.monitor.notification_manager = mock_notification_manager
        
        with patch.object(self.monitor.config_manager, 'get_monitoring_config', return_value={
            'monitoring_interval': 1,
            'max_attempts': 1
        }):
            mock_courts = {
                '2025-10-26': [
                    {'time': '6:00 AM', 'text': 'Book 6:00 am as 48hr', 'court_number': '1'}
                ]
            }
            mock_monitor.scan_all_dates.return_value = mock_courts
            mock_monitor.detect_new_courts.return_value = mock_courts
            
            with patch('run_background_env.time.sleep', side_effect=KeyboardInterrupt()):
                self.monitor.run_continuous_monitoring()
            
            mock_monitor.scan_all_dates.assert_called_once()
            mock_monitor.detect_new_courts.assert_called_once_with(mock_courts)
            mock_notification_manager.send_email_notification.assert_called_once_with(mock_courts)
            mock_notification_manager.send_sms_notification.assert_called_once_with(mock_courts)
    
    def test_run_continuous_monitoring_no_courts(self):
        """Test continuous monitoring with no courts"""
        mock_monitor = MagicMock()
        
        self.monitor.monitor = mock_monitor
        
        with patch.object(self.monitor.config_manager, 'get_monitoring_config', return_value={
            'monitoring_interval': 1,
            'max_attempts': 1
        }):
            mock_monitor.scan_all_dates.return_value = {}
            
            with patch('run_background_env.time.sleep', side_effect=KeyboardInterrupt()):
                self.monitor.run_continuous_monitoring()
            
            mock_monitor.scan_all_dates.assert_called_once()
    
    def test_run_continuous_monitoring_exception(self):
        """Test continuous monitoring with exception"""
        mock_monitor = MagicMock()
        
        self.monitor.monitor = mock_monitor
        
        with patch.object(self.monitor.config_manager, 'get_monitoring_config', return_value={
            'monitoring_interval': 1,
            'max_attempts': 1
        }):
            mock_monitor.scan_all_dates.side_effect = Exception("Scan failed")
            
            with patch('run_background_env.time.sleep', side_effect=KeyboardInterrupt()):
                self.monitor.run_continuous_monitoring()
            
            mock_monitor.scan_all_dates.assert_called_once()
    
    def test_run_success(self):
        """Test successful run"""
        with patch.object(self.monitor, 'initialize_components', return_value=True):
            with patch.object(self.monitor, 'setup_signal_handlers'):
                with patch.object(self.monitor, 'run_initial_scan', return_value={}):
                    with patch.object(self.monitor, 'run_continuous_monitoring'):
                        result = self.monitor.run()
        
        assert result is True
    
    def test_run_initialization_failed(self):
        """Test run with initialization failure"""
        with patch.object(self.monitor, 'initialize_components', return_value=False):
            result = self.monitor.run()
        
        assert result is False
    
    def test_run_exception(self):
        """Test run with exception"""
        with patch.object(self.monitor, 'initialize_components', return_value=True):
            with patch.object(self.monitor, 'setup_signal_handlers'):
                with patch.object(self.monitor, 'run_initial_scan', side_effect=Exception("Run failed")):
                    result = self.monitor.run()
        
        assert result is False
    
    def test_run_finally_cleanup(self):
        """Test that cleanup is called in finally block"""
        mock_monitor = MagicMock()
        self.monitor.monitor = mock_monitor
        
        # The run method catches exceptions and returns False, so we need to check cleanup is called
        with patch.object(self.monitor, 'initialize_components', return_value=True):
            with patch.object(self.monitor, 'setup_signal_handlers'):
                with patch.object(self.monitor, 'run_initial_scan', side_effect=Exception("Run failed")):
                    result = self.monitor.run()
        
        assert result is False
        mock_monitor.cleanup.assert_called_once()
