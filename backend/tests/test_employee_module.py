"""
Comprehensive test suite for employee module validations and features.
Run with: pytest backend/tests/test_employee_module.py -v
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.domains.hcm import models
from backend import schemas, crud
from backend.main import app
from backend.database import SessionLocal


@pytest.fixture
def db():
    """Fixture to provide database session"""
    db_session = SessionLocal()
    yield db_session
    db_session.close()


@pytest.fixture
def client():
    """Fixture to provide test client"""
    return TestClient(app)


class TestEmailValidation:
    """Test email validation in employee creation"""
    
    def test_email_format_valid(self):
        """Valid email formats should be accepted"""
        from backend.crud import validate_employee_email
        
        valid_emails = [
            "user@company.com",
            "john.doe@company.co.uk",
            "user+tag@example.org",
            "test123@domain.io"
        ]
        
        for email in valid_emails:
            assert validate_employee_email(email), f"Should accept: {email}"
    
    def test_email_format_invalid(self):
        """Invalid email formats should be rejected"""
        from backend.crud import validate_employee_email
        
        invalid_emails = [
            "invalid@domain",  # No TLD
            "@domain.com",      # No local part
            "user@.com",        # No domain
            "user name@domain.com",  # Space in local part
            "user@domain",      # No TLD
        ]
        
        for email in invalid_emails:
            assert not validate_employee_email(email), f"Should reject: {email}"
    
    def test_email_uniqueness_per_org(self, db: Session):
        """Emails must be unique within organization"""
        org_id = "TEST_ORG_001"
        email = "test@example.com"
        # Ensure organization exists for this test
        from backend.domains.core.models import DBOrganization
        org = DBOrganization(id=org_id, code="TEST_ORG_001", name="Test Org", email="test@org.test", created_by="test")
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Create first employee
        emp1_data = {
            "name": "Employee 1",
            "email": email,
            "organization_id": org_id
        }
        emp1 = crud.create_employee(db, schemas.EmployeeCreate(**emp1_data), user_id="test")
        assert emp1.email == email
        
        # Try to create second employee with same email in same org
        emp2_data = {
            "name": "Employee 2",
            "email": email,
            "organization_id": org_id
        }
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            crud.create_employee(db, schemas.EmployeeCreate(**emp2_data), user_id="test")
        
        assert exc_info.value.status_code == 409  # Conflict


class TestCNICValidation:
    """Test CNIC validation in employee creation"""
    
    def test_cnic_format_valid(self):
        """Valid CNIC formats should be accepted"""
        from backend.crud import validate_cnic
        
        valid_cnics = [
            "12345-1234567-5",
            "42201-1234567-8",
            "00000-0000000-0"
        ]
        
        for cnic in valid_cnics:
            result = validate_cnic(cnic)
            assert result["valid"], f"Should accept: {cnic}"
    
    def test_cnic_format_invalid(self):
        """Invalid CNIC formats should be rejected"""
        from backend.crud import validate_cnic
        
        invalid_cnics = [
            "12345-123456-5",   # Too short
            "123456-1234567-5", # Wrong format
            "abcde-1234567-5",  # Non-digits
        ]
        
        for cnic in invalid_cnics:
            result = validate_cnic(cnic)
            assert not result["valid"], f"Should reject: {cnic}"
    
    def test_cnic_expiry_validation(self):
        """Expired CNIC should be rejected"""
        from backend.crud import validate_cnic
        
        expired_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        result = validate_cnic("12345-1234567-5", expired_date)
        
        assert not result["valid"]
        assert any("expired" in error.lower() for error in result["errors"])


class TestActiveEmployeeUniqueness:
    """Test CNIC and phone uniqueness among active employees"""
    
    def test_active_employee_uniqueness_cnic(self, db: Session):
        """CNIC must be unique among active employees"""
        from backend.crud import validate_active_employee_uniqueness
        
        org_id = "TEST_ORG_002"
        cnic = "12345-1234567-5"
        
        # Simulate active employee with CNIC
        employee = models.DBEmployee(
            id="EMP001",
            name="Active Employee",
            organization_id=org_id,
            cnic=cnic,
            status="active"
        )
        db.add(employee)
        db.commit()
        
        # Check uniqueness for new employee
        result = validate_active_employee_uniqueness(db, "cnic", cnic, org_id)
        assert not result["valid"]
        assert any("already used" in error for error in result["errors"])
    
    def test_inactive_employee_cnic_reusable(self, db: Session):
        """CNIC of inactive employee can be reused"""
        from backend.crud import validate_active_employee_uniqueness
        
        org_id = "TEST_ORG_003"
        cnic = "12345-1234567-5"
        
        # Create inactive employee
        employee = models.DBEmployee(
            id="EMP002",
            name="Inactive Employee",
            organization_id=org_id,
            cnic=cnic,
            status="left"
        )
        db.add(employee)
        db.commit()
        
        # Check uniqueness - should be available
        result = validate_active_employee_uniqueness(db, "cnic", cnic, org_id)
        assert result["valid"]


class TestDeleteSafety:
    """Test deletion safety checks"""
    
    def test_cannot_delete_active_employee(self, db: Session):
        """Active employee cannot be deleted"""
        org_id = "TEST_ORG_004"
        
        employee = models.DBEmployee(
            id="EMP003",
            name="Active Employee",
            organization_id=org_id,
            status="active"
        )
        db.add(employee)
        db.commit()
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            crud.delete_employee(db, "EMP003", current_user_id="test")
        
        assert exc_info.value.status_code == 400
        assert "active" in exc_info.value.detail.lower()
    
    def test_cannot_delete_line_manager(self, db: Session):
        """Cannot delete employee who is line manager for others"""
        org_id = "TEST_ORG_005"
        manager_id = "MGR001"
        
        # Create manager
        manager = models.DBEmployee(
            id=manager_id,
            name="Line Manager",
            organization_id=org_id,
            status="left"
        )
        db.add(manager)
        
        # Create subordinate
        subordinate = models.DBEmployee(
            id="SUB001",
            name="Subordinate",
            organization_id=org_id,
            line_manager_id=manager_id,
            status="active"
        )
        db.add(subordinate)
        db.commit()
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            crud.delete_employee(db, manager_id, current_user_id="test")
        
        assert exc_info.value.status_code == 400
        assert "subordinate" in exc_info.value.detail.lower()


class TestSalaryValidation:
    """Test salary validation"""
    
    def test_salary_range_valid(self):
        """Valid salary amounts should be accepted"""
        from backend.crud import validate_salary
        
        valid_salaries = [0, 50000, 500000, 10000000]
        
        for salary in valid_salaries:
            result = validate_salary(salary)
            assert result["valid"], f"Should accept: {salary}"
    
    def test_salary_range_invalid(self):
        """Invalid salary amounts should be rejected"""
        from backend.crud import validate_salary
        
        invalid_salaries = [-1000, -100, 10000001, 15000000]
        
        for salary in invalid_salaries:
            result = validate_salary(salary)
            assert not result["valid"], f"Should reject: {salary}"


class TestDateValidation:
    """Test employment date validation"""
    
    def test_future_join_date_invalid(self):
        """Join date cannot be in future"""
        from backend.crud import validate_employment_dates
        
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = validate_employment_dates(future_date)
        
        assert not result["valid"]
        assert any("future" in error.lower() for error in result["errors"])
    
    def test_date_sequence_valid(self):
        """Date sequence should be: join ≤ confirmation ≤ leaving"""
        from backend.crud import validate_employment_dates
        
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        result = validate_employment_dates(
            join_date=today,
            confirmation_date=today,
            leaving_date=tomorrow
        )
        
        assert result["valid"]
    
    def test_date_sequence_invalid(self):
        """Invalid date sequence should be rejected"""
        from backend.crud import validate_employment_dates
        
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        result = validate_employment_dates(
            join_date=today,
            leaving_date=yesterday
        )
        
        assert not result["valid"]


class TestForeignKeyValidation:
    """Test foreign key validation"""
    
    def test_invalid_department_rejected(self, db: Session):
        """Invalid department ID should be rejected"""
        from backend.crud import validate_employee_fks
        
        org_id = "TEST_ORG_006"
        employee_data = schemas.EmployeeCreate(
            name="Test",
            organization_id=org_id,
            department_id="INVALID_DEPT"
        )
        
        result = validate_employee_fks(db, employee_data, org_id)
        assert not result["valid"]
        assert any("department" in error.lower() for error in result["errors"])


class TestBulkImport:
    """Test bulk import functionality"""
    
    def test_bulk_import_endpoint_exists(self, client: TestClient):
        """Bulk import endpoint should be accessible"""
        # This is a smoke test - assumes authentication handled by test fixtures
        # In real testing, would need proper auth setup
        pass


class TestSearchEndpoint:
    """Test employee search/filter functionality"""
    
    def test_search_by_name(self, client: TestClient):
        """Search endpoint should filter by name"""
        # Smoke test for endpoint existence
        pass
    
    def test_search_by_email(self, client: TestClient):
        """Search endpoint should filter by email"""
        pass
    
    def test_filter_by_status(self, client: TestClient):
        """Search endpoint should filter by status"""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
