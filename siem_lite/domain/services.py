from typing import List, Optional, Tuple
from datetime import datetime
from collections import Counter

from .entities import Alert, AlertStatus, AlertSeverity
from .interfaces import IAlertRepository, IAlertService


class AlertService(IAlertService):
    def __init__(self, alert_repo: IAlertRepository):
        self.alert_repo = alert_repo

    def list_alerts(self, **filters) -> List[Alert]:
        """List alerts with optional filters."""
        if "ip" in filters:
            return self.alert_repo.get_alerts_by_ip(filters["ip"])
        return self.alert_repo.get_all_alerts()

    def list_alerts_paginated(self, skip: int = 0, limit: int = 10, filters=None) -> Tuple[List[Alert], int]:
        """List alerts with pagination and filtering."""
        all_alerts = self.alert_repo.get_all_alerts()
        
        # Apply filters
        filtered_alerts = all_alerts
        if filters:
            if filters.severity:
                filtered_alerts = [a for a in filtered_alerts if a.severity == filters.severity]
            if filters.status:
                filtered_alerts = [a for a in filtered_alerts if a.status == filters.status]
            if filters.source_ip:
                filtered_alerts = [a for a in filtered_alerts if a.source_ip == filters.source_ip]
            if filters.alert_type:
                filtered_alerts = [a for a in filtered_alerts if a.alert_type == filters.alert_type]
            if filters.start_date:
                filtered_alerts = [a for a in filtered_alerts if a.timestamp >= filters.start_date]
            if filters.end_date:
                filtered_alerts = [a for a in filtered_alerts if a.timestamp <= filters.end_date]
        
        # Apply pagination
        total = len(filtered_alerts)
        paginated_alerts = filtered_alerts[skip:skip + limit]
        
        return paginated_alerts, total

    def create_alert(self, alert: Alert) -> Alert:
        """Create a new alert with business logic validation."""
        # Set default values
        if not alert.timestamp:
            alert.timestamp = datetime.now()
        if not alert.status:
            alert.status = AlertStatus.OPEN
        if not alert.severity:
            alert.severity = AlertSeverity.MEDIUM
            
        return self.alert_repo.create_alert(alert)

    def get_alert(self, alert_id: int) -> Optional[Alert]:
        """Get alert by ID."""
        return self.alert_repo.get_alert(alert_id)

    def update_alert(self, alert_id: int, update_data) -> Optional[Alert]:
        """Update an existing alert."""
        alert = self.alert_repo.get_alert(alert_id)
        if not alert:
            return None
        
        # Update fields
        if hasattr(update_data, 'status') and update_data.status:
            alert.status = AlertStatus(update_data.status)
        if hasattr(update_data, 'severity') and update_data.severity:
            alert.severity = AlertSeverity(update_data.severity)
        if hasattr(update_data, 'details') and update_data.details:
            alert.details = update_data.details
        if hasattr(update_data, 'metadata') and update_data.metadata:
            alert.metadata.update(update_data.metadata)
        
        alert.updated_at = datetime.now()
        return self.alert_repo.update_alert(alert)

    def acknowledge_alert(self, alert_id: int, analyst: str) -> bool:
        """Acknowledge an alert."""
        alert = self.alert_repo.get_alert(alert_id)
        if not alert:
            return False
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.metadata['acknowledged_by'] = analyst
        alert.metadata['acknowledged_at'] = datetime.now().isoformat()
        alert.updated_at = datetime.now()
        
        self.alert_repo.update_alert(alert)
        return True

    def resolve_alert(self, alert_id: int, analyst: str) -> bool:
        """Resolve an alert."""
        alert = self.alert_repo.get_alert(alert_id)
        if not alert:
            return False
        
        alert.status = AlertStatus.RESOLVED
        alert.metadata['resolved_by'] = analyst
        alert.metadata['resolved_at'] = datetime.now().isoformat()
        alert.updated_at = datetime.now()
        
        self.alert_repo.update_alert(alert)
        return True

    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert."""
        alert = self.alert_repo.get_alert(alert_id)
        if not alert:
            return False
        
        return self.alert_repo.delete_alert(alert_id)

    def get_alert_statistics(self) -> dict:
        """Get comprehensive alert statistics."""
        alerts = self.alert_repo.get_all_alerts()
        
        # Basic counts
        total_alerts = len(alerts)
        
        # Status distribution
        status_counts = Counter(alert.status.value for alert in alerts)
        
        # Severity distribution  
        severity_counts = Counter(alert.severity.value for alert in alerts)
        
        # Alert type distribution
        type_counts = Counter(alert.alert_type for alert in alerts)
        
        # Top source IPs
        ip_counts = Counter(alert.source_ip for alert in alerts)
        top_ips = dict(ip_counts.most_common(10))
        
        # Recent activity (last 24 hours)
        now = datetime.now()
        recent_alerts = [a for a in alerts if (now - a.timestamp).days < 1]
        
        return {
            "total_alerts": total_alerts,
            "recent_alerts_24h": len(recent_alerts),
            "status_distribution": dict(status_counts),
            "severity_distribution": dict(severity_counts),
            "alert_type_distribution": dict(type_counts),
            "top_source_ips": top_ips,
            "unique_ips": len(set(alert.source_ip for alert in alerts))
        }
