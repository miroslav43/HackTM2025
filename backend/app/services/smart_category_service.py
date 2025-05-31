"""
Smart Category Service for Auto-Archive Integration
Handles intelligent category matching, creation, and archive integration
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Dict, Tuple
from uuid import UUID
import logging
from fuzzywuzzy import fuzz
import re

from ..models.document import DocumentCategory, ArchiveDocument
from ..schemas.document import ArchiveDocumentCreate
from ..services.document_service import DocumentService

logger = logging.getLogger(__name__)

class SmartCategoryService:
    """Service for intelligent category matching and management"""
    
    MAX_CATEGORIES = 100
    SIMILARITY_THRESHOLD = 75  # Minimum similarity score for category matching
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.document_service = DocumentService(db)
    
    async def get_category_count(self) -> int:
        """Get current number of categories"""
        stmt = select(func.count(DocumentCategory.id))
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def find_best_matching_category(self, extracted_metadata: dict) -> Optional[str]:
        """
        Find the best matching category for extracted metadata
        
        Args:
            extracted_metadata: Metadata extracted from document
            
        Returns:
            category_id if match found, None otherwise
        """
        # Get all existing categories
        categories = await self.document_service.get_categories()
        
        if not categories:
            return None
        
        # Extract relevant fields for matching
        doc_category = extracted_metadata.get("category", "").lower()
        doc_title = extracted_metadata.get("title", "").lower()
        doc_description = extracted_metadata.get("description", "").lower()
        doc_tags = extracted_metadata.get("tags", [])
        
        # Combine all text for matching
        doc_text = f"{doc_category} {doc_title} {doc_description} {' '.join(doc_tags)}".lower()
        
        best_match = None
        best_score = 0
        
        for category in categories:
            score = self._calculate_category_similarity(
                doc_text, doc_category, doc_tags, category
            )
            
            if score > best_score and score >= self.SIMILARITY_THRESHOLD:
                best_score = score
                best_match = str(category.id)
        
        logger.info(f"Best category match: {best_match} (score: {best_score})")
        return best_match
    
    def _calculate_category_similarity(
        self, 
        doc_text: str, 
        doc_category: str, 
        doc_tags: List[str], 
        category: DocumentCategory
    ) -> float:
        """Calculate similarity score between document and category"""
        
        cat_name = category.name.lower()
        cat_desc = (category.description or "").lower()
        
        # Direct category name matching (highest weight)
        category_score = 0
        if doc_category:
            category_score = fuzz.partial_ratio(doc_category, cat_name)
        
        # Title/description matching
        title_score = max(
            fuzz.partial_ratio(doc_text, cat_name),
            fuzz.partial_ratio(doc_text, cat_desc)
        )
        
        # Tag-based matching
        tag_score = 0
        if doc_tags:
            for tag in doc_tags:
                tag_lower = tag.lower()
                tag_score = max(
                    tag_score,
                    fuzz.partial_ratio(tag_lower, cat_name),
                    fuzz.partial_ratio(tag_lower, cat_desc)
                )
        
        # Keyword matching
        keyword_score = self._keyword_based_matching(doc_text, category)
        
        # Weighted final score
        final_score = (
            category_score * 0.4 +  # Category field has highest weight
            title_score * 0.3 +     # Title/description matching
            tag_score * 0.2 +       # Tag matching
            keyword_score * 0.1     # Keyword matching
        )
        
        return final_score
    
    def _keyword_based_matching(self, doc_text: str, category: DocumentCategory) -> float:
        """Advanced keyword-based matching for Romanian administrative documents"""
        
        # Mapping of category keywords to categories
        category_keywords = {
            "urbanism": ["urbanism", "construcții", "autorizații", "planuri", "edificii", "clădiri"],
            "fiscal": ["fiscal", "taxe", "impozite", "plăți", "contribuții", "venituri"],
            "social": ["social", "asistență", "ajutoare", "servicii", "vulnerabile", "sprijin"],
            "transport": ["transport", "circulație", "rutiere", "vehicule", "drumuri", "trafic"],
            "mediu": ["mediu", "ecologic", "natură", "protecție", "salubritate", "deșeuri"],
            "administrativ": ["administrativ", "organizare", "funcționare", "regulament", "hotărâre"],
            "educație": ["educație", "școli", "învățământ", "cultură", "biblioteci", "elevi"],
            "sănătate": ["sănătate", "medical", "sanitare", "clinici", "spitale", "prevenție"],
            "siguranță": ["siguranță", "ordine", "publică", "securitate", "poliție", "protecție"],
            "economic": ["economic", "dezvoltare", "investiții", "afaceri", "comerț", "industrie"],
            "participare": ["participare", "cetățeni", "consultări", "transparență", "dezbatere"],
            "personal": ["personal", "angajați", "concursuri", "resurse", "umane", "posturi"]
        }
        
        cat_name_lower = category.name.lower()
        
        # Find matching keyword group
        max_score = 0
        for cat_type, keywords in category_keywords.items():
            if any(keyword in cat_name_lower for keyword in keywords):
                # Check how many keywords from this group appear in document
                matches = sum(1 for keyword in keywords if keyword in doc_text)
                score = (matches / len(keywords)) * 100
                max_score = max(max_score, score)
        
        return max_score
    
    async def create_smart_category(self, extracted_metadata: dict) -> Optional[str]:
        """
        Create a new category based on extracted metadata
        
        Args:
            extracted_metadata: Metadata from document
            
        Returns:
            category_id if created, None if limit reached
        """
        current_count = await self.get_category_count()
        
        if current_count >= self.MAX_CATEGORIES:
            logger.warning(f"Category limit reached: {current_count}/{self.MAX_CATEGORIES}")
            return None
        
        # Generate category name and description
        category_name = self._generate_category_name(extracted_metadata)
        category_description = self._generate_category_description(extracted_metadata)
        
        try:
            # Create new category
            new_category = DocumentCategory(
                name=category_name,
                description=category_description,
                icon="file",  # Default icon
                color="#6B7280"  # Default gray color
            )
            
            self.db.add(new_category)
            await self.db.commit()
            await self.db.refresh(new_category)
            
            logger.info(f"Created new category: {category_name} (ID: {new_category.id})")
            return str(new_category.id)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating category: {str(e)}")
            return None
    
    def _generate_category_name(self, metadata: dict) -> str:
        """Generate smart category name from metadata"""
        category = metadata.get("category", "")
        authority = metadata.get("authority", "")
        
        # Clean and format category name
        if category and category != "Document":
            # Use the detected category type
            if "regulament" in category.lower():
                return "Regulamente și Norme"
            elif "hotărâre" in category.lower():
                return "Hotărâri Administrative"
            elif "ordin" in category.lower():
                return "Ordine și Dispoziții"
            elif "contract" in category.lower():
                return "Contracte și Acorduri"
            elif "decizie" in category.lower():
                return "Decizii Administrative"
            elif "raport" in category.lower():
                return "Rapoarte și Analize"
            else:
                return f"{category} - {authority}" if authority else category
        
        # Fallback based on authority
        if authority and authority != "Autoritate publică":
            return f"Documente {authority}"
        
        # Generic fallback
        return "Documente Administrative"
    
    def _generate_category_description(self, metadata: dict) -> str:
        """Generate category description from metadata"""
        category = metadata.get("category", "")
        authority = metadata.get("authority", "")
        description = metadata.get("description", "")
        
        if description and len(description) > 20:
            return f"Categoria pentru documente de tip {category.lower()} - {description[:100]}..."
        
        return f"Documente de tip {category.lower()} emise de {authority}"
    
    async def get_fallback_category(self) -> str:
        """Get fallback category for when limit is reached"""
        # Try to find "Documente Administrative" or similar
        categories = await self.document_service.get_categories()
        
        fallback_names = [
            "Administrativ și Organizare",
            "Documente Administrative", 
            "Administrative",
            "Generale"
        ]
        
        for category in categories:
            if any(name.lower() in category.name.lower() for name in fallback_names):
                return str(category.id)
        
        # If no fallback found, return the first category
        if categories:
            return str(categories[0].id)
        
        raise Exception("No categories available for fallback")
    
    async def auto_archive_document(
        self, 
        file_path: str, 
        extracted_metadata: dict,
        uploaded_by_id: str
    ) -> str:
        """
        Automatically add document to archive with smart categorization
        
        Args:
            file_path: Path to the document file
            extracted_metadata: AI-extracted metadata
            uploaded_by_id: User ID who uploaded/scanned
            
        Returns:
            document_id of created archive document
        """
        # Step 1: Try to find matching category
        category_id = await self.find_best_matching_category(extracted_metadata)
        
        # Step 2: If no match, try to create new category
        if not category_id:
            category_id = await self.create_smart_category(extracted_metadata)
        
        # Step 3: If can't create (limit reached), use fallback
        if not category_id:
            category_id = await self.get_fallback_category()
            logger.warning(f"Using fallback category due to limit: {category_id}")
        
        # Step 4: Create archive document
        archive_data = ArchiveDocumentCreate(
            title=extracted_metadata.get("title", "Document scanat"),
            category_id=category_id,
            authority=extracted_metadata.get("authority", "Autoritate publică"),
            description=extracted_metadata.get("description"),
            tags=extracted_metadata.get("tags", [])
        )
        
        try:
            # Get file info
            import os
            file_size = os.path.getsize(file_path)
            
            # Create archive document
            archive_doc = ArchiveDocument(
                title=archive_data.title,
                category_id=UUID(category_id),
                authority=archive_data.authority,
                description=archive_data.description,
                file_path=file_path,
                file_size=file_size,
                mime_type="application/pdf",
                tags=archive_data.tags or [],
                uploaded_by=UUID(uploaded_by_id)
            )
            
            self.db.add(archive_doc)
            await self.db.commit()
            await self.db.refresh(archive_doc)
            
            logger.info(f"Document auto-archived: {archive_doc.id} in category: {category_id}")
            return str(archive_doc.id)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error auto-archiving document: {str(e)}")
            raise e 