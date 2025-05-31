"""
Document schemas for upload, verification, and archive management.
Provides type-safe validation for all document-related endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration"""
    ID = "id"
    LAND_REGISTRY = "landRegistry"
    INCOME = "income"
    PROPERTY = "property"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Document status enumeration"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DocumentUpload(BaseModel):
    """Schema for document upload"""
    name: str = Field(..., min_length=1, max_length=255)
    type: DocumentType
    description: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: str
    user_id: str
    name: str
    type: DocumentType
    status: DocumentStatus
    file_path: str
    file_size: int
    mime_type: Optional[str] = None
    verification_progress: int
    rejection_reason: Optional[str] = None
    uploaded_at: datetime
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentVerification(BaseModel):
    """Schema for document verification"""
    status: DocumentStatus
    rejection_reason: Optional[str] = None
    verification_progress: int = Field(ge=0, le=100)


class DocumentCategoryCreate(BaseModel):
    """Schema for creating document categories"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None


class DocumentCategoryResponse(BaseModel):
    """Schema for document category response"""
    id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    document_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ArchiveDocumentCreate(BaseModel):
    """Schema for adding documents to archive"""
    title: str = Field(..., min_length=1, max_length=255)
    category_id: str
    authority: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = []


class ArchiveDocumentResponse(BaseModel):
    """Schema for archive document response"""
    id: str
    title: str
    category_id: Optional[str] = None
    authority: str
    description: Optional[str] = None
    file_path: str
    file_size: int
    mime_type: Optional[str] = None
    tags: Optional[List[str]] = []
    download_count: int
    uploaded_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArchiveSearchFilters(BaseModel):
    """Schema for archive search filters"""
    category_id: Optional[str] = None
    authority: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = []


class DocumentAnalysisResponse(BaseModel):
    """Schema for document analysis response"""
    id: str
    document_id: str
    accuracy_score: Optional[str] = None
    extracted_data: Optional[dict] = None
    suggestions: Optional[List[str]] = []
    errors: Optional[List[str]] = []
    analyzed_at: datetime
    analyzed_by_ai: bool

    class Config:
        from_attributes = True 