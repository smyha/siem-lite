from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import Alert, User


class IAlertRepository(ABC):
    @abstractmethod
    def get_all_alerts(self) -> List[Alert]: ...
    @abstractmethod
    def get_alerts_by_ip(self, ip_address: str) -> List[Alert]: ...
    @abstractmethod
    def create_alert(self, alert: Alert) -> Alert: ...
    @abstractmethod
    def get_alert(self, alert_id: int) -> Optional[Alert]: ...


class IUserRepository(ABC):
    @abstractmethod
    def get_user(self, username: str) -> Optional[User]: ...
    @abstractmethod
    def create_user(self, user: User) -> User: ...


class IAlertService(ABC):
    @abstractmethod
    def list_alerts(self, **filters) -> List[Alert]: ...
    @abstractmethod
    def create_alert(self, alert: Alert) -> Alert: ...
    @abstractmethod
    def get_alert(self, alert_id: int) -> Optional[Alert]: ...
