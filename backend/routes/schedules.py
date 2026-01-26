"""
Report Scheduling API Endpoints
REST API for managing scheduled reports
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import logging

from backend.dependencies import get_db, get_current_user
from backend.services.report_scheduler import (
    ReportScheduler,
    ReportScheduleRequest,
    ReportScheduleResponse,
    get_scheduler
)
from backend.services.email_delivery import (
    EmailConfig,
    get_email_service
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics/schedules", tags=["schedules"])


@router.post("", response_model=ReportScheduleResponse)
async def create_schedule(
    request: ReportScheduleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new report schedule
    
    Args:
        request: Schedule creation request
        db: Database session
        current_user: Current user
    
    Returns:
        Created schedule response
    """
    try:
        scheduler = get_scheduler(db)
        schedule = scheduler.create_schedule(current_user.id, request)

        # Send confirmation email
        email_service = get_email_service()
        email_service.send_confirmation_email(
            recipients=request.recipients,
            report_name=request.report_name,
            frequency=request.frequency.value,
            next_run=schedule.next_run
        )

        return ReportScheduleResponse(
            id=str(schedule.id),
            report_name=schedule.report_name,
            report_type=schedule.report_type,
            format=schedule.format,
            frequency=schedule.frequency,
            recipients=schedule.recipients,
            is_active=schedule.is_active,
            next_run=schedule.next_run,
            last_run=schedule.last_run,
            created_at=schedule.created_at
        )

    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ReportScheduleResponse])
async def list_schedules(
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List all schedules for the current user
    
    Args:
        active_only: Only return active schedules
        db: Database session
        current_user: Current user
    
    Returns:
        List of schedules
    """
    try:
        scheduler = get_scheduler(db)
        schedules = scheduler.list_schedules(current_user.id)

        if active_only:
            schedules = [s for s in schedules if s.is_active]

        return [
            ReportScheduleResponse(
                id=str(s.id),
                report_name=s.report_name,
                report_type=s.report_type,
                format=s.format,
                frequency=s.frequency,
                recipients=s.recipients,
                is_active=s.is_active,
                next_run=s.next_run,
                last_run=s.last_run,
                created_at=s.created_at
            )
            for s in schedules
        ]

    except Exception as e:
        logger.error(f"Error listing schedules: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{schedule_id}", response_model=ReportScheduleResponse)
async def get_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a specific schedule
    
    Args:
        schedule_id: Schedule ID
        db: Database session
        current_user: Current user
    
    Returns:
        Schedule details
    """
    try:
        scheduler = get_scheduler(db)
        schedule = scheduler.get_schedule(schedule_id, current_user.id)

        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        return ReportScheduleResponse(
            id=str(schedule.id),
            report_name=schedule.report_name,
            report_type=schedule.report_type,
            format=schedule.format,
            frequency=schedule.frequency,
            recipients=schedule.recipients,
            is_active=schedule.is_active,
            next_run=schedule.next_run,
            last_run=schedule.last_run,
            created_at=schedule.created_at
        )

    except Exception as e:
        logger.error(f"Error getting schedule: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{schedule_id}", response_model=ReportScheduleResponse)
async def update_schedule(
    schedule_id: str,
    request: ReportScheduleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update a schedule
    
    Args:
        schedule_id: Schedule ID
        request: Update request
        db: Database session
        current_user: Current user
    
    Returns:
        Updated schedule
    """
    try:
        scheduler = get_scheduler(db)
        schedule = scheduler.update_schedule(schedule_id, request, current_user.id)

        return ReportScheduleResponse(
            id=str(schedule.id),
            report_name=schedule.report_name,
            report_type=schedule.report_type,
            format=schedule.format,
            frequency=schedule.frequency,
            recipients=schedule.recipients,
            is_active=schedule.is_active,
            next_run=schedule.next_run,
            last_run=schedule.last_run,
            created_at=schedule.created_at
        )

    except Exception as e:
        logger.error(f"Error updating schedule: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a schedule
    
    Args:
        schedule_id: Schedule ID
        db: Database session
        current_user: Current user
    
    Returns:
        Success message
    """
    try:
        scheduler = get_scheduler(db)
        success = scheduler.delete_schedule(schedule_id, current_user.id)

        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")

        return {"message": "Schedule deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting schedule: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{schedule_id}/pause")
async def pause_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Pause a schedule
    
    Args:
        schedule_id: Schedule ID
        db: Database session
        current_user: Current user
    
    Returns:
        Success message
    """
    try:
        scheduler = get_scheduler(db)
        success = scheduler.pause_schedule(schedule_id, current_user.id)

        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")

        return {"message": "Schedule paused successfully"}

    except Exception as e:
        logger.error(f"Error pausing schedule: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{schedule_id}/resume")
async def resume_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Resume a paused schedule
    
    Args:
        schedule_id: Schedule ID
        db: Database session
        current_user: Current user
    
    Returns:
        Success message
    """
    try:
        scheduler = get_scheduler(db)
        success = scheduler.resume_schedule(schedule_id, current_user.id)

        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")

        return {"message": "Schedule resumed successfully"}

    except Exception as e:
        logger.error(f"Error resuming schedule: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{schedule_id}/trigger")
async def trigger_report(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Manually trigger a report
    
    Args:
        schedule_id: Schedule ID
        db: Database session
        current_user: Current user
    
    Returns:
        Task ID and status
    """
    try:
        from backend.services.async_tasks import generate_and_deliver_report
        from backend.services.report_scheduler import ReportScheduleModel

        schedule = db.query(ReportScheduleModel).filter(
            ReportScheduleModel.id == schedule_id,
            ReportScheduleModel.user_id == current_user.id
        ).first()

        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        # Trigger async task
        task = generate_and_deliver_report.delay(
            schedule_id=schedule.id,
            user_id=schedule.user_id,
            report_type=schedule.report_type,
            report_format=schedule.format,
            recipients=schedule.recipients,
            include_summary=schedule.include_summary
        )

        logger.info(f"Triggered manual report for schedule {schedule_id}, task {task.id}")

        return {
            "message": "Report generation triggered",
            "task_id": task.id,
            "schedule_id": schedule_id
        }

    except Exception as e:
        logger.error(f"Error triggering report: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{schedule_id}/task-status/{task_id}")
async def get_task_status(
    schedule_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get status of a report generation task
    
    Args:
        schedule_id: Schedule ID
        task_id: Celery task ID
        db: Database session
        current_user: Current user
    
    Returns:
        Task status and result
    """
    try:
        from backend.services.async_tasks import celery_app

        task = celery_app.AsyncResult(task_id)

        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.state in ('SUCCESS', 'FAILURE') else None,
            "progress": getattr(task.info, 'progress', None) if task.state == 'PROGRESS' else None
        }

    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=400, detail=str(e))
