"""
Document models for user document management and archive.
Includes documents, categories, archive documents, and analysis.
"""

from sqlalchemy import Column, String, DateTime, Text, BigInteger, Integer, Boolean, ForeignKey, CheckConstraint, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship

from ..db.database import Base


class Document(Base):
    """
    User uploaded documents for verification
    """
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(20), server_default="pending")
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100))
    verification_progress = Column(Integer, server_default="0")
    rejection_reason = Column(Text)
    uploaded_at = Column(DateTime, server_default=func.current_timestamp())
    verified_at = Column(DateTime)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Add check constraints
    __table_args__ = (
        CheckConstraint("type IN ('id', 'landRegistry', 'income', 'property', 'other')", name='documents_type_check'),
        CheckConstraint("status IN ('pending', 'verified', 'rejected')", name='documents_status_check'),
    )


class DocumentCategory(Base):
    """
    Categories for archive documents
    """
    __tablename__ = "document_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(100))
    color = Column(String(7), server_default="'#3B82F6'")  # Hex color code
    created_at = Column(DateTime, server_default=func.current_timestamp())


class ArchiveDocument(Base):
    """
    Public archive documents accessible to all users
    """
    __tablename__ = "archive_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title = Column(String(255), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("document_categories.id"))
    authority = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100))
    tags = Column(ARRAY(Text))  # PostgreSQL array for tags
    download_count = Column(Integer, server_default="0")
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp())


class DocumentAnalysis(Base):
    """
    AI analysis results for documents
    """
    __tablename__ = "document_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    accuracy_score = Column(String)  # DECIMAL(5, 4) equivalent
    extracted_data = Column(JSONB)
    suggestions = Column(ARRAY(Text))
    errors = Column(ARRAY(Text))
    analyzed_at = Column(DateTime, server_default=func.current_timestamp())
    analyzed_by_ai = Column(Boolean, server_default="true") 