import datetime
import importlib
import logging
import os
import shutil
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from typing import List, Optional


from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text
from sqlalchemy.orm import Session
import jwt

from backend.database import SessionLocal

# Internal Imports
from backend.audit.scheduler import start_scheduler
from backend.config import settings
from backend.database import engine
from backend.dependencies import (
    check_permission,
    create_access_token,
    get_current_user,
    get_db,
    get_user_org,
    log_audit_event,
    requires_role,
    verify_password,
)
from backend.domains.core import models as core_models
from backend.domains.hcm import models as hcm_models
from backend.domains.gen_admin import models as gen_admin_models
from backend import crud, schemas
from backend.services import tax_calculator
from backend.services.async_tasks import audit_log_task

# Configure Logging (use central logging_config)
from backend.logging_config import logger

from backend.shared.models import models

# Lifecycle Events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Life-cycle Context Manager
    Handles startup and shutdown events cleanly
    """
    # STARTUP
    logger.info("Starting peopleOS eBusiness Suite...")
    
    # 1. Database Connectivity Check
    logger.info("[1/5] Checking Database Connectivity...")
    try:
        # Simple test query
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established.")
    except Exception as e:
        logger.critical(f"Critical Failure: Database unreachable: {e}")
        # In production we might exit, but for dev we warn
        logger.warning(f"Database security check degraded or skipped: {e}")
    
    # 2. Environment Fingerprint Validation
    logger.info("[2/5] Validating Environment Fingerprint...")
    try:
        from backend.domains.core.env_validator import validate_environment_fingerprint
        validate_environment_fingerprint()
    except Exception as e:
        logger.critical(f"Critical Failure: Environment validation failed: {e}")
        # In strictly production environments we might sys.exit here
        if settings.ENVIRONMENT == "production":
            import sys
            sys.exit(1)

    # 3. Domain Model Synchronization
    logger.info("[3/5] Synchronizing Domain Models...")
    try:
        core_models.Base.metadata.create_all(bind=engine)
        hcm_models.Base.metadata.create_all(bind=engine)
        gen_admin_models.Base.metadata.create_all(bind=engine)
        backend.shared.models.models.Base.metadata.create_all(bind=engine)
        logger.info("Domain models synced successfully.")
    except Exception as e:
        logger.error(f"Critical Failure: Model synchronization failed: {e}")
    
    # 4. Security & Audit Schedulers
    logger.info("[4/5] Activating Security & Audit Schedulers...")
    try:
        # Only start scheduler in production or if explicitly enabled to avoid
        # blocking dev reload loops or duplicate tasks
        if settings.APP_ENV != "development":
             start_scheduler()
             logger.info("Audit engine online.")
        else:
             logger.info("Audit scheduler skipped in development mode.")
    except Exception as e:
        logger.error(f"Security Engine Failure: Failed to start Audit Scheduler: {e}")
    
    # 5. Data Protection Services
    logger.info("[5/5] Mounting Data Protection Services...")
    
    logger.info("Application Startup Sequence Complete. All systems operational.")
    
    yield
    
    # SHUTDOWN
    logger.info("Shutting down peopleOS...")


# API Metadata
app = FastAPI(
    title="peopleOS eBusiness Suite API",
    description="peopleOS eBusiness Suite - Comprehensive Human Capital Management API with domain-organized endpoints.",
    lifespan=lifespan,
)

# Sentry error tracking removed per user request

app.add_middleware(
    CORSMiddleware,
    # Wildcard origin with allow_credentials=True is invalid in fetch API.
    # We must whitelist specific origins.
    # Wildcard exception for fetch API with credentials
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Non-blocking logging
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.4f}s"
    )

    # Offload audit logging to background thread to prevent blocking the main event loop
    try:
        import asyncio
        
        # Extract minimal info needed for logging
        # We avoid heavy JWT decoding or DB lookups here if possible. 
        # For rich audit trails, specific endpoints use log_audit_event dependency.
        username = "anonymous"
        organization_id = None
        auth = request.headers.get("authorization") or request.headers.get("Authorization")
        
        # Fast JWT decode only (no DB lookup)
        if auth and auth.lower().startswith("bearer "):
            try:
                token = auth.split(" ", 1)[1]
                # We do a purely stateless decode to get the 'sub'
                # avoiding the overhead of heavy dependencies if possible
                payload = jwt.decode(token, options={"verify_signature": False})
                username = payload.get("sub", "anonymous")
                # If organization_id is in token, use it. Otherwise leave None to save DB lookup.
                organization_id = payload.get("organization_id") 
            except Exception:
                pass

        details = f"duration={duration:.4f}s; client={request.client.host if request.client else 'unknown'}"
        audit_time = datetime.datetime.utcnow().isoformat()
        
        # Dispatch the audit log creation to the Celery worker
        # This is a fire-and-forget asynchronous execution
        audit_log_task.delay(
            organization_id=organization_id,
            user=username,
            action=f"{request.method} {request.url.path}",
            status=str(response.status_code),
            time=audit_time,
            details=details,
        )

    except Exception as e:
        logger.error(f"Failed to dispatch audit log task: {e}")

    return response

# Static Files
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Security & Limits
limiter = Limiter(key_func=get_remote_address, default_limits=["1000/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



# Include Modular Routers
from backend.routers import (
    auth_router,
    core_org_router,
    hcm_employees_router,
    hcm_attendance_router,
    hcm_payroll_router,
    self_service_router,
    system_router,
    hcm_overtime_router,
    gen_admin_router,
    hcm_onboarding_router,
    hcm_offboarding_router,
    hcm_performance_router,
    hcm_learning_router,
    hcm_benefits_router,
    hcm_expenses_router,
    hcm_rewards_router,
    hcm_promotions_router,
)

app.include_router(auth_router, prefix="/api")
app.include_router(core_org_router, prefix="/api")
app.include_router(hcm_employees_router, prefix="/api")
app.include_router(hcm_attendance_router, prefix="/api")
app.include_router(hcm_payroll_router, prefix="/api")
app.include_router(self_service_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(hcm_overtime_router, prefix="/api")
app.include_router(gen_admin_router, prefix="/api")
app.include_router(hcm_onboarding_router, prefix="/api")
app.include_router(hcm_offboarding_router, prefix="/api")
app.include_router(hcm_performance_router, prefix="/api")
app.include_router(hcm_learning_router, prefix="/api")
app.include_router(hcm_benefits_router, prefix="/api")
app.include_router(hcm_expenses_router, prefix="/api")
app.include_router(hcm_rewards_router, prefix="/api")
app.include_router(hcm_promotions_router, prefix="/api")

@app.get("/api", tags=["System"])
def read_root():
    return {"message": "peopleOS eBusiness Suite API Operating Normally"}


@app.get("/api/health", tags=["System"])
def health_root(db: Session = Depends(get_db)):
    try:
        # Lightweight DB check
        db.execute(text("SELECT 1"))
        return {"status": "Optimal", "database": "Connected", "timestamp": datetime.datetime.now().isoformat()}
    except Exception as e:
        return {"status": "Degraded", "database": "Disconnected", "details": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Enable hot-reload only in development
    should_reload = settings.ENVIRONMENT == "development"
    
    logger.info(f"Starting server in {settings.ENVIRONMENT} mode on port {settings.PORT}")
    
    if should_reload:
        # Reload requires loading via import string
        uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
    else:
        uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
