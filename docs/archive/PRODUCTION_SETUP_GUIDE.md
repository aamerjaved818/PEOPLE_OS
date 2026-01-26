# Production Environment Setup & Deployment Guide

## Overview

This guide covers setting up Phase 4B Part 3 (Report Scheduling) in a production environment. It includes:

1. Database migrations
2. Environment configuration
3. Service startup procedures
4. Docker deployment (optional)
5. Monitoring and maintenance

---

## Prerequisites

### System Requirements

- Python 3.8+
- Redis 7.0+ (for message broker)
- PostgreSQL 12+ (recommended) or SQLite (default)
- 2GB RAM minimum
- 1 vCPU minimum

### Required Software

- `pip` - Python package manager
- `docker` & `docker-compose` (optional, for containerized deployment)
- `alembic` - Database migration tool

### Python Dependencies

```bash
pip install fastapi uvicorn celery redis sqlalchemy jinja2 pydantic alembic aioredis
```

---

## Step 1: Environment Configuration

### Option A: Automated Setup (Recommended)

```bash
# Run configuration script
python scripts/configure_environment.py
```

This script will:

1. Check system requirements
2. Verify Python dependencies
3. Create necessary directories
4. Generate .env configuration file
5. Provide setup instructions

### Option B: Manual Setup

Create `.env` file in project root:

```bash
# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SENDER_NAME=PeopleOS Reports

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TIMEZONE=UTC

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/peopledb
# Or for SQLite:
# DATABASE_URL=sqlite:///./app.db

# Report Configuration
REPORTS_DIR=/tmp/reports
REPORT_RETENTION_DAYS=30
MAX_REPORT_SIZE_MB=100

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Security
SECRET_KEY=your-generated-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

**Important:** Update email credentials and database URL for your environment!

---

## Step 2: Database Setup

### Create Reports Directory

```bash
mkdir -p /tmp/reports
chmod 755 /tmp/reports
```

### Run Database Migration

```bash
# Create migration
alembic revision --autogenerate -m "Add report schedules"

# Apply migration
alembic upgrade head

# Verify (check for report_schedules table)
# SQLite:
sqlite3 app.db ".tables"

# PostgreSQL:
psql -c "\dt" -d your_database
```

The migration creates:

- `report_schedules` table
- 4 indices for performance
- All necessary columns for schedule management

---

## Step 3: Start Redis

### Option A: Docker (Recommended)

```bash
docker run -d \
  --name peopledb-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine redis-server --requirepass your_password
```

### Option B: Local Installation

**macOS:**

```bash
brew install redis
brew services start redis
```

**Linux:**

```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Windows:**

```bash
# Download from: https://github.com/microsoftarchive/redis/releases
redis-server.exe
```

### Verify Redis is Running

```bash
redis-cli ping
# Expected output: PONG
```

---

## Step 4: Start Services

### Terminal 1: FastAPI Server

```bash
python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --reload
```

Or for production (no reload):

```bash
python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

Expected output:

```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Celery Worker

```bash
celery -A backend.services.async_tasks worker \
  --loglevel=info \
  --concurrency=4 \
  --time-limit=1800 \
  --soft-time-limit=1500
```

Expected output:

```
[CONFIG]
.> app:         backend.services.async_tasks:0x...
.> transport:   redis://localhost:6379/0
.> results:     redis://localhost:6379/1
```

### Terminal 3: Celery Beat (Scheduler)

```bash
celery -A backend.services.async_tasks beat \
  --loglevel=info
```

Expected output:

```
celery beat v5.3.1 (dawn-chorus) is starting.
LocalTime -> 2026-01-23 10:30:00
Configuration ->
    ...
    scheduler -> celery.beat.PersistentScheduler
    db -> celerybeat-schedule
    ...
```

---

## Step 5: Verify Installation

### Check API Server

```bash
curl http://localhost:8000/api/analytics/schedules
# Should return: []
```

### Check Celery Worker

```bash
celery -A backend.services.async_tasks inspect active
# Should show worker status
```

### Check Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### Check Database

```bash
# SQLite
sqlite3 app.db "SELECT COUNT(*) FROM report_schedules;"

# PostgreSQL
psql -c "SELECT COUNT(*) FROM report_schedules;" your_database
```

---

## Step 6: Test the System

### Create a Test Schedule via API

```bash
curl -X POST http://localhost:8000/api/analytics/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "report_name": "Test Report",
    "report_type": "sales",
    "format": "pdf",
    "frequency": "daily",
    "recipients": ["test@example.com"],
    "include_summary": true
  }'
```

### List Schedules

```bash
curl http://localhost:8000/api/analytics/schedules
```

### Monitor Task Execution

Watch the Celery worker output for task execution logs.

### Verify Email Delivery

Check your email for the confirmation email when the schedule is created.

---

## Docker Deployment

### Build and Run with Docker Compose

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose Services

- **redis** - Message broker (port 6379)
- **postgres** - Database (port 5432)
- **api** - FastAPI server (port 8000)
- **celery_worker** - Task processor
- **celery_beat** - Scheduler

### Environment Variables for Docker

Create `.env` file for Docker:

```bash
# Database
DB_USER=peopledb
DB_PASSWORD=secure_password
DB_NAME=peopledb

# Redis
REDIS_PASSWORD=redis_password

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Application
DEBUG=false
```

---

## Monitoring & Maintenance

### Monitor Celery Queue

```bash
# Active tasks
celery -A backend.services.async_tasks inspect active

# Reserved tasks
celery -A backend.services.async_tasks inspect reserved

# Queue stats
celery -A backend.services.async_tasks inspect stats

# Worker status
celery -A backend.services.async_tasks inspect ping
```

### View Logs

```bash
# API logs
tail -f logs/app.log

# Celery worker logs
tail -f logs/celery_worker.log

# Email delivery logs
tail -f logs/email_delivery.log

# Scheduler logs
tail -f logs/scheduler.log
```

### Database Maintenance

```bash
# Cleanup old reports (30 days)
python -c "
from backend.services.async_tasks import cleanup_old_reports
cleanup_old_reports.delay(days=30)
"

# Check schedule status
python -c "
from backend.services.report_scheduler import get_scheduler
from backend.database import SessionLocal
db = SessionLocal()
scheduler = get_scheduler(db)
schedules = scheduler.list_schedules('user123')
for s in schedules:
    print(f'{s.report_name}: {s.is_active}')
"
```

### Redis Monitoring

```bash
# Check memory usage
redis-cli info memory

# Monitor commands in real-time
redis-cli monitor

# Check keys
redis-cli KEYS '*'

# Database size
redis-cli DBSIZE
```

---

## Troubleshooting

### Redis Connection Failed

```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
redis-server  # or docker run ... redis

# Check connection string
grep CELERY_BROKER_URL .env
```

### Celery Worker Not Processing Tasks

```bash
# Check if worker is active
celery -A backend.services.async_tasks inspect active

# Restart worker
pkill -f "celery.*worker"
celery -A backend.services.async_tasks worker --loglevel=info

# Check for errors
tail -f logs/celery_worker.log
```

### Email Not Sending

```bash
# Verify SMTP credentials in .env
grep SMTP .env
grep SENDER .env

# Check email delivery logs
tail -f logs/email_delivery.log

# Test SMTP connection
python -c "
import smtplib
from backend.services.email_delivery import get_email_service, EmailConfig
# Test SMTP
"
```

### Database Connection Error

```bash
# Check database URL
grep DATABASE_URL .env

# Test connection
python -c "
from sqlalchemy import create_engine
from backend.config import DATABASE_URL
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    print('✓ Connection successful')
"
```

### Schedule Not Triggering

```bash
# Check APScheduler is running
# Verify schedule is active:
python -c "
from backend.services.report_scheduler import get_scheduler
from backend.database import SessionLocal
db = SessionLocal()
scheduler = get_scheduler(db)
schedules = scheduler.list_schedules('user123')
for s in schedules:
    print(f'{s.report_name}: active={s.is_active}, next_run={s.next_run}')
"

# Check scheduler logs
tail -f logs/scheduler.log
```

---

## Performance Tuning

### Celery Configuration

```python
# In backend/config.py
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False
```

### Database Connection Pooling

```python
# For production, use connection pooling
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
SQLALCHEMY_POOL_RECYCLE = 3600
```

### Redis Configuration

```bash
# In redis.conf or docker-compose
maxmemory 1gb
maxmemory-policy allkeys-lru
appendonly yes
```

---

## Security Checklist

- [ ] SMTP credentials in .env (never in code)
- [ ] SECRET_KEY is strong and unique
- [ ] Database password is strong
- [ ] Redis requires password authentication
- [ ] API runs behind HTTPS in production
- [ ] Firewall restricts access to ports (6379, 5432)
- [ ] Logs don't contain sensitive information
- [ ] Database backups are secured
- [ ] Redis persistence is enabled
- [ ] Rate limiting is configured

---

## Backup & Recovery

### Database Backup

**PostgreSQL:**

```bash
pg_dump -U user -d database > backup.sql
```

**SQLite:**

```bash
cp app.db app.db.backup
```

### Redis Backup

```bash
redis-cli BGSAVE
# Backup from /var/lib/redis/dump.rdb
```

### Report Files Backup

```bash
tar -czf reports_backup.tar.gz /tmp/reports/
```

---

## Performance Characteristics

| Operation       | Expected Time |
| --------------- | ------------- |
| Create Schedule | < 100ms       |
| List Schedules  | < 50ms        |
| Get Schedule    | < 10ms        |
| Generate Report | 5-30s         |
| Send Email      | 1-5s          |
| Task Status     | < 10ms        |
| Database Query  | < 10ms        |

---

## Next Steps

1. ✅ Environment configured
2. ✅ Database migrated
3. ✅ Services started
4. ⏳ Run integration tests (Task 8)
5. ⏳ Performance optimization (Task 7)
6. ⏳ User documentation (Task 9)
7. ⏳ Phase completion (Task 10)

---

## Support

For issues:

1. Check troubleshooting section above
2. Review logs in `/logs` directory
3. Consult PHASE_4B_PART3_IMPLEMENTATION.md
4. Check QUICKSTART_PHASE_4B_PART3.md for common issues

---

**Version:** 1.0  
**Date:** January 23, 2026  
**Status:** Complete ✅
