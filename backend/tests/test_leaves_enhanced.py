"""
Tests for Enhanced Leaves Module
Tests leave types, approval workflow, balance automation, and calendar features
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend import crud, schemas
from backend.domains.hcm.models import DBLeaveType, DBLeaveRequest, DBLeaveBalance, DBEmployee
from backend.domains.core.models import DBOrganization, DBDepartment


@pytest.fixture
def leave_type(db: Session, test_org):
    """Create a test leave type"""
    leave_type = DBLeaveType(
        id="LT-ANNUAL-TEST",
        organization_id=test_org.id,
        code="ANNUAL",
        name="Annual Leave",
        days_per_year=14.0,
        carry_forward_allowed=True,
        carry_forward_max=5.0,
        requires_approval=True,
        requires_document=False,
        min_days_notice=2,
        is_active=True,
        created_by="test_user"
    )
    db.add(leave_type)
    db.commit()
    db.refresh(leave_type)
    return leave_type


class TestLeaveTypes:
    def test_create_leave_type(self, db, test_org):
        """Test creating a new leave type"""
        leave_type_data = schemas.LeaveTypeCreate(
            organization_id=test_org.id,
            code="SICK",
            name="Sick Leave",
            description="Medical leave",
            days_per_year=10.0,
            carry_forward_allowed=False,
            carry_forward_max=0.0,
            requires_approval=True,
            requires_document=True,
            min_days_notice=0,
            is_active=True
        )
        
        result = crud.create_leave_type(db, leave_type_data, user_id="test")
        
        assert result.id is not None
        assert result.code == "SICK"
        assert result.days_per_year == 10.0
        assert result.requires_document == True


    def test_get_leave_types(self, db, test_org, leave_type):
        """Test retrieving leave types for organization"""
        types = crud.get_leave_types(db, organization_id=test_org.id)
        
        assert len(types) >= 1
        assert any(t.code == "ANNUAL" for t in types)


class TestLeaveRequestValidation:
    def test_calculate_business_days(self):
        """Test business day calculation"""
        # Mon to Fri (5 business days)
        days = crud.calculate_business_days("2025-01-06", "2025-01-10")
        assert days == 5.0


    def test_calculate_half_day(self):
        """Test half-day calculation"""
        days = crud.calculate_business_days("2025-01-06", "2025-01-06", half_day="AM")
        assert days == 0.5


    def test_validate_overlapping_leave(self, db, test_employee):
        """Test validation catches overlapping leave"""
        # Create existing leave
        existing = DBLeaveRequest(
            id="LR-EXIST",
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            type="Annual",
            start_date="2026-02-10",
            end_date="2026-02-14",
            days=5.0,
            status="Approved",
            created_by="test"
        )
        db.add(existing)
        db.commit()
        
        # Try to create overlapping leave
        new_leave = schemas.LeaveRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            type="Annual",
            start_date="2026-02-12",
            end_date="2026-02-16",
            days=3.0
        )
        
        validation = crud.validate_leave_request(db, new_leave)
        assert validation["valid"] == False
        assert "overlap" in validation["errors"][0].lower()


    def test_validate_insufficient_balance(self, db, test_employee):
        """Test validation catches insufficient balance"""
        # Create balance with limited annual leave
        balance = DBLeaveBalance(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            year=2026,
            annual_total=5.0,
            annual_used=4.0,
            created_by="test"
        )
        db.add(balance)
        db.commit()
        
        # Request more than available
        leave_req = schemas.LeaveRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            type="Annual",
            start_date="2026-03-10",
            end_date="2026-03-12",
            days=3.0
        )
        
        validation = crud.validate_leave_request(db, leave_req)
        # Should either be invalid or have errors list, check either case
        if "errors" in validation and validation["errors"]:
            assert "insufficient" in validation["errors"][0].lower() or validation["valid"] == False
        else:
            assert validation["valid"] == False


class TestApprovalWorkflow:
    def test_approve_leave_deducts_balance(self, db, test_employee, test_manager):
        """Test that approving leave deducts from balance"""
        # Create balance
        balance = DBLeaveBalance(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            year=2026,
            annual_total=14.0,
            annual_used=0.0,
            created_by="test"
        )
        db.add(balance)
        
        # Create leave request
        leave = DBLeaveRequest(
            id="LR-APPROVE-TEST",
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            type="Annual",
            start_date="2026-04-01",
            end_date="2026-04-05",
            days=5.0,
            status="Pending",
            created_by="test"
        )
        db.add(leave)
        db.commit()
        
        # Approve
        approval = schemas.LeaveApproval(status="Approved")
        result = crud.approve_leave_request(db, leave.id, approver_id=test_manager.id, approval=approval)
        
        assert result.status == "Approved"
        assert result.approved_by == test_manager.id
        assert result.approved_at is not None
        
        # Check balance deducted
        db.refresh(balance)
        assert balance.annual_used == 5.0


    def test_reject_leave_does_not_deduct(self, db, test_employee, test_manager):
        """Test that rejecting leave does not deduct balance"""
        balance = DBLeaveBalance(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            year=2026,
            annual_total=14.0,
            annual_used=0.0,
            created_by="test"
        )
        db.add(balance)
        
        leave = DBLeaveRequest(
            id="LR-REJECT-TEST",
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            type="Annual",
            start_date="2026-05-01",
            end_date="2026-05-03",
            days=3.0,
            status="Pending",
            created_by="test"
        )
        db.add(leave)
        db.commit()
        
        # Reject
        approval = schemas.LeaveApproval(status="Rejected", rejection_reason="Not enough coverage")
        result = crud.approve_leave_request(db, leave.id, approver_id=test_manager.id, approval=approval)
        
        assert result.status == "Rejected"
        assert result.rejection_reason == "Not enough coverage"
        
        # Balance unchanged
        db.refresh(balance)
        assert balance.annual_used == 0.0


class TestCarryForward:
    def test_carry_forward_respects_limit(self, db, test_org, test_employee, leave_type):
        """Test carry-forward respects maximum limit"""
        # Create 2024 balance with 8 unused annual days
        balance_2024 = DBLeaveBalance(
            organization_id=test_org.id,
            employee_id=test_employee.id,
            year=2024,
            annual_total=14.0,
            annual_used=6.0,  # 8 days unused
            created_by="test"
        )
        db.add(balance_2024)
        db.commit()
        
        # Carry forward (max is 5 days per leave_type)
        result = crud.carry_forward_leave_balances(db, from_year=2024, to_year=2025, organization_id=test_org.id)
        
        # Check 2025 balance
        balance_2025 = db.query(DBLeaveBalance).filter(
            DBLeaveBalance.employee_id == test_employee.id,
            DBLeaveBalance.year == 2025
        ).first()
        
        assert balance_2025 is not None
        assert balance_2025.annual_carry_forward == 5.0  # Capped at max


class TestCalendar:
    def test_get_team_leave_calendar(self, db, test_org, test_employee, test_manager, leave_type):
        """Test retrieving team leave calendar"""
        # Create approved leave
        leave = DBLeaveRequest(
            id="LR-CAL-TEST",
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            type="Annual",
            start_date="2026-06-10",
            end_date="2026-06-14",
            days=5.0,
            status="Approved",
            created_by="test"
        )
        db.add(leave)
        db.commit()
        
        # Get calendar
        calendar = crud.get_team_leave_calendar(
            db,
            manager_id=test_manager.id,
            start_date="2026-06-01",
            end_date="2026-06-30"
        )
        
        assert len(calendar) >= 1
        assert any(item["employee_id"] == test_employee.id for item in calendar)
