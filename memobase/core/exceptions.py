"""
Core exceptions for MemoBase.
"""


class MemoBaseError(Exception):
    """Base exception for all MemoBase errors."""
    pass


class ParseError(MemoBaseError):
    """Raised when parsing fails."""
    pass


class StorageError(MemoBaseError):
    """Raised when storage operations fail."""
    pass


class IndexError(MemoBaseError):
    """Raised when index operations fail."""
    pass


class GraphError(MemoBaseError):
    """Raised when graph operations fail."""
    pass


class QueryError(MemoBaseError):
    """Raised when query operations fail."""
    pass


class ConfigurationError(MemoBaseError):
    """Raised when configuration is invalid."""
    pass


class ValidationError(MemoBaseError):
    """Raised when data validation fails."""
    pass


class FileNotFoundError(MemoBaseError):
    """Raised when a required file is not found."""
    pass


class PermissionError(MemoBaseError):
    """Raised when permission is denied."""
    pass


class NetworkError(MemoBaseError):
    """Raised when network operations fail."""
    pass


class TimeoutError(MemoBaseError):
    """Raised when operations timeout."""
    pass


class ResourceExhaustedError(MemoBaseError):
    """Raised when system resources are exhausted."""
    pass


class NotImplementedError(MemoBaseError):
    """Raised when a feature is not implemented."""
    pass
