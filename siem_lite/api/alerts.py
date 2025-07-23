"""
Enhanced Alerts API for SIEM Lite.

This module provides comprehensive REST API endpoints for managing security alerts
with proper validation, error handling, and security features.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from siem_lite.api.schemas import Alert as AlertSchema
from siem_lite.api.schemas import (
    AlertCreate,
    AlertFilter,
    AlertResponse,
    AlertUpdate,
    PaginatedResponse,
)
from siem_lite.domain.entities import Alert, AlertSeverity, AlertStatus
from siem_lite.domain.services import AlertService
from siem_lite.infrastructure.database import get_db
from siem_lite.infrastructure.repositories import SQLAlchemyAlertRepository
from siem_lite.utils.exceptions import APIError, ValidationError
from siem_lite.utils.logging import SecurityLogger, get_logger
from siem_lite.utils.security import SecurityMiddleware
from siem_lite.utils.validation import validate_alert_type, validate_ip_address

router = APIRouter(prefix="/alerts", tags=["alerts"])
logger = get_logger(__name__)
security_logger = SecurityLogger("alerts_api")
security_middleware = SecurityMiddleware()


def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    """Get alert service instance."""
    repo = SQLAlchemyAlertRepository(db)
    return AlertService(repo)


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    return request.client.host if request.client else "unknown"


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert: AlertCreate,
    request: Request,
    service: AlertService = Depends(get_alert_service),
):
    """
    Create a new security alert.

    Args:
        alert: Alert data to create
        request: HTTP request object
        service: Alert service instance

    Returns:
        Created alert with assigned ID

    Raises:
        HTTPException: If validation fails or creation error occurs
    """
    client_ip = get_client_ip(request)

    try:
        # Validate input data
        validate_ip_address(alert.source_ip)
        validate_alert_type(alert.alert_type)

        # Create alert entity
        alert_entity = Alert(
            id=None,
            alert_type=alert.alert_type,
            source_ip=alert.source_ip,
            details=alert.details,
            severity=(
                AlertSeverity(alert.severity)
                if alert.severity
                else AlertSeverity.MEDIUM
            ),
            metadata=alert.metadata or {},
        )

        # Create alert
        created = service.create_alert(alert_entity)

        # Log security event
        security_logger.log_alert_generation(
            alert_type=created.alert_type,
            source_ip=created.source_ip,
            severity=created.severity.value,
        )

        logger.info(
            "Alert created successfully",
            alert_id=created.id,
            alert_type=created.alert_type,
            source_ip=created.source_ip,
            client_ip=client_ip,
        )

        return AlertResponse.from_entity(created)

    except ValidationError as e:
        logger.warning(
            f"Validation error creating alert: {e.message}", client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
        )
    except Exception as e:
        logger.error(f"Error creating alert: {e}", client_ip=client_ip, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating alert",
        )


@router.get("", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of records to return"
    ),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    source_ip: Optional[str] = Query(None, description="Filter by source IP"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    start_date: Optional[datetime] = Query(
        None, description="Filter alerts from this date"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter alerts until this date"
    ),
    service: AlertService = Depends(get_alert_service),
):
    """
    List security alerts with filtering and pagination.

    Args:
        request: HTTP request object
        skip: Number of records to skip
        limit: Maximum number of records to return
        severity: Filter by severity level
        status: Filter by alert status
        source_ip: Filter by source IP address
        alert_type: Filter by alert type
        start_date: Filter alerts from this date
        end_date: Filter alerts until this date
        service: Alert service instance

    Returns:
        Paginated list of alerts
    """
    client_ip = get_client_ip(request)

    try:
        # Validate IP filter if provided
        if source_ip:
            validate_ip_address(source_ip)

        # Create filter object
        filters = AlertFilter(
            severity=severity,
            status=status,
            source_ip=source_ip,
            alert_type=alert_type,
            start_date=start_date,
            end_date=end_date,
        )

        # Get alerts with pagination
        alerts, total = service.list_alerts_paginated(
            skip=skip, limit=limit, filters=filters
        )

        # Convert to response objects
        alert_responses = [AlertResponse.from_entity(alert) for alert in alerts]

        logger.info(
            "Alerts listed successfully",
            count=len(alerts),
            total=total,
            client_ip=client_ip,
        )

        return PaginatedResponse(
            items=alert_responses, total=total, skip=skip, limit=limit
        )

    except ValidationError as e:
        logger.warning(
            f"Validation error listing alerts: {e.message}", client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
        )
    except Exception as e:
        logger.error(f"Error listing alerts: {e}", client_ip=client_ip, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while listing alerts",
        )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int, request: Request, service: AlertService = Depends(get_alert_service)
):
    """
    Get a specific alert by ID.

    Args:
        alert_id: Alert ID to retrieve
        request: HTTP request object
        service: Alert service instance

    Returns:
        Alert details

    Raises:
        HTTPException: If alert not found or error occurs
    """
    client_ip = get_client_ip(request)

    try:
        alert = service.get_alert(alert_id)

        if alert is None:
            logger.warning(f"Alert not found: {alert_id}", client_ip=client_ip)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with ID {alert_id} not found",
            )

        logger.info(f"Alert retrieved successfully: {alert_id}", client_ip=client_ip)
        return AlertResponse.from_entity(alert)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving alert {alert_id}: {e}",
            client_ip=client_ip,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving alert",
        )


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    request: Request,
    service: AlertService = Depends(get_alert_service),
):
    """
    Update an existing alert.

    Args:
        alert_id: Alert ID to update
        alert_update: Update data
        request: HTTP request object
        service: Alert service instance

    Returns:
        Updated alert

    Raises:
        HTTPException: If alert not found or update fails
    """
    client_ip = get_client_ip(request)

    try:
        # Get existing alert
        existing_alert = service.get_alert(alert_id)
        if existing_alert is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with ID {alert_id} not found",
            )

        # Update alert
        updated_alert = service.update_alert(alert_id, alert_update)

        logger.info(
            "Alert updated successfully", alert_id=alert_id, client_ip=client_ip
        )

        return AlertResponse.from_entity(updated_alert)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating alert {alert_id}: {e}", client_ip=client_ip, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating alert",
        )


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    request: Request,
    analyst: str = Query(..., description="Analyst acknowledging the alert"),
    service: AlertService = Depends(get_alert_service),
):
    """
    Acknowledge an alert.

    Args:
        alert_id: Alert ID to acknowledge
        request: HTTP request object
        analyst: Name of analyst acknowledging
        service: Alert service instance

    Returns:
        Success message
    """
    client_ip = get_client_ip(request)

    try:
        success = service.acknowledge_alert(alert_id, analyst)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with ID {alert_id} not found",
            )

        logger.info(
            "Alert acknowledged",
            alert_id=alert_id,
            analyst=analyst,
            client_ip=client_ip,
        )

        return {"message": "Alert acknowledged successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error acknowledging alert {alert_id}: {e}",
            client_ip=client_ip,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while acknowledging alert",
        )


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    request: Request,
    analyst: str = Query(..., description="Analyst resolving the alert"),
    service: AlertService = Depends(get_alert_service),
):
    """
    Resolve an alert.

    Args:
        alert_id: Alert ID to resolve
        request: HTTP request object
        analyst: Name of analyst resolving
        service: Alert service instance

    Returns:
        Success message
    """
    client_ip = get_client_ip(request)

    try:
        success = service.resolve_alert(alert_id, analyst)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with ID {alert_id} not found",
            )

        logger.info(
            "Alert resolved", alert_id=alert_id, analyst=analyst, client_ip=client_ip
        )

        return {"message": "Alert resolved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error resolving alert {alert_id}: {e}", client_ip=client_ip, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while resolving alert",
        )


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int, request: Request, service: AlertService = Depends(get_alert_service)
):
    """
    Delete an alert.

    Args:
        alert_id: Alert ID to delete
        request: HTTP request object
        service: Alert service instance

    Returns:
        Success message
    """
    client_ip = get_client_ip(request)

    try:
        success = service.delete_alert(alert_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with ID {alert_id} not found",
            )

        logger.info("Alert deleted", alert_id=alert_id, client_ip=client_ip)

        return {"message": "Alert deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting alert {alert_id}: {e}", client_ip=client_ip, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting alert",
        )
