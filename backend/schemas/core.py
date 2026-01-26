
import json
from datetime import datetime
from typing import Optional, List, Union, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .shared import AuditBase

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    role: str
    name: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[str] = Field(None, alias="organizationId")
    employee_id: Optional[str] = Field(None, alias="employeeId")
    status: Optional[str] = "Active"
    is_system_user: Optional[bool] = Field(None, alias="isSystemUser")

    model_config = ConfigDict(populate_by_name=True)

class UserCreate(UserBase):
    id: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    organization_id: str = Field(..., alias="organizationId")
    employeeId: Optional[str] = None
    status: Optional[str] = None
    profileStatus: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    is_system_user: Optional[bool] = Field(None, alias="isSystemUser")

    model_config = ConfigDict(populate_by_name=True)

class User(UserBase, AuditBase):
    id: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# --- System Settings Schemas ---
class SystemFlagsBase(BaseModel):
    ai_enabled: bool = True
    advanced_analytics_enabled: bool = True
    employee_self_service_enabled: bool = True
    maintenance_mode: bool = False
    read_only_mode: bool = False
    cache_enabled: bool = True
    cache_ttl: int = 3600
    db_optimization_enabled: bool = True
    debug_logging_enabled: bool = False
    log_retention_days: int = 30
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    webhooks_max_retries: int = 3
    
    # Security
    mfa_enforced: bool = False
    biometrics_required: bool = False
    ip_whitelisting: bool = False
    session_timeout: str = "30"
    password_complexity: str = "Standard"
    session_isolation: bool = False
    
    # Audit
    neural_bypass: bool = False
    api_caching: bool = False
    immutable_logs: bool = False
    
    custom_flags: Optional[dict] = None

class SystemFlagsCreate(SystemFlagsBase):
    pass

class SystemFlagsUpdate(BaseModel):
    ai_enabled: Optional[bool] = None
    advanced_analytics_enabled: Optional[bool] = None
    employee_self_service_enabled: Optional[bool] = None
    maintenance_mode: Optional[bool] = None
    read_only_mode: Optional[bool] = None
    cache_enabled: Optional[bool] = None
    cache_ttl: Optional[int] = None
    db_optimization_enabled: Optional[bool] = None
    debug_logging_enabled: Optional[bool] = None
    log_retention_days: Optional[int] = None
    rate_limit_enabled: Optional[bool] = None
    rate_limit_requests_per_minute: Optional[int] = None
    webhooks_max_retries: Optional[int] = None
    
    mfa_enforced: Optional[bool] = None
    biometrics_required: Optional[bool] = None
    ip_whitelisting: Optional[bool] = None
    session_timeout: Optional[str] = None
    password_complexity: Optional[str] = None
    session_isolation: Optional[bool] = None
    
    neural_bypass: Optional[bool] = None
    api_caching: Optional[bool] = None
    immutable_logs: Optional[bool] = None
    
    custom_flags: Optional[dict] = None

class SystemFlags(SystemFlagsBase, AuditBase):
    id: str
    organization_id: str
    db_optimization_last_run: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ===== AI Configuration =====
class AIConfigurationBase(BaseModel):
    provider: str = "gemini"
    status: str = "offline"
    api_keys: Optional[dict] = Field(default_factory=dict, alias="apiKeys")
    agents: Optional[dict] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

class AIConfigurationCreate(AIConfigurationBase):
    pass

class AIConfigurationUpdate(BaseModel):
    provider: Optional[str] = None
    status: Optional[str] = None
    api_keys: Optional[dict] = Field(None, alias="apiKeys")
    agents: Optional[dict] = None

    model_config = ConfigDict(populate_by_name=True)

class AIConfigurationResponse(AIConfigurationBase, AuditBase):
    id: str
    organization_id: str

    model_config = ConfigDict(from_attributes=True)

# ===== Notification Settings =====
class NotificationSettingsBase(BaseModel):
    email_enabled: bool = True
    email_provider: str = "smtp"
    email_from_address: str = ""
    email_from_name: str = ""
    email_on_employee_created: bool = True
    email_on_leave_request: bool = True
    email_on_payroll_processed: bool = True
    email_on_system_alert: bool = True

    sms_enabled: bool = False
    sms_provider: Optional[str] = None
    sms_from_number: Optional[str] = None
    sms_on_leave_approval: bool = False
    sms_on_payroll_processed: bool = False
    sms_on_system_alert: bool = False

    slack_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None
    slack_on_critical_alerts: bool = True

    digest_enabled: bool = True
    digest_frequency: str = "daily"
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

    dnd_enabled: bool = False
    dnd_start_date: Optional[datetime] = None
    dnd_end_date: Optional[datetime] = None
    custom_settings: Optional[dict] = None

class NotificationSettingsCreate(NotificationSettingsBase):
    pass

class NotificationSettingsUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    email_provider: Optional[str] = None
    email_from_address: Optional[str] = None
    email_from_name: Optional[str] = None
    email_on_employee_created: Optional[bool] = None
    email_on_leave_request: Optional[bool] = None
    email_on_payroll_processed: Optional[bool] = None
    email_on_system_alert: Optional[bool] = None

    sms_enabled: Optional[bool] = None
    sms_provider: Optional[str] = None
    sms_from_number: Optional[str] = None
    sms_on_leave_approval: Optional[bool] = None
    sms_on_payroll_processed: Optional[bool] = None
    sms_on_system_alert: Optional[bool] = None

    slack_enabled: Optional[bool] = None
    slack_webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None
    slack_on_critical_alerts: Optional[bool] = None

    digest_enabled: Optional[bool] = None
    digest_frequency: Optional[str] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

    dnd_enabled: Optional[bool] = None
    dnd_start_date: Optional[datetime] = None
    dnd_end_date: Optional[datetime] = None
    custom_settings: Optional[dict] = None

class NotificationSettings(NotificationSettingsBase, AuditBase):
    id: str

    model_config = ConfigDict(from_attributes=True)

class NotificationSettingsResponse(NotificationSettingsBase, AuditBase):
    id: str
    organization_id: str

    model_config = ConfigDict(from_attributes=True)

# ===== Webhook Schemas =====
class WebhookBase(BaseModel):
    name: str
    url: str
    event_types: list[str]
    headers: Optional[dict] = None
    max_retries: int = 3

class WebhookCreate(WebhookBase):
    pass

class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    event_types: Optional[list[str]] = None
    headers: Optional[dict] = None
    is_active: Optional[bool] = None
    max_retries: Optional[int] = None

class WebhookResponse(WebhookBase, AuditBase):
    id: str
    organization_id: str
    is_active: bool = True

class WebhookLogResponse(BaseModel):
    id: str
    webhook_id: str
    event_type: str
    delivery_status: str
    response_status: Optional[int] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WebhookLogList(BaseModel):
    logs: list[WebhookLogResponse]
    total: int

# ===== Background Jobs =====
class BackgroundJobBase(BaseModel):
    job_type: str
    priority: int = 0
    payload: Optional[dict] = None

class BackgroundJobCreate(BackgroundJobBase):
    pass

class BackgroundJobResponse(BaseModel):
    id: str
    organization_id: str
    job_type: str
    status: str
    priority: int
    payload: Optional[dict] = None
    result: Optional[dict] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int
    max_retries: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BackgroundJobList(BaseModel):
    jobs: list[BackgroundJobResponse]
    total: int

# ===== Admin/Compliance =====
class ComplianceSettingsBase(BaseModel):
    tax_year_end: Optional[str] = Field(None, alias="taxYear")
    min_wage: float = Field(0.0, alias="minWage")
    eobi_rate: float = Field(0.0, alias="eobiRate")
    social_security_rate: float = Field(0.0, alias="socialSecurityRate")
    organization_id: str = Field(..., alias="organizationId")

    model_config = ConfigDict(populate_by_name=True)

class ComplianceSettingsCreate(ComplianceSettingsBase):
    pass

class ComplianceSettings(ComplianceSettingsBase, AuditBase):
    id: str
    failure_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class PayrollSettingsBase(BaseModel):
    currency: str = "PKR"
    tax_year_start: str = Field("July", alias="taxYearStart")
    allow_negative_salary: bool = Field(False, alias="allowNegativeSalary")
    pay_frequency: str = Field("Monthly", alias="payFrequency")
    pay_day: int = Field(1, alias="payDay")
    tax_calculation_method: str = Field("Annualized", alias="taxCalculationMethod")
    eobi_enabled: bool = Field(True, alias="eobiEnabled")
    social_security_enabled: bool = Field(True, alias="socialSecurityEnabled")
    overtime_enabled: bool = Field(True, alias="overtimeEnabled")
    overtime_rate: float = Field(1.5, alias="overtimeRate")

    calculation_method: str = Field("Per Month", alias="calculationMethod")
    custom_formulas: dict = Field({}, alias="customFormulas")
    overtime_rules: dict = Field({}, alias="overtime")

    organization_id: str = Field(..., alias="organizationId")
    
    @field_validator("custom_formulas", mode="before")
    def parse_formulas(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return {}
        return v

    model_config = ConfigDict(populate_by_name=True)

class PayrollSettingsCreate(PayrollSettingsBase):
    id: Optional[str] = None

class PayrollSettings(PayrollSettingsBase, AuditBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
