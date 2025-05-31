"""
Auto-Archive Routes for Romanian Public Administration Platform
Provides automated document scanning, OCR processing, and archival with AI-powered metadata extraction.
Includes smart category matching and automatic archive integration.
"""

import os
import subprocess
import tempfile
import shutil
import datetime
import json
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ocr_processor import LegalDocumentOCR
from app.services.smart_category_service import SmartCategoryService
from app.db.database import get_db
from app.core.dependencies import get_current_user, require_official
from app.models.user import User
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
    logger.info("OCR processor initialized successfully")
except Exception as e:
    logger.warning(f"OCR processor initialization failed: {e}")


def find_naps2():
    """Find NAPS2 scanner software installation"""
    for path in NAPS2_PATHS:
        if os.path.exists(path):
            return path
    return None


# Pydantic models for auto-archive functionality
class AutoArchiveMetadata(BaseModel):
    title: str = "Document fără titlu"  # Denumire document
    document_number: Optional[str] = None  # Număr document
    category: str = "Document"  # Categorie
    authority: str = "Autoritate publică"  # Autoritate emitentă
    issue_date: Optional[str] = None  # Data documentului
    tags: List[str] = []  # Etichete (separate prin virgulă)
    description: str = "Document oficial"  # Descriere
    confidence_score: float = 0.0  # Scor încredere AI
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create AutoArchiveMetadata from dict with safe defaults"""
        return cls(
            title=data.get("title") or "Document fără titlu",
            document_number=data.get("document_number"),
            category=data.get("category") or "Document", 
            authority=data.get("authority") or "Autoritate publică",
            issue_date=data.get("issue_date"),
            tags=data.get("tags") or [],
            description=data.get("description") or "Document oficial",
            confidence_score=data.get("confidence_score") or 0.0
        )


class AutoArchiveResponse(BaseModel):
    success: bool
    document_id: Optional[str] = None
    metadata: Optional[AutoArchiveMetadata] = None
    file_path: Optional[str] = None
    error: Optional[str] = None


class DocumentTypeRequest(BaseModel):
    document_type: Optional[str] = None


@router.get("/info")
async def get_auto_archive_info():
    """Get auto-archive service information and capabilities"""
    naps2_path = find_naps2()
    
    return {
        "message": "Auto-Archive Service - AI-Powered Document Processing",
        "version": "2.1.0",
        "features": {
            "basic_scanning": True,
            "ocr_processing": OCR_ENABLED,
            "auto_archive_upload": OCR_ENABLED,
            "auto_archive_scan": OCR_ENABLED and naps2_path is not None
        },
        "naps2_found": naps2_path is not None,
        "naps2_path": naps2_path,
        "ocr_enabled": OCR_ENABLED,
        "gemini_model": "gemini-1.5-flash" if OCR_ENABLED else None,
        "directories": {
            "scans": "scans",
            "archive": "archive"
        },
        "endpoints": {
            "auto_archive_upload": "/api/auto-archive/upload-pdf",
            "auto_archive_scan": "/api/auto-archive/scan-and-archive",
            "list_archived": "/api/auto-archive/list",
            "get_metadata": "/api/auto-archive/metadata/{doc_id}",
            "category_stats": "/api/auto-archive/category-stats"
        },
        "authentication_required": True,
        "required_role": "official"
    }


@router.post("/upload-pdf", response_model=AutoArchiveResponse)
async def auto_archive_upload_pdf(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """Upload PDF and auto-generate archival metadata using Gemini AI with smart categorization"""
    if not OCR_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="OCR service not available. Please set GEMINI_API_KEY environment variable."
        )
    
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    if file.size and file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process PDF with OCR
            ocr_result = ocr_processor.process_pdf_file(temp_file_path, document_type)
            
            if not ocr_result["success"]:
                raise HTTPException(status_code=500, detail=f"OCR processing failed: {ocr_result.get('error')}")
            
            # Extract metadata from OCR text
            metadata = await ocr_processor.extract_metadata_from_text(
                ocr_result["transcribed_text"], 
                document_type
            )
            
            # Create archive directory if it doesn't exist
            archive_dir = Path("uploads/archive")
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"auto_archive_{timestamp}_{file.filename}"
            archive_path = archive_dir / safe_filename
            
            # Copy file to archive
            shutil.copy2(temp_file_path, str(archive_path))
            
            # Initialize Smart Category Service
            smart_category_service = SmartCategoryService(db)
            
            # Auto-archive with smart categorization
            archive_doc_id = await smart_category_service.auto_archive_document(
                file_path=str(archive_path),
                extracted_metadata=metadata,
                uploaded_by_id=str(current_user.id)
            )
            
            # Store metadata in OCR database for compatibility
            ocr_doc_id = ocr_processor._store_in_database(
                filename=safe_filename,
                document_type=metadata.get("category", "Document"),
                transcribed_text=ocr_result["transcribed_text"],
                original_format="PDF"
            )
            
            logger.info(f"Auto-archive completed: Archive ID: {archive_doc_id}, OCR ID: {ocr_doc_id}")
            
            return AutoArchiveResponse(
                success=True,
                document_id=archive_doc_id,  # Return archive document ID
                metadata=AutoArchiveMetadata.from_dict(metadata),
                file_path=str(archive_path)
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error in auto-archive upload: {str(e)}")
        return AutoArchiveResponse(
            success=False,
            error=str(e)
        )


@router.post("/scan-and-archive", response_model=AutoArchiveResponse)
async def auto_archive_scan_from_printer(
    background_tasks: BackgroundTasks,
    document_type: Optional[str] = Form(None),
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """Scan from printer, perform OCR, extract metadata, and add to archive automatically with smart categorization"""
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
    
    # Create scans directory if it doesn't exist
    scans_dir = Path("uploads/scans")
    scans_dir.mkdir(parents=True, exist_ok=True)
    
    # Create archive directory if it doesn't exist
    archive_dir = Path("uploads/archive")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Use timestamp-based filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_pdf_path = scans_dir / f"auto_scan_{timestamp}.pdf"
    
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
                detail=f"NAPS2 scan failed: {error_msg}"
            )
        
        if not temp_pdf_path.exists() or temp_pdf_path.stat().st_size == 0:
            raise HTTPException(
                status_code=500,
                detail="Scan completed but no valid PDF file was created"
            )
        
        logger.info(f"Scan successful: {temp_pdf_path}")
        
        try:
            # Process scanned PDF with OCR
            ocr_result = ocr_processor.process_pdf_file(str(temp_pdf_path), document_type)
            
            if not ocr_result["success"]:
                raise HTTPException(status_code=500, detail=f"OCR processing failed: {ocr_result.get('error')}")
            
            # Extract metadata from OCR text
            metadata = await ocr_processor.extract_metadata_from_text(
                ocr_result["transcribed_text"], 
                document_type
            )
            
            # Generate archive filename
            archive_filename = f"scanned_archive_{timestamp}.pdf"
            archive_path = archive_dir / archive_filename
            
            # Move file to archive
            shutil.move(str(temp_pdf_path), str(archive_path))
            
            # Initialize Smart Category Service
            smart_category_service = SmartCategoryService(db)
            
            # Auto-archive with smart categorization
            archive_doc_id = await smart_category_service.auto_archive_document(
                file_path=str(archive_path),
                extracted_metadata=metadata,
                uploaded_by_id=str(current_user.id)
            )
            
            # Store metadata in OCR database for compatibility
            ocr_doc_id = ocr_processor._store_in_database(
                filename=archive_filename,
                document_type=metadata.get("category", "Document"),
                transcribed_text=ocr_result["transcribed_text"],
                original_format="PDF_SCANNED"
            )
            
            logger.info(f"Auto-archive scan completed: Archive ID: {archive_doc_id}, OCR ID: {ocr_doc_id}")
            
            return AutoArchiveResponse(
                success=True,
                document_id=archive_doc_id,  # Return archive document ID
                metadata=AutoArchiveMetadata.from_dict(metadata),
                file_path=str(archive_path)
            )
            
        except Exception as ocr_error:
            # If OCR fails, still keep the scanned file but with basic metadata
            logger.error(f"OCR processing failed: {str(ocr_error)}")
            
            archive_filename = f"scanned_basic_{timestamp}.pdf"
            archive_path = archive_dir / archive_filename
            shutil.move(str(temp_pdf_path), str(archive_path))
            
            basic_metadata = {
                "title": f"Document scanat {timestamp}",
                "category": "Scanat",
                "authority": "Autoritate publică",
                "description": "Document scanat fără procesare OCR",
                "tags": ["scanat", "document"],
                "confidence_score": 0.0
            }
            
            # Try to add to archive even without OCR
            try:
                smart_category_service = SmartCategoryService(db)
                archive_doc_id = await smart_category_service.auto_archive_document(
                    file_path=str(archive_path),
                    extracted_metadata=basic_metadata,
                    uploaded_by_id=str(current_user.id)
                )
                
                return AutoArchiveResponse(
                    success=True,
                    document_id=archive_doc_id,
                    metadata=AutoArchiveMetadata.from_dict(basic_metadata),
                    file_path=str(archive_path)
                )
            except Exception as archive_error:
                logger.error(f"Failed to archive even basic document: {str(archive_error)}")
                return AutoArchiveResponse(
                    success=True,
                    document_id=None,
                    metadata=AutoArchiveMetadata.from_dict(basic_metadata),
                    file_path=str(archive_path)
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
        logger.error(f"Unexpected error in scan and archive: {str(e)}")
        if temp_pdf_path.exists():
            temp_pdf_path.unlink()
        return AutoArchiveResponse(
            success=False,
            error=str(e)
        )


@router.get("/metadata/{doc_id}")
async def get_auto_archive_metadata(doc_id: int):
    """Get auto-generated metadata for a document"""
    if not OCR_ENABLED:
        raise HTTPException(status_code=503, detail="OCR service not available")
    
    try:
        document = ocr_processor.get_document_by_id(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": doc_id,
            "filename": document.get("filename"),
            "document_type": document.get("document_type"),
            "transcribed_text": document.get("transcribed_text"),
            "scan_date": document.get("scan_date"),
            "created_at": document.get("created_at")
        }
    except Exception as e:
        logger.error(f"Error retrieving metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_auto_archive_documents(limit: int = 20):
    """List recent auto-archived documents"""
    if not OCR_ENABLED:
        raise HTTPException(status_code=503, detail="OCR service not available")
    
    try:
        documents = ocr_processor.list_recent_documents(limit)
        return {
            "documents": documents,
            "total": len(documents)
        }
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Additional OCR endpoints for compatibility
@router.post("/process-pdf/{filename}")
def process_pdf_ocr(filename: str, request: DocumentTypeRequest):
    """Process a scanned PDF with OCR using Gemini 1.5 Flash"""
    if not OCR_ENABLED:
        raise HTTPException(
            status_code=503, 
            detail="OCR service not available. Please set GEMINI_API_KEY environment variable."
        )
    
    file_path = Path("uploads/scans") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    if not file_path.suffix.lower() == '.pdf':
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        logger.info(f"Starting OCR processing for: {filename}")
        result = ocr_processor.process_pdf_file(
            str(file_path), 
            document_type=request.document_type
        )
        
        if result["success"]:
            logger.info(f"OCR completed successfully for {filename}")
            return {
                "success": True,
                "message": "PDF processed successfully with OCR",
                "document_id": result["document_id"],
                "filename": result["filename"],
                "document_type": result.get("document_type", "unknown"),
                "word_count": result["word_count"],
                "character_count": result["character_count"],
                "processing_date": result["processing_date"],
                "transcribed_text_preview": result["transcribed_text"][:500] + "..." if len(result["transcribed_text"]) > 500 else result["transcribed_text"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@router.post("/upload-and-process")
async def upload_and_process_ocr(
    file: UploadFile = File(...),
    document_type: Optional[str] = None
):
    """Upload and process a document with OCR"""
    if not OCR_ENABLED:
        raise HTTPException(
            status_code=503, 
            detail="OCR service not available. Please set GEMINI_API_KEY environment variable."
        )
    
    # Validate file type
    allowed_types = {'.pdf', '.png', '.jpg', '.jpeg', '.webp'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        logger.info(f"Processing uploaded file: {file.filename}")
        
        if file_extension == '.pdf':
            result = ocr_processor.process_pdf_file(tmp_file_path, document_type)
        else:
            result = ocr_processor.process_image_file(tmp_file_path, document_type)
        
        if result["success"]:
            logger.info(f"OCR completed successfully for uploaded file: {file.filename}")
            return {
                "success": True,
                "message": "File processed successfully with OCR",
                "document_id": result["document_id"],
                "original_filename": file.filename,
                "document_type": result.get("document_type", "unknown"),
                "word_count": result["word_count"],
                "character_count": result["character_count"],
                "processing_date": result["processing_date"],
                "transcribed_text_preview": result["transcribed_text"][:500] + "..." if len(result["transcribed_text"]) > 500 else result["transcribed_text"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Upload and OCR processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_file_path)
        except:
            pass


@router.get("/search")
def search_documents(
    query: str,
    document_type: Optional[str] = None,
    limit: int = 20
):
    """Search transcribed documents by content"""
    if not OCR_ENABLED:
        raise HTTPException(
            status_code=503, 
            detail="OCR service not available. Please set GEMINI_API_KEY environment variable."
        )
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    try:
        results = ocr_processor.search_documents(query, document_type)
        
        # Limit results
        if limit > 0:
            results = results[:limit]
        
        return {
            "success": True,
            "query": query,
            "document_type_filter": document_type,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/document/{doc_id}")
def get_document(doc_id: int):
    """Get a specific document by ID"""
    if not OCR_ENABLED:
        raise HTTPException(
            status_code=503, 
            detail="OCR service not available. Please set GEMINI_API_KEY environment variable."
        )
    
    try:
        document = ocr_processor.get_document_by_id(doc_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "document": document
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")


@router.get("/recent")
def get_recent_documents(limit: int = 20):
    """Get recently processed documents"""
    if not OCR_ENABLED:
        raise HTTPException(
            status_code=503, 
            detail="OCR service not available. Please set GEMINI_API_KEY environment variable."
        )
    
    try:
        documents = ocr_processor.list_recent_documents(limit)
        
        return {
            "success": True,
            "total_documents": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        logger.error(f"Get recent documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")


@router.get("/stats")
def get_ocr_stats():
    """Get OCR processing statistics"""
    if not OCR_ENABLED:
        raise HTTPException(
            status_code=503, 
            detail="OCR service not available. Please set GEMINI_API_KEY environment variable."
        )
    
    try:
        # Get basic stats from database
        import sqlite3
        conn = sqlite3.connect(ocr_processor.db_path)
        cursor = conn.cursor()
        
        # Total documents
        cursor.execute("SELECT COUNT(*) FROM legal_documents")
        total_docs = cursor.fetchone()[0]
        
        # Documents by type
        cursor.execute("""
            SELECT document_type, COUNT(*) as count 
            FROM legal_documents 
            GROUP BY document_type 
            ORDER BY count DESC
        """)
        by_type = dict(cursor.fetchall())
        
        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM legal_documents 
            WHERE scan_date >= datetime('now', '-7 days')
        """)
        recent_activity = cursor.fetchone()[0]
        
        # Total words processed
        cursor.execute("""
            SELECT SUM(LENGTH(transcribed_text) - LENGTH(REPLACE(transcribed_text, ' ', '')) + 1) 
            FROM legal_documents
        """)
        total_words_result = cursor.fetchone()[0]
        total_words = total_words_result if total_words_result else 0
        
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "total_documents": total_docs,
                "documents_by_type": by_type,
                "recent_activity_7_days": recent_activity,
                "total_words_processed": total_words,
                "ocr_model": "gemini-1.5-flash",
                "database_path": ocr_processor.db_path
            }
        }
        
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")


# Legacy scanning endpoint (non-auto-archive)
@router.post("/scan")
async def scan_document():
    """Legacy endpoint for basic document scanning"""
    naps2_path = find_naps2()
    if not naps2_path:
        raise HTTPException(
            status_code=500,
            detail="NAPS2 not found. Please ensure NAPS2 is installed."
        )
    
    # Create scans directory if it doesn't exist
    scans_dir = Path("uploads/scans")
    scans_dir.mkdir(parents=True, exist_ok=True)
    
    # Use timestamp-based filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_pdf_path = scans_dir / f"scan_{timestamp}.pdf"
    
    try:
        command = [
            naps2_path,
            "-o", str(temp_pdf_path),
            "--verbose"
        ]
        
        logger.info(f"Executing command: {' '.join(command)}")
        
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
                detail=f"NAPS2 scan failed: {error_msg}"
            )
        
        if not temp_pdf_path.exists() or temp_pdf_path.stat().st_size == 0:
            raise HTTPException(
                status_code=500,
                detail="Scan completed but no valid PDF file was created"
            )
        
        file_size = temp_pdf_path.stat().st_size
        logger.info(f"Scan successful: {temp_pdf_path}")
        
        return {
            "success": True,
            "message": "Document scanned successfully",
            "filename": temp_pdf_path.name,
            "file_size": file_size,
            "timestamp": datetime.datetime.now().isoformat(),
            "download_url": f"/api/auto-archive/download/{temp_pdf_path.name}"
        }
        
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
        logger.error(f"Unexpected error: {str(e)}")
        if temp_pdf_path.exists():
            temp_pdf_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {str(e)}"
        )


@router.get("/download/{filename}")
def download_file(filename: str):
    """Download a scanned file"""
    file_path = Path("uploads/scans") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/pdf"
    )


@router.get("/category-stats")
async def get_auto_archive_category_stats(
    current_user: User = Depends(require_official),
    db: AsyncSession = Depends(get_db)
):
    """Get auto-archive category statistics and management info"""
    try:
        smart_category_service = SmartCategoryService(db)
        
        # Get category count
        category_count = await smart_category_service.get_category_count()
        
        # Get all categories with document counts
        categories = await smart_category_service.document_service.get_categories()
        
        # Calculate statistics
        category_stats = []
        for category in categories:
            category_stats.append({
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "document_count": getattr(category, 'document_count', 0),
                "created_at": category.created_at.isoformat() if category.created_at else None
            })
        
        return {
            "success": True,
            "total_categories": category_count,
            "max_categories": SmartCategoryService.MAX_CATEGORIES,
            "categories_remaining": SmartCategoryService.MAX_CATEGORIES - category_count,
            "categories": category_stats,
            "auto_archive_info": {
                "similarity_threshold": SmartCategoryService.SIMILARITY_THRESHOLD,
                "matching_enabled": True,
                "auto_creation_enabled": category_count < SmartCategoryService.MAX_CATEGORIES
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting category stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 