"""
Structured logging configuration for SIEM Lite.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import structlog
    from rich.console import Console
    from rich.logging import RichHandler

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    structlog = None

from .config import get_settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    # Configure handlers
    handlers = []

    if RICH_AVAILABLE:
        # Console handler with Rich
        console = Console(stderr=True)
        rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=True,
            rich_tracebacks=True,
        )
        rich_handler.setLevel(getattr(logging, settings.logging.level.upper()))
        handlers.append(rich_handler)
    else:
        # Fallback to standard console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(getattr(logging, settings.logging.level.upper()))
        console_formatter = logging.Formatter(settings.logging.format)
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)

    # File handler if configured
    if settings.logging.file_path:
        file_path = Path(settings.logging.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=settings.logging.max_file_size,
            backupCount=settings.logging.backup_count,
        )
        file_handler.setLevel(getattr(logging, settings.logging.level.upper()))
        file_formatter = logging.Formatter(settings.logging.format)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.logging.level.upper()),
        handlers=handlers,
        format=settings.logging.format,
    )

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Configure structlog if available
    if structlog is not None:
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(fmt="ISO"),
                (
                    structlog.dev.ConsoleRenderer()
                    if settings.debug
                    else structlog.processors.JSONRenderer()
                ),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, settings.logging.level.upper())
            ),
            logger_factory=structlog.WriteLoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    if structlog is not None:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


class SecurityLogger:
    """Security-focused logger for sensitive operations."""

    def __init__(self, name: str):
        self.logger = get_logger(f"security.{name}")

    def log_authentication_attempt(self, username: str, ip: str, success: bool):
        """Log authentication attempt."""
        self.logger.info(
            "Authentication attempt",
            username=username,
            ip=ip,
            success=success,
            event_type="authentication",
        )

    def log_authorization_failure(self, username: str, resource: str, ip: str):
        """Log authorization failure."""
        self.logger.warning(
            "Authorization failure",
            username=username,
            resource=resource,
            ip=ip,
            event_type="authorization",
        )

    def log_suspicious_activity(self, ip: str, activity: str, details: Dict[str, Any]):
        """Log suspicious activity."""
        self.logger.warning(
            "Suspicious activity detected",
            ip=ip,
            activity=activity,
            details=details,
            event_type="suspicious",
        )

    def log_alert_generation(self, alert_type: str, source_ip: str, severity: str):
        """Log alert generation."""
        self.logger.info(
            "Alert generated",
            alert_type=alert_type,
            source_ip=source_ip,
            severity=severity,
            event_type="alert",
        )


class AuditLogger:
    """Audit logger for tracking system changes."""

    def __init__(self, name: str):
        self.logger = get_logger(f"audit.{name}")

    def log_configuration_change(
        self, user: str, setting: str, old_value: Any, new_value: Any
    ):
        """Log configuration change."""
        self.logger.info(
            "Configuration changed",
            user=user,
            setting=setting,
            old_value=str(old_value),
            new_value=str(new_value),
            event_type="config_change",
        )

    def log_data_access(self, user: str, resource: str, action: str):
        """Log data access."""
        self.logger.info(
            "Data accessed",
            user=user,
            resource=resource,
            action=action,
            event_type="data_access",
        )

    def log_system_event(self, event: str, details: Dict[str, Any]):
        """Log system event."""
        self.logger.info(
            "System event", event=event, details=details, event_type="system"
        )


class PerformanceLogger:
    """Performance logger for monitoring system performance."""

    def __init__(self, name: str):
        self.logger = get_logger(f"performance.{name}")

    def log_operation_time(
        self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None
    ):
        """Log operation execution time."""
        self.logger.info(
            "Operation completed",
            operation=operation,
            duration_seconds=duration,
            details=details or {},
            event_type="performance",
        )

    def log_resource_usage(
        self, cpu_percent: float, memory_percent: float, disk_usage: float
    ):
        """Log resource usage."""
        self.logger.debug(
            "Resource usage",
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage=disk_usage,
            event_type="resource_usage",
        )
