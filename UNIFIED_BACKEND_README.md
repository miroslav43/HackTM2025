# Unified Backend Implementation

This document describes the successful merger of the AI ScanComponent into the main backend API, creating a single unified FastAPI server.

## Overview

The Romanian Public Administration Platform now runs on a **single unified backend** that includes:
- ✅ Authentication & User Management
- ✅ Document Management & Archive
- ✅ AI Agent Integration  
- ✅ **Auto-Archive with OCR** (newly integrated)
- ✅ Dashboard & Search functionality

## What Changed

### 🔄 Backend Integration

1. **OCR Service Integration**
   - Moved `ocr_processor.py` to `backend/app/services/`
   - Created `auto_archive.py` routes in `backend/app/api/routes/`
   - Added auto-archive router to main FastAPI app

2. **Dependencies Updated**
   - Added `google-genai==1.18.0` to backend requirements
   - All OCR and AI functionality now part of main backend

3. **Unified API Structure**
   ```
   backend/main.py (Port 8000)
   ├── /api/auth/*
   ├── /api/users/*
   ├── /api/documents/*
   ├── /api/archive/*
   ├── /api/auto-archive/*  ← NEW: Auto-Archive & OCR
   ├── /api/dashboard/*
   └── /api/settings/*
   ```

### 🌐 Frontend Updates

1. **API Base URL Changed**
   - From: `http://localhost:8000` (separate server)
   - To: `http://localhost:8000/api/auto-archive` (unified backend)

2. **Single Backend Connection**
   - Frontend now connects to one unified backend
   - Consistent error handling across all features

## New Unified Endpoints

### Auto-Archive & OCR Routes (`/api/auto-archive/`)

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/info` | GET | Service capabilities and status |
| `/upload-pdf` | POST | Upload PDF with auto-metadata generation |
| `/scan-and-archive` | POST | Scan from printer with auto-archive |
| `/metadata/{doc_id}` | GET | Get document metadata by ID |
| `/list` | GET | List recent auto-archived documents |
| `/upload-and-process` | POST | Upload any file type for OCR |
| `/search` | GET | Search transcribed documents |
| `/stats` | GET | OCR processing statistics |
| `/category-stats` | GET | Smart categorization statistics |
| `/scan` | POST | Legacy basic scanning |
| `/download/{filename}` | GET | Download scanned files |

## Installation & Setup

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Create .env file with:
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://...
```

### 2. Frontend Setup  
```bash
cd frontend
npm install
# react-dropzone already installed
```

### 3. Prerequisites
- ✅ PostgreSQL database running
- ✅ GEMINI_API_KEY configured
- ✅ NAPS2 installed (Windows, for scanning)

## Running the System

### Option 1: Use Unified Startup Script
```bash
./start_unified_backend.sh
```

### Option 2: Manual Start
```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend  
cd frontend && npm run dev
```

## Access Points

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Frontend App**: http://localhost:3000

## Features Available

### ✅ Core Platform Features
- User authentication & authorization
- Document management & archive
- AI agent integration
- Dashboard analytics
- Advanced search

### ✅ Auto-Archive Features (Integrated)
- **PDF Upload**: Drag-and-drop with auto-metadata extraction
- **Printer Scanning**: Direct NAPS2 integration
- **OCR Processing**: Gemini 1.5 Flash for text extraction
- **Metadata Generation**: AI-powered Romanian legal document analysis
- **Progress Tracking**: Real-time upload/scan progress
- **Error Handling**: Comprehensive error management

## 🤖 AI-Powered Auto-Archive Features

### Intelligent Metadata Extraction
Sistemul folosește **Gemini 1.5 Flash** pentru a genera automat metadate complete pentru documentele încărcate sau scanate:

#### Câmpuri Generate Automat:
- **Denumire Document**: Titlul extras din document sau generat inteligent
- **Număr Document**: Numărul/identificatorul dacă este detectat
- **Categorie**: Tipul documentului (Regulament, Hotărâre, Ordin, etc.)
- **Autoritate Emitentă**: Instituția care a emis documentul
- **Data Documentului**: Data de emitere în format YYYY-MM-DD
- **Etichete**: Cuvinte cheie relevante extrase din conținut
- **Descriere**: Sumar al conținutului documentului
- **Scor Încredere**: Nivelul de încredere al AI-ului (0.0-1.0)

#### Detecție Inteligentă:
- **Categorii**: Regulament, Hotărâre, Ordin, Lege, Contract, Notificare, Cerere, Decizie, Proces-verbal, Raport, Adeverință, Comunicat, Dispoziție
- **Autorități**: Primăria, Consiliul Local, Prefectura, Ministerul, ANAF, Agenția, Compania, Direcția
- **Forțare Completare**: Toate câmpurile obligatorii sunt completate automat, chiar dacă informația nu este clară

#### Exemple de Extragere:
```json
{
    "title": "HOTĂRÂREA NR. 123 privind regulamentul de organizare",
    "document_number": "123/2024",
    "category": "Hotărâre",
    "authority": "Consiliul Local",
    "issue_date": "2024-01-15",
    "tags": ["regulament", "organizare", "consiliul", "local"],
    "description": "Hotărâre privind aprobarea regulamentului de organizare și funcționare",
    "confidence_score": 0.85
}
```

## File Storage Structure

```
backend/uploads/
├── documents/         # Regular document uploads
├── avatars/          # User avatars
├── scans/            # Scanned documents (temporary)
├── archive/          # Auto-archived documents
└── temp/             # Temporary files
```

## Database Storage

### PostgreSQL (Main Database)
- Users, documents, categories, etc.
- Existing platform data

### SQLite (OCR Database)  
- File: `legal_documents_ocr.db`
- OCR transcriptions and metadata
- Separate from main database for performance

## Benefits of Unified Backend

### ✅ Simplified Architecture
- Single server to manage
- Consistent API patterns
- Unified error handling

### ✅ Better Performance
- Reduced network overhead
- Shared resources and connections
- Single authentication system

### ✅ Easier Deployment
- One backend service to deploy
- Simplified configuration
- Single SSL certificate needed

### ✅ Development Benefits
- Consistent code patterns
- Shared utilities and middleware
- Single API documentation

## Security Considerations

- ✅ Role-based access (officials only for auto-archive)
- ✅ File type validation (PDF, images)
- ✅ File size limits (50MB PDF, 7MB images)
- ✅ CORS configuration
- ✅ Secure file storage

## Migration Notes

### No Data Loss
- ✅ Existing documents preserved
- ✅ User accounts maintained  
- ✅ Archive contents intact

### Frontend Compatibility
- ✅ All existing features work
- ✅ New auto-archive features added
- ✅ No breaking changes

## Troubleshooting

### OCR Not Working
1. Check `GEMINI_API_KEY` in backend/.env
2. Verify google-genai package installed
3. Check logs in terminal

### Scanning Issues
1. Ensure NAPS2 installed on Windows
2. Check scanner drivers
3. Verify scanner permissions

### Database Issues
1. Check PostgreSQL connection
2. Verify database credentials
3. Run database migrations if needed

## Future Enhancements

- [ ] Batch document processing
- [ ] Advanced metadata templates
- [ ] Integration with main PostgreSQL DB
- [ ] Document version control
- [ ] Enhanced search across both databases

## 🎯 Smart Auto-Archive Integration

### 🔄 Intelligent Category Matching & Archive Integration
Sistemul integrează automat documentele scanate/încărcate în arhiva principală cu matching inteligent de categorii:

#### 🧠 **Logica de Matching:**
1. **Analiză Metadata**: Extrage categorii din conținutul documentului
2. **Matching Existent**: Compară cu categoriile din baza de date (similaritate > 75%)
3. **Creare Automată**: Dacă nu găsește match, creează categorie nouă
4. **Limită Categorii**: Maxim 100 categorii (forțează în categoria existentă dacă e atinsă limita)
5. **Integrare Arhivă**: Adaugă automat în arhiva oficială accesibilă tuturor

#### 📊 **Algoritm de Similaritate:**
- **40%** - Match direct pe tipul de categorie (Hotărâre, Regulament, etc.)
- **30%** - Similaritate titlu/descriere cu categoriile existente  
- **20%** - Match pe etichete/tags
- **10%** - Cuvinte cheie specifice românești

#### 🏗️ **Categorii Generate Automat:**
- **"Hotărâri Administrative"** - pentru documente tip Hotărâre
- **"Regulamente și Norme"** - pentru Regulamente
- **"Ordine și Dispoziții"** - pentru Ordine
- **"Contracte și Acorduri"** - pentru Contracte
- **"Decizii Administrative"** - pentru Decizii
- **"Rapoarte și Analize"** - pentru Rapoarte

#### 🔄 **Flux de Lucru Auto-Archive:**
```
PDF Upload/Scan → OCR → Extract Metadata → 
Find Category Match → Create Category (if needed) → 
Add to Main Archive → Store OCR Data → Return Archive ID
```

#### 📈 **Beneficii:**
- ✅ **Zero intervenție manuală** pentru categorizare
- ✅ **Consistență** în organizarea documentelor
- ✅ **Scalabilitate** până la 100 categorii
- ✅ **Căutare îmbunătățită** prin categorii relevante
- ✅ **Acces public** prin arhiva principală

---

🎉 **The unified backend successfully combines all platform features into a single, powerful FastAPI server with AI-powered document processing capabilities!** 