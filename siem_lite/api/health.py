import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from siem_lite.infrastructure.database import engine, get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    detailed: bool = Query(False, description="Include detailed health information"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Health check endpoint that provides system status information.
    
    Args:
        detailed: If True, includes detailed system information
        db: Database session
        
    Returns:
        Health status information
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }
    
    # Check database connectivity
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
        if not detailed:
            health_data["status"] = "healthy"
    except Exception:
        db_status = "disconnected"
        health_data["status"] = "unhealthy"
    
    health_data["database"] = db_status
    
    # Add detailed information if requested
    if detailed:
        try:
            # Get additional system metrics
            from siem_lite.domain.services import AlertService
            from siem_lite.infrastructure.repositories import SQLAlchemyAlertRepository
            
            service = AlertService(SQLAlchemyAlertRepository(db))
            stats = service.get_alert_statistics()
            
            health_data["details"] = {
                "database_engine": str(engine.url).split("://")[0],
                "total_alerts": stats.get("total_alerts", 0),
                "recent_alerts_24h": stats.get("recent_alerts_24h", 0),
                "api_version": "1.0.0",
                "python_version": "3.8+",
                "uptime": "healthy"
            }
        except Exception:
            health_data["details"] = {
                "error": "Unable to retrieve detailed metrics"
            }
    
    return health_data
