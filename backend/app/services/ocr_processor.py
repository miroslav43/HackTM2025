import os
import base64
import sqlite3
import datetime
from pathlib import Path
import google.generativeai as genai
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDocumentOCR:
    def __init__(self, api_key=None):
        """
        Initialize the Legal Document OCR processor using Gemini 1.5 Flash
        
        Args:
            api_key (str): Google AI API key. If None, reads from GEMINI_API_KEY environment variable
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable must be set or api_key provided")
        
        # Configure the API key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        # Use a separate database for OCR documents
        self.db_path = "legal_documents_ocr.db"
        self._setup_database()
    
    def _setup_database(self):
        """Set up SQLite database for storing transcribed documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legal_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                document_type TEXT,
                transcribed_text TEXT NOT NULL,
                original_format TEXT NOT NULL,
                scan_date TIMESTAMP NOT NULL,
                confidence_score REAL,
                verification_status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_filename ON legal_documents(filename);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scan_date ON legal_documents(scan_date);
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_legal_ocr_prompt(self):
        """
        Get the specialized system prompt for legal document OCR transcription
        Following best practices from Gemini documentation
        """
        return """You are an expert legal document transcription specialist with decades of experience transcribing legal documents with absolute precision and accuracy.

CRITICAL INSTRUCTIONS:
1. You will receive a PDF or scanned image of a legal document (contracts, statutes, court filings, legislation, regulations, etc.)
2. Your task is to transcribe EVERY single word, punctuation mark, number, and formatting element with 100% accuracy
3. Legal documents require PERFECT transcription - even small errors can have serious legal consequences
4. Maintain the EXACT formatting, structure, and layout of the original document
5. Preserve all legal formatting conventions (indentation, numbering, section breaks, signatures, dates, etc.)

TRANSCRIPTION PROCESS:
1. First, carefully examine the entire document to understand its structure and type
2. Transcribe the document word-for-word, maintaining original formatting
3. After completing the initial transcription, REVIEW your work carefully
4. Check for any errors, missing text, or formatting issues
5. Make corrections to ensure the transcription perfectly matches the original
6. Provide your final, verified transcription

FORMATTING REQUIREMENTS:
- Preserve all paragraph breaks, line breaks, and spacing
- Maintain original numbering systems (1., a), i), etc.)
- Keep all section headers, titles, and subtitles exactly as shown
- Preserve signatures, dates, and legal stamps/seals as text descriptions
- Maintain tables, lists, and bullet points in their original format
- Include margin notes, footnotes, and annotations if present

QUALITY ASSURANCE:
- Double-check all numbers, dates, names, and legal terms
- Verify all punctuation is correctly transcribed
- Ensure no text is missing or duplicated
- Confirm formatting matches the original document structure

OUTPUT FORMAT:
Provide only the transcribed text in the exact format and structure of the original legal document. Do not add any commentary, explanations, or metadata unless specifically requested."""

    def _get_metadata_extraction_prompt(self, text: str, document_type: str = None) -> str:
        """
        Get specialized prompt for extracting structured metadata from Romanian legal documents
        """
        return f"""
Ești un expert în analiza documentelor administrative și legale românești. OBLIGATORIU trebuie să extragi metadate complete pentru TOATE câmpurile, chiar dacă trebuie să faci inferențe educate.

TEXTUL DOCUMENTULUI:
{text[:3000]}...

INSTRUCȚIUNI CRITICE:
Tu TREBUIE să completezi TOATE câmpurile de mai jos. NICIODATĂ nu lăsa câmpuri goale sau null pentru câmpurile obligatorii. Dacă informația nu este clară, fă o inferență logică pe baza contextului documentului.

EXTRACTIE METADATE - JSON EXACT:
{{
    "title": "[OBLIGATORIU] Titlul complet al documentului sau numele descriptiv",
    "document_number": "[OPȚIONAL] Numărul documentului dacă este identificabil",
    "category": "[OBLIGATORIU] Una dintre: Regulament|Hotărâre|Ordin|Lege|Contract|Notificare|Cerere|Decizie|Proces-verbal|Raport|Adeverință|Comunicat|Dispozitie",
    "authority": "[OBLIGATORIU] Autoritatea emitentă: Primăria|Consiliul Local|Prefectura|Ministerul|ANAF|Agenția|Compania|etc.",
    "issue_date": "[OPȚIONAL] Data în format YYYY-MM-DD dacă se găsește clar",
    "tags": "[OBLIGATORIU] Array cu 4-8 cuvinte cheie relevante din document",
    "description": "[OBLIGATORIU] Descriere scurtă a conținutului (max 200 caractere)",
    "confidence_score": "[OBLIGATORIU] Scor încredere 0.0-1.0"
}}

REGULI STRICTE:
1. Pentru "title": Extrage titlul exact din document SAU creează unul descriptiv
2. Pentru "category": Alege categoria cea mai apropiată din lista dată
3. Pentru "authority": Identifică instituția emitentă chiar dacă e abreviată
4. Pentru "tags": Extrage cuvinte cheie importante din conținut
5. Pentru "description": Sumarizează scopul/conținutul documentului
6. NICIODATĂ null/empty pentru: title, category, authority, tags, description
7. Returnează DOAR JSON-ul, fără text suplimentar

EXEMPLU pentru document neclar:
{{
    "title": "Document administrativ oficial",
    "document_number": null,
    "category": "Document",
    "authority": "Instituție publică",
    "issue_date": null,
    "tags": ["administrativ", "oficial", "document", "public"],
    "description": "Document oficial cu caracter administrativ",
    "confidence_score": 0.4
}}

ANALIZEAZĂ DOCUMENTUL ȘI RETURNEAZĂ JSON-ul:"""

    async def extract_metadata_from_text(self, text: str, document_type: str = None) -> dict:
        """Extract structured metadata from OCR text using Gemini API"""
        logger.info(f"Starting metadata extraction for document type: {document_type}")
        logger.debug(f"Text preview: {text[:200]}...")
        
        try:
            metadata_prompt = self._get_metadata_extraction_prompt(text, document_type)
            
            generation_config = genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.3,
                top_p=0.9,
                max_output_tokens=1000
            )
            
            logger.info("Sending request to Gemini for metadata extraction...")
            response = self.model.generate_content(
                metadata_prompt,
                generation_config=generation_config,
            )
            
            logger.info(f"Received response from Gemini: {response.text[:200]}...")
            
            import json
            metadata_json = json.loads(response.text)
            logger.info(f"Parsed metadata JSON: {metadata_json}")
            
            # Add original text for smart validation
            metadata_json["_original_text"] = text[:1000]
            
            # Validate and clean the metadata
            cleaned_metadata = self._validate_and_clean_metadata(metadata_json, document_type)
            logger.info(f"Final cleaned metadata: {cleaned_metadata}")
            
            return cleaned_metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
            return self._get_fallback_metadata(document_type)
        except Exception as e:
            logger.error(f"Metadata extraction error: {str(e)}")
            return self._get_fallback_metadata(document_type)
    
    def _validate_and_clean_metadata(self, metadata: dict, document_type: str = None) -> dict:
        """Validate and clean extracted metadata - FORCE all required fields"""
        
        # Extract text content for smart defaults
        text_preview = metadata.get("_original_text", "")[:500] if "_original_text" in metadata else ""
        
        # FORCE completion of all required fields
        cleaned = {
            "title": self._force_title(metadata.get("title"), text_preview),
            "document_number": self._clean_optional_field(metadata.get("document_number")),
            "category": self._force_category(metadata.get("category"), text_preview),
            "authority": self._force_authority(metadata.get("authority"), text_preview),
            "issue_date": self._clean_date(metadata.get("issue_date")),
            "tags": self._force_tags(metadata.get("tags"), text_preview),
            "description": self._force_description(metadata.get("description"), text_preview),
            "confidence_score": self._clean_confidence(metadata.get("confidence_score"))
        }
        
        logger.info(f"Forced metadata completion: {cleaned}")
        return cleaned
    
    def _force_title(self, title, text_preview):
        """Force a meaningful title"""
        if title and str(title).strip():
            return str(title).strip()
        
        # Try to extract from text preview
        lines = text_preview.split('\n')
        for line in lines[:3]:
            line = line.strip()
            if len(line) > 10 and any(word in line.upper() for word in ['HOTĂRÂRE', 'ORDIN', 'REGULAMENT', 'CONTRACT', 'DECIZIE']):
                return line[:100]
        
        # Generic fallback
        return "Document administrativ"
    
    def _force_category(self, category, text_preview):
        """Force a valid category"""
        valid_categories = [
            "Regulament", "Hotărâre", "Ordin", "Lege", "Contract", 
            "Notificare", "Cerere", "Decizie", "Proces-verbal", 
            "Raport", "Adeverință", "Comunicat", "Dispoziție"
        ]
        
        if category and str(category).strip() in valid_categories:
            return str(category).strip()
        
        # Try to detect from text
        text_upper = text_preview.upper()
        for cat in valid_categories:
            if cat.upper() in text_upper:
                return cat
        
        # Smart defaults based on keywords
        if any(word in text_upper for word in ['HOTĂRÂRE', 'HOTARARE']):
            return "Hotărâre"
        elif any(word in text_upper for word in ['ORDIN']):
            return "Ordin"
        elif any(word in text_upper for word in ['REGULAMENT']):
            return "Regulament"
        elif any(word in text_upper for word in ['CONTRACT']):
            return "Contract"
        elif any(word in text_upper for word in ['DECIZIE']):
            return "Decizie"
        
        return "Document"
    
    def _force_authority(self, authority, text_preview):
        """Force a meaningful authority"""
        if authority and str(authority).strip():
            return str(authority).strip()
        
        # Try to detect from text
        text_upper = text_preview.upper()
        authorities = [
            ("PRIMĂRIA", "Primăria"),
            ("CONSILIUL LOCAL", "Consiliul Local"),
            ("PREFECTURA", "Prefectura"),
            ("MINISTERUL", "Ministerul"),
            ("ANAF", "ANAF"),
            ("AGENȚIA", "Agenția"),
            ("COMPANIA", "Compania"),
            ("DIRECȚIA", "Direcția")
        ]
        
        for keyword, name in authorities:
            if keyword in text_upper:
                return name
        
        return "Autoritate publică"
    
    def _force_tags(self, tags, text_preview):
        """Force meaningful tags"""
        if tags and isinstance(tags, list) and len(tags) >= 3:
            return [str(tag).strip() for tag in tags if str(tag).strip()][:8]
        
        # Generate tags from text
        common_words = ['administrativ', 'oficial', 'document', 'public']
        text_words = text_preview.lower().split()
        
        important_words = []
        for word in text_words:
            word = word.strip('.,;!?()[]{}\"\'')
            if len(word) > 4 and word.isalpha():
                if word in ['hotărâre', 'ordin', 'regulament', 'contract', 'decizie', 'primăria', 'consiliul']:
                    important_words.append(word)
        
        tags_result = common_words + important_words[:4]
        return tags_result[:8] if tags_result else ['document', 'administrativ', 'oficial']
    
    def _force_description(self, description, text_preview):
        """Force a meaningful description"""
        if description and str(description).strip():
            return str(description).strip()[:200]
        
        # Generate from text preview
        sentences = text_preview.replace('\n', ' ').split('.')
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if len(sentence) > 20 and not sentence.isupper():
                return sentence[:200]
        
        return "Document oficial cu caracter administrativ"
    
    def _clean_optional_field(self, value):
        """Clean optional field"""
        if value and str(value).strip() and str(value).strip().lower() != 'null':
            return str(value).strip()
        return None
    
    def _clean_date(self, date_value):
        """Clean and validate date"""
        if not date_value:
            return None
        
        date_str = str(date_value).strip()
        if len(date_str) == 10 and date_str.count('-') == 2:
            return date_str
        return None
    
    def _clean_confidence(self, confidence):
        """Clean confidence score"""
        try:
            score = float(confidence) if confidence is not None else 0.0
            return max(0.0, min(1.0, score))
        except:
            return 0.0
    
    def _get_fallback_metadata(self, document_type: str = None) -> dict:
        """Get fallback metadata when extraction fails"""
        return {
            "title": "Document fără titlu",
            "category": "Necunoscut",
            "authority": "Nespecificat",
            "document_type": document_type or "Nespecificat",
            "issue_date": None,
            "document_number": None,
            "description": "Metadatele nu au putut fi extrase automat",
            "tags": [],
            "confidence_score": 0.0
        }

    def process_pdf_file(self, pdf_path, document_type=None):
        """
        Process a PDF file using Google's Gemini model for OCR transcription
        
        Args:
            pdf_path (str): Path to the PDF file
            document_type (str): Optional document type classification
            
        Returns:
            dict: Processing results including transcribed text and metadata
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            return {
                "success": False,
                "error": f"File not found: {pdf_path}",
                "filename": pdf_path.name
            }
        
        try:
            logger.info(f"Starting PDF processing: {pdf_path}")
            
            # Upload the PDF file to Gemini
            uploaded_file = genai.upload_file(str(pdf_path))
            logger.info(f"File uploaded successfully: {uploaded_file.uri}")
            
            generation_config = genai.GenerationConfig(
                temperature=0.1,  # Low temperature for consistency
                top_p=0.95,
                max_output_tokens=65535
            )
            
            logger.info("Starting OCR transcription...")
            
            # Generate the transcription
            response = self.model.generate_content([
                self._get_legal_ocr_prompt(),
                uploaded_file
            ], generation_config=generation_config)
            
            transcribed_text = response.text
            
            if not transcribed_text:
                raise ValueError("No text was transcribed from the PDF")
            
            # Perform quality verification
            verified_text = self._verify_transcription(transcribed_text, str(pdf_path))
            
            # Store in database
            doc_id = self._store_in_database(
                filename=pdf_path.name,
                document_type=document_type or "unknown",
                transcribed_text=verified_text,
                original_format="PDF"
            )
            
            result = {
                "success": True,
                "document_id": doc_id,
                "filename": pdf_path.name,
                "transcribed_text": verified_text,
                "document_type": document_type,
                "word_count": len(verified_text.split()),
                "character_count": len(verified_text),
                "processing_date": datetime.datetime.now().isoformat()
            }
            
            logger.info(f"PDF processing completed successfully. Document ID: {doc_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "filename": pdf_path.name
            }

    def process_image_file(self, image_path, document_type=None):
        """
        Process an image file using Google's Gemini model for OCR transcription
        
        Args:
            image_path (str): Path to the image file  
            document_type (str): Optional document type classification
            
        Returns:
            dict: Processing results including transcribed text and metadata
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            return {
                "success": False,
                "error": f"File not found: {image_path}",
                "filename": image_path.name
            }
        
        try:
            logger.info(f"Starting image processing: {image_path}")
            
            # Upload the image file
            uploaded_file = genai.upload_file(str(image_path))
            logger.info(f"Image uploaded successfully: {uploaded_file.uri}")
            
            generation_config = genai.GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                max_output_tokens=65535
            )
            
            logger.info("Starting OCR transcription...")
            
            # Generate the transcription
            response = self.model.generate_content([
                self._get_legal_ocr_prompt(),
                uploaded_file
            ], generation_config=generation_config)
            
            transcribed_text = response.text
            
            if not transcribed_text:
                raise ValueError("No text was transcribed from the image")
            
            # Perform quality verification
            verified_text = self._verify_transcription(transcribed_text, str(image_path))
            
            # Store in database
            doc_id = self._store_in_database(
                filename=image_path.name,
                document_type=document_type or "unknown",
                transcribed_text=verified_text,
                original_format="IMAGE"
            )
            
            result = {
                "success": True,
                "document_id": doc_id,
                "filename": image_path.name,
                "transcribed_text": verified_text,
                "document_type": document_type,
                "word_count": len(verified_text.split()),
                "character_count": len(verified_text),
                "processing_date": datetime.datetime.now().isoformat()
            }
            
            logger.info(f"OCR processing completed successfully. Document ID: {doc_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "filename": image_path.name
            }

    def _get_image_mime_type(self, extension):
        """Get MIME type for image extensions"""
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp'
        }
        return mime_types.get(extension, 'image/jpeg')

    def _verify_transcription(self, transcribed_text, file_path):
        """
        Perform additional verification and quality checks on the transcribed text
        
        Args:
            transcribed_text (str): The initial transcription
            file_path (str): Path to the original file
            
        Returns:
            str: Verified and potentially corrected transcription
        """
        verification_prompt = f"""You are reviewing a legal document transcription for accuracy and completeness. 

ORIGINAL TRANSCRIPTION:
{transcribed_text}

VERIFICATION TASKS:
1. Carefully review the transcription for any obvious errors, inconsistencies, or missing elements
2. Check that legal formatting conventions are properly maintained
3. Verify that all text appears complete and sensible in the legal context
4. Look for any OCR-typical errors (character substitutions, missing punctuation, etc.)
5. Ensure the document structure and formatting are legally appropriate

If you find any errors or improvements needed, provide the corrected version.
If the transcription is accurate and complete, return it exactly as provided.

IMPORTANT: Only return the final, verified transcription text - no explanations or commentary."""
        
        try:
            generation_config = genai.GenerationConfig(
                temperature=0.05,  # Very low temperature for verification
                top_p=0.9,
                max_output_tokens=65535
            )
            
            response = self.model.generate_content(
                verification_prompt,
                generation_config=generation_config,
            )
            
            verified_text = response.text.strip()
            
            if verified_text and len(verified_text) > 10:
                logger.info("Transcription verification completed")
                return verified_text
            else:
                logger.warning("Verification returned empty result, using original transcription")
                return transcribed_text
                
        except Exception as e:
            logger.warning(f"Verification failed, using original transcription: {str(e)}")
            return transcribed_text
    
    def _store_in_database(self, filename, document_type, transcribed_text, original_format):
        """Store the transcribed document in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO legal_documents 
            (filename, document_type, transcribed_text, original_format, scan_date, verification_status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            document_type,
            transcribed_text,
            original_format,
            datetime.datetime.now(),
            'verified'
        ))
        
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return doc_id
    
    def search_documents(self, search_term, document_type=None):
        """
        Search transcribed documents by content
        
        Args:
            search_term (str): Text to search for
            document_type (str): Optional document type filter
            
        Returns:
            list: List of matching documents
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if document_type:
            cursor.execute('''
                SELECT id, filename, document_type, transcribed_text, scan_date
                FROM legal_documents 
                WHERE transcribed_text LIKE ? AND document_type = ?
                ORDER BY scan_date DESC
            ''', (f'%{search_term}%', document_type))
        else:
            cursor.execute('''
                SELECT id, filename, document_type, transcribed_text, scan_date
                FROM legal_documents 
                WHERE transcribed_text LIKE ?
                ORDER BY scan_date DESC
            ''', (f'%{search_term}%',))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "filename": row[1],
                "document_type": row[2],
                "transcribed_text": row[3][:500] + "..." if len(row[3]) > 500 else row[3],
                "scan_date": row[4]
            }
            for row in results
        ]
    
    def get_document_by_id(self, doc_id):
        """Get a specific document by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM legal_documents WHERE id = ?
        ''', (doc_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "filename": result[1],
                "document_type": result[2],
                "transcribed_text": result[3],
                "original_format": result[4],
                "scan_date": result[5],
                "confidence_score": result[6],
                "verification_status": result[7],
                "created_at": result[8]
            }
        return None
    
    def list_recent_documents(self, limit=20):
        """Get recently processed documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, document_type, scan_date, verification_status
            FROM legal_documents 
            ORDER BY scan_date DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "filename": row[1],
                "document_type": row[2],
                "scan_date": row[3],
                "verification_status": row[4]
            }
            for row in results
        ] 