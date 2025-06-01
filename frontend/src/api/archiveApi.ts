import { apiClient } from './client';

/**
 * API functions for document archive management
 * Handles document search, categorization, and access
 */

export interface ArchiveDocument {
  id: string;
  title: string;
  description?: string;
  authority: string;
  category_id?: string;
  file_path: string;
  mime_type: string;
  file_size: number;
  download_count: number;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface DocumentCategory {
  id: string;
  name: string;
  description: string;
  icon?: string;
  color?: string;
  document_count: number;
}

export interface ArchiveSearchParams {
  q?: string;
  category_id?: string;
  authority?: string;
  tags?: string;
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface AddToArchiveRequest {
  title: string;
  category_id: string;
  authority: string;
  description?: string;
  tags?: string[];
  document_date?: string;
}

/**
 * Archive API functions
 */
export const archiveApi = {
  // Get all document categories
  getCategories: async (): Promise<DocumentCategory[]> => {
    const response = await apiClient.get('/archive/categories');
    return response.data;
  },

  // Search documents in archive
  searchDocuments: async (params: ArchiveSearchParams = {}): Promise<PaginatedResponse<ArchiveDocument>> => {
    const response = await apiClient.get('/archive/search', { params });
    return response.data;
  },

  // Get documents by category
  getDocumentsByCategory: async (
    categoryId: string, 
    page = 1, 
    limit = 20
  ): Promise<ArchiveDocument[]> => {
    const response = await apiClient.get(`/archive/categories/${categoryId}/documents`, {
      params: { page, limit }
    });
    return response.data;
  },

  // Get single document details
  getDocument: async (documentId: string): Promise<ArchiveDocument> => {
    const response = await apiClient.get(`/archive/documents/${documentId}`);
    return response.data;
  },

  // Download document
  downloadDocument: async (documentId: string): Promise<Blob> => {
    const response = await apiClient.get(`/archive/documents/${documentId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Get archive statistics
  getStats: async (): Promise<any> => {
    const response = await apiClient.get('/archive/stats');
    return response.data;
  },

  // Add document to archive (for officials)
  addToArchive: async (file: File, metadata: AddToArchiveRequest): Promise<ArchiveDocument> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', metadata.title);
      formData.append('category_id', metadata.category_id);
      formData.append('authority', metadata.authority);
      
      if (metadata.description) {
        formData.append('description', metadata.description);
      }
      
      if (metadata.tags && metadata.tags.length > 0) {
        formData.append('tags', metadata.tags.join(','));
      }

      // Use a custom fetch for FormData because apiClient adds Content-Type: application/json
      const response = await fetch('/api/archive/documents', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // If can't parse JSON, use default message
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Error adding document to archive:', error);
      throw error;
    }
  },
};