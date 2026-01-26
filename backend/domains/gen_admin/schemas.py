from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AssetBase(BaseModel):
    name: str
    serialNumber: str = Field(..., alias="serial_number")
    category: str
    status: Optional[str] = "Active"
    employeeId: Optional[str] = Field(None, alias="employee_id")
    purchaseDate: Optional[str] = Field(None, alias="purchase_date")
    purchaseValue: Optional[float] = Field(0.0, alias="purchase_value")
    currency: Optional[str] = "PKR"
    specifications: Optional[str] = None
    location: Optional[str] = None
    maintenanceScheduleDays: Optional[int] = Field(180, alias="maintenance_schedule_days")

    class Config:
        populate_by_name = True

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: str
    lastMaintenanceDate: Optional[str] = Field(None, alias="last_maintenance_date")
    organization_id: str
    createdAt: Optional[datetime] = Field(None, alias="created_at")

    class Config:
        from_attributes = True
        populate_by_name = True

class MaintenanceBase(BaseModel):
    asset_id: str
    maintenance_date: str
    cost: Optional[float] = 0.0
    description: Optional[str] = None
    service_provider: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class Maintenance(MaintenanceBase):
    id: int

    class Config:
        from_attributes = True

class VisitorBase(BaseModel):
    name: str
    identificationNumber: Optional[str] = Field(None, alias="identification_number")
    organization: Optional[str] = None
    hostId: Optional[str] = Field(None, alias="host_id")
    checkIn: str = Field(..., alias="check_in")
    checkOut: Optional[str] = Field(None, alias="check_out")
    purpose: Optional[str] = None
    badgeNumber: Optional[str] = Field(None, alias="badge_number")
    status: Optional[str] = "Checked-In"

    class Config:
        populate_by_name = True

class VisitorCreate(VisitorBase):
    pass

class Visitor(VisitorBase):
    id: str
    organization_id: str
    createdAt: Optional[datetime] = Field(None, alias="created_at")

    class Config:
        from_attributes = True
        populate_by_name = True

class FacilityBase(BaseModel):
    name: str
    type: str # Room, Desk
    capacity: Optional[int] = 0
    location: Optional[str] = None
    status: Optional[str] = "Available"

class FacilityCreate(FacilityBase):
    pass

class Facility(FacilityBase):
    id: str
    organization_id: str
    createdAt: Optional[datetime] = Field(None, alias="created_at")

    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    facility_id: str
    start_time: str
    end_time: str
    purpose: Optional[str] = None
    attendees: Optional[int] = 1

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: str
    createdAt: Optional[datetime] = Field(None, alias="created_at")

    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    model: str
    plateNumber: str = Field(..., alias="plate_number")
    category: str
    status: Optional[str] = "Available"
    assignedToId: Optional[str] = Field(None, alias="assigned_to_id")
    lastServiceDate: Optional[str] = Field(None, alias="last_service_date")
    lastServiceMileage: Optional[int] = Field(0, alias="last_service_mileage")
    currentMileage: Optional[int] = Field(0, alias="current_mileage")

    class Config:
        populate_by_name = True

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: str
    organization_id: str
    createdAt: Optional[datetime] = Field(None, alias="created_at")

    class Config:
        from_attributes = True
        populate_by_name = True

class ComplianceBase(BaseModel):
    licenseName: str = Field(..., alias="license_name")
    provider: Optional[str] = None
    expiryDate: str = Field(..., alias="expiry_date")
    status: Optional[str] = "Active"
    reminderDaysBefore: Optional[int] = Field(30, alias="reminder_days_before")
    documentUrl: Optional[str] = Field(None, alias="document_url")

    class Config:
        populate_by_name = True

class ComplianceCreate(ComplianceBase):
    pass

class Compliance(ComplianceBase):
    id: int
    organization_id: str
    createdAt: Optional[datetime] = Field(None, alias="created_at")

    class Config:
        from_attributes = True
