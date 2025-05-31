# Auto-Archive System - Implementation

This document describes the implementation of the automatic archival system with AI-powered metadata extraction.

## Overview

The Auto-Archive system provides two main functionalities:
1. **Upload PDF** - Users upload PDF files and the system automatically generates archival metadata using Gemini AI
2. **Scan from Printer** - Direct scanning from connected printers via NAPS2, with automatic OCR and metadata extraction

## Backend Implementation (FastAPI)

### New Endpoints

#### `/auto-archive/upload-pdf`
- **Method**: POST
- **Purpose**: Upload PDF and auto-generate metadata
- **Input**: PDF file + optional document type
- **Output**: Auto-generated metadata + document ID

#### `/auto-archive/scan-and-archive`
- **Method**: POST
- **Purpose**: Scan from printer and auto-archive
- **Input**: Optional document type
- **Output**: Scanned document + extracted metadata

#### `/auto-archive/metadata/{doc_id}`
- **Method**: GET
- **Purpose**: Retrieve metadata for specific document
- **Output**: Document metadata and details

#### `/auto-archive/list`
- **Method**: GET
- **Purpose**: List recent auto-archived documents
- **Output**: List of processed documents

### Key Features

- **AI-Powered Metadata Extraction**: Uses Gemini 1.5 Flash model to analyze document content and extract structured metadata
- **Multi-format Support**: Handles PDF files with OCR processing
- **NAPS2 Integration**: Direct integration with NAPS2 scanner software
- **Robust Error Handling**: Comprehensive error handling and fallback mechanisms
- **Database Storage**: Automatic storage of processed documents and metadata

### Metadata Structure

The system extracts the following metadata:
```json
{
  "title": "Document title",
  "category": "Document category (e.g., Regulament, Hotărâre)",
  "authority": "Issuing authority (e.g., Primăria, Consiliul Local)",
  "document_type": "Specific document type",
  "issue_date": "YYYY-MM-DD format",
  "document_number": "Document number if found",
  "description": "Brief description",
  "tags": ["relevant", "keywords"],
  "confidence_score": 0.85
}
```

## Frontend Implementation (React)

### New Components

#### `AutoArchiveUpload`
- **Location**: `/auto-archive/upload`
- **Purpose**: PDF upload with drag-and-drop interface
- **Features**:
  - Drag-and-drop file upload
  - Real-time progress tracking
  - Metadata visualization
  - Error handling with user feedback

#### `AutoArchiveScan`
- **Location**: `/auto-archive/scan`
- **Purpose**: Scanner interface for direct scanning
- **Features**:
  - Service status monitoring
  - Real-time scan progress
  - Automatic OCR processing
  - Metadata display

### Navigation Updates

Added new sidebar navigation item "Adaugă în arhivă - automat" with two sub-options:
- Upload PDF
- Scan din imprimantă

Only visible to users with `official` role.

### API Integration

Created `autoArchiveApi.ts` service with methods:
- `uploadPdfForAutoArchive()` - Upload and process PDF
- `scanAndAutoArchive()` - Initiate scan and archive
- `getAutoArchiveMetadata()` - Retrieve document metadata
- `listAutoArchivedDocuments()` - List processed documents
- `getServiceInfo()` - Check service capabilities

## Installation & Setup

### Backend Dependencies

```bash
cd AI/ScanComponent
pip install -r requirements.txt
```

Dependencies include:
- `fastapi==0.115.0`
- `uvicorn[standard]==0.32.0`
- `python-multipart==0.0.12`
- `google-genai==1.18.0`
- `python-dotenv==1.0.0`

### Frontend Dependencies

```bash
cd frontend
npm install react-dropzone@14.2.3
```

### Environment Configuration

Create `.env` file in `AI/ScanComponent/`:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### NAPS2 Installation

For Windows:
1. Download NAPS2 from official website
2. Install to default location (`C:\Program Files\NAPS2\`)
3. Ensure scanner drivers are properly configured

## Usage

### Upload PDF Workflow
1. Navigate to "Adaugă în arhivă - automat" → "Upload PDF"
2. Optionally specify document type
3. Drag and drop PDF file or click to select
4. System processes file with OCR and AI metadata extraction
5. Review generated metadata
6. Document is automatically saved to archive

### Scan from Printer Workflow
1. Navigate to "Adaugă în arhivă - automat" → "Scan din imprimantă"
2. Check service status (NAPS2, OCR, Auto Archive)
3. Place document in scanner
4. Optionally specify document type
5. Click "Începe scanarea"
6. Follow scanner prompts
7. System automatically processes, extracts metadata, and archives

## Technical Details

### File Storage
- Scanned files: `scans/` directory
- Archived files: `archive/` directory
- Database: SQLite (`legal_documents.db`)

### AI Processing
- Model: Gemini 1.5 Flash
- Specialized prompts for Romanian legal documents
- Confidence scoring for metadata quality
- Fallback mechanisms for processing failures

### Error Handling
- Network connectivity issues
- Scanner hardware problems
- OCR processing failures
- Invalid file formats
- Service unavailability

## Security Considerations

- File size limits (50MB for PDFs)
- File type validation
- Role-based access control
- Secure file storage
- API endpoint protection

## Future Enhancements

Potential improvements:
- Batch processing for multiple documents
- Advanced metadata validation
- Document version control
- Integration with existing archive systems
- Support for additional file formats
- Custom metadata templates per document type 