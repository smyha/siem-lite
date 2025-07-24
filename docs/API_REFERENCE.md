# SIEM Lite API Reference

## 🌐 Overview

SIEM Lite provides a comprehensive REST API for managing security alerts, system statistics, and health monitoring. The API is built with FastAPI and provides automatic interactive documentation.

## 📋 Base Information

- **Base URL**: `http://localhost:8000`
- **API Version**: `v1`
- **Content Type**: `application/json`
- **Authentication**: Token-based (JWT) for protected endpoints

## 🔗 Interactive Documentation

When documentation is enabled, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 📊 API Endpoints

### System Information

#### `GET /api/info`
Get application information and configuration.

**Response:**
```json
{
  "name": "SIEM Lite",
  "version": "1.0.0",
  "environment": "development",
  "debug": true,
  "features": {
    "dashboard": true,
    "monitoring": true,
    "reports": true,
    "docs": true
  },
  "api": {
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json"
  },
  "timestamp": "2025-07-24T11:30:00Z"
}
```

### Health Check Endpoints

#### `GET /api/health`
Get system health status.

**Parameters:**
- `detailed` (boolean, optional): Return detailed system information

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-24T11:30:00Z",
  "uptime": "3600.50s",
  "version": "1.0.0",
  "database": "connected",
  "system": {
    "platform": "Windows-10-10.0.19045-SP0",
    "python_version": "3.13.3",
    "architecture": "64bit"
  },
  "environment": "development",
  "debug_mode": false,
  "features": {
    "dashboard": true,
    "monitoring": true,
    "reports": true
  }
}
```

#### `GET /api/health/ready`
Readiness probe for container orchestration.

#### `GET /api/health/live`
Liveness probe for container orchestration.

### Alert Management

#### `GET /api/alerts`
List all alerts with optional filtering and pagination.

**Parameters:**
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Maximum number of records to return
- `severity` (string, optional): Filter by severity level (LOW, MEDIUM, HIGH, CRITICAL)
- `status` (string, optional): Filter by alert status (OPEN, ACKNOWLEDGED, RESOLVED)
- `source_ip` (string, optional): Filter by source IP address
- `alert_type` (string, optional): Filter by alert type

**Response:**
```json
[
  {
    "id": 1,
    "alert_type": "brute_force_attack",
    "source_ip": "192.168.1.100",
    "details": "Multiple failed login attempts detected",
    "severity": "HIGH",
    "status": "OPEN",
    "timestamp": "2025-07-24T11:30:00Z",
    "acknowledged": false,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "resolved": false,
    "resolved_by": null,
    "resolved_at": null
  }
]
```

#### `POST /api/alerts`
Create a new security alert.

**Request Body:**
```json
{
  "alert_type": "brute_force_attack",
  "source_ip": "192.168.1.100",
  "details": "Multiple failed login attempts detected",
  "severity": "HIGH"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "alert_type": "brute_force_attack",
  "source_ip": "192.168.1.100",
  "details": "Multiple failed login attempts detected",
  "severity": "HIGH",
  "status": "OPEN",
  "timestamp": "2025-07-24T11:30:00Z",
  "acknowledged": false
}
```

#### `GET /api/alerts/{alert_id}`
Get a specific alert by ID.

**Response:**
```json
{
  "id": 1,
  "alert_type": "brute_force_attack",
  "source_ip": "192.168.1.100",
  "details": "Multiple failed login attempts detected",
  "severity": "HIGH",
  "status": "OPEN",
  "timestamp": "2025-07-24T11:30:00Z",
  "acknowledged": false
}
```

#### `PUT /api/alerts/{alert_id}`
Update an existing alert.

#### `DELETE /api/alerts/{alert_id}`
Delete an alert.

#### `POST /api/alerts/{alert_id}/acknowledge`
Acknowledge an alert.

**Request Body:**
```json
{
  "acknowledged_by": "analyst1",
  "notes": "Alert reviewed and confirmed as valid threat"
}
```

#### `POST /api/alerts/{alert_id}/resolve`
Mark an alert as resolved.

**Request Body:**
```json
{
  "resolved_by": "analyst1",
  "resolution_notes": "Threat mitigated, IP blocked"
}
```

### Statistics

#### `GET /api/stats`
Get comprehensive system statistics and metrics.

**Response:**
```json
{
  "total_alerts": 150,
  "recent_alerts_24h": 25,
  "status_distribution": {
    "OPEN": 20,
    "ACKNOWLEDGED": 15,
    "RESOLVED": 115
  },
  "severity_distribution": {
    "LOW": 50,
    "MEDIUM": 60,
    "HIGH": 30,
    "CRITICAL": 10
  },
  "alert_type_distribution": {
    "brute_force_attack": 45,
    "sql_injection_attempt": 30,
    "ddos_attack": 25,
    "malware_detection": 20,
    "privilege_escalation": 15
  },
  "top_source_ips": {
    "192.168.1.100": 15,
    "10.0.0.25": 12,
    "203.0.113.50": 8
  },
  "unique_ips": 25,
  "alert_trends": {
    "last_hour": 2,
    "last_day": 25,
    "last_week": 180
  },
  "timestamp": "2025-07-24T11:30:00Z"
}
```

### Metrics (Prometheus)

#### `GET /api/metrics`
Prometheus-compatible metrics endpoint.

**Response Format:** Prometheus text format
```
# HELP siem_lite_alerts_total Total alerts generated
# TYPE siem_lite_alerts_total counter
siem_lite_alerts_total{alert_type="brute_force_attack",severity="HIGH",source_ip="192.168.1.100"} 1.0

# HELP siem_lite_alerts_by_severity Current alerts by severity
# TYPE siem_lite_alerts_by_severity gauge
siem_lite_alerts_by_severity{severity="CRITICAL"} 10.0
siem_lite_alerts_by_severity{severity="HIGH"} 30.0
siem_lite_alerts_by_severity{severity="MEDIUM"} 60.0
siem_lite_alerts_by_severity{severity="LOW"} 50.0
```

#### `GET /api/metrics/alerts`
Get detailed alert metrics in JSON format.

**Response:**
```json
{
  "metrics_updated": true,
  "alert_statistics": {
    "total_alerts": 150,
    "recent_alerts_24h": 25,
    "status_distribution": {
      "OPEN": 20
    },
    "severity_distribution": {
      "HIGH": 30,
      "CRITICAL": 10
    },
    "alert_type_distribution": {
      "brute_force_attack": 45
    },
    "top_source_ips": {
      "192.168.1.100": 15
    },
    "unique_ips": 25
  },
  "prometheus_enabled": true
}
```

#### `GET /api/metrics/system`
Get system resource metrics.

**Response:**
```json
{
  "timestamp": "2025-07-24T11:30:00Z",
  "cpu_usage": 15.3,
  "memory_usage": 64.1,
  "disk_usage": 51.4,
  "uptime": 3600.50,
  "prometheus_enabled": true
}
```

#### `GET /api/metrics/security`
Get security-specific metrics and threat intelligence.

**Response:**
```json
{
  "timestamp": "2025-07-24T11:30:00Z",
  "attack_patterns": {
    "brute_force_attempts": 15,
    "sql_injection_attempts": 8,
    "ddos_attempts": 3
  },
  "threat_levels": {
    "critical": 5,
    "high": 12,
    "medium": 25,
    "low": 8
  },
  "temporal_analysis": {
    "last_hour": 2,
    "last_24h": 25,
    "last_7d": 180
  },
  "top_source_ips": [
    {
      "ip": "192.168.1.100",
      "count": 25
    }
  ],
  "system_health": {
    "alerts_processed": 150,
    "false_positive_rate": 0.15,
    "response_time_avg": 2.5
  }
}
```

#### `GET /api/metrics/performance`
Get application performance metrics.

**Response:**
```json
{
  "timestamp": "2025-07-24T11:30:00Z",
  "system_resources": {
    "cpu_percent": 15.3,
    "memory_percent": 64.1,
    "disk_io": {
      "read_bytes": 570135347200,
      "write_bytes": 463276208640
    },
    "network_io": {
      "bytes_sent": 2796386334,
      "bytes_recv": 46180756849
    }
  },
  "application_metrics": {
    "active_connections": 5,
    "cache_hit_rate": 85.5,
    "queue_length": 12
  },
  "prometheus_enabled": true
}
```

## 🔒 Authentication

### JWT Token Authentication

For protected endpoints, include the JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "password": "your-password"
  }'
```

## 📝 Request/Response Examples

### Create Alert with cURL

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "sql_injection_attempt",
    "source_ip": "10.0.0.1",
    "details": "Suspicious SQL patterns detected in web request",
    "severity": "CRITICAL"
  }'
```

### List Alerts with Filtering

```bash
# Get high severity alerts
curl "http://localhost:8000/api/alerts?severity=HIGH&limit=10"

# Get alerts from specific IP
curl "http://localhost:8000/api/alerts?source_ip=192.168.1.100"

# Get recent alerts with pagination
curl "http://localhost:8000/api/alerts?skip=0&limit=20"
```

### Health Check

```bash
# Basic health check
curl "http://localhost:8000/api/health"

# Detailed health information
curl "http://localhost:8000/api/health?detailed=true"

# Kubernetes readiness probe
curl "http://localhost:8000/api/health/ready"
```

### Metrics Collection

```bash
# Prometheus metrics
curl "http://localhost:8000/api/metrics"

# Alert statistics
curl "http://localhost:8000/api/metrics/alerts"

# System performance
curl "http://localhost:8000/api/metrics/performance"
```

## ⚠️ Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
  "error": "Alert not found",
  "error_code": "ALERT_NOT_FOUND",
  "timestamp": "2025-07-24T11:30:00Z",
  "path": "/api/alerts/999"
}
```

### Common Status Codes

- `200` - OK: Request successful
- `201` - Created: Resource created successfully
- `400` - Bad Request: Invalid request data
- `401` - Unauthorized: Authentication required
- `403` - Forbidden: Access denied
- `404` - Not Found: Resource not found
- `422` - Unprocessable Entity: Validation error
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server error
- `503` - Service Unavailable: Service temporarily unavailable

## 📊 Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP
- **Headers**: Rate limit information is included in response headers
  - `X-RateLimit-Limit`: Request limit per window
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Window reset time

## 🔍 Validation

All input data is validated using Pydantic models:

- **IP Addresses**: Must be valid IPv4 or IPv6 addresses
- **Severity Levels**: Must be one of: LOW, MEDIUM, HIGH, CRITICAL
- **Alert Types**: Must be non-empty strings with maximum length of 100 characters
- **Timestamps**: Must be valid ISO 8601 format
- **Status Values**: Must be one of: OPEN, ACKNOWLEDGED, RESOLVED

### Validation Error Example

```json
{
  "error": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "severity",
    "message": "Severity must be one of: LOW, MEDIUM, HIGH, CRITICAL"
  },
  "timestamp": "2025-07-24T11:30:00Z",
  "path": "/api/alerts"
}
```

## 📈 Performance

- **Response Times**: P95 < 500ms for most endpoints
- **Throughput**: Supports up to 1000 requests/second
- **Pagination**: Use `skip` and `limit` parameters for large datasets
- **Caching**: Frequently accessed data is cached for better performance

## 🛠️ Development

### Running the API

```bash
# Development mode with auto-reload
uvicorn siem_lite.main:app --reload --host 127.0.0.1 --port 8000

# Using the CLI
python -m siem_lite.cli run

# Using Make
make run
```

### Testing the API

```bash
# Run API tests
pytest tests/test_api.py -v

# Test with coverage
pytest tests/test_api.py --cov=siem_lite.api

# Load testing
locust -f tests/load_test.py --host=http://localhost:8000
```

### Environment Variables

```bash
# Database configuration
DATABASE_URL=sqlite:///./siem_lite.db
DATABASE_ECHO=false

# API configuration
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true

# Security settings
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Feature flags
ENABLE_DOCS=true
ENABLE_DASHBOARD=true
ENABLE_MONITORING=true

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/siem_lite.log
```

---

## 📞 Support

For more information about implementation, see:
- [System Architecture](./ARCHITECTURE.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Monitoring Guide](./MONITORING.md)
- [Development Guide](../CONTRIBUTING.md)

## 🔗 Quick Links

- [GitHub Repository](https://github.com/smyha/siem-lite)
- [Issue Tracker](https://github.com/smyha/siem-lite/issues)
- [Documentation](https://github.com/smyha/siem-lite/tree/main/docs)
- [Contributing Guide](../CONTRIBUTING.md)
