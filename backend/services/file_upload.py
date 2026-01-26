"""
File Upload Service
Handles file uploads, validation, storage, and thumbnail generation
"""
import os
import uuid
import hashlib
from datetime import datetime
from typing import Optional, List, Tuple
from fastapi import UploadFile, HTTPException
from PIL import Image
import mimetypes


class FileUploadService:
    """Service for handling file uploads with validation and storage"""
    
    def __init__(self, upload_dir: str = "backend/uploads"):
        self.upload_dir = upload_dir
        self.profile_photos_dir = os.path.join(upload_dir, "profile_photos")
        self.documents_dir = os.path.join(upload_dir, "documents")
        self.generated_docs_dir = os.path.join(upload_dir, "generated_documents")
        
        # Create directories if they don't exist
        for directory in [self.profile_photos_dir, self.documents_dir, self.generated_docs_dir]:
            os.makedirs(directory, exist_ok=True)
    
    # File size limits in MB
    MAX_PHOTO_SIZE_MB = 5
    MAX_DOCUMENT_SIZE_MB = 10
    
    # Allowed file extensions
    ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "txt"}
    
    def validate_file(
        self, 
        file: UploadFile, 
        max_size_mb: float, 
        allowed_extensions: set
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        Returns: (is_valid, error_message)
        """
        # Check file extension
        file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"File too large. Maximum size: {max_size_mb}MB"
        
        # Check content type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        if not content_type:
            return False, "Could not determine file type"
        
        return True, None
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename with timestamp and UUID"""
        ext = original_filename.split('.')[-1].lower() if '.' in original_filename else ''
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{timestamp}_{unique_id}.{ext}"
    
    async def upload_profile_photo(
        self, 
        file: UploadFile, 
        employee_id: str
    ) -> dict:
        """
        Upload and process profile photo
        Returns: {url, thumbnail_url, file_size}
        """
        # Validate file
        is_valid, error = self.validate_file(
            file, 
            self.MAX_PHOTO_SIZE_MB, 
            self.ALLOWED_PHOTO_EXTENSIONS
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Generate unique filename
        filename = self.generate_unique_filename(file.filename)
        file_path = os.path.join(self.profile_photos_dir, filename)
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Generate thumbnail
        thumbnail_path = await self.generate_thumbnail(file_path, size=(150, 150))
        
        # Calculate file size
        file_size = os.path.getsize(file_path)
        
        return {
            "url": f"/uploads/profile_photos/{filename}",
            "thumbnail_url": f"/uploads/profile_photos/{os.path.basename(thumbnail_path)}",
            "file_size": file_size,
            "filename": filename
        }
    
    async def upload_document(
        self, 
        file: UploadFile, 
        employee_id: str,
        document_type: str
    ) -> dict:
        """
        Upload employee document
        Returns: {url, file_size, mime_type, filename}
        """
        # Validate file
        is_valid, error = self.validate_file(
            file, 
            self.MAX_DOCUMENT_SIZE_MB, 
            self.ALLOWED_DOCUMENT_EXTENSIONS
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Generate unique filename
        filename = self.generate_unique_filename(file.filename)
        file_path = os.path.join(self.documents_dir, filename)
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Get mime type
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        # Calculate file size
        file_size = os.path.getsize(file_path)
        
        return {
            "url": f"/uploads/documents/{filename}",
            "file_size": file_size,
            "mime_type": mime_type,
            "filename": filename
        }
    
    async def generate_thumbnail(
        self, 
        image_path: str, 
        size: tuple = (150, 150)
    ) -> str:
        """
        Generate thumbnail for image
        Returns: thumbnail file path
        """
        try:
            # Open image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Generate thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumbnail_filename = f"thumb_{os.path.basename(image_path)}"
            thumbnail_path = os.path.join(os.path.dirname(image_path), thumbnail_filename)
            img.save(thumbnail_path, "JPEG", quality=85)
            
            return thumbnail_path
        except Exception as e:
            # If thumbnail generation fails, return original
            print(f"Thumbnail generation failed: {e}")
            return image_path
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete file from storage
        Returns: True if deleted successfully
        """
        try:
            # Extract file path from URL
            file_path = file_url.replace("/uploads/", self.upload_dir + "/")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
                # Also delete thumbnail if it exists
                thumbnail_path = os.path.join(
                    os.path.dirname(file_path),
                    f"thumb_{os.path.basename(file_path)}"
                )
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                return True
            return False
        except Exception as e:
            print(f"File deletion failed: {e}")
            return False
    
    def get_file_info(self, file_url: str) -> Optional[dict]:
        """Get information about a file"""
        try:
            file_path = file_url.replace("/uploads/", self.upload_dir + "/")
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                mime_type = mimetypes.guess_type(file_path)[0]
                
                return {
                    "url": file_url,
                    "file_size": file_size,
                    "mime_type": mime_type,
                    "exists": True
                }
            return None
        except Exception as e:
            print(f"Get file info failed: {e}")
            return None


# Global instance
file_upload_service = FileUploadService()
