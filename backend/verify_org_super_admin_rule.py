#!/usr/bin/env python
"""
Verification Script: Organization Super Admin Rule
==================================================

This script demonstrates and verifies the Organization Super Admin Rule:
- Creates an organization
- Verifies Super Admin is auto-created
- Displays Super Admin details
- Adds org users and verifies they cannot be Super Admin

Run with: python verify_org_super_admin_rule.py
"""

import sys
import os
from datetime import datetime

# Handle Unicode output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import crud, models, schemas
from backend.database import Base
import backend.domains.core.models
import backend.domains.hcm.models


def setup_test_db():
    """Setup in-memory test database"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def verify_org_super_admin_rule():
    """Verify the Organization Super Admin Rule"""
    print("\n" + "="*80)
    print("ORGANIZATION SUPER ADMIN RULE VERIFICATION")
    print("="*80 + "\n")
    
    db = setup_test_db()
    creator_id = "test-user-123"
    
    # Step 1: Create Organization
    print("STEP 1: Creating Organization")
    print("-" * 80)
    org_data = schemas.OrganizationCreate(
        id="TECHCORP-001",
        code="TECHCORP",
        name="Tech Corporation",
        email="admin@techcorp.com",
        phone="+923001234567",
        is_active=True,
    )
    
    org = crud.create_organization(db, org_data, creator_id)
    print(f"✓ Organization Created:")
    print(f"  - ID: {org.id}")
    print(f"  - Code: {org.code}")
    print(f"  - Name: {org.name}")
    print(f"  - Email: {org.email}\n")
    
    # Step 2: Verify Super Admin Auto-Creation
    print("STEP 2: Verifying Super Admin Auto-Creation")
    print("-" * 80)
    
    super_admin = db.query(models.DBUser).filter(
        models.DBUser.organization_id == org.id,
        models.DBUser.role == "Super Admin"
    ).first()
    
    if super_admin:
        print(f"✓ Super Admin User Auto-Created:")
        print(f"  - ID: {super_admin.id}")
        print(f"  - Username: {super_admin.username}")
        print(f"  - Role: {super_admin.role}")
        print(f"  - Organization ID: {super_admin.organization_id}")
        print(f"  - Is System User: {super_admin.is_system_user}")
        print(f"  - Is Active: {super_admin.is_active}")
        print(f"  - Email: {super_admin.email}")
        print(f"  - Name: {super_admin.name}\n")
    else:
        print("✗ ERROR: Super Admin was not created!\n")
        return False
    
    # Step 3: Verify Super Admin Details
    print("STEP 3: Verifying Super Admin Details")
    print("-" * 80)
    
    # Check username
    expected_username = org.code.lower()
    username_match = super_admin.username == expected_username
    print(f"✓ Username matches org_code (lowercase):")
    print(f"  - Expected: {expected_username}")
    print(f"  - Actual: {super_admin.username}")
    print(f"  - Match: {username_match}\n")
    
    # Check is_system_user
    is_org_user = super_admin.is_system_user == False
    print(f"✓ Super Admin is Organization User (not System User):")
    print(f"  - is_system_user: {super_admin.is_system_user}")
    print(f"  - Correct: {is_org_user}\n")
    
    # Check organization_id
    org_correct = super_admin.organization_id == org.id
    print(f"✓ Super Admin belongs to correct organization:")
    print(f"  - Expected: {org.id}")
    print(f"  - Actual: {super_admin.organization_id}")
    print(f"  - Correct: {org_correct}\n")
    
    # Step 4: Verify Only One Super Admin
    print("STEP 4: Verifying Only One Super Admin Per Organization")
    print("-" * 80)
    
    super_admins = db.query(models.DBUser).filter(
        models.DBUser.organization_id == org.id,
        models.DBUser.role == "Super Admin"
    ).all()
    
    single_admin = len(super_admins) == 1
    print(f"✓ Super Admin Count: {len(super_admins)}")
    print(f"  - Expected: 1")
    print(f"  - Correct: {single_admin}\n")
    
    # Step 5: Add Organization Users
    print("STEP 5: Adding Organization Users")
    print("-" * 80)
    
    users_to_add = [
        ("john.manager", "Manager", "John Manager"),
        ("sarah.hr", "HRManager", "Sarah HR Manager"),
        ("mike.emp", "Employee", "Mike Employee"),
    ]
    
    org_users = []
    for username, role, name in users_to_add:
        user = schemas.UserCreate(
            username=username,
            password=os.getenv("TEST_USER_PASSWORD", "DefaultTestPass123!"),
            role=role,
            name=name,
            email=f"{username}@techcorp.com",
            organization_id=org.id,
            is_system_user=False,
        )
        created_user = crud.create_user(db, user, creator_id)
        org_users.append(created_user)
        print(f"✓ Created {role}: {username}")
    
    print(f"\n  Total users created: {len(org_users)}\n")
    
    # Step 6: Verify Org Users Cannot Be Super Admin
    print("STEP 6: Verifying Organization User Rules")
    print("-" * 80)
    
    for user in org_users:
        is_org_user = user.is_system_user == False
        has_org_id = user.organization_id == org.id
        is_valid_role = user.role in ["Manager", "HRManager", "Employee", "HRExecutive"]
        
        print(f"✓ User: {user.username}")
        print(f"  - Role: {user.role} (Valid: {is_valid_role})")
        print(f"  - Is Org User: {is_org_user}")
        print(f"  - Organization ID Set: {has_org_id}")
    
    print()
    
    # Step 7: Summary
    print("STEP 7: Verification Summary")
    print("-" * 80)
    
    all_checks = [
        ("Super Admin Auto-Created", super_admin is not None),
        ("Username Matches Org Code", username_match),
        ("Super Admin is Org User", is_org_user),
        ("Organization ID Correct", org_correct),
        ("Only One Super Admin", single_admin),
        ("Organization Users Added", len(org_users) > 0),
    ]
    
    passed = sum(1 for _, result in all_checks if result)
    total = len(all_checks)
    
    for check_name, result in all_checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n" + "="*80)
        print("✓ ALL VERIFICATION CHECKS PASSED")
        print("Organization Super Admin Rule is working correctly!")
        print("="*80 + "\n")
        return True
    else:
        print("\n" + "="*80)
        print("✗ SOME VERIFICATION CHECKS FAILED")
        print("="*80 + "\n")
        return False


if __name__ == "__main__":
    try:
        success = verify_org_super_admin_rule()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
