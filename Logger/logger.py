import os
import re
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

class SecureLogger:
    """
    A secure logging system that can detect and handle potentially malicious content.
    """
    
    # Patterns that might indicate malicious content
    SUSPICIOUS_PATTERNS = [
        r'keylog(?:ger)?',
        r'(?:password|credential).*(?:steal|capture)',
        r'(?:registry|regedit).*(?:modify|change)',
        r'(?:startup|autorun)',
        r'(?:antivirus|defender).*(?:bypass|avoid|evade)',
        r'smtplib',
        r'obfuscat(?:e|ion)',
        r'sandbox.*detect',
        r'(?:malware|virus|trojan|backdoor)',
    ]
    
    def __init__(self, log_dir: str = "logs", 
                 log_level: int = logging.INFO,
                 max_log_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_security_scan: bool = True):
        """
        Initialize the secure logger.
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level
            max_log_size: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            enable_security_scan: Whether to scan logs for suspicious content
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        self.enable_security_scan = enable_security_scan
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("SecureLogger")
        self.logger.setLevel(log_level)
        
        # Create handlers
        self._setup_handlers()
        
        # Compile suspicious patterns
        self.suspicious_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SUSPICIOUS_PATTERNS]
        
        # Security log for tracking suspicious activities
        self.security_logger = logging.getLogger("SecurityLogger")
        self.security_logger.setLevel(logging.WARNING)
        
        # Set up security logger handler
        security_handler = logging.FileHandler(os.path.join(log_dir, "security.log"))
        security_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        security_handler.setFormatter(security_formatter)
        self.security_logger.addHandler(security_handler)
        
    def _setup_handlers(self):
        """Set up logging handlers with rotation"""
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        # Create file handler for regular logs
        log_file = os.path.join(self.log_dir, "application.log")
        file_handler = logging.FileHandler(log_file)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _check_for_suspicious_content(self, message: str) -> List[str]:
        """
        Check if the log message contains suspicious patterns.
        
        Args:
            message: The log message to check
            
        Returns:
            List of matched suspicious patterns
        """
        if not self.enable_security_scan:
            return []
            
        matches = []
        for pattern in self.suspicious_patterns:
            if pattern.search(message):
                matches.append(pattern.pattern)
                
        return matches
    
    def _sanitize_log_message(self, message: str) -> str:
        """
        Sanitize log message to prevent log injection attacks.
        
        Args:
            message: The log message to sanitize
            
        Returns:
            Sanitized log message
        """
        # Replace newlines with spaces to prevent log injection
        message = message.replace('\n', ' ').replace('\r', ' ')
        
        # Limit message length
        if len(message) > 10000:  # Arbitrary limit to prevent DoS
            message = message[:10000] + "... (message truncated)"
            
        return message
    
    def log(self, level: int, message: str, **kwargs) -> None:
        """
        Log a message with the specified level.
        
        Args:
            level: Logging level
            message: Message to log
            **kwargs: Additional data to include in the log
        """
        # Sanitize the message
        sanitized_message = self._sanitize_log_message(message)
        
        # Check for suspicious content
        suspicious_matches = self._check_for_suspicious_content(sanitized_message)
        
        # If suspicious content is found, log it to security log
        if suspicious_matches:
            self.security_logger.warning(
                f"Suspicious content detected in log message: {sanitized_message}. "
                f"Matched patterns: {', '.join(suspicious_matches)}"
            )
            
            # Add security metadata to the log
            kwargs['security_alert'] = True
            kwargs['matched_patterns'] = suspicious_matches
        
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': sanitized_message,
            'metadata': kwargs
        }
        
        # Log the message
        self.logger.log(level, json.dumps(log_entry))
    
    def info(self, message: str, **kwargs) -> None:
        """Log an info message"""
        self.log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message"""
        self.log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log an error message"""
        self.log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message"""
        self.log(logging.CRITICAL, message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message"""
        self.log(logging.DEBUG, message, **kwargs)
        
    def log_file_content(self, file_path: str, log_level: int = logging.INFO) -> bool:
        """
        Safely log the content of a file with security checks.
        
        Args:
            file_path: Path to the file to log
            log_level: Logging level to use
            
        Returns:
            True if file was logged successfully, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.isfile(file_path):
                self.error(f"File not found: {file_path}")
                return False
                
            # Check file size to prevent memory issues
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:  # 1MB limit
                self.warning(f"File too large to log: {file_path} ({file_size} bytes)")
                return False
                
            # Calculate file hash for integrity checking
            file_hash = self._calculate_file_hash(file_path)
                
            # Read and log file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            # Check for suspicious content
            suspicious_matches = self._check_for_suspicious_content(content)
            
            if suspicious_matches:
                self.warning(
                    f"Suspicious content detected in file: {file_path}. "
                    f"Matched patterns: {', '.join(suspicious_matches)}",
                    file_hash=file_hash,
                    file_size=file_size
                )
            
            # Log the file content
            self.log(
                log_level,
                f"Content of file {file_path}",
                file_hash=file_hash,
                file_size=file_size,
                suspicious_content_detected=bool(suspicious_matches)
            )
            
            return True
            
        except Exception as e:
            self.error(f"Error logging file content: {str(e)}", file_path=file_path)
            return False
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()