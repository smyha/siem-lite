import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from siem_lite.domain.services import AlertService
from siem_lite.infrastructure.database import get_db
from siem_lite.infrastructure.repositories import SQLAlchemyAlertRepository

router = APIRouter()
logger = logging.getLogger(__name__)


def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    """Get alert service instance."""
    repo = SQLAlchemyAlertRepository(db)
    return AlertService(repo)


@router.get("/stats")
async def get_stats(service: AlertService = Depends(get_alert_service)):
    """Get system statistics."""
    try:
        stats = service.get_alert_statistics()
        return stats
    except Exception as e:
        logger.error(f"❌ Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting statistics",
        )


@router.get("/trends")
async def get_trends(service: AlertService = Depends(get_alert_service)):
    """Get trends data."""
    try:
        from datetime import datetime, timedelta

        alerts = service.list_alerts()
        now = datetime.now()
        periods = {
            "1h": now - timedelta(hours=1),
            "24h": now - timedelta(days=1),
            "7d": now - timedelta(days=7),
            "30d": now - timedelta(days=30),
        }
        trends = {}
        for period_name, start_time in periods.items():
            count = len([a for a in alerts if a.timestamp >= start_time])
            trends[period_name] = count
        # Top sources and patterns (last 24h)
        yesterday = now - timedelta(days=1)
        last_24h_alerts = [a for a in alerts if a.timestamp >= yesterday]
        from collections import Counter

        top_sources = Counter(a.source_ip for a in last_24h_alerts).most_common(10)
        top_sources_list = [{"ip": ip, "count": count} for ip, count in top_sources]
        patterns = Counter(a.alert_type for a in last_24h_alerts).most_common(5)
        patterns_list = [{"type": t, "count": c} for t, c in patterns]
        return {
            "alerts": trends,
            "top_sources": top_sources_list,
            "patterns": patterns_list,
        }
    except Exception as e:
        logger.error(f"❌ Error getting trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting trends",
        )
