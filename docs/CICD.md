# SIEM Lite - CI/CD y DevOps

## 🔄 Descripción General

SIEM Lite implementa un pipeline completo de CI/CD usando GitHub Actions, con automatización para testing, seguridad, building y deployment. El sistema está diseñado siguiendo las mejores prácticas de DevOps.

## 🏗️ Arquitectura del Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CI/CD Pipeline                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Trigger   │    │    Test     │    │   Security  │    │    Build    │
│             │────│             │────│             │────│             │
│ Push/PR     │    │ Unit Tests  │    │ SAST/DAST   │    │ Docker      │
│             │    │ Integration │    │ Vuln Scan   │    │ Multi-arch  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│   Deploy    │    │   Monitor   │    │   Notify    │           │
│             │────│             │────│             │───────────┘
│ Staging     │    │ Health      │    │ Slack/Email │
│ Production  │    │ Metrics     │    │ Teams       │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 📋 Workflows de GitHub Actions

### Principal CI/CD Pipeline

#### `.github/workflows/ci-cd.yml`

```yaml
name: 🚀 CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

env:
  PYTHON_VERSION: '3.11'
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ============================================
  # Testing Stage
  # ============================================
  test:
    name: 🧪 Test Suite
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_siem_lite
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🐍 Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: 📦 Cache Dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: 🔧 Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: 🧹 Lint with flake8
        run: |
          flake8 siem_lite tests --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 siem_lite tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

      - name: 🔍 Type Checking with mypy
        run: |
          mypy siem_lite --ignore-missing-imports

      - name: 🧪 Run Tests with Coverage
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_siem_lite
          REDIS_URL: redis://localhost:6379/0
          ENVIRONMENT: testing
        run: |
          pytest tests/ --cov=siem_lite --cov-report=xml --cov-report=term-missing -v

      - name: 📊 Upload Coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella

      - name: 📈 SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  # ============================================
  # Security Scanning
  # ============================================
  security:
    name: 🔒 Security Scan
    runs-on: ubuntu-latest
    needs: test

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: 🔧 Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install bandit safety

      - name: 🛡️ Run Bandit Security Scan
        run: |
          bandit -r siem_lite -f json -o bandit-report.json || true
          bandit -r siem_lite

      - name: 🔐 Check Dependencies with Safety
        run: |
          safety check --json --output safety-report.json || true
          safety check

      - name: 🔍 Snyk Security Scan
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: 📋 Upload Security Reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json

  # ============================================
  # Build Docker Images
  # ============================================
  build:
    name: 🐳 Build Docker Images
    runs-on: ubuntu-latest
    needs: [test, security]
    
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
      image-tags: ${{ steps.meta.outputs.tags }}

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🐳 Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: 🔑 Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.DOCKER_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: 📝 Extract Metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-

      - name: 🏗️ Build and Push Docker Image
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          target: production

      - name: 🔍 Scan Docker Image with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: 📊 Upload Trivy Results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

  # ============================================
  # Deploy to Staging
  # ============================================
  deploy-staging:
    name: 🚀 Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    
    environment:
      name: staging
      url: https://staging.siem-lite.example.com

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🔧 Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.0'

      - name: 🔑 Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: 📦 Deploy to EKS Staging
        run: |
          aws eks update-kubeconfig --name siem-lite-staging
          kubectl set image deployment/siem-lite siem-lite=${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          kubectl rollout status deployment/siem-lite --timeout=300s

      - name: 🩺 Health Check
        run: |
          sleep 60
          curl -f https://staging.siem-lite.example.com/api/health

      - name: 🧪 Run Smoke Tests
        run: |
          python -m pytest tests/smoke/ --base-url=https://staging.siem-lite.example.com

  # ============================================
  # Deploy to Production
  # ============================================
  deploy-production:
    name: 🚀 Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'release'
    
    environment:
      name: production
      url: https://siem-lite.example.com

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🔧 Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.0'

      - name: 🔑 Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: 📦 Deploy to EKS Production
        run: |
          aws eks update-kubeconfig --name siem-lite-production
          kubectl set image deployment/siem-lite siem-lite=${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.ref_name }}
          kubectl rollout status deployment/siem-lite --timeout=300s

      - name: 🩺 Health Check
        run: |
          sleep 60
          curl -f https://siem-lite.example.com/api/health

      - name: 🧪 Run End-to-End Tests
        run: |
          python -m pytest tests/e2e/ --base-url=https://siem-lite.example.com

      - name: 📢 Notify Deployment Success
        uses: 8398a7/action-slack@v3
        with:
          status: success
          channel: '#deployments'
          message: '🚀 SIEM Lite ${{ github.ref_name }} deployed to production successfully!'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

  # ============================================
  # Performance Testing
  # ============================================
  performance:
    name: ⚡ Performance Tests
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/develop'

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🔧 Setup K6
        run: |
          sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: 🚀 Run Load Tests
        run: |
          k6 run tests/performance/load-test.js --env BASE_URL=https://staging.siem-lite.example.com

      - name: 📊 Upload Performance Results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: performance-results.json
```

### Security-focused Workflow

#### `.github/workflows/security.yml`

```yaml
name: 🔒 Security Scanning

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:
  push:
    paths:
      - 'requirements*.txt'
      - 'Dockerfile'
      - '.github/workflows/security.yml'

jobs:
  # ============================================
  # Dependency Scanning
  # ============================================
  dependency-scan:
    name: 📦 Dependency Security Scan
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: 🔧 Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install safety pip-audit

      - name: 🔐 Safety Check
        run: |
          safety check --json --output safety-report.json
          safety check --short-report

      - name: 🔍 Pip Audit
        run: |
          pip-audit --format=json --output=pip-audit-report.json
          pip-audit

      - name: 📋 Upload Reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: dependency-scan-reports
          path: |
            safety-report.json
            pip-audit-report.json

  # ============================================
  # Container Security
  # ============================================
  container-scan:
    name: 🐳 Container Security Scan
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🐳 Build Docker Image
        run: |
          docker build -t siem-lite:security-scan .

      - name: 🔍 Run Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'siem-lite:security-scan'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'

      - name: 🛡️ Run Docker Bench Security
        run: |
          docker run --rm --net host --pid host --userns host --cap-add audit_control \
            -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
            -v /etc:/etc:ro \
            -v /usr/bin/containerd:/usr/bin/containerd:ro \
            -v /usr/bin/runc:/usr/bin/runc:ro \
            -v /usr/lib/systemd:/usr/lib/systemd:ro \
            -v /var/lib:/var/lib:ro \
            -v /var/run/docker.sock:/var/run/docker.sock:ro \
            --label docker_bench_security \
            docker/docker-bench-security

  # ============================================
  # SAST (Static Application Security Testing)
  # ============================================
  sast:
    name: 🔬 Static Application Security Testing
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: 🔧 Install SAST Tools
        run: |
          python -m pip install --upgrade pip
          pip install bandit semgrep

      - name: 🛡️ Run Bandit
        run: |
          bandit -r siem_lite -f json -o bandit-results.json
          bandit -r siem_lite

      - name: 🔍 Run Semgrep
        run: |
          semgrep --config=auto --json --output=semgrep-results.json siem_lite/
          semgrep --config=auto siem_lite/

      - name: 📊 CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          languages: python

      - name: 📋 Upload SAST Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: sast-results
          path: |
            bandit-results.json
            semgrep-results.json

  # ============================================
  # DAST (Dynamic Application Security Testing)
  # ============================================
  dast:
    name: 🌐 Dynamic Application Security Testing
    runs-on: ubuntu-latest
    services:
      siem-lite:
        image: ghcr.io/${{ github.repository }}:latest
        ports:
          - 8000:8000
        env:
          DATABASE_URL: sqlite:///test.db
          ENVIRONMENT: testing

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🕷️ OWASP ZAP Scan
        uses: zaproxy/action-full-scan@v0.7.0
        with:
          target: 'http://localhost:8000'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'

      - name: 📋 Upload ZAP Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: zap-results
          path: report_html.html

  # ============================================
  # Secret Scanning
  # ============================================
  secret-scan:
    name: 🔐 Secret Scanning
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🔍 TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
          extra_args: --debug --only-verified

      - name: 🔎 GitLeaks Scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # ============================================
  # Security Notification
  # ============================================
  notify-security:
    name: 📢 Security Notifications
    runs-on: ubuntu-latest
    needs: [dependency-scan, container-scan, sast, dast, secret-scan]
    if: failure()

    steps:
      - name: 📢 Slack Notification
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          channel: '#security-alerts'
          message: '🚨 Security scan failed in SIEM Lite repository!'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: 📧 Email Notification
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 587
          username: ${{ secrets.EMAIL_USERNAME }}
          password: ${{ secrets.EMAIL_PASSWORD }}
          subject: 'SECURITY ALERT: SIEM Lite Security Scan Failed'
          body: 'A security scan has failed in the SIEM Lite repository. Please review the results immediately.'
          to: security-team@company.com
```

## 🔧 Configuraciones Adicionales

### SonarCloud Configuration

#### `sonar-project.properties`

```properties
sonar.projectKey=your-org_siem-lite
sonar.organization=your-org
sonar.host.url=https://sonarcloud.io

# Source code settings
sonar.sources=siem_lite
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml

# Exclusions
sonar.exclusions=**/*_pb2.py,**/migrations/**,**/venv/**,**/env/**

# Test exclusions
sonar.test.exclusions=tests/**

# Coverage exclusions
sonar.coverage.exclusions=**/tests/**,**/migrations/**,**/__init__.py

# Duplication exclusions
sonar.cpd.exclusions=**/migrations/**
```

### CodeQL Configuration

#### `.github/codeql/codeql-config.yml`

```yaml
name: "CodeQL Config"

queries:
  - uses: security-and-quality
  - uses: security-extended

paths-ignore:
  - tests/
  - migrations/
  - __pycache__/

disable-default-queries: false

query-filters:
  - exclude:
      id: py/unused-import
      
  - exclude:
      id: py/similar-function
```

### Performance Testing

#### `tests/performance/load-test.js`

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// Custom metrics
const alertCreationRate = new Rate('alert_creation_rate');
const alertCreationDuration = new Trend('alert_creation_duration');
const errorCounter = new Counter('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 },    // Ramp up
    { duration: '5m', target: 10 },    // Stay at 10 users
    { duration: '2m', target: 20 },    // Ramp up to 20 users
    { duration: '5m', target: 20 },    // Stay at 20 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],     // Error rate under 1%
    alert_creation_rate: ['rate>0.9'],  // 90% success rate for alerts
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export function setup() {
  // Health check before starting
  const response = http.get(`${BASE_URL}/api/health`);
  check(response, {
    'API is healthy': (r) => r.status === 200,
  });
}

export default function () {
  // Test alert creation
  const alertPayload = {
    alert_type: `Load Test Alert ${Math.random()}`,
    source_ip: '192.168.1.100',
    details: 'Load testing alert creation',
    severity: 'MEDIUM'
  };

  const alertResponse = http.post(
    `${BASE_URL}/api/alerts`,
    JSON.stringify(alertPayload),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );

  const alertSuccess = check(alertResponse, {
    'alert created successfully': (r) => r.status === 201,
  });

  alertCreationRate.add(alertSuccess);
  alertCreationDuration.add(alertResponse.timings.duration);

  if (!alertSuccess) {
    errorCounter.add(1);
  }

  // Test alerts listing
  const listResponse = http.get(`${BASE_URL}/api/alerts`);
  check(listResponse, {
    'alerts listed successfully': (r) => r.status === 200,
  });

  // Test statistics
  const statsResponse = http.get(`${BASE_URL}/api/stats`);
  check(statsResponse, {
    'stats retrieved successfully': (r) => r.status === 200,
  });

  sleep(1);
}

export function teardown(data) {
  // Cleanup after tests
  console.log('Load test completed');
}
```

## 📊 Métricas y Monitoreo del Pipeline

### GitHub Actions Metrics

```yaml
# Add to workflow for metrics collection
- name: 📊 Collect Metrics
  run: |
    echo "PIPELINE_START_TIME=${{ github.event.head_commit.timestamp }}" >> $GITHUB_ENV
    echo "PIPELINE_DURATION=$(($(date +%s) - $(date -d "${{ github.event.head_commit.timestamp }}" +%s)))" >> $GITHUB_ENV

- name: 📈 Send Metrics to Datadog
  uses: DataDog/datadog-ci@v1
  with:
    api-key: ${{ secrets.DATADOG_API_KEY }}
    metrics: |
      - metric: cicd.pipeline.duration
        value: ${{ env.PIPELINE_DURATION }}
        tags:
          - repository:${{ github.repository }}
          - branch:${{ github.ref_name }}
```

### Pipeline Dashboard

```yaml
# Grafana dashboard for CI/CD metrics
{
  "dashboard": {
    "title": "CI/CD Pipeline Metrics",
    "panels": [
      {
        "title": "Pipeline Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(github_actions_workflow_run_conclusion_total{conclusion=\"success\"}[24h])"
          }
        ]
      },
      {
        "title": "Pipeline Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "github_actions_workflow_run_duration_seconds"
          }
        ]
      }
    ]
  }
}
```

## 🚨 Alertas y Notificaciones

### Slack Integration

```yaml
- name: 📢 Slack Notification
  uses: 8398a7/action-slack@v3
  if: always()
  with:
    status: ${{ job.status }}
    channel: '#ci-cd'
    author_name: GitHub Actions
    fields: repo,message,commit,author,action,eventName,ref,workflow
    custom_payload: |
      {
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*${{ job.status == 'success' && '✅' || '❌' }} CI/CD Pipeline ${{ job.status }}*\n*Repository:* ${{ github.repository }}\n*Branch:* ${{ github.ref_name }}\n*Commit:* ${{ github.sha }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Email Notifications

```yaml
- name: 📧 Email Notification on Failure
  uses: dawidd6/action-send-mail@v3
  if: failure()
  with:
    server_address: smtp.company.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: '❌ SIEM Lite CI/CD Pipeline Failed'
    html_body: |
      <h2>Pipeline Failure Notification</h2>
      <p><strong>Repository:</strong> ${{ github.repository }}</p>
      <p><strong>Branch:</strong> ${{ github.ref_name }}</p>
      <p><strong>Commit:</strong> ${{ github.sha }}</p>
      <p><strong>Workflow:</strong> ${{ github.workflow }}</p>
      <p><strong>Run URL:</strong> <a href="${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}">View Details</a></p>
    to: devops-team@company.com,security-team@company.com
```

## 🔐 Secrets Management

### Required Secrets

```bash
# GitHub Container Registry
GITHUB_TOKEN                 # Automatic token

# Cloud Provider (AWS)
AWS_ACCESS_KEY_ID            # AWS access key
AWS_SECRET_ACCESS_KEY        # AWS secret key

# Security Tools
SNYK_TOKEN                   # Snyk API token
SONAR_TOKEN                  # SonarCloud token

# Notifications
SLACK_WEBHOOK_URL            # Slack webhook URL
EMAIL_USERNAME               # SMTP username
EMAIL_PASSWORD               # SMTP password

# Monitoring
DATADOG_API_KEY             # Datadog API key

# Custom Application Secrets
SECRET_KEY                   # Application secret key
DATABASE_PASSWORD            # Production database password
```

### Secrets Rotation

```yaml
name: 🔄 Secrets Rotation

on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly
  workflow_dispatch:

jobs:
  rotate-secrets:
    runs-on: ubuntu-latest
    steps:
      - name: 🔐 Rotate AWS Keys
        run: |
          # Script to rotate AWS access keys
          ./scripts/rotate-aws-keys.sh

      - name: 🔑 Update Database Passwords
        run: |
          # Script to update database passwords
          ./scripts/rotate-db-passwords.sh

      - name: 📢 Notify Security Team
        uses: 8398a7/action-slack@v3
        with:
          status: success
          channel: '#security'
          message: '🔄 Monthly secrets rotation completed'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 📋 Checklist de Deployment

### Pre-deployment

- [ ] ✅ Todos los tests pasan
- [ ] 🔒 Scans de seguridad completados
- [ ] 📊 Métricas de performance aceptables
- [ ] 🔍 Code review aprobado
- [ ] 📝 Documentación actualizada
- [ ] 🔄 Backup de base de datos realizado

### Deployment

- [ ] 🚀 Deployment a staging exitoso
- [ ] 🧪 Smoke tests pasando
- [ ] 📈 Métricas de aplicación normales
- [ ] 🔍 Logs sin errores críticos
- [ ] 🩺 Health checks OK

### Post-deployment

- [ ] 📊 Monitoreo activado
- [ ] 🚨 Alertas configuradas
- [ ] 📧 Notificaciones enviadas
- [ ] 📝 Release notes publicadas
- [ ] 🔄 Rollback plan preparado

## 🛠️ Troubleshooting del Pipeline

### Problemas Comunes

#### Tests Fallan

```bash
# Ejecutar localmente
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Ver logs detallados
pytest tests/ -v --tb=long

# Verificar dependencias
pip check
```

#### Build de Docker Falla

```bash
# Build local con cache deshabilitado
docker build --no-cache -t siem-lite:debug .

# Verificar multi-stage build
docker build --target=development -t siem-lite:dev .

# Inspeccionar layers
docker history siem-lite:latest
```

#### Deployment Falla

```bash
# Verificar configuración de kubectl
kubectl config current-context

# Ver estado del deployment
kubectl rollout status deployment/siem-lite

# Ver logs del pod
kubectl logs -f deployment/siem-lite
```

Esta documentación proporciona una guía completa para el CI/CD de SIEM Lite, desde la configuración básica hasta el troubleshooting avanzado.
