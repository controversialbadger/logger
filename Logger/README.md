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
    enable_security_scan=True          # Enable/disable security scanning
)
```

## Log Files

The logger creates two main log files:

- **application.log**: Contains all regular log messages
- **security.log**: Contains security alerts for suspicious content

## License

[MIT License](LICENSE)