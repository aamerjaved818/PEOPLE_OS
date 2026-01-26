"""
Async Report Generation Task Service
Handles background report generation and delivery
"""

from datetime import datetime, timedelta
from typing import Optional, List
import logging
import os
from celery import Celery, Task
from celery.schedules import crontab
from functools import wraps

from backend.config import settings

logger = logging.getLogger(__name__)


# Initialize Celery
celery_app = Celery(
    'peopleOS',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_URL,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    
    # Priority Queuing & Worker Tuning
    task_default_queue='default',
    task_routes={
        'backend.services.async_tasks.audit_log_task': {'queue': 'audit_logs'},
        'backend.services.async_tasks.generate_and_deliver_report': {'queue': 'reports'},
        'backend.services.async_tasks.cleanup_old_audit_logs': {'queue': 'audit_logs'},
    },
    worker_prefetch_multiplier=10,
    task_acks_late=True,
    broker_transport_options={
        'visibility_timeout': 3600,  # 1 hour
    },
)


class ReportTask(Task):
    """Base class for report generation tasks"""

    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True


@celery_app.task(bind=True, base=ReportTask)
def generate_and_deliver_report(
    self,
    schedule_id: str,
    user_id: str,
    report_type: str,
    report_format: str,
    recipients: list,
    include_summary: bool = True
) -> dict:
    """
    Generate report and deliver via email
    
    Args:
        schedule_id: Schedule ID
        user_id: User ID
        report_type: Type of report (workforce, recruitment, payroll)
        report_format: Output format (pdf, excel)
        recipients: List of email recipients
        include_summary: Include metrics summary in email
    
    Returns:
        Task result with status and details
    """
    try:
        logger.info(
            f"Starting report generation for schedule {schedule_id}, "
            f"type: {report_type}, format: {report_format}"
        )

        # Import here to avoid circular imports
        from backend.services.enhanced_report_generator import EnhancedReportGenerator
        from backend.services.email_delivery import (
            ReportEmailPayload, get_email_service
        )
        from backend.database import SessionLocal

        db = SessionLocal()
        try:
            # Generate report
            generator = EnhancedReportGenerator(db)
            
            logger.info(f"Generating {report_format.upper()} report")
            file_path = generator.generate_report(
                report_type=report_type,
                format=report_format,
                user_id=user_id
            )

            if not file_path:
                raise Exception(f"Failed to generate {report_format} report")

            # Get metrics summary if requested
            metrics_summary = None
            if include_summary:
                from backend.services.analytics_calculator import AnalyticsCalculator
                calc = AnalyticsCalculator(db)
                metrics_summary = {
                    "Total Employees": calc.get_total_employees(user_id),
                    "Retention Rate": f"{calc.get_retention_rate(user_id):.1f}%",
                    "Open Positions": calc.get_open_positions(user_id),
                    "Pipeline Candidates": calc.get_pipeline_candidates(user_id),
                }

            # Send email
            email_service = get_email_service()
            payload = ReportEmailPayload(
                schedule_id=schedule_id,
                report_name=f"{report_type.title()} Report",
                report_type=report_type,
                format=report_format,
                recipients=recipients,
                include_summary=include_summary,
                generated_at=datetime.utcnow(),
                file_path=file_path,
                metrics_summary=metrics_summary
            )

            logger.info(f"Sending report email to {', '.join(recipients)}")
            email_sent = email_service.send_report_email(payload, file_path)

            if not email_sent:
                logger.error(f"Failed to send report email for schedule {schedule_id}")
                raise Exception("Email delivery failed")

            logger.info(f"Report generated and delivered for schedule {schedule_id}")

            return {
                'status': 'success',
                'schedule_id': schedule_id,
                'file_path': file_path,
                'recipients': recipients,
                'generated_at': datetime.utcnow().isoformat(),
                'message': f"Report generated and sent to {len(recipients)} recipients"
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(
            f"Error generating report for schedule {schedule_id}: {str(e)}"
        )

        # Send failure notification
        try:
            from backend.services.email_delivery import get_email_service
            email_service = get_email_service()
            email_service.send_failure_notification(
                recipients=recipients,
                report_name=f"{report_type.title()} Report",
                error_message=str(e)
            )
        except Exception as email_error:
            logger.error(f"Failed to send failure notification: {email_error}")

        # Retry with exponential backoff
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    name='backend.services.async_tasks.audit_log_task',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    max_retries=5,
    retry_jitter=True
)
def audit_log_task(
    self,
    organization_id: Optional[str],
    user: str,
    action: str,
    status: str,
    time: str,
    details: Optional[str] = None,
) -> dict:
    """Asynchronously creates an audit log entry in the database."""
    from backend.database import SessionLocal
    from backend.schemas.shared import AuditLogCreate
    from backend.crud.core import create_audit_log

    db = SessionLocal()
    try:
        # Parse time back to datetime if it came as string
        audit_time = datetime.fromisoformat(time) if isinstance(time, str) else time
        
        log_data = AuditLogCreate(
            organizationId=organization_id,
            user=user,
            action=action,
            status=status,
            time=audit_time,
            details=details,
        )
        
        db_log = create_audit_log(db, log_data)
        logger.info(f"✅ Audit Log created via Celery: {db_log.id}")
        
        return {
            'status': 'success',
            'log_id': db_log.id,
            'user': user,
            'action': action,
        }
    except Exception as e:
        logger.error(f"❌ Failed to create audit log: {e}")
        raise self.retry(exc=e)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def cleanup_old_audit_logs(self, days_to_keep: int = 90) -> dict:
    """Deletes audit log entries older than a specified number of days."""
    from backend.database import SessionLocal
    from backend.domains.core.models import DBAuditLog
    
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        logger.info(f"Starting audit log cleanup. Older than: {cutoff_date}")

        # Bulk delete using ORM
        deleted_count = db.query(DBAuditLog).filter(
            DBAuditLog.time < cutoff_date
        ).delete(synchronize_session=False)
        
        db.commit()
        logger.info(f"✅ Audit Log Cleanup complete. Deleted {deleted_count} records.")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ Cleanup task failed: {e}")
        raise self.retry(exc=e)
    finally:
        db.close()


@celery_app.task(bind=True, base=ReportTask)
def cleanup_old_reports(self, days: int = 30) -> dict:
    """
    Clean up old generated reports
    
    Args:
        days: Remove reports older than this many days
    
    Returns:
        Cleanup statistics
    """
    try:
        logger.info(f"Starting cleanup of reports older than {days} days")

        from backend.database import SessionLocal
        from datetime import datetime, timedelta
        import os

        db = SessionLocal()
        try:
            # Find and delete old report files
            reports_dir = settings.REPORTS_DIR
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = 0

            if os.path.exists(reports_dir):
                for filename in os.listdir(reports_dir):
                    file_path = os.path.join(reports_dir, filename)
                    try:
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_mtime < cutoff_date:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.info(f"Deleted old report: {filename}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {filename}: {e}")

            logger.info(f"Cleanup completed: {deleted_count} files deleted")

            return {
                'status': 'success',
                'deleted_count': deleted_count,
                'cutoff_date': cutoff_date.isoformat(),
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error during report cleanup: {str(e)}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, base=ReportTask)
def retry_failed_delivery(self, schedule_id: str) -> dict:
    """
    Retry delivery for a failed report
    
    Args:
        schedule_id: Schedule ID to retry
    
    Returns:
        Retry result
    """
    try:
        logger.info(f"Retrying delivery for schedule {schedule_id}")

        from backend.database import SessionLocal
        from backend.services.report_scheduler import ReportScheduleModel

        db = SessionLocal()
        try:
            schedule = db.query(ReportScheduleModel).filter(
                ReportScheduleModel.id == schedule_id
            ).first()

            if not schedule:
                raise Exception(f"Schedule {schedule_id} not found")

            # Regenerate and deliver
            result = generate_and_deliver_report.delay(
                schedule_id=schedule.id,
                user_id=schedule.user_id,
                report_type=schedule.report_type,
                report_format=schedule.format,
                recipients=schedule.recipients,
                include_summary=schedule.include_summary
            )

            logger.info(f"Retry initiated for schedule {schedule_id}")

            return {
                'status': 'initiated',
                'schedule_id': schedule_id,
                'task_id': result.id,
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error retrying delivery for schedule {schedule_id}: {e}")
        raise


@celery_app.task
def monitor_schedules() -> dict:
    """
    Monitor and update schedule status
    
    Returns:
        Monitoring statistics
    """
    try:
        logger.info("Running schedule monitoring task")

        from backend.database import SessionLocal
        from backend.services.report_scheduler import ReportScheduleModel
        from datetime import datetime

        db = SessionLocal()
        try:
            # Check for expired schedules
            expiring_count = 0
            for schedule in db.query(ReportScheduleModel).filter(
                ReportScheduleModel.end_date <= datetime.utcnow(),
                ReportScheduleModel.is_active == True
            ).all():
                schedule.is_active = False
                expiring_count += 1
                logger.info(f"Deactivated expired schedule {schedule.id}")

            db.commit()

            logger.info(f"Schedule monitoring completed: {expiring_count} expired")

            return {
                'status': 'success',
                'expired_schedules': expiring_count,
                'timestamp': datetime.utcnow().isoformat(),
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in schedule monitoring: {e}")
        raise


# Periodic task configuration
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-old-reports': {
        'task': 'backend.services.async_tasks.cleanup_old_reports',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        'kwargs': {'days': 30}
    },
    'cleanup-old-audit-logs': {
        'task': 'backend.services.async_tasks.cleanup_old_audit_logs',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
        'kwargs': {'days_to_keep': 90}
    },
    'monitor-schedules': {
        'task': 'backend.services.async_tasks.monitor_schedules',
        'schedule': crontab(minute=0),  # Every hour
    },
}


def async_task(func):
    """Decorator to make any function async"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func.delay(*args, **kwargs)
    return wrapper
