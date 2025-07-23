"""
Configuration management for SIEM Lite.

This module provides a centralized configuration system using environment variables
and configuration files with proper validation and type safety.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    try:
        from pydantic import BaseSettings
    except ImportError:
        raise ImportError(
            "Neither pydantic_settings nor pydantic.BaseSettings is available"
        )

from pydantic import ConfigDict, Field, field_validator


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    model_config = ConfigDict(env_prefix="DATABASE_")

    url: str = Field(default="sqlite:///./siem_lite.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)


class APISettings(BaseSettings):
    """API server configuration settings."""

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    reload: bool = Field(default=False)
    log_level: str = Field(default="info")
    workers: int = Field(default=1)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["critical", "error", "warning", "info", "debug", "trace"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.lower()


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    secret_key: str = Field(default="your-secret-key-change-this")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    allowed_hosts: List[str] = Field(default=["*"])
    cors_origins: List[str] = Field(default=["*"])
    rate_limit: int = Field(default=100)

    @field_validator("allowed_hosts", "cors_origins", mode="before")
    @classmethod
    def parse_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    level: str = Field(default="INFO")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_path: Optional[str] = Field(default=None)
    max_file_size: int = Field(default=10_000_000)  # 10MB
    backup_count: int = Field(default=5)


class DetectionSettings(BaseSettings):
    """Detection rules configuration settings."""

    time_window_seconds: int = Field(default=60)
    ssh_threshold: int = Field(default=5)
    web_threshold: int = Field(default=10)
    suspicious_codes: List[int] = Field(default=[400, 401, 403, 404, 500])

    @field_validator("suspicious_codes", mode="before")
    @classmethod
    def parse_codes(cls, v: Union[str, List[int]]) -> List[int]:
        if isinstance(v, str):
            return [int(code.strip()) for code in v.split(",")]
        return v


class Settings(BaseSettings):
    """Main application settings."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Application info
    app_name: str = "SIEM Lite"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False)
    environment: str = Field(default="development")

    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data"
    )
    reports_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "reports"
    )
    plots_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent
        / "reports"
        / "plots"
    )

    # Sub-configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    detection: DetectionSettings = Field(default_factory=DetectionSettings)

    # Feature flags
    enable_dashboard: bool = Field(default=True)
    enable_monitoring: bool = Field(default=True)
    enable_reports: bool = Field(default=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.plots_dir.mkdir(exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Legacy configuration for backward compatibility
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
PLOTS_DIR = REPORTS_DIR / "plots"

# Database configuration
DATABASE_URL = "sqlite:///siem_lite.db"
DATABASE_ECHO = False

# API configuration
API_HOST = "127.0.0.1"
API_PORT = 8000
API_RELOAD = False
API_LOG_LEVEL = "info"

# Log generation configuration
LOG_FILE_PATH = DATA_DIR / "simulated.log"
DEFAULT_LOG_COUNT = 500
ATTACK_PROBABILITY = 0.15  # 15% of logs will be attack patterns
NORMAL_FAILURE_RATE = 0.1  # 10% failures in normal traffic

# Detection rules configuration
TIME_WINDOW_SECONDS = 60
SSH_FAILED_LOGIN_THRESHOLD = 5
WEB_ERROR_THRESHOLD = 10
SUSPICIOUS_STATUS_CODES = [400, 401, 403, 404, 500]

# Dashboard configuration
DASHBOARD_REFRESH_INTERVAL = 30  # seconds
DASHBOARD_HISTORY_SIZE = 1000
DASHBOARD_LOG_FILE = "dashboard_history.json"

# Monitoring configuration
MONITORING_INTERVAL = 5  # minutes
MONITORING_TIMEOUT = 10  # seconds for API requests

# Reporting configuration
REPORT_LANGUAGE = "en"  # en, es, fr, de, pt
REPORT_FORMAT = "latex"  # latex, json
REPORT_INCLUDE_PLOTS = True
REPORT_INCLUDE_STATISTICS = True

# Internationalization
DEFAULT_LANGUAGE = "en"
AVAILABLE_LANGUAGES = ["en", "es", "fr", "de", "pt"]

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Security configuration
ALLOWED_HOSTS = ["*"]  # In production, specify specific domains
CORS_ORIGINS = ["*"]  # In production, specify specific origins
API_RATE_LIMIT = 100  # requests per minute

# Data pools for log generation
IP_ADDRESSES = [
    "192.168.1.101",
    "10.0.0.5",
    "172.16.31.45",
    "203.0.113.78",
    "198.51.100.22",
    "99.88.77.66",  # Attacker IP
]

USERNAMES = ["admin", "user", "guest", "dev", "root", "testuser"]

WEB_PATHS = [
    "/login",
    "/dashboard",
    "/api/v1/users",
    "/static/style.css",
    "/admin",
    "/uploads/img.png",
    "/.git/config",
    "/wp-admin",
    "/phpmyadmin",
    "/.env",
    "/config.php",
]

WEB_METHODS = ["GET", "POST", "PUT", "DELETE"]

NORMAL_STATUS_CODES = [200, 201, 301, 302]
SUSPICIOUS_STATUS_CODES_CONFIG = [400, 401, 403, 404, 500]

# System configuration
SSHD_PROCESS_ID = 1234
HOSTNAME = "webserver-01"

# Alert types and severity mapping
ALERT_TYPES = {
    "SSH Brute-Force Attempt": "HIGH",
    "Suspicious Web Activity": "MEDIUM",
    "Failed Login": "LOW",
    "Unauthorized Access": "HIGH",
    "Web Attack": "MEDIUM",
}

# Export configuration
EXPORT_FORMATS = ["json", "csv"]
EXPORT_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Testing configuration
TEST_TIMEOUT = 30  # seconds
TEST_LOG_COUNT = 100

# Development configuration
DEBUG_MODE = False
VERBOSE_OUTPUT = False
SAVE_INTERMEDIATE_RESULTS = False

# Performance configuration
BATCH_SIZE = 1000  # Process logs in batches
MAX_CONCURRENT_REQUESTS = 10
CACHE_TIMEOUT = 300  # seconds

# Notification configuration (for future use)
NOTIFICATIONS_ENABLED = False
EMAIL_NOTIFICATIONS = False
WEBHOOK_NOTIFICATIONS = False

# Custom rules configuration
CUSTOM_RULES_FILE = DATA_DIR / "custom_rules.json"
CUSTOM_RULES_ENABLED = True

# Backup configuration
BACKUP_ENABLED = True
BACKUP_INTERVAL = 24  # hours
BACKUP_RETENTION = 7  # days

# Validation configuration
VALIDATE_INPUT_DATA = True
VALIDATE_OUTPUT_DATA = True
SANITIZE_USER_INPUT = True

# Error handling configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds
GRACEFUL_SHUTDOWN_TIMEOUT = 30  # seconds

# Feature flags
FEATURE_DASHBOARD_SCROLLING = True
FEATURE_REAL_TIME_MONITORING = True
FEATURE_MULTI_LANGUAGE = True
FEATURE_EXPORT_DATA = True
FEATURE_GENERATE_REPORTS = True
FEATURE_CUSTOM_RULES = True
FEATURE_API_DOCUMENTATION = True


# Environment-specific overrides
def get_config() -> Dict[str, Any]:
    """
    Get configuration based on environment.

    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    config = {
        "database": {"url": DATABASE_URL, "echo": DATABASE_ECHO},
        "api": {
            "host": API_HOST,
            "port": API_PORT,
            "reload": API_RELOAD,
            "log_level": API_LOG_LEVEL,
        },
        "logs": {
            "file_path": str(LOG_FILE_PATH),
            "default_count": DEFAULT_LOG_COUNT,
            "attack_probability": ATTACK_PROBABILITY,
            "normal_failure_rate": NORMAL_FAILURE_RATE,
        },
        "detection": {
            "time_window": TIME_WINDOW_SECONDS,
            "ssh_threshold": SSH_FAILED_LOGIN_THRESHOLD,
            "web_threshold": WEB_ERROR_THRESHOLD,
            "suspicious_codes": SUSPICIOUS_STATUS_CODES,
        },
        "dashboard": {
            "refresh_interval": DASHBOARD_REFRESH_INTERVAL,
            "history_size": DASHBOARD_HISTORY_SIZE,
            "log_file": DASHBOARD_LOG_FILE,
        },
        "monitoring": {"interval": MONITORING_INTERVAL, "timeout": MONITORING_TIMEOUT},
        "reporting": {
            "language": REPORT_LANGUAGE,
            "format": REPORT_FORMAT,
            "include_plots": REPORT_INCLUDE_PLOTS,
            "include_statistics": REPORT_INCLUDE_STATISTICS,
        },
        "i18n": {
            "default_language": DEFAULT_LANGUAGE,
            "available_languages": AVAILABLE_LANGUAGES,
        },
        "logging": {"level": LOG_LEVEL, "format": LOG_FORMAT},
        "security": {
            "allowed_hosts": ALLOWED_HOSTS,
            "cors_origins": CORS_ORIGINS,
            "rate_limit": API_RATE_LIMIT,
        },
        "data_pools": {
            "ip_addresses": IP_ADDRESSES,
            "usernames": USERNAMES,
            "web_paths": WEB_PATHS,
            "web_methods": WEB_METHODS,
            "normal_status_codes": NORMAL_STATUS_CODES,
            "suspicious_status_codes": SUSPICIOUS_STATUS_CODES_CONFIG,
        },
        "system": {"sshd_process_id": SSHD_PROCESS_ID, "hostname": HOSTNAME},
        "alerts": {"types": ALERT_TYPES},
        "export": {
            "formats": EXPORT_FORMATS,
            "timestamp_format": EXPORT_TIMESTAMP_FORMAT,
        },
        "testing": {"timeout": TEST_TIMEOUT, "log_count": TEST_LOG_COUNT},
        "development": {
            "debug_mode": DEBUG_MODE,
            "verbose_output": VERBOSE_OUTPUT,
            "save_intermediate_results": SAVE_INTERMEDIATE_RESULTS,
        },
        "performance": {
            "batch_size": BATCH_SIZE,
            "max_concurrent_requests": MAX_CONCURRENT_REQUESTS,
            "cache_timeout": CACHE_TIMEOUT,
        },
        "notifications": {
            "enabled": NOTIFICATIONS_ENABLED,
            "email": EMAIL_NOTIFICATIONS,
            "webhook": WEBHOOK_NOTIFICATIONS,
        },
        "custom_rules": {
            "file": str(CUSTOM_RULES_FILE),
            "enabled": CUSTOM_RULES_ENABLED,
        },
        "backup": {
            "enabled": BACKUP_ENABLED,
            "interval": BACKUP_INTERVAL,
            "retention": BACKUP_RETENTION,
        },
        "validation": {
            "input_data": VALIDATE_INPUT_DATA,
            "output_data": VALIDATE_OUTPUT_DATA,
            "sanitize_user_input": SANITIZE_USER_INPUT,
        },
        "error_handling": {
            "max_retry_attempts": MAX_RETRY_ATTEMPTS,
            "retry_delay": RETRY_DELAY,
            "graceful_shutdown_timeout": GRACEFUL_SHUTDOWN_TIMEOUT,
        },
        "features": {
            "dashboard_scrolling": FEATURE_DASHBOARD_SCROLLING,
            "real_time_monitoring": FEATURE_REAL_TIME_MONITORING,
            "multi_language": FEATURE_MULTI_LANGUAGE,
            "export_data": FEATURE_EXPORT_DATA,
            "generate_reports": FEATURE_GENERATE_REPORTS,
            "custom_rules": FEATURE_CUSTOM_RULES,
            "api_documentation": FEATURE_API_DOCUMENTATION,
        },
    }

    # Environment-specific overrides
    if os.getenv("SIEM_DEBUG"):
        config["development"]["debug_mode"] = True
        config["development"]["verbose_output"] = True

    if os.getenv("SIEM_API_PORT"):
        config["api"]["port"] = int(os.getenv("SIEM_API_PORT"))

    if os.getenv("SIEM_LOG_LEVEL"):
        config["logging"]["level"] = os.getenv("SIEM_LOG_LEVEL")

    return config


# Convenience functions
def get_database_url() -> str:
    """Get database URL from configuration."""
    return get_config()["database"]["url"]


def get_api_config() -> Dict[str, Any]:
    """Get API configuration."""
    return get_config()["api"]


def get_detection_config() -> Dict[str, Any]:
    """Get detection rules configuration."""
    return get_config()["detection"]


def get_dashboard_config() -> Dict[str, Any]:
    """Get dashboard configuration."""
    return get_config()["dashboard"]


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    return get_config()["logging"]


def get_security_config() -> Dict[str, Any]:
    """Get security configuration."""
    return get_config()["security"]


def get_features_config() -> Dict[str, Any]:
    """Get feature flags configuration."""
    return get_config()["features"]


def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled."""
    features = get_features_config()
    return features.get(feature_name, False)


# Convenience functions for backward compatibility
def get_config() -> Dict[str, Any]:
    """Get configuration as dictionary for backward compatibility."""
    settings = get_settings()
    return {
        "database": {
            "url": settings.database.url,
            "echo": settings.database.echo,
        },
        "api": {
            "host": settings.api.host,
            "port": settings.api.port,
            "reload": settings.api.reload,
            "log_level": settings.api.log_level,
        },
        "security": {
            "allowed_hosts": settings.security.allowed_hosts,
            "cors_origins": settings.security.cors_origins,
            "rate_limit": settings.security.rate_limit,
        },
        "detection": {
            "time_window": settings.detection.time_window_seconds,
            "ssh_threshold": settings.detection.ssh_threshold,
            "web_threshold": settings.detection.web_threshold,
            "suspicious_codes": settings.detection.suspicious_codes,
        },
    }


def get_database_url() -> str:
    """Get database URL from configuration."""
    return get_settings().database.url


def get_api_config() -> Dict[str, Any]:
    """Get API configuration."""
    settings = get_settings()
    return {
        "host": settings.api.host,
        "port": settings.api.port,
        "reload": settings.api.reload,
        "log_level": settings.api.log_level,
    }
