
import json
from datetime import datetime
from typing import Optional, List, Union, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from .shared import AuditBase
from .core import User
# from .org import Education, Experience, Family, Discipline, Increment # REMOVED: Defined locally
# Actually, the internal classes for Employee were in the original file. 
# I will define them here as nested classes if possible or just normal classes.
# Note: They were separate classes in the original file.

# --- Secondary Employee Tab Schemas ---
class EducationCreate(BaseModel):
    degree: str
    institute: str
    year: str
    grade_gpa: str = Field(..., alias="gradeGpa")
    marks_obtained: float = Field(..., alias="marksObtained")
    total_marks: float = Field(..., alias="totalMarks")
    class Config:
        populate_by_name = True

class Education(EducationCreate, AuditBase):
    id: int
    class Config:
        from_attributes = True

class ExperienceCreate(BaseModel):
    org_name: str = Field(..., alias="orgName")
    designation: str
    from_: str = Field(..., alias="from")
    to: str
    gross_salary: float = Field(..., alias="grossSalary")
    remarks: str
    class Config:
        populate_by_name = True

class Experience(ExperienceCreate, AuditBase):
    id: int
    class Config:
        from_attributes = True

class FamilyCreate(BaseModel):
    name: str
    relationship: str
    dob: str

class Family(FamilyCreate, AuditBase):
    id: int
    class Config:
        from_attributes = True

class DisciplineCreate(BaseModel):
    date: str
    description: str
    outcome: str

class Discipline(DisciplineCreate, AuditBase):
    id: int
    class Config:
        from_attributes = True

class IncrementCreate(BaseModel):
    effective_date: str = Field(..., alias="effectiveDate")
    new_gross: float = Field(..., alias="newGross")
    type: str
    remarks: str
    new_house_rent: float | None = Field(0, alias="newHouseRent")
    new_utility_allowance: float | None = Field(0, alias="newUtilityAllowance")
    new_other_allowance: float | None = Field(0, alias="newOtherAllowance")
    class Config:
        populate_by_name = True

class Increment(IncrementCreate, AuditBase):
    id: int
    class Config:
        from_attributes = True

# --- Employee ---
class EmployeeBase(BaseModel):
    name: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    role: Optional[str] = None
    department: Optional[str] = None
    status: str = "Active"
    join_date: Optional[str] = Field(None, alias="joiningDate")
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth")
    hire_date: Optional[str] = Field(None, alias="hireDate")
    employment_type: Optional[str] = Field(None, alias="employmentType")
    employee_code: Optional[str] = Field(None, alias="employeeCode")
    email: Optional[str] = None
    phone: Optional[str] = None
    organization_id: Optional[str] = Field(None, alias="organizationId")

    # Personal Details
    father_name: Optional[str] = Field(None, alias="fatherName")
    gender: Optional[str] = None
    cnic: Optional[str] = None
    cnic_expiry: Optional[str] = Field(None, alias="cnicExpiryDate")
    religion: Optional[str] = None
    marital_status: Optional[str] = Field(None, alias="maritalStatus")
    blood_group: Optional[str] = Field(None, alias="bloodGroup")
    nationality: Optional[str] = None
    
    # Contact
    personal_email: Optional[str] = Field(None, alias="personalEmail")
    personal_phone: Optional[str] = Field(None, alias="personalCellNumber")
    present_address: Optional[str] = Field(None, alias="presentAddress")
    permanent_address: Optional[str] = Field(None, alias="permanentAddress")
    present_district: Optional[str] = Field(None, alias="presentDistrict")
    permanent_district: Optional[str] = Field(None, alias="permanentDistrict")

    # Financial & Benefits
    gross_salary: Optional[float] = Field(0.0, alias="grossSalary")
    payment_mode: Optional[str] = Field(None, alias="paymentMode")
    bank_account: Optional[str] = Field(None, alias="bankAccount")
    bank_name: Optional[str] = Field(None, alias="bankName")
    eobi_number: Optional[str] = Field(None, alias="eobiNumber")
    social_security_number: Optional[str] = Field(None, alias="socialSecurityNumber")

    # Extended
    probation_period: Optional[str] = Field(None, alias="probationPeriod")
    confirmation_date: Optional[str] = Field(None, alias="confirmationDate")
    leaving_date: Optional[str] = Field(None, alias="leavingDate")
    leaving_type: Optional[str] = Field(None, alias="leavingType")
    
    eobi_status: bool = Field(False, alias="eobiStatus")
    social_security_status: bool = Field(False, alias="socialSecurityStatus")
    medical_status: bool = Field(False, alias="medicalStatus")
    
    cnic_issue_date: Optional[str] = Field(None, alias="cnicIssueDate")
    line_manager_id: Optional[str] = Field(None, alias="lineManagerId")
    sub_department_id: Optional[str] = Field(None, alias="subDepartmentId")

    @field_validator("cnic")
    @classmethod
    def validate_cnic(cls, v):
        if not v:
            return v
        import re
        pattern = r"^(\d{5}-\d{7}-\d{1}|\d{13})$"
        if not re.match(pattern, v):
            # raise ValueError("CNIC must be 13 digits") # Suppressed for migration
            pass
        return v

    @field_validator("phone", "personal_phone")
    @classmethod
    def validate_phone(cls, v):
        return v # Simplified for now

    class Config:
        populate_by_name = True
        by_alias = True

class EmployeeCreate(EmployeeBase):
    id: Optional[str] = None
    department_id: str | None = None
    designation_id: str | None = None
    grade_id: str | None = None
    plant_id: str | None = None
    shift_id: str | None = None

    education: list["EducationCreate"] = []
    experience: list["ExperienceCreate"] = []
    family: list["FamilyCreate"] = []
    discipline: list["DisciplineCreate"] = []
    increments: list["IncrementCreate"] = []

    @model_validator(mode="before")
    @classmethod
    def populate_missing_fields(cls, data):
        if isinstance(data, dict):
            first = data.get("firstName") or data.get("first_name")
            last = data.get("lastName") or data.get("last_name")
            if not data.get("name") and (first or last):
                data["name"] = (f"{first or ''} {last or ''}".strip() or "Unknown")
            
            hire = data.get("hireDate") or data.get("hire_date")
            if not data.get("join_date") and hire:
                data["join_date"] = hire
        return data

class Employee(EmployeeBase, AuditBase):
    id: str
    department_id: str | None = None
    designation_id: str | None = None
    grade_id: str | None = None
    plant_id: str | None = None
    shift_id: str | None = None
    
    # Computed
    grade: str | None = None
    employmentLevel: str | None = None
    designation: str | None = None
    hrPlant: str | None = None
    shift: str | None = None

    education: list["Education"] = []
    experience: list["Experience"] = []
    family: list["Family"] = []
    discipline: list["Discipline"] = []
    increments: list["Increment"] = []

    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True


# --- Recruitment ---
class CandidateBase(BaseModel):
    name: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    email: str
    phone: Optional[str] = None
    position_applied: str = Field(..., alias="positionApplied")
    current_stage: str = Field("Applied", alias="currentStage")
    score: int = 0
    resume_url: Optional[str] = Field(None, alias="resumeUrl")
    skills: Union[list[str], str] = []
    applied_date: str = Field(..., alias="appliedDate")
    avatar: Optional[str] = None
    organization_id: Optional[str] = Field(None, alias="organizationId")

    class Config:
        populate_by_name = True

class CandidateCreate(CandidateBase):
    id: str

class Candidate(CandidateBase, AuditBase):
    id: str
    @field_validator("skills", mode="before")
    def parse_skills(cls, v):
        if isinstance(v, str):
            return v.split(",") if v else []
        return v
    class Config:
        from_attributes = True

class JobVacancyBase(BaseModel):
    title: str
    department: str
    location: str
    type: str
    posted_date: str = Field(..., alias="postedDate")
    status: str
    applicants_count: int = Field(0, alias="applicants")
    description: str = ""
    requirements: list[str] = []
    salary_range: str = Field("", alias="salaryRange")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class JobVacancyCreate(JobVacancyBase):
    id: str

class JobVacancy(JobVacancyBase, AuditBase):
    id: str
    class Config:
        from_attributes = True


# --- Onboarding/Offboarding ---
class OnboardingStepBase(BaseModel):
    label: str
    done: bool = False

class OnboardingStepCreate(OnboardingStepBase):
    id: Optional[str] = None

class OnboardingStep(OnboardingStepBase, AuditBase):
    id: str
    hire_id: str
    class Config:
        from_attributes = True

class OnboardingHireBase(BaseModel):
    name: str
    role: str
    mentor: str
    start_date: str = Field(..., alias="startDate")
    progress: int = 0
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class OnboardingHireCreate(OnboardingHireBase):
    id: Optional[str] = None
    steps: List[OnboardingStepCreate] = []

class OnboardingHire(OnboardingHireBase, AuditBase):
    id: str
    steps: List[OnboardingStep] = []
    class Config:
        from_attributes = True

class OffboardingStepBase(BaseModel):
    label: str
    done: bool = False

class OffboardingStepCreate(OffboardingStepBase):
    id: Optional[str] = None

class OffboardingStep(OffboardingStepBase, AuditBase):
    id: str
    exit_id: str
    class Config:
        from_attributes = True

class OffboardingExitBase(BaseModel):
    name: str
    role: str
    type: str
    last_date: str = Field(..., alias="lDate")
    status: str = "Initiated"
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class OffboardingExitCreate(OffboardingExitBase):
    id: Optional[str] = None
    checklist: List[OffboardingStepCreate] = []

class OffboardingExit(OffboardingExitBase, AuditBase):
    id: str
    checklist: List[OffboardingStep] = []
    class Config:
        from_attributes = True


# --- Performance ---
class GoalBase(BaseModel):
    title: str
    category: str
    progress: int = 0
    metric: str
    status: str = "Initiated"
    due_date: str = Field(..., alias="dueDate")
    weight: int
    description: str
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: Optional[str] = Field(None, alias="employeeId")
    class Config:
        populate_by_name = True

class GoalCreate(GoalBase):
    id: Optional[str] = None

class Goal(GoalBase, AuditBase):
    id: str
    class Config:
        from_attributes = True

class PerformanceReviewBase(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    review_period: str = Field(..., alias="reviewPeriod")
    status: str
    score: int
    feedback: str
    reviewer_id: str = Field(..., alias="reviewerId")
    review_date: str = Field(..., alias="reviewDate")
    organization_id: str = Field(..., alias="organizationId")
    class Config:
        populate_by_name = True

class PerformanceReviewCreate(PerformanceReviewBase):
    id: str

class PerformanceReview(PerformanceReviewBase, AuditBase):
    id: str
    class Config:
        from_attributes = True


# --- Learning ---
class CourseBase(BaseModel):
    title: str
    provider: Optional[str] = None
    duration: Optional[str] = None
    level: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    progress: int = 0
    status: str = "Not Started"
    score: Optional[int] = None
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: Optional[str] = Field(None, alias="employeeId")
    class Config:
        populate_by_name = True

class CourseCreate(CourseBase):
    pass

class Course(CourseBase, AuditBase):
    id: int
    class Config:
        from_attributes = True


# --- Benefits, Expenses, Rewards ---
class BenefitTierBase(BaseModel):
    name: str
    color: Optional[str] = None
    price: Optional[str] = None
    items: List[str] = []
    icon: Optional[str] = None
    popular: bool = False
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class BenefitTierCreate(BenefitTierBase):
    pass

class BenefitTier(BenefitTierBase):
    id: int
    class Config:
        from_attributes = True

class BenefitEnrollmentBase(BaseModel):
    name: str
    tier: str
    date: str
    status: str = "Pending"
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: Optional[str] = Field(None, alias="employeeId")
    class Config:
        populate_by_name = True

class BenefitEnrollmentCreate(BenefitEnrollmentBase):
    pass

class BenefitEnrollment(BenefitEnrollmentBase):
    id: int
    class Config:
        from_attributes = True

class ExpenseBase(BaseModel):
    employee_name: str = Field(..., alias="employeeName")
    category: str
    amount: float
    currency: str = "USD"
    date: str
    status: str = "Pending"
    receipt_url: Optional[str] = Field(None, alias="receiptUrl")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: Optional[str] = Field(None, alias="employeeId")
    class Config:
        populate_by_name = True

class ExpenseCreate(ExpenseBase):
    id: Optional[str] = None

class Expense(ExpenseBase, AuditBase):
    id: str
    class Config:
        from_attributes = True
        populate_by_name = True

class RewardBase(BaseModel):
    title: str
    description: Optional[str] = None
    points_required: int = Field(0, alias="pointsRequired")
    category: Optional[str] = None
    image_url: Optional[str] = Field(None, alias="imageUrl")
    is_active: bool = Field(True, alias="isActive")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class RewardCreate(RewardBase):
    pass

class Reward(RewardBase, AuditBase):
    id: int
    class Config:
        from_attributes = True

class RecognitionBase(BaseModel):
    sender_id: str = Field(..., alias="senderId")
    receiver_id: str = Field(..., alias="receiverId")
    message: str
    category: Optional[str] = None
    points_awarded: int = Field(0, alias="pointsAwarded")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class RecognitionCreate(RecognitionBase):
    pass

class Recognition(RecognitionBase, AuditBase):
    id: int
    class Config:
        from_attributes = True

class RewardPointBase(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    balance: int = 0
    total_earned: int = Field(0, alias="totalEarned")
    total_redeemed: int = Field(0, alias="totalRedeemed")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class RewardPointCreate(RewardPointBase):
    pass

class RewardPoint(RewardPointBase, AuditBase):
    id: int
    class Config:
        from_attributes = True

class RewardPointTransactionBase(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    points: int
    type: str 
    description: Optional[str] = None
    reference_id: Optional[str] = Field(None, alias="referenceId")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class RewardPointTransactionCreate(RewardPointTransactionBase):
    pass

class RewardPointTransaction(RewardPointTransactionBase, AuditBase):
    id: int
    class Config:
        from_attributes = True


# --- Promotion ---
class PromotionCycleBase(BaseModel):
    title: str
    status: str = "Open"
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class PromotionCycleCreate(PromotionCycleBase):
    pass

class PromotionCycle(PromotionCycleBase, AuditBase):
    id: int
    class Config:
        from_attributes = True

class PromotionApprovalBase(BaseModel):
    level: str 
    status: str 
    remarks: Optional[str] = None
    class Config:
        populate_by_name = True

class PromotionApprovalCreate(PromotionApprovalBase):
    request_id: int = Field(..., alias="requestId")

class PromotionApproval(PromotionApprovalBase, AuditBase):
    id: int
    request_id: int = Field(..., alias="requestId")
    approver_id: str = Field(..., alias="approverId")
    class Config:
        from_attributes = True

class PromotionRequestBase(BaseModel):
    cycle_id: Optional[int] = Field(None, alias="cycleId")
    employee_id: str = Field(..., alias="employeeId")
    type: str
    current_salary: float = Field(0.0, alias="currentSalary")
    proposed_salary: float = Field(0.0, alias="proposedSalary")
    current_designation_id: Optional[str] = Field(None, alias="currentDesignationId")
    proposed_designation_id: Optional[str] = Field(None, alias="proposedDesignationId")
    current_grade_id: Optional[str] = Field(None, alias="currentGradeId")
    proposed_grade_id: Optional[str] = Field(None, alias="proposedGradeId")
    reason: Optional[str] = None
    performance_rating: Optional[str] = Field(None, alias="performanceRating")
    manager_remarks: Optional[str] = Field(None, alias="managerRemarks")
    status: str = "Pending"
    effective_date: str = Field(..., alias="effectiveDate")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    class Config:
        populate_by_name = True

class PromotionRequestCreate(PromotionRequestBase):
    pass

class PromotionRequest(PromotionRequestBase, AuditBase):
    id: int
    approvals: List[PromotionApproval] = []
    class Config:
        from_attributes = True


# --- Self Service ---
class ProfileUpdate(BaseModel):
    profile_photo_url: Optional[str] = Field(None, alias="profilePhotoUrl")
    bio: Optional[str] = None
    class Config:
        populate_by_name = True

class EmergencyContactUpdate(BaseModel):
    emergency_contact_name: Optional[str] = Field(None, alias="emergencyContactName")
    emergency_contact_phone: Optional[str] = Field(None, alias="emergencyContactPhone")
    emergency_contact_relation: Optional[str] = Field(None, alias="emergencyContactRelation")
    class Config:
        populate_by_name = True

class DocumentRequestCreate(BaseModel):
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: str = Field(..., alias="employeeId")
    document_type: str = Field(..., alias="documentType")
    purpose: Optional[str] = None
    additional_notes: Optional[str] = Field(None, alias="additionalNotes")
    class Config:
        populate_by_name = True

class DocumentRequest(DocumentRequestCreate, AuditBase):
    id: str
    status: str
    requested_date: str = Field(..., alias="requestedDate")
    approved_by: Optional[str] = Field(None, alias="approvedBy")
    approved_date: Optional[str] = Field(None, alias="approvedDate")
    fulfilled_date: Optional[str] = Field(None, alias="fulfilledDate")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    document_url: Optional[str] = Field(None, alias="documentUrl")
    employee_name: Optional[str] = Field(None, alias="employeeName")
    approver_name: Optional[str] = Field(None, alias="approverName")
    class Config:
        from_attributes = True
        populate_by_name = True

class DocumentRequestApproval(BaseModel):
    status: str
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    document_url: Optional[str] = Field(None, alias="documentUrl")
    class Config:
        populate_by_name = True

class EmployeeDocumentCreate(BaseModel):
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: str = Field(..., alias="employeeId")
    document_type: str = Field(..., alias="documentType")
    document_name: str = Field(..., alias="documentName")
    document_url: str = Field(..., alias="documentUrl")
    file_size: Optional[int] = Field(None, alias="fileSize")
    mime_type: Optional[str] = Field(None, alias="mimeType")
    description: Optional[str] = None
    expiry_date: Optional[str] = Field(None, alias="expiryDate")
    is_private: bool = Field(True, alias="isPrivate")
    class Config:
        populate_by_name = True

class EmployeeDocument(EmployeeDocumentCreate, AuditBase):
    id: str
    upload_date: str = Field(..., alias="uploadDate")
    uploaded_by: str = Field(..., alias="uploadedBy")
    uploader_name: Optional[str] = Field(None, alias="uploaderName")
    class Config:
        from_attributes = True
        populate_by_name = True

class InfoUpdateRequestCreate(BaseModel):
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: str = Field(..., alias="employeeId")
    field_name: str = Field(..., alias="fieldName")
    current_value: Optional[str] = Field(None, alias="currentValue")
    new_value: str = Field(..., alias="newValue")
    reason: Optional[str] = None
    class Config:
        populate_by_name = True

class InfoUpdateRequest(InfoUpdateRequestCreate, AuditBase):
    id: str
    status: str
    requested_date: str = Field(..., alias="requestedDate")
    approved_by: Optional[str] = Field(None, alias="approvedBy")
    approved_date: Optional[str] = Field(None, alias="approvedDate")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    employee_name: Optional[str] = Field(None, alias="employeeName")
    class Config:
        from_attributes = True
        populate_by_name = True

class TeamMember(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    profile_photo_url: Optional[str] = Field(None, alias="profilePhotoUrl")
    bio: Optional[str] = None
    join_date: Optional[str] = Field(None, alias="joinDate")
    class Config:
        from_attributes = True
        populate_by_name = True

class MyProfile(BaseModel):
    id: str
    employee_code: Optional[str] = Field(None, alias="employeeCode")
    name: str
    email: str
    phone: Optional[str] = None
    personal_email: Optional[str] = Field(None, alias="personalEmail")
    personal_phone: Optional[str] = Field(None, alias="personalPhone")
    department: Optional[str] = None
    designation: Optional[str] = None
    join_date: Optional[str] = Field(None, alias="joinDate")
    status: Optional[str] = None
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth")
    gender: Optional[str] = None
    marital_status: Optional[str] = Field(None, alias="maritalStatus")
    blood_group: Optional[str] = Field(None, alias="bloodGroup")
    present_address: Optional[str] = Field(None, alias="presentAddress")
    permanent_address: Optional[str] = Field(None, alias="permanentAddress")
    emergency_contact_name: Optional[str] = Field(None, alias="emergencyContactName")
    emergency_contact_phone: Optional[str] = Field(None, alias="emergencyContactPhone")
    emergency_contact_relation: Optional[str] = Field(None, alias="emergencyContactRelation")
    profile_photo_url: Optional[str] = Field(None, alias="profilePhotoUrl")
    bio: Optional[str] = None
    gross_salary: Optional[float] = Field(None, alias="grossSalary")
    bank_name: Optional[str] = Field(None, alias="bankName")
    class Config:
        from_attributes = True
        populate_by_name = True

class AnalyticsDataPoint(BaseModel):
    name: str
    value: float

class TrendDataPoint(BaseModel):
    name: str
    count: int
    liability: float

class EngagementDataPoint(BaseModel):
    name: str
    engagement: int
    productivity: int
    sentiment: int

class DashboardSummary(BaseModel):
    workforce_velocity: str = Field(..., alias="workforce_velocity")
    retention_vector: str = Field(..., alias="retention_vector")
    neural_alignment: str = Field(..., alias="neural_alignment")
    asset_equity: str = Field(..., alias="asset_equity")
    total_active_employees: int
    total_candidates: int
    department_distribution: List[AnalyticsDataPoint]
    gender_distribution: List[AnalyticsDataPoint]
    class Config:
        populate_by_name = True
