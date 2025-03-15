#!/usr/bin/env python3
import os
import logging
from logger import SecureLogger

def main():
    # Initialize the secure logger
    logger = SecureLogger(log_dir="./logs")
    
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

if __name__ == "__main__":
    main()