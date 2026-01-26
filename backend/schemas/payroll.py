
import json
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .shared import AuditBase

# --- Salary Components ---
class SalaryComponentCreate(BaseModel):
    organization_id: str = Field(..., alias="organizationId")
    code: str
    name: str
    description: Optional[str] = None
    component_type: str = Field(..., alias="componentType") # earning, deduction
    calculation_type: str = Field("fixed", alias="calculationType")
    percentage_of: Optional[str] = Field(None, alias="percentageOf")
    default_amount: float = Field(0.0, alias="defaultAmount")
    is_taxable: bool = Field(True, alias="isTaxable")
    is_statutory: bool = Field(False, alias="isStatutory")
    is_active: bool = Field(True, alias="isActive")
    display_order: int = Field(0, alias="displayOrder")

    model_config = ConfigDict(populate_by_name=True)

class SalaryComponent(SalaryComponentCreate):
    id: str
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class EmployeeSalaryStructureCreate(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    component_id: str = Field(..., alias="componentId")
    amount: float = 0.0
    percentage: Optional[float] = None
    effective_from: str = Field(..., alias="effectiveFrom")
    effective_to: Optional[str] = Field(None, alias="effectiveTo")
    is_active: bool = Field(True, alias="isActive")

    model_config = ConfigDict(populate_by_name=True)

class EmployeeSalaryStructure(EmployeeSalaryStructureCreate):
    id: int
    component_name: Optional[str] = Field(None, alias="componentName")
    component_type: Optional[str] = Field(None, alias="componentType")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# --- Tax Schemas ---
class TaxSlabCreate(BaseModel):
    organization_id: str = Field(..., alias="organizationId")
    tax_year: str = Field(..., alias="taxYear")
    min_income: float = Field(..., alias="minIncome")
    max_income: Optional[float] = Field(None, alias="maxIncome")
    fixed_tax: float = Field(0.0, alias="fixedTax")
    tax_rate: float = Field(0.0, alias="taxRate")
    excess_over: float = Field(0.0, alias="excessOver")
    is_active: bool = Field(True, alias="isActive")

    model_config = ConfigDict(populate_by_name=True)

class TaxSlab(TaxSlabCreate):
    id: str
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class TaxDeductionTypeCreate(BaseModel):
    organization_id: str = Field(..., alias="organizationId")
    code: str
    name: str
    section: str
    description: Optional[str] = None
    deduction_type: str = Field(..., alias="deductionType")
    max_income_limit: Optional[float] = Field(None, alias="maxIncomeLimit")
    calc_percentage: Optional[float] = Field(None, alias="calcPercentage")
    calc_income_percentage: Optional[float] = Field(None, alias="calcIncomePercentage")
    calc_per_unit_limit: Optional[float] = Field(None, alias="calcPerUnitLimit")
    calc_max_limit: Optional[float] = Field(None, alias="calcMaxLimit")
    requires_document: bool = Field(True, alias="requiresDocument")
    requires_ntn: bool = Field(False, alias="requiresNtn")
    is_active: bool = Field(True, alias="isActive")

    model_config = ConfigDict(populate_by_name=True)

class TaxDeductionType(TaxDeductionTypeCreate):
    id: str
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class EmployeeTaxDeductionCreate(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    deduction_type_id: str = Field(..., alias="deductionTypeId")
    tax_year: str = Field(..., alias="taxYear")
    claimed_amount: float = Field(..., alias="claimedAmount")
    number_of_children: Optional[int] = Field(None, alias="numberOfChildren")
    institution_name: Optional[str] = Field(None, alias="institutionName")
    institution_ntn: Optional[str] = Field(None, alias="institutionNtn")

    model_config = ConfigDict(populate_by_name=True)

class EmployeeTaxDeduction(EmployeeTaxDeductionCreate):
    id: int
    approved_amount: Optional[float] = Field(None, alias="approvedAmount")
    status: str = "Pending"
    deduction_type_name: Optional[str] = Field(None, alias="deductionTypeName")
    deduction_section: Optional[str] = Field(None, alias="deductionSection")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class TaxCalculationDetail(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    tax_year: str = Field(..., alias="taxYear")
    annual_gross_income: float = Field(..., alias="annualGrossIncome")
    section_60d_tuition: float = Field(0.0, alias="section60dTuition")
    other_allowances: float = Field(0.0, alias="otherAllowances")
    total_deductible_allowances: float = Field(0.0, alias="totalDeductibleAllowances")
    taxable_income: float = Field(..., alias="taxableIncome")
    gross_tax: float = Field(..., alias="grossTax")
    charitable_donation_credit: float = Field(0.0, alias="charitableDonationCredit")
    insurance_credit: float = Field(0.0, alias="insuranceCredit")
    total_tax_credits: float = Field(0.0, alias="totalTaxCredits")
    annual_tax_payable: float = Field(..., alias="annualTaxPayable")
    monthly_tax: float = Field(..., alias="monthlyTax")

    model_config = ConfigDict(populate_by_name=True)


# --- Payroll Run & Ledger ---
class PayrollLedgerCreate(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    period_month: str = Field(..., alias="periodMonth")
    period_year: str = Field(..., alias="periodYear")
    basic_salary: float = Field(0.0, alias="basicSalary")
    gross_salary: float = Field(0.0, alias="grossSalary")
    net_salary: float = Field(0.0, alias="netSalary")
    additions: float = 0.0
    deductions: float = 0.0
    status: str = "Draft"
    payment_mode: Optional[str] = Field(None, alias="paymentMode")

    model_config = ConfigDict(populate_by_name=True)

class PayrollLedger(PayrollLedgerCreate, AuditBase):
    id: int
    employee_name: Optional[str] = Field(None, alias="employeeName")
    model_config = ConfigDict(from_attributes=True)

class PayrollRunCreate(BaseModel):
    organization_id: str = Field(..., alias="organizationId")
    period_month: str = Field(..., alias="periodMonth")
    period_year: str = Field(..., alias="periodYear")
    notes: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)

class PayrollRun(PayrollRunCreate):
    id: str
    status: str = "Draft"
    total_employees: int = Field(0, alias="totalEmployees")
    processed_employees: int = Field(0, alias="processedEmployees")
    total_gross: float = Field(0.0, alias="totalGross")
    total_deductions: float = Field(0.0, alias="totalDeductions")
    total_net: float = Field(0.0, alias="totalNet")
    processed_at: Optional[str] = Field(None, alias="processedAt")
    processed_by: Optional[str] = Field(None, alias="processedBy")
    approved_at: Optional[str] = Field(None, alias="approvedAt")
    approved_by: Optional[str] = Field(None, alias="approvedBy")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class PayslipDetail(BaseModel):
    id: int
    employee_id: str = Field(..., alias="employeeId")
    employee_name: Optional[str] = Field(None, alias="employeeName")
    employee_code: Optional[str] = Field(None, alias="employeeCode")
    period_month: str = Field(..., alias="periodMonth")
    period_year: str = Field(..., alias="periodYear")
    basic_salary: float = Field(0.0, alias="basicSalary")
    house_rent: float = Field(0.0, alias="houseRent")
    medical_allowance: float = Field(0.0, alias="medicalAllowance")
    transport_allowance: float = Field(0.0, alias="transportAllowance")
    other_allowances: float = Field(0.0, alias="otherAllowances")
    gross_salary: float = Field(0.0, alias="grossSalary")
    income_tax: float = Field(0.0, alias="incomeTax")
    eobi_deduction: float = Field(0.0, alias="eobiDeduction")
    social_security: float = Field(0.0, alias="socialSecurity")
    loan_deduction: float = Field(0.0, alias="loanDeduction")
    other_deductions: float = Field(0.0, alias="otherDeductions")
    total_deductions: float = Field(0.0, alias="totalDeductions")
    net_salary: float = Field(0.0, alias="netSalary")
    status: str = "Draft"
    
    # Adjustments
    lop_days: float = Field(0.0, alias="lopDays")
    lop_amount: float = Field(0.0, alias="lopAmount")
    overtime_hours: float = Field(0.0, alias="overtimeHours")
    overtime_amount: float = Field(0.0, alias="overtimeAmount")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class PayrollSummary(BaseModel):
    payroll_run_id: str = Field(..., alias="payrollRunId")
    period: str
    total_employees: int = Field(..., alias="totalEmployees")
    total_gross: float = Field(..., alias="totalGross")
    total_deductions: float = Field(..., alias="totalDeductions")
    total_net: float = Field(..., alias="totalNet")
    status: str
    model_config = ConfigDict(populate_by_name=True)

class PayrollGenerateRequest(BaseModel):
    period_month: str = Field(..., alias="periodMonth")
    period_year: str = Field(..., alias="periodYear")
    organization_id: Optional[str] = Field(None, alias="organizationId")
    model_config = ConfigDict(populate_by_name=True)
