"""
Archive management API routes.
Handles document archive search, categories, downloads, and uploads.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...db.database import get_db
from ...services.document_service import DocumentService
from ...schemas.document import (
    DocumentCategoryCreate, DocumentCategoryResponse,
    ArchiveDocumentCreate, ArchiveDocumentResponse, ArchiveSearchFilters
)
from ...schemas.common import PaginatedResponse, SuccessResponse
from ...core.dependencies import get_current_user, require_official, get_optional_user
from ...models.user import User
from ...utils.file_handler import file_handler

router = APIRouter()


@router.get("/search", response_model=PaginatedResponse[ArchiveDocumentResponse])
async def search_archive_documents(
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    authority: Optional[str] = Query(None, description="Filter by authority"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search documents in the public archive
    """
    document_service = DocumentService(db)
    
    # Parse tags if provided
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Create filters
    filters = ArchiveSearchFilters(
        category_id=category_id,
        authority=authority,
        tags=tag_list if tag_list else None
    )
    
    offset = (page - 1) * limit
    documents, total = await document_service.search_archive(
        query=q,
        filters=filters,
        limit=limit,
        offset=offset
    )
    
    # Calculate pagination info
    pages = (total + limit - 1) // limit
    has_next = page < pages
    has_prev = page > 1
    
    return PaginatedResponse(
        items=[
            ArchiveDocumentResponse(**{
                "id": str(doc.id),
                "title": doc.title,
                "category_id": str(doc.category_id) if doc.category_id else None,
                "authority": doc.authority,
                "description": doc.description,
                "file_path": doc.file_path,
                "file_size": doc.file_size,
                "mime_type": doc.mime_type,
                "tags": doc.tags or [],
                "download_count": doc.download_count,
                "uploaded_by": str(doc.uploaded_by) if doc.uploaded_by else None,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at
            }) for doc in documents
        ],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/categories", response_model=List[DocumentCategoryResponse])
async def get_document_categories(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all document categories
    """
    document_service = DocumentService(db)
    categories = await document_service.get_categories()
    
    # Convert each category to response format with manual UUID conversion
    response_categories = []
    for cat in categories:
        category_data = {
            "id": str(cat.id),
            "name": cat.name,
            "description": cat.description,
            "icon": cat.icon,
            "color": cat.color,
            "document_count": getattr(cat, 'document_count', 0),
            "created_at": cat.created_at
        }
        response_categories.append(DocumentCategoryResponse(**category_data))
    
    return response_categories


@router.post("/categories", response_model=DocumentCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_document_category(
    category_data: DocumentCategoryCreate,
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new document category (officials only)
    """
    document_service = DocumentService(db)
    
    try:
        category = await document_service.create_category(category_data)
        return DocumentCategoryResponse.model_validate(category)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category creation failed: {str(e)}"
        )


@router.get("/categories/{category_id}/documents", response_model=List[ArchiveDocumentResponse])
async def get_documents_by_category(
    category_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get documents in a specific category
    """
    document_service = DocumentService(db)
    
    offset = (page - 1) * limit
    documents = await document_service.get_documents_by_category(
        category_id, 
        limit=limit, 
        offset=offset
    )
    
    return [
        ArchiveDocumentResponse(**{
            "id": str(doc.id),
            "title": doc.title,
            "category_id": str(doc.category_id) if doc.category_id else None,
            "authority": doc.authority,
            "description": doc.description,
            "file_path": doc.file_path,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "tags": doc.tags or [],
            "download_count": doc.download_count,
            "uploaded_by": str(doc.uploaded_by) if doc.uploaded_by else None,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at
        }) for doc in documents
    ]


@router.get("/documents/{document_id}", response_model=ArchiveDocumentResponse)
async def get_archive_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get archive document details by ID
    """
    document_service = DocumentService(db)
    
    document = await document_service.get_archive_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return ArchiveDocumentResponse(**{
        "id": str(document.id),
        "title": document.title,
        "category_id": str(document.category_id) if document.category_id else None,
        "authority": document.authority,
        "description": document.description,
        "file_path": document.file_path,
        "file_size": document.file_size,
        "mime_type": document.mime_type,
        "tags": document.tags or [],
        "download_count": document.download_count,
        "uploaded_by": str(document.uploaded_by) if document.uploaded_by else None,
        "created_at": document.created_at,
        "updated_at": document.updated_at
    })


@router.get("/documents/{document_id}/download")
async def download_archive_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download an archive document
    """
    document_service = DocumentService(db)
    
    document = await document_service.get_archive_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if file exists
    file_info = file_handler.get_file_info(document.file_path)
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Increment download count
    await document_service.increment_download_count(document_id)
    
    return FileResponse(
        path=document.file_path,
        filename=document.title,
        media_type=document.mime_type
    )


@router.post("/documents", response_model=ArchiveDocumentResponse, status_code=status.HTTP_201_CREATED)
async def add_document_to_archive(
    file: UploadFile = File(...),
    title: str = Form(...),
    category_id: str = Form(...),
    authority: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a document to the public archive (officials only)
    """
    document_service = DocumentService(db)
    
    # Parse tags if provided
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Create archive document data
    archive_data = ArchiveDocumentCreate(
        title=title,
        category_id=category_id,
        authority=authority,
        description=description,
        tags=tag_list
    )
    
    try:
        # Add to archive
        document = await document_service.add_to_archive(
            file,
            archive_data,
            str(current_user.id)
        )
        
        # Convert UUIDs to strings for Pydantic validation
        archive_response_data = {
            "id": str(document.id),
            "title": document.title,
            "category_id": str(document.category_id) if document.category_id else None,
            "authority": document.authority,
            "description": document.description,
            "file_path": document.file_path,
            "file_size": document.file_size,
            "mime_type": document.mime_type,
            "tags": document.tags or [],
            "download_count": document.download_count,
            "uploaded_by": str(document.uploaded_by) if document.uploaded_by else None,
            "created_at": document.created_at,
            "updated_at": document.updated_at
        }
        
        return ArchiveDocumentResponse(**archive_response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Archive upload failed: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_archive_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get archive statistics
    """
    document_service = DocumentService(db)
    
    # Get all documents for stats
    documents, total = await document_service.search_archive(limit=10000)
    categories = await document_service.get_categories()
    
    # Calculate stats by category
    category_stats = {}
    for doc in documents:
        cat_id = str(doc.category_id) if doc.category_id else "uncategorized"
        if cat_id not in category_stats:
            category_stats[cat_id] = 0
        category_stats[cat_id] += 1
    
    # Calculate total downloads
    total_downloads = sum(doc.download_count for doc in documents)
    
    return {
        "total_documents": total,
        "total_categories": len(categories),
        "total_downloads": total_downloads,
        "documents_by_category": category_stats
    } 