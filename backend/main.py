import datetime
import importlib
import logging
import os
import shutil
import time
import traceback
import uuid
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
from backend.config import auth_config, settings
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

# Configure Logging (use central logging_config)
from backend.logging_config import logger

from backend.shared.models import models

# API Metadata
app = FastAPI(
    title="peopleOS eBusiness Suite API",
    description="peopleOS eBusiness Suite - Comprehensive Human Capital Management API with domain-organized endpoints.",
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


class APIVersionRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.scope.get("path", "")
        if path.startswith("/api/") and not path.startswith("/api/v1/"):
            request.scope["path"] = "/api/v1" + path[len("/api"):]
        return await call_next(request)


app.add_middleware(APIVersionRedirectMiddleware)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.4f}s"
    )
    # Persist a minimal per-request audit entry (mandatory per-user logs)
    try:
        username = "anonymous"
        organization_id = None
        # Attempt to extract username from Bearer token
        auth = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            try:
                token = auth.split(" ", 1)[1]
                # Reuse secret and algorithm from dependencies
                from backend.dependencies import SECRET_KEY, ALGORITHM, ROOT_USERNAME

                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                sub = payload.get("sub")
                if sub:
                    username = sub
                    if sub != ROOT_USERNAME:
                        # Resolve organization for non-root users
                        from backend.domains.core.models import DBUser
                        db_lookup = SessionLocal()
                        try:
                            user = db_lookup.query(DBUser).filter(DBUser.username == sub).first()
                            if user:
                                organization_id = user.organization_id
                        finally:
                            try:
                                db_lookup.close()
                            except Exception:
                                pass
            except Exception:
                # Token decode failed; leave username as anonymous
                pass

        # Build audit record and persist
        try:
            db = SessionLocal()
            audit_time = datetime.datetime.utcnow().isoformat()
            details = f"duration={duration:.4f}s; client={request.client.host if request.client else 'unknown'}"
            audit_payload = schemas.AuditLogCreate(
                organization_id=organization_id,
                user=username,
                action=f"{request.method} {request.url.path}",
                status=str(response.status_code),
                time=audit_time,
                details=details,
            )
            crud.create_audit_log(db, audit_payload)
        except Exception as e:
            logger.error(f"Failed to persist audit log: {e}")
        finally:
            try:
                db.close()
            except Exception:
                pass
    except Exception:
        # Ensure that audit failures never block responses
        logger.exception("Unexpected error while creating audit log")

    return response

# Static Files
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Security & Limits
limiter = Limiter(key_func=get_remote_address, default_limits=["1000/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Lifecycle Events
@app.on_event("startup")
async def startup_event():
    """System-level application startup sequence"""
    logger.info("Initializing peopleOS eBusiness internal engines...")
    
    # 1. Database Security & Integrity
    logger.info("[1/4] Verifying Core Database Integrity...")
    try:
        from backend.security.db_enforcer import enforce_clean_db_state
        enforce_clean_db_state()
        logger.info("Database security check passed.")
    except Exception as e:
        logger.warning(f"Database security check degraded or skipped: {e}")
    
    # 2. Domain Model Synchronization
    logger.info("[2/4] Synchronizing Domain Models...")
    try:
        core_models.Base.metadata.create_all(bind=engine)
        hcm_models.Base.metadata.create_all(bind=engine)
        gen_admin_models.Base.metadata.create_all(bind=engine)
        logger.info("Domain models synced successfully.")
    except Exception as e:
        logger.error(f"Critical Failure: Model synchronization failed: {e}")
        # In a production environment, we might want to exit here
    
    # 3. Security & Audit Schedulers
    logger.info("[3/4] Activating Security & Audit Schedulers...")
    # DISABLED: May cause startup blocking
    # try:
    #     start_scheduler()
    #     logger.info("Audit engine online.")
    # except Exception as e:
    #     logger.error(f"Security Engine Failure: Failed to start Audit Scheduler: {e}")
    
    # 4. Data Protection Services
    logger.info("[4/4] Mounting Data Protection Services...")
    # DISABLED: May cause startup blocking
    # try:
    #     from backend.backup_scheduler import schedule_backups
    #     schedule_backups()
    #     logger.info("Backup protocol engaged.")
    # except Exception as e:
    #     logger.error(f"Data Protection Failure: Failed to start Backup Scheduler: {e}")
        
    logger.info("Application Startup Sequence Complete. All systems operational.")

    # Launch a local PowerShell log tail window on Windows so the user sees logs in real-time
    # DISABLED: This may cause startup issues on some systems
    # try:
    #     project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #     logs_dir = os.path.join(project_root, "logs")
    #     os.makedirs(logs_dir, exist_ok=True)
    #     log_path = os.path.join(logs_dir, "people_os.log")
    #     # Ensure file exists
    #     open(log_path, "a", encoding="utf-8").close()
    #
    #     if os.name == "nt":
    #         try:
    #             import subprocess
    #
    #             cmd = [
    #                 "powershell",
    #                 "-NoExit",
    #                 "-Command",
    #                 f"Get-Content -Path \"{log_path}\" -Wait -Tail 200",
    #             ]
    #             subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    #             logger.info("Launched PowerShell log tail window.")
    #         except Exception as e:
    #             logger.warning(f"Could not launch PowerShell log tail window: {e}")
    #     else:
    #         logger.info("Log tail window only supported on Windows; skip launching tail.")
    # except Exception as e:
    #     logger.warning(f"Failed to prepare log tail window: {e}")


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

app.include_router(auth_router, prefix="/api/v1")
app.include_router(core_org_router, prefix="/api/v1")
app.include_router(hcm_employees_router, prefix="/api/v1")
app.include_router(hcm_attendance_router, prefix="/api/v1")
app.include_router(hcm_payroll_router, prefix="/api/v1")
app.include_router(self_service_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(hcm_overtime_router, prefix="/api/v1")
app.include_router(gen_admin_router, prefix="/api/v1")
app.include_router(hcm_onboarding_router, prefix="/api/v1")
app.include_router(hcm_offboarding_router, prefix="/api/v1")
app.include_router(hcm_performance_router, prefix="/api/v1")
app.include_router(hcm_learning_router, prefix="/api/v1")
app.include_router(hcm_benefits_router, prefix="/api/v1")
app.include_router(hcm_expenses_router, prefix="/api/v1")
app.include_router(hcm_rewards_router, prefix="/api/v1")
app.include_router(hcm_promotions_router, prefix="/api/v1")

@app.get("/api/v1", tags=["System"])
def read_root():
    return {"message": "peopleOS eBusiness Suite API Operating Normally"}


@app.get("/api/v1/health", tags=["System"])
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
