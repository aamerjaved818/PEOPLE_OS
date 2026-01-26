#!/bin/bash

# Production Deployment Script for Phase 4B Part 3
# Handles complete system startup with proper ordering and health checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOG_DIR="logs"
REPORTS_DIR="tmp/reports"
MIGRATIONS_DIR="migrations"
VENV_DIR="venv"
PYTHON_CMD="python"
STARTUP_TIMEOUT=30

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is not installed"
        return 1
    fi
    return 0
}

create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p $LOG_DIR
    mkdir -p $REPORTS_DIR
    mkdir -p $MIGRATIONS_DIR
    log_success "Directories created"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! check_command python3; then
        check_command python || (log_error "Python not found"; exit 1)
    fi
    
    # Check pip
    if ! check_command pip; then
        log_error "pip not found"
        exit 1
    fi
    
    # Check Redis CLI (optional but recommended)
    if ! check_command redis-cli; then
        log_warning "redis-cli not found (optional)"
    fi
    
    # Check PostgreSQL CLI (optional)
    if ! check_command psql; then
        log_warning "psql not found (PostgreSQL client optional)"
    fi
    
    log_success "Prerequisites check completed"
}

check_env_file() {
    log_info "Checking .env file..."
    
    if [ ! -f ".env" ]; then
        log_warning ".env file not found"
        log_info "Running environment configuration script..."
        $PYTHON_CMD scripts/configure_environment.py || {
            log_error "Failed to configure environment"
            exit 1
        }
    fi
    
    log_success ".env file verified"
}

setup_python_env() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment if not exists
    if [ ! -d "$VENV_DIR" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv $VENV_DIR
    fi
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate || . $VENV_DIR/Scripts/activate 2>/dev/null
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel > /dev/null
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt > /dev/null
    else
        log_warning "requirements.txt not found"
    fi
    
    log_success "Python environment ready"
}

check_redis() {
    log_info "Checking Redis connectivity..."
    
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping > /dev/null 2>&1; then
            log_success "Redis is accessible"
            return 0
        else
            log_error "Redis is not responding"
            return 1
        fi
    else
        log_warning "redis-cli not installed, skipping Redis check"
        return 0
    fi
}

check_database() {
    log_info "Checking database connectivity..."
    
    # Test database connection
    if $PYTHON_CMD -c "
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        pass
    print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
        log_success "Database is accessible"
        return 0
    else
        log_error "Database connection failed"
        return 1
    fi
}

run_migrations() {
    log_info "Running database migrations..."
    
    if command -v alembic &> /dev/null; then
        alembic upgrade head || {
            log_error "Migrations failed"
            exit 1
        }
        log_success "Migrations completed"
    else
        log_warning "alembic not installed, skipping migrations"
    fi
}

start_service() {
    local name=$1
    local command=$2
    local logfile="$LOG_DIR/${name}.log"
    
    log_info "Starting $name..."
    
    # Start in background and redirect output
    nohup $command > "$logfile" 2>&1 &
    local pid=$!
    
    # Wait for service to be ready
    sleep 2
    
    if kill -0 $pid 2>/dev/null; then
        log_success "$name started (PID: $pid)"
        echo $pid
    else
        log_error "$name failed to start"
        cat "$logfile"
        exit 1
    fi
}

verify_services() {
    log_info "Verifying services..."
    
    # Check API
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        log_success "API is responding"
    else
        log_warning "API not responding yet (may still be starting)"
    fi
    
    # Check Celery Worker
    if command -v celery &> /dev/null; then
        if celery -A backend.services.async_tasks inspect ping > /dev/null 2>&1; then
            log_success "Celery worker is responding"
        else
            log_warning "Celery worker not responding yet"
        fi
    fi
}

print_startup_summary() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║          Phase 4B Part 3 - Production Deployment Ready         ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Service URLs:"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  API Health:        http://localhost:8000/health"
    echo "  Schedules API:     http://localhost:8000/api/v1/analytics/schedules"
    echo ""
    echo "📝 Log Files:"
    echo "  Application:       $LOG_DIR/app.log"
    echo "  Celery Worker:     $LOG_DIR/celery_worker.log"
    echo "  Celery Beat:       $LOG_DIR/celery_beat.log"
    echo "  Email Delivery:    $LOG_DIR/email_delivery.log"
    echo "  Scheduler:         $LOG_DIR/scheduler.log"
    echo ""
    echo "🛠️  Common Commands:"
    echo "  View Schedules:           curl http://localhost:8000/api/v1/analytics/schedules"
    echo "  Check Celery Queue:       celery -A backend.services.async_tasks inspect active"
    echo "  Monitor Tasks:            tail -f $LOG_DIR/celery_worker.log"
    echo "  Stop Services:            bash scripts/stop_services.sh"
    echo ""
    echo "✅ System is ready for testing!"
    echo ""
}

cleanup_on_exit() {
    log_info "Cleanup handler registered (press Ctrl+C to stop all services)"
}

# Main execution
main() {
    log_info "Starting Phase 4B Part 3 Production Deployment"
    echo ""
    
    # Setup
    create_directories
    check_prerequisites
    check_env_file
    setup_python_env
    
    # Verify connections
    check_redis || {
        log_warning "Redis check failed (may affect Celery)"
    }
    check_database || {
        log_error "Database check failed"
        exit 1
    }
    
    # Database setup
    run_migrations
    
    # Start services
    log_info "Starting services..."
    echo ""
    
    # Start FastAPI API Server
    API_CMD="$PYTHON_CMD -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4"
    API_PID=$(start_service "API Server" "$API_CMD")
    
    # Wait for API to be ready
    log_info "Waiting for API to be ready..."
    sleep 3
    
    # Start Celery Worker
    WORKER_CMD="celery -A backend.services.async_tasks worker --loglevel=info --concurrency=4"
    WORKER_PID=$(start_service "Celery Worker" "$WORKER_CMD")
    
    # Start Celery Beat
    BEAT_CMD="celery -A backend.services.async_tasks beat --loglevel=info"
    BEAT_PID=$(start_service "Celery Beat" "$BEAT_CMD")
    
    sleep 2
    
    # Verify services
    verify_services
    
    # Print summary
    print_startup_summary
    
    # Save PIDs
    echo "$API_PID" > "$LOG_DIR/api.pid"
    echo "$WORKER_PID" > "$LOG_DIR/worker.pid"
    echo "$BEAT_PID" > "$LOG_DIR/beat.pid"
    
    log_success "Deployment completed successfully!"
    
    # Register cleanup on exit
    trap cleanup_on_exit EXIT
    
    # Keep script running
    log_info "Services are running. Press Ctrl+C to stop."
    wait
}

# Run main function
main "$@"
