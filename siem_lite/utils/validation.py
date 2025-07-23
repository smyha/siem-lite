"""
Data validation utilities for SIEM Lite.
"""

import ipaddress
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .exceptions import ValidationError


def validate_ip_address(ip: str) -> str:
    """
    Validate IP address format.

    Args:
        ip: IP address string to validate

    Returns:
        Validated IP address string

    Raises:
        ValidationError: If IP address is invalid
    """
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        raise ValidationError(f"Invalid IP address: {ip}")


def validate_alert_type(alert_type: str) -> str:
    """
    Validate alert type.

    Args:
        alert_type: Alert type string to validate

    Returns:
        Validated alert type string

    Raises:
        ValidationError: If alert type is invalid
    """
    if not alert_type or len(alert_type.strip()) == 0:
        raise ValidationError("Alert type cannot be empty")

    if len(alert_type) > 100:
        raise ValidationError("Alert type too long (max 100 characters)")

    return alert_type.strip()


def validate_log_entry(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate log entry data.

    Args:
        log_entry: Log entry dictionary to validate

    Returns:
        Validated log entry

    Raises:
        ValidationError: If log entry is invalid
    """
    required_fields = ["timestamp", "log_type"]

    for field in required_fields:
        if field not in log_entry:
            raise ValidationError(f"Missing required field: {field}")

    # Validate IP if present
    if "ip" in log_entry:
        log_entry["ip"] = validate_ip_address(log_entry["ip"])

    # Validate timestamp
    if "timestamp" in log_entry:
        if isinstance(log_entry["timestamp"], str):
            try:
                datetime.fromisoformat(log_entry["timestamp"])
            except ValueError:
                raise ValidationError(
                    f"Invalid timestamp format: {log_entry['timestamp']}"
                )

    return log_entry


def validate_status_code(status_code: Union[int, str]) -> int:
    """
    Validate HTTP status code.

    Args:
        status_code: Status code to validate

    Returns:
        Validated status code as integer

    Raises:
        ValidationError: If status code is invalid
    """
    try:
        code = int(status_code)
        if code < 100 or code >= 600:
            raise ValidationError(f"Invalid HTTP status code: {code}")
        return code
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid status code format: {status_code}")


def validate_username(username: str) -> str:
    """
    Validate username format.

    Args:
        username: Username to validate

    Returns:
        Validated username

    Raises:
        ValidationError: If username is invalid
    """
    if not username or len(username.strip()) == 0:
        raise ValidationError("Username cannot be empty")

    if len(username) > 50:
        raise ValidationError("Username too long (max 50 characters)")

    # Allow alphanumeric, underscore, hyphen, dot
    if not re.match(r"^[a-zA-Z0-9._-]+$", username):
        raise ValidationError("Username contains invalid characters")

    return username.strip()


def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text

    Raises:
        ValidationError: If input is invalid
    """
    if not isinstance(text, str):
        raise ValidationError("Input must be a string")

    if len(text) > max_length:
        raise ValidationError(f"Input too long (max {max_length} characters)")

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', "", text)

    return sanitized.strip()


def validate_email(email: str) -> str:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Validated email address

    Raises:
        ValidationError: If email is invalid
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValidationError(f"Invalid email format: {email}")

    return email.lower().strip()


def validate_port(port: Union[int, str]) -> int:
    """
    Validate port number.

    Args:
        port: Port number to validate

    Returns:
        Validated port number

    Raises:
        ValidationError: If port is invalid
    """
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            raise ValidationError(f"Port must be between 1 and 65535: {port_num}")
        return port_num
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid port format: {port}")


def validate_severity_level(severity: str) -> str:
    """
    Validate alert severity level.

    Args:
        severity: Severity level to validate

    Returns:
        Validated severity level

    Raises:
        ValidationError: If severity is invalid
    """
    valid_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    severity_upper = severity.upper()

    if severity_upper not in valid_levels:
        raise ValidationError(
            f"Invalid severity level: {severity}. Must be one of: {valid_levels}"
        )

    return severity_upper


def validate_file_path(file_path: str) -> str:
    """
    Validate file path format.

    Args:
        file_path: File path to validate

    Returns:
        Validated file path

    Raises:
        ValidationError: If file path is invalid
    """
    if not file_path or len(file_path.strip()) == 0:
        raise ValidationError("File path cannot be empty")

    # Check for potentially dangerous path patterns
    dangerous_patterns = ["../", "..\\", "/etc/", "/root/", "C:\\Windows\\"]
    for pattern in dangerous_patterns:
        if pattern in file_path:
            raise ValidationError(f"Potentially dangerous path: {file_path}")

    return file_path.strip()


def validate_json_data(
    data: Dict[str, Any], required_fields: List[str]
) -> Dict[str, Any]:
    """
    Validate JSON data structure.

    Args:
        data: JSON data to validate
        required_fields: List of required field names

    Returns:
        Validated data

    Raises:
        ValidationError: If data is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError("Data must be a dictionary")

    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    return data


def validate_time_range(start_time: datetime, end_time: datetime) -> None:
    """
    Validate time range.

    Args:
        start_time: Start time
        end_time: End time

    Raises:
        ValidationError: If time range is invalid
    """
    if start_time >= end_time:
        raise ValidationError("Start time must be before end time")

    # Check if time range is reasonable (not more than 1 year)
    max_range = 365 * 24 * 60 * 60  # 1 year in seconds
    if (end_time - start_time).total_seconds() > max_range:
        raise ValidationError("Time range too large (max 1 year)")
