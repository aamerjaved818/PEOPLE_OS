"""
Self-Service Module Tests
Validates document requests, info updates, and security boundaries
"""

import pytest
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
import time

from backend import crud, schemas
import backend.domains.core.models as core_models
import backend.domains.hcm.models as hcm_models

# Setup models proxy
class ModelsProxy:
    def __getattr__(self, name):
        if hasattr(core_models, name):
            return getattr(core_models, name)
        if hasattr(hcm_models, name):
            return getattr(hcm_models, name)
        raise AttributeError(f"Model {name} not found in Core or HCM domains")

models = ModelsProxy()


class TestDocumentRequests:
    """Test document request functionality with security validation"""
    
    def test_create_document_request_success(self, db: Session, test_employee):
        """Test successful document request creation"""
        request_data = schemas.DocumentRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            document_type="Experience Letter",
            purpose="Job application",
            additional_notes="Required by Friday"
        )
        
        result = crud.create_document_request(db, request_data, test_employee.id)
        
        assert result is not None
        assert result.organization_id == test_employee.organization_id
        assert result.employee_id == test_employee.id
        assert result.document_type == "Experience Letter"
        assert result.status == "Pending"
    
    def test_create_document_request_org_mismatch(self, db: Session, test_employee):
        """FIX 2: Verify organization boundary - should reject cross-org requests"""
        request_data = schemas.DocumentRequestCreate(
            organization_id="WRONG-ORG-ID",  # Different from employee's org
            employee_id=test_employee.id,
            document_type="Salary Certificate",
            purpose="Loan application"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            crud.create_document_request(db, request_data, test_employee.id)
        
        assert exc_info.value.status_code == 403
        assert "Organization mismatch" in exc_info.value.detail
    
    def test_create_document_request_employee_not_found(self, db: Session):
        """Test document request with non-existent employee"""
        request_data = schemas.DocumentRequestCreate(
            organization_id="ORG-001",
            employee_id="INVALID-EMP-ID",
            document_type="Experience Letter",
            purpose="Job application"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            crud.create_document_request(db, request_data, "INVALID-EMP-ID")
        
        assert exc_info.value.status_code == 404
    
    def test_get_document_requests(self, db: Session, test_employee):
        """Test retrieving employee's document requests"""
        # Create a document request
        request_data = schemas.DocumentRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            document_type="Salary Certificate",
            purpose="Bank loan"
        )
        created = crud.create_document_request(db, request_data, test_employee.id)
        
        # Retrieve requests
        requests = crud.get_my_document_requests(db, test_employee.id)
        
        assert len(requests) >= 1
        assert any(r.id == created.id for r in requests)


class TestInfoUpdateRequests:
    """Test info update request functionality with security validation"""
    
    def test_create_info_update_request_allowed_field(self, db: Session, test_employee):
        """Test creating info update request for allowed field"""
        request_data = schemas.InfoUpdateRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            field_name="personal_phone",
            new_value="03001234567",
            reason="Updated contact number"
        )
        
        result = crud.create_info_update_request(db, request_data, test_employee.id)
        
        assert result is not None
        assert result.field_name == "personal_phone"
        assert result.new_value == "03001234567"
        assert result.status == "Pending"
    
    def test_create_info_update_request_forbidden_field(self, db: Session, test_employee):
        """FIX 1: Verify field whitelist - should reject sensitive fields"""
        request_data = schemas.InfoUpdateRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            field_name="salary",  # NOT in ALLOWED_UPDATE_FIELDS
            new_value="50000",
            reason="Salary review"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            crud.create_info_update_request(db, request_data, test_employee.id)
        
        assert exc_info.value.status_code == 400
        assert "Cannot update field" in exc_info.value.detail
    
    def test_create_info_update_request_system_field(self, db: Session, test_employee):
        """FIX 1: Verify field whitelist - should reject system fields"""
        request_data = schemas.InfoUpdateRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            field_name="employee_code",  # System field
            new_value="NEW-CODE",
            reason="Correction"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            crud.create_info_update_request(db, request_data, test_employee.id)
        
        assert exc_info.value.status_code == 400
    
    def test_approve_info_update_request_success(self, db: Session, test_employee, test_manager):
        """Test successful approval of info update request"""
        # Create request
        request_data = schemas.InfoUpdateRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            field_name="personal_email",
            new_value="newemail@company.com",
            reason="Personal email update"
        )
        created = crud.create_info_update_request(db, request_data, test_employee.id)
        
        # Approve request
        result = crud.approve_info_update_request(
            db, created.id, test_manager.id, "Approved"
        )
        
        assert result.status == "Approved"
        assert result.approved_by == test_manager.id
        assert result.approved_date is not None
        
        # Verify employee field was updated
        db.refresh(test_employee)
        assert test_employee.personal_email == "newemail@company.com"
    
    def test_approve_info_update_request_forbidden_field(self, db: Session, test_employee, test_manager):
        """FIX 4: Verify field whitelist on approval - should reject forbidden fields"""
        # Manually create a request with forbidden field (bypass creation validation for testing)
        update_request = models.DBInfoUpdateRequest(
            id=f"IU-TEST-{int(__import__('time').time() * 1000)}",
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            field_name="salary",  # Forbidden field
            current_value=None,
            new_value="50000",
            reason="Test",
            status="Pending",
            requested_date=datetime.now().isoformat(),
            created_by=test_employee.id,
            updated_by=test_employee.id
        )
        db.add(update_request)
        db.commit()
        
        # Attempt to approve - should fail
        with pytest.raises(HTTPException) as exc_info:
            crud.approve_info_update_request(
                db, update_request.id, test_manager.id, "Approved"
            )
        
        assert exc_info.value.status_code == 400
        assert "Cannot approve update for field" in exc_info.value.detail
    
    def test_approve_info_update_request_rejection(self, db: Session, test_employee, test_manager):
        """Test rejecting an info update request"""
        # Create request
        request_data = schemas.InfoUpdateRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            field_name="permanent_address",
            new_value="New Address",
            reason="Address update"
        )
        created = crud.create_info_update_request(db, request_data, test_employee.id)
        
        # Reject request
        result = crud.approve_info_update_request(
            db, created.id, test_manager.id, "Rejected", 
            rejection_reason="Address not verifiable"
        )
        
        assert result.status == "Rejected"
        assert result.rejection_reason == "Address not verifiable"
        assert result.approved_by == test_manager.id
        
        # Verify employee field was NOT updated
        db.refresh(test_employee)
        assert test_employee.permanent_address != "New Address"


class TestDocumentUpload:
    """Test document upload functionality with org isolation"""
    
    def test_upload_employee_document_success(self, db: Session, test_employee, test_manager):
        """Test successful document upload"""
        document_data = schemas.EmployeeDocumentCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            document_type="Insurance",
            document_name="Health Insurance Policy",
            document_url="https://documents.company.com/insurance-2026.pdf",
            file_size=2048576,
            mime_type="application/pdf",
            description="Employee health insurance policy",
            expiry_date="2027-12-31",
            is_private=False
        )
        
        result = crud.upload_employee_document(db, document_data, test_manager.id)
        
        assert result is not None
        assert result.organization_id == test_employee.organization_id
        assert result.employee_id == test_employee.id
        assert result.document_name == "Health Insurance Policy"
        assert result.uploaded_by == test_manager.id
    
    def test_upload_document_org_mismatch(self, db: Session, test_employee, test_manager):
        """FIX 2: Verify org isolation - should reject cross-org uploads"""
        document_data = schemas.EmployeeDocumentCreate(
            organization_id="WRONG-ORG",  # Different from employee's org
            employee_id=test_employee.id,
            document_type="Insurance",
            document_name="Document",
            document_url="https://documents.company.com/doc.pdf",
            file_size=1024,
            mime_type="application/pdf"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            crud.upload_employee_document(db, document_data, test_manager.id)
        
        assert exc_info.value.status_code == 403
        assert "Organization mismatch" in exc_info.value.detail
    
    def test_upload_document_employee_not_found(self, db: Session, test_manager):
        """Test upload for non-existent employee"""
        document_data = schemas.EmployeeDocumentCreate(
            organization_id="ORG-001",
            employee_id="INVALID-EMP",
            document_type="Insurance",
            document_name="Document",
            document_url="https://documents.company.com/doc.pdf",
            file_size=1024,
            mime_type="application/pdf"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            crud.upload_employee_document(db, document_data, test_manager.id)
        
        assert exc_info.value.status_code == 404
    
    def test_get_my_documents(self, db: Session, test_employee, test_manager):
        """Test retrieving employee's documents"""
        # Upload a document
        document_data = schemas.EmployeeDocumentCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            document_type="Contract",
            document_name="Employment Contract",
            document_url="https://documents.company.com/contract.pdf",
            file_size=512000,
            mime_type="application/pdf"
        )
        uploaded = crud.upload_employee_document(db, document_data, test_manager.id)
        
        # Retrieve documents
        documents = crud.get_my_documents(db, test_employee.id)
        
        assert len(documents) >= 1
        assert any(d.id == uploaded.id for d in documents)


class TestProfileUpdates:
    """Test profile update functionality"""
    
    def test_update_my_profile(self, db: Session, test_employee):
        """Test profile update with photo and bio"""
        profile_data = schemas.ProfileUpdate(
            profile_photo_url="https://photos.company.com/user-001.jpg",
            bio="Senior Developer with 5 years experience"
        )
        
        result = crud.update_my_profile(db, profile_data, test_employee.id)
        
        assert result is not None
        assert result.profile_photo_url == "https://photos.company.com/user-001.jpg"
        assert result.bio == "Senior Developer with 5 years experience"
    
    def test_update_emergency_contact(self, db: Session, test_employee):
        """Test emergency contact update"""
        contact_data = schemas.EmergencyContactUpdate(
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="03001234567",
            emergency_contact_relation="Spouse"
        )
        
        result = crud.update_emergency_contact(db, contact_data, test_employee.id)
        
        assert result is not None
        assert result.emergency_contact_name == "Jane Doe"
        assert result.emergency_contact_phone == "03001234567"
        assert result.emergency_contact_relation == "Spouse"


class TestAllowedFieldsWhitelist:
    """Test that ALLOWED_UPDATE_FIELDS whitelist is properly enforced"""
    
    def test_whitelist_contains_required_fields(self):
        """Verify whitelist has all necessary fields"""
        required_fields = {
            'present_address',
            'permanent_address',
            'personal_phone',
            'personal_email',
            'date_of_birth',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relation',
            'father_name',
            'marital_status'
        }
        
        assert crud.ALLOWED_UPDATE_FIELDS >= required_fields
    
    def test_whitelist_excludes_sensitive_fields(self):
        """Verify whitelist excludes sensitive system fields"""
        sensitive_fields = {
            'salary',
            'employee_code',
            'department_id',
            'is_active',
            'created_by',
            'organization_id',
            'line_manager_id',
            'job_level_id'
        }
        
        # Verify NO sensitive fields in whitelist
        for field in sensitive_fields:
            assert field not in crud.ALLOWED_UPDATE_FIELDS, \
                f"Sensitive field '{field}' should not be in whitelist"


class TestSecurityBoundaries:
    """Test multi-tenancy and security boundaries"""
    
    def test_org_isolation_document_request(self, db: Session, test_employee):
        """Verify document requests respect org boundaries"""
        # Create request for employee
        request_data = schemas.DocumentRequestCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            document_type="Letter",
            purpose="Test"
        )
        
        crud.create_document_request(db, request_data, test_employee.id)
        
        # Verify requests filtered by employee
        requests = crud.get_my_document_requests(db, test_employee.id)
        
        # All requests should belong to this employee
        for req in requests:
            assert req.employee_id == test_employee.id
    
    def test_org_isolation_documents(self, db: Session, test_employee, test_manager):
        """Verify documents respect org boundaries"""
        # Upload document for employee
        document_data = schemas.EmployeeDocumentCreate(
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            document_type="Test",
            document_name="Test Doc",
            document_url="https://example.com/doc.pdf",
            file_size=1024,
            mime_type="text/plain"
        )
        
        crud.upload_employee_document(db, document_data, test_manager.id)
        
        # Verify documents filtered by employee
        documents = crud.get_my_documents(db, test_employee.id)
        
        # All documents should belong to this employee
        for doc in documents:
            assert doc.employee_id == test_employee.id
