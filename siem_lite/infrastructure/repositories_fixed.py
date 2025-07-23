from typing import List, Optional

from sqlalchemy.orm import Session

from siem_lite.domain.entities import Alert, AlertStatus, AlertSeverity
from siem_lite.domain.interfaces import IAlertRepository

from .models import AlertORM


class SQLAlchemyAlertRepository(IAlertRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all_alerts(self) -> List[Alert]:
        return [self._to_entity(a) for a in self.db.query(AlertORM).all()]

    def get_alerts_by_ip(self, ip_address: str) -> List[Alert]:
        return [
            self._to_entity(a)
            for a in self.db.query(AlertORM)
            .filter(AlertORM.source_ip == ip_address)
            .all()
        ]

    def create_alert(self, alert: Alert) -> Alert:
        alert_orm = AlertORM(
            alert_type=alert.alert_type,
            source_ip=alert.source_ip,
            details=alert.details,
            timestamp=alert.timestamp,
            severity=alert.severity.value if alert.severity else AlertSeverity.MEDIUM.value,
            status=alert.status.value if alert.status else AlertStatus.OPEN.value,
        )
        # Set metadata
        alert_orm.set_metadata(alert.metadata or {})
        
        self.db.add(alert_orm)
        self.db.commit()
        self.db.refresh(alert_orm)
        return self._to_entity(alert_orm)

    def get_alert(self, alert_id: int) -> Optional[Alert]:
        alert_orm = self.db.query(AlertORM).filter(AlertORM.id == alert_id).first()
        return self._to_entity(alert_orm) if alert_orm else None

    def update_alert(self, alert: Alert) -> Alert:
        """Update an existing alert."""
        alert_orm = self.db.query(AlertORM).filter(AlertORM.id == alert.id).first()
        if alert_orm:
            alert_orm.alert_type = alert.alert_type
            alert_orm.source_ip = alert.source_ip
            alert_orm.details = alert.details
            alert_orm.severity = alert.severity.value
            alert_orm.status = alert.status.value
            alert_orm.timestamp = alert.timestamp
            alert_orm.set_metadata(alert.metadata or {})
            self.db.commit()
            self.db.refresh(alert_orm)
        return self._to_entity(alert_orm)

    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert by ID."""
        alert_orm = self.db.query(AlertORM).filter(AlertORM.id == alert_id).first()
        if alert_orm:
            self.db.delete(alert_orm)
            self.db.commit()
            return True
        return False

    def _to_entity(self, alert_orm: AlertORM) -> Alert:
        return Alert(
            id=alert_orm.id,
            alert_type=alert_orm.alert_type,
            source_ip=alert_orm.source_ip,
            details=alert_orm.details,
            timestamp=alert_orm.timestamp,
            severity=AlertSeverity(getattr(alert_orm, 'severity', AlertSeverity.MEDIUM.value)),
            status=AlertStatus(getattr(alert_orm, 'status', AlertStatus.OPEN.value)),
            metadata=alert_orm.get_metadata(),
            updated_at=getattr(alert_orm, 'updated_at', alert_orm.timestamp)
        )
