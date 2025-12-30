"""
Debug Logging Module for AEPGP Context Menu

This module provides debug logging functionality to help trace issues
when using the AEPGP context menu tools.
"""

import os
import sys
import datetime
import traceback
from pathlib import Path


class DebugLogger:
    """Handles debug logging for AEPGP operations"""

    def __init__(self, log_file=None):
        """
        Initialize the debug logger.

        Args:
            log_file: Path to log file. If None, uses default location.
        """
        if log_file is None:
            # Log to user's temp directory
            temp_dir = os.environ.get('TEMP', os.environ.get('TMP', 'C:\\Temp'))
            log_file = os.path.join(temp_dir, 'aepgp_debug.log')

        self.log_file = log_file
        self.enabled = True

    def log(self, level, message, exception=None):
        """
        Write a log entry.

        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            exception: Optional exception object to log
        """
        if not self.enabled:
            return

        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"[{timestamp}] [{level}]\n")
                f.write(f"{message}\n")

                if exception:
                    f.write(f"\nException Details:\n")
                    f.write(f"Type: {type(exception).__name__}\n")
                    f.write(f"Message: {str(exception)}\n")
                    f.write(f"\nTraceback:\n")
                    f.write(traceback.format_exc())

                f.write(f"{'='*80}\n")

        except Exception as e:
            # If logging fails, don't crash the main operation
            print(f"Debug logging failed: {e}")

    def info(self, message):
        """Log an info message"""
        self.log('INFO', message)

    def warning(self, message):
        """Log a warning message"""
        self.log('WARNING', message)

    def error(self, message, exception=None):
        """Log an error message"""
        self.log('ERROR', message, exception)

    def debug(self, message):
        """Log a debug message"""
        self.log('DEBUG', message)

    def log_operation_start(self, operation, file_path):
        """Log the start of an operation"""
        self.info(f"Starting {operation} operation\nFile: {file_path}")

    def log_operation_end(self, operation, success, error_msg=None):
        """Log the end of an operation"""
        if success:
            self.info(f"{operation} operation completed successfully")
        else:
            self.error(f"{operation} operation failed: {error_msg}")

    def log_card_detection(self, reader_count, card_found, atr=None):
        """Log card detection details"""
        msg = f"Card Detection:\n"
        msg += f"  Readers found: {reader_count}\n"
        msg += f"  Card detected: {card_found}\n"
        if atr:
            msg += f"  ATR: {atr}"
        self.debug(msg)

    def log_system_info(self):
        """Log system information"""
        msg = "System Information:\n"
        msg += f"  Python: {sys.version}\n"
        msg += f"  Platform: {sys.platform}\n"
        msg += f"  Working Dir: {os.getcwd()}\n"

        try:
            from smartcard.System import readers
            reader_list = readers()
            msg += f"  Smart Card Readers: {len(reader_list)}\n"
            for i, reader in enumerate(reader_list):
                msg += f"    {i+1}. {reader}\n"
        except Exception as e:
            msg += f"  Smart Card Readers: Error getting readers - {e}\n"

        self.debug(msg)

    def clear_old_logs(self, days_to_keep=7):
        """
        Clear log entries older than specified days.

        Args:
            days_to_keep: Number of days of logs to keep
        """
        try:
            if not os.path.exists(self.log_file):
                return

            # For simplicity, just truncate if file is too large (>5MB)
            file_size = os.path.getsize(self.log_file)
            if file_size > 5 * 1024 * 1024:  # 5MB
                # Create backup
                backup = self.log_file + '.old'
                if os.path.exists(backup):
                    os.remove(backup)
                os.rename(self.log_file, backup)
                self.info("Log file rotated (exceeded 5MB)")

        except Exception as e:
            print(f"Failed to rotate log: {e}")


# Global logger instance
_logger = None


def get_logger():
    """Get the global debug logger instance"""
    global _logger
    if _logger is None:
        _logger = DebugLogger()
    return _logger


def init_logger(log_file=None):
    """
    Initialize the global logger with a specific log file.

    Args:
        log_file: Path to log file
    """
    global _logger
    _logger = DebugLogger(log_file)
    return _logger


if __name__ == "__main__":
    # Test the logger
    logger = get_logger()
    logger.log_system_info()
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")

    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.error("Caught test exception", e)

    print(f"Log file created at: {logger.log_file}")
