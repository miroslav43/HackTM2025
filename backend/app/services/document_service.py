"""
Document service for managing user documents and archive.
Handles document upload, verification, categorization, and archive operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Tuple
from uuid import UUID
from fastapi import UploadFile, HTTPException, status
from datetime import datetime

from ..models.document import Document, DocumentCategory, ArchiveDocument, DocumentAnalysis
from ..schemas.document import (
    DocumentUpload, DocumentResponse, DocumentVerification,
    DocumentCategoryCreate, DocumentCategoryResponse,
    ArchiveDocumentCreate, ArchiveDocumentResponse, ArchiveSearchFilters
)
from ..utils.file_handler import file_handler
from ..utils.email_service import email_service


class DocumentService:
    """
    Service class for document-related business logic
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def upload_document(
        self, 
        user_id: str, 
        file: UploadFile, 
        document_data: DocumentUpload
    ) -> Document:
        """
        Upload and save a user document
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        # Save file to disk
        file_path, file_size = await file_handler.save_uploaded_file(
            file, subfolder="documents"
        )
        
        # Get MIME type
        mime_type = file_handler.get_mime_type(file_path)
        
        try:
            # Create document record
            db_document = Document(
                user_id=user_uuid,
                name=document_data.name,
                type=document_data.type.value,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                verification_progress=0
            )
            
            self.db.add(db_document)
            await self.db.commit()
            await self.db.refresh(db_document)
            
            return db_document
            
        except Exception as e:
            # Clean up file on database error
            file_handler.delete_file(file_path)
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document upload failed: {str(e)}"
            )
    
    async def get_user_documents(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Document]:
        """
        Get documents for a specific user
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return []
        
        stmt = (
            select(Document)
            .where(Document.user_id == user_uuid)
            .order_by(Document.uploaded_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """
        Get document by ID
        """
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            return None
        
        stmt = select(Document).where(Document.id == doc_uuid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def verify_document(
        self, 
        document_id: str, 
        verified_by_id: str,
        notes: Optional[str] = None
    ) -> Optional[Document]:
        """
        Verify a document (officials only)
        """
        document = await self.get_document_by_id(document_id)
        if not document:
            return None
        
        # Get verifier user
        verifier_stmt = select(User).where(User.id == UUID(verified_by_id))
        verifier_result = await self.db.execute(verifier_stmt)
        verifier = verifier_result.scalar_one_or_none()
        
        if not verifier:
            return None
        
        # Update document status
        stmt = (
            update(Document)
            .where(Document.id == UUID(document_id))
            .values(
                status="verified",
                verified_by=UUID(verified_by_id),
                verified_at=datetime.utcnow(),
                verification_notes=notes,
                updated_at=datetime.utcnow()
            )
            .returning(Document)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        updated_document = result.scalar_one_or_none()
        
        # Send email notification
        if updated_document:
            # Get document owner for email
            owner_stmt = select(User).where(User.id == updated_document.user_id)
            owner_result = await self.db.execute(owner_stmt)
            owner = owner_result.scalar_one_or_none()
            
            if owner:
                try:
                    await email_service.send_document_verification_email(
                        user_email=owner.email,
                        user_name=f"{owner.first_name} {owner.last_name}".strip() or owner.email,
                        document_name=updated_document.name,
                        verified_by=f"{verifier.first_name} {verifier.last_name}".strip() or verifier.email,
                        verification_notes=notes
                    )
                except Exception as e:
                    # Log email error but don't fail the verification
                    pass
        
        return updated_document
    
    async def reject_document(
        self, 
        document_id: str, 
        rejected_by_id: str,
        reason: str
    ) -> Optional[Document]:
        """
        Reject a document (officials only)
        """
        document = await self.get_document_by_id(document_id)
        if not document:
            return None
        
        # Get rejector user
        rejector_stmt = select(User).where(User.id == UUID(rejected_by_id))
        rejector_result = await self.db.execute(rejector_stmt)
        rejector = rejector_result.scalar_one_or_none()
        
        if not rejector:
            return None
        
        # Update document status
        stmt = (
            update(Document)
            .where(Document.id == UUID(document_id))
            .values(
                status="rejected",
                verified_by=UUID(rejected_by_id),
                verified_at=datetime.utcnow(),
                verification_notes=reason,
                updated_at=datetime.utcnow()
            )
            .returning(Document)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        updated_document = result.scalar_one_or_none()
        
        # Send email notification
        if updated_document:
            # Get document owner for email
            owner_stmt = select(User).where(User.id == updated_document.user_id)
            owner_result = await self.db.execute(owner_stmt)
            owner = owner_result.scalar_one_or_none()
            
            if owner:
                try:
                    await email_service.send_document_rejection_email(
                        user_email=owner.email,
                        user_name=f"{owner.first_name} {owner.last_name}".strip() or owner.email,
                        document_name=updated_document.name,
                        rejected_by=f"{rejector.first_name} {rejector.last_name}".strip() or rejector.email,
                        rejection_reason=reason
                    )
                except Exception as e:
                    # Log email error but don't fail the rejection
                    pass
        
        return updated_document
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete a document (owner only)
        """
        try:
            doc_uuid = UUID(document_id)
            user_uuid = UUID(user_id)
        except ValueError:
            return False
        
        # Get document first to check ownership and get file path
        document = await self.get_document_by_id(document_id)
        if not document or str(document.user_id) != user_id:
            return False
        
        # Delete file from disk
        file_handler.delete_file(document.file_path)
        
        # Delete from database
        stmt = delete(Document).where(
            and_(Document.id == doc_uuid, Document.user_id == user_uuid)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    # === DOCUMENT CATEGORIES ===
    
    async def create_category(
        self, 
        category_data: DocumentCategoryCreate
    ) -> DocumentCategory:
        """
        Create a new document category
        """
        db_category = DocumentCategory(
            name=category_data.name,
            description=category_data.description,
            icon=category_data.icon
        )
        
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        
        return db_category
    
    async def get_categories(self) -> List[DocumentCategory]:
        """
        Get all document categories with document counts
        """
        # Query categories with document counts
        stmt = (
            select(
                DocumentCategory,
                func.count(ArchiveDocument.id).label('document_count')
            )
            .outerjoin(ArchiveDocument, DocumentCategory.id == ArchiveDocument.category_id)
            .group_by(DocumentCategory.id)
            .order_by(DocumentCategory.name)
        )
        
        result = await self.db.execute(stmt)
        categories_with_counts = result.all()
        
        # Create category objects with document count
        categories = []
        for category, doc_count in categories_with_counts:
            # Add document_count as attribute to the category object
            category.document_count = doc_count
            categories.append(category)
        
        return categories
    
    # === ARCHIVE DOCUMENTS ===
    
    async def add_to_archive(
        self, 
        file: UploadFile, 
        archive_data: ArchiveDocumentCreate,
        uploaded_by_id: str
    ) -> ArchiveDocument:
        """
        Add document to public archive (officials only)
        """
        try:
            uploader_uuid = UUID(uploaded_by_id)
            category_uuid = UUID(archive_data.category_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format"
            )
        
        # Save file to archive directory
        file_path, file_size = await file_handler.save_uploaded_file(
            file, subfolder="archive"
        )
        
        # Get MIME type
        mime_type = file_handler.get_mime_type(file_path)
        
        try:
            # Create archive document record
            db_archive_doc = ArchiveDocument(
                title=archive_data.title,
                category_id=category_uuid,
                authority=archive_data.authority,
                description=archive_data.description,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                tags=archive_data.tags or [],
                uploaded_by=uploader_uuid
            )
            
            self.db.add(db_archive_doc)
            await self.db.commit()
            await self.db.refresh(db_archive_doc)
            
            return db_archive_doc
            
        except Exception as e:
            # Clean up file on error
            file_handler.delete_file(file_path)
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Archive upload failed: {str(e)}"
            )
    
    async def search_archive(
        self, 
        query: Optional[str] = None,
        filters: Optional[ArchiveSearchFilters] = None,
        limit: int = 50, 
        offset: int = 0
    ) -> Tuple[List[ArchiveDocument], int]:
        """
        Search documents in archive with filters
        """
        # Build base query
        stmt = select(ArchiveDocument)
        count_stmt = select(func.count(ArchiveDocument.id))
        
        # Apply filters
        conditions = []
        
        if query:
            # Search in title, description, authority (removed expensive tags search for performance)
            search_condition = or_(
                ArchiveDocument.title.ilike(f"%{query}%"),
                ArchiveDocument.description.ilike(f"%{query}%"),
                ArchiveDocument.authority.ilike(f"%{query}%")
            )
            conditions.append(search_condition)
        
        if filters:
            if filters.category_id:
                try:
                    category_uuid = UUID(filters.category_id)
                    conditions.append(ArchiveDocument.category_id == category_uuid)
                except ValueError:
                    pass
            
            if filters.authority:
                conditions.append(ArchiveDocument.authority.ilike(f"%{filters.authority}%"))
            
            if filters.date_from:
                conditions.append(ArchiveDocument.created_at >= filters.date_from)
            
            if filters.date_to:
                conditions.append(ArchiveDocument.created_at <= filters.date_to)
            
            if filters.tags:
                for tag in filters.tags:
                    conditions.append(ArchiveDocument.tags.any(tag))
        
        # Apply conditions
        if conditions:
            where_clause = and_(*conditions)
            stmt = stmt.where(where_clause)
            count_stmt = count_stmt.where(where_clause)
        
        # Get total count
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        stmt = (
            stmt
            .order_by(ArchiveDocument.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        # Execute query
        result = await self.db.execute(stmt)
        documents = list(result.scalars().all())
        
        return documents, total
    
    async def get_archive_document_by_id(self, document_id: str) -> Optional[ArchiveDocument]:
        """
        Get archive document by ID
        """
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            return None
        
        stmt = select(ArchiveDocument).where(ArchiveDocument.id == doc_uuid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def increment_download_count(self, document_id: str) -> bool:
        """
        Increment download count for archive document
        """
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            return False
        
        stmt = (
            update(ArchiveDocument)
            .where(ArchiveDocument.id == doc_uuid)
            .values(download_count=ArchiveDocument.download_count + 1)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def get_documents_by_category(
        self, 
        category_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ArchiveDocument]:
        """
        Get archive documents by category
        """
        try:
            category_uuid = UUID(category_id)
        except ValueError:
            return []
        
        stmt = (
            select(ArchiveDocument)
            .where(ArchiveDocument.category_id == category_uuid)
            .order_by(ArchiveDocument.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all()) 