from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from . import models, schemas

# --- Assets ---
def get_assets(db: Session, skip: int = 0, limit: int = 100, organization_id: str = None):
    query = db.query(models.DBAsset)
    if organization_id:
        query = query.filter(models.DBAsset.organization_id == organization_id)
    return query.offset(skip).limit(limit).all()

def create_asset(db: Session, asset: schemas.AssetCreate, organization_id: str, user_id: str):
    db_asset = models.DBAsset(
        **asset.dict(by_alias=True),
        id=f"AST-{int(datetime.now().timestamp())}",
        organization_id=organization_id,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

# --- Visitors ---
def get_visitors(db: Session, skip: int = 0, limit: int = 100, organization_id: str = None):
    query = db.query(models.DBVisitor)
    if organization_id:
        query = query.filter(models.DBVisitor.organization_id == organization_id)
    return query.offset(skip).limit(limit).all()

def create_visitor(db: Session, visitor: schemas.VisitorCreate, organization_id: str, user_id: str):
    db_visitor = models.DBVisitor(
        **visitor.dict(by_alias=True),
        id=f"VST-{int(datetime.now().timestamp())}",
        organization_id=organization_id,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_visitor)
    db.commit()
    db.refresh(db_visitor)
    return db_visitor

def checkout_visitor(db: Session, visitor_id: str, user_id: str):
    db_visitor = db.query(models.DBVisitor).filter(models.DBVisitor.id == visitor_id).first()
    if db_visitor:
        db_visitor.check_out = datetime.now().isoformat()
        db_visitor.status = "Checked-Out"
        db_visitor.updated_by = user_id
        db.commit()
        db.refresh(db_visitor)
    return db_visitor

# --- Facilities ---
def get_facilities(db: Session, skip: int = 0, limit: int = 100, organization_id: str = None):
    query = db.query(models.DBFacility)
    if organization_id:
        query = query.filter(models.DBFacility.organization_id == organization_id)
    return query.offset(skip).limit(limit).all()

def create_facility(db: Session, facility: schemas.FacilityCreate, organization_id: str, user_id: str):
    db_facility = models.DBFacility(
        **facility.dict(),
        id=f"FAC-{int(datetime.now().timestamp())}",
        organization_id=organization_id,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility

def book_facility(db: Session, booking: schemas.BookingCreate, user_id: str):
    # Overlap check
    overlap = db.query(models.DBFacilityBooking).filter(
        models.DBFacilityBooking.facility_id == booking.facility_id,
        models.DBFacilityBooking.start_time < booking.end_time,
        models.DBFacilityBooking.end_time > booking.start_time
    ).first()
    
    if overlap:
        return None # Conflict
        
    db_booking = models.DBFacilityBooking(
        **booking.dict(),
        user_id=user_id,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

# --- Vehicles ---
def get_vehicles(db: Session, skip: int = 0, limit: int = 100, organization_id: str = None):
    query = db.query(models.DBVehicle)
    if organization_id:
        query = query.filter(models.DBVehicle.organization_id == organization_id)
    return query.offset(skip).limit(limit).all()

def create_vehicle(db: Session, vehicle: schemas.VehicleCreate, organization_id: str, user_id: str):
    db_vehicle = models.DBVehicle(
        **vehicle.dict(by_alias=True),
        id=f"VHC-{int(datetime.now().timestamp())}",
        organization_id=organization_id,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

# --- Compliance ---
def get_compliance_records(db: Session, organization_id: str):
    return db.query(models.DBAdminCompliance).filter(models.DBAdminCompliance.organization_id == organization_id).all()

def create_compliance_record(db: Session, record: schemas.ComplianceCreate, organization_id: str, user_id: str):
    db_record = models.DBAdminCompliance(
        **record.dict(),
        organization_id=organization_id,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record
