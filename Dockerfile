# SIEM Lite - Dockerfile
# Multi-stage build for production-ready Python application

# Build stage
FROM python:3.12-alpine AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apk add --no-cache \
    build-base \
    curl \
    gcc \
    musl-dev \
    libffi-dev

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-alpine AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    SIEM_LITE_ENV=production

# Install only runtime dependencies
RUN apk add --no-cache \
    curl \
    && addgroup -g 1001 -S siem \
    && adduser -S siem -G siem -u 1001

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/data /app/reports /app/logs && \
    chown -R siem:siem /app

# Switch to non-root user
USER siem

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "uvicorn", "siem_lite.main:app", "--host", "0.0.0.0", "--port", "8000"]
