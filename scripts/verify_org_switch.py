import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.domains.core.models import DBUser, DBOrganization, DBDepartment, DBHRPlant
from backend.domains.hcm.models import DBEmployee, DBDesignation, DBGrade, DBJobLevel, DBShift
from backend.dependencies import get_password_hash
import backend.dependencies

# Monkeypatch verify_password to bypass hashing issues
# Monkeypatch verify_password to bypass hashing issues
import backend.dependencies
import backend.main
backend.dependencies.verify_password = lambda p, h: True
backend.main.verify_password = lambda p, h: True

from fastapi.exceptions import ResponseValidationError

try:
    client = TestClient(app)
except Exception as e:
    print(f"FAILED TO CREATE CLIENT: {e}")
    raise


def setup_test_data():
    db = SessionLocal()
    try:
        # 1. ensure organizations
        org1 = db.query(DBOrganization).filter_by(name="Org One").first()
        if not org1:
            org1 = DBOrganization(id="ORG-TEST-1", name="Org One", code="O1", is_active=True)
            db.add(org1)
        
        org2 = db.query(DBOrganization).filter_by(name="Org Two").first()
        if not org2:
            org2 = DBOrganization(id="ORG-TEST-2", name="Org Two", code="O2", is_active=True)
            db.add(org2)
            
        db.commit()
        
        # 2. ensure admin user linked to Org 1
        admin = db.query(DBUser).filter_by(username="verifier").first()
        if not admin:
            admin = DBUser(
                id="USR-TEST-1",
                username="verifier",
                email="verifier@example.com",
                password_hash=get_password_hash("password123"),
                role="Super Admin",
                organization_id="ORG-TEST-1",
                is_active=True
            )
            db.add(admin)
        else:
            admin.organization_id = "ORG-TEST-1"
            admin.role = "Super Admin"
            
        db.commit()

        def create_org_deps(org_id, suffix):
            print(f"Creating deps for {org_id}...")
            # Job Level
            jl = db.query(DBJobLevel).filter_by(id=f"JL-{suffix}").first()
            if not jl:
                jl = DBJobLevel(id=f"JL-{suffix}", name=f"Level {suffix}", code=f"L{suffix}", organization_id=org_id)
                db.add(jl)
                db.commit()
                print("JobLevel created")
            
            # Grade
            gr = db.query(DBGrade).filter_by(id=f"GRD-{suffix}").first()
            if not gr:
                gr = DBGrade(id=f"GRD-{suffix}", name=f"Grade {suffix}", code=f"G{suffix}", job_level_id=f"JL-{suffix}", organization_id=org_id, level=1)
                db.add(gr)
                db.commit()
                print("Grade created")
                
            # Department
            dp = db.query(DBDepartment).filter_by(id=f"DEP-{suffix}").first()
            if not dp:
                dp = DBDepartment(id=f"DEP-{suffix}", name=f"Dept {suffix}", code=f"D{suffix}", organization_id=org_id)
                db.add(dp)
                db.commit()
                print("Department created")

            # Plant
            pl = db.query(DBHRPlant).filter_by(id=f"PLT-{suffix}").first()
            if not pl:
                pl = DBHRPlant(id=f"PLT-{suffix}", name=f"Plant {suffix}", code=f"P{suffix}", location="Loc", organization_id=org_id)
                db.add(pl)
                db.commit()
                print("Plant created")

            # Shift
            sh = db.query(DBShift).filter_by(id=f"SHF-{suffix}").first()
            if not sh:
                sh = DBShift(id=f"SHF-{suffix}", name=f"Shift {suffix}", code=f"S{suffix}", start_time="09:00", end_time="17:00", organization_id=org_id)
                db.add(sh)
                db.commit()
                print("Shift created")

            # Designation
            ds = db.query(DBDesignation).filter_by(id=f"DES-{suffix}").first()
            if not ds:
                ds = DBDesignation(id=f"DES-{suffix}", name=f"Desig {suffix}", code=f"DG{suffix}", grade_id=f"GRD-{suffix}", organization_id=org_id)
                db.add(ds)
                db.commit()
                print("Designation created")

        create_org_deps("ORG-TEST-1", "1")
        create_org_deps("ORG-TEST-2", "2")

        # 3. Add employee to Org 1
        emp1 = db.query(DBEmployee).filter_by(id="EMP-TEST-1").first()
        if not emp1:
            emp1 = DBEmployee(
                id="EMP-TEST-1",
                name="Employee One",
                email="emp1@one.com",
                organization_id="ORG-TEST-1",
                department_id="DEP-1", designation_id="DES-1", grade_id="GRD-1", plant_id="PLT-1", shift_id="SHF-1",
                status="Active"
            )
            db.add(emp1)
        else:
            emp1.status = "Active"
            emp1.organization_id = "ORG-TEST-1"

        # 4. Add employee to Org 2
        emp2 = db.query(DBEmployee).filter_by(id="EMP-TEST-2").first()
        if not emp2:
            emp2 = DBEmployee(
                id="EMP-TEST-2",
                name="Employee Two",
                email="emp2@two.com",
                organization_id="ORG-TEST-2",
                department_id="DEP-2", designation_id="DES-2", grade_id="GRD-2", plant_id="PLT-2", shift_id="SHF-2",
                status="Active"
            )
            db.add(emp2)
        else:
            emp2.status = "Active"
            emp2.organization_id = "ORG-TEST-2"
            
        db.commit()
            
        db.commit()
        return "ORG-TEST-1", "ORG-TEST-2"
        
    finally:
        db.close()

def run_test():
    org1_id, org2_id = setup_test_data()
    print(f"Setup Complete. Org1: {org1_id}, Org2: {org2_id}")

    # Login
    response = client.post("/api/auth/login", json={"username": "verifier", "password": "password123"})
    if response.status_code != 200:
        print("Login Failed", response.text)
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Fetch Default (Org 1)

    print("\n--- TEST 1: Get Employees with User Role (Should return Org 1) ---")
    try:
        resp1 = client.get("/api/employees", headers=headers)
        print(f"Status: {resp1.status_code}")
        employees1 = resp1.json()
        print(f"Response Body: {employees1}")
        ids1 = [e['id'] for e in employees1]
        print(f"Employee IDs: {ids1}")
        
        if "EMP-TEST-1" in ids1 and "EMP-TEST-2" not in ids1:
            print("SUCCESS: Only Org 1 employees returned.")
        else:
            print(f"FAILURE: Expected ['EMP-TEST-1'], got {ids1}")
            
    except ResponseValidationError as e:
        print("\n\n!!! RESPONSE VALIDATION ERROR !!!")
        with open("backend/debug_error.txt", "w") as f:
            import json
            # e.errors() returns list of dicts, but might contain unjsonable objects? usually fine.
            f.write(str(e.errors()))
        raise


    # 2. Fetch Switched (Org 2)
    print(f"\n--- Test 2: Fetch Switched to {org2_id} (Expect Org 2 Data) ---")
    headers_switched = headers.copy()
    headers_switched["x-organization-id"] = org2_id
    
    resp2 = client.get("/api/employees", headers=headers_switched)
    print(f"Status: {resp2.status_code}")
    employees2 = resp2.json()
    ids2 = [e['id'] for e in employees2]
    print(f"Employee IDs: {ids2}")
    
    if "EMP-TEST-2" in ids2 and "EMP-TEST-1" not in ids2:
        print("PASS: Correctly fetched Org 2 employees only.")
    else:
        print("FAIL: Expected only EMP-TEST-2.")

if __name__ == "__main__":
    run_test()
