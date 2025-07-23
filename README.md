# 🛡️ SIEM Lite - Security Information and Event Management

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the modern REST API framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for powerful database ORM (2.0+ ready)
- [Pydantic V2](https://docs.pydantic.dev/latest/) for high-performance data validation
- [Sphinx](https://www.sphinx-doc.org/) for professional documentation generation
- [pytest](https://pytest.org/) for comprehensive testing frameworkcker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A lightweight Security Information and Event Management system built with FastAPI, designed to detect, analyze and manage security events in real-time.

## 🎯 Key Features

- **🔍 Event Detection**: Real-time security log analysis
- **📊 Web Dashboard**: Intuitive interface for monitoring and management
- **🚨 Alert System**: Automatic notifications for critical events
- **📈 Metrics & Reports**: Statistical analysis and report generation
- **🐳 Containerization**: Easy deployment with Docker and Docker Compose
- **📊 Monitoring**: Integration with Prometheus and Grafana
- **🔄 CI/CD**: Automated pipeline with GitHub Actions

## 📚 Documentation

### 📖 Main Guides
- **[� Execution Guide](./EXECUTION_GUIDE.md)** - Step-by-step setup and troubleshooting
- **[�📋 API Documentation](./docs/API.md)** - Complete REST API documentation
- **[🏗️ Architecture Guide](./docs/ARCHITECTURE.md)** - System architecture and design patterns
- **[🐳 Docker Guide](./docs/DOCKER.md)** - Complete containerization and orchestration
- **[📊 Monitoring Guide](./docs/MONITORING.md)** - Prometheus/Grafana metrics system
- **[🔄 CI/CD Guide](./docs/CICD.md)** - Complete CI/CD pipeline with GitHub Actions
- **[📖 Code Documentation](./docs/_build/html/index.html)** - Sphinx-generated API reference

## 🏛️ Architecture

SIEM Lite follows Clean Architecture principles with clear separation of concerns:

```
siem_lite/
├── api/                    # REST API endpoints (FastAPI)
├── domain/                 # Business logic (framework-independent)
├── infrastructure/        # External concerns (database, files, etc.)
├── utils/                  # Shared utilities
├── cli.py                  # Command-line interface
└── main.py                 # FastAPI application
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (recommended: Python 3.11+)
- pip package manager
- Git (for cloning the repository)

### Installation & Usage

#### 1. **Clone and Setup**
```bash
# Clone the repository
git clone https://github.com/siem-lite/siem-lite.git
cd siem-lite

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. **Initialize Database**
```bash
python -c "from siem_lite.infrastructure.database import init_database; init_database()"
```

#### 3. **Start the Server**
```bash
# Development mode (with auto-reload)
uvicorn siem_lite.main:app --reload --host 127.0.0.1 --port 8000

# Production mode
uvicorn siem_lite.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 4. **Access the Application**
- **📚 API Documentation:** http://127.0.0.1:8000/docs
- **❤️ Health Check:** http://127.0.0.1:8000/api/health
- **🚨 Alerts API:** http://127.0.0.1:8000/api/alerts

#### 5. **Quick Test**
```bash
# Run automated tests
python -m pytest tests/ -v

# Test API endpoints
python test_api.py
```

### 🐳 Docker Option (Alternative)

```bash
# Start with Docker Compose
docker-compose up -d

# Access services
# API: http://localhost:8000
# Grafana: http://localhost:3000 (admin/admin_password)
# Prometheus: http://localhost:9090
```

## 📋 Main API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/alerts` | List alerts (with pagination) |
| `POST` | `/api/alerts` | Create new alert |
| `GET` | `/api/alerts/{id}` | Get specific alert |
| `PUT` | `/api/alerts/{id}` | Update alert |
| `DELETE` | `/api/alerts/{id}` | Delete alert |
| `POST` | `/api/alerts/{id}/acknowledge` | Acknowledge alert |
| `POST` | `/api/alerts/{id}/resolve` | Resolve alert |
| `GET` | `/api/stats` | System statistics |
| `GET` | `/api/health` | Health status |
| `GET` | `/api/metrics` | Prometheus metrics |

## 🔗 How to Use

### Creating Alerts
```bash
# Create a new alert via API
curl -X POST "http://127.0.0.1:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "SSH Brute Force",
    "source_ip": "192.168.1.100",
    "details": "Detected 5 failed login attempts"
  }'
```

### Listing Alerts
```bash
# Get all alerts
curl "http://127.0.0.1:8000/api/alerts"

# Get alerts with pagination
curl "http://127.0.0.1:8000/api/alerts?skip=0&limit=10"

# Filter alerts by severity
curl "http://127.0.0.1:8000/api/alerts?severity=HIGH"
```

### System Monitoring
```bash
# Check system health
curl "http://127.0.0.1:8000/api/health"

# Get detailed health info
curl "http://127.0.0.1:8000/api/health?detailed=true"

# Get system statistics
curl "http://127.0.0.1:8000/api/stats"
```

### Interactive Documentation
Access the Swagger UI at `http://127.0.0.1:8000/docs` to:
- 🔍 Explore all available endpoints
- 🧪 Test API calls directly in the browser
- 📖 View detailed request/response schemas
- 🔐 Test authentication features

## 🔧 Configuration

### Environment Variables

Key configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `DATABASE_URL` | Database connection string | `sqlite:///./siem_lite.db` |
| `API_HOST` | API server host | `127.0.0.1` |
| `API_PORT` | API server port | `8000` |
| `SECRET_KEY` | Secret key for JWT tokens | `your-secret-key` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🧪 Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest --cov=siem_lite --cov-report=html

# Build documentation
cd docs/
make html
```

### Code Documentation

This project uses **Sphinx** for comprehensive code documentation. To build and view the documentation:

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Build documentation
cd docs/
make html

# View documentation
# Open docs/_build/html/index.html in your browser
```

The Sphinx documentation includes:
- **API Reference**: Auto-generated from docstrings
- **Module Documentation**: Detailed description of each module
- **Type Annotations**: Complete type information
- **Examples**: Usage examples for all public APIs

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper tests and documentation
4. **Run the test suite:** `pytest`
5. **Commit your changes:** `git commit -m 'Add amazing feature'`
6. **Push to the branch:** `git push origin feature/amazing-feature`
7. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Code Documentation:** [Sphinx Documentation](./docs/_build/html/index.html)
- **API Reference:** [API Documentation](./docs/API.md)
- **Issues:** [GitHub Issues](https://github.com/siem-lite/siem-lite/issues)

## �🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the REST API
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [Sphinx](https://www.sphinx-doc.org/) for documentation generation
