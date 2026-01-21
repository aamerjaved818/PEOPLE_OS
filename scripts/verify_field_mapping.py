"""
Comprehensive Field Mapping Verification
Checks alignment between Pydantic Schema, Database Columns, and CRUD operations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.config import settings
from backend import schemas
from sqlalchemy import create_engine, inspect
import re

print("="*80)
print("ORGANIZATION FIELD MAPPING VERIFICATION")
print("="*80)

# Step 1: Get Pydantic Schema Fields
print("\n[STEP 1] Pydantic Schema Fields")
print("-"*80)

schema_fields = {}
org_schema = schemas.OrganizationBase.model_fields

for field_name, field_info in org_schema.items():
    alias = field_info.alias if hasattr(field_info, 'alias') else None
    schema_fields[field_name] = {
        'alias': alias,
        'type': str(field_info.annotation)
    }
    print(f"  {field_name:25} -> alias: {alias or 'None':20} type: {field_info.annotation}")

print(f"\nTotal Schema Fields: {len(schema_fields)}")

# Step 2: Get Database Columns
print("\n[STEP 2] Database Columns")
print("-"*80)

db_url = settings.DATABASE_URL
engine = create_engine(db_url)
inspector = inspect(engine)

db_columns = {}
columns = inspector.get_columns('core_organizations')

for col in columns:
    db_columns[col['name']] = str(col['type'])
    if col['name'] not in ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']:
        print(f"  {col['name']:25} -> type: {col['type']}")

print(f"\nTotal DB Columns: {len(db_columns)}")

# Step 3: Analyze CRUD update_organization function
print("\n[STEP 3] CRUD Field Assignments")
print("-"*80)

crud_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'crud.py')
with open(crud_file, 'r', encoding='utf-8') as f:
    crud_content = f.read()

# Find the update_organization function
update_org_match = re.search(
    r'def update_organization\(.*?\n(.*?)(?=\n    except|\ndef )', 
    crud_content, 
    re.DOTALL
)

if update_org_match:
    update_body = update_org_match.group(1)
    
    # Find all db_org.xxx = org.yyy assignments
    assignments = re.findall(r'db_org\.(\w+)\s*=\s*org\.(\w+)', update_body)
    
    print("  DB Column          <- Pydantic Field")
    print("  " + "-"*50)
    for db_field, pydantic_field in assignments:
        print(f"  {db_field:25} <- {pydantic_field}")
    
    print(f"\nTotal CRUD Assignments: {len(assignments)}")
    
    # Step 4: Identify Mismatches
    print("\n[STEP 4] Mismatch Detection")
    print("-"*80)
    
    mismatches = []
    
    for db_field, pydantic_field in assignments:
        # Check if DB column exists
        if db_field not in db_columns:
            mismatches.append({
                'type': 'DB_COLUMN_MISSING',
                'db_field': db_field,
                'pydantic_field': pydantic_field,
                'issue': f"DB column '{db_field}' does not exist in core_organizations table"
            })
        
        # Check if Pydantic field exists
        if pydantic_field not in schema_fields:
            mismatches.append({
                'type': 'PYDANTIC_FIELD_MISSING',
                'db_field': db_field,
                'pydantic_field': pydantic_field,
                'issue': f"Pydantic field '{pydantic_field}' does not exist in OrganizationBase schema"
            })
    
    if mismatches:
        print("\n❌ MISMATCHES FOUND:")
        for i, mismatch in enumerate(mismatches, 1):
            print(f"\n  {i}. {mismatch['type']}")
            print(f"     DB Field: {mismatch['db_field']}")
            print(f"     Pydantic Field: {mismatch['pydantic_field']}")
            print(f"     Issue: {mismatch['issue']}")
    else:
        print("\n✅ No mismatches found in field assignments")
    
    # Step 5: Check for Missing Assignments
    print("\n[STEP 5] Missing Field Assignments")
    print("-"*80)
    
    assigned_db_fields = {db_field for db_field, _ in assignments}
    assigned_pydantic_fields = {pydantic_field for _, pydantic_field in assignments}
    
    # Exclude audit fields
    exclude_fields = {'id', 'created_at', 'updated_at', 'created_by', 'updated_by'}
    
    missing_db_assignments = [
        col for col in db_columns.keys() 
        if col not in assigned_db_fields and col not in exclude_fields
    ]
    
    missing_pydantic_assignments = [
        field for field in schema_fields.keys()
        if field not in assigned_pydantic_fields
    ]
    
    if missing_db_assignments:
        print("\n⚠️  DB Columns NOT assigned in CRUD:")
        for col in missing_db_assignments:
            print(f"  - {col}")
    
    if missing_pydantic_assignments:
        print("\n⚠️  Pydantic Fields NOT used in CRUD:")
        for field in missing_pydantic_assignments:
            alias = schema_fields[field]['alias']
            print(f"  - {field:25} (alias: {alias or 'None'})")
    
    if not missing_db_assignments and not missing_pydantic_assignments:
        print("\n✅ All fields are assigned")

else:
    print("\n❌ ERROR: Could not find update_organization function in crud.py")

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80)
