"""
Common schemas for responses, pagination, and error handling.
Provides reusable type-safe models across all endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime


T = TypeVar('T')


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    error: str
    details: Optional[str] = None
    status_code: int


class PaginationParams(BaseModel):
    """Pagination parameters schema"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field("asc", description="Sort order: asc or desc")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool


class FileUploadResponse(BaseModel):
    """File upload response schema"""
    file_id: str
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    upload_url: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response schema"""
    status: str
    timestamp: datetime
    version: str
    environment: str
    database_status: str


class SearchParams(BaseModel):
    """Search parameters schema"""
    query: Optional[str] = Field(None, min_length=1, max_length=255)
    filters: Optional[dict] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class BulkOperationResponse(BaseModel):
    """Bulk operation response schema"""
    success_count: int
    error_count: int
    total_count: int
    errors: Optional[List[str]] = [] 