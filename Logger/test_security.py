#!/usr/bin/env python3
import os
import sys
import unittest
import io
import logging
from unittest.mock import patch, MagicMock
from logger import SecureLogger

class TestSecureLogger(unittest.TestCase):
    """Test cases for the SecureLogger class with focus on security features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_log_dir = "./test_logs"
        self.logger = SecureLogger(log_dir=self.test_log_dir)
        
        # Create test directory if it doesn't exist
        if not os.path.exists(self.test_log_dir):
            os.makedirs(self.test_log_dir)
            
        # Path to the suspicious file
        self.suspicious_file = os.path.abspath("33333333333333333333333334.ccurve")
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove test log files
        if os.path.exists(self.test_log_dir):
            for file in os.listdir(self.test_log_dir):
                os.remove(os.path.join(self.test_log_dir, file))
            os.rmdir(self.test_log_dir)
    
    def test_suspicious_message_detection(self):
        """Test that suspicious messages are detected and logged to security log."""
        suspicious_messages = [
            "The keylogger is running in the background",
            "How to bypass Windows Defender for my application",
            "Script to steal passwords from browser",
            "Adding program to startup folder for persistence",
            "Using smtplib to send collected data"
        ]
        
        for message in suspicious_messages:
            self.logger.info(message)
        
        # Check that security log exists and contains alerts
        security_log_path = os.path.join(self.test_log_dir, "security.log")
        self.assertTrue(os.path.exists(security_log_path), "Security log file was not created")
        
        with open(security_log_path, 'r') as f:
            content = f.read()
            
        # Verify each suspicious message triggered an alert
        for message in suspicious_messages:
            self.assertIn("Suspicious content detected", content, 
                         f"Security alert not logged for message: {message}")
    
    def test_log_sanitization(self):
        """Test that log messages are properly sanitized."""
        # Test newline sanitization
        message_with_newlines = "This message\nhas newlines\rand should be\nsanitized"
        self.logger.info(message_with_newlines)
        
        # Check application log
        app_log_path = os.path.join(self.test_log_dir, "application.log")
        with open(app_log_path, 'r') as f:
            content = f.read()
            
        self.assertNotIn("\n has newlines", content, "Newlines were not sanitized")
        self.assertIn("has newlines", content, "Message content was lost during sanitization")
        
        # Test long message truncation
        long_message = "x" * 15000  # Message longer than the 10000 character limit
        self.logger.info(long_message)
        
        with open(app_log_path, 'r') as f:
            content = f.read()
            
        self.assertIn("message truncated", content, "Long message was not truncated")
    
    def test_suspicious_file_logging(self):
        """Test logging content of a suspicious file."""
        # Skip test if suspicious file doesn't exist
        if not os.path.exists(self.suspicious_file):
            self.skipTest(f"Suspicious file {self.suspicious_file} not found")
            
        # Log the suspicious file
        result = self.logger.log_file_content(self.suspicious_file)
        self.assertTrue(result, "File logging failed")
        
        # Check security log for alerts
        security_log_path = os.path.join(self.test_log_dir, "security.log")
        with open(security_log_path, 'r') as f:
            content = f.read()
            
        self.assertIn("Suspicious content detected in file", content, 
                     "Security alert not logged for suspicious file")
        
        # Verify file hash was logged
        app_log_path = os.path.join(self.test_log_dir, "application.log")
        with open(app_log_path, 'r') as f:
            content = f.read()
            
        self.assertIn("file_hash", content, "File hash was not logged")
        
    def test_metadata_logging(self):
        """Test that metadata is properly included in logs."""
        # Log with metadata
        self.logger.info("Test message with metadata", 
                        user="test_user", 
                        ip_address="127.0.0.1", 
                        action="login")
        
        # Check application log
        app_log_path = os.path.join(self.test_log_dir, "application.log")
        with open(app_log_path, 'r') as f:
            content = f.read()
            
        self.assertIn("test_user", content, "User metadata not found in log")
        self.assertIn("127.0.0.1", content, "IP address metadata not found in log")
        self.assertIn("login", content, "Action metadata not found in log")
    
    @patch('smtplib.SMTP')
    def test_email_alerts(self, mock_smtp):
        """Test email alert functionality."""
        # Configure mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        
        # Configure logger with email alerts enabled
        email_config = {
            'smtp_server': 'test-smtp.example.com',
            'smtp_port': 587,
            'smtp_user': 'test-user',
            'smtp_password': 'test-password',
            'from_addr': 'test@example.com',
            'to_addrs': ['admin@example.com'],
            'use_tls': True,
            'min_level_for_email': logging.WARNING
        }
        
        logger = SecureLogger(
            log_dir=self.test_log_dir,
            enable_email_alerts=True,
            email_config=email_config
        )
        
        # Log a suspicious message with WARNING level
        logger.warning("This message contains keylogger reference which should trigger an alert")
        
        # Verify SMTP was called
        mock_smtp.assert_called_once_with('test-smtp.example.com', 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with('test-user', 'test-password')
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()
    
    def test_console_output(self):
        """Test console output configuration."""
        # This test is more of a functional test than a unit test
        # since it's difficult to capture console output from the logger
        # We'll just verify that the logger can be created with custom console config
        
        console_config = {
            'enable': True,
            'format': '%(levelname)s: %(message)s',
            'min_level': logging.INFO
        }
        
        # This should not raise any exceptions
        logger = SecureLogger(
            log_dir=self.test_log_dir,
            console_config=console_config
        )
        
        # Log a message
        logger.info("Test console output")
        
        # Test passes if no exceptions are raised
        self.assertTrue(True)
    
    def test_disable_console_output(self):
        """Test disabling console output."""
        # Similar to test_console_output, this is more of a functional test
        # We'll just verify that the logger can be created with console output disabled
        
        console_config = {
            'enable': False
        }
        
        # This should not raise any exceptions
        logger = SecureLogger(
            log_dir=self.test_log_dir,
            console_config=console_config
        )
        
        # Log a message
        logger.info("This should not appear in console")
        
        # Test passes if no exceptions are raised
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()