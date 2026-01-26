
import json
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .shared import AuditBase

# --- Attendance Schemas ---
class AttendanceCreate(BaseModel):
    organization_id: str = Field(..., alias="organizationId")
    employee_id: str = Field(..., alias="employeeId")
    plant_id: Optional[str] = Field(None, alias="plantId")
    date: str  # YYYY-MM-DD
    clock_in: Optional[str] = Field(None, alias="clockIn")
    clock_out: Optional[str] = Field(None, alias="clockOut")
    status: Optional[str] = None
    shift_id: Optional[str] = Field(None, alias="shiftId")
    overtime_hours: Optional[float] = Field(0.0, alias="overtimeHours")
    early_leave: Optional[bool] = Field(False, alias="earlyLeave")
    late_minutes: Optional[int] = Field(0, alias="lateMinutes")
    verification_type: str = Field("Manual", alias="verificationType")
    location: Optional[str] = None
    remarks: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

class Attendance(AttendanceCreate, AuditBase):
    id: int
    employee_name: Optional[str] = Field(None, alias="employeeName")
    employee_code: Optional[str] = Field(None, alias="employeeCode")
    shift_name: Optional[str] = Field(None, alias="shiftName")
    duration: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AttendanceStats(BaseModel):
    present: int = 0
    late: int = 0
    absent: int = 0
    on_leave: int = Field(0, alias="onLeave")
    half_day: int = Field(0, alias="halfDay")
    total_employees: int = Field(0, alias="totalEmployees")
    date: str

    model_config = ConfigDict(populate_by_name=True)

# --- Attendance Search ---
class AttendanceSearch(BaseModel):
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    department_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    status: Optional[str] = None
    shift_id: Optional[str] = None
    skip: int = 0
    limit: int = 50

class AttendanceSearchResult(BaseModel):
    id: str
    employee_id: str
    employee_name: str
    date: str
    status: str
    clock_in: Optional[str]
    clock_out: Optional[str]
    shift_id: Optional[str]
    late_minutes: int
    overtime_minutes: int
    organization_id: str

class AttendanceSearchResponse(BaseModel):
    total: int
    returned: int
    skip: int
    limit: int
    has_more: bool
    records: List[AttendanceSearchResult]

# --- Bulk Operations ---
class AttendanceRecordImport(BaseModel):
    organization_id: str = Field(..., alias="organizationId")
    employee_id: str = Field(..., alias="employeeId")
    date: str
    clock_in: Optional[str] = Field(None, alias="clockIn")
    clock_out: Optional[str] = Field(None, alias="clockOut")
    status: Optional[str] = None
    plant_id: Optional[str] = Field(None, alias="plantId")
    shift_id: Optional[str] = Field(None, alias="shiftId")

    model_config = ConfigDict(populate_by_name=True)

class AttendanceRecordValidationResult(BaseModel):
    line_number: int
    employee_id: str
    date: str
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    action: str

class AttendanceBulkCreate(BaseModel):
    records: List[AttendanceCreate]

class AttendanceBulkValidationRequest(BaseModel):
    records: List[AttendanceRecordImport]
    dry_run: bool = False

class AttendanceBulkValidationResponse(BaseModel):
    total: int
    valid: int
    invalid: int
    warnings: int
    results: List[AttendanceRecordValidationResult]
    dry_run: bool
    error_manifest: str

# --- Correction Approval ---
class AttendanceCorrectionApproval(BaseModel):
    action: str
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")

    model_config = ConfigDict(populate_by_name=True)

class AttendanceUpsertRequest(BaseModel):
    organization_id: str = Field(..., alias="organizationId")
    employee_id: str = Field(..., alias="employeeId")
    date: str
    clock_in: Optional[str] = Field(None, alias="clockIn")
    clock_out: Optional[str] = Field(None, alias="clockOut")
    status: Optional[str] = None
    plant_id: Optional[str] = Field(None, alias="plantId")
    shift_id: Optional[str] = Field(None, alias="shiftId")
    force_update: bool = False
    model_config = ConfigDict(populate_by_name=True)

class AttendanceUpsertResult(BaseModel):
    employee_id: str
    date: str
    action: str
    record_id: int
    message: str

class AttendanceUpsertBulkRequest(BaseModel):
    records: List[AttendanceUpsertRequest]
    strategy: str = "smart"

class AttendanceUpsertResponse(BaseModel):
    total: int
    inserted: int
    updated: int
    skipped: int
    results: List[AttendanceUpsertResult]

# --- Corrections ---
class AttendanceCorrectionCreate(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    date: str
    type: str 
    original_clock_in: Optional[str] = Field(None, alias="originalClockIn")
    original_clock_out: Optional[str] = Field(None, alias="originalClockOut")
    original_status: Optional[str] = Field(None, alias="originalStatus")
    requested_clock_in: Optional[str] = Field(None, alias="requestedClockIn")
    requested_clock_out: Optional[str] = Field(None, alias="requestedClockOut")
    requested_status: Optional[str] = Field(None, alias="requestedStatus")
    reason: str
    model_config = ConfigDict(populate_by_name=True)

class AttendanceCorrection(AttendanceCorrectionCreate, AuditBase):
    id: str
    status: str = "Pending"
    employee_name: Optional[str] = Field(None, alias="employeeName")
    employee_code: Optional[str] = Field(None, alias="employeeCode")
    approved_by: Optional[str] = Field(None, alias="approvedBy")
    approved_at: Optional[str] = Field(None, alias="approvedAt")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AttendanceCorrectionApproval(BaseModel):
    action: str
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")


# --- Leave Schemas ---
class LeaveTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    days_per_year: float = Field(0.0, alias="daysPerYear")
    carry_forward_allowed: bool = Field(False, alias="carryForwardAllowed")
    carry_forward_max: float = Field(0.0, alias="carryForwardMax")
    requires_approval: bool = Field(True, alias="requiresApproval")
    requires_document: bool = Field(False, alias="requiresDocument")
    min_days_notice: int = Field(0, alias="minDaysNotice")
    is_active: bool = Field(True, alias="isActive")
    model_config = ConfigDict(populate_by_name=True)

class LeaveTypeCreate(LeaveTypeBase):
    organization_id: str = Field(..., alias="organizationId")

class LeaveType(LeaveTypeBase, AuditBase):
    id: str
    organization_id: str = Field(..., alias="organizationId")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class LeaveRequestCreate(BaseModel):
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: str = Field(..., alias="employeeId")
    leave_type_id: Optional[str] = Field(None, alias="leaveTypeId")
    type: str = "Annual"
    start_date: str = Field(..., alias="startDate")
    end_date: str = Field(..., alias="endDate")
    days: float = 1.0
    half_day: Optional[str] = Field(None, alias="halfDay")
    reason: Optional[str] = None
    document_url: Optional[str] = Field(None, alias="documentUrl")
    status: str = "Pending"
    model_config = ConfigDict(populate_by_name=True)

class LeaveRequest(LeaveRequestCreate, AuditBase):
    id: str
    employee_name: Optional[str] = Field(None, alias="employeeName")
    approved_by: Optional[str] = Field(None, alias="approvedBy")
    approved_at: Optional[str] = Field(None, alias="approvedAt")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    approver_name: Optional[str] = Field(None, alias="approverName")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class LeaveApproval(BaseModel):
    status: str
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    model_config = ConfigDict(populate_by_name=True)

class LeaveBalanceCreate(BaseModel):
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: str = Field(..., alias="employeeId")
    year: int
    annual_total: float = Field(14.0, alias="annualTotal")
    annual_used: float = Field(0.0, alias="annualUsed")
    annual_carry_forward: float = Field(0.0, alias="annualCarryForward")
    sick_total: float = Field(10.0, alias="sickTotal")
    sick_used: float = Field(0.0, alias="sickUsed")
    casual_total: float = Field(10.0, alias="casualTotal")
    casual_used: float = Field(0.0, alias="casualUsed")
    unpaid_used: float = Field(0.0, alias="unpaidUsed")
    model_config = ConfigDict(populate_by_name=True)

class LeaveBalance(LeaveBalanceCreate, AuditBase):
    id: int
    name: Optional[str] = None
    total: Optional[float] = None
    used: Optional[float] = None
    annual: Optional[str] = None
    annual_available: Optional[float] = Field(None, alias="annualAvailable")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Overtime ---
class OvertimeRequestCreate(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    date: str
    hours: float
    multiplier: float = 1.5
    reason: Optional[str] = None
    organization_id: Optional[str] = Field(None, alias="organizationId")
    model_config = ConfigDict(populate_by_name=True)

class OvertimeRequest(OvertimeRequestCreate, AuditBase):
    id: str
    status: str = "Pending"
    employee_name: Optional[str] = Field(None, alias="employeeName")
    employee_code: Optional[str] = Field(None, alias="employeeCode")
    approved_by: Optional[str] = Field(None, alias="approvedBy")
    approved_at: Optional[str] = Field(None, alias="approvedAt")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    approver_name: Optional[str] = Field(None, alias="approverName")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class OvertimeApproval(BaseModel):
    action: str
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    model_config = ConfigDict(populate_by_name=True)
