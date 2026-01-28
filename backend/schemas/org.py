
import json
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict, computed_field
from .shared import AuditBase

# --- Plant ---
class PlantDivisionBase(BaseModel):
    name: str
    code: str
    is_active: bool = Field(True, alias="isActive")
    model_config = ConfigDict(populate_by_name=True)

class PlantDivisionCreate(PlantDivisionBase):
    id: Optional[str] = None
    plant_id: Optional[str] = Field(None, alias="plantId")

class PlantDivision(PlantDivisionBase, AuditBase):
    id: str
    plant_id: Optional[str] = Field(None, alias="plantId")

    model_config = ConfigDict(from_attributes=True)

class PlantBase(BaseModel):
    name: str
    location: Optional[str] = None
    code: str
    head_of_plant: Optional[str] = Field(None, alias="headOfPlant")
    contact_number: Optional[str] = Field(None, alias="contactNumber")
    is_active: bool = Field(True, alias="isActive")
    current_sequence: int = Field(0, alias="currentSequence")

    model_config = ConfigDict(populate_by_name=True)

class PlantCreate(PlantBase):
    id: Optional[str] = None
    organization_id: Optional[str] = Field(None, alias="organizationId")
    divisions: list[PlantDivisionCreate] = []

class Plant(PlantBase, AuditBase):
    id: str
    organization_id: Optional[str] = Field(None, alias="organizationId")
    divisions: list[PlantDivision] = Field(default=[])
    plant_id: Optional[str] = Field(None, alias="plantId")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Organization ---
class OrganizationBase(BaseModel):
    id: Optional[str] = None
    code: Optional[str] = "PEOPLE01"
    name: str = "My Organization"
    is_active: bool = Field(True, alias="isActive")
    head_id: Optional[str] = Field(None, alias="headId")

    @computed_field
    @property
    def status(self) -> str:
        return "Active" if self.is_active else "Inactive"

    industry: Optional[str] = None
    currency: Optional[str] = "PKR"
    tax_year_end: Optional[str] = Field(None, alias="taxYearEnd")

    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = Field(None, alias="addressLine1")
    address_line2: Optional[str] = Field(None, alias="addressLine2")
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = Field(None, alias="zipCode")
    country: Optional[str] = None

    tax_identifier: Optional[str] = Field(None, alias="taxId")
    registration_number: Optional[str] = Field(None, alias="registrationNumber")
    founded_date: Optional[str] = Field(None, alias="foundedDate")
    logo: Optional[str] = None
    cover_url: Optional[str] = Field(None, alias="coverUrl")
    description: Optional[str] = None
    social_links: Optional[Any] = Field(None, alias="socialLinks")
    
    enabled_modules: Optional[Any] = Field(None, alias="enabledModules")
    system_authority: Optional[str] = Field(None, alias="systemAuthority")
    approval_workflows: Optional[Any] = Field(None, alias="approvalWorkflows")

    @field_validator("code")
    @classmethod
    def validate_org_code(cls, v):
        if v:
            import re
            pattern = r"^[A-Z]{3,7}[0-9]{2}$"
            if not re.match(pattern, v):
                # We can choose to be strict or lenient. Let's be lenient for migration.
                pass
        return v

    model_config = ConfigDict(populate_by_name=True)

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationWithAdminCreate(OrganizationCreate):
    admin_username: str = Field(..., alias="adminUsername")
    admin_password: str = Field(..., alias="adminPassword")
    admin_name: Optional[str] = Field(None, alias="adminName")
    admin_email: Optional[str] = Field(None, alias="adminEmail")

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    head_id: Optional[str] = None
    industry: Optional[str] = None
    currency: Optional[str] = None
    tax_year_end: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    tax_identifier: Optional[str] = None
    registration_number: Optional[str] = None
    founded_date: Optional[str] = None
    logo: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    social_links: Optional[Any] = None
    enabled_modules: Optional[Any] = None
    system_authority: Optional[str] = None
    approval_workflows: Optional[Any] = None

    model_config = ConfigDict(populate_by_name=True)

class Organization(OrganizationBase, AuditBase):
    id: str
    plants: list[Plant] = []

    @field_validator("social_links", mode="before")
    def parse_social_links(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return v
        return v

    model_config = ConfigDict(from_attributes=True)

class OrganizationList(OrganizationBase, AuditBase):
    id: str
    
    @field_validator("social_links", mode="before")
    def parse_social_links(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return v
        return v

    model_config = ConfigDict(from_attributes=True)


# --- Org Elements ---
class DepartmentCreate(BaseModel):
    id: Optional[str] = None
    code: str
    name: str
    is_active: bool = Field(True, alias="isActive")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    hod_id: Optional[str] = Field(None, alias="hodId")

    model_config = ConfigDict(populate_by_name=True)

class Department(DepartmentCreate, AuditBase):
    pass
    model_config = ConfigDict(from_attributes=True)

class SubDepartmentCreate(BaseModel):
    id: Optional[str] = None
    code: Optional[str] = None
    name: str
    parent_department_id: str = Field(..., alias="parentDepartmentId")
    is_active: bool = Field(True, alias="isActive")
    organization_id: Optional[str] = Field(None, alias="organizationId")

    model_config = ConfigDict(populate_by_name=True)

class SubDepartment(SubDepartmentCreate, AuditBase):
    pass
    model_config = ConfigDict(from_attributes=True)

class GradeCreate(BaseModel):
    id: Optional[str] = None
    name: str
    level: int = 0
    is_active: bool = Field(True, alias="isActive")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    job_level_id: Optional[str] = Field(None, alias="jobLevelId")

    model_config = ConfigDict(populate_by_name=True)

class Grade(AuditBase):
    id: str
    name: str
    level: int
    is_active: bool = True
    organization_id: Optional[str] = None
    jobLevelId: str = Field(..., validation_alias="job_level_id")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class DesignationCreate(BaseModel):
    id: Optional[str] = None
    name: str
    grade_id: str = Field(..., alias="gradeId")
    department_id: Optional[str] = Field(None, alias="departmentId")
    is_active: bool = Field(True, alias="isActive")
    organization_id: Optional[str] = Field(None, alias="organizationId")

    model_config = ConfigDict(populate_by_name=True)

class Designation(DesignationCreate, AuditBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class ShiftCreate(BaseModel):
    id: Optional[str] = None
    name: str
    code: str
    type: Optional[str] = None
    start_time: Optional[str] = Field(None, alias="startTime")
    end_time: Optional[str] = Field(None, alias="endTime")
    grace_period: Optional[int] = Field(0, alias="gracePeriod")
    break_duration: Optional[int] = Field(0, alias="breakDuration")
    work_days: Optional[list[str]] = Field([], alias="workDays")
    is_active: bool = Field(True, alias="isActive")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    color: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

class Shift(AuditBase):
    id: str
    name: str
    code: Optional[str] = None
    type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    grace_period: Optional[int] = 0
    break_duration: Optional[int] = 0
    work_days: Optional[str] = None
    is_active: bool = True
    organization_id: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class EmploymentLevelCreate(BaseModel):
    id: Optional[str] = None
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = Field(True, alias="isActive")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    model_config = ConfigDict(populate_by_name=True)

class EmploymentLevel(AuditBase):
    id: str
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    organization_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PositionCreate(BaseModel):
    id: Optional[str] = None
    title: str
    department_id: Optional[str] = Field(None, alias="departmentId")
    grade_id: Optional[str] = Field(None, alias="gradeId")
    reports_to: Optional[str] = Field(None, alias="reportsTo")
    description: Optional[str] = None
    is_active: bool = True
    organization_id: Optional[str] = Field(None, alias="organizationId")
    model_config = ConfigDict(populate_by_name=True)

class Position(AuditBase):
    id: str
    title: str
    department_id: Optional[str] = None
    grade_id: Optional[str] = None
    reports_to: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    organization_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class JobLevelCreate(BaseModel):
    id: Optional[str] = None
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = Field(True, alias="isActive")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    model_config = ConfigDict(populate_by_name=True)

class JobLevel(JobLevelCreate, AuditBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class HolidayCreate(BaseModel):
    id: Optional[str] = None
    name: str
    date: str
    type: Optional[str] = None
    is_recurring: bool = False
    description: Optional[str] = None
    organization_id: Optional[str] = Field(None, alias="organizationId")
    model_config = ConfigDict(populate_by_name=True)

class Holiday(AuditBase):
    id: str
    name: str
    date: str
    type: Optional[str] = None
    is_recurring: bool = False
    description: Optional[str] = None
    organization_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class BankCreate(BaseModel):
    id: Optional[str] = None
    bank_name: str = Field(..., alias="bankName")
    account_number: str = Field(..., alias="accountNumber")
    account_title: Optional[str] = Field(None, alias="accountTitle")
    branch: Optional[str] = None
    iban: Optional[str] = None
    swift_code: Optional[str] = Field(None, alias="swiftCode")
    currency: str = "PKR"
    is_active: bool = True
    organization_id: Optional[str] = Field(None, alias="organizationId")
    model_config = ConfigDict(populate_by_name=True)

class Bank(AuditBase):
    id: str
    bank_name: str
    account_number: str
    account_title: Optional[str] = None
    branch: Optional[str] = None
    iban: Optional[str] = None
    swift_code: Optional[str] = None
    currency: str = "PKR"
    is_active: bool = True
    organization_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
