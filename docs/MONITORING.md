# SIEM Lite - Métricas y Monitoreo

## 📊 Descripción General

SIEM Lite incluye un sistema completo de métricas y monitoreo basado en Prometheus y Grafana, con métricas automáticas para todas las operaciones del sistema.

## 🎯 Métricas Disponibles

### 📈 Contadores (Counters)

#### `siem_alerts_total`
Total de alertas creadas en el sistema.

**Labels:**
- `severity`: Severidad de la alerta (LOW, MEDIUM, HIGH, CRITICAL)
- `alert_type`: Tipo de alerta

**Ejemplo:**
```prometheus
siem_alerts_total{severity="HIGH",alert_type="SSH Brute-Force Attempt"} 25
```

#### `siem_api_requests_total`
Total de requests procesados por la API.

**Labels:**
- `method`: Método HTTP (GET, POST, PUT, DELETE)
- `endpoint`: Endpoint de la API
- `status_code`: Código de estado HTTP

**Ejemplo:**
```prometheus
siem_api_requests_total{method="GET",endpoint="/api/alerts",status_code="200"} 1250
```

#### `siem_alerts_acknowledged_total`
Total de alertas reconocidas.

**Labels:**
- `acknowledged_by`: Usuario que reconoció la alerta

#### `siem_alerts_resolved_total`
Total de alertas resueltas.

**Labels:**
- `resolved_by`: Usuario que resolvió la alerta

---

### ⏱️ Histogramas (Histograms)

#### `siem_alert_processing_duration_seconds`
Tiempo de procesamiento de alertas.

**Buckets:** 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, +Inf

**Labels:**
- `alert_type`: Tipo de alerta procesada

#### `siem_api_request_duration_seconds`
Tiempo de respuesta de la API.

**Buckets:** 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, +Inf

**Labels:**
- `method`: Método HTTP
- `endpoint`: Endpoint de la API

---

### 🔢 Gauges

#### `siem_active_alerts`
Número actual de alertas activas (no resueltas).

**Labels:**
- `severity`: Severidad de las alertas

#### `siem_system_health`
Estado general del sistema (1 = healthy, 0 = unhealthy).

#### `siem_database_connections`
Número de conexiones activas a la base de datos.

#### `siem_unique_source_ips`
Número de IPs únicas que han generado alertas en las últimas 24h.

---

## 🔧 Configuración de Prometheus

### prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'siem-lite'
    static_configs:
      - targets: ['siem-lite:8000']
    metrics_path: '/api/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s
```

### Reglas de Alertas

#### `rules/siem-alerts.yml`
```yaml
groups:
  - name: siem_alerts
    rules:
      # Alta frecuencia de alertas
      - alert: HighAlertRate
        expr: rate(siem_alerts_total[5m]) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Alta frecuencia de alertas detectada"
          description: "Se están creando {{ $value }} alertas por segundo en los últimos 5 minutos"

      # Alertas críticas sin resolver
      - alert: CriticalAlertsUnresolved
        expr: siem_active_alerts{severity="CRITICAL"} > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alertas críticas sin resolver"
          description: "Hay {{ $value }} alertas críticas sin resolver"

      # Sistema no saludable
      - alert: SystemUnhealthy
        expr: siem_system_health == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Sistema SIEM no saludable"
          description: "El sistema SIEM Lite no está respondiendo correctamente"

      # Alto tiempo de respuesta de API
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, rate(siem_api_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alto tiempo de respuesta de API"
          description: "El percentil 95 del tiempo de respuesta es {{ $value }}s"

      # Muchas alertas de un mismo IP
      - alert: SuspiciousIPActivity
        expr: rate(siem_alerts_total[10m]) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Actividad sospechosa de IP"
          description: "IP generando muchas alertas: {{ $value }} por segundo"
```

---

## 📊 Dashboards de Grafana

### Dashboard Principal - SIEM Overview

#### Panel 1: Alertas por Tiempo
```json
{
  "title": "Alertas por Tiempo",
  "type": "graph",
  "targets": [
    {
      "expr": "rate(siem_alerts_total[5m])",
      "legendFormat": "Alertas/seg"
    }
  ]
}
```

#### Panel 2: Distribución por Severidad
```json
{
  "title": "Alertas por Severidad",
  "type": "piechart",
  "targets": [
    {
      "expr": "siem_active_alerts",
      "legendFormat": "{{ severity }}"
    }
  ]
}
```

#### Panel 3: Top IPs Generadoras
```json
{
  "title": "Top IPs Generadoras de Alertas",
  "type": "table",
  "targets": [
    {
      "expr": "topk(10, sum by(source_ip) (siem_alerts_total))",
      "format": "table"
    }
  ]
}
```

#### Panel 4: Tiempo de Respuesta API
```json
{
  "title": "Tiempo de Respuesta API",
  "type": "graph",
  "targets": [
    {
      "expr": "histogram_quantile(0.50, rate(siem_api_request_duration_seconds_bucket[5m]))",
      "legendFormat": "p50"
    },
    {
      "expr": "histogram_quantile(0.95, rate(siem_api_request_duration_seconds_bucket[5m]))",
      "legendFormat": "p95"
    }
  ]
}
```

---

## 🚨 Configuración de Alertas

### Alertmanager Configuration
```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@siem-lite.local'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@company.com'
        subject: 'SIEM Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
    
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#security-alerts'
        title: 'SIEM Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

---

## 📋 Queries Útiles

### Prometheus Queries

#### Alertas por hora en las últimas 24h
```promql
increase(siem_alerts_total[1h])
```

#### Top 5 tipos de alertas
```promql
topk(5, sum by(alert_type) (siem_alerts_total))
```

#### Tasa de alertas críticas
```promql
rate(siem_alerts_total{severity="CRITICAL"}[5m])
```

#### Tiempo promedio de procesamiento
```promql
rate(siem_alert_processing_duration_seconds_sum[5m]) / 
rate(siem_alert_processing_duration_seconds_count[5m])
```

#### Alertas sin resolver por más de 1 hora
```promql
siem_active_alerts * on() (time() - siem_alert_created_time > 3600)
```

---

## 📊 Métricas Personalizadas

### Implementación en Código

```python
from siem_lite.utils.metrics import MetricsCollector

# Inicializar colector
metrics = MetricsCollector()

# Incrementar contador
metrics.alert_counter.labels(
    severity='HIGH',
    alert_type='SSH Brute-Force'
).inc()

# Observar histograma
with metrics.processing_time.labels(alert_type='Port Scan').time():
    # Procesar alerta
    process_alert(alert)

# Establecer gauge
metrics.active_alerts.labels(severity='CRITICAL').set(5)
```

### Decoradores para Métricas Automáticas

```python
from siem_lite.utils.metrics import monitor_api_calls, monitor_processing_time

@monitor_api_calls
@monitor_processing_time
async def create_alert(alert_data):
    # Función automáticamente monitoreada
    return await service.create_alert(alert_data)
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Métricas
ENABLE_METRICS=true
METRICS_PORT=8000
METRICS_PATH=/api/metrics

# Prometheus
PROMETHEUS_URL=http://prometheus:9090
PROMETHEUS_PUSH_GATEWAY=http://pushgateway:9091

# Alertas
ENABLE_ALERTING=true
ALERT_WEBHOOK_URL=https://hooks.slack.com/...
```

### Configuración en Docker Compose

```yaml
version: '3.8'
services:
  siem-lite:
    environment:
      - ENABLE_METRICS=true
      - PROMETHEUS_URL=http://prometheus:9090
    ports:
      - "8000:8000"

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - ./monitoring/grafana:/etc/grafana/provisioning
```

---

## 📈 Monitoreo de Performance

### Métricas de Sistema

- **CPU Usage**: Uso de CPU de la aplicación
- **Memory Usage**: Uso de memoria
- **Disk I/O**: Operaciones de entrada/salida
- **Network Traffic**: Tráfico de red

### Métricas de Aplicación

- **Request Rate**: Requests por segundo
- **Error Rate**: Porcentaje de errores
- **Response Time**: Tiempo de respuesta
- **Throughput**: Alertas procesadas por segundo

### SLAs y SLIs

#### Service Level Indicators (SLIs)
- **Availability**: Uptime del sistema > 99.9%
- **Latency**: P95 < 500ms para requests de API
- **Error Rate**: < 0.1% de requests fallidos
- **Alert Processing**: < 1s para procesar alertas

#### Service Level Objectives (SLOs)
- **API Availability**: 99.9% mensual
- **Alert Processing Time**: 95% < 1 segundo
- **System Recovery**: < 5 minutos tras fallo

---

## 🛠️ Troubleshooting

### Problemas Comunes

#### Métricas no aparecen
```bash
# Verificar endpoint de métricas
curl http://localhost:8000/api/metrics

# Verificar configuración Prometheus
docker logs prometheus_container
```

#### Alertas no se disparan
```bash
# Verificar reglas de Prometheus
curl http://localhost:9090/api/v1/rules

# Verificar Alertmanager
curl http://localhost:9093/api/v1/alerts
```

#### Dashboards no cargan datos
```bash
# Verificar conexión Grafana-Prometheus
# En Grafana: Configuration > Data Sources > Test
```

---

## 📚 Referencias

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [FastAPI Metrics](https://fastapi.tiangolo.com/advanced/middleware/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
