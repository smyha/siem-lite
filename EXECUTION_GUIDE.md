# 🚀 SIEM Lite - Execution Guide

*Cross-p### 4. **Virtual Environment Setup (Recom### 5. **Install Dependencies**

**All Platforms:**
```bash
# Ensure you're in the project directory and venv is activated

# Method 1: Install core dependencies only
pip install -r requirements.txt

# Method 2: Install in development mode (recommended)
pip install -e .

# Method 3: Install with development dependencies
pip install -e .[dev]

# Method 4: Install all optional dependencies
pip install -e .[dev,test,docs]
```

**Verify Installation:**
```bash
# Test core functionality
python -c "import siem_lite; print('✅ SIEM Lite installed successfully')"

# Check if CLI is available
siem-lite --help
```tform guide for Windows, Linux, and macOS*

## 📋 Table of Contents
- [Environment Setup](#environment-setup)
- [Installation Methods](#installation-methods)
- [Running the Server](#running-the-server)
- [Available API Routes](#available-api-routes)
- [Functionality Verification](#functionality-verification)
- [Platform-Specific Notes](#platform-specific-notes)
- [Troubleshooting](#troubleshooting)

## 🛠️ Environment Setup

### 1. **System Requirements**

**Minimum Requirements:**
- **Python:** 3.9+ (recommended: Python 3.11+)
- **RAM:** 2GB minimum, 4GB recommended
- **Disk Space:** 1GB for installation + additional space for logs and reports
- **Network:** Internet connection for initial setup and package installation

**Supported Operating Systems:**
- Windows 10/11 (x64)
- Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- macOS 10.15+ (Catalina or later)

### 3. **Project Setup**

**All Platforms:**
```bash
python --version
# Should show Python 3.9+ (recommended: 3.11+)

# On some Linux distributions, use python3
python3 --version
```

**If Python is not installed:**
- **Windows:** Download from [python.org](https://python.org) or install via Microsoft Store
- **Linux:** `sudo apt install python3 python3-pip` (Ubuntu/Debian) or `sudo yum install python3 python3-pip` (CentOS/RHEL)
- **macOS:** `brew install python3` or download from [python.org](https://python.org)

### 2. **Virtual Environment Setup (Recommended)**

#### **Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If execution policy error, run first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify activation
where python
```

#### **Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Verify activation
where python
```

#### **Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation
which python
```

### 3. **Install Dependencies**

**All Platforms:**
```bash
# Ensure you're in the project directory and venv is activated
pip install -r requirements.txt

# Alternative: Install in development mode
pip install -e .
```

## 🔧 Installation Methods

### **Method 1: Quick Setup (Recommended)**
```bash
# All platforms - this will install the package with entry point
pip install -e .

# Now you can use the unified command from anywhere
siem-lite
```

### **Method 2: Docker Setup**
```bash
# Build the container
docker build -t siem-lite .

# Run with docker-compose
docker-compose up -d

# Check status
docker-compose ps
```

### **Method 3: Manual Setup**
```bash
# Initialize database manually
python -c "from siem_lite.infrastructure.database import init_database; init_database(); print('✅ Database initialized')"

# Create required directories
mkdir -p data reports reports/plots  # Linux/macOS
# or
md data, reports, reports\plots       # Windows CMD
```

## 📦 **Dependencies Overview**

### **Core Dependencies**
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.104.0 | Web API framework |
| uvicorn | >=0.24.0 | ASGI server |
| pydantic | >=2.0.0 | Data validation |
| sqlalchemy | >=2.0.0 | Database ORM |
| rich | >=13.0.0 | Terminal formatting |
| questionary | >=2.0.0 | Interactive CLI |

### **Security Dependencies**
| Package | Version | Purpose |
|---------|---------|---------|
| python-jose | >=3.3.0 | JWT tokens |
| passlib | >=1.7.4 | Password hashing |
| python-multipart | >=0.0.6 | Form data parsing |

### **Data Analysis Dependencies**
| Package | Version | Purpose |
|---------|---------|---------|
| pandas | >=2.0.0 | Data manipulation |
| matplotlib | >=3.7.0 | Plotting |
| seaborn | >=0.12.0 | Statistical visualization |

### **System Dependencies**
| Package | Version | Purpose |
|---------|---------|---------|
| psutil | >=5.9.0 | System monitoring |
| requests | >=2.31.0 | HTTP client |
| structlog | >=23.0.0 | Structured logging |

### **Development Dependencies** (optional)
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=7.4.0 | Testing framework |
| black | >=23.0.0 | Code formatting |
| mypy | >=1.5.0 | Type checking |
| sphinx | >=8.0.0 | Documentation |

## 🚀 Running the Server

### **Method 1: Unified Command (Recommended)**
After running `pip install -e .`, you can use the unified command:

```bash
# Start complete system (database + API server + interactive menu)
siem-lite

# Show help
siem-lite --help

# Start just the API server
siem-lite run

# Check system status
siem-lite status

# Interactive dashboard
siem-lite dashboard
```

### **Method 2: Direct API Server**

#### **Development Mode:**
```bash
# Windows
uvicorn siem_lite.main:app --reload --host 127.0.0.1 --port 8000

# Linux/macOS  
uvicorn siem_lite.main:app --reload --host 127.0.0.1 --port 8000
```

#### **Production Mode:**
```bash
# Single worker
uvicorn siem_lite.main:app --host 0.0.0.0 --port 8000

# Multiple workers (Linux/macOS)
uvicorn siem_lite.main:app --host 0.0.0.0 --port 8000 --workers 4

# Windows (single worker recommended)
uvicorn siem_lite.main:app --host 0.0.0.0 --port 8000
```

### **Method 3: Docker**
```bash
# Using docker-compose (all platforms)
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Method 4: Background Service**

#### **Linux (systemd):**
```bash
# Create service file
sudo nano /etc/systemd/system/siem-lite.service

# Example content:
[Unit]
Description=SIEM Lite Service
After=network.target

[Service]
Type=simple
User=siem
WorkingDirectory=/home/siem/siem-lite
Environment=PATH=/home/siem/siem-lite/venv/bin
ExecStart=/home/siem/siem-lite/venv/bin/uvicorn siem_lite.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable siem-lite
sudo systemctl start siem-lite
sudo systemctl status siem-lite
```

#### **Windows (Task Scheduler):**
```powershell
# Create a batch file (start-siem.bat)
@echo off
cd /d "C:\path\to\siem-lite"
call venv\Scripts\activate.bat
uvicorn siem_lite.main:app --host 127.0.0.1 --port 8000

# Then create a scheduled task using Task Scheduler GUI
# or use schtasks command
```

## 🛣️ Available API Routes

Once the server is running, these routes are available:

### **📊 System Status**
- **GET** `http://localhost:8000/api/health` - Basic system status
- **GET** `http://localhost:8000/api/health?detailed=true` - Detailed status
- **GET** `http://localhost:8000/api/metrics` - General metrics

### **🚨 Alert Management**
- **GET** `http://localhost:8000/api/alerts` - List all alerts
- **POST** `http://localhost:8000/api/alerts` - Create new alert
- **GET** `http://localhost:8000/api/alerts/{id}` - Get specific alert
- **PUT** `http://localhost:8000/api/alerts/{id}` - Update alert
- **DELETE** `http://localhost:8000/api/alerts/{id}` - Delete alert

### **📈 Statistics**
- **GET** `http://localhost:8000/api/stats` - General statistics
- **GET** `http://localhost:8000/api/trends` - Trends and analysis

### **📚 Documentation**
- **GET** `http://localhost:8000/docs` - Swagger UI documentation
- **GET** `http://localhost:8000/redoc` - ReDoc documentation
- **GET** `http://localhost:8000/` - Main page

## ✅ Functionality Verification

### 1. **Verify server is running**

#### **Using curl (Linux/macOS/Windows with WSL):**
```bash
curl http://localhost:8000/api/health
curl http://127.0.0.1:8000/api/health
```

#### **Using PowerShell (Windows):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health"
# or
curl.exe http://localhost:8000/api/health
```

#### **Using browser (All platforms):**
Open: `http://localhost:8000/api/health`

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-23T...",
  "database": "connected"
}
```

### 2. **Test interactive documentation**
Open in browser: `http://localhost:8000/docs`

### 3. **Create a test alert**

#### **Linux/macOS:**
```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "Test Alert",
    "source_ip": "192.168.1.100",
    "details": "System test alert"
  }'
```

#### **Windows PowerShell:**
```powershell
$body = @{
    alert_type = "Test Alert"
    source_ip = "192.168.1.100" 
    details = "System test alert"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/alerts" -Method POST -Body $body -ContentType "application/json"
```

### 4. **Verify alert was created**
```bash
# Linux/macOS/WSL
curl http://localhost:8000/api/alerts

# Windows PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/alerts"
```

## 🖥️ Platform-Specific Notes

### **Windows**
- **PowerShell Execution Policy:** You may need to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Path Separators:** Use backslashes `\` in Windows paths
- **Multiple Workers:** Not recommended on Windows, use single worker
- **Dependencies:** Some packages may require Visual Studio Build Tools
- **Python Installation:** Recommended to install from [python.org](https://python.org) with "Add to PATH" option
- **Alternative Package Manager:** Consider using [Chocolatey](https://chocolatey.org/) for easier dependency management

### **Linux**
- **Python Command:** Use `python3` instead of `python` on most distributions
- **Permissions:** May need `sudo` for installing system packages
- **Service Management:** Use `systemd` for background services
- **Firewall:** Configure firewall to allow port 8000 if needed:
  ```bash
  sudo ufw allow 8000
  ```
- **System Dependencies:** May need to install build tools:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-dev python3-pip build-essential
  
  # CentOS/RHEL
  sudo yum install python3-devel python3-pip gcc
  ```

### **macOS**
- **Python Installation:** Consider using `brew install python3`
- **Xcode Tools:** May need to install command line tools: `xcode-select --install`
- **Service Management:** Use `launchctl` for background services
- **Homebrew Dependencies:**
  ```bash
  # Install required system libraries
  brew install pkg-config libffi openssl
  ```

### **Docker (All Platforms)**
- **Requirements:** Docker and docker-compose installed
- **Ports:** Ensure port 8000 is not used by other services
- **Volumes:** Data persists in Docker volumes
- **Memory:** Allocate at least 1GB RAM for the container
- **Multi-platform:** Uses Python 3.11 slim image for optimal performance

## 🔧 Troubleshooting

### ❌ **Common Issues**

#### **1. `{"detail":"Not Found"}` on `/api/health`**

**🔍 Quick diagnosis:**
The `{"detail":"Not Found"}` error indicates incorrect URL or server misconfiguration.

**✅ STEP-BY-STEP SOLUTION:**

1. **Verify the server is running:**
   ```bash
   # Navigate to project directory first
   
   # Start server
   uvicorn siem_lite.main:app --host 127.0.0.1 --port 8000
   ```
   
   **You should see this output:**
   ```
   INFO: Started server process [####]
   🚀 Starting SIEM Lite API...
   Environment: development
   ✅ SIEM Lite API started successfully
   INFO: Uvicorn running on http://127.0.0.1:8000
   ```

2. **Use the EXACT correct URL:**
   ```
   ✅ CORRECT: http://127.0.0.1:8000/api/health
   ❌ INCORRECT: http://localhost:8000/api/health  (sometimes doesn't work)
   ❌ INCORRECT: http://127.0.0.1:8000/health     (missing /api/)
   ```

3. **Test with the automatic script:**
   ```bash
   # In another terminal, while server is running
   python test_api.py
   ```

#### **2. Python/Python3 Command Issues**

**Linux/macOS:**
```bash
# If 'python' command not found, use python3
python3 --version
python3 -m pip install -r requirements.txt
python3 -m uvicorn siem_lite.main:app --host 127.0.0.1 --port 8000
```

**Windows:**
```bash
# If Python not in PATH, use full path
C:\Python311\python.exe --version
# or install Python from Microsoft Store
```

#### **3. Virtual Environment Issues**

**Windows PowerShell Execution Policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux Permission Issues:**
```bash
sudo chmod +x venv/bin/activate
source venv/bin/activate
```

#### **4. Port Already in Use**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -i :8000
kill -9 <PID>

# Use different port:
uvicorn siem_lite.main:app --host 127.0.0.1 --port 8001
```

#### **5. Database Issues**
```bash
# Reinitialize database
python -c "from siem_lite.infrastructure.database import init_database; init_database(); print('✅ Database reinitialized')"

# Check database file exists
# Windows:
dir siem_lite.db
# Linux/macOS:
ls -la siem_lite.db
```

#### **6. Import Errors**
```bash
# Ensure you're in the correct directory
pwd  # Linux/macOS
cd    # Windows

# Verify Python can find the module
python -c "import siem_lite; print('✅ Module found')"

# Reinstall in development mode
pip install -e .
```

#### **7. Missing Dependencies**
```bash
# Install missing core dependencies
pip install fastapi uvicorn pydantic sqlalchemy rich questionary

# Install missing data analysis dependencies
pip install pandas matplotlib seaborn

# Install missing system dependencies
pip install psutil requests structlog

# Force reinstall all dependencies
pip install --force-reinstall -r requirements.txt
```

#### **8. Version Conflicts**
```bash
# Check for conflicts
pip check

# Create fresh environment
python -m venv fresh_env
# Activate fresh_env (see activation commands above)
pip install -e .

# List installed packages and versions
pip list
```

#### **9. Compilation Errors (Windows)**
```bash
# Install Visual Studio Build Tools if you get compilation errors
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Alternative: Use pre-compiled wheels
pip install --only-binary=all -r requirements.txt
```

### **🔍 Debugging Commands**

#### **Check System Status:**
```bash
# Test configuration loading
python -c "from siem_lite.main import app; print('✅ App loads OK')"

# Test database connection
python -c "from siem_lite.infrastructure.database import init_database; init_database(); print('✅ DB OK')"

# Test dependencies
python -c "import fastapi, uvicorn, sqlalchemy; print('✅ Dependencies OK')"
```

#### **Get Detailed Logs:**
```bash
# Start with debug logging
uvicorn siem_lite.main:app --host 127.0.0.1 --port 8000 --log-level debug

# Check application logs
tail -f logs/app.log  # Linux/macOS
Get-Content logs\app.log -Tail 50 -Wait  # Windows PowerShell
```

### **💡 Performance Tips**

#### **Linux Production Deployment:**
```bash
# Use Gunicorn for production
pip install gunicorn
gunicorn siem_lite.main:app -w 4 -k uvicorn.workers.UnicornWorker --bind 0.0.0.0:8000

# With systemd service
sudo systemctl enable siem-lite
sudo systemctl start siem-lite
```

#### **Windows Production Deployment:**
```powershell
# Use Windows Service or IIS
# Install IIS with Python integration
# Or use Task Scheduler for auto-start
```

#### **Docker Production:**
```bash
# Build optimized image
docker build -t siem-lite:production .

# Run with resource limits
docker run -d --name siem-lite -p 8000:8000 --memory=512m --cpus=1.0 siem-lite:production
```