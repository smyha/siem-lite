# SIEM Lite API Documentation

## 🚀 Overview

SIEM Lite API is a comprehensive REST API built with FastAPI that provides security alert management, monitoring, and system statistics functionalities.

## 📋 Available Endpoints

### 🏠 Root Endpoint

#### `GET /`
System root endpoint.

**Response:**
```json
{
  "message": "SIEM Lite API - Security Information and Event Management",
  "version": "1.0.0",
  "status": "operational"
}
```

---

### 🚨 Alerts

#### `GET /api/alerts`
Lists all alerts with pagination.

**Query parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 10)
- `severity` (string, optional): Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
- `status` (string, optional): Filter by status (OPEN, ACKNOWLEDGED, RESOLVED)
- `alert_type` (string, optional): Filter by alert type

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "alert_type": "SSH Brute-Force Attempt",
      "source_ip": "192.168.1.100",
      "details": "Detected 5 failed login attempts in 60 seconds",
      "timestamp": "2025-07-23T10:30:00Z",
      "severity": "HIGH",
      "status": "OPEN",
      "assigned_to": null,
      "resolved_at": null,
      "metadata": {},
      "updated_at": "2025-07-23T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "has_next": false,
  "has_prev": false
}
```

#### `POST /api/alerts`
Creates a new alert.

**Request body:**
```json
{
  "alert_type": "SSH Brute-Force Attempt",
  "source_ip": "192.168.1.100",
  "details": "Detected 5 failed login attempts in 60 seconds",
  "severity": "HIGH"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "alert_type": "SSH Brute-Force Attempt",
  "source_ip": "192.168.1.100",
  "details": "Detected 5 failed login attempts in 60 seconds",
  "timestamp": "2025-07-23T10:30:00Z",
  "severity": "HIGH",
  "status": "OPEN",
  "assigned_to": null,
  "resolved_at": null,
  "metadata": {},
  "updated_at": "2025-07-23T10:30:00Z"
}
```

#### `GET /api/alerts/{id}`
Gets a specific alert by ID.

**Parameters:**
- `id` (int): Alert ID

**Response:** `200 OK` (same structure as POST)

#### `PUT /api/alerts/{id}`
Updates an existing alert.

**Parameters:**
- `id` (int): Alert ID

**Request body:**
```json
{
  "alert_type": "SSH Brute-Force Attempt",
  "source_ip": "192.168.1.100",
  "details": "Updated details",
  "severity": "CRITICAL",
  "status": "ACKNOWLEDGED"
}
```

**Respuesta:** `200 OK`

#### `DELETE /api/alerts/{id}`
Elimina una alerta.

**Parámetros:**
- `id` (int): ID de la alerta

**Respuesta:** `204 No Content`

#### `POST /api/alerts/{id}/acknowledge`
Reconoce una alerta (cambia estado a ACKNOWLEDGED).

**Parámetros:**
- `id` (int): ID de la alerta

**Cuerpo de la petición:**
```json
{
  "acknowledged_by": "admin_user",
  "notes": "Investigating the incident"
}
```

**Respuesta:** `200 OK`

#### `POST /api/alerts/{id}/resolve`
Resuelve una alerta (cambia estado a RESOLVED).

**Parámetros:**
- `id` (int): ID de la alerta

**Cuerpo de la petición:**
```json
{
  "resolved_by": "admin_user",
  "resolution_notes": "False positive - IP whitelisted"
}
```

**Respuesta:** `200 OK`

---

### 📊 Estadísticas (Statistics)

#### `GET /api/stats`
Obtiene estadísticas generales del sistema.

**Respuesta:**
```json
{
  "total_alerts": 150,
  "recent_alerts_24h": 25,
  "alerts_by_severity": {
    "LOW": 50,
    "MEDIUM": 75,
    "HIGH": 20,
    "CRITICAL": 5
  },
  "alerts_by_status": {
    "OPEN": 30,
    "ACKNOWLEDGED": 15,
    "RESOLVED": 105
  },
  "alert_types": {
    "SSH Brute-Force Attempt": 45,
    "Suspicious File Access": 30,
    "Port Scan Detected": 25,
    "Login Anomaly": 20,
    "Other": 30
  },
  "top_source_ips": {
    "192.168.1.100": 15,
    "10.0.0.50": 12,
    "172.16.0.25": 8
  },
  "unique_ips": 45
}
```

#### `GET /api/trends`
Obtiene tendencias temporales de alertas.

**Respuesta:**
```json
{
  "alerts": {
    "1h": 5,
    "24h": 25,
    "7d": 120,
    "30d": 400
  },
  "top_sources": [
    {
      "ip": "192.168.1.100",
      "count": 15
    },
    {
      "ip": "10.0.0.50",
      "count": 12
    }
  ],
  "patterns": [
    {
      "type": "SSH Brute-Force Attempt",
      "count": 18
    },
    {
      "type": "Port Scan Detected",
      "count": 7
    }
  ]
}
```

---

### ❤️ Health Check

#### `GET /api/health`
Verifica el estado de salud del sistema.

**Parámetros de consulta:**
- `detailed` (bool, opcional): Incluir información detallada

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-23T10:30:00Z",
  "database": "connected"
}
```

**Respuesta detallada (`?detailed=true`):**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-23T10:30:00Z",
  "database": "connected",
  "details": {
    "database_engine": "sqlite",
    "total_alerts": 150,
    "recent_alerts_24h": 25,
    "api_version": "1.0.0",
    "python_version": "3.8+",
    "uptime": "healthy"
  }
}
```

---

### 📈 Métricas (Metrics)

#### `GET /api/metrics`
Endpoint para Prometheus - métricas del sistema en formato Prometheus.

**Respuesta:** `text/plain`
```
# HELP siem_alerts_total Total number of alerts
# TYPE siem_alerts_total counter
siem_alerts_total 150

# HELP siem_api_requests_total Total API requests
# TYPE siem_api_requests_total counter
siem_api_requests_total{method="GET",endpoint="/api/alerts"} 1250

# HELP siem_alert_processing_duration_seconds Alert processing time
# TYPE siem_alert_processing_duration_seconds histogram
siem_alert_processing_duration_seconds_bucket{le="0.1"} 95
siem_alert_processing_duration_seconds_bucket{le="0.5"} 148
siem_alert_processing_duration_seconds_bucket{le="1.0"} 150
siem_alert_processing_duration_seconds_bucket{le="+Inf"} 150

# HELP siem_active_alerts Number of active alerts
# TYPE siem_active_alerts gauge
siem_active_alerts 45
```

---

## 🔒 Autenticación y Seguridad

### Headers de Seguridad
Todas las respuestas incluyen headers de seguridad:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### CORS
- Configurado para permitir orígenes específicos
- Métodos permitidos: GET, POST, PUT, DELETE
- Headers permitidos: Authorization, Content-Type

### Rate Limiting
- Implementado middleware de rate limiting
- Validación de tamaño de request
- Protección contra ataques de denegación de servicio

---

## 📝 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200    | OK - Operación exitosa |
| 201    | Created - Recurso creado exitosamente |
| 204    | No Content - Operación exitosa sin contenido |
| 400    | Bad Request - Error en los datos enviados |
| 404    | Not Found - Recurso no encontrado |
| 422    | Unprocessable Entity - Error de validación |
| 500    | Internal Server Error - Error interno del servidor |

---

## 🛠️ Ejemplos de Uso

### Crear una alerta
```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "Suspicious Login",
    "source_ip": "192.168.1.50",
    "details": "Login from unusual location",
    "severity": "MEDIUM"
  }'
```

### Listar alertas con filtros
```bash
curl "http://localhost:8000/api/alerts?severity=HIGH&status=OPEN&page=1&limit=5"
```

### Reconocer una alerta
```bash
curl -X POST "http://localhost:8000/api/alerts/1/acknowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "acknowledged_by": "security_analyst",
    "notes": "Investigating this incident"
  }'
```

### Obtener estadísticas
```bash
curl "http://localhost:8000/api/stats"
```

---

## 📋 Tipos de Datos

### AlertSeverity
- `LOW` - Severidad baja
- `MEDIUM` - Severidad media
- `HIGH` - Severidad alta
- `CRITICAL` - Severidad crítica

### AlertStatus
- `OPEN` - Alerta nueva/abierta
- `ACKNOWLEDGED` - Alerta reconocida
- `RESOLVED` - Alerta resuelta

### Tipos de Alerta Comunes
- `SSH Brute-Force Attempt`
- `Suspicious File Access`
- `Port Scan Detected`
- `Login Anomaly`
- `DDoS Attack`
- `Malware Detection`
- `Unauthorized Access`
- `Data Exfiltration`

---

## 🔗 Documentación Interactiva

Cuando el modo debug está activado, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## 📞 Soporte

Para más información sobre la implementación, consulta:
- [Arquitectura del Sistema](./ARCHITECTURE.md)
- [Guía de Deployment](../DEPLOYMENT.md)
- [Métricas y Monitoreo](./MONITORING.md)
