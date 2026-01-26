"""
Request validation and security middleware for API protection

Validates request format, size, and content before processing.
"""

from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import json


class RequestValidationConfig:
    """Configuration for request validation"""
    
    def __init__(
        self,
        max_body_size: int = 10 * 1024 * 1024,  # 10MB
        max_header_size: int = 8192,  # 8KB
        allowed_content_types: Optional[list] = None,
        require_content_type: bool = True,
        max_query_params: int = 100,
        validate_json: bool = True
    ):
        self.max_body_size = max_body_size
        self.max_header_size = max_header_size
        self.allowed_content_types = allowed_content_types or [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ]
        self.require_content_type = require_content_type
        self.max_query_params = max_query_params
        self.validate_json = validate_json


class RequestValidator:
    """Validates incoming requests"""
    
    def __init__(self, config: Optional[RequestValidationConfig] = None):
        self.config = config or RequestValidationConfig()
    
    async def validate_request(self, request: Request) -> tuple[bool, Optional[str]]:
        """Validate request comprehensively"""
        
        # Check headers
        valid, error = await self._validate_headers(request)
        if not valid:
            return False, error
        
        # Check query parameters
        valid, error = self._validate_query_params(request)
        if not valid:
            return False, error
        
        # Check content type
        if request.method in ["POST", "PUT", "PATCH"]:
            valid, error = await self._validate_content_type(request)
            if not valid:
                return False, error
            
            # Check body size
            valid, error = await self._validate_body_size(request)
            if not valid:
                return False, error
            
            # Validate JSON if needed
            if self.config.validate_json:
                valid, error = await self._validate_json(request)
                if not valid:
                    return False, error
        
        return True, None
    
    async def _validate_headers(self, request: Request) -> tuple[bool, Optional[str]]:
        """Validate request headers"""
        total_header_size = sum(
            len(k) + len(str(v))
            for k, v in request.headers.items()
        )
        
        if total_header_size > self.config.max_header_size:
            return False, "Headers exceed maximum size"
        
        return True, None
    
    def _validate_query_params(self, request: Request) -> tuple[bool, Optional[str]]:
        """Validate query parameters"""
        if len(request.query_params) > self.config.max_query_params:
            return False, f"Too many query parameters (max: {self.config.max_query_params})"
        
        return True, None
    
    async def _validate_content_type(self, request: Request) -> tuple[bool, Optional[str]]:
        """Validate content type"""
        content_type = request.headers.get("content-type", "").lower()
        
        if not content_type and self.config.require_content_type:
            return False, "Content-Type header required"
        
        if content_type:
            # Extract base content type (without charset)
            base_type = content_type.split(";")[0].strip()
            
            if base_type not in self.config.allowed_content_types:
                return False, f"Unsupported Content-Type: {base_type}"
        
        return True, None
    
    async def _validate_body_size(self, request: Request) -> tuple[bool, Optional[str]]:
        """Validate request body size"""
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                size = int(content_length)
                if size > self.config.max_body_size:
                    return False, f"Request body exceeds maximum size ({self.config.max_body_size} bytes)"
            except ValueError:
                return False, "Invalid Content-Length header"
        
        return True, None
    
    async def _validate_json(self, request: Request) -> tuple[bool, Optional[str]]:
        """Validate JSON content"""
        content_type = request.headers.get("content-type", "").lower()
        
        if "application/json" not in content_type:
            return True, None  # Not JSON, skip validation
        
        try:
            body = await request.body()
            if body:
                json.loads(body)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Error validating JSON: {str(e)}"
        
        return True, None


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate requests"""
    
    def __init__(self, app, config: Optional[RequestValidationConfig] = None):
        super().__init__(app)
        self.validator = RequestValidator(config)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Validate request before processing"""
        
        valid, error = await self.validator.validate_request(request)
        
        if not valid:
            raise HTTPException(
                status_code=400,
                detail=error or "Invalid request"
            )
        
        return await call_next(request)


class PayloadValidator:
    """Validates JSON payload structure"""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: list[str]) -> tuple[bool, Optional[str]]:
        """Check required fields are present"""
        missing = [field for field in required_fields if field not in data]
        
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        return True, None
    
    @staticmethod
    def validate_field_types(data: Dict[str, Any], type_map: Dict[str, type]) -> tuple[bool, Optional[str]]:
        """Validate field types"""
        for field, expected_type in type_map.items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    return False, f"Field '{field}' must be {expected_type.__name__}"
        
        return True, None
    
    @staticmethod
    def validate_field_values(
        data: Dict[str, Any],
        validation_rules: Dict[str, callable]
    ) -> tuple[bool, Optional[str]]:
        """Validate field values with custom validators"""
        for field, validator in validation_rules.items():
            if field in data:
                try:
                    is_valid = validator(data[field])
                    if not is_valid:
                        return False, f"Field '{field}' has invalid value"
                except Exception as e:
                    return False, f"Validation error for field '{field}': {str(e)}"
        
        return True, None


class InputSanitizer:
    """Sanitizes user input to prevent injection attacks"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return value
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Trim whitespace
        value = value.strip()
        
        # Limit length
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], max_string_length: Optional[int] = None) -> Dict[str, Any]:
        """Sanitize dictionary values"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value, max_string_length)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(value, max_string_length)
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_string(v, max_string_length) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def detect_injection_attempts(value: str) -> bool:
        """Detect common injection patterns"""
        if not isinstance(value, str):
            return False
        
        import re
        # Check for SQL injection patterns
        sql_patterns = [
            r"'.*?OR.*?'.*?=.*?'",  # ' OR '1'='1
            r'OR.*?1=1',            # OR 1=1
            r"';.*?DROP",           # '; DROP
            r"UNION.*?SELECT",      # UNION SELECT
            r"INSERT.*?INTO",       # INSERT INTO
            r"DELETE.*?FROM",       # DELETE FROM
            r"UPDATE.*?SET"         # UPDATE SET
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        # Check for script injection
        script_patterns = [r"<script", r"javascript:", r"onerror=", r"onclick="]
        for pattern in script_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False
