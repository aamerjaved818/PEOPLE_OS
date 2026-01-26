# Phase 4B Part 3 - Integration Test Guide

## Overview

This guide covers running and understanding the integration tests for Phase 4B Part 3 (Report Scheduling). The test suite validates:

1. **Database Integration** - Schema and CRUD operations
2. **Report Scheduler** - Schedule creation and management
3. **Email Delivery** - Email sending functionality
4. **Async Tasks** - Celery task execution
5. **API Integration** - REST endpoint functionality
6. **Workflow Integration** - End-to-end processes
7. **Error Handling** - Edge cases and validation

---

## Prerequisites

### Python Packages

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
pip install sqlalchemy celery redis jinja2 pydantic fastapi
```

### Service Requirements

For full integration testing:

- Redis running (for Celery)
- PostgreSQL or SQLite available
- Email SMTP credentials configured in .env

---

## Running Tests

### Run All Tests

```bash
pytest tests/test_phase4b_part3_integration.py -v
```

### Run Specific Test Class

```bash
# Test database functionality
pytest tests/test_phase4b_part3_integration.py::TestDatabaseIntegration -v

# Test scheduler functionality
pytest tests/test_phase4b_part3_integration.py::TestReportScheduler -v

# Test email delivery
pytest tests/test_phase4b_part3_integration.py::TestEmailDelivery -v

# Test API endpoints
pytest tests/test_phase4b_part3_integration.py::TestAPIIntegration -v

# Test complete workflow
pytest tests/test_phase4b_part3_integration.py::TestWorkflowIntegration -v

# Test error handling
pytest tests/test_phase4b_part3_integration.py::TestErrorHandling -v
```

### Run Specific Test

```bash
pytest tests/test_phase4b_part3_integration.py::TestDatabaseIntegration::test_create_report_schedule -v
```

### Run with Coverage

```bash
pytest tests/test_phase4b_part3_integration.py --cov=backend --cov-report=html
```

### Run with Markers

```bash
# Run only async tests
pytest tests/test_phase4b_part3_integration.py -m asyncio -v

# Run only slow tests
pytest tests/test_phase4b_part3_integration.py -m slow -v
```

---

## Test Suite Details

### TestDatabaseIntegration

**Purpose:** Verify database connectivity and CRUD operations

**Tests:**

1. `test_database_connection` - Basic connectivity
2. `test_create_report_schedule` - Creating a schedule
3. `test_list_report_schedules` - Listing user schedules
4. `test_schedule_with_json_recipients` - JSON field handling

**Expected Results:**

```
PASSED test_database_connection
PASSED test_create_report_schedule
PASSED test_list_report_schedules
PASSED test_schedule_with_json_recipients
```

**Troubleshooting:**

- If database connection fails: Check DATABASE_URL in .env
- If creation fails: Verify model schema matches migration
- If listing fails: Check user_id filtering logic

---

### TestReportScheduler

**Purpose:** Test APScheduler functionality

**Tests:**

1. `test_schedule_report_creation` - Creating scheduled jobs
2. `test_schedule_with_cron_expression` - Cron expression parsing
3. `test_list_user_schedules` - Listing user's schedules
4. `test_unschedule_report` - Removing schedules

**Expected Results:**

```
PASSED test_schedule_report_creation
PASSED test_schedule_with_cron_expression
PASSED test_list_user_schedules
PASSED test_unschedule_report
```

**Sample Output:**

```
Job ID generated: 550e8400-e29b-41d4-a716-446655440000
Schedule created for: test_user_123
Next run: 2026-01-24 09:00:00
```

**Troubleshooting:**

- If scheduler initialization fails: Check Redis connectivity
- If cron parsing fails: Validate cron expression format
- If unschedule fails: Verify job_id exists

---

### TestEmailDelivery

**Purpose:** Test email sending functionality

**Tests:**

1. `test_send_email` - Basic email sending
2. `test_send_email_with_attachment` - Attachment handling
3. `test_email_template_rendering` - Jinja2 template rendering

**Expected Results:**

```
PASSED test_send_email
PASSED test_send_email_with_attachment
PASSED test_email_template_rendering
```

**Mocked Behavior:**

- SMTP connections are mocked (no actual emails sent in tests)
- Tests verify correct method calls
- Attachments are validated but not actually transmitted

**Troubleshooting:**

- If template rendering fails: Check template directory path
- If SMTP mock fails: Verify smtplib import works
- If attachment test fails: Check MIME type handling

---

### TestAsyncTasks

**Purpose:** Test Celery async task execution

**Tests:**

1. `test_generate_report_task` - Report generation
2. `test_send_email_task` - Email task execution

**Expected Results:**

```
PASSED test_generate_report_task
PASSED test_send_email_task
```

**Note:** These tests use mocked tasks by default to avoid Celery broker dependency. For integration with real Celery:

```bash
# Start Celery worker in another terminal
celery -A backend.services.async_tasks worker --loglevel=info

# Run tests with live Celery
pytest tests/test_phase4b_part3_integration.py::TestAsyncTasks -v --tb=short
```

---

### TestAPIIntegration

**Purpose:** Test FastAPI REST endpoints

**Tests:**

1. `test_api_health_endpoint` - Health check endpoint
2. `test_api_docs_endpoint` - API documentation
3. `test_get_schedules_endpoint` - List schedules endpoint

**Expected Results:**

```
PASSED test_api_health_endpoint
PASSED test_api_docs_endpoint
PASSED test_get_schedules_endpoint
```

**Sample API Responses:**

```json
GET /health
{
  "status": "healthy",
  "timestamp": "2026-01-23T10:30:00Z"
}

GET /api/v1/analytics/schedules
[]  // Empty initially, populated after creating schedules

GET /docs
// Swagger UI HTML
```

**Troubleshooting:**

- If endpoint returns 404: Check FastAPI app initialization
- If auth fails (401): Verify JWT token configuration
- If CORS issue: Check CORS middleware configuration

---

### TestWorkflowIntegration

**Purpose:** Test complete end-to-end workflow

**Workflow Steps:**

1. Create schedule via API
2. Verify schedule creation in database
3. Confirm active status
4. Check job_id assignment
5. Validate recipients storage

**Expected Results:**

```
PASSED test_complete_schedule_workflow
```

**Workflow Output:**

```
✓ Schedule created with ID: abc-123-def
✓ Retrieved from database
✓ Status: active (is_active=true)
✓ Job ID assigned: job_550e8400
✓ Recipients stored: ['workflow@example.com']
```

**Troubleshooting:**

- If creation fails: Check CRUD function
- If retrieval fails: Verify database session handling
- If validation fails: Check model validation rules

---

### TestErrorHandling

**Purpose:** Test error handling and validation

**Tests:**

1. `test_invalid_schedule_data` - Missing required fields
2. `test_duplicate_recipient_email` - Duplicate recipient handling

**Expected Results:**

```
PASSED test_invalid_schedule_data
PASSED test_duplicate_recipient_email
```

**Error Scenarios:**

```
Invalid Data:
- Missing user_id → ValidationError
- Missing report_type → ValidationError
- Empty recipients → ValidationError

Duplicate Emails:
- Handled gracefully (deduplicated or stored as-is)
- Should not cause failure
```

---

## Test Coverage

### Generate Coverage Report

```bash
pytest tests/test_phase4b_part3_integration.py --cov=backend --cov-report=html --cov-report=term
```

### Expected Coverage

| Module                            | Coverage | Status             |
| --------------------------------- | -------- | ------------------ |
| backend.services.report_scheduler | 95%+     | ✅                 |
| backend.services.email_delivery   | 90%+     | ✅                 |
| backend.services.async_tasks      | 85%+     | ⚠️ (Celery mocked) |
| backend.crud                      | 100%     | ✅                 |
| backend.models                    | 100%     | ✅                 |
| backend.database                  | 95%+     | ✅                 |

### View HTML Coverage Report

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:test@localhost/test_db
          CELERY_BROKER_URL: redis://localhost:6379/0
        run: |
          pytest tests/test_phase4b_part3_integration.py -v --cov=backend

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Performance Testing

### Load Testing Schedules

```bash
# Test creating many schedules
pytest tests/test_phase4b_part3_integration.py::TestReportScheduler -v --benchmark
```

### Database Query Performance

```bash
# Measure query times
pytest tests/test_phase4b_part3_integration.py::TestDatabaseIntegration -v --durations=10
```

### Expected Performance Metrics

| Operation       | Expected Time | Status |
| --------------- | ------------- | ------ |
| Create Schedule | < 100ms       | ✅     |
| List Schedules  | < 50ms        | ✅     |
| Send Email      | < 5s          | ✅     |
| Generate Report | 5-30s         | ✅     |
| Task Execution  | < 1s          | ✅     |

---

## Common Issues & Solutions

### 1. Database Connection Error

```
ERROR: cannot create database connection
```

**Solution:**

```bash
# Check DATABASE_URL in .env
grep DATABASE_URL .env

# Test connection directly
python -c "
from sqlalchemy import create_engine
engine = create_engine('sqlite:///./app.db')
with engine.connect() as conn:
    print('✓ Connection OK')
"
```

### 2. Redis Connection Error

```
ERROR: redis connection refused
```

**Solution:**

```bash
# Start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine

# Verify
redis-cli ping  # Should return PONG
```

### 3. Celery Tasks Not Running

```
ERROR: celery worker not responding
```

**Solution:**

```bash
# Start Celery worker
celery -A backend.services.async_tasks worker --loglevel=info

# In another terminal, run tests
pytest tests/test_phase4b_part3_integration.py::TestAsyncTasks -v
```

### 4. Import Errors

```
ERROR: cannot import backend.services
```

**Solution:**

```bash
# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in editable mode
pip install -e .
```

### 5. Email SMTP Errors

```
ERROR: SMTP authentication failed
```

**Solution:**

```bash
# Verify SMTP credentials in .env
grep SMTP .env
grep SENDER .env

# Tests use mocked SMTP, so real credentials not required for testing
# Use test credentials or mock SMTP
```

---

## Test Execution Checklist

- [ ] Python environment activated
- [ ] All dependencies installed (`pip list | grep pytest`)
- [ ] Database accessible
- [ ] Redis running (optional but recommended)
- [ ] .env file configured
- [ ] Tests discover properly (`pytest --collect-only`)
- [ ] Run tests with `-v` flag for detailed output
- [ ] Check coverage report
- [ ] Review any warnings or deprecations
- [ ] Document any failing tests

---

## Next Steps

After passing integration tests:

1. **Performance Optimization** (Task 7)
   - Profile slow queries
   - Optimize database indices
   - Cache frequently accessed data

2. **End-to-End Testing** (Task 8)
   - User acceptance testing
   - Load testing
   - Failure scenario testing

3. **User Documentation** (Task 9)
   - Create user guides
   - Document API endpoints
   - Provide troubleshooting guides

4. **Phase Completion** (Task 10)
   - Final security audit
   - Performance benchmarking
   - Release preparation

---

## Support & Debugging

### Enable Debug Logging

```python
# In conftest.py or test file
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

### Run with Verbose Output

```bash
pytest tests/test_phase4b_part3_integration.py -vv --tb=long --log-cli-level=DEBUG
```

### Generate Test Report

```bash
pytest tests/test_phase4b_part3_integration.py --html=report.html --self-contained-html
```

---

**Version:** 1.0  
**Date:** January 23, 2026  
**Status:** Complete ✅
