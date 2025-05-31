
import { useState, useMemo } from 'react';
import { Document, SortField, SortOrder, filterDocuments, sortDocuments } from '@/utils/documentUtils';

export interface UseDocumentFilterProps {
  documents: Document[];
  selectedCategory: string | null;
}

export const useDocumentFilter = ({ documents, selectedCategory }: UseDocumentFilterProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<SortField>('date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [filterAuthority, setFilterAuthority] = useState('');
  const [filterDocumentType, setFilterDocumentType] = useState('');

  // Filter and sort documents based on current state
  const filteredDocuments = useMemo(() => {
    const filtered = filterDocuments(
      documents,
      searchTerm,
      selectedCategory,
      filterAuthority,
      filterDocumentType
    );
    
    return sortDocuments(filtered, sortBy, sortOrder);
  }, [documents, searchTerm, selectedCategory, filterAuthority, filterDocumentType, sortBy, sortOrder]);

  // Check if any filters are active
  const hasActiveFilters = useMemo(() => {
    return searchTerm !== '' || 
           (filterAuthority !== '' && filterAuthority !== 'all') || 
           (filterDocumentType !== '' && filterDocumentType !== 'all');
  }, [searchTerm, filterAuthority, filterDocumentType]);

  // Reset all filters
  const resetFilters = () => {
    setSearchTerm('');
    setFilterAuthority('');
    setFilterDocumentType('');
  };

  // Toggle sort order
  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  return {
    // State
    searchTerm,
    sortBy,
    sortOrder,
    filterAuthority,
    filterDocumentType,
    filteredDocuments,
    hasActiveFilters,
    
    // Actions
    setSearchTerm,
    setSortBy,
    setSortOrder,
    setFilterAuthority,
    setFilterDocumentType,
    resetFilters,
    toggleSortOrder
  };
};
