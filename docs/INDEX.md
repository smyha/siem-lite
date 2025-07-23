# 📚 SIEM Lite - Documentation Index

Welcome to the SIEM Lite documentation center. Here you'll find comprehensive information to understand, install, configure, and maintain the system.

## 📖 Documentation Structure

### 🚀 Getting Started
- **[🏠 Main README](../README.md)** - Project overview and quick start
- **[🚀 Deployment Guide](../DEPLOYMENT.md)** - Complete production deployment guide

### 📋 Technical Documentation

#### 🔧 Development and API
- **[📋 API Documentation](./API.md)** - Complete REST API reference
  - All available endpoints
  - Usage examples with curl
  - Response codes and schemas
  - Authentication and security

#### 🏗️ Architecture and Design
- **[🏗️ Architecture Guide](./ARCHITECTURE.md)** - System architecture and patterns
  - Hexagonal architecture (Clean Architecture)
  - Implemented design patterns
  - Data flow and component structure
  - Scalability and performance considerations

#### 🐳 Containerization
- **[🐳 Docker Guide](./DOCKER.md)** - Containerization and orchestration
  - Multi-stage Dockerfile
  - Complete Docker Compose stack
  - Deployment scripts and security configurations
  - Troubleshooting guide

#### 📊 Monitoring and Metrics
- **[📊 Monitoring Guide](./MONITORING.md)** - Metrics and monitoring system
  - Prometheus metrics collection
  - Grafana dashboards configuration
  - Alert rules and notifications
  - Useful queries and troubleshooting

#### 🔄 CI/CD and DevOps
- **[🔄 CI/CD Guide](./CICD.md)** - Complete CI/CD pipeline
  - GitHub Actions workflows
  - Automated testing and security scanning
  - Deployment automation
  - Pipeline monitoring and troubleshooting

#### 📖 Code Documentation
- **[📖 Sphinx Documentation](./_build/html/index.html)** - Auto-generated code documentation
  - Complete API reference
  - Module documentation with type annotations
  - Usage examples and best practices

---

## 🎯 Guides by Audience

### 👨‍💻 Developers
1. Start with **[Architecture Guide](./ARCHITECTURE.md)** to understand the design
2. Review **[API Documentation](./API.md)** to learn the endpoints
3. Check **[Sphinx Documentation](./_build/html/index.html)** for code reference
4. Use **[Docker Guide](./DOCKER.md)** for development environment

### 🔧 DevOps/SRE
1. Begin with **[Docker Guide](./DOCKER.md)** for containerization
2. Implement **[Monitoring Guide](./MONITORING.md)** for observability
3. Configure **[CI/CD Guide](./CICD.md)** for automation
4. Follow **[Deployment Guide](../DEPLOYMENT.md)** for production

### 👨‍💼 System Administrators
1. Start with **[Main README](../README.md)** for overview
2. Use **[Deployment Guide](../DEPLOYMENT.md)** for installation
3. Configure **[Monitoring Guide](./MONITORING.md)** for supervision
4. Reference **[API Documentation](./API.md)** for integrations

### 🔒 Security Analysts
1. Review **[API Documentation](./API.md)** to understand functionality
2. Check **[Architecture Guide](./ARCHITECTURE.md)** for data flow
3. Configure **[Monitoring Guide](./MONITORING.md)** for alerts
4. Use **[Main README](../README.md)** for use cases

---

## 🔗 Quick Links

### 🌐 Service Access (Development/Local)
- **Main API**: http://localhost:8000
- **Swagger Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin_password)
- **Prometheus**: http://localhost:9090
- **Health Check**: http://localhost:8000/api/health

### 📋 Most Used API Endpoints
```bash
# List alerts
curl http://localhost:8000/api/alerts

# Create alert
curl -X POST http://localhost:8000/api/alerts -H "Content-Type: application/json" -d '{"alert_type":"Test","source_ip":"192.168.1.1","details":"Test alert"}'

# Statistics
curl http://localhost:8000/api/stats

# Metrics
curl http://localhost:8000/api/metrics
```

### 🐳 Useful Docker Commands
```bash
# Start complete stack
docker-compose up -d

# View logs
docker-compose logs -f siem-lite

# Service status
docker-compose ps

# Run tests
docker-compose exec siem-lite pytest
```

---

## 🆘 Support and Troubleshooting

### 🐛 Common Issues
1. **Service won't start**: Check [Docker Guide - Troubleshooting](./DOCKER.md#troubleshooting)
2. **API not responding**: Review [API Documentation - Error Codes](./API.md#http-status-codes)
3. **Metrics not showing**: See [Monitoring Guide - Troubleshooting](./MONITORING.md#troubleshooting)
4. **Pipeline failing**: Check [CI/CD Guide - Troubleshooting](./CICD.md#pipeline-troubleshooting)

### 📞 Getting Help
- Check logs: `docker-compose logs -f siem-lite`
- Verify health: `curl http://localhost:8000/api/health`
- Review the specific documentation for your issue
- Check GitHub issues (if applicable)

---

## 🔄 Documentation Updates

This documentation is maintained and updated with each release. Last update: **July 2025**

### 📝 Change History
- **v1.0.0** (July 2025): Complete initial documentation
  - Complete API documentation
  - Detailed architecture guide
  - Docker guide with complete stack
  - Monitoring guide with Prometheus/Grafana
  - CI/CD guide with GitHub Actions
  - Sphinx code documentation

---

**Ready for production!** SIEM Lite is fully implemented and documented, ready for deployment in any environment.
