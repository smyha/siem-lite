"""
Custom exceptions for SIEM Lite.

This module provides a comprehensive set of custom exceptions for different
components of the SIEM Lite system with proper error codes and HTTP status mapping.
"""

from typing import Any, Dict, Optional
from fastapi import status


class SIEMException(Exception):
    """Base exception for SIEM Lite application with HTTP status support."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.status_code = status_code
        self.details = details or {}


class ValidationError(SIEMException):
    """Raised when data validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message, 
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs
        )
        if field:
            self.details["field"] = field


class DatabaseError(SIEMException):
    """Raised when database operations fail."""

    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="DATABASE_ERROR", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            **kwargs
        )
        if operation:
            self.details["operation"] = operation


class ConfigurationError(SIEMException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, setting: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            **kwargs
        )
        if setting:
            self.details["setting"] = setting


class APIError(SIEMException):
    """Raised when API operations fail."""

    def __init__(self, message: str, endpoint: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="API_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            **kwargs
        )
        if endpoint:
            self.details["endpoint"] = endpoint


class AlertNotFoundError(SIEMException):
    """Raised when an alert is not found."""

    def __init__(self, alert_id: int, **kwargs):
        super().__init__(
            f"Alert with ID {alert_id} not found",
            error_code="ALERT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            **kwargs
        )
        self.details["alert_id"] = alert_id


class ProcessingError(SIEMException):
    """Raised when log processing fails."""

    def __init__(self, message: str, log_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="PROCESSING_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            **kwargs
        )
        if log_type:
            self.details["log_type"] = log_type


class AuthenticationError(SIEMException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )


class AuthorizationError(SIEMException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Access denied", resource: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            **kwargs
        )
        if resource:
            self.details["resource"] = resource


class ParsingError(SIEMException):
    """Raised when log parsing fails."""

    def __init__(self, message: str, log_format: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="PARSING_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs
        )
        if log_format:
            self.details["log_format"] = log_format


class ReportGenerationError(SIEMException):
    """Raised when report generation fails."""

    def __init__(self, message: str, report_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="REPORT_GENERATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            **kwargs
        )
        if report_type:
            self.details["report_type"] = report_type


class MonitoringError(SIEMException):
    """Raised when monitoring operations fail."""

    def __init__(self, message: str, metric: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="MONITORING_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            **kwargs
        )
        if metric:
            self.details["metric"] = metric


class RateLimitError(SIEMException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(
            message,
            error_code="RATE_LIMIT_ERROR",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            **kwargs
        )


class ServiceUnavailableError(SIEMException):
    """Raised when a service is unavailable."""

    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            **kwargs
        )
        if service:
            self.details["service"] = service


# Alias for backward compatibility
SIEMLiteException = SIEMException
