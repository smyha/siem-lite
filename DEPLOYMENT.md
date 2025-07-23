# SIEM Lite - Production Deployment Guide

This guide provides comprehensive instructions for deploying SIEM Lite to production environments.

## Prerequisites

- Docker and Docker Compose installed
- Minimum 2GB RAM, 2 CPU cores
- 10GB available disk space
- Python 3.9+ (for local development)
- Network access for external dependencies

## Quick Start with Docker

### 1. Clone and Setup

```bash
git clone <repository-url>
cd siem-lite
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with production settings:

```bash
# Application
SIEM_LITE_ENV=production
LOG_LEVEL=INFO
SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=sqlite:///data/siem_lite.db

# Security
ALLOWED_HOSTS=your-domain.com,localhost
CORS_ORIGINS=https://your-domain.com

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=secure-password
```

### 3. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f siem-lite
```

### 4. Verify Deployment

- Application: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Grafana Dashboard: http://localhost:3000 (admin/admin123)
- Prometheus: http://localhost:9090

## Production Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SIEM_LITE_ENV` | Environment (production/development) | development | Yes |
| `SECRET_KEY` | JWT secret key | generated | Yes |
| `DATABASE_URL` | Database connection string | sqlite:///siem_lite.db | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO | No |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | * | Yes |
| `CORS_ORIGINS` | Comma-separated CORS origins | http://localhost:3000 | No |
| `PROMETHEUS_ENABLED` | Enable Prometheus metrics | true | No |

### SSL/TLS Configuration

For production, configure SSL certificates:

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Add your SSL certificates
cp your-cert.pem nginx/ssl/
cp your-key.pem nginx/ssl/
```

Update `nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/your-cert.pem;
    ssl_certificate_key /etc/nginx/ssl/your-key.pem;
    
    location / {
        proxy_pass http://siem-lite:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Database Setup

### SQLite (Default)

SQLite is used by default for simplicity:

```bash
# Database will be created automatically in data/siem_lite.db
# Ensure proper permissions
chmod 644 data/siem_lite.db
```

### PostgreSQL (Recommended for Production)

For better performance and concurrent access:

```yaml
# Add to docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: siem_lite
      POSTGRES_USER: siem_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

Update environment:
```bash
DATABASE_URL=postgresql://siem_user:secure_password@postgres:5432/siem_lite
```

## Monitoring Setup

### Prometheus Configuration

The included Prometheus setup monitors:
- HTTP request metrics
- Alert generation rates
- System health
- Response times
- Error rates

### Grafana Dashboards

Access Grafana at http://localhost:3000:
- Default login: admin/admin123
- Pre-configured dashboards available
- Alerts configured for critical metrics

### Custom Alerts

Edit `monitoring/prometheus/rules/siem_lite_rules.yml` to customize alerting rules.

## Performance Tuning

### Application Level

```bash
# Increase worker processes
uvicorn siem_lite.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Database Optimization

```sql
-- For PostgreSQL
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX idx_alerts_source_ip ON alerts(source_ip);
CREATE INDEX idx_alerts_status ON alerts(status);
```

### Caching

Enable Redis for session management:

```yaml
# In docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
```

## Security Hardening

### 1. Network Security

```bash
# Use firewall to restrict access
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 8000/tcp  # Block direct API access
```

### 2. Container Security

```bash
# Run containers as non-root
USER siem:siem

# Limit resources
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

### 3. Secrets Management

Use Docker secrets or external secret management:

```yaml
secrets:
  secret_key:
    external: true
  db_password:
    external: true
```

## Backup and Recovery

### Database Backup

```bash
# SQLite backup
docker exec siem-lite-app cp /app/data/siem_lite.db /app/backups/backup-$(date +%Y%m%d).db

# PostgreSQL backup
docker exec postgres pg_dump -U siem_user siem_lite > backup-$(date +%Y%m%d).sql
```

### Application Data Backup

```bash
# Backup reports and logs
tar -czf siem-backup-$(date +%Y%m%d).tar.gz data/ reports/ logs/
```

### Restore Procedure

```bash
# Stop services
docker-compose down

# Restore database
cp backup-20231201.db data/siem_lite.db

# Restart services
docker-compose up -d
```

## Health Monitoring

### Health Check Endpoints

- `/api/health` - Basic health status
- `/api/health?detailed=true` - Detailed system information
- `/api/metrics` - Prometheus metrics
- `/api/stats` - Application statistics

### Log Monitoring

```bash
# Monitor application logs
docker-compose logs -f siem-lite

# Monitor all services
docker-compose logs -f
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready
   
   # Restart database
   docker-compose restart postgres
   ```

2. **High Memory Usage**
   ```bash
   # Check container resource usage
   docker stats
   
   # Restart application
   docker-compose restart siem-lite
   ```

3. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R 1000:1000 data/ reports/ logs/
   ```

### Log Analysis

```bash
# Check error logs
docker-compose logs siem-lite | grep ERROR

# Monitor real-time logs
docker-compose logs -f --tail=100 siem-lite
```

## Scaling

### Horizontal Scaling

```yaml
# Scale API instances
services:
  siem-lite:
    deploy:
      replicas: 3
```

### Load Balancing

Use nginx or external load balancer:

```nginx
upstream siem_backend {
    server siem-lite-1:8000;
    server siem-lite-2:8000;
    server siem-lite-3:8000;
}
```

## Maintenance

### Regular Tasks

1. **Log Rotation**
   ```bash
   # Configure logrotate
   echo "/app/logs/*.log {
       daily
       missingok
       rotate 7
       compress
   }" > /etc/logrotate.d/siem-lite
   ```

2. **Database Cleanup**
   ```sql
   -- Remove old alerts (older than 90 days)
   DELETE FROM alerts WHERE timestamp < NOW() - INTERVAL '90 days';
   ```

3. **Update Dependencies**
   ```bash
   # Update Docker images
   docker-compose pull
   docker-compose up -d
   ```

### Monitoring Checklist

- [ ] Application health endpoints responding
- [ ] Prometheus metrics being collected
- [ ] Grafana dashboards displaying data
- [ ] Log files being generated
- [ ] Database connections healthy
- [ ] SSL certificates valid
- [ ] Backups running successfully

## Support and Documentation

- Application logs: `/app/logs/`
- Health check: `GET /api/health`
- API documentation: `GET /docs`
- Metrics endpoint: `GET /api/metrics`
- Grafana dashboards: `http://localhost:3000`

For additional support, check the troubleshooting section or review application logs.
