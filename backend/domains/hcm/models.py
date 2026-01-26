from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
from backend.domains.core.models import PrismaAuditMixin

class AuditMixin:
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(String)
    updated_by = Column(String)

class DBEmployee(Base, PrismaAuditMixin):
    __tablename__ = "hcm_employees"

    def __init__(self, *args, **kwargs):
        # Backwards-compatibility: accept common legacy keyword names and map them
        alias_map = {
            'code': 'employee_code',
            'date_of_joining': 'join_date',
            # keep date_of_birth as-is if provided
        }
        for old_key, new_key in alias_map.items():
            if old_key in kwargs and new_key not in kwargs:
                kwargs[new_key] = kwargs.pop(old_key)
        super().__init__(*args, **kwargs)

    # Computed Properties for ease of serialization
    @property
    def grade(self):
        return self.grade_rel.name if self.grade_rel else None

    @property
    def employmentLevel(self):
        # Grade -> JobLevel -> Name
        return self.grade_rel.job_level.name if self.grade_rel and self.grade_rel.job_level else None

    @property
    def designation(self):
        return self.designation_rel.name if self.designation_rel else None

    @property
    def department(self):
        return self.department_rel.name if self.department_rel else None

    @property
    def hrPlant(self):
        return self.plant_rel.name if self.plant_rel else None

    @property
    def shift(self):
        return self.shift_rel.name if self.shift_rel else None

    id = Column(String, primary_key=True, index=True)
    employee_code = Column(String)
    name = Column(String, index=True)
    eobi_status = Column(Boolean, default=False)
    social_security_status = Column(Boolean, default=False)
    medical_status = Column(Boolean, default=False)
    role = Column(String)
    organization_id = Column(String, ForeignKey("core_organizations.id"), index=True, nullable=True)
    
    # Foreign Keys
    department_id = Column(String, ForeignKey("core_departments.id"))
    designation_id = Column(String, ForeignKey("hcm_designations.id"))
    grade_id = Column(String, ForeignKey("hcm_grades.id"))
    plant_id = Column(String, ForeignKey("core_locations.id"))
    shift_id = Column(String, ForeignKey("hcm_shifts.id"))

    status = Column(String)
    join_date = Column(String)
    email = Column(String, unique=True, index=True)
    date_of_birth = Column(String, nullable=True)
    
    # Personal Details
    father_name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    cnic = Column(String, nullable=True)
    cnic_expiry = Column(String, nullable=True)
    religion = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    
    # Contact
    phone = Column(String, nullable=True)
    personal_email = Column(String, nullable=True)
    personal_phone = Column(String, nullable=True)
    present_address = Column(String, nullable=True)
    permanent_address = Column(String, nullable=True)
    present_district = Column(String, nullable=True)
    permanent_district = Column(String, nullable=True)
    
    # Financial
    gross_salary = Column(Float, default=0.0)
    payment_mode = Column(String, nullable=True)
    bank_account = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    eobi_number = Column(String, nullable=True)
    social_security_number = Column(String, nullable=True)

    # Missing fields added
    probation_period = Column(String, nullable=True)
    confirmation_date = Column(String, nullable=True)
    leaving_date = Column(String, nullable=True)
    leaving_type = Column(String, nullable=True)
    cnic_issue_date = Column(String, nullable=True)
    line_manager_id = Column(String, ForeignKey("hcm_employees.id"), nullable=True)
    sub_department_id = Column(String, ForeignKey("core_sub_departments.id"), nullable=True)
    
    # Self-Service Fields
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    emergency_contact_relation = Column(String, nullable=True)
    profile_photo_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)  # Short employee bio for directory

    # Backwards-compatible accessors used across older code/tests
    @property
    def date_of_joining(self):
        return self.join_date

    @property
    def separation_date(self):
        return self.leaving_date

    # Relationships
    department_rel = relationship("DBDepartment", foreign_keys=[department_id])
    designation_rel = relationship("DBDesignation", foreign_keys=[designation_id])
    grade_rel = relationship("DBGrade", foreign_keys=[grade_id])
    plant_rel = relationship("DBHRPlant", foreign_keys=[plant_id])
    shift_rel = relationship("DBShift", foreign_keys=[shift_id])
    line_manager = relationship("DBEmployee", remote_side=[id], foreign_keys=[line_manager_id])
    sub_department = relationship("DBSubDepartment", foreign_keys=[sub_department_id])
    
    education = relationship("DBEducation", backref="employee", cascade="all, delete-orphan")
    experience = relationship("DBExperience", backref="employee", cascade="all, delete-orphan")
    family = relationship("DBFamily", backref="employee", cascade="all, delete-orphan")
    discipline = relationship("DBDiscipline", backref="employee", cascade="all, delete-orphan")
    increments = relationship("DBIncrement", backref="employee", cascade="all, delete-orphan")

class DBJobLevel(Base, PrismaAuditMixin):
    __tablename__ = "hcm_job_levels"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    code = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    level_number = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    grades = relationship("DBGrade", backref="job_level", cascade="all, delete-orphan")

    @property
    def isActive(self):
        return self.is_active

class DBGrade(Base, PrismaAuditMixin):
    __tablename__ = "hcm_grades"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True)
    level = Column(Integer)
    job_level_id = Column(String, ForeignKey("hcm_job_levels.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    code = Column(String, unique=True)

class DBCandidate(Base, AuditMixin):
    __tablename__ = "hcm_candidates"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    phone = Column(String, nullable=True)
    position_applied = Column(String)
    current_stage = Column(String, default="Applied")
    score = Column(Integer, default=0)
    resume_url = Column(String, nullable=True)
    applied_date = Column(String)
    avatar = Column(String, nullable=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=True)

    @property
    def isActive(self):
        return self.is_active

class DBDesignation(Base, PrismaAuditMixin):
    __tablename__ = "hcm_designations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True)
    grade_id = Column(String, ForeignKey("hcm_grades.id"), nullable=False)
    department_id = Column(String, ForeignKey("core_departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    code = Column(String, unique=True)

    @property
    def isActive(self):
        return self.is_active

class DBShift(Base, PrismaAuditMixin):
    __tablename__ = "hcm_shifts"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    type = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    grace_period = Column(Integer)
    break_duration = Column(Integer)
    work_days = Column(String)
    color = Column(String, nullable=True)
    description = Column(String, nullable=True)
    isActive = Column(Boolean, default=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    @property
    def is_active(self):
        return self.isActive

    @property
    def startTime(self):
        return self.start_time

    @property
    def endTime(self):
        return self.end_time

    @property
    def gracePeriod(self):
        return self.grace_period

    @property
    def breakDuration(self):
        return self.break_duration

    @property
    def workDays(self):
        return self.work_days

class DBEducation(Base, AuditMixin):
    __tablename__ = "hcm_employee_education"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"))
    degree = Column(String)
    institute = Column(String)
    passing_year = Column(String)
    score = Column(String)
    marks_obtained = Column(Float)
    total_marks = Column(Float)

    @property
    def year(self): return self.passing_year
    @property
    def gradeGpa(self): return self.score
    @property
    def marksObtained(self): return self.marks_obtained
    @property
    def totalMarks(self): return self.total_marks

class DBExperience(Base, AuditMixin):
    __tablename__ = "hcm_employee_experience"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"))
    company_name = Column(String)
    designation = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    gross_salary = Column(Float)
    remarks = Column(String)

    @property
    def orgName(self): return self.company_name
    @property
    def to(self): return self.end_date
    @property
    def grossSalary(self): return self.gross_salary

class DBFamily(Base, AuditMixin):
    __tablename__ = "hcm_employee_family"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"))
    name = Column(String)
    relationship = Column(String)
    dob = Column(String)

class DBDiscipline(Base, AuditMixin):
    __tablename__ = "hcm_employee_discipline"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"))
    date = Column(String)
    description = Column(String)
    outcome = Column(String)

class DBIncrement(Base, AuditMixin):
    __tablename__ = "hcm_employee_increments"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"))
    effective_date = Column(String)
    amount = Column(Float)
    increment_type = Column(String)
    remarks = Column(String)
    previous_salary = Column(Float)
    new_gross = Column(Float)
    house_rent = Column(Float)
    utility = Column(Float)
    other_allowance = Column(Float)

    @property
    def effectiveDate(self): return self.effective_date
    @property
    def type(self): return self.increment_type
    @property
    def newGross(self): return self.new_gross
    @property
    def newHouseRent(self): return self.house_rent
    @property
    def newUtilityAllowance(self): return self.utility
    @property
    def newOtherAllowance(self): return self.other_allowance

class DBOnboardingHire(Base, AuditMixin):
    __tablename__ = "hcm_onboarding_hires"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    mentor = Column(String)
    start_date = Column(String)
    progress = Column(Integer, default=0)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    steps = relationship("DBOnboardingStep", backref="hire", cascade="all, delete-orphan")

class DBOnboardingStep(Base, AuditMixin):
    __tablename__ = "hcm_onboarding_steps"
    id = Column(String, primary_key=True, index=True)
    hire_id = Column(String, ForeignKey("hcm_onboarding_hires.id"), nullable=False, index=True)
    label = Column(String)
    done = Column(Boolean, default=False)

class DBOffboardingExit(Base, AuditMixin):
    __tablename__ = "hcm_offboarding_exits"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    type = Column(String) # Resignation, Termination, etc.
    last_date = Column(String)
    status = Column(String, default="Initiated") # Initiated, In Progress, Cleared
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    checklist = relationship("DBOffboardingStep", backref="exit", cascade="all, delete-orphan")

class DBOffboardingStep(Base, AuditMixin):
    __tablename__ = "hcm_offboarding_steps"
    id = Column(String, primary_key=True, index=True)
    exit_id = Column(String, ForeignKey("hcm_offboarding_exits.id"), nullable=False, index=True)
    label = Column(String)
    done = Column(Boolean, default=False)

class DBGoal(Base, AuditMixin):
    __tablename__ = "hcm_goals"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    category = Column(String) # Operational, Strategic, Cultural, Development
    progress = Column(Integer, default=0)
    metric = Column(String)
    status = Column(String, default="Initiated")
    due_date = Column(String)
    weight = Column(Integer, default=0)
    description = Column(String)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=True, index=True) # Optional: Can be personal or team goal

    organization = relationship("DBOrganization", backref="goals")
    employee = relationship("DBEmployee", backref="goals")

class DBCourse(Base, AuditMixin):
    __tablename__ = "hcm_learning_courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    provider = Column(String)
    duration = Column(String)
    level = Column(String) # Beginner, Intermediate, Advanced
    category = Column(String)
    icon = Column(String)
    color = Column(String)
    progress = Column(Integer, default=0)
    status = Column(String, default="Not Started") # Not Started, In Progress, Completed
    score = Column(Integer, nullable=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=True, index=True)

    organization = relationship("DBOrganization", backref="courses")
    employee = relationship("DBEmployee", backref="course_enrollments")

class DBBenefitTier(Base, AuditMixin):
    __tablename__ = "hcm_benefit_tiers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String)
    price = Column(String)
    items = Column(String) # JSON list of strings
    icon = Column(String)
    popular = Column(Boolean, default=False)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

class DBBenefitEnrollment(Base, AuditMixin):
    __tablename__ = "hcm_benefit_enrollments"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tier = Column(String) # Standard, Gold, Platinum
    date = Column(String)
    status = Column(String, default="Pending") # Active, Pending
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=True, index=True)

    organization = relationship("DBOrganization", backref="benefit_enrollments")
    employee = relationship("DBEmployee", backref="benefits")

class DBExpense(Base, AuditMixin):
    __tablename__ = "hcm_expenses"
    id = Column(String, primary_key=True, index=True) # E-1234
    employee_name = Column(String, nullable=False)
    category = Column(String, nullable=False) # Travel, Meals, etc.
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    date = Column(String, nullable=False)
    status = Column(String, default="Pending") # Pending, Approved, Rejected, Paid
    receipt_url = Column(String, nullable=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=True, index=True)

    organization = relationship("DBOrganization", backref="expenses")
    employee = relationship("DBEmployee", backref="expense_claims")

class DBReward(Base, AuditMixin):
    __tablename__ = "hcm_rewards"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    points_required = Column(Integer, default=0)
    category = Column(String) # e.g., Gift Card, Experience, Merchandise
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    organization = relationship("DBOrganization", backref="rewards")

class DBRecognition(Base, AuditMixin):
    __tablename__ = "hcm_recognitions"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    receiver_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    message = Column(String, nullable=False)
    category = Column(String) # e.g., Team Player, Innovation, Customer Success
    points_awarded = Column(Integer, default=0)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    organization = relationship("DBOrganization", backref="recognitions")
    sender = relationship("DBEmployee", foreign_keys=[sender_id], backref="given_recognitions")
    receiver = relationship("DBEmployee", foreign_keys=[receiver_id], backref="received_recognitions")

class DBRewardPoint(Base, AuditMixin):
    __tablename__ = "hcm_reward_points"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    balance = Column(Integer, default=0)
    total_earned = Column(Integer, default=0)
    total_redeemed = Column(Integer, default=0)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    organization = relationship("DBOrganization", backref="reward_points")
    employee = relationship("DBEmployee", backref="loyalty_profile")

class DBRewardPointTransaction(Base, AuditMixin):
    __tablename__ = "hcm_reward_point_transactions"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    points = Column(Integer, nullable=False) # Positive for earned, negative for redeemed
    type = Column(String, nullable=False) # e.g., EARNED, REDEEMED, ADJUSTED
    description = Column(String) # e.g., Recognition from John Doe, Redeemed Gift Card
    reference_id = Column(String, ForeignKey("hcm_employees.id")) # e.g., Recognition ID or Reward ID
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    organization = relationship("DBOrganization", backref="reward_transactions")
    employee = relationship("DBEmployee", foreign_keys=[employee_id], backref="reward_transactions")

class DBAttendance(Base, AuditMixin):
    __tablename__ = "hcm_attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"), nullable=False, index=True)
    plant_id = Column(String, ForeignKey("core_locations.id"), nullable=True, index=True)
    date = Column(String, nullable=False, index=True) # YYYY-MM-DD
    clock_in = Column(String, nullable=True)
    clock_out = Column(String, nullable=True)
    status = Column(String, default="Absent") # Present, Absent, Leave, Late, Half Day
    shift_id = Column(String, ForeignKey("hcm_shifts.id"), nullable=True)
    verification_type = Column(String, default="Manual") # Facial, GPS, Manual, Biometric
    location = Column(String, nullable=True) # Geofence location name
    remarks = Column(String, nullable=True)
    
    # Enhanced Fields
    overtime_hours = Column(Float, default=0.0)
    early_leave = Column(Boolean, default=False)
    late_minutes = Column(Integer, default=0)
    
    # Relationships
    organization = relationship("DBOrganization", backref="attendance_records")
    employee = relationship("DBEmployee", backref="attendance_records")
    plant = relationship("DBHRPlant", backref="attendance_records")
    shift = relationship("DBShift")

    # Computed properties for API response
    @property
    def employee_name(self):
        return self.employee.name if self.employee else None

    @property
    def employee_code(self):
        return self.employee.employee_code if self.employee else None

    @property
    def shift_name(self):
        return self.shift.name if self.shift else None

    @property
    def duration(self):
        """Calculate duration between clock_in and clock_out"""
        if self.clock_in and self.clock_out:
            try:
                from datetime import datetime
                fmt = "%H:%M"
                t_in = datetime.strptime(self.clock_in, fmt)
                t_out = datetime.strptime(self.clock_out, fmt)
                diff = t_out - t_in
                hours, remainder = divmod(diff.seconds, 3600)
                minutes = remainder // 60
                return f"{hours}h {minutes}m"
            except:
                return "-"
        return "-"


class DBAttendanceCorrection(Base, AuditMixin):
    """Attendance Correction Request Model"""
    __tablename__ = "hcm_attendance_corrections"
    
    id = Column(String, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"), nullable=False, index=True)
    date = Column(String, nullable=False) # YYYY-MM-DD
    type = Column(String, nullable=False) # Missing Punch, Shift Swap, Time Correction, Wrong Status
    
    # Original values
    original_clock_in = Column(String, nullable=True)
    original_clock_out = Column(String, nullable=True)
    original_status = Column(String, nullable=True)
    
    # Requested corrections
    requested_clock_in = Column(String, nullable=True)
    requested_clock_out = Column(String, nullable=True)
    requested_status = Column(String, nullable=True)
    
    reason = Column(String, nullable=False)
    status = Column(String, default="Pending") # Pending, Approved, Rejected
    
    approved_by = Column(String, ForeignKey("core_users.id"), nullable=True)
    approved_at = Column(String, nullable=True)
    rejection_reason = Column(String, nullable=True)
    
    # Relationships
    employee = relationship("DBEmployee")

    @property
    def employee_name(self):
        return self.employee.name if self.employee else None

    @property
    def employee_code(self):
        return self.employee.employee_code if self.employee else None

class DBPayrollLedger(Base, AuditMixin):
    """Enhanced Payroll Ledger with component breakdown"""
    __tablename__ = "hcm_payroll_ledger"
    __table_args__ = (
        Index('idx_payroll_period_emp', 'employee_id', 'period_month', 'period_year', unique=True),
        Index('idx_payroll_org_period', 'organization_id', 'period_month', 'period_year'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"), nullable=False, index=True)
    payroll_run_id = Column(String, ForeignKey("hcm_payroll_runs.id"), nullable=True, index=True)
    period_month = Column(String, nullable=False)  # e.g. "January"
    period_year = Column(String, nullable=False)  # e.g. "2026"

    # Legacy compatibility field - some analytics code expects a period_start_date
    period_start_date = Column(String, nullable=True)
    
    # Salary Breakdown
    basic_salary = Column(Float, default=0.0)
    house_rent = Column(Float, default=0.0)
    medical_allowance = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    other_allowances = Column(Float, default=0.0)
    gross_salary = Column(Float, default=0.0)
    
    # Deductions
    income_tax = Column(Float, default=0.0)
    eobi_deduction = Column(Float, default=0.0)
    social_security = Column(Float, default=0.0)
    loan_deduction = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    
    # Attendance Adjustments
    lop_days = Column(Float, default=0.0)  # Loss of Pay days
    lop_amount = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    overtime_amount = Column(Float, default=0.0)
    
    # Final
    net_salary = Column(Float, default=0.0)
    
    # Status & Payment
    status = Column(String, default="Draft")  # Draft, Processed, Approved, Paid
    payment_date = Column(String, nullable=True)
    payment_mode = Column(String, nullable=True)  # Cash, Bank Transfer, Cheque
    payment_reference = Column(String, nullable=True)
    
    # JSON for detailed component breakdown
    salary_components_json = Column(String, nullable=True)  # JSON array of components
    
    # Relationships
    employee = relationship("DBEmployee", backref="payroll_records")


class DBSalaryComponent(Base, AuditMixin):
    """Configurable Salary Components (Allowances & Deductions)"""
    __tablename__ = "hcm_salary_components"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    code = Column(String, nullable=False)  # HRA, MEDICAL, TAX, etc.
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Type: earning or deduction
    component_type = Column(String, nullable=False)  # "earning" or "deduction"
    
    # Calculation
    calculation_type = Column(String, default="fixed")  # fixed, percentage
    percentage_of = Column(String, nullable=True)  # "basic" if percentage-based
    default_amount = Column(Float, default=0.0)
    
    # Flags
    is_taxable = Column(Boolean, default=True)
    is_statutory = Column(Boolean, default=False)  # EOBI, Tax, etc.
    is_active = Column(Boolean, default=True)
    
    # Display Order
    display_order = Column(Integer, default=0)


class DBEmployeeSalaryStructure(Base, AuditMixin):
    """Employee-specific salary component assignments"""
    __tablename__ = "hcm_employee_salary_structures"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    component_id = Column(String, ForeignKey("hcm_salary_components.id"), nullable=False)
    
    # Override values
    amount = Column(Float, default=0.0)
    percentage = Column(Float, nullable=True)  # If percentage-based
    
    # Effective dates
    effective_from = Column(String, nullable=False)
    effective_to = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    employee = relationship("DBEmployee", backref="salary_structure")
    component = relationship("DBSalaryComponent")


class DBTaxSlab(Base, AuditMixin):
    """Configurable Tax Slabs for Income Tax Calculation"""
    __tablename__ = "hcm_tax_slabs"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    
    # Tax Year
    tax_year = Column(String, nullable=False)  # e.g. "2025-2026"
    
    # Income Range
    min_income = Column(Float, nullable=False)
    max_income = Column(Float, nullable=True)  # Null = no upper limit
    
    # Tax Calculation
    fixed_tax = Column(Float, default=0.0)  # Fixed amount for this slab
    tax_rate = Column(Float, default=0.0)  # Percentage on excess
    excess_over = Column(Float, default=0.0)  # Calculate rate on amount exceeding this
    
    is_active = Column(Boolean, default=True)


class DBTaxDeductionType(Base, AuditMixin):
    """Master list of tax deduction types under Income Tax Ordinance 2001"""
    __tablename__ = "hcm_tax_deduction_types"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    
    code = Column(String, nullable=False)  # SECTION_60D, SECTION_62, SECTION_64, etc.
    name = Column(String, nullable=False)  # Tuition Fee, Charitable Donation, etc.
    section = Column(String, nullable=False)  # 60D, 62, 63, 64
    description = Column(String, nullable=True)
    
    # Type: deductible_allowance (reduces taxable income) or tax_credit (reduces tax)
    deduction_type = Column(String, nullable=False)  # "allowance" or "credit"
    
    # Eligibility
    max_income_limit = Column(Float, nullable=True)  # e.g., 1,500,000 for Section 60D
    
    # Calculation parameters (stored as percentages or fixed amounts)
    calc_percentage = Column(Float, nullable=True)  # e.g., 5% for tuition
    calc_income_percentage = Column(Float, nullable=True)  # e.g., 25% of income
    calc_per_unit_limit = Column(Float, nullable=True)  # e.g., 60,000 per child
    calc_max_limit = Column(Float, nullable=True)  # Overall max limit
    
    requires_document = Column(Boolean, default=True)
    requires_ntn = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)


class DBEmployeeTaxDeduction(Base, AuditMixin):
    """Employee's claimed tax deductions for a tax year"""
    __tablename__ = "hcm_employee_tax_deductions"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    deduction_type_id = Column(String, ForeignKey("hcm_tax_deduction_types.id"), nullable=False)
    tax_year = Column(String, nullable=False)  # e.g., "2025-2026"
    
    # Claimed amounts
    claimed_amount = Column(Float, default=0.0)  # Total amount claimed (e.g., tuition paid)
    approved_amount = Column(Float, nullable=True)  # Amount approved after verification
    
    # Section 60D specific
    number_of_children = Column(Integer, nullable=True)  # For tuition fee
    
    # Documentation
    institution_name = Column(String, nullable=True)  # School/University name
    institution_ntn = Column(String, nullable=True)  # NTN of institution
    document_urls = Column(String, nullable=True)  # JSON array of document URLs
    
    # Status
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    approved_by = Column(String, nullable=True)
    approved_date = Column(String, nullable=True)
    rejection_reason = Column(String, nullable=True)
    
    # Relationships
    employee = relationship("DBEmployee", backref="tax_deductions")
    deduction_type = relationship("DBTaxDeductionType")


class DBPayrollRun(Base, AuditMixin):
    """Payroll Processing Batch"""
    __tablename__ = "hcm_payroll_runs"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    
    # Period
    period_month = Column(String, nullable=False)
    period_year = Column(String, nullable=False)
    
    # Status: Draft, Processing, Processed, Approved, Paid
    status = Column(String, default="Draft")
    
    # Counts
    total_employees = Column(Integer, default=0)
    processed_employees = Column(Integer, default=0)
    
    # Totals
    total_gross = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    total_net = Column(Float, default=0.0)
    
    # Processing Info
    processed_at = Column(String, nullable=True)
    processed_by = Column(String, nullable=True)
    approved_at = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    paid_at = Column(String, nullable=True)
    paid_by = Column(String, nullable=True)
    
    # Notes
    notes = Column(String, nullable=True)


class DBLeaveType(Base, AuditMixin):
    """Configurable Leave Types per Organization"""
    __tablename__ = "hcm_leave_types"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    code = Column(String, nullable=False)  # ANNUAL, SICK, CASUAL, MATERNITY, etc.
    name = Column(String, nullable=False)  # Display name
    description = Column(String, nullable=True)
    
    # Entitlement Configuration
    days_per_year = Column(Float, default=0.0)  # Default entitlement
    carry_forward_allowed = Column(Boolean, default=False)
    carry_forward_max = Column(Float, default=0.0)  # Max days to carry forward
    
    # Workflow Configuration
    requires_approval = Column(Boolean, default=True)
    requires_document = Column(Boolean, default=False)  # Medical certificate etc.
    min_days_notice = Column(Integer, default=0)  # Advance notice required
    
    # Validity
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("DBOrganization", backref="leave_types")


class DBLeaveBalance(Base, AuditMixin):
    __tablename__ = "hcm_leave_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False) # e.g. 2025
    
    # Entitlements
    annual_total = Column(Float, default=14.0)
    annual_used = Column(Float, default=0.0)
    annual_carry_forward = Column(Float, default=0.0)  # Carried from previous year
    
    sick_total = Column(Float, default=10.0)
    sick_used = Column(Float, default=0.0)
    
    casual_total = Column(Float, default=10.0)
    casual_used = Column(Float, default=0.0)
    
    unpaid_used = Column(Float, default=0.0)
    
    # Relationships
    organization = relationship("DBOrganization", backref="leave_balances")
    employee = relationship("DBEmployee", backref="leave_balances")


class DBLeaveRequest(Base, AuditMixin):
    __tablename__ = "hcm_leave_requests"
    
    id = Column(String, primary_key=True, index=True) # LR-123
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(String, ForeignKey("hcm_leave_types.id"), nullable=True, index=True)  # Optional FK to leave type
    type = Column(String, nullable=False) # Annual, Sick, Casual, Unpaid (kept for backward compat)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    days = Column(Float, default=1.0)
    half_day = Column(String, nullable=True)  # None, "AM", "PM" for half-day leaves
    reason = Column(String, nullable=True)
    status = Column(String, default="Pending") # Pending, Approved, Rejected, Cancelled
    
    # Approval Workflow
    approved_by = Column(String, ForeignKey("hcm_employees.id"), nullable=True, index=True)
    approved_at = Column(String, nullable=True)  # ISO timestamp
    rejection_reason = Column(String, nullable=True)
    
    # Document Support
    document_url = Column(String, nullable=True)  # For medical certificates etc.
    
    # Relationships
    organization = relationship("DBOrganization", backref="leave_requests")
    employee = relationship("DBEmployee", foreign_keys=[employee_id], backref="leave_requests")
    approver = relationship("DBEmployee", foreign_keys=[approved_by])
    leave_type = relationship("DBLeaveType", backref="leave_requests")



class DBJobVacancy(Base, PrismaAuditMixin):
    __tablename__ = "hcm_job_vacancies"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    department = Column(String) # Stored as string name/code in CRUD
    location = Column(String)
    type = Column(String)
    posted_date = Column(String)
    status = Column(String)
    applicants_count = Column(Integer, default=0)
    description = Column(String, nullable=True)
    requirements = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)


class DBPosition(Base, PrismaAuditMixin):
    __tablename__ = "hcm_positions"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    department_id = Column(String, ForeignKey("core_departments.id"), nullable=True)
    grade_id = Column(String, ForeignKey("hcm_grades.id"), nullable=True)
    designation_id = Column(String, ForeignKey("hcm_designations.id"), nullable=True)
    reports_to = Column(String, nullable=True) # ID of reporting position/employee
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    @property
    def isActive(self):
        return self.is_active


class DBHoliday(Base, PrismaAuditMixin):
    __tablename__ = "hcm_holidays"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    date = Column(String)
    type = Column(String)
    is_recurring = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    @property
    def isRecurring(self):
        return self.is_recurring


class DBBank(Base, PrismaAuditMixin):
    __tablename__ = "hcm_banks"

    id = Column(String, primary_key=True, index=True)
    bank_name = Column(String)
    account_number = Column(String)
    account_title = Column(String)
    branch = Column(String, nullable=True)
    iban = Column(String, nullable=True)
    swift_code = Column(String, nullable=True)
    currency = Column(String, default="PKR")
    is_active = Column(Boolean, default=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    @property
    def isActive(self):
        return self.is_active


class DBPerformanceReview(Base, PrismaAuditMixin):
    """Performance Review Model"""
    __tablename__ = "hcm_performance_reviews"

    id = Column(String, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    reviewer_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    review_period = Column(String, nullable=False)
    review_date = Column(String, nullable=False)
    status = Column(String, default="Draft")  # Draft, Submitted, Approved
    score = Column(Integer, default=0)
    feedback = Column(String, nullable=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    # Relationships
    employee = relationship("DBEmployee", foreign_keys=[employee_id], backref="performance_reviews")
    reviewer = relationship("DBEmployee", foreign_keys=[reviewer_id])


class DBOvertimeRequest(Base, AuditMixin):
    """Overtime Request Model"""
    __tablename__ = "hcm_overtime_requests"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    
    date = Column(String, nullable=False) # YYYY-MM-DD
    hours = Column(Float, nullable=False)
    multiplier = Column(Float, default=1.5)
    reason = Column(String, nullable=True)
    
    status = Column(String, default="Pending") # Pending, Approved, Rejected
    approved_by = Column(String, ForeignKey("hcm_employees.id"), nullable=True)
    approved_at = Column(String, nullable=True)
    rejection_reason = Column(String, nullable=True)
    
    # Relationships
    organization = relationship("DBOrganization", backref="overtime_requests")
    employee = relationship("DBEmployee", foreign_keys=[employee_id], backref="overtime_requests")
    approver = relationship("DBEmployee", foreign_keys=[approved_by])



# ===== Self-Service Models =====

class DBDocumentRequest(Base, AuditMixin):
    """Employee document requests (certificates, letters, verification)"""
    __tablename__ = "hcm_document_requests"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    
    # Request Details
    document_type = Column(String, nullable=False)  # Experience Letter, Salary Certificate, etc.
    purpose = Column(String, nullable=True)  # Why document is needed
    additional_notes = Column(String, nullable=True)
    
    # Workflow
    status = Column(String, default="Pending")  # Pending, Approved, Ready, Delivered, Rejected
    requested_date = Column(String, nullable=False)
    approved_by = Column(String, ForeignKey("hcm_employees.id"), nullable=True)
    approved_date = Column(String, nullable=True)
    fulfilled_date = Column(String, nullable=True)
    rejection_reason = Column(String, nullable=True)
    
    # Generated Document
    document_url = Column(String, nullable=True)  # Link to generated/uploaded document
    
    # Relationships
    organization = relationship("DBOrganization", backref="document_requests")
    employee = relationship("DBEmployee", foreign_keys=[employee_id], backref="document_requests")
    approver = relationship("DBEmployee", foreign_keys=[approved_by])


class DBEmployeeDocument(Base, AuditMixin):
    """Employee document library (contracts, certificates, IDs)"""
    __tablename__ = "hcm_employee_documents"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    
    # Document Details
    document_type = Column(String, nullable=False)  # Offer Letter, Contract, Certificate, ID Copy, etc.
    document_name = Column(String, nullable=False)
    document_url = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String, nullable=True)
    
    # Metadata
    description = Column(String, nullable=True)
    upload_date = Column(String, nullable=False)
    uploaded_by = Column(String, ForeignKey("hcm_employees.id"), nullable=False)
    expiry_date = Column(String, nullable=True)  # For certifications, visas, etc.
    is_private = Column(Boolean, default=True)  # Visibility control
    
    # Relationships
    organization = relationship("DBOrganization", backref="employee_documents")
    employee = relationship("DBEmployee", foreign_keys=[employee_id], backref="documents")
    uploader = relationship("DBEmployee", foreign_keys=[uploaded_by])


class DBInfoUpdateRequest(Base, AuditMixin):
    """Employee requests to update personal information"""
    __tablename__ = "hcm_info_update_requests"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    
    # Update Details
    field_name = Column(String, nullable=False)  # e.g., "present_address", "personal_phone"
    current_value = Column(String, nullable=True)
    new_value = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    
    # Workflow
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    requested_date = Column(String, nullable=False)
    approved_by = Column(String, ForeignKey("hcm_employees.id"), nullable=True)
    approved_date = Column(String, nullable=True)
    rejection_reason = Column(String, nullable=True)
    
    # Relationships
    organization = relationship("DBOrganization", backref="info_update_requests")
    employee = relationship("DBEmployee", foreign_keys=[employee_id], backref="info_update_requests")
    approver = relationship("DBEmployee", foreign_keys=[approved_by])


# ===== Notification Models =====

class DBNotification(Base, AuditMixin):
    """In-app notifications for employees"""
    __tablename__ = "hcm_notifications"
    
    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    recipient_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    sender_id = Column(String, ForeignKey("hcm_employees.id"), nullable=True)
    
    # Notification Content
    type = Column(String, nullable=False)  # LeaveApproved, DocumentReady, InfoUpdateApproved, etc.
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    action_url = Column(String, nullable=True)  # URL to relevant resource
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(String, nullable=True)
    is_sent_email = Column(Boolean, default=False)
    is_sent_sms = Column(Boolean, default=False)
    
    # Relationships
    organization = relationship("DBOrganization", backref="notifications")
    recipient = relationship("DBEmployee", foreign_keys=[recipient_id], backref="notifications")
    sender = relationship("DBEmployee", foreign_keys=[sender_id])


class DBNotificationPreference(Base, AuditMixin):
    """Employee notification preferences"""
    __tablename__ = "hcm_notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    
    # Notification Type
    notification_type = Column(String, nullable=False)  # leave_approved, document_ready, etc.
    
    # Channel Preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    in_app_enabled = Column(Boolean, default=True)
    
    # Relationships
    employee = relationship("DBEmployee", backref="notification_preferences")

class DBPromotionCycle(Base, AuditMixin):
    __tablename__ = "hcm_promotion_cycles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(String, default="Open")  # Open, Processing, Completed
    start_date = Column(String)
    end_date = Column(String)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    requests = relationship("DBPromotionRequest", back_populates="cycle", cascade="all, delete-orphan")

class DBPromotionRequest(Base, AuditMixin):
    __tablename__ = "hcm_promotion_requests"
    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("hcm_promotion_cycles.id"))
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=False, index=True)
    
    # Review Details
    type = Column(String)  # Increment, Promotion, Both
    current_salary = Column(Float)
    proposed_salary = Column(Float)
    current_designation_id = Column(String, ForeignKey("hcm_designations.id"), nullable=True)
    proposed_designation_id = Column(String, ForeignKey("hcm_designations.id"), nullable=True)
    current_grade_id = Column(String, ForeignKey("hcm_grades.id"), nullable=True)
    proposed_grade_id = Column(String, ForeignKey("hcm_grades.id"), nullable=True)
    
    reason = Column(String)
    performance_rating = Column(String)
    manager_remarks = Column(String)
    
    # Status & Workflow
    status = Column(String, default="Pending")  # Pending, HR_Approved, Finance_Approved, Final_Approved, Implemented, Rejected
    effective_date = Column(String)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)

    # Relationships
    cycle = relationship("DBPromotionCycle", back_populates="requests")
    employee = relationship("DBEmployee", foreign_keys=[employee_id])
    current_designation = relationship("DBDesignation", foreign_keys=[current_designation_id])
    proposed_designation = relationship("DBDesignation", foreign_keys=[proposed_designation_id])
    current_grade = relationship("DBGrade", foreign_keys=[current_grade_id])
    proposed_grade = relationship("DBGrade", foreign_keys=[proposed_grade_id])
    approvals = relationship("DBPromotionApproval", back_populates="request", cascade="all, delete-orphan")

class DBPromotionApproval(Base, AuditMixin):
    __tablename__ = "hcm_promotion_approvals"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("hcm_promotion_requests.id"), nullable=False)
    approver_id = Column(String, ForeignKey("core_users.id"), nullable=False)
    level = Column(String)  # HR, Finance, Final
    status = Column(String)  # Approved, Rejected
    remarks = Column(String)

    request = relationship("DBPromotionRequest", back_populates="approvals")
