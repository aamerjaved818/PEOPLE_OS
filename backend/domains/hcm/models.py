from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer, String)
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
    line_manager_id = Column(String, nullable=True)
    sub_department_id = Column(String, nullable=True)

    # Relationships
    department_rel = relationship("DBDepartment", foreign_keys=[department_id])
    designation_rel = relationship("DBDesignation", foreign_keys=[designation_id])
    grade_rel = relationship("DBGrade", foreign_keys=[grade_id])
    plant_rel = relationship("DBHRPlant", foreign_keys=[plant_id])
    shift_rel = relationship("DBShift", foreign_keys=[shift_id])
    
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
    job_level_id = Column(String, ForeignKey("hcm_job_levels.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False, index=True)
    code = Column(String, unique=True)

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

# ... (Additional HCM models abbreviated for brevity, can be added if needed)

class DBAttendance(Base, AuditMixin):
    __tablename__ = "hcm_attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"), nullable=False, index=True)
    date = Column(String, nullable=False, index=True) # YYYY-MM-DD
    clock_in = Column(String, nullable=True)
    clock_out = Column(String, nullable=True)
    status = Column(String, default="Absent") # Present, Absent, Leave, Late, Half Day
    shift_id = Column(String, ForeignKey("hcm_shifts.id"), nullable=True)
    verification_type = Column(String, default="Manual") # Facial, GPS, Manual, Biometric
    location = Column(String, nullable=True) # Geofence location name
    remarks = Column(String, nullable=True)
    
    # Relationships
    employee = relationship("DBEmployee", backref="attendance_records")
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
    __tablename__ = "hcm_payroll_ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"), nullable=False)
    period_month = Column(String, nullable=False) # e.g. "January"
    period_year = Column(String, nullable=False) # e.g. "2025"
    
    basic_salary = Column(Float, default=0.0)
    gross_salary = Column(Float, default=0.0)
    net_salary = Column(Float, default=0.0)
    
    additions = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    
    status = Column(String, default="Draft") # Draft, Processed, Paid
    payment_date = Column(String, nullable=True)
    payment_mode = Column(String, nullable=True) # Cash, Bank Transfer
    
    # Relationships
    employee = relationship("DBEmployee", backref="payroll_records")

class DBLeaveBalance(Base, AuditMixin):
    __tablename__ = "hcm_leave_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False) # e.g. 2025
    
    # Entitlements
    annual_total = Column(Float, default=14.0)
    annual_used = Column(Float, default=0.0)
    
    sick_total = Column(Float, default=10.0)
    sick_used = Column(Float, default=0.0)
    
    casual_total = Column(Float, default=10.0)
    casual_used = Column(Float, default=0.0)
    
    unpaid_used = Column(Float, default=0.0)
    
    employee = relationship("DBEmployee", backref="leave_balances")

class DBLeaveRequest(Base, AuditMixin):
    __tablename__ = "hcm_leave_requests"
    
    id = Column(String, primary_key=True, index=True) # LR-123
    employee_id = Column(String, ForeignKey("hcm_employees.id", onupdate="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False) # Annual, Sick, Casual, Unpaid
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    days = Column(Float, default=1.0)
    reason = Column(String, nullable=True)
    status = Column(String, default="Pending") # Pending, Approved, Rejected
    
    # Relationships
    employee = relationship("DBEmployee", backref="leave_requests")


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

