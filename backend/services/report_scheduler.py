"""
Report Scheduling Service
Manages scheduled report generation and delivery via cron jobs
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import Column, String, DateTime, Integer, Boolean, JSON, Text, Enum as SQLEnum
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger(__name__)


class ReportFrequency(str, Enum):
    """Report delivery frequency"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class ReportScheduleModel(BaseModel):
    """Database model for scheduled reports"""
    id: Optional[str] = Field(default=None)
    user_id: str
    report_name: str
    report_type: str  # workforce, recruitment, payroll, custom
    format: str  # pdf, excel
    frequency: ReportFrequency
    cron_expression: Optional[str] = None  # Custom cron
    start_date: datetime
    end_date: Optional[datetime] = None
    recipients: List[EmailStr]
    include_summary: bool = True
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    job_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReportScheduleRequest(BaseModel):
    """Request model for creating/updating schedules"""
    report_name: str
    report_type: str
    format: str
    frequency: ReportFrequency
    recipients: List[EmailStr]
    start_date: datetime
    end_date: Optional[datetime] = None
    include_summary: bool = True


class ReportScheduleResponse(BaseModel):
    """Response model for schedules"""
    id: str
    report_name: str
    report_type: str
    format: str
    frequency: ReportFrequency
    recipients: List[EmailStr]
    is_active: bool
    next_run: Optional[datetime]
    last_run: Optional[datetime]
    created_at: datetime


class ReportScheduler:
    """
    Manages report scheduling with APScheduler
    Handles cron job creation, execution, and tracking
    """

    def __init__(self, db: Session):
        """Initialize scheduler"""
        self.db = db
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("Report scheduler initialized")

    def create_schedule(
        self,
        user_id: str,
        request: ReportScheduleRequest
    ) -> ReportScheduleModel:
        """Create a new report schedule"""
        # Generate cron expression based on frequency
        cron_expr = self._get_cron_expression(request.frequency)

        # Create schedule in database
        schedule = ReportScheduleModel(
            user_id=user_id,
            report_name=request.report_name,
            report_type=request.report_type,
            format=request.format,
            frequency=request.frequency,
            cron_expression=cron_expr,
            start_date=request.start_date,
            end_date=request.end_date,
            recipients=request.recipients,
            include_summary=request.include_summary,
            next_run=self._calculate_next_run(request.start_date, cron_expr)
        )

        # Schedule the job
        job_id = self._schedule_job(schedule)
        schedule.job_id = job_id

        logger.info(f"Created schedule {schedule.id} for user {user_id}")
        return schedule

    def update_schedule(
        self,
        schedule_id: str,
        request: ReportScheduleRequest,
        user_id: str
    ) -> ReportScheduleModel:
        """Update an existing schedule"""
        schedule = self.db.query(ReportScheduleModel).filter(
            ReportScheduleModel.id == schedule_id,
            ReportScheduleModel.user_id == user_id
        ).first()

        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")

        # Remove old job
        if schedule.job_id:
            try:
                self.scheduler.remove_job(schedule.job_id)
            except Exception as e:
                logger.warning(f"Failed to remove old job: {e}")

        # Update fields
        schedule.report_name = request.report_name
        schedule.report_type = request.report_type
        schedule.format = request.format
        schedule.frequency = request.frequency
        schedule.recipients = request.recipients
        schedule.include_summary = request.include_summary
        schedule.updated_at = datetime.utcnow()

        # Generate new cron expression
        cron_expr = self._get_cron_expression(request.frequency)
        schedule.cron_expression = cron_expr
        schedule.next_run = self._calculate_next_run(request.start_date, cron_expr)

        # Schedule new job
        job_id = self._schedule_job(schedule)
        schedule.job_id = job_id

        self.db.commit()
        logger.info(f"Updated schedule {schedule_id}")
        return schedule

    def delete_schedule(self, schedule_id: str, user_id: str) -> bool:
        """Delete a schedule"""
        schedule = self.db.query(ReportScheduleModel).filter(
            ReportScheduleModel.id == schedule_id,
            ReportScheduleModel.user_id == user_id
        ).first()

        if not schedule:
            return False

        # Remove scheduled job
        if schedule.job_id:
            try:
                self.scheduler.remove_job(schedule.job_id)
            except Exception as e:
                logger.warning(f"Failed to remove job: {e}")

        self.db.delete(schedule)
        self.db.commit()
        logger.info(f"Deleted schedule {schedule_id}")
        return True

    def pause_schedule(self, schedule_id: str, user_id: str) -> bool:
        """Pause a schedule"""
        schedule = self.db.query(ReportScheduleModel).filter(
            ReportScheduleModel.id == schedule_id,
            ReportScheduleModel.user_id == user_id
        ).first()

        if not schedule:
            return False

        schedule.is_active = False
        if schedule.job_id:
            try:
                self.scheduler.pause_job(schedule.job_id)
            except Exception as e:
                logger.warning(f"Failed to pause job: {e}")

        self.db.commit()
        logger.info(f"Paused schedule {schedule_id}")
        return True

    def resume_schedule(self, schedule_id: str, user_id: str) -> bool:
        """Resume a paused schedule"""
        schedule = self.db.query(ReportScheduleModel).filter(
            ReportScheduleModel.id == schedule_id,
            ReportScheduleModel.user_id == user_id
        ).first()

        if not schedule:
            return False

        schedule.is_active = True
        if schedule.job_id:
            try:
                self.scheduler.resume_job(schedule.job_id)
            except Exception as e:
                logger.warning(f"Failed to resume job: {e}")

        self.db.commit()
        logger.info(f"Resumed schedule {schedule_id}")
        return True

    def list_schedules(self, user_id: str) -> List[ReportScheduleModel]:
        """List all schedules for a user"""
        schedules = self.db.query(ReportScheduleModel).filter(
            ReportScheduleModel.user_id == user_id
        ).order_by(ReportScheduleModel.created_at.desc()).all()
        return schedules

    def get_schedule(self, schedule_id: str, user_id: str) -> Optional[ReportScheduleModel]:
        """Get a specific schedule"""
        schedule = self.db.query(ReportScheduleModel).filter(
            ReportScheduleModel.id == schedule_id,
            ReportScheduleModel.user_id == user_id
        ).first()
        return schedule

    def trigger_report(self, schedule_id: str) -> None:
        """Manually trigger a report generation"""
        schedule = self.db.query(ReportScheduleModel).filter(
            ReportScheduleModel.id == schedule_id
        ).first()

        if not schedule:
            logger.error(f"Schedule {schedule_id} not found")
            return

        logger.info(f"Triggering report for schedule {schedule_id}")
        # Report generation will be handled by async task

    def _get_cron_expression(self, frequency: ReportFrequency) -> str:
        """Generate cron expression based on frequency"""
        cron_expressions = {
            ReportFrequency.DAILY: "0 9 * * *",  # 9 AM daily
            ReportFrequency.WEEKLY: "0 9 * * 1",  # 9 AM Monday
            ReportFrequency.BIWEEKLY: "0 9 * * 1",  # Every 2 weeks Monday
            ReportFrequency.MONTHLY: "0 9 1 * *",  # 9 AM on 1st of month
        }
        return cron_expressions.get(frequency, "0 9 * * 1")

    def _calculate_next_run(self, start_date: datetime, cron_expr: str) -> datetime:
        """Calculate next run time based on cron expression"""
        trigger = CronTrigger.from_crontab(cron_expr)
        next_fire_time = trigger.get_next_fire_time(None, start_date)
        return next_fire_time

    def _schedule_job(self, schedule: ReportScheduleModel) -> str:
        """Schedule a job with APScheduler"""
        job = self.scheduler.add_job(
            func=self._execute_report,
            trigger=CronTrigger.from_crontab(schedule.cron_expression),
            args=[schedule.id],
            id=f"report_{schedule.id}",
            name=schedule.report_name,
            misfire_grace_time=300,  # 5 minute grace period
            replace_existing=True
        )
        return job.id

    def _execute_report(self, schedule_id: str) -> None:
        """Execute report generation (async task)"""
        logger.info(f"Executing report for schedule {schedule_id}")
        # This will be called from async task queue
        # Update last_run timestamp
        schedule = self.db.query(ReportScheduleModel).filter(
            ReportScheduleModel.id == schedule_id
        ).first()

        if schedule:
            schedule.last_run = datetime.utcnow()
            trigger = CronTrigger.from_crontab(schedule.cron_expression)
            schedule.next_run = trigger.get_next_fire_time(None, datetime.utcnow())
            self.db.commit()
            logger.info(f"Updated run times for schedule {schedule_id}")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Report scheduler shut down")


# Global scheduler instance
_scheduler: Optional[ReportScheduler] = None


def get_scheduler(db: Session) -> ReportScheduler:
    """Get or create scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = ReportScheduler(db)
    return _scheduler
