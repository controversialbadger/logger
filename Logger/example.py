#!/usr/bin/env python3
import os
import logging
import socket
from logger import SecureLogger

def main():
    # Example email configuration
    email_config = {
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'smtp_user': 'user@example.com',
        'smtp_password': 'password',
        'from_addr': f'securelogger@{socket.gethostname()}',
        'to_addrs': ['admin@example.com'],
        'use_tls': True,
        'subject_prefix': '[SECURITY ALERT]',
        'min_level_for_email': logging.WARNING
    }
    
    # Example console configuration
    console_config = {
        'enable': True,
        'format': '%(asctime)s [%(levelname)s] %(message)s',
        'colors': True,
        'min_level': logging.INFO
    }
    
    # Initialize the secure logger with email and console configuration
    # Note: Email alerts are disabled by default in this example
    logger = SecureLogger(
        log_dir="./logs",
        enable_email_alerts=False,  # Set to True to enable email alerts
        email_config=email_config,
        console_config=console_config
    )
    
    print("Secure Logger Example")
    print("=====================")
    
    # Log some normal messages
    logger.info("Application started")
    logger.debug("Debug information")
    logger.warning("This is a warning message")
    
    # Log a message with additional metadata
    logger.info("User logged in", user_id="user123", ip_address="192.168.1.100")
    
    # Demonstrate logging a file with suspicious content
    suspicious_file_path = os.path.abspath("33333333333333333333333334.ccurve")
    if os.path.exists(suspicious_file_path):
        print(f"\nLogging content of file: {suspicious_file_path}")
        logger.log_file_content(suspicious_file_path)
        print("Check the logs directory for security alerts")
    
    # Demonstrate logging a message with suspicious content
    print("\nLogging a message with suspicious content...")
    logger.info("User reported an issue with keylogger detection in their antivirus software")
    
    # Show where logs are stored
    log_dir = os.path.abspath(logger.log_dir)
    print(f"\nLogs are stored in: {log_dir}")
    print("- application.log: Contains all regular log messages")
    print("- security.log: Contains security alerts for suspicious content")
    
    # Email alerts information
    print("\nEmail Alerts:")
    if logger.enable_email_alerts:
        print("- Email alerts are ENABLED")
        print(f"- SMTP Server: {logger.email_config['smtp_server']}:{logger.email_config['smtp_port']}")
        print(f"- From: {logger.email_config['from_addr']}")
        print(f"- To: {', '.join(logger.email_config['to_addrs'])}")
        print(f"- Minimum level for email alerts: {logging.getLevelName(logger.email_config['min_level_for_email'])}")
    else:
        print("- Email alerts are DISABLED")
        print("- To enable email alerts, set enable_email_alerts=True and configure email_config")

if __name__ == "__main__":
    main()