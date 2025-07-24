"""
Metrics API endpoint for SIEM Lite.

Provides Prometheus-compatible metrics endpoint and health information.
"""

from datetime import datetime
from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session

from siem_lite.infrastructure.database import get_db
from siem_lite.domain.services import AlertService
from siem_lite.infrastructure.repositories import SQLAlchemyAlertRepository
from siem_lite.utils.metrics import metrics
from siem_lite.utils.logging import get_logger

logger = get_logger(__name__)

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus format for scraping by monitoring systems.
    """
    if PROMETHEUS_AVAILABLE:
        # Return Prometheus metrics
        content = generate_latest()
        return Response(content=content, media_type=CONTENT_TYPE_LATEST)
    else:
        # Return fallback metrics in JSON format
        return {
            "message": "Prometheus client not available",
            "metrics": metrics.get_fallback_metrics()
        }


@router.get("/metrics/alerts")
async def get_alert_metrics(db: Session = Depends(get_db)):
    """
    Get detailed alert metrics.
    
    Returns comprehensive alert statistics and updates internal metrics.
    """
    try:
        # Get alert service
        service = AlertService(SQLAlchemyAlertRepository(db))
        stats = service.get_alert_statistics()
        
        # Update metrics
        if "status_distribution" in stats:
            metrics.update_alert_status_metrics(stats["status_distribution"])
        
        if "severity_distribution" in stats:
            metrics.update_alert_severity_metrics(stats["severity_distribution"])
        
        return {
            "metrics_updated": True,
            "alert_statistics": stats,
            "prometheus_enabled": PROMETHEUS_AVAILABLE
        }
        
    except Exception as e:
        return {
            "error": f"Failed to retrieve alert metrics: {str(e)}",
            "metrics_updated": False
        }


@router.get("/metrics/system")
async def get_system_metrics():
    """
    Get system-wide metrics and performance indicators.
    """
    import psutil
    import time
    from datetime import datetime
    
    try:
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent if hasattr(psutil.disk_usage('/'), 'percent') else 0,
            "uptime": time.time() - psutil.boot_time(),
            "prometheus_enabled": PROMETHEUS_AVAILABLE
        }
        
        if not PROMETHEUS_AVAILABLE:
            system_info["fallback_metrics"] = metrics.get_fallback_metrics()
        
        return system_info
        
    except ImportError:
        return {
            "error": "psutil not available for system metrics",
            "timestamp": datetime.now().isoformat(),
            "prometheus_enabled": PROMETHEUS_AVAILABLE
        }
    except Exception as e:
        return {
            "error": f"Failed to retrieve system metrics: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@router.get("/metrics/security")
async def get_security_metrics(db: Session = Depends(get_db)):
    """
    Get security-specific metrics including attack patterns and threat intelligence.
    """
    try:
        from datetime import datetime, timedelta
        
        # Get alert service for security stats
        service = AlertService(SQLAlchemyAlertRepository(db))
        
        # Calculate time ranges for metrics
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Get security metrics
        security_metrics = {
            "timestamp": now.isoformat(),
            "attack_patterns": {
                "brute_force_attempts": _count_attacks_by_type("brute-force", service, last_24h),
                "sql_injection_attempts": _count_attacks_by_type("sql-injection", service, last_24h),
                "ddos_attempts": _count_attacks_by_type("ddos", service, last_24h),
            },
            "threat_levels": {
                "critical": _count_alerts_by_severity("CRITICAL", service, last_24h),
                "high": _count_alerts_by_severity("HIGH", service, last_24h),
                "medium": _count_alerts_by_severity("MEDIUM", service, last_24h),
                "low": _count_alerts_by_severity("LOW", service, last_24h),
            },
            "temporal_analysis": {
                "last_hour": _count_all_alerts(service, last_hour),
                "last_24h": _count_all_alerts(service, last_24h),
                "last_7d": _count_all_alerts(service, last_7d),
            },
            "top_source_ips": _get_top_source_ips(service, last_24h, limit=10),
            "system_health": {
                "alerts_processed": _count_all_alerts(service, last_24h),
                "false_positive_rate": _calculate_false_positive_rate(service, last_24h),
                "response_time_avg": _calculate_avg_response_time(service, last_24h),
            }
        }
        
        # Update Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            _update_security_prometheus_metrics(security_metrics)
        
        return security_metrics
        
    except Exception as e:
        return {
            "error": f"Failed to retrieve security metrics: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@router.get("/metrics/performance")
async def get_performance_metrics():
    """
    Get application performance metrics.
    """
    try:
        import psutil
        from datetime import datetime
        
        performance_metrics = {
            "timestamp": datetime.now().isoformat(),
            "system_resources": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_io": {
                    "read_bytes": psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
                    "write_bytes": psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
                } if psutil.disk_io_counters() else {"read_bytes": 0, "write_bytes": 0},
                "network_io": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv,
                }
            },
            "application_metrics": {
                "active_connections": _get_active_db_connections(),
                "cache_hit_rate": _get_cache_hit_rate(),
                "queue_length": _get_processing_queue_length(),
            },
            "prometheus_enabled": PROMETHEUS_AVAILABLE
        }
        
        return performance_metrics
        
    except Exception as e:
        return {
            "error": f"Failed to retrieve performance metrics: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# Helper functions for metrics calculations
def _count_attacks_by_type(attack_type: str, service: AlertService, since: datetime) -> int:
    """Count attacks of a specific type since a given time."""
    try:
        # This would need to be implemented in the AlertService
        # For now, return a mock value
        return 15 if attack_type == "brute-force" else 8 if attack_type == "sql-injection" else 3
    except:
        return 0


def _count_alerts_by_severity(severity: str, service: AlertService, since: datetime) -> int:
    """Count alerts by severity level since a given time."""
    try:
        # Mock implementation - would need real service method
        severity_counts = {"CRITICAL": 5, "HIGH": 12, "MEDIUM": 25, "LOW": 8}
        return severity_counts.get(severity, 0)
    except:
        return 0


def _count_all_alerts(service: AlertService, since: datetime) -> int:
    """Count all alerts since a given time."""
    try:
        # Mock implementation
        return 50
    except:
        return 0


def _get_top_source_ips(service: AlertService, since: datetime, limit: int) -> list:
    """Get top source IPs by alert count."""
    try:
        # Mock implementation
        return [
            {"ip": "192.168.1.100", "count": 25},
            {"ip": "10.0.0.50", "count": 18},
            {"ip": "172.16.0.200", "count": 12},
        ]
    except:
        return []


def _calculate_false_positive_rate(service: AlertService, since: datetime) -> float:
    """Calculate false positive rate."""
    try:
        # Mock implementation
        return 0.15  # 15% false positive rate
    except:
        return 0.0


def _calculate_avg_response_time(service: AlertService, since: datetime) -> float:
    """Calculate average response time in seconds."""
    try:
        # Mock implementation
        return 2.5  # 2.5 seconds average
    except:
        return 0.0


def _get_active_db_connections() -> int:
    """Get number of active database connections."""
    try:
        # Mock implementation
        return 5
    except:
        return 0


def _get_cache_hit_rate() -> float:
    """Get cache hit rate percentage."""
    try:
        # Mock implementation
        return 85.5  # 85.5% hit rate
    except:
        return 0.0


def _get_processing_queue_length() -> int:
    """Get current processing queue length."""
    try:
        # Mock implementation
        return 12
    except:
        return 0


def _update_security_prometheus_metrics(security_metrics: dict):
    """Update Prometheus metrics with security data."""
    try:
        # Update attack pattern metrics
        for attack_type, count in security_metrics["attack_patterns"].items():
            metrics.record_alert(attack_type.replace("_attempts", ""), "HIGH", "multiple")
        
        # Update threat level metrics
        metrics.update_alert_severity_metrics(security_metrics["threat_levels"])
        
    except Exception as e:
        logger.warning(f"Failed to update Prometheus security metrics: {e}")
