import datetime
import json

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AlertORM(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String, nullable=False)
    source_ip = Column(String, nullable=False)
    details = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="MEDIUM")
    status = Column(String, nullable=False, default="OPEN")
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc), 
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    alert_metadata = Column(Text, default='{}')
    
    def get_metadata(self):
        """Get metadata as dictionary."""
        try:
            return json.loads(self.alert_metadata) if self.alert_metadata else {}
        except json.JSONDecodeError:
            return {}
    
    def set_metadata(self, value):
        """Set metadata from dictionary."""
        self.alert_metadata = json.dumps(value) if isinstance(value, dict) else str(value)


class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc), 
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
