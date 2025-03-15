#!/usr/bin/env python3
import os
import sys
import subprocess
import time

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def run_command(command, description):
    """Run a command and print its output."""
    print_header(description)
    print(f"Running: {command}\n")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(e.stdout)
        return False

def check_logs():
    """Check and display log files."""
    print_header("Checking Log Files")
    
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} not found!")
        return
        
    print(f"Log files in {os.path.abspath(log_dir)}:")
    
    for file in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file)
        file_size = os.path.getsize(file_path)
        print(f"- {file} ({file_size} bytes)")
        
        # Show a preview of each log file
        print(f"\nPreview of {file}:")
        try:
            with open(file_path, 'r') as f:
                # Read first 5 lines
                lines = [next(f) for _ in range(5)]
                for line in lines:
                    print(f"  {line.strip()}")
            print("  ...")
        except Exception as e:
            print(f"  Error reading file: {e}")
        print()

def show_email_config_example():
    """Show example of email configuration."""
    print_header("Email Configuration Example")
    
    print("To enable email alerts, you can configure the logger as follows:")
    print("\nPython code example:")
    print("""
    from logger import SecureLogger
    import logging
    
    # Email configuration
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': 'your-email@gmail.com',
        'smtp_password': 'your-app-password',
        'from_addr': 'security-alerts@yourcompany.com',
        'to_addrs': ['admin@yourcompany.com', 'security@yourcompany.com'],
        'use_tls': True,
        'subject_prefix': '[SECURITY ALERT]',
        'min_level_for_email': logging.WARNING
    }
    
    # Initialize logger with email alerts enabled
    logger = SecureLogger(
        enable_email_alerts=True,
        email_config=email_config
    )
    """)
    
    print("\nWhen suspicious content is detected, an email alert will be sent to the configured recipients.")
    print("For Gmail, you'll need to use an App Password instead of your regular password.")
    print("See: https://support.google.com/accounts/answer/185833")

def show_console_config_example():
    """Show example of console configuration."""
    print_header("Console Configuration Example")
    
    print("You can customize the console output with the following configuration:")
    print("\nPython code example:")
    print("""
    from logger import SecureLogger
    import logging
    
    # Console configuration
    console_config = {
        'enable': True,                                # Enable/disable console output
        'format': '%(asctime)s [%(levelname)s] %(message)s',  # Custom format
        'colors': True,                                # Enable colored output
        'min_level': logging.DEBUG                     # Show all messages including debug
    }
    
    # Initialize logger with custom console configuration
    logger = SecureLogger(console_config=console_config)
    """)
    
    print("\nThis allows you to control how log messages appear in the console.")
    print("You can disable console output entirely by setting 'enable' to False.")

def main():
    """Run the demo and tests."""
    print_header("Secure Logger Demo")
    print("This script will demonstrate the Secure Logger functionality")
    print("by running the example script and tests.")
    
    # Run the example script
    if run_command("python example.py", "Running Example Script"):
        # Wait a moment for logs to be written
        time.sleep(1)
        check_logs()
    
    # Show email configuration example
    show_email_config_example()
    
    # Show console configuration example
    show_console_config_example()
    
    # Run the tests
    run_command("python test_security.py", "Running Security Tests")
    
    print_header("Demo Complete")
    print("The Secure Logger has been demonstrated.")
    print("Check the README.md file for more information on how to use the logger.")

if __name__ == "__main__":
    main()