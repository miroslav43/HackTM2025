"""
Advanced search and filtering system with full-text search capabilities.
Provides intelligent ranking, faceted search, and complex query support.
"""

import re
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text, func, case, cast, String
from sqlalchemy.sql.expression import literal_column
from dataclasses import dataclass
from enum import Enum

from ..models.document import Document, ArchiveDocument
from ..models.user import User
from ..schemas.common import PaginatedResponse


class SearchType(str, Enum):
    """Search operation types"""
    EXACT = "exact"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    FUZZY = "fuzzy"


class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


class DocumentType(str, Enum):
    """Document type for search filtering"""
    USER_DOCUMENTS = "user_documents"
    ARCHIVE_DOCUMENTS = "archive_documents"
    ALL = "all"


@dataclass
class SearchFilter:
    """Individual search filter definition"""
    field: str
    value: Any
    operation: SearchType = SearchType.CONTAINS
    case_sensitive: bool = False


@dataclass
class DateRangeFilter:
    """Date range filter for temporal searches"""
    field: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class SortCriteria:
    """Sort criteria definition"""
    field: str
    order: SortOrder = SortOrder.DESC


@dataclass
class SearchQuery:
    """Complete search query specification"""
    text: Optional[str] = None
    filters: List[SearchFilter] = None
    date_ranges: List[DateRangeFilter] = None
    sort_criteria: List[SortCriteria] = None
    document_type: DocumentType = DocumentType.ALL
    include_inactive: bool = False
    limit: int = 20
    offset: int = 0


class SearchEngine:
    """
    Advanced search engine with full-text search and intelligent ranking
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
        # Search configuration
        self.max_results = 1000
        self.default_limit = 20
        
        # Text search weights for ranking
        self.text_weights = {
            'name': 3.0,
            'title': 2.5,
            'description': 2.0,
            'content': 1.5,
            'category': 1.0,
            'authority': 1.0
        }
        
        # Stopwords for text processing (Romanian)
        self.stopwords = {
            'si', 'sau', 'dar', 'de', 'la', 'cu', 'in', 'pe', 'pentru', 'prin',
            'din', 'ca', 'ce', 'care', 'cum', 'unde', 'cand', 'cat', 'sa', 'se',
            'un', 'o', 'al', 'unei', 'unui', 'unei', 'ale', 'lor', 'lui', 'ei',
            'este', 'sunt', 'era', 'eram', 'vor', 'va', 'avea', 'avem', 'au'
        }
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Preprocess text for search (tokenization, stopword removal)"""
        if not text:
            return []
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Tokenize
        tokens = text.split()
        
        # Remove stopwords and short tokens
        tokens = [token for token in tokens if len(token) > 2 and token not in self.stopwords]
        
        return tokens
    
    def _build_text_search_conditions(self, search_text: str, model_class) -> List:
        """Build text search conditions with ranking"""
        if not search_text:
            return []
        
        tokens = self._preprocess_text(search_text)
        if not tokens:
            return []
        
        conditions = []
        
        # Define searchable fields based on model
        if model_class == Document:
            searchable_fields = {
                'name': model_class.name,
                'description': model_class.description,
                'type': model_class.type
            }
        elif model_class == ArchiveDocument:
            searchable_fields = {
                'title': model_class.title,
                'description': model_class.description,
                'content': model_class.content,
                'category': literal_column("categories.name"),  # Join required
                'authority': model_class.authority
            }
        else:
            return []
        
        # Build search conditions for each token
        for token in tokens:
            token_conditions = []
            
            for field_name, field_column in searchable_fields.items():
                # Use ILIKE for case-insensitive search
                condition = field_column.ilike(f'%{token}%')
                token_conditions.append(condition)
            
            # At least one field must match each token
            if token_conditions:
                conditions.append(or_(*token_conditions))
        
        return conditions
    
    def _calculate_relevance_score(self, search_text: str, model_class) -> Any:
        """Calculate relevance score for ranking"""
        if not search_text:
            return literal_column("0")
        
        tokens = self._preprocess_text(search_text)
        if not tokens:
            return literal_column("0")
        
        score_parts = []
        
        # Define scoring fields based on model
        if model_class == Document:
            scoring_fields = {
                'name': model_class.name,
                'description': model_class.description
            }
        elif model_class == ArchiveDocument:
            scoring_fields = {
                'title': model_class.title,
                'description': model_class.description,
                'content': model_class.content
            }
        else:
            return literal_column("0")
        
        # Calculate score for each field and token
        for field_name, field_column in scoring_fields.items():
            weight = self.text_weights.get(field_name, 1.0)
            
            for token in tokens:
                # Exact match gets higher score
                exact_match = case(
                    (field_column.ilike(f'%{token}%'), weight),
                    else_=0
                )
                
                # Title/name exact match gets bonus
                if field_name in ['name', 'title']:
                    exact_match = case(
                        (field_column.ilike(token), weight * 2),
                        (field_column.ilike(f'%{token}%'), weight),
                        else_=0
                    )
                
                score_parts.append(exact_match)
        
        # Combine all score parts
        if score_parts:
            return sum(score_parts)
        else:
            return literal_column("0")
    
    def _apply_filters(self, query, filters: List[SearchFilter], model_class):
        """Apply filters to query"""
        if not filters:
            return query
        
        for filter_item in filters:
            field_name = filter_item.field
            value = filter_item.value
            operation = filter_item.operation
            
            # Get field from model
            if hasattr(model_class, field_name):
                field = getattr(model_class, field_name)
            else:
                continue  # Skip invalid fields
            
            # Apply operation
            if operation == SearchType.EXACT:
                if filter_item.case_sensitive:
                    condition = field == value
                else:
                    condition = func.lower(field) == func.lower(value)
            
            elif operation == SearchType.CONTAINS:
                if filter_item.case_sensitive:
                    condition = field.like(f'%{value}%')
                else:
                    condition = field.ilike(f'%{value}%')
            
            elif operation == SearchType.STARTS_WITH:
                if filter_item.case_sensitive:
                    condition = field.like(f'{value}%')
                else:
                    condition = field.ilike(f'{value}%')
            
            elif operation == SearchType.ENDS_WITH:
                if filter_item.case_sensitive:
                    condition = field.like(f'%{value}')
                else:
                    condition = field.ilike(f'%{value}')
            
            elif operation == SearchType.REGEX:
                # PostgreSQL regex (case-insensitive by default)
                if filter_item.case_sensitive:
                    condition = field.op('~')(value)
                else:
                    condition = field.op('~*')(value)
            
            else:
                continue  # Skip unsupported operations
            
            query = query.where(condition)
        
        return query
    
    def _apply_date_filters(self, query, date_ranges: List[DateRangeFilter], model_class):
        """Apply date range filters"""
        if not date_ranges:
            return query
        
        for date_range in date_ranges:
            field_name = date_range.field
            
            # Get field from model
            if hasattr(model_class, field_name):
                field = getattr(model_class, field_name)
            else:
                continue  # Skip invalid fields
            
            # Apply date range
            if date_range.start_date:
                query = query.where(field >= date_range.start_date)
            
            if date_range.end_date:
                query = query.where(field <= date_range.end_date)
        
        return query
    
    def _apply_sorting(self, query, sort_criteria: List[SortCriteria], model_class, relevance_score=None):
        """Apply sorting to query"""
        if not sort_criteria and relevance_score is None:
            # Default sorting
            if hasattr(model_class, 'created_at'):
                return query.order_by(model_class.created_at.desc())
            return query
        
        # Apply relevance score first if available
        if relevance_score is not None:
            query = query.order_by(relevance_score.desc())
        
        # Apply custom sort criteria
        if sort_criteria:
            for sort_item in sort_criteria:
                field_name = sort_item.field
                
                # Get field from model
                if hasattr(model_class, field_name):
                    field = getattr(model_class, field_name)
                    
                    if sort_item.order == SortOrder.ASC:
                        query = query.order_by(field.asc())
                    else:
                        query = query.order_by(field.desc())
        
        return query
    
    async def search_documents(self, search_query: SearchQuery, user_id: Optional[str] = None) -> PaginatedResponse:
        """
        Search user documents with advanced filtering
        """
        query = select(Document)
        
        # Apply user filter if specified
        if user_id:
            from uuid import UUID
            try:
                user_uuid = UUID(user_id)
                query = query.where(Document.user_id == user_uuid)
            except ValueError:
                pass  # Invalid UUID, ignore filter
        
        # Apply text search
        text_conditions = []
        relevance_score = None
        
        if search_query.text:
            text_conditions = self._build_text_search_conditions(search_query.text, Document)
            relevance_score = self._calculate_relevance_score(search_query.text, Document)
            
            if text_conditions:
                query = query.where(and_(*text_conditions))
        
        # Apply filters
        if search_query.filters:
            query = self._apply_filters(query, search_query.filters, Document)
        
        # Apply date filters
        if search_query.date_ranges:
            query = self._apply_date_filters(query, search_query.date_ranges, Document)
        
        # Include inactive documents filter
        if not search_query.include_inactive:
            # Assuming there's an active/status field
            if hasattr(Document, 'status'):
                query = query.where(Document.status != 'deleted')
        
        # Get total count before pagination
        count_query = select(func.count()).select_from(query.alias())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Apply sorting
        if relevance_score is not None:
            query = query.add_columns(relevance_score.label('relevance_score'))
        
        query = self._apply_sorting(query, search_query.sort_criteria, Document, relevance_score)
        
        # Apply pagination
        query = query.offset(search_query.offset).limit(search_query.limit)
        
        # Execute query
        result = await self.db.execute(query)
        
        if relevance_score is not None:
            # Extract documents and scores
            rows = result.all()
            documents = [row[0] for row in rows]
            scores = [row[1] for row in rows]
        else:
            documents = list(result.scalars().all())
            scores = []
        
        # Calculate pagination info
        pages = (total + search_query.limit - 1) // search_query.limit
        current_page = (search_query.offset // search_query.limit) + 1
        
        return PaginatedResponse(
            items=documents,
            total=total,
            page=current_page,
            limit=search_query.limit,
            pages=pages,
            has_next=current_page < pages,
            has_prev=current_page > 1
        )
    
    async def search_archive(self, search_query: SearchQuery) -> PaginatedResponse:
        """
        Search archive documents with advanced filtering
        """
        from ..models.document import DocumentCategory
        
        query = select(ArchiveDocument).join(
            DocumentCategory, 
            ArchiveDocument.category_id == DocumentCategory.id,
            isouter=True
        )
        
        # Apply text search
        text_conditions = []
        relevance_score = None
        
        if search_query.text:
            text_conditions = self._build_text_search_conditions(search_query.text, ArchiveDocument)
            relevance_score = self._calculate_relevance_score(search_query.text, ArchiveDocument)
            
            if text_conditions:
                query = query.where(and_(*text_conditions))
        
        # Apply filters
        if search_query.filters:
            query = self._apply_filters(query, search_query.filters, ArchiveDocument)
        
        # Apply date filters
        if search_query.date_ranges:
            query = self._apply_date_filters(query, search_query.date_ranges, ArchiveDocument)
        
        # Get total count before pagination
        count_query = select(func.count()).select_from(query.alias())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Apply sorting
        if relevance_score is not None:
            query = query.add_columns(relevance_score.label('relevance_score'))
        
        query = self._apply_sorting(query, search_query.sort_criteria, ArchiveDocument, relevance_score)
        
        # Apply pagination
        query = query.offset(search_query.offset).limit(search_query.limit)
        
        # Execute query
        result = await self.db.execute(query)
        
        if relevance_score is not None:
            # Extract documents and scores
            rows = result.all()
            documents = [row[0] for row in rows]
            scores = [row[1] for row in rows]
        else:
            documents = list(result.scalars().all())
            scores = []
        
        # Calculate pagination info
        pages = (total + search_query.limit - 1) // search_query.limit
        current_page = (search_query.offset // search_query.limit) + 1
        
        return PaginatedResponse(
            items=documents,
            total=total,
            page=current_page,
            limit=search_query.limit,
            pages=pages,
            has_next=current_page < pages,
            has_prev=current_page > 1
        )
    
    async def get_search_suggestions(self, query_text: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions based on partial query
        """
        if not query_text or len(query_text) < 2:
            return []
        
        suggestions = set()
        
        # Search in document names
        doc_query = select(Document.name).where(
            Document.name.ilike(f'%{query_text}%')
        ).limit(limit)
        
        doc_result = await self.db.execute(doc_query)
        suggestions.update([name for name in doc_result.scalars() if name])
        
        # Search in archive document titles
        archive_query = select(ArchiveDocument.title).where(
            ArchiveDocument.title.ilike(f'%{query_text}%')
        ).limit(limit)
        
        archive_result = await self.db.execute(archive_query)
        suggestions.update([title for title in archive_result.scalars() if title])
        
        # Return sorted suggestions
        return sorted(list(suggestions))[:limit]
    
    async def get_faceted_search_data(self, base_query: SearchQuery) -> Dict[str, Any]:
        """
        Get faceted search data for building search filters UI
        """
        facets = {}
        
        # Document types facet
        if base_query.document_type in [DocumentType.USER_DOCUMENTS, DocumentType.ALL]:
            doc_types = await self.db.execute(
                select(Document.type, func.count(Document.id)).group_by(Document.type)
            )
            facets['document_types'] = [
                {'value': type_name, 'count': count} 
                for type_name, count in doc_types.all()
            ]
        
        # Document status facet
        if base_query.document_type in [DocumentType.USER_DOCUMENTS, DocumentType.ALL]:
            doc_status = await self.db.execute(
                select(Document.status, func.count(Document.id)).group_by(Document.status)
            )
            facets['document_status'] = [
                {'value': status, 'count': count} 
                for status, count in doc_status.all()
            ]
        
        # Archive categories facet
        if base_query.document_type in [DocumentType.ARCHIVE_DOCUMENTS, DocumentType.ALL]:
            from ..models.document import DocumentCategory
            
            categories = await self.db.execute(
                select(DocumentCategory.name, func.count(ArchiveDocument.id))
                .join(ArchiveDocument, DocumentCategory.id == ArchiveDocument.category_id)
                .group_by(DocumentCategory.name)
            )
            facets['archive_categories'] = [
                {'value': name, 'count': count} 
                for name, count in categories.all()
            ]
        
        # Date ranges facet (last 30 days, 3 months, 6 months, 1 year)
        now = datetime.utcnow()
        date_ranges = [
            ('last_30_days', now - timedelta(days=30)),
            ('last_3_months', now - timedelta(days=90)),
            ('last_6_months', now - timedelta(days=180)),
            ('last_year', now - timedelta(days=365))
        ]
        
        facets['date_ranges'] = []
        for range_name, start_date in date_ranges:
            # Count documents in this range
            doc_count = 0
            archive_count = 0
            
            if base_query.document_type in [DocumentType.USER_DOCUMENTS, DocumentType.ALL]:
                doc_result = await self.db.execute(
                    select(func.count(Document.id)).where(Document.created_at >= start_date)
                )
                doc_count = doc_result.scalar()
            
            if base_query.document_type in [DocumentType.ARCHIVE_DOCUMENTS, DocumentType.ALL]:
                archive_result = await self.db.execute(
                    select(func.count(ArchiveDocument.id)).where(ArchiveDocument.created_at >= start_date)
                )
                archive_count = archive_result.scalar()
            
            facets['date_ranges'].append({
                'value': range_name,
                'count': doc_count + archive_count,
                'start_date': start_date.isoformat()
            })
        
        return facets
    
    async def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular search terms (would require search logging in production)
        """
        # This is a placeholder - in production, you'd log searches and analyze them
        return [
            {'term': 'certificat nastere', 'count': 150},
            {'term': 'pasaport', 'count': 120},
            {'term': 'carte identitate', 'count': 100},
            {'term': 'cazier', 'count': 85},
            {'term': 'diploma', 'count': 70}
        ][:limit]


# Search query builder helper functions

def build_text_search(text: str) -> SearchQuery:
    """Build simple text search query"""
    return SearchQuery(text=text)


def build_filtered_search(
    text: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: Optional[str] = None,
    sort_order: SortOrder = SortOrder.DESC
) -> SearchQuery:
    """Build complex filtered search query"""
    
    search_filters = []
    if filters:
        for field, value in filters.items():
            search_filters.append(SearchFilter(field=field, value=value))
    
    date_ranges = []
    if date_from or date_to:
        date_ranges.append(DateRangeFilter(
            field='created_at',
            start_date=date_from,
            end_date=date_to
        ))
    
    sort_criteria = []
    if sort_by:
        sort_criteria.append(SortCriteria(field=sort_by, order=sort_order))
    
    return SearchQuery(
        text=text,
        filters=search_filters,
        date_ranges=date_ranges,
        sort_criteria=sort_criteria
    ) 