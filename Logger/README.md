# Secure Logger

A robust and secure logging system designed to detect and handle potentially malicious content while providing comprehensive logging capabilities.

## Features

- **Security Scanning**: Automatically detects suspicious patterns in log messages and file contents
- **Log Sanitization**: Prevents log injection attacks by sanitizing log messages
- **Structured Logging**: Logs are stored in a structured JSON format with metadata
- **Security Alerts**: Separate security log for tracking suspicious activities
- **File Content Logging**: Safely log file contents with security checks
- **File Integrity**: Calculates and stores file hashes for integrity verification

## Installation

Clone the repository and ensure you have Python 3.6+ installed:

```bash
git clone <repository-url>
cd Logger
```

No additional dependencies are required as the logger uses only Python standard library modules.

## Usage

### Basic Usage

```python
from logger import SecureLogger

# Initialize the logger
logger = SecureLogger(log_dir="./logs")

# Log messages with different severity levels
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred", error_code=500)
logger.debug("Debug information")
logger.critical("Critical system failure")

# Log with additional metadata
logger.info("User logged in", user_id="user123", ip_address="192.168.1.100")
```

### Logging File Content

```python
# Log the content of a file with security checks
logger.log_file_content("/path/to/file.txt")
```

### Running the Example

An example script is provided to demonstrate the logger's capabilities:

```bash
python example.py
```

## Security Features

### Suspicious Pattern Detection

The logger includes built-in patterns to detect potentially malicious content, such as:

- Keylogger-related terms
- Password/credential stealing
- Registry modification
- Startup/autorun manipulation
- Antivirus evasion techniques
- And more...

When suspicious content is detected, it's logged to a separate security log file with detailed information.

### Log Sanitization

All log messages are sanitized to prevent log injection attacks:

- Newlines are replaced with spaces
- Message length is limited to prevent DoS attacks
- Structured format prevents injection of malformed data

### File Integrity

When logging file content, the logger:

- Calculates and stores SHA-256 hash of the file
- Limits file size to prevent memory issues
- Checks for suspicious content in the file

## Configuration

The logger can be configured with various options:

```python
logger = SecureLogger(
    log_dir="./logs",                  # Directory to store log files
    log_level=logging.INFO,            # Logging level
    max_log_size=10 * 1024 * 1024,     # 10MB max log file size
    backup_count=5,                    # Number of backup files to keep
    enable_security_scan=True,         # Enable/disable security scanning
    enable_email_alerts=False,         # Enable/disable email alerts
    email_config={                     # Email configuration
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'smtp_user': 'username',
        'smtp_password': 'password',
        'from_addr': 'alerts@example.com',
        'to_addrs': ['admin@example.com'],
        'use_tls': True,
        'subject_prefix': '[SECURITY ALERT]',
        'min_level_for_email': logging.WARNING
    },
    console_config={                   # Console output configuration
        'enable': True,
        'format': '%(asctime)s - %(levelname)s - %(message)s',
        'colors': True,
        'min_level': logging.INFO
    }
)
```

## Email Alerts

The logger can be configured to send email alerts when suspicious content is detected:

### Email Configuration

- **SMTP Settings**: Configure your SMTP server details for sending emails
- **Recipients**: Specify who should receive security alerts
- **Alert Levels**: Set minimum log level that triggers email alerts
- **Customization**: Customize email subject prefix and format

### Example Email Configuration

```python
email_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_user': 'your-email@gmail.com',
    'smtp_password': 'your-app-password',
    'from_addr': 'security-alerts@yourcompany.com',
    'to_addrs': ['admin@yourcompany.com', 'security@yourcompany.com'],
    'use_tls': True,
    'subject_prefix': '[CRITICAL SECURITY ALERT]',
    'min_level_for_email': logging.WARNING
}

logger = SecureLogger(
    enable_email_alerts=True,
    email_config=email_config
)
```

## Console Output

The logger supports customizable console output:

### Console Configuration

- **Enable/Disable**: Turn console output on or off
- **Format**: Customize the format of console log messages
- **Colors**: Enable or disable colored output in the console
- **Minimum Level**: Set the minimum log level for console output

### Example Console Configuration

```python
console_config = {
    'enable': True,
    'format': '%(asctime)s [%(levelname)s] %(message)s',
    'colors': True,
    'min_level': logging.DEBUG
}

logger = SecureLogger(console_config=console_config)
```

## Log Files

The logger creates two main log files:

- **application.log**: Contains all regular log messages
- **security.log**: Contains security alerts for suspicious content

## License

[MIT License](LICENSE)