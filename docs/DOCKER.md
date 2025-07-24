# SIEM Lite - Docker and Containerization

## 🐳 Overview

SIEM Lite is fully containerized using Docker and Docker Compose, providing a complete application stack including API, database, monitoring, and reverse proxy.

## 📦 Container Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Docker Compose Stack                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   nginx         │    │   siem-lite     │    │   postgres      │
│   Port 80/443   │────│   Port 8000     │────│   Port 5432     │
│   Reverse Proxy │    │   FastAPI App   │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   redis         │              │
         └──────────────│   Port 6379     │──────────────┘
                        │   Cache         │
                        └─────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   prometheus    │    │   grafana       │    │   alertmanager  │
│   Port 9090     │    │   Port 3000     │    │   Port 9093     │
│   Metrics       │    │   Dashboards    │    │   Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🗂️ Estructura de Archivos Docker

```
siem-lite/
├── Dockerfile                    # Imagen principal de la aplicación
├── docker-compose.yml           # Orquestación completa
├── docker-compose.dev.yml       # Override para desarrollo
├── docker-compose.prod.yml      # Override para producción
├── .dockerignore                 # Archivos excluidos del build
│
├── monitoring/                   # Configuraciones de monitoreo
│   ├── prometheus/
│   │   ├── prometheus.yml        # Config Prometheus
│   │   └── rules/               # Reglas de alertas
│   │       └── siem-alerts.yml
│   └── grafana/
│       ├── dashboards/          # Dashboards pre-configurados
│       │   └── siem-overview.json
│       └── datasources/         # Configuración de fuentes
│           └── prometheus.yml
│
├── nginx/                        # Configuración Nginx
│   ├── nginx.conf               # Configuración principal
│   ├── ssl/                     # Certificados SSL
│   └── sites-enabled/           # Sites habilitados
│
└── scripts/                      # Scripts de deployment
    ├── docker-build.sh          # Build de imágenes
    ├── docker-deploy.sh         # Deploy automático
    └── docker-cleanup.sh        # Limpieza de recursos
```

## 🔧 Dockerfile - Multi-stage Build

```dockerfile
# ============================================
# SIEM Lite - Multi-stage Dockerfile
# ============================================

# Stage 1: Base Python Environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Development
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Set working directory
WORKDIR /app

# Copy source code
COPY --chown=appuser:appgroup . .

# Install application in development mode
RUN pip install -e .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Development command
CMD ["uvicorn", "siem_lite.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 4: Production
FROM dependencies as production

# Set working directory
WORKDIR /app

# Copy source code
COPY --chown=appuser:appgroup . .

# Install application
RUN pip install --no-cache-dir .

# Create required directories
RUN mkdir -p /app/data /app/logs /app/reports && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Production command
CMD ["uvicorn", "siem_lite.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 🐋 Docker Compose - Stack Completo

### docker-compose.yml

```yaml
version: '3.8'

# Networks
networks:
  siem-network:
    driver: bridge
  monitoring-network:
    driver: bridge

# Volumes
volumes:
  postgres_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
  redis_data:
    driver: local

services:
  # ============================================
  # SIEM Lite Application
  # ============================================
  siem-lite:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: siem-lite-app
    restart: unless-stopped
    environment:
      # Database configuration
      - DATABASE_URL=postgresql://siem_user:siem_password@postgres:5432/siem_lite
      
      # Redis configuration
      - REDIS_URL=redis://redis:6379/0
      
      # Application settings
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=INFO
      
      # Security settings
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-change-in-production}
      - ALLOWED_HOSTS=localhost,127.0.0.1,siem-lite
      
      # Monitoring
      - ENABLE_METRICS=true
      - PROMETHEUS_URL=http://prometheus:9090
      
    ports:
      - "8000:8000"
    
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./reports:/app/reports
    
    networks:
      - siem-network
      - monitoring-network
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # ============================================
  # PostgreSQL Database
  # ============================================
  postgres:
    image: postgres:15-alpine
    container_name: siem-lite-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=siem_lite
      - POSTGRES_USER=siem_user
      - POSTGRES_PASSWORD=siem_password
      - POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256
    
    ports:
      - "5432:5432"
    
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    
    networks:
      - siem-network
    
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U siem_user -d siem_lite"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ============================================
  # Redis Cache
  # ============================================
  redis:
    image: redis:7-alpine
    container_name: siem-lite-redis
    restart: unless-stopped
    command: redis-server --requirepass redis_password
    
    ports:
      - "6379:6379"
    
    volumes:
      - redis_data:/data
    
    networks:
      - siem-network
    
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # ============================================
  # Nginx Reverse Proxy
  # ============================================
  nginx:
    image: nginx:alpine
    container_name: siem-lite-nginx
    restart: unless-stopped
    
    ports:
      - "80:80"
      - "443:443"
    
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/sites-enabled:/etc/nginx/sites-enabled:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    
    depends_on:
      - siem-lite
    
    networks:
      - siem-network
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================
  # Prometheus Monitoring
  # ============================================
  prometheus:
    image: prom/prometheus:latest
    container_name: siem-lite-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    
    ports:
      - "9090:9090"
    
    volumes:
      - ./monitoring/prometheus:/etc/prometheus:ro
      - prometheus_data:/prometheus
    
    networks:
      - monitoring-network
    
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================
  # Grafana Dashboards
  # ============================================
  grafana:
    image: grafana/grafana:latest
    container_name: siem-lite-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin_password
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SECURITY_DISABLE_INITIAL_ADMIN_CREATION=false
    
    ports:
      - "3000:3000"
    
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    
    depends_on:
      - prometheus
    
    networks:
      - monitoring-network
    
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:3000/api/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================
  # Alertmanager
  # ============================================
  alertmanager:
    image: prom/alertmanager:latest
    container_name: siem-lite-alertmanager
    restart: unless-stopped
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    
    ports:
      - "9093:9093"
    
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager:ro
    
    networks:
      - monitoring-network
    
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9093/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## ⚙️ Configuraciones Específicas

### .dockerignore

```gitignore
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.pytest_cache
nosetests.xml
coverage.xml
*.cover
*.log
.mypy_cache

# Development
.vscode
.idea
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
*.db
*.sqlite
node_modules
npm-debug.log*
reports/*.pdf
reports/*.json
logs/*.log

# Docker
Dockerfile*
docker-compose*.yml
.dockerignore

# Documentation
README.md
docs/
*.md
```

### docker-compose.dev.yml (Override para Desarrollo)

```yaml
version: '3.8'

services:
  siem-lite:
    build:
      target: development
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - .:/app  # Mount source code for hot reload
    command: ["uvicorn", "siem_lite.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  postgres:
    environment:
      - POSTGRES_DB=siem_lite_dev
    ports:
      - "5433:5432"  # Different port for dev

  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin  # Simple password for dev
```

### docker-compose.prod.yml (Override para Producción)

```yaml
version: '3.8'

services:
  siem-lite:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=WARNING
    command: ["uvicorn", "siem_lite.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

  nginx:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  postgres:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    environment:
      - POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements
      - POSTGRES_MAX_CONNECTIONS=100
```

## 🚀 Scripts de Deployment

### scripts/docker-build.sh

```bash
#!/bin/bash

# ============================================
# SIEM Lite - Docker Build Script
# ============================================

set -e

echo "🐳 Building SIEM Lite Docker images..."

# Build arguments
BUILD_ARGS=""
if [ ! -z "$BUILD_TARGET" ]; then
    BUILD_ARGS="--target $BUILD_TARGET"
fi

# Build the main application image
echo "📦 Building main application image..."
docker build $BUILD_ARGS -t siem-lite:latest .

# Build with version tag if provided
if [ ! -z "$VERSION" ]; then
    echo "🏷️  Tagging with version: $VERSION"
    docker tag siem-lite:latest siem-lite:$VERSION
fi

# Prune unused images
echo "🧹 Cleaning up unused images..."
docker image prune -f

echo "✅ Build completed successfully!"

# Show built images
echo "📋 Built images:"
docker images siem-lite
```

### scripts/docker-deploy.sh

```bash
#!/bin/bash

# ============================================
# SIEM Lite - Docker Deploy Script
# ============================================

set -e

ENVIRONMENT=${1:-development}
COMPOSE_FILE="docker-compose.yml"

case $ENVIRONMENT in
    "dev"|"development")
        COMPOSE_FILE="docker-compose.yml -f docker-compose.dev.yml"
        ;;
    "prod"|"production")
        COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"
        ;;
esac

echo "🚀 Deploying SIEM Lite to $ENVIRONMENT environment..."

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose -f $COMPOSE_FILE pull

# Build custom images
echo "🔨 Building custom images..."
docker-compose -f $COMPOSE_FILE build

# Start services
echo "▶️  Starting services..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo "🔍 Waiting for services to be healthy..."
sleep 30

# Check service health
echo "❤️  Checking service health..."
docker-compose -f $COMPOSE_FILE ps

# Run health checks
echo "🩺 Running health checks..."
curl -f http://localhost:8000/api/health || echo "❌ SIEM Lite health check failed"
curl -f http://localhost:9090/-/healthy || echo "❌ Prometheus health check failed"
curl -f http://localhost:3000/api/health || echo "❌ Grafana health check failed"

echo "✅ Deployment completed!"
echo "🌐 Services available at:"
echo "   - SIEM Lite API: http://localhost:8000"
echo "   - Grafana: http://localhost:3000"
echo "   - Prometheus: http://localhost:9090"
```

### scripts/docker-cleanup.sh

```bash
#!/bin/bash

# ============================================
# SIEM Lite - Docker Cleanup Script
# ============================================

echo "🧹 Cleaning up Docker resources..."

# Stop all containers
echo "⏹️  Stopping all containers..."
docker-compose down

# Remove unused images
echo "🖼️  Removing unused images..."
docker image prune -f

# Remove unused volumes (be careful in production!)
if [ "$1" == "--volumes" ]; then
    echo "💾 Removing unused volumes..."
    docker volume prune -f
fi

# Remove unused networks
echo "🌐 Removing unused networks..."
docker network prune -f

# Show remaining resources
echo "📊 Remaining Docker resources:"
echo "Images:"
docker images
echo ""
echo "Containers:"
docker ps -a
echo ""
echo "Volumes:"
docker volume ls

echo "✅ Cleanup completed!"
```

## 🔧 Comandos Útiles

### Desarrollo

```bash
# Iniciar en modo desarrollo
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Ver logs en tiempo real
docker-compose logs -f siem-lite

# Ejecutar tests dentro del contenedor
docker-compose exec siem-lite pytest

# Acceder al shell del contenedor
docker-compose exec siem-lite bash

# Reiniciar un servicio específico
docker-compose restart siem-lite
```

### Producción

```bash
# Deploy en producción
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Escalar la aplicación
docker-compose up -d --scale siem-lite=3

# Ver estadísticas de recursos
docker stats

# Backup de base de datos
docker-compose exec postgres pg_dump -U siem_user siem_lite > backup.sql
```

### Monitoreo

```bash
# Ver estado de todos los servicios
docker-compose ps

# Verificar health checks
docker-compose exec siem-lite curl http://localhost:8000/api/health

# Ver métricas de Prometheus
curl http://localhost:9090/api/v1/query?query=siem_alerts_total

# Acceder a Grafana
open http://localhost:3000
```

## 📊 Monitoreo de Contenedores

### Métricas de Docker

```yaml
# Agregar al docker-compose.yml para monitoreo
services:
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    networks:
      - monitoring-network

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    restart: unless-stopped
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    networks:
      - monitoring-network
```

## 🔒 Seguridad en Contenedores

### Mejores Prácticas Implementadas

1. **Usuario no-root**: Todos los contenedores corren con usuario dedicado
2. **Multi-stage builds**: Imágenes optimizadas sin herramientas de desarrollo
3. **Health checks**: Monitoreo automático de la salud de contenedores
4. **Secrets management**: Variables de entorno para datos sensibles
5. **Network isolation**: Redes separadas para diferentes servicios
6. **Resource limits**: Límites de CPU y memoria definidos

### Escaneo de Vulnerabilidades

```bash
# Escanear imagen con Trivy
trivy image siem-lite:latest

# Escanear con Docker Scout
docker scout cves siem-lite:latest

# Análisis de seguridad con Snyk
snyk container test siem-lite:latest
```

## 📋 Troubleshooting

### Problemas Comunes

#### Contenedor no inicia
```bash
# Ver logs detallados
docker-compose logs siem-lite

# Verificar configuración
docker-compose config

# Verificar recursos del sistema
docker system df
```

#### Base de datos no conecta
```bash
# Verificar estado de PostgreSQL
docker-compose exec postgres pg_isready -U siem_user

# Ver logs de PostgreSQL
docker-compose logs postgres

# Conectar manualmente
docker-compose exec postgres psql -U siem_user -d siem_lite
```

#### Prometheus no recolecta métricas
```bash
# Verificar configuración
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# Ver targets en Prometheus
curl http://localhost:9090/api/v1/targets

# Verificar endpoint de métricas
curl http://localhost:8000/api/metrics
```

## 🔄 Actualizaciones y Rollbacks

### Rolling Updates

```bash
# Actualización sin downtime
docker-compose pull siem-lite
docker-compose up -d --no-deps siem-lite

# Verificar que la actualización fue exitosa
curl http://localhost:8000/api/health
```

### Rollback

```bash
# Rollback a versión anterior
docker tag siem-lite:v1.0.0 siem-lite:latest
docker-compose up -d --no-deps siem-lite

# Verificar rollback
docker-compose ps
```

Esta documentación proporciona una guía completa para trabajar con la containerización de SIEM Lite, desde el desarrollo hasta la producción.
