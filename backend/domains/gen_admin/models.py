from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.domains.hcm.models import AuditMixin
from backend.domains.core.models import PrismaAuditMixin

class DBAsset(Base, AuditMixin):
    __tablename__ = "gen_admin_assets"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    serial_number = Column(String, unique=True, index=True)
    category = Column(String, index=True) # IT, Furniture, Vehicle, etc.
    status = Column(String, default="Active") # Active, Maintenance, Retired, Disposed
    
    # Ownership
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False)
    employee_id = Column(String, ForeignKey("hcm_employees.id"), nullable=True)
    
    # Financials
    purchase_date = Column(String, nullable=True) # YYYY-MM-DD
    purchase_value = Column(Float, default=0.0)
    currency = Column(String, default="PKR")
    
    # Details
    specifications = Column(Text, nullable=True) # JSON or Text
    location = Column(String, nullable=True)
    
    maintenance_schedule_days = Column(Integer, default=180) # Routine maintenance interval
    last_maintenance_date = Column(String, nullable=True)
    
    # Relationships
    organization = relationship("DBOrganization")
    employee = relationship("DBEmployee")

class DBAssetMaintenance(Base, AuditMixin):
    __tablename__ = "gen_admin_asset_maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String, ForeignKey("gen_admin_assets.id"), nullable=False)
    
    maintenance_date = Column(String, nullable=False)
    cost = Column(Float, default=0.0)
    description = Column(String, nullable=True)
    service_provider = Column(String, nullable=True)
    
    asset = relationship("DBAsset", backref="maintenance_history")

class DBVisitor(Base, AuditMixin):
    __tablename__ = "gen_admin_visitors"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    identification_number = Column(String, nullable=True) # CNIC/Passport
    organization = Column(String, nullable=True) # Visitor's org
    
    # Host Info
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False)
    host_id = Column(String, ForeignKey("hcm_employees.id"), nullable=True)
    
    # Visit Details
    check_in = Column(String, nullable=False) # ISO Timestamp
    check_out = Column(String, nullable=True) # ISO Timestamp
    purpose = Column(String, nullable=True)
    badge_number = Column(String, nullable=True)
    status = Column(String, default="Checked-In") # Checked-In, Checked-Out, Expected
    
    # Relationships
    host = relationship("DBEmployee")

class DBFacility(Base, AuditMixin):
    __tablename__ = "gen_admin_facilities"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True) # Meeting Room, Hot Desk, Conference Hall
    capacity = Column(Integer, default=0)
    location = Column(String, nullable=True)
    
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False)
    status = Column(String, default="Available") # Available, Maintenance, Restricted

class DBFacilityBooking(Base, AuditMixin):
    __tablename__ = "gen_admin_facility_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(String, ForeignKey("gen_admin_facilities.id"), nullable=False)
    user_id = Column(String, ForeignKey("core_users.id"), nullable=False)
    
    start_time = Column(String, nullable=False) # ISO Timestamp
    end_time = Column(String, nullable=False)   # ISO Timestamp
    purpose = Column(String, nullable=True)
    attendees = Column(Integer, default=1)
    
    facility = relationship("DBFacility", backref="bookings")
    user = relationship("DBUser")

class DBVehicle(Base, AuditMixin):
    __tablename__ = "gen_admin_vehicles"
    
    id = Column(String, primary_key=True, index=True)
    model = Column(String)
    plate_number = Column(String, unique=True, index=True)
    category = Column(String) # Pool, Assigned, Logistics
    status = Column(String, default="Available") # Available, In-Use, Maintenance
    
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False)
    assigned_to_id = Column(String, ForeignKey("hcm_employees.id"), nullable=True)
    
    last_service_date = Column(String, nullable=True)
    last_service_mileage = Column(Integer, default=0)
    current_mileage = Column(Integer, default=0)
    
    assigned_to = relationship("DBEmployee")

class DBAdminCompliance(Base, AuditMixin):
    __tablename__ = "gen_admin_compliance"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("core_organizations.id"), nullable=False)
    
    license_name = Column(String, index=True)
    provider = Column(String, nullable=True) # Authority/Issuer
    expiry_date = Column(String, nullable=False)
    status = Column(String, default="Active") # Active, Expired, Renewal-Pending
    
    reminder_days_before = Column(Integer, default=30)
    document_url = Column(String, nullable=True)
