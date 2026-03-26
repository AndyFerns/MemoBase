"""
Logger for MemoBase.

Supports:
- verbosity levels
- debug mode
- CLI + TUI compatibility
"""

from __future__ import annotations

import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Optional


class LogLevel(Enum):
    """Log level enumeration."""
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    DEBUG = 3


class Logger:
    """MemoBase logger with verbosity support."""
    
    def __init__(self, name: str = "memobase", level: LogLevel = LogLevel.NORMAL) -> None:
        """Initialize logger.
        
        Args:
            name: Logger name
            level: Initial log level
        """
        self.name = name
        self.level = level
        
        # Create Python logger
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Add console handler
        self._console_handler = logging.StreamHandler(sys.stderr)
        self._console_handler.setLevel(self._get_python_level(level))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._console_handler.setFormatter(formatter)
        self._logger.addHandler(self._console_handler)
        
        # File handler (optional)
        self._file_handler: Optional[logging.FileHandler] = None
    
    def set_level(self, level: LogLevel) -> None:
        """Set log level.
        
        Args:
            level: New log level
        """
        self.level = level
        self._console_handler.setLevel(self._get_python_level(level))
    
    def enable_file_logging(self, log_path: Path) -> None:
        """Enable logging to file.
        
        Args:
            log_path: Path to log file
        """
        if self._file_handler:
            self._logger.removeHandler(self._file_handler)
        
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._file_handler = logging.FileHandler(log_path)
        self._file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._file_handler.setFormatter(formatter)
        self._logger.addHandler(self._file_handler)
    
    def _get_python_level(self, level: LogLevel) -> int:
        """Convert LogLevel to Python logging level.
        
        Args:
            level: LogLevel value
            
        Returns:
            Python logging level
        """
        level_map = {
            LogLevel.QUIET: logging.ERROR,
            LogLevel.NORMAL: logging.WARNING,
            LogLevel.VERBOSE: logging.INFO,
            LogLevel.DEBUG: logging.DEBUG,
        }
        return level_map.get(level, logging.INFO)
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged at current level.
        
        Args:
            level: Message level
            
        Returns:
            True if should log
        """
        return level.value <= self.level.value
    
    def debug(self, message: str) -> None:
        """Log debug message.
        
        Args:
            message: Message to log
        """
        if self._should_log(LogLevel.DEBUG):
            self._logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message.
        
        Args:
            message: Message to log
        """
        if self._should_log(LogLevel.VERBOSE):
            self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message.
        
        Args:
            message: Message to log
        """
        if self._should_log(LogLevel.NORMAL):
            self._logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message.
        
        Args:
            message: Message to log
        """
        if self._should_log(LogLevel.QUIET):
            self._logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message.
        
        Args:
            message: Message to log
        """
        self._logger.critical(message)
    
    def log(self, level: LogLevel, message: str) -> None:
        """Log message at specified level.
        
        Args:
            level: Log level
            message: Message to log
        """
        if self._should_log(level):
            if level == LogLevel.DEBUG:
                self._logger.debug(message)
            elif level == LogLevel.VERBOSE:
                self._logger.info(message)
            elif level == LogLevel.NORMAL:
                self._logger.warning(message)
            elif level == LogLevel.QUIET:
                self._logger.error(message)


class TUILogger(Logger):
    """Logger for TUI with notification support."""
    
    def __init__(self, app, name: str = "memobase", level: LogLevel = LogLevel.NORMAL) -> None:
        """Initialize TUI logger.
        
        Args:
            app: Textual app instance
            name: Logger name
            level: Initial log level
        """
        super().__init__(name, level)
        self.app = app
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        super().debug(message)
        if self.app and self.level.value >= LogLevel.DEBUG.value:
            self.app.notify(message, severity="information")
    
    def info(self, message: str) -> None:
        """Log info message."""
        super().info(message)
        if self.app and self.level.value >= LogLevel.VERBOSE.value:
            self.app.notify(message, severity="information")
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        super().warning(message)
        if self.app:
            self.app.notify(message, severity="warning")
    
    def error(self, message: str) -> None:
        """Log error message."""
        super().error(message)
        if self.app:
            self.app.notify(message, severity="error")


# Global logger instance
_global_logger: Optional[Logger] = None


def get_logger() -> Logger:
    """Get global logger instance.
    
    Returns:
        Logger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger()
    return _global_logger


def set_global_logger(logger: Logger) -> None:
    """Set global logger instance.
    
    Args:
        logger: Logger to set
    """
    global _global_logger
    _global_logger = logger
