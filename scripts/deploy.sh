#!/bin/bash
# Production deployment script for SIEM Lite

set -e

echo "🚀 Starting SIEM Lite production deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [ ! -f .env ]; then
        print_warning ".env file not found, copying from .env.example"
        cp .env.example .env
        print_warning "Please edit .env file with your production settings"
        read -p "Press enter to continue after editing .env file..."
    fi
    
    # Create necessary directories
    mkdir -p data reports logs nginx/ssl
    
    # Set proper permissions
    chmod 755 data reports logs
    
    print_status "Environment setup completed"
}

# Build and deploy
deploy() {
    print_status "Building and deploying services..."
    
    # Pull latest images
    docker-compose pull
    
    # Build application
    docker-compose build --no-cache
    
    # Start services
    docker-compose up -d
    
    print_status "Services deployed successfully"
}

# Health check
health_check() {
    print_status "Performing health checks..."
    
    # Wait for services to start
    sleep 30
    
    # Check API health
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        print_status "✅ API is healthy"
    else
        print_error "❌ API health check failed"
        return 1
    fi
    
    # Check Prometheus
    if curl -f http://localhost:9090/-/healthy &> /dev/null; then
        print_status "✅ Prometheus is healthy"
    else
        print_warning "⚠️ Prometheus health check failed"
    fi
    
    # Check Grafana
    if curl -f http://localhost:3000/api/health &> /dev/null; then
        print_status "✅ Grafana is healthy"
    else
        print_warning "⚠️ Grafana health check failed"
    fi
    
    print_status "Health checks completed"
}

# Show status
show_status() {
    print_status "Current deployment status:"
    echo ""
    docker-compose ps
    echo ""
    print_status "Access URLs:"
    echo "  🌐 Application: http://localhost:8000"
    echo "  📊 API Docs: http://localhost:8000/docs"
    echo "  📈 Grafana: http://localhost:3000 (admin/admin123)"
    echo "  🔍 Prometheus: http://localhost:9090"
    echo ""
}

# Backup data
backup_data() {
    print_status "Creating backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if [ -f "data/siem_lite.db" ]; then
        cp data/siem_lite.db "$BACKUP_DIR/"
    fi
    
    # Backup reports
    if [ -d "reports" ]; then
        cp -r reports "$BACKUP_DIR/"
    fi
    
    # Backup logs (last 7 days)
    if [ -d "logs" ]; then
        find logs -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/" \;
    fi
    
    print_status "Backup created in $BACKUP_DIR"
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            setup_environment
            deploy
            health_check
            show_status
            ;;
        "backup")
            backup_data
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose logs -f "${2:-siem-lite}"
            ;;
        "restart")
            print_status "Restarting services..."
            docker-compose restart
            health_check
            ;;
        "stop")
            print_status "Stopping services..."
            docker-compose down
            ;;
        "update")
            print_status "Updating deployment..."
            docker-compose pull
            docker-compose up -d
            health_check
            ;;
        *)
            echo "Usage: $0 {deploy|backup|status|logs|restart|stop|update}"
            echo ""
            echo "Commands:"
            echo "  deploy  - Full deployment (default)"
            echo "  backup  - Create backup of data"
            echo "  status  - Show deployment status"
            echo "  logs    - Show logs (optionally specify service)"
            echo "  restart - Restart all services"
            echo "  stop    - Stop all services"
            echo "  update  - Update and restart services"
            exit 1
            ;;
    esac
}

main "$@"
