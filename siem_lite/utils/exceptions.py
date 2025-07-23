"""
Custom exceptions for SIEM Lite.
"""

from typing import Any, Dict, Optional


class SIEMLiteException(Exception):
    """Base exception for SIEM Lite application."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ValidationError(SIEMLiteException):
    """Raised when data validation fails."""

    pass


class DatabaseError(SIEMLiteException):
    """Raised when database operations fail."""

    pass


class ConfigurationError(SIEMLiteException):
    """Raised when configuration is invalid."""

    pass


class APIError(SIEMLiteException):
    """Raised when API operations fail."""

    pass


class ProcessingError(SIEMLiteException):
    """Raised when log processing fails."""

    pass


class AuthenticationError(SIEMLiteException):
    """Raised when authentication fails."""

    pass


class AuthorizationError(SIEMLiteException):
    """Raised when authorization fails."""

    pass


class ParsingError(SIEMLiteException):
    """Raised when log parsing fails."""

    pass


class ReportGenerationError(SIEMLiteException):
    """Raised when report generation fails."""

    pass


class MonitoringError(SIEMLiteException):
    """Raised when monitoring operations fail."""

    pass
