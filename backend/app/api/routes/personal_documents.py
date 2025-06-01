"""
Personal Documents API Routes for Romanian Public Administration Platform
Handles personal document upload, scanning, and AI-powered metadata extraction.
Documents are stored for individual users only, not in the global archive.
"""

import os
import subprocess
import tempfile
import shutil
import datetime
import json
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ocr_processor import LegalDocumentOCR
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.services.document_service import DocumentService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# NAPS2 scanner paths (Windows)
NAPS2_PATHS = [
    r"C:\Program Files\NAPS2\NAPS2.Console.exe",
    r"C:\Program Files (x86)\NAPS2\NAPS2.Console.exe"
]

# Initialize OCR processor
ocr_processor = None
OCR_ENABLED = False

try:
    ocr_processor = LegalDocumentOCR()
    OCR_ENABLED = True
    logger.info("Personal documents OCR processor initialized successfully")
except Exception as e:
    logger.warning(f"Personal documents OCR processor initialization failed: {e}")


def find_naps2():
    """Find NAPS2 scanner software installation"""
    for path in NAPS2_PATHS:
        if os.path.exists(path):
            return path
    return None


# Pydantic models for personal documents
class PersonalDocumentMetadata(BaseModel):
    id: str
    extractedData: Dict[str, Optional[str]] = {}
    confidence: float = 0.0
    filePath: str
    fileSize: int
    processingDate: str


class PersonalDocumentResponse(BaseModel):
    success: bool
    metadata: Optional[PersonalDocumentMetadata] = None
    error: Optional[str] = None


class DocumentTypeRequest(BaseModel):
    documentType: str


@router.get("/info")
async def get_personal_documents_info():
    """Get personal documents service information"""
    naps2_path = find_naps2()
    
    return {
        "message": "Personal Documents Service - AI-Powered Document Processing",
        "version": "1.0.0",
        "features": {
            "personal_upload": OCR_ENABLED,
            "personal_scan": OCR_ENABLED and naps2_path is not None,
            "ai_extraction": OCR_ENABLED,
            "metadata_storage": True
        },
        "naps2_found": naps2_path is not None,
        "naps2_path": naps2_path,
        "ocr_enabled": OCR_ENABLED,
        "gemini_model": "gemini-1.5-flash" if OCR_ENABLED else None,
        "supported_documents": [
            "Carte de identitate",
            "Pașaport",
            "Permis de conducere", 
            "Certificat de naștere",
            "Certificat de căsătorie",
            "Alte documente de identitate"
        ]
    }


@router.post("/upload-and-process", response_model=PersonalDocumentResponse)
async def upload_and_process_personal_document(
    file: UploadFile = File(...),
    documentType: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a personal document with AI metadata extraction"""
    if not OCR_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="OCR service not available. Please set GEMINI_API_KEY environment variable."
        )
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Only JPEG, PNG, WebP images and PDF files are accepted"
        )
    
    if file.size and file.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=400, 
            detail="File size exceeds 10MB limit"
        )
    
    try:
        # Create user documents directory
        user_docs_dir = Path("uploads/documents") / str(current_user.id)
        user_docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process document with OCR
            if file.content_type == "application/pdf":
                ocr_result = ocr_processor.process_pdf_file(temp_file_path, documentType)
            else:
                ocr_result = ocr_processor.process_image_file(temp_file_path, documentType)
            
            if not ocr_result["success"]:
                raise HTTPException(
                    status_code=500, 
                    detail=f"OCR processing failed: {ocr_result.get('error')}"
                )
            
            # Extract personal document metadata using specialized prompt
            personal_metadata = await extract_personal_document_metadata(
                ocr_result["transcribed_text"], 
                documentType
            )
            
            # Generate unique filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = Path(file.filename).suffix
            safe_filename = f"personal_{documentType}_{timestamp}{file_extension}"
            final_path = user_docs_dir / safe_filename
            
            # Move file to final location
            shutil.move(temp_file_path, str(final_path))
            
            # Store in database using document service
            document_service = DocumentService(db)
            
            # Map document type to supported types
            doc_type_mapping = {
                "id": "id",
                "passport": "other", 
                "license": "other",
                "birth": "other",
                "marriage": "other"
            }
            
            # Create document record
            db_document = Document(
                user_id=current_user.id,
                name=f"{documentType.title()} - {timestamp}",
                type=doc_type_mapping.get(documentType, "other"),
                file_path=str(final_path),
                file_size=final_path.stat().st_size,
                mime_type=file.content_type,
                verification_progress=100,  # Personal docs are auto-"verified"
                status="verified"
            )
            
            db.add(db_document)
            await db.commit()
            await db.refresh(db_document)
            
            # Prepare response
            response_metadata = PersonalDocumentMetadata(
                id=str(db_document.id),
                extractedData={k: v for k, v in personal_metadata.items() if k != "confidence_score"},
                confidence=personal_metadata.get("confidence_score", 0.8),
                filePath=str(final_path),
                fileSize=final_path.stat().st_size,
                processingDate=datetime.datetime.now().isoformat()
            )
            
            logger.info(f"Personal document processed successfully for user {current_user.id}")
            
            return PersonalDocumentResponse(
                success=True,
                metadata=response_metadata
            )
            
        finally:
            # Clean up temp file if it still exists
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error processing personal document: {str(e)}")
        return PersonalDocumentResponse(
            success=False,
            error=str(e)
        )


@router.post("/scan", response_model=PersonalDocumentResponse)
async def scan_personal_document(
    request: DocumentTypeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Scan a personal document from printer and process with AI"""
    naps2_path = find_naps2()
    if not naps2_path:
        raise HTTPException(
            status_code=500,
            detail="NAPS2 not found. Please ensure NAPS2 is installed."
        )
    
    if not OCR_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="OCR service not available. Please set GEMINI_API_KEY environment variable."
        )
    
    # Create user documents directory
    user_docs_dir = Path("uploads/documents") / str(current_user.id)
    user_docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temporary scans directory
    temp_scans_dir = Path("uploads/temp") / str(current_user.id)
    temp_scans_dir.mkdir(parents=True, exist_ok=True)
    
    # Use timestamp-based filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_pdf_path = temp_scans_dir / f"personal_scan_{timestamp}.pdf"
    
    try:
        command = [
            naps2_path,
            "-o", str(temp_pdf_path),
            "--verbose"
        ]
        
        logger.info(f"Executing NAPS2 command: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or f'NAPS2 exited with code {result.returncode}'
            logger.error(f"NAPS2 failed with: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Scanning failed: {error_msg}"
            )
        
        if not temp_pdf_path.exists() or temp_pdf_path.stat().st_size == 0:
            raise HTTPException(
                status_code=500,
                detail="Scan completed but no valid PDF file was created"
            )
        
        logger.info(f"Scan successful: {temp_pdf_path}")
        
        try:
            # Process scanned PDF with OCR
            ocr_result = ocr_processor.process_pdf_file(str(temp_pdf_path), request.documentType)
            
            if not ocr_result["success"]:
                raise HTTPException(
                    status_code=500, 
                    detail=f"OCR processing failed: {ocr_result.get('error')}"
                )
            
            # Extract personal document metadata
            personal_metadata = await extract_personal_document_metadata(
                ocr_result["transcribed_text"], 
                request.documentType
            )
            
            # Move to final location
            final_filename = f"personal_{request.documentType}_scanned_{timestamp}.pdf"
            final_path = user_docs_dir / final_filename
            shutil.move(str(temp_pdf_path), str(final_path))
            
            # Store in database
            document_service = DocumentService(db)
            
            doc_type_mapping = {
                "id": "id",
                "passport": "other",
                "license": "other", 
                "birth": "other",
                "marriage": "other"
            }
            
            db_document = Document(
                user_id=current_user.id,
                name=f"{request.documentType.title()} Scanat - {timestamp}",
                type=doc_type_mapping.get(request.documentType, "other"),
                file_path=str(final_path),
                file_size=final_path.stat().st_size,
                mime_type="application/pdf",
                verification_progress=100,
                status="verified"
            )
            
            db.add(db_document)
            await db.commit()
            await db.refresh(db_document)
            
            # Prepare response
            response_metadata = PersonalDocumentMetadata(
                id=str(db_document.id),
                extractedData={k: v for k, v in personal_metadata.items() if k != "confidence_score"},
                confidence=personal_metadata.get("confidence_score", 0.8),
                filePath=str(final_path),
                fileSize=final_path.stat().st_size,
                processingDate=datetime.datetime.now().isoformat()
            )
            
            logger.info(f"Personal document scanned and processed for user {current_user.id}")
            
            return PersonalDocumentResponse(
                success=True,
                metadata=response_metadata
            )
            
        except Exception as ocr_error:
            logger.error(f"OCR processing failed: {str(ocr_error)}")
            return PersonalDocumentResponse(
                success=False,
                error=f"Document scanned but processing failed: {str(ocr_error)}"
            )
        
    except subprocess.TimeoutExpired:
        logger.error("NAPS2 command timed out")
        if temp_pdf_path.exists():
            temp_pdf_path.unlink()
        raise HTTPException(
            status_code=500,
            detail="Scan operation timed out"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in personal document scan: {str(e)}")
        if temp_pdf_path.exists():
            temp_pdf_path.unlink()
        return PersonalDocumentResponse(
            success=False,
            error=str(e)
        )


async def extract_personal_document_metadata(text: str, document_type: str) -> Dict[str, Any]:
    """
    Extract personal document metadata using the OCR processor's existing method
    Simplified to extract only the most important metadata fields
    """
    if not OCR_ENABLED or not ocr_processor:
        return {
            "nume": "Nu s-a putut extrage",
            "confidence_score": 0.0
        }
    
    try:
        # Use the existing metadata extraction method from OCR processor
        metadata = await ocr_processor.extract_metadata_from_text(text, document_type)
        
        # Simplify to only the most important fields for personal documents
        simplified_metadata = {
            "nume": metadata.get("title", "Document fără titlu"),
            "tipDocument": metadata.get("category", document_type),
            "autoritate": metadata.get("authority", "Nespecificat"),
            "dataDocument": metadata.get("issue_date"),
            "observatii": metadata.get("description", "Fără descriere"),
            "confidence_score": metadata.get("confidence_score", 0.0)
        }
        
        logger.info(f"Successfully extracted simplified personal document metadata: {list(simplified_metadata.keys())}")
        return simplified_metadata
        
    except Exception as e:
        logger.error(f"Error extracting personal document metadata: {str(e)}")
        return {
            "nume": "Eroare la procesare",
            "observatii": f"Eroare: {str(e)}",
            "confidence_score": 0.0
        }


@router.get("/user/{user_id}/documents")
async def get_user_personal_documents(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all personal documents for a user (only own documents)"""
    # Users can only access their own documents
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own documents."
        )
    
    try:
        document_service = DocumentService(db)
        documents = await document_service.get_user_documents(user_id)
        
        return {
            "success": True,
            "documents": [
                {
                    "id": str(doc.id),
                    "name": doc.name,
                    "type": doc.type,
                    "status": doc.status,
                    "file_size": doc.file_size,
                    "uploaded_at": doc.uploaded_at.isoformat(),
                    "verification_progress": doc.verification_progress
                }
                for doc in documents
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {str(e)}"
        ) 