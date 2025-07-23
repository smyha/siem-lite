"""
Domain entities for SIEM Lite.

This module contains the core domain entities that represent the business objects
in the SIEM Lite system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(Enum):
    """Alert status values."""

    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class UserRole(Enum):
    """User role values."""

    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


@dataclass
class Alert:
    """
    Security alert entity.

    Represents a security alert detected by the SIEM system.
    """

    id: Optional[int]
    alert_type: str
    source_ip: str
    details: str
    timestamp: datetime = field(default_factory=datetime.now)
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.OPEN
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    updated_at: Optional[datetime] = None

    def __str__(self) -> str:
        return f"Alert({self.alert_type}, {self.source_ip}, {self.severity.value})"

    def __repr__(self) -> str:
        return (
            f"Alert(id={self.id}, alert_type='{self.alert_type}', "
            f"source_ip='{self.source_ip}', severity={self.severity.value}, "
            f"status={self.status.value})"
        )

    def acknowledge(self, analyst: str) -> None:
        """Acknowledge the alert."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.assigned_to = analyst

    def resolve(self, analyst: str) -> None:
        """Resolve the alert."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.now()
        if not self.assigned_to:
            self.assigned_to = analyst

    def mark_false_positive(self, analyst: str) -> None:
        """Mark alert as false positive."""
        self.status = AlertStatus.FALSE_POSITIVE
        self.resolved_at = datetime.now()
        if not self.assigned_to:
            self.assigned_to = analyst


@dataclass
class User:
    """
    User entity.

    Represents a user of the SIEM system.
    """

    id: Optional[int]
    username: str
    email: str
    role: UserRole
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    password_hash: Optional[str] = None
    api_key: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"User({self.username}, {self.role.value})"

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, username='{self.username}', "
            f"email='{self.email}', role={self.role.value}, "
            f"is_active={self.is_active})"
        )

    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.now()

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    def can_manage_alerts(self) -> bool:
        """Check if user can manage alerts."""
        return self.role in [UserRole.ADMIN, UserRole.ANALYST]

    def can_view_alerts(self) -> bool:
        """Check if user can view alerts."""
        return self.is_active  # All active users can view alerts


@dataclass
class LogEntry:
    """
    Log entry entity.

    Represents a single log entry processed by the system.
    """

    id: Optional[int]
    timestamp: datetime
    log_type: str
    source_ip: str
    raw_data: str
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    processed_at: Optional[datetime] = None

    def __str__(self) -> str:
        return f"LogEntry({self.log_type}, {self.source_ip}, {self.timestamp})"

    def __repr__(self) -> str:
        return (
            f"LogEntry(id={self.id}, log_type='{self.log_type}', "
            f"source_ip='{self.source_ip}', timestamp={self.timestamp}, "
            f"processed={self.processed})"
        )

    def mark_processed(self) -> None:
        """Mark the log entry as processed."""
        self.processed = True
        self.processed_at = datetime.now()


@dataclass
class Rule:
    """
    Detection rule entity.

    Represents a detection rule used by the SIEM system.
    """

    id: Optional[int]
    name: str
    description: str
    rule_type: str
    conditions: Dict[str, Any]
    alert_type: str
    severity: AlertSeverity
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    def __str__(self) -> str:
        return f"Rule({self.name}, {self.rule_type}, {self.severity.value})"

    def __repr__(self) -> str:
        return (
            f"Rule(id={self.id}, name='{self.name}', "
            f"rule_type='{self.rule_type}', enabled={self.enabled})"
        )

    def update(self, **kwargs) -> None:
        """Update rule properties."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def disable(self) -> None:
        """Disable the rule."""
        self.enabled = False
        self.updated_at = datetime.now()

    def enable(self) -> None:
        """Enable the rule."""
        self.enabled = True
        self.updated_at = datetime.now()


@dataclass
class Dashboard:
    """
    Dashboard entity.

    Represents a dashboard configuration.
    """

    id: Optional[int]
    name: str
    user_id: int
    layout: Dict[str, Any]
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def __str__(self) -> str:
        return f"Dashboard({self.name}, {len(self.widgets)} widgets)"

    def add_widget(self, widget: Dict[str, Any]) -> None:
        """Add a widget to the dashboard."""
        self.widgets.append(widget)
        self.updated_at = datetime.now()

    def remove_widget(self, widget_id: str) -> None:
        """Remove a widget from the dashboard."""
        self.widgets = [w for w in self.widgets if w.get("id") != widget_id]
        self.updated_at = datetime.now()


@dataclass
class SystemMetrics:
    """
    System metrics entity.

    Represents system performance and health metrics.
    """

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: float
    active_alerts: int
    processed_logs: int
    response_time: float

    def __str__(self) -> str:
        return f"SystemMetrics(CPU: {self.cpu_usage}%, Memory: {self.memory_usage}%)"

    def is_healthy(self) -> bool:
        """Check if system metrics indicate healthy state."""
        return (
            self.cpu_usage < 80
            and self.memory_usage < 85
            and self.disk_usage < 90
            and self.response_time < 5.0
        )
