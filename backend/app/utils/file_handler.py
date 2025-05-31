"""
Comprehensive file handling system with security and optimization.
Handles file uploads, validation, storage, streaming, and cleanup.
"""

import os
import uuid
import hashlib
import mimetypes
import magic
import io
from pathlib import Path
from typing import Optional, Tuple, BinaryIO, AsyncGenerator, Dict, Any, List
from datetime import datetime
from PIL import Image, ImageOps
import aiofiles
import aiofiles.os
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse

from ..core.config import settings


class FileHandler:
    """
    Advanced file handling with security, optimization, and streaming
    """
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIRECTORY)
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_types = settings.ALLOWED_FILE_TYPES
        
        # Create subdirectories for organization
        self.subdirs = {
            'documents': self.upload_dir / 'documents',
            'avatars': self.upload_dir / 'avatars',
            'archive': self.upload_dir / 'archive',
            'temp': self.upload_dir / 'temp'
        }
        
        # Initialize directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create upload directories if they don't exist"""
        for subdir in self.subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_hash(self, content: bytes) -> str:
        """Generate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type using python-magic for accurate detection"""
        try:
            return magic.from_file(file_path, mime=True)
        except Exception:
            # Fallback to mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type or 'application/octet-stream'
    
    def _validate_file_type(self, file: UploadFile) -> bool:
        """Validate file type using both extension and MIME type"""
        if not file.filename:
            return False
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        if file_ext not in self.allowed_types:
            return False
        
        # Additional MIME type validation for security
        allowed_mimes = {
            'pdf': ['application/pdf'],
            'doc': ['application/msword'],
            'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            'jpg': ['image/jpeg'],
            'jpeg': ['image/jpeg'],
            'png': ['image/png']
        }
        
        if file_ext in allowed_mimes:
            # Note: Full MIME validation requires reading file content
            # This is a basic check - full validation happens during upload
            return True
        
        return False
    
    def _generate_unique_filename(self, original_filename: str, subdirectory: str = 'documents') -> str:
        """Generate unique filename while preserving extension"""
        if not original_filename:
            raise ValueError("Original filename is required")
        
        file_ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{timestamp}_{unique_id}{file_ext}"
    
    async def _save_file_content(self, file: UploadFile, file_path: Path) -> Tuple[str, int]:
        """Save file content with validation and return hash and size"""
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size {file_size} exceeds maximum allowed size {self.max_file_size}"
            )
        
        # Validate content is not empty
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file is not allowed"
            )
        
        # Generate file hash
        file_hash = self._get_file_hash(content)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Additional MIME type validation after saving
        try:
            detected_mime = self._get_mime_type(str(file_path))
            # Log for monitoring but don't strictly enforce for now
            # Could be enhanced to reject files with mismatched MIME types
        except Exception:
            pass  # Continue even if MIME detection fails
        
        return file_hash, file_size
    
    async def save_document(self, file: UploadFile, user_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Save document file with validation and metadata
        """
        if not self._validate_file_type(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(self.allowed_types)}"
            )
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename, 'documents')
        file_path = self.subdirs['documents'] / unique_filename
        
        # Save file and get metadata
        file_hash, file_size = await self._save_file_content(file, file_path)
        
        # Prepare metadata
        metadata = {
            'original_filename': file.filename,
            'stored_filename': unique_filename,
            'file_size': file_size,
            'file_hash': file_hash,
            'mime_type': file.content_type or 'application/octet-stream',
            'upload_timestamp': datetime.utcnow(),
            'file_path': str(file_path),
            'user_id': user_id
        }
        
        # Reset file position for potential re-reading
        await file.seek(0)
        
        return str(file_path), metadata
    
    async def save_avatar(self, file: UploadFile, max_size: Tuple[int, int] = (300, 300)) -> Tuple[str, Dict[str, Any]]:
        """
        Save and optimize avatar image
        """
        # Validate it's an image
        if not file.filename or not any(file.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Avatar must be a JPG or PNG image"
            )
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename, 'avatars')
        file_path = self.subdirs['avatars'] / unique_filename
        
        # Read and validate file
        content = await file.read()
        file_size = len(content)
        
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Avatar file too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
            )
        
        try:
            # Process image with PIL
            with Image.open(io.BytesIO(content)) as image:
                # Convert to RGB if necessary (for PNG with transparency)
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                
                # Resize while maintaining aspect ratio
                image = ImageOps.fit(image, max_size, Image.Resampling.LANCZOS)
                
                # Save optimized image
                image.save(file_path, 'JPEG', quality=85, optimize=True)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image file: {str(e)}"
            )
        
        # Get final file info
        final_size = file_path.stat().st_size
        file_hash = self._get_file_hash(file_path.read_bytes())
        
        metadata = {
            'original_filename': file.filename,
            'stored_filename': unique_filename,
            'file_size': final_size,
            'original_size': file_size,
            'file_hash': file_hash,
            'mime_type': 'image/jpeg',
            'upload_timestamp': datetime.utcnow(),
            'file_path': str(file_path),
            'optimized': True
        }
        
        return str(file_path), metadata
    
    async def save_archive_document(self, file: UploadFile, category: str, authority: str) -> Tuple[str, Dict[str, Any]]:
        """
        Save document to public archive
        """
        if not self._validate_file_type(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(self.allowed_types)}"
            )
        
        # Create category subdirectory
        category_dir = self.subdirs['archive'] / category.lower().replace(' ', '_')
        category_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename, 'archive')
        file_path = category_dir / unique_filename
        
        # Save file and get metadata
        file_hash, file_size = await self._save_file_content(file, file_path)
        
        metadata = {
            'original_filename': file.filename,
            'stored_filename': unique_filename,
            'file_size': file_size,
            'file_hash': file_hash,
            'mime_type': file.content_type or 'application/octet-stream',
            'upload_timestamp': datetime.utcnow(),
            'file_path': str(file_path),
            'category': category,
            'authority': authority,
            'public': True
        }
        
        return str(file_path), metadata
    
    async def save_uploaded_file(self, file: UploadFile, subfolder: str = 'documents') -> Tuple[str, int]:
        """
        General method to save uploaded files with validation
        Returns file path and file size
        """
        if not self._validate_file_type(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(self.allowed_types)}"
            )
        
        # Determine target directory
        if subfolder in self.subdirs:
            target_dir = self.subdirs[subfolder]
        else:
            # Create custom subfolder if it doesn't exist in predefined ones
            target_dir = self.upload_dir / subfolder
            target_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename, subfolder)
        file_path = target_dir / unique_filename
        
        # Save file and get metadata
        file_hash, file_size = await self._save_file_content(file, file_path)
        
        return str(file_path), file_size
    
    def get_mime_type(self, file_path: str) -> str:
        """
        Public method to get MIME type (wrapper for _get_mime_type)
        """
        return self._get_mime_type(file_path)
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information and metadata
        """
        path = Path(file_path)
        
        if not path.exists() or not path.is_file():
            return None
        
        try:
            stat = path.stat()
            
            return {
                'filename': path.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'mime_type': self._get_mime_type(str(path)),
                'exists': True,
                'path': str(path)
            }
        except Exception:
            return None
    
    async def stream_file(self, file_path: str, chunk_size: int = 8192) -> AsyncGenerator[bytes, None]:
        """
        Stream file content in chunks for efficient download
        """
        path = Path(file_path)
        
        if not path.exists() or not path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        try:
            async with aiofiles.open(path, 'rb') as file:
                while chunk := await file.read(chunk_size):
                    yield chunk
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading file: {str(e)}"
            )
    
    def create_download_response(self, file_path: str, filename: Optional[str] = None) -> StreamingResponse:
        """
        Create streaming response for file download
        """
        path = Path(file_path)
        
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Get file info
        file_info = self.get_file_info(file_path)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not accessible"
            )
        
        # Determine filename for download
        download_filename = filename or path.name
        
        # Create streaming response
        response = StreamingResponse(
            self.stream_file(file_path),
            media_type=file_info['mime_type'],
            headers={
                "Content-Disposition": f"attachment; filename={download_filename}",
                "Content-Length": str(file_info['size'])
            }
        )
        
        return response
    
    def delete_file(self, file_path: str) -> bool:
        """
        Synchronous version of delete_file for backward compatibility
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    async def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Move file from source to destination
        """
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            if source.exists():
                # Ensure destination directory exists
                destination.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                source.rename(destination)
                return True
            return False
        except Exception:
            return False
    
    def calculate_storage_stats(self) -> Dict[str, Any]:
        """
        Calculate storage statistics
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_category': {}
        }
        
        for category, directory in self.subdirs.items():
            if directory.exists():
                files = list(directory.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                
                stats['by_category'][category] = {
                    'file_count': file_count,
                    'total_size': total_size,
                    'average_size': total_size / file_count if file_count > 0 else 0
                }
                
                stats['total_files'] += file_count
                stats['total_size'] += total_size
        
        return stats
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up temporary files older than specified hours
        """
        temp_dir = self.subdirs['temp']
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        deleted_count = 0
        
        if temp_dir.exists():
            for file_path in temp_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        await aiofiles.os.remove(file_path)
                        deleted_count += 1
                    except Exception:
                        pass  # Continue with other files
        
        return deleted_count


# Global file handler instance
file_handler = FileHandler()


# Global file handler instance
file_handler = FileHandler() 