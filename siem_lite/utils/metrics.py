"""
Prometheus metrics for SIEM Lite.

This module provides comprehensive metrics collection for monitoring
and observability using Prometheus.
"""

import time
from datetime import datetime
from functools import wraps
from typing import Dict, Any

try:
    from prometheus_client import Counter, Histogram, Gauge, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from .logging import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """
    Centralized metrics collector for SIEM Lite.
    
    Provides Prometheus-compatible metrics for monitoring system performance,
    security events, and operational health.
    """
    
    def __init__(self):
        self.enabled = PROMETHEUS_AVAILABLE
        
        if self.enabled:
            self._init_prometheus_metrics()
        else:
            logger.warning("Prometheus client not available. Metrics collection disabled.")
            self._init_fallback_metrics()
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        # Request metrics
        self.http_requests_total = Counter(
            'siem_lite_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration = Histogram(
            'siem_lite_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint']
        )
        
        # Alert metrics
        self.alerts_total = Counter(
            'siem_lite_alerts_total',
            'Total alerts generated',
            ['alert_type', 'severity', 'source_ip']
        )
        
        self.alerts_by_status = Gauge(
            'siem_lite_alerts_by_status',
            'Current alerts by status',
            ['status']
        )
        
        self.alerts_by_severity = Gauge(
            'siem_lite_alerts_by_severity',
            'Current alerts by severity',
            ['severity']
        )
        
        # System metrics
        self.database_connections = Gauge(
            'siem_lite_database_connections',
            'Current database connections'
        )
        
        self.log_processing_duration = Histogram(
            'siem_lite_log_processing_duration_seconds',
            'Log processing duration in seconds',
            ['log_type']
        )
        
        self.log_entries_processed = Counter(
            'siem_lite_log_entries_processed_total',
            'Total log entries processed',
            ['log_type', 'status']
        )
        
        # Security metrics
        self.authentication_attempts = Counter(
            'siem_lite_authentication_attempts_total',
            'Total authentication attempts',
            ['result', 'source_ip']
        )
        
        self.api_errors = Counter(
            'siem_lite_api_errors_total',
            'Total API errors',
            ['endpoint', 'error_type']
        )
        
        # Application info
        self.app_info = Info(
            'siem_lite_app_info',
            'Application information'
        )
        
        self.app_info.info({
            'version': '1.0.0',
            'python_version': '3.8+',
            'environment': 'production'
        })
        
    def _init_fallback_metrics(self):
        """Initialize fallback metrics when Prometheus is not available."""
        self._counters = {}
        self._gauges = {}
        self._histograms = {}
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        if self.enabled:
            self.http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            self.http_request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
        else:
            key = f"http_requests_{method}_{endpoint}_{status_code}"
            self._counters[key] = self._counters.get(key, 0) + 1
    
    def record_alert(self, alert_type: str, severity: str, source_ip: str):
        """Record alert generation metrics."""
        if self.enabled:
            self.alerts_total.labels(
                alert_type=alert_type,
                severity=severity,
                source_ip=source_ip
            ).inc()
        else:
            key = f"alerts_{alert_type}_{severity}"
            self._counters[key] = self._counters.get(key, 0) + 1
    
    def update_alert_status_metrics(self, status_counts: Dict[str, int]):
        """Update alert status gauge metrics."""
        if self.enabled:
            for status, count in status_counts.items():
                self.alerts_by_status.labels(status=status).set(count)
        else:
            self._gauges.update(status_counts)
    
    def update_alert_severity_metrics(self, severity_counts: Dict[str, int]):
        """Update alert severity gauge metrics."""
        if self.enabled:
            for severity, count in severity_counts.items():
                self.alerts_by_severity.labels(severity=severity).set(count)
        else:
            self._gauges.update(severity_counts)
    
    def record_log_processing(self, log_type: str, count: int, duration: float, success: bool):
        """Record log processing metrics."""
        status = "success" if success else "error"
        
        if self.enabled:
            self.log_entries_processed.labels(
                log_type=log_type,
                status=status
            ).inc(count)
            
            self.log_processing_duration.labels(
                log_type=log_type
            ).observe(duration)
        else:
            key = f"log_processing_{log_type}_{status}"
            self._counters[key] = self._counters.get(key, 0) + count
    
    def record_authentication_attempt(self, success: bool, source_ip: str):
        """Record authentication attempt metrics."""
        result = "success" if success else "failure"
        
        if self.enabled:
            self.authentication_attempts.labels(
                result=result,
                source_ip=source_ip
            ).inc()
        else:
            key = f"auth_{result}_{source_ip}"
            self._counters[key] = self._counters.get(key, 0) + 1
    
    def record_api_error(self, endpoint: str, error_type: str):
        """Record API error metrics."""
        if self.enabled:
            self.api_errors.labels(
                endpoint=endpoint,
                error_type=error_type
            ).inc()
        else:
            key = f"api_errors_{endpoint}_{error_type}"
            self._counters[key] = self._counters.get(key, 0) + 1
    
    def set_database_connections(self, count: int):
        """Set current database connections."""
        if self.enabled:
            self.database_connections.set(count)
        else:
            self._gauges["database_connections"] = count
    
    def get_fallback_metrics(self) -> Dict[str, Any]:
        """Get fallback metrics when Prometheus is not available."""
        return {
            "counters": self._counters.copy(),
            "gauges": self._gauges.copy(),
            "histograms": self._histograms.copy(),
            "timestamp": datetime.now().isoformat()
        }


# Global metrics instance
metrics = MetricsCollector()


def monitor_request_metrics(func):
    """
    Decorator to automatically monitor HTTP request metrics.
    
    Args:
        func: FastAPI endpoint function to monitor
        
    Returns:
        Wrapped function with metrics collection
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Extract request information
        request = None
        for arg in args:
            if hasattr(arg, 'method') and hasattr(arg, 'url'):
                request = arg
                break
        
        method = request.method if request else "UNKNOWN"
        endpoint = str(request.url.path) if request else "unknown"
        
        try:
            result = await func(*args, **kwargs)
            status_code = getattr(result, 'status_code', 200)
            
            # Record metrics
            duration = time.time() - start_time
            metrics.record_http_request(method, endpoint, status_code, duration)
            
            return result
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            status_code = getattr(e, 'status_code', 500)
            metrics.record_http_request(method, endpoint, status_code, duration)
            metrics.record_api_error(endpoint, type(e).__name__)
            
            raise
    
    return wrapper


def monitor_alert_generation(func):
    """
    Decorator to monitor alert generation metrics.
    
    Args:
        func: Function that generates alerts
        
    Returns:
        Wrapped function with alert metrics collection
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Extract alert information from result
        if hasattr(result, 'alert_type'):
            metrics.record_alert(
                alert_type=result.alert_type,
                severity=getattr(result, 'severity', 'UNKNOWN'),
                source_ip=getattr(result, 'source_ip', 'unknown')
            )
        
        return result
    
    return wrapper


def monitor_log_processing(log_type: str):
    """
    Decorator to monitor log processing metrics.
    
    Args:
        log_type: Type of logs being processed
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Try to extract count from result
                count = len(result) if isinstance(result, (list, tuple)) else 1
                
                metrics.record_log_processing(log_type, count, duration, True)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_log_processing(log_type, 0, duration, False)
                raise
        
        return wrapper
    return decorator
