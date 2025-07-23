"""
Pydantic models (schemas) for SIEM Lite API.

This module defines the data validation models used for API requests and responses.
These models are based on Pydantic and ensure that the data exchanged with the API
is well-formed and respects the defined constraints.
"""

import datetime
import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AlertCreate(BaseModel):
    """
    Pydantic model for creating a new alert.

    Attributes:
        alert_type (str): Type of security alert
        source_ip (str): Source IP address of the event
        details (str): Security event details
    """

    alert_type: str = Field(
        ..., min_length=1, max_length=100, description="Type of security alert"
    )
    source_ip: str = Field(..., description="Source IP address of the event")
    details: str = Field(..., min_length=1, description="Security event details")

    @field_validator("source_ip")
    @classmethod
    def validate_source_ip(cls, v: str) -> str:
        """
        Validates that the IP address has a valid format.

        Args:
            v (str): IP address to validate

        Returns:
            str: Validated IP address

        Raises:
            ValueError: If the IP address is not valid
        """
        ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if not re.match(ip_pattern, v):
            raise ValueError("Invalid IP address format")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alert_type": "SSH Brute-Force Attempt",
                "source_ip": "192.168.1.100",
                "details": "Detected 5 failed login attempts in 60 seconds",
            }
        }
    )


class Alert(BaseModel):
    """
    Pydantic model for alert responses.

    Attributes:
        id (int): Unique alert identifier
        alert_type (str): Type of security alert
        source_ip (str): Source IP address
        details (str): Security event details
        timestamp (datetime): Alert date and time
    """

    id: int
    alert_type: str
    source_ip: str
    details: str
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
