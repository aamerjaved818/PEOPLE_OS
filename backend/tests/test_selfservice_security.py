"""
Self-Service Security Fixes Validation Tests
Focus on core security validations: whitelist, org boundaries, and field mapping
"""

import pytest
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend import crud


class TestFieldWhitelistValidation:
    """Test FIX 1: Field whitelist enforcement"""
    
    def test_allowed_fields_whitelist_exists(self):
        """Verify whitelist is defined"""
        assert hasattr(crud, 'ALLOWED_UPDATE_FIELDS')
        assert isinstance(crud.ALLOWED_UPDATE_FIELDS, set)
    
    def test_whitelist_contains_personal_fields(self):
        """Verify whitelist has personal information fields"""
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
        assert required_fields.issubset(crud.ALLOWED_UPDATE_FIELDS)
    
    def test_whitelist_excludes_sensitive_fields(self):
        """Verify sensitive fields are NOT in whitelist"""
        forbidden_fields = {
            'salary',
            'employee_code',
            'department_id',
            'is_active',
            'organization_id',
            'line_manager_id',
            'job_level_id',
            'created_by',
            'updated_by'
        }
        for field in forbidden_fields:
            assert field not in crud.ALLOWED_UPDATE_FIELDS, \
                f"Sensitive field '{field}' should not be in whitelist"


class TestOrganizationBoundaryValidation:
    """Test FIX 2: Organization isolation"""
    
    def test_document_request_validates_org_boundary(self, db, test_employee):
        """Verify document requests enforce org boundaries"""
        from backend import schemas
        
        # Attempt to create request with mismatched org
        request_data = schemas.DocumentRequestCreate.model_validate({
            'organization_id': 'DIFFERENT-ORG',
            'employee_id': test_employee.id,
            'document_type': 'Letter',
            'purpose': 'Test'
        })
        
        with pytest.raises(HTTPException) as exc:
            crud.create_document_request(db, request_data, test_employee.id)
        
        assert exc.value.status_code == 403
        assert 'Organization' in str(exc.value.detail)
    
    def test_document_upload_validates_org_boundary(self, db, test_employee):
        """Verify document uploads enforce org boundaries"""
        from backend import schemas
        
        # Attempt to upload with mismatched org
        doc_data = schemas.EmployeeDocumentCreate.model_validate({
            'organization_id': 'DIFFERENT-ORG',
            'employee_id': test_employee.id,
            'document_type': 'Test',
            'document_name': 'Test',
            'document_url': 'https://example.com/test.pdf',
            'file_size': 1024,
            'mime_type': 'application/pdf'
        })
        
        with pytest.raises(HTTPException) as exc:
            crud.upload_employee_document(db, doc_data, 'uploader-id')
        
        assert exc.value.status_code == 403
        assert 'Organization' in str(exc.value.detail)


class TestInfoUpdateFieldValidation:
    """Test FIX 1: Info update field whitelist enforcement"""
    
    def test_forbidden_field_rejected_on_create(self, db, test_employee):
        """Verify forbidden fields are rejected"""
        from backend import schemas
        
        # Try to create request for salary (forbidden)
        request_data = schemas.InfoUpdateRequestCreate.model_validate({
            'organization_id': test_employee.organization_id,
            'employee_id': test_employee.id,
            'field_name': 'salary',  # FORBIDDEN
            'new_value': '50000',
            'reason': 'Test'
        })
        
        with pytest.raises(HTTPException) as exc:
            crud.create_info_update_request(db, request_data, test_employee.id)
        
        assert exc.value.status_code == 400
        assert 'Cannot update field' in str(exc.value.detail)
    
    def test_allowed_field_accepted_on_create(self, db, test_employee):
        """Verify allowed fields are accepted"""
        from backend import schemas
        
        # Create request for personal_phone (allowed)
        request_data = schemas.InfoUpdateRequestCreate.model_validate({
            'organization_id': test_employee.organization_id,
            'employee_id': test_employee.id,
            'field_name': 'personal_phone',  # ALLOWED
            'new_value': '03001234567',
            'reason': 'Test'
        })
        
        result = crud.create_info_update_request(db, request_data, test_employee.id)
        assert result is not None
        assert result.field_name == 'personal_phone'
    
    def test_forbidden_field_rejected_on_approval(self, db, test_employee, test_manager):
        """Verify forbidden fields can't be approved even if request exists"""
        # Manually create a request with forbidden field (bypassing creation check)
        import backend.domains.hcm.models as hcm_models
        forbidden_request = hcm_models.DBInfoUpdateRequest(
            id=f"IU-TEST-{int(datetime.now().timestamp() * 1000)}",
            organization_id=test_employee.organization_id,
            employee_id=test_employee.id,
            field_name='salary',  # Forbidden
            current_value='40000',
            new_value='50000',
            reason='Bypass test',
            status='Pending',
            requested_date=datetime.now().isoformat(),
            created_by=test_employee.id,
            updated_by=test_employee.id
        )
        db.add(forbidden_request)
        db.commit()
        
        # Try to approve - should fail
        with pytest.raises(HTTPException) as exc:
            crud.approve_info_update_request(
                db, forbidden_request.id, test_manager.id, 'Approved'
            )
        
        assert exc.value.status_code == 400
        assert 'Cannot approve' in str(exc.value.detail)


class TestExplicitFieldMapping:
    """Test FIX 4: Explicit field mapping instead of setattr"""
    
    def test_field_mapping_updates_correct_field(self, db, test_employee, test_manager):
        """Verify that approval uses explicit field mapping"""
        from backend import schemas
        
        original_phone = test_employee.personal_phone
        new_phone = '03119999999'
        
        # Create and approve update for personal_phone
        request_data = schemas.InfoUpdateRequestCreate.model_validate({
            'organization_id': test_employee.organization_id,
            'employee_id': test_employee.id,
            'field_name': 'personal_phone',
            'new_value': new_phone,
            'reason': 'Phone update'
        })
        
        created = crud.create_info_update_request(db, request_data, test_employee.id)
        
        # Approve the update
        crud.approve_info_update_request(
            db, created.id, test_manager.id, 'Approved'
        )
        
        # Verify field was updated
        db.refresh(test_employee)
        assert test_employee.personal_phone == new_phone
        assert test_employee.personal_phone != original_phone
    
    def test_field_mapping_updates_only_requested_field(self, db, test_employee, test_manager):
        """Verify that only the requested field is updated, not others"""
        from backend import schemas
        
        # Store original values
        original_address = test_employee.present_address
        original_email = test_employee.personal_email
        
        new_address = '123 Main Street'
        
        # Create and approve update for present_address
        request_data = schemas.InfoUpdateRequestCreate.model_validate({
            'organization_id': test_employee.organization_id,
            'employee_id': test_employee.id,
            'field_name': 'present_address',
            'new_value': new_address,
            'reason': 'Address update'
        })
        
        created = crud.create_info_update_request(db, request_data, test_employee.id)
        crud.approve_info_update_request(
            db, created.id, test_manager.id, 'Approved'
        )
        
        # Verify only present_address changed
        db.refresh(test_employee)
        assert test_employee.present_address == new_address
        assert test_employee.personal_email == original_email  # Should NOT change


class TestSecurityIntegration:
    """Integration tests for all security fixes working together"""
    
    def test_multiple_security_layers(self, db, test_employee, test_manager):
        """Verify all security layers work together"""
        from backend import schemas
        
        # Test 1: Can't create with wrong org
        bad_request = schemas.DocumentRequestCreate.model_validate({
            'organization_id': 'WRONG-ORG',
            'employee_id': test_employee.id,
            'document_type': 'Letter',
            'purpose': 'Test'
        })
        
        with pytest.raises(HTTPException):
            crud.create_document_request(db, bad_request, test_employee.id)
        
        # Test 2: CAN create with correct org
        good_request = schemas.DocumentRequestCreate.model_validate({
            'organization_id': test_employee.organization_id,
            'employee_id': test_employee.id,
            'document_type': 'Letter',
            'purpose': 'Test'
        })
        
        result = crud.create_document_request(db, good_request, test_employee.id)
        assert result is not None
        assert result.status == 'Pending'
    
    def test_info_update_security_chain(self, db, test_employee):
        """Verify info update security chain"""
        from backend import schemas
        
        # Step 1: Reject forbidden field on creation
        forbidden = schemas.InfoUpdateRequestCreate.model_validate({
            'organization_id': test_employee.organization_id,
            'employee_id': test_employee.id,
            'field_name': 'cnic',  # Sensitive field
            'new_value': 'new-value',
            'reason': 'Test'
        })
        
        with pytest.raises(HTTPException) as exc:
            crud.create_info_update_request(db, forbidden, test_employee.id)
        assert exc.value.status_code == 400
        
        # Step 2: Accept allowed field on creation
        allowed = schemas.InfoUpdateRequestCreate.model_validate({
            'organization_id': test_employee.organization_id,
            'employee_id': test_employee.id,
            'field_name': 'personal_email',  # Allowed field
            'new_value': 'new@example.com',
            'reason': 'Email update'
        })
        
        result = crud.create_info_update_request(db, allowed, test_employee.id)
        assert result.status == 'Pending'
