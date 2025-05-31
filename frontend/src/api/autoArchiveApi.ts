const BASE_URL = 'http://localhost:8000/api/auto-archive';

/**
 * Get authentication token from localStorage
 */
function getAuthToken(): string | null {
  return localStorage.getItem('authToken');
}

/**
 * Get auth headers for API requests
 */
function getAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export interface AutoArchiveMetadata {
  title: string;
  category: string;
  authority: string;
  document_type: string;
  issue_date?: string;
  document_number?: string;
  description?: string;
  tags?: string[];
  confidence_score?: number;
}

export interface AutoArchiveResponse {
  success: boolean;
  document_id?: string;
  metadata?: AutoArchiveMetadata;
  file_path?: string;
  error?: string;
}

export interface ArchivedDocument {
  document_id: number;
  filename: string;
  document_type: string;
  transcribed_text: string;
  scan_date: string;
  created_at: string;
}

export const autoArchiveApi = {
  /**
   * Upload PDF and auto-generate archival metadata using Gemini API
   */
  async uploadPdfForAutoArchive(
    file: File,
    documentType?: string
  ): Promise<AutoArchiveResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (documentType) {
      formData.append('document_type', documentType);
    }

    const response = await fetch(`${BASE_URL}/upload-pdf`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Scan from printer and automatically archive with metadata extraction
   */
  async scanAndAutoArchive(documentType?: string): Promise<AutoArchiveResponse> {
    const formData = new FormData();
    if (documentType) {
      formData.append('document_type', documentType);
    }

    const response = await fetch(`${BASE_URL}/scan-and-archive`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Get auto-generated metadata for a document
   */
  async getAutoArchiveMetadata(docId: number): Promise<ArchivedDocument> {
    const response = await fetch(`${BASE_URL}/metadata/${docId}`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * List recent auto-archived documents
   */
  async listAutoArchivedDocuments(limit: number = 20): Promise<{
    documents: ArchivedDocument[];
    total: number;
  }> {
    const response = await fetch(`${BASE_URL}/list?limit=${limit}`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Check API health and capabilities
   */
  async getServiceInfo(): Promise<{
    message: string;
    version: string;
    features: {
      basic_scanning: boolean;
      ocr_processing: boolean;
      auto_archive_upload: boolean;
      auto_archive_scan: boolean;
    };
    naps2_found: boolean;
    ocr_enabled: boolean;
  }> {
    const response = await fetch(`${BASE_URL}/info`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Get category statistics for auto-archive
   */
  async getCategoryStats(): Promise<{
    success: boolean;
    total_categories: number;
    max_categories: number;
    categories_remaining: number;
    categories: Array<{
      id: string;
      name: string;
      description: string;
      document_count: number;
      created_at: string;
    }>;
    auto_archive_info: {
      similarity_threshold: number;
      matching_enabled: boolean;
      auto_creation_enabled: boolean;
    };
  }> {
    const response = await fetch(`${BASE_URL}/category-stats`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },
}; 