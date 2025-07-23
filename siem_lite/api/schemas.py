"""
Enhanced Pydantic schemas for SIEM Lite API.

This module defines comprehensive data validation models used for API requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
import ipaddress

from pydantic import BaseModel, Field, field_validator, ConfigDict

from siem_lite.domain.entities import AlertSeverity, AlertStatus, UserRole

# Generic type for paginated responses
T = TypeVar("T")


class AlertCreate(BaseModel):
    """Schema for creating a new alert."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alert_type": "SSH Brute-Force Attempt",
                "source_ip": "192.168.1.100",
                "details": "Detected 5 failed login attempts in 60 seconds",
                "severity": "HIGH",
            }
        }
    )

    alert_type: str = Field(
        ..., min_length=1, max_length=100, description="Type of security alert"
    )
    source_ip: str = Field(..., description="Source IP address of the event")
    details: str = Field(..., min_length=1, description="Security event details")
    severity: Optional[AlertSeverity] = Field(
        default=AlertSeverity.MEDIUM, description="Alert severity level"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @field_validator("source_ip")
    @classmethod
    def validate_ip_address(cls, v: str) -> str:
        """Validate IP address format."""
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError("Invalid IP address format")


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""

    model_config = ConfigDict(use_enum_values=True)

    alert_type: Optional[str] = Field(None, min_length=1, max_length=100)
    details: Optional[str] = Field(None, min_length=1)
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    assigned_to: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Alert(BaseModel):
    """Schema for alert responses."""

    id: int
    alert_type: str
    source_ip: str
    details: str
    timestamp: datetime
    severity: AlertSeverity
    status: AlertStatus
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )


class AlertResponse(BaseModel):
    """Enhanced alert response with additional metadata."""

    id: int
    alert_type: str
    source_ip: str
    details: str
    timestamp: datetime
    severity: str
    status: str
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_entity(cls, alert) -> "AlertResponse":
        """Create response from domain entity."""
        return cls(
            id=alert.id,
            alert_type=alert.alert_type,
            source_ip=alert.source_ip,
            details=alert.details,
            timestamp=alert.timestamp,
            severity=(
                alert.severity.value
                if hasattr(alert.severity, "value")
                else str(alert.severity)
            ),
            status=(
                alert.status.value
                if hasattr(alert.status, "value")
                else str(alert.status)
            ),
            assigned_to=alert.assigned_to,
            resolved_at=alert.resolved_at,
            metadata=alert.metadata,
        )


class AlertFilter(BaseModel):
    """Schema for filtering alerts."""

    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    source_ip: Optional[str] = None
    alert_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assigned_to: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    items: List[T]
    total: int
    skip: int
    limit: int
    has_next: Optional[bool] = None
    has_prev: Optional[bool] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.has_next = (self.skip + self.limit) < self.total
        self.has_prev = self.skip > 0


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(
        ..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9._-]+$"
    )
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    role: UserRole
    password: str = Field(..., min_length=8)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "analyst1",
                "email": "analyst@company.com",
                "role": "ANALYST",
                "password": "SecurePassword123!",
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """Schema for user responses."""

    id: int
    username: str
    email: str
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool
    preferences: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Schema for login requests."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Schema for login responses."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class StatsResponse(BaseModel):
    """Schema for statistics responses."""

    total_alerts: int
    alerts_by_severity: Dict[str, int]
    alerts_by_status: Dict[str, int]
    top_source_ips: List[Dict[str, Any]]
    recent_alerts: List[AlertResponse]
    system_health: Dict[str, Any]


class HealthResponse(BaseModel):
    """Schema for health check responses."""

    status: str
    timestamp: datetime
    version: str
    uptime: float
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class LogEntryCreate(BaseModel):
    """Schema for creating log entries."""

    timestamp: datetime
    log_type: str
    source_ip: str
    raw_data: str
    parsed_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class LogEntryResponse(BaseModel):
    """Schema for log entry responses."""

    id: int
    timestamp: datetime
    log_type: str
    source_ip: str
    raw_data: str
    parsed_data: Dict[str, Any]
    processed: bool
    processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RuleCreate(BaseModel):
    """Schema for creating detection rules."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str
    rule_type: str
    conditions: Dict[str, Any]
    alert_type: str
    severity: AlertSeverity
    enabled: bool = True


class RuleUpdate(BaseModel):
    """Schema for updating detection rules."""

    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    alert_type: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    enabled: Optional[bool] = None


class RuleResponse(BaseModel):
    """Schema for detection rule responses."""

    id: int
    name: str
    description: str
    rule_type: str
    conditions: Dict[str, Any]
    alert_type: str
    severity: str
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DashboardCreate(BaseModel):
    """Schema for creating dashboards."""

    name: str = Field(..., min_length=1, max_length=100)
    layout: Dict[str, Any]
    widgets: List[Dict[str, Any]] = Field(default_factory=list)
    is_default: bool = False


class DashboardUpdate(BaseModel):
    """Schema for updating dashboards."""

    name: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    widgets: Optional[List[Dict[str, Any]]] = None
    is_default: Optional[bool] = None


class DashboardResponse(BaseModel):
    """Schema for dashboard responses."""

    id: int
    name: str
    user_id: int
    layout: Dict[str, Any]
    widgets: List[Dict[str, Any]]
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
