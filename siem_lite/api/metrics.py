"""
Metrics API endpoint for SIEM Lite.

Provides Prometheus-compatible metrics endpoint and health information.
"""

from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session

from siem_lite.infrastructure.database import get_db
from siem_lite.domain.services import AlertService
from siem_lite.infrastructure.repositories import SQLAlchemyAlertRepository
from siem_lite.utils.metrics import metrics

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
