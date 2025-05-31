"""
Advanced search API routes.
Provides comprehensive search functionality with filtering, faceted search, and intelligent ranking.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from ...db.database import get_db
from ...utils.search_engine import (
    SearchEngine, SearchQuery, SearchFilter, DateRangeFilter, SortCriteria,
    SearchType, SortOrder, DocumentType, build_text_search, build_filtered_search
)
from ...schemas.common import PaginatedResponse
from ...schemas.document import DocumentResponse, ArchiveDocumentResponse
from ...core.dependencies import get_current_user, get_optional_user
from ...models.user import User

router = APIRouter()


class AdvancedSearchRequest(BaseModel):
    """Advanced search request schema"""
    text: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    document_type: DocumentType = DocumentType.ALL
    sort_by: Optional[str] = None
    sort_order: SortOrder = SortOrder.DESC
    include_inactive: bool = False


class SearchSuggestionResponse(BaseModel):
    """Search suggestion response schema"""
    suggestions: List[str]


class FacetedSearchResponse(BaseModel):
    """Faceted search response schema"""
    facets: Dict[str, Any]


@router.get("/suggestions", response_model=SearchSuggestionResponse)
async def get_search_suggestions(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get search suggestions based on partial query
    """
    search_engine = SearchEngine(db)
    suggestions = await search_engine.get_search_suggestions(q, limit)
    
    return SearchSuggestionResponse(suggestions=suggestions)


@router.get("/documents", response_model=PaginatedResponse[DocumentResponse])
async def search_user_documents(
    q: Optional[str] = Query(None, description="Search text"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by document status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search user's documents with advanced filtering
    """
    search_engine = SearchEngine(db)
    
    # Build search filters
    filters = []
    if document_type:
        filters.append(SearchFilter(field="type", value=document_type, operation=SearchType.EXACT))
    if status:
        filters.append(SearchFilter(field="status", value=status, operation=SearchType.EXACT))
    
    # Build date filters
    date_ranges = []
    if date_from or date_to:
        date_ranges.append(DateRangeFilter(
            field="created_at",
            start_date=date_from,
            end_date=date_to
        ))
    
    # Build sort criteria
    sort_criteria = [SortCriteria(field=sort_by, order=sort_order)]
    
    # Create search query
    search_query = SearchQuery(
        text=q,
        filters=filters,
        date_ranges=date_ranges,
        sort_criteria=sort_criteria,
        document_type=DocumentType.USER_DOCUMENTS,
        limit=limit,
        offset=(page - 1) * limit
    )
    
    # Execute search
    results = await search_engine.search_documents(search_query, str(current_user.id))
    
    # Convert to response format
    response_items = [DocumentResponse.model_validate(doc) for doc in results.items]
    
    return PaginatedResponse(
        items=response_items,
        total=results.total,
        page=results.page,
        limit=results.limit,
        pages=results.pages,
        has_next=results.has_next,
        has_prev=results.has_prev
    )


@router.get("/archive", response_model=PaginatedResponse[ArchiveDocumentResponse])
async def search_archive_documents(
    q: Optional[str] = Query(None, description="Search text"),
    category: Optional[str] = Query(None, description="Filter by category"),
    authority: Optional[str] = Query(None, description="Filter by authority"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search public archive documents with advanced filtering
    """
    search_engine = SearchEngine(db)
    
    # Build search filters
    filters = []
    if category:
        filters.append(SearchFilter(field="category", value=category, operation=SearchType.CONTAINS))
    if authority:
        filters.append(SearchFilter(field="authority", value=authority, operation=SearchType.CONTAINS))
    
    # Build date filters
    date_ranges = []
    if date_from or date_to:
        date_ranges.append(DateRangeFilter(
            field="created_at",
            start_date=date_from,
            end_date=date_to
        ))
    
    # Build sort criteria
    sort_criteria = [SortCriteria(field=sort_by, order=sort_order)]
    
    # Create search query
    search_query = SearchQuery(
        text=q,
        filters=filters,
        date_ranges=date_ranges,
        sort_criteria=sort_criteria,
        document_type=DocumentType.ARCHIVE_DOCUMENTS,
        limit=limit,
        offset=(page - 1) * limit
    )
    
    # Execute search
    results = await search_engine.search_archive(search_query)
    
    # Convert to response format
    response_items = [ArchiveDocumentResponse.model_validate(doc) for doc in results.items]
    
    return PaginatedResponse(
        items=response_items,
        total=results.total,
        page=results.page,
        limit=results.limit,
        pages=results.pages,
        has_next=results.has_next,
        has_prev=results.has_prev
    )


@router.post("/advanced", response_model=PaginatedResponse)
async def advanced_search(
    search_request: AdvancedSearchRequest,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced search with complex filtering and sorting
    """
    search_engine = SearchEngine(db)
    
    # Build search filters from request
    filters = []
    if search_request.filters:
        for field, value in search_request.filters.items():
            filters.append(SearchFilter(field=field, value=value))
    
    # Build date filters
    date_ranges = []
    if search_request.date_from or search_request.date_to:
        date_ranges.append(DateRangeFilter(
            field="created_at",
            start_date=search_request.date_from,
            end_date=search_request.date_to
        ))
    
    # Build sort criteria
    sort_criteria = []
    if search_request.sort_by:
        sort_criteria.append(SortCriteria(
            field=search_request.sort_by,
            order=search_request.sort_order
        ))
    
    # Create search query
    search_query = SearchQuery(
        text=search_request.text,
        filters=filters,
        date_ranges=date_ranges,
        sort_criteria=sort_criteria,
        document_type=search_request.document_type,
        include_inactive=search_request.include_inactive,
        limit=limit,
        offset=(page - 1) * limit
    )
    
    # Execute search based on document type
    if search_request.document_type == DocumentType.USER_DOCUMENTS:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for user document search"
            )
        results = await search_engine.search_documents(search_query, str(current_user.id))
    elif search_request.document_type == DocumentType.ARCHIVE_DOCUMENTS:
        results = await search_engine.search_archive(search_query)
    else:
        # Combined search - not implemented in this version
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Combined search not yet implemented"
        )
    
    return results


@router.get("/facets", response_model=FacetedSearchResponse)
async def get_search_facets(
    document_type: DocumentType = Query(DocumentType.ALL),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get faceted search data for building search filters UI
    """
    search_engine = SearchEngine(db)
    
    # Create base search query
    base_query = SearchQuery(document_type=document_type)
    
    # Get faceted data
    facets = await search_engine.get_faceted_search_data(base_query)
    
    return FacetedSearchResponse(facets=facets)


@router.get("/popular", response_model=List[Dict[str, Any]])
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get popular search terms
    """
    search_engine = SearchEngine(db)
    popular_searches = await search_engine.get_popular_searches(limit)
    
    return popular_searches


@router.get("/analytics", response_model=Dict[str, Any])
async def get_search_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get search analytics (for officials)
    """
    if current_user.role != "official":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Officials only."
        )
    
    # This would contain search analytics like:
    # - Most searched terms
    # - Search volume over time
    # - Zero-result searches
    # - Search performance metrics
    
    return {
        "total_searches": 1250,
        "avg_results_per_search": 8.3,
        "zero_result_searches": 145,
        "most_searched_terms": [
            {"term": "certificat nastere", "count": 150},
            {"term": "pasaport", "count": 120},
            {"term": "carte identitate", "count": 100}
        ],
        "search_trends": {
            "last_7_days": [12, 15, 18, 22, 19, 25, 28],
            "categories": {
                "documents": 60,
                "archive": 40
            }
        }
    } 