#!/bin/bash

# Health Check Script for Phase 4B Part 3 Production Environment
# Verifies all services are running and responsive

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_PORT="${API_PORT:-8000}"
API_URL="http://localhost:${API_PORT}"
REDIS_HOST="localhost"
REDIS_PORT="6379"
CELERY_APP="backend.services.async_tasks"
TIMEOUT=5

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((PASSED_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((FAILED_CHECKS++))
}

check_api_health() {
    log_info "Checking API Health..."
    ((TOTAL_CHECKS++))
    
    if curl -s -m $TIMEOUT "${API_URL}/health" > /dev/null 2>&1; then
        log_success "API health endpoint responding"
    else
        log_error "API health endpoint not responding"
        return 1
    fi
}

check_api_docs() {
    log_info "Checking API Documentation..."
    ((TOTAL_CHECKS++))
    
    if curl -s -m $TIMEOUT "${API_URL}/docs" > /dev/null 2>&1; then
        log_success "API documentation available"
    else
        log_error "API documentation not accessible"
        return 1
    fi
}

check_schedules_endpoint() {
    log_info "Checking Schedules API..."
    ((TOTAL_CHECKS++))
    
    response=$(curl -s -m $TIMEOUT -w "\n%{http_code}" "${API_URL}/api/analytics/schedules")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        log_success "Schedules API responding (HTTP $http_code)"
    else
        log_error "Schedules API returned HTTP $http_code"
        return 1
    fi
}

check_redis_connection() {
    log_info "Checking Redis Connection..."
    ((TOTAL_CHECKS++))
    
    if command -v redis-cli &> /dev/null; then
        if timeout $TIMEOUT redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1; then
            log_success "Redis connection OK"
        else
            log_error "Redis connection failed"
            return 1
        fi
    else
        log_warning "redis-cli not installed, skipping Redis check"
    fi
}

check_redis_memory() {
    log_info "Checking Redis Memory Usage..."
    ((TOTAL_CHECKS++))
    
    if command -v redis-cli &> /dev/null; then
        memory=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT info memory 2>/dev/null | grep used_memory_human | cut -d: -f2 | tr -d '\r')
        if [ -n "$memory" ]; then
            log_success "Redis memory usage: $memory"
        else
            log_warning "Could not retrieve Redis memory info"
        fi
    else
        log_warning "redis-cli not installed, skipping memory check"
    fi
}

check_database_connection() {
    log_info "Checking Database Connection..."
    ((TOTAL_CHECKS++))
    
    if python3 -c "
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
try:
    engine = create_engine(url, echo=False)
    with engine.connect() as conn:
        pass
except Exception as e:
    print(f'Error: {e}')
    exit(1)
" 2>/dev/null; then
        log_success "Database connection OK"
    else
        log_error "Database connection failed"
        return 1
    fi
}

check_database_table() {
    log_info "Checking Report Schedules Table..."
    ((TOTAL_CHECKS++))
    
    if python3 -c "
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
try:
    engine = create_engine(url, echo=False)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM report_schedules'))
        count = result.scalar()
        print(f'Report schedules: {count}')
except Exception as e:
    print(f'Table check failed: {e}')
    exit(1)
" 2>/dev/null; then
        log_success "Report schedules table exists"
    else
        log_error "Report schedules table not found or inaccessible"
        return 1
    fi
}

check_celery_worker() {
    log_info "Checking Celery Worker..."
    ((TOTAL_CHECKS++))
    
    if command -v celery &> /dev/null; then
        if timeout $TIMEOUT celery -A $CELERY_APP inspect ping > /dev/null 2>&1; then
            log_success "Celery worker responding"
        else
            log_error "Celery worker not responding"
            return 1
        fi
    else
        log_warning "celery not installed, skipping worker check"
    fi
}

check_celery_stats() {
    log_info "Checking Celery Worker Stats..."
    ((TOTAL_CHECKS++))
    
    if command -v celery &> /dev/null; then
        stats=$(celery -A $CELERY_APP inspect stats 2>/dev/null)
        if [ -n "$stats" ]; then
            log_success "Celery stats available"
        else
            log_warning "Could not retrieve Celery stats"
        fi
    else
        log_warning "celery not installed, skipping stats check"
    fi
}

check_celery_active_tasks() {
    log_info "Checking Active Tasks..."
    ((TOTAL_CHECKS++))
    
    if command -v celery &> /dev/null; then
        active=$(celery -A $CELERY_APP inspect active 2>/dev/null | grep -c "active" || echo "0")
        log_success "Active tasks checked ($active)"
    else
        log_warning "celery not installed, skipping active tasks check"
    fi
}

check_process_logs() {
    log_info "Checking Process Logs..."
    ((TOTAL_CHECKS++))
    
    if [ -f "logs/api.pid" ]; then
        api_pid=$(cat logs/api.pid)
        if kill -0 $api_pid 2>/dev/null; then
            log_success "API process running (PID: $api_pid)"
        else
            log_error "API process not running (PID: $api_pid)"
            return 1
        fi
    else
        log_warning "API PID file not found"
    fi
    
    if [ -f "logs/worker.pid" ]; then
        worker_pid=$(cat logs/worker.pid)
        if kill -0 $worker_pid 2>/dev/null; then
            log_success "Worker process running (PID: $worker_pid)"
        else
            log_error "Worker process not running (PID: $worker_pid)"
            return 1
        fi
    else
        log_warning "Worker PID file not found"
    fi
}

check_log_files() {
    log_info "Checking Log Files..."
    ((TOTAL_CHECKS++))
    
    local log_dir="logs"
    local files_found=0
    
    if [ -d "$log_dir" ]; then
        for file in "$log_dir"/*.log; do
            if [ -f "$file" ]; then
                ((files_found++))
                local size=$(du -h "$file" | cut -f1)
                log_success "Found: $(basename $file) ($size)"
            fi
        done
    else
        log_warning "Logs directory not found"
    fi
}

check_disk_space() {
    log_info "Checking Disk Space..."
    ((TOTAL_CHECKS++))
    
    if command -v df &> /dev/null; then
        local usage=$(df -h . | awk 'NR==2 {print $5}')
        local available=$(df -h . | awk 'NR==2 {print $4}')
        log_success "Disk usage: $usage (Available: $available)"
    else
        log_warning "df command not available"
    fi
}

check_environment_variables() {
    log_info "Checking Environment Variables..."
    ((TOTAL_CHECKS++))
    
    if [ -f ".env" ]; then
        local count=$(grep -c "^[^#]" .env | grep -v "^$" || echo "0")
        log_success ".env file exists ($count variables)"
        
        # Check critical variables
        for var in "DATABASE_URL" "CELERY_BROKER_URL" "SMTP_HOST"; do
            if grep -q "^$var=" .env; then
                log_success "  ✓ $var configured"
            else
                log_warning "  ⚠ $var not configured"
            fi
        done
    else
        log_error ".env file not found"
        return 1
    fi
}

print_summary() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              System Health Check Summary                        ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Results:"
    echo "  Total Checks:     $TOTAL_CHECKS"
    echo "  Passed:           $PASSED_CHECKS"
    echo "  Failed:           $FAILED_CHECKS"
    echo ""
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${GREEN}✅ All systems operational!${NC}"
        echo ""
        return 0
    else
        echo -e "${YELLOW}⚠️  Some checks failed. Please review above.${NC}"
        echo ""
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting health check for Phase 4B Part 3..."
    echo ""
    
    # API checks
    check_api_health
    check_api_docs
    check_schedules_endpoint
    echo ""
    
    # Redis checks
    check_redis_connection
    check_redis_memory
    echo ""
    
    # Database checks
    check_database_connection
    check_database_table
    echo ""
    
    # Celery checks
    check_celery_worker
    check_celery_stats
    check_celery_active_tasks
    echo ""
    
    # System checks
    check_process_logs
    check_log_files
    check_disk_space
    check_environment_variables
    echo ""
    
    # Print summary
    print_summary
}

# Run main
main "$@"
exit $?
