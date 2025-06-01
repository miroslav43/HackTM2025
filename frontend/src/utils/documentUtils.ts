export interface Document {
  id: string;
  title: string;
  type: string;
  authority: string;
  date: string;
  category: string;
  size: string;
  status: 'available' | 'pending' | 'archived';
  description?: string;
}

export interface DocumentCategory {
  id: string;
  name: string;
  icon: React.ElementType;
  color: string;
  description: string;
  documentCount: number;
}

export type SortField = 'date' | 'name' | 'authority';
export type SortOrder = 'asc' | 'desc';

/**
 * Sorts documents based on the specified field and order
 */
export const sortDocuments = (
  documents: Document[], 
  sortBy: SortField, 
  sortOrder: SortOrder
): Document[] => {
  return documents.sort((a, b) => {
    let aValue: string, bValue: string;
    
    switch (sortBy) {
      case 'name':
        aValue = a.title;
        bValue = b.title;
        break;
      case 'authority':
        aValue = a.authority;
        bValue = b.authority;
        break;
      case 'date':
      default:
        aValue = a.date;
        bValue = b.date;
        break;
    }
    
    if (sortOrder === 'asc') {
      return aValue.localeCompare(bValue);
    } else {
      return bValue.localeCompare(aValue);
    }
  });
};

/**
 * Filters documents based on search term, category, authority, and document type
 */
export const filterDocuments = (
  documents: Document[],
  searchTerm: string,
  selectedCategory: string | null,
  filterAuthority: string,
  filterDocumentType: string
): Document[] => {
  return documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || doc.category === selectedCategory;
    const matchesAuthority = !filterAuthority || filterAuthority === 'all' || 
                            doc.authority.toLowerCase().includes(filterAuthority.toLowerCase());
    const matchesDocumentType = !filterDocumentType || filterDocumentType === 'all' || 
                               doc.type.toLowerCase().includes(filterDocumentType.toLowerCase());
    
    return matchesSearch && matchesCategory && matchesAuthority && matchesDocumentType;
  });
};

/**
 * Gets the appropriate CSS class for document status
 */
export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'available': return 'bg-green-100 text-green-800 border-green-200';
    case 'pending': return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'archived': return 'bg-gray-100 text-gray-800 border-gray-200';
    default: return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

/**
 * Gets the localized text for document status
 */
export const getStatusText = (status: string): string => {
  switch (status) {
    case 'available': return 'Disponibil';
    case 'pending': return 'În procesare';
    case 'archived': return 'Arhivat';
    default: return 'Necunoscut';
  }
};

/**
 * Handles document download logic
 */
export const handleDocumentDownload = (document: Document): void => {
  console.log(`Descărcare document: ${document.title}`);
  // Aici ar fi logica pentru descărcarea documentului
};
