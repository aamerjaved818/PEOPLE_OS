import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.crud import get_next_employee_code
from backend.domains.core.models import DBHRPlant, DBOrganization
from backend.domains.hcm.models import DBEmployee
from backend.database import Base

# Setup temporary in-memory DB or use existing if safe.
# Using a separate test DB to avoid messing with real data.
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/data/test_auto_numbering.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_auto_numbering():
    init_db()
    db = SessionLocal()
    
    # Setup constraints
    org = DBOrganization(id="ORG1", name="Test Org", code="ORG")
    db.add(org)
    db.commit()
    
    # Create Plant
    plant = DBHRPlant(id="P1", name="Plant 1", code="P1", organization_id="ORG1", current_sequence=0)
    db.add(plant)
    db.commit()
    
    print("Testing basic generation...")
    # Test 1: Basic Generation
    code1 = get_next_employee_code(db, "P1", peek=False)
    print(f"Code 1 (seq should be 1): {code1}")
    assert code1 == "P1-0001"
    assert plant.current_sequence == 1
    
    # Test 2: Peek
    print("Testing peek...")
    code_peek = get_next_employee_code(db, "P1", peek=True)
    print(f"Peek Code (should be P1-0002): {code_peek}")
    assert code_peek == "P1-0002"
    # Sequence should NOT increment
    db.refresh(plant)
    assert plant.current_sequence == 1
    
    # Test 3: Regular call again
    print("Testing regular call after peek...")
    code2 = get_next_employee_code(db, "P1", peek=False)
    print(f"Code 2 (should be P1-0002): {code2}")
    assert code2 == "P1-0002"
    assert plant.current_sequence == 2
    
    # Test 4: Simulate Gap / Manual Insertion
    print("Testing manual insertion gap...")
    # Manually insert P1-0005
    emp = DBEmployee(
        id="P1-0005", employee_code="P1-0005", name="Gap Employee", 
        role="Worker", organization_id="ORG1", plant_id="P1"
    )
    db.add(emp)
    db.commit()
    
    # Next call should skip to 0006, recognizing 0005 exists
    # Current sequence is 2. 
    # Logic: max_db_seq will be 5. next_seq will start at max(5, 2) = 5.
    # Loop will increment to 6.
    code3 = get_next_employee_code(db, "P1", peek=False)
    print(f"Code 3 (should be P1-0006): {code3}")
    assert code3 == "P1-0006"
    assert plant.current_sequence == 6

    print("ALL TESTS PASSED")
    db.close()

if __name__ == "__main__":
    try:
        test_auto_numbering()
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
