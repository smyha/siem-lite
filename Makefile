# SIEM Lite - Enhanced Makefile for Development and Production

.PHONY: help install install-dev test lint format type-check security clean setup dev build docker-build docker-run docker-stop production deploy backup monitor docs

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python
PIP := pip
DOCKER := docker
DOCKER_COMPOSE := docker-compose
PROJECT_NAME := siem-lite
DOCKER_IMAGE := $(PROJECT_NAME):latest

help: ## Show this help message
	@echo "SIEM Lite - Security Information and Event Management"
	@echo "======================================================"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation
install: ## Install production dependencies
	$(PIP) install -e .

install-dev: ## Install development dependencies
	$(PIP) install -e ".[dev,test,docs]"
	pre-commit install

# Development
setup: ## Setup development environment
	$(PYTHON) -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  Unix/Mac: source venv/bin/activate"
	@echo "Then run: make install-dev"

dev: ## Start development server
	$(PYTHON) -m uvicorn siem_lite.main:app --reload --host 127.0.0.1 --port 8000

# Testing and Quality
test: ## Run tests
	pytest tests/ -v --cov=siem_lite --cov-report=html --cov-report=term

test-fast: ## Run tests without coverage
	pytest tests/ -v

lint: ## Run linting
	flake8 siem_lite/ tests/
	black --check siem_lite/ tests/
	isort --check-only siem_lite/ tests/

format: ## Format code
	black siem_lite/ tests/
	isort siem_lite/ tests/

type-check: ## Run type checking
	mypy siem_lite/ --ignore-missing-imports

security: ## Run security checks
	bandit -r siem_lite/
	safety check

pre-commit: ## Run all pre-commit checks
	pre-commit run --all-files

# Database
db-init: ## Initialize database
	$(PYTHON) -c "from siem_lite.infrastructure.database import init_database; init_database()"

db-reset: ## Reset database (WARNING: destroys all data)
	powershell -Command "Remove-Item -Force siem_lite.db -ErrorAction SilentlyContinue"
	$(MAKE) db-init

# Docker Development
docker-build: ## Build Docker image
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run: ## Run Docker container
	$(DOCKER) run -p 8000:8000 --env-file .env $(DOCKER_IMAGE)

docker-dev: ## Run development environment with Docker Compose
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml up --build

# Production Deployment
production: ## Deploy to production using Docker Compose
	$(DOCKER_COMPOSE) up -d --build

deploy: ## Full production deployment with health checks
	powershell -Command "& './scripts/deploy.ps1' deploy"

docker-stop: ## Stop Docker containers
	$(DOCKER_COMPOSE) down

docker-logs: ## Show Docker logs
	$(DOCKER_COMPOSE) logs -f

backup: ## Create backup of production data
	powershell -Command "& './scripts/deploy.ps1' backup"

# Monitoring
monitor: ## Open monitoring dashboards
	@echo "Opening monitoring dashboards..."
	@echo "Grafana: http://localhost:3000 (admin/admin123)"
	@echo "Prometheus: http://localhost:9090"
	@echo "API Docs: http://localhost:8000/docs"

health: ## Check system health
	curl -f http://localhost:8000/api/health || echo "API not responding"

metrics: ## Show current metrics
	curl -s http://localhost:8000/api/metrics/alerts || echo "Metrics not available"

# Data Management
generate-logs: ## Generate sample logs for testing
	$(PYTHON) -m siem_lite.cli generate

process-logs: ## Process logs and generate alerts
	$(PYTHON) -m siem_lite.cli process

# Reports
generate-report: ## Generate security report
	$(PYTHON) -c "from siem_lite.infrastructure.report_generator import LaTeXReportGenerator; rg = LaTeXReportGenerator(); rg.generate_security_report()"

# Documentation
docs: ## Generate documentation
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

# Maintenance
clean: ## Clean up temporary files
	powershell -Command "Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue"
	powershell -Command "Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue"
	powershell -Command "Remove-Item -Recurse -Force *.egg-info -ErrorAction SilentlyContinue"
	powershell -Command "Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue"
	powershell -Command "Remove-Item -Force .coverage -ErrorAction SilentlyContinue"
	powershell -Command "Remove-Item -Recurse -Force htmlcov -ErrorAction SilentlyContinue"
	powershell -Command "Get-ChildItem -Recurse -Name __pycache__ | Remove-Item -Recurse -Force"
	powershell -Command "Get-ChildItem -Recurse -Filter '*.pyc' | Remove-Item -Force"

clean-docker: ## Clean up Docker resources
	$(DOCKER) system prune -f
	$(DOCKER) volume prune -f

update: ## Update dependencies
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[dev,test,docs]"

# CI/CD
ci: ## Run CI pipeline locally
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	$(MAKE) test

# CLI Commands
run-api: ## Run the API server
	$(PYTHON) -m siem_lite.cli api

run-dashboard: ## Run the dashboard
	$(PYTHON) -m siem_lite.cli dashboard

setup-siem: ## Setup the SIEM environment
	$(PYTHON) -m siem_lite.cli setup

# Utilities
logs: ## Show application logs
	powershell -Command "Get-Content logs/siem_lite.log -Wait -ErrorAction SilentlyContinue"

shell: ## Open Python shell with app context
	$(PYTHON) -c "from siem_lite.main import app; import IPython; IPython.embed()"

# Environment Management
env-check: ## Check environment configuration
	@echo "Environment Status:"
	@echo "==================="
	@$(PYTHON) --version
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Docker Compose: $$(docker-compose --version 2>/dev/null || echo 'Not installed')"
	@powershell -Command "if (Test-Path .env) { Write-Host '✅ .env file exists' } else { Write-Host '❌ .env file missing' }"

env-create: ## Create .env file from template
	copy .env.example .env
	@echo "✅ .env file created. Please edit it with your settings."

# Quick Start
quick-start: env-create install-dev db-init ## Quick setup for new developers
	@echo ""
	@echo "🎉 Quick start completed!"
	@echo "========================="
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your settings"
	@echo "2. Run 'make dev' to start development server"
	@echo "3. Visit http://localhost:8000/docs for API documentation"
	@echo ""

# Production Quick Deploy
prod-deploy: ## Quick production deployment
	@echo "🚀 Starting production deployment..."
	$(MAKE) env-create
	@echo "Please edit .env file for production settings"
	@pause
	$(MAKE) deploy

build: clean ## Build distribution packages
	$(PYTHON) -m build
