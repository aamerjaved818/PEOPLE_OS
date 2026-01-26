from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.dependencies import get_current_user, get_current_active_user
from backend.domains.gen_admin import crud, schemas
from backend.domains.core.models import DBUser

router = APIRouter(prefix="/gen-admin", tags=["General Administration"])

# --- Assets ---
@router.get("/assets", response_model=List[schemas.Asset])
def read_assets(
    organization_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.get_assets(db, skip=skip, limit=limit, organization_id=organization_id)

@router.post("/assets", response_model=schemas.Asset)
def create_asset(
    asset: schemas.AssetCreate,
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.create_asset(db, asset=asset, organization_id=organization_id, user_id=current_user.id)

# --- Visitors ---
@router.get("/visitors", response_model=List[schemas.Visitor])
def read_visitors(
    organization_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.get_visitors(db, skip=skip, limit=limit, organization_id=organization_id)

@router.post("/visitors", response_model=schemas.Visitor)
def create_visitor(
    visitor: schemas.VisitorCreate,
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.create_visitor(db, visitor=visitor, organization_id=organization_id, user_id=current_user.id)

@router.put("/visitors/{visitor_id}/checkout", response_model=schemas.Visitor)
def checkout_visitor(
    visitor_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    visitor = crud.checkout_visitor(db, visitor_id=visitor_id, user_id=current_user.id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor

# --- Facilities ---
@router.get("/facilities", response_model=List[schemas.Facility])
def read_facilities(
    organization_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.get_facilities(db, skip=skip, limit=limit, organization_id=organization_id)

@router.post("/facilities", response_model=schemas.Facility)
def create_facility(
    facility: schemas.FacilityCreate,
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.create_facility(db, facility=facility, organization_id=organization_id, user_id=current_user.id)

@router.post("/bookings", response_model=schemas.Booking)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    db_booking = crud.book_facility(db, booking=booking, user_id=current_user.id)
    if not db_booking:
        raise HTTPException(status_code=400, detail="Facility already booked for this time slot")
    return db_booking

# --- Vehicles ---
@router.get("/vehicles", response_model=List[schemas.Vehicle])
def read_vehicles(
    organization_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.get_vehicles(db, skip=skip, limit=limit, organization_id=organization_id)

@router.post("/vehicles", response_model=schemas.Vehicle)
def create_vehicle(
    vehicle: schemas.VehicleCreate,
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.create_vehicle(db, vehicle=vehicle, organization_id=organization_id, user_id=current_user.id)

# --- Compliance ---
@router.get("/compliance", response_model=List[schemas.Compliance])
def read_compliance(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.get_compliance_records(db, organization_id=organization_id)

@router.post("/compliance", response_model=schemas.Compliance)
def create_compliance(
    record: schemas.ComplianceCreate,
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    return crud.create_compliance_record(db, record=record, organization_id=organization_id, user_id=current_user.id)
