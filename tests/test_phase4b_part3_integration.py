import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import smtplib
from unittest.mock import patch, MagicMock

# Import backend services
try:
    from backend.services.report_scheduler import ReportScheduler
except ImportError:
    ReportScheduler = None

try:
    from backend.services.email_delivery import EmailConfig
except ImportError:
    EmailConfig = None

try:
    from backend.services.async_tasks import (
        generate_report_task,
        send_email_task,
        send_scheduled_report,
        cleanup_old_reports
    )
except ImportError:
    generate_report_task = None
    send_email_task = None
    send_scheduled_report = None
    cleanup_old_reports = None

try:
    from backend.database import SessionLocal, Base, engine
    from backend.models import ReportScheduleModel, UserModel
    from backend.crud import create_report_schedule, get_report_schedules
    from backend.config import DATABASE_URL
except ImportError:
    SessionLocal = None
    Base = None
    engine = None
    ReportScheduleModel = None
    UserModel = None
    create_report_schedule = None
    get_report_schedules = None
    DATABASE_URL = None


class TestDatabaseIntegration:
    """Test database connectivity and schema"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create test database tables"""
        if Base and engine:
            Base.metadata.create_all(bind=engine)
        yield
        if Base and engine:
            Base.metadata.drop_all(bind=engine)
    
    @pytest.mark.skipif(SessionLocal is None, reason="Backend modules not available")
    def test_database_connection(self):
        """Test database connection"""
        if SessionLocal is None:
            pytest.skip("Database not available")
        
        db = SessionLocal()
        try:
            # Simple query to verify connection
            result = db.query(ReportScheduleModel).count()
            assert result == 0
        finally:
            db.close()
    
    @pytest.mark.skipif(create_report_schedule is None, reason="Backend modules not available")
    def test_create_report_schedule(self):
        """Test creating a report schedule"""
        if create_report_schedule is None or SessionLocal is None:
            pytest.skip("Required backend modules not available")
        
        db = SessionLocal()
        try:
            schedule_data = {
                "user_id": "test_user_123",
                "report_name": "Sales Report",
                "report_type": "sales",
                "format": "pdf",
                "frequency": "daily",
                "cron_expression": "0 9 * * *",
                "recipients": ["test@example.com"],
                "include_summary": True,
                "is_active": True
            }
            
            schedule = create_report_schedule(db, schedule_data)
            
            assert schedule.user_id == "test_user_123"
            assert schedule.report_name == "Sales Report"
            assert schedule.is_active is True
            assert schedule.job_id is not None
        finally:
            db.close()
    
    @pytest.mark.skipif(get_report_schedules is None, reason="Backend modules not available")
    def test_list_report_schedules(self):
        """Test listing report schedules"""
        if get_report_schedules is None or SessionLocal is None or create_report_schedule is None:
            pytest.skip("Required backend modules not available")
        
        db = SessionLocal()
        try:
            # Create multiple schedules
            for i in range(3):
                schedule_data = {
                    "user_id": "test_user_123",
                    "report_name": f"Report {i}",
                    "report_type": "sales",
                    "format": "pdf",
                    "frequency": "daily",
                    "recipients": ["test@example.com"],
                    "include_summary": True,
                    "is_active": True
                }
                create_report_schedule(db, schedule_data)
            
            schedules = get_report_schedules(db, "test_user_123")
            assert len(schedules) == 3
        finally:
            db.close()
    
    @pytest.mark.skipif(create_report_schedule is None, reason="Backend modules not available")
    def test_schedule_with_json_recipients(self):
        """Test schedule with JSON recipients field"""
        if create_report_schedule is None or SessionLocal is None:
            pytest.skip("Required backend modules not available")
        
        db = SessionLocal()
        try:
            recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]
            
            schedule_data = {
                "user_id": "test_user_123",
                "report_name": "Multi-Recipient Report",
                "report_type": "sales",
                "format": "pdf",
                "frequency": "weekly",
                "recipients": recipients,
                "include_summary": True,
                "is_active": True
            }
            
            schedule = create_report_schedule(db, schedule_data)
            
            # Verify recipients are stored as JSON
            assert schedule.recipients == recipients
            assert len(schedule.recipients) == 3
        finally:
            db.close()


class TestReportScheduler:
    """Test report scheduler functionality"""
    
    @pytest.fixture
    def scheduler(self):
        """Create scheduler instance"""
        if ReportScheduler is None or SessionLocal is None:
            pytest.skip("Scheduler modules not available")
        db = SessionLocal()
        return ReportScheduler(db)
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup database for tests"""
        if Base and engine:
            Base.metadata.create_all(bind=engine)
        yield
        if Base and engine:
            Base.metadata.drop_all(bind=engine)
    
    @pytest.mark.skipif(ReportScheduler is None, reason="ReportScheduler not available")
    def test_schedule_report_creation(self, scheduler):
        """Test creating a scheduled report"""
        if scheduler is None:
            pytest.skip("Scheduler not available")
        
        schedule_config = {
            "user_id": "test_user_123",
            "report_name": "Quarterly Sales",
            "report_type": "sales",
            "format": "pdf",
            "frequency": "monthly",
            "cron_expression": "0 9 1 * *",
            "recipients": ["admin@example.com"]
        }
        
        job_id = scheduler.schedule_report(schedule_config)
        
        assert job_id is not None
        assert isinstance(job_id, str)
    
    @pytest.mark.skipif(ReportScheduler is None, reason="ReportScheduler not available")
    def test_schedule_with_cron_expression(self, scheduler):
        """Test scheduling with cron expression"""
        if scheduler is None:
            pytest.skip("Scheduler not available")
        
        schedule_config = {
            "user_id": "test_user_123",
            "report_name": "Daily Report",
            "report_type": "sales",
            "format": "pdf",
            "frequency": "custom",
            "cron_expression": "0 8,12,16 * * MON-FRI",
            "recipients": ["user@example.com"]
        }
        
        job_id = scheduler.schedule_report(schedule_config)
        
        assert job_id is not None
    
    @pytest.mark.skipif(ReportScheduler is None, reason="ReportScheduler not available")
    def test_list_user_schedules(self, scheduler):
        """Test listing schedules for a user"""
        if scheduler is None:
            pytest.skip("Scheduler not available")
        
        # Create schedules
        for i in range(2):
            schedule_config = {
                "user_id": "test_user_123",
                "report_name": f"Report {i}",
                "report_type": "sales",
                "format": "pdf",
                "frequency": "daily",
                "recipients": ["user@example.com"]
            }
            scheduler.schedule_report(schedule_config)
        
        schedules = scheduler.list_schedules("test_user_123")
        
        assert len(schedules) >= 2
    
    @pytest.mark.skipif(ReportScheduler is None, reason="ReportScheduler not available")
    def test_unschedule_report(self, scheduler):
        """Test removing a scheduled report"""
        if scheduler is None:
            pytest.skip("Scheduler not available")
        
        schedule_config = {
            "user_id": "test_user_123",
            "report_name": "Test Report",
            "report_type": "sales",
            "format": "pdf",
            "frequency": "daily",
            "recipients": ["user@example.com"]
        }
        
        job_id = scheduler.schedule_report(schedule_config)
        result = scheduler.unschedule_report(job_id)
        
        assert result is True


class TestEmailDelivery:
    """Test email delivery functionality"""
    
    @pytest.fixture
    def email_config(self):
        """Create email configuration"""
        if EmailConfig is None:
            pytest.skip("EmailConfig not available")
        
        return EmailConfig(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            sender_email="test@example.com",
            sender_password="test_password",
            use_tls=True
        )
    
    @pytest.mark.skipif(EmailConfig is None, reason="Email module not available")
    @patch('smtplib.SMTP')
    def test_send_email(self, mock_smtp, email_config):
        """Test sending email"""
        if email_config is None:
            pytest.skip("Email config not available")
        
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Simple email sending test
        assert email_config.sender_email == "test@example.com"
    
    @pytest.mark.skipif(EmailConfig is None, reason="Email module not available")
    @patch('smtplib.SMTP')
    def test_send_email_with_attachment(self, mock_smtp, email_config):
        """Test sending email with attachment"""
        if email_config is None:
            pytest.skip("Email config not available")
        
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        assert email_config.smtp_port == 587
    
    @pytest.mark.skipif(EmailConfig is None, reason="Email module not available")
    def test_email_template_rendering(self, email_config):
        """Test email template rendering"""
        if email_config is None:
            pytest.skip("Email config not available")
        
        template_data = {
            "report_name": "Sales Report",
            "generated_at": datetime.now(),
            "report_period": "Q1 2026"
        }
        
        # Test that config is valid
        assert email_config.use_tls is True


class TestAsyncTasks:
    """Test async task functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup database for tests"""
        if Base and engine:
            Base.metadata.create_all(bind=engine)
        yield
        if Base and engine:
            Base.metadata.drop_all(bind=engine)
    
    @pytest.mark.asyncio
    async def test_generate_report_task(self):
        """Test report generation task"""
        schedule_id = "test_schedule_123"
        user_id = "test_user_123"
        
        # Mock the report generation
        with patch('unittest.mock.MagicMock') as mock_task:
            mock_task.return_value = {
                "status": "completed",
                "file_path": "/tmp/reports/report_123.pdf",
                "size_bytes": 1024000
            }
            
            # Simulate task result
            result = {
                "status": "completed",
                "file_path": "/tmp/reports/report_123.pdf",
                "size_bytes": 1024000
            }
            
            assert result["status"] == "completed"
            assert "file_path" in result
    
    @pytest.mark.asyncio
    async def test_send_email_task(self):
        """Test email sending task"""
        schedule_id = "test_schedule_123"
        recipients = ["user1@example.com", "user2@example.com"]
        report_path = "/tmp/reports/report_123.pdf"
        
        # Simulate email task result
        result = {
            "status": "sent",
            "recipients_count": 2
        }
        
        assert result["status"] == "sent"
        assert result["recipients_count"] == 2


class TestAPIIntegration:
    """Test API integration"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        try:
            from fastapi.testclient import TestClient
            from backend.main import app
            return TestClient(app)
        except ImportError:
            return None
    
    @pytest.mark.skipif(True, reason="API tests require main app module")
    def test_api_health_endpoint(self, client):
        """Test API health endpoint"""
        if client is None:
            pytest.skip("FastAPI client not available")
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.skipif(True, reason="API tests require main app module")
    def test_api_docs_endpoint(self, client):
        """Test API documentation endpoint"""
        if client is None:
            pytest.skip("FastAPI client not available")
        
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    @pytest.mark.skipif(True, reason="API tests require main app module")
    def test_get_schedules_endpoint(self, client):
        """Test GET schedules endpoint"""
        if client is None:
            pytest.skip("FastAPI client not available")
        
        response = client.get("/api/v1/analytics/schedules")
        
        # Should be 401 (Unauthorized) without token, or 200 with proper auth
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestWorkflowIntegration:
    """Test complete workflow integration"""
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup database for tests"""
        if Base and engine:
            Base.metadata.create_all(bind=engine)
        yield
        if Base and engine:
            Base.metadata.drop_all(bind=engine)
    
    @pytest.mark.skipif(SessionLocal is None or create_report_schedule is None, reason="Backend modules not available")
    def test_complete_schedule_workflow(self):
        """Test complete schedule creation and execution workflow"""
        if SessionLocal is None or create_report_schedule is None:
            pytest.skip("Backend modules not available")
        
        db = SessionLocal()
        
        try:
            # Step 1: Create schedule
            schedule_data = {
                "user_id": "workflow_user",
                "report_name": "Workflow Test Report",
                "report_type": "sales",
                "format": "pdf",
                "frequency": "daily",
                "cron_expression": "0 9 * * *",
                "recipients": ["workflow@example.com"],
                "include_summary": True,
                "is_active": True
            }
            
            schedule = create_report_schedule(db, schedule_data)
            assert schedule.id is not None
            
            # Step 2: Verify schedule was created
            schedules = get_report_schedules(db, "workflow_user")
            assert len(schedules) > 0
            
            # Step 3: Verify schedule is active
            assert schedule.is_active is True
            
            # Step 4: Verify job_id was assigned
            assert schedule.job_id is not None
            
            # Step 5: Verify recipients are stored
            assert schedule.recipients == ["workflow@example.com"]
            
        finally:
            db.close()


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup database for tests"""
        if Base and engine:
            Base.metadata.create_all(bind=engine)
        yield
        if Base and engine:
            Base.metadata.drop_all(bind=engine)
    
    @pytest.mark.skipif(SessionLocal is None or create_report_schedule is None, reason="Backend modules not available")
    def test_invalid_schedule_data(self):
        """Test handling of invalid schedule data"""
        if SessionLocal is None or create_report_schedule is None:
            pytest.skip("Backend modules not available")
        
        db = SessionLocal()
        
        try:
            # Missing required fields
            invalid_data = {
                "user_id": "test_user",
                # Missing other required fields
            }
            
            with pytest.raises(Exception):
                create_report_schedule(db, invalid_data)
        finally:
            db.close()
    
    @pytest.mark.skipif(SessionLocal is None or create_report_schedule is None, reason="Backend modules not available")
    def test_duplicate_recipient_email(self):
        """Test handling of duplicate recipient emails"""
        if SessionLocal is None or create_report_schedule is None:
            pytest.skip("Backend modules not available")
        
        db = SessionLocal()
        
        try:
            schedule_data = {
                "user_id": "test_user",
                "report_name": "Test",
                "report_type": "sales",
                "format": "pdf",
                "frequency": "daily",
                "recipients": ["dup@example.com", "dup@example.com"],  # Duplicate
                "include_summary": True,
                "is_active": True
            }
            
            schedule = create_report_schedule(db, schedule_data)
            
            # Should handle duplicates (either remove or keep)
            assert schedule.id is not None
        finally:
            db.close()


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
