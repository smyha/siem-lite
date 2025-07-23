"""
Enhanced REST API for SIEM Lite.

This module provides a robust REST API built with FastAPI for the SIEM Lite system.
It includes comprehensive security, monitoring, and error handling features.
"""

import datetime
import logging
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from siem_lite.api.alerts import router as alerts_router
from siem_lite.api.health import router as health_router
from siem_lite.api.root import router as root_router
from siem_lite.api.stats import router as stats_router
from siem_lite.api.metrics import router as metrics_router
from siem_lite.utils.config import get_settings
from siem_lite.utils.exceptions import SIEMLiteException
from siem_lite.utils.logging import SecurityLogger, get_logger, setup_logging
from siem_lite.utils.security import SecurityMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)
security_logger = SecurityLogger("api")

# Initialize security middleware
security_middleware = SecurityMiddleware()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting SIEM Lite API...")

    # Startup checks
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Database connection check could go here
    # if not check_database_connection():
    #     logger.error("❌ Could not connect to database")
    #     raise RuntimeError("Database connection error")

    logger.info("✅ SIEM Lite API started successfully")
    yield

    # Cleanup
    logger.info("🛑 Shutting down SIEM Lite API...")


# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="SIEM Lite API",
    description="Enhanced REST API for the SIEM Lite Security Information and Event Management system",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)


# Custom exception handler
@app.exception_handler(SIEMLiteException)
async def siem_exception_handler(request: Request, exc: SIEMLiteException):
    """Handle custom SIEM Lite exceptions."""
    security_logger.logger.error(
        "SIEM exception occurred",
        exception=exc.__class__.__name__,
        message=exc.message,
        code=exc.code,
        details=exc.details,
        url=str(request.url),
        method=request.method,
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "code": exc.code,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception",
        exception=str(exc),
        url=str(request.url),
        method=request.method,
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        },
    )


# Security middleware
@app.middleware("http")
async def security_middleware_handler(request: Request, call_next):
    """Security middleware for all requests."""
    start_time = time.time()

    # Log request
    client_ip = request.client.host if request.client else "unknown"
    security_logger.logger.info(
        "Request received",
        method=request.method,
        url=str(request.url),
        client_ip=client_ip,
        user_agent=request.headers.get("user-agent", "unknown"),
    )

    # Security validations
    try:
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length:
            security_middleware.validate_request_size(int(content_length))

        # Rate limiting check (implement based on your needs)
        # if not security_middleware.check_rate_limit(client_ip, str(request.url.path)):
        #     return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        security_logger.logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time,
        )

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response

    except Exception as e:
        logger.error(f"Security middleware error: {e}")
        return JSONResponse(
            status_code=400, content={"error": "Security validation failed"}
        )


# Trusted host middleware
if settings.security.allowed_hosts != ["*"]:
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=settings.security.allowed_hosts
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Mount routers
app.include_router(root_router, tags=["Root"])
app.include_router(alerts_router, prefix="/api", tags=["Alerts"])
app.include_router(stats_router, prefix="/api", tags=["Statistics"])
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(metrics_router, prefix="/api", tags=["Metrics"])
