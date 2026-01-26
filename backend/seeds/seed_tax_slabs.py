"""
Seed Script: Pakistani Income Tax Slabs (FBR 2025-2026)
Run this after database migration to populate default tax slabs.

Usage:
    python backend/seeds/seed_tax_slabs.py --org-id YOUR_ORG_ID
"""
import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import SessionLocal
from backend.domains.hcm.models import DBTaxSlab
import time


# FBR Tax Slabs for Salaried Individuals (2025-2026)
# Source: Federal Board of Revenue Pakistan
PAKISTAN_TAX_SLABS_2025_2026 = [
    # (min_income, max_income, fixed_tax, tax_rate%, excess_over)
    (0, 600000, 0, 0, 0),                          # No tax up to 600,000
    (600001, 1200000, 0, 2.5, 600000),             # 2.5% on excess over 600,000
    (1200001, 2200000, 15000, 12.5, 1200000),      # 15,000 + 12.5% on excess over 1,200,000
    (2200001, 3200000, 140000, 22.5, 2200000),     # 140,000 + 22.5% on excess over 2,200,000
    (3200001, 4100000, 365000, 27.5, 3200000),     # 365,000 + 27.5% on excess over 3,200,000
    (4100001, None, 612500, 35, 4100000),          # 612,500 + 35% on excess over 4,100,000
]


def seed_tax_slabs(organization_id: str, tax_year: str = "2025-2026"):
    """Seed Pakistani tax slabs for an organization"""
    db = SessionLocal()
    
    try:
        # Check if slabs already exist
        existing = db.query(DBTaxSlab).filter(
            DBTaxSlab.organization_id == organization_id,
            DBTaxSlab.tax_year == tax_year
        ).first()
        
        if existing:
            print(f"⚠️  Tax slabs for {tax_year} already exist for org {organization_id}")
            print("   Use --force to overwrite")
            return False
        
        # Create slabs
        created_count = 0
        for min_income, max_income, fixed_tax, tax_rate, excess_over in PAKISTAN_TAX_SLABS_2025_2026:
            slab = DBTaxSlab(
                id=f"TS-{int(time.time() * 1000)}-{created_count}",
                organization_id=organization_id,
                tax_year=tax_year,
                min_income=min_income,
                max_income=max_income,
                fixed_tax=fixed_tax,
                tax_rate=tax_rate,
                excess_over=excess_over,
                is_active=True,
                created_by="system",
                updated_by="system"
            )
            db.add(slab)
            created_count += 1
            time.sleep(0.001)  # Ensure unique IDs
        
        db.commit()
        print(f"✅ Created {created_count} tax slabs for {tax_year}")
        print(f"   Organization: {organization_id}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()


def seed_default_salary_components(organization_id: str):
    """Seed default salary components"""
    from backend.domains.hcm.models import DBSalaryComponent
    
    db = SessionLocal()
    
    DEFAULT_COMPONENTS = [
        # Earnings
        ("HRA", "House Rent Allowance", "earning", "percentage", "basic", 40, True, False, 1),
        ("MEDICAL", "Medical Allowance", "earning", "fixed", None, 0, True, False, 2),
        ("TRANSPORT", "Transport Allowance", "earning", "fixed", None, 0, True, False, 3),
        ("UTILITY", "Utility Allowance", "earning", "fixed", None, 0, True, False, 4),
        ("BONUS", "Performance Bonus", "earning", "fixed", None, 0, True, False, 5),
        
        # Deductions
        ("LOAN", "Loan Deduction", "deduction", "fixed", None, 0, False, False, 10),
        ("ADVANCE", "Salary Advance", "deduction", "fixed", None, 0, False, False, 11),
        ("PF", "Provident Fund", "deduction", "percentage", "basic", 0, False, True, 12),
    ]
    
    try:
        created_count = 0
        for code, name, comp_type, calc_type, pct_of, default_amt, taxable, statutory, order in DEFAULT_COMPONENTS:
            # Check if exists
            existing = db.query(DBSalaryComponent).filter(
                DBSalaryComponent.organization_id == organization_id,
                DBSalaryComponent.code == code
            ).first()
            
            if existing:
                continue
            
            component = DBSalaryComponent(
                id=f"SC-{int(time.time() * 1000)}-{created_count}",
                organization_id=organization_id,
                code=code,
                name=name,
                component_type=comp_type,
                calculation_type=calc_type,
                percentage_of=pct_of,
                default_amount=default_amt,
                is_taxable=taxable,
                is_statutory=statutory,
                display_order=order,
                is_active=True,
                created_by="system",
                updated_by="system"
            )
            db.add(component)
            created_count += 1
            time.sleep(0.001)
        
        db.commit()
        print(f"✅ Created {created_count} default salary components")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Pakistani tax slabs and salary components")
    parser.add_argument("--org-id", required=True, help="Organization ID")
    parser.add_argument("--tax-year", default="2025-2026", help="Tax year (default: 2025-2026)")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing data")
    parser.add_argument("--components", action="store_true", help="Also seed default salary components")
    parser.add_argument("--deductions", action="store_true", help="Also seed tax deduction types")
    parser.add_argument("--all", action="store_true", help="Seed everything")
    
    args = parser.parse_args()
    
    print(f"\n🌱 Seeding payroll data for organization: {args.org_id}\n")
    
    # Seed tax slabs
    seed_tax_slabs(args.org_id, args.tax_year)
    
    # Optionally seed salary components
    if args.components or args.all:
        print()
        seed_default_salary_components(args.org_id)
    
    # Optionally seed tax deduction types
    if args.deductions or args.all:
        print()
        seed_tax_deduction_types(args.org_id)
    
    print("\n✨ Done!\n")


def seed_tax_deduction_types(organization_id: str):
    """Seed default tax deduction types under Income Tax Ordinance 2001"""
    from backend.domains.hcm.models import DBTaxDeductionType
    
    db = SessionLocal()
    
    # (code, name, section, description, deduction_type, max_income_limit, 
    #  calc_percentage, calc_income_percentage, calc_per_unit_limit, requires_doc, requires_ntn)
    DEFAULT_DEDUCTION_TYPES = [
        (
            "SECTION_60D",
            "Tuition Fee Deduction",
            "60D",
            "Deduction for tuition fees paid for children's education",
            "allowance",
            1500000,  # Max income Rs. 1.5M
            5.0,      # 5% of tuition
            25.0,     # 25% of income
            60000,    # Rs. 60,000 per child
            True,
            True
        ),
        (
            "SECTION_62",
            "Charitable Donations",
            "62",
            "Tax credit for approved charitable donations",
            "credit",
            None,
            35.0,     # 35% of donation
            None,
            None,
            True,
            True
        ),
        (
            "SECTION_63",
            "Zakat Deduction",
            "63",
            "Zakat paid during the year",
            "allowance",
            None,
            100.0,    # Full amount deductible
            None,
            None,
            True,
            False
        ),
        (
            "SECTION_64",
            "Life Insurance Premium",
            "64",
            "Tax credit for life insurance or pension fund contributions",
            "credit",
            None,
            20.0,     # 20% of premium
            None,
            None,
            True,
            True
        ),
    ]
    
    try:
        created_count = 0
        for i, (code, name, section, desc, d_type, max_income, calc_pct, income_pct, unit_limit, req_doc, req_ntn) in enumerate(DEFAULT_DEDUCTION_TYPES):
            # Check if exists
            existing = db.query(DBTaxDeductionType).filter(
                DBTaxDeductionType.organization_id == organization_id,
                DBTaxDeductionType.code == code
            ).first()
            
            if existing:
                continue
            
            deduction_type = DBTaxDeductionType(
                id=f"TDT-{int(time.time() * 1000)}-{i}",
                organization_id=organization_id,
                code=code,
                name=name,
                section=section,
                description=desc,
                deduction_type=d_type,
                max_income_limit=max_income,
                calc_percentage=calc_pct,
                calc_income_percentage=income_pct,
                calc_per_unit_limit=unit_limit,
                requires_document=req_doc,
                requires_ntn=req_ntn,
                is_active=True,
                display_order=i,
                created_by="system",
                updated_by="system"
            )
            db.add(deduction_type)
            created_count += 1
            time.sleep(0.001)
        
        db.commit()
        print(f"✅ Created {created_count} tax deduction types (Income Tax Ordinance 2001)")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()
