"""
Document management API routes.
Handles document upload, verification, listing, and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...db.database import get_db
from ...services.document_service import DocumentService
from ...schemas.document import (
    DocumentUpload, DocumentResponse, DocumentVerification,
    DocumentType, DocumentStatus
)
from ...schemas.common import PaginatedResponse, SuccessResponse
from ...core.dependencies import get_current_user, require_official
from ...models.user import User
from ...utils.file_handler import file_handler

router = APIRouter()


def document_to_response_dict(document) -> dict:
    """
    Convert a document object to a dictionary compatible with DocumentResponse schema.
    Handles UUID to string conversion.
    """
    return {
        "id": str(document.id),
        "user_id": str(document.user_id),
        "name": document.name,
        "type": document.type,
        "status": document.status,
        "file_path": document.file_path,
        "file_size": document.file_size,
        "mime_type": document.mime_type,
        "verification_progress": document.verification_progress,
        "rejection_reason": document.rejection_reason,
        "uploaded_at": document.uploaded_at,
        "verified_at": document.verified_at,
        "verified_by": str(document.verified_by) if document.verified_by else None
    }


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    type: DocumentType = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a new document for verification
    """
    document_service = DocumentService(db)
    
    # Create document data from form
    document_data = DocumentUpload(
        name=name,
        type=type,
        description=description
    )
    
    try:
        # Upload document
        document = await document_service.upload_document(
            str(current_user.id), 
            file, 
            document_data
        )
        
        # Convert UUID fields to strings for Pydantic validation
        doc_dict = document_to_response_dict(document)
        
        return DocumentResponse.model_validate(doc_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )


@router.get("/", response_model=List[DocumentResponse])
async def get_user_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get documents for the current user
    """
    document_service = DocumentService(db)
    
    offset = (page - 1) * limit
    documents = await document_service.get_user_documents(
        str(current_user.id), 
        limit=limit, 
        offset=offset
    )
    
    # Convert UUID fields to strings for Pydantic validation
    document_responses = []
    for doc in documents:
        doc_dict = document_to_response_dict(doc)
        document_responses.append(DocumentResponse.model_validate(doc_dict))
    
    return document_responses


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific document by ID
    """
    document_service = DocumentService(db)
    
    document = await document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user owns the document or is an official
    if str(document.user_id) != str(current_user.id) and current_user.role != "official":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Convert UUID fields to strings for Pydantic validation
    doc_dict = document_to_response_dict(document)
    
    return DocumentResponse.model_validate(doc_dict)


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download a document file
    """
    document_service = DocumentService(db)
    
    document = await document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user owns the document or is an official
    if str(document.user_id) != str(current_user.id) and current_user.role != "official":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if file exists
    file_info = file_handler.get_file_info(document.file_path)
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=document.file_path,
        filename=document.name,
        media_type=document.mime_type
    )


@router.put("/{document_id}/verify", response_model=DocumentResponse)
async def verify_document(
    document_id: str,
    verification_notes: str = Form(None),
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a document (officials only)
    """
    document_service = DocumentService(db)
    
    updated_document = await document_service.verify_document(
        document_id=document_id,
        verified_by_id=str(current_user.id),
        notes=verification_notes
    )
    
    if not updated_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Convert UUID fields to strings for Pydantic validation
    doc_dict = document_to_response_dict(updated_document)
    
    return DocumentResponse.model_validate(doc_dict)


@router.put("/{document_id}/reject", response_model=DocumentResponse)
async def reject_document(
    document_id: str,
    rejection_reason: str = Form(...),
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a document (officials only)
    """
    document_service = DocumentService(db)
    
    updated_document = await document_service.reject_document(
        document_id=document_id,
        rejected_by_id=str(current_user.id),
        reason=rejection_reason
    )
    
    if not updated_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Convert UUID fields to strings for Pydantic validation
    doc_dict = document_to_response_dict(updated_document)
    
    return DocumentResponse.model_validate(doc_dict)


@router.delete("/{document_id}", response_model=SuccessResponse)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a document
    """
    document_service = DocumentService(db)
    
    success = await document_service.delete_document(
        document_id, 
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    return SuccessResponse(message="Document deleted successfully")


@router.get("/pending/verification", response_model=List[DocumentResponse])
async def get_pending_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """
    Get documents pending verification (officials only)
    """
    document_service = DocumentService(db)
    
    # This would require additional method in DocumentService
    # For now, we'll return empty list
    # TODO: Implement get_pending_documents in DocumentService
    
    return []


@router.get("/stats/summary", response_model=dict)
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get document statistics for current user
    """
    document_service = DocumentService(db)
    
    # Get user documents
    documents = await document_service.get_user_documents(str(current_user.id), limit=1000)
    
    # Calculate stats
    total = len(documents)
    pending = len([d for d in documents if d.status == "pending"])
    verified = len([d for d in documents if d.status == "verified"])
    rejected = len([d for d in documents if d.status == "rejected"])
    
    return {
        "total_documents": total,
        "pending": pending,
        "verified": verified,
        "rejected": rejected
    } 