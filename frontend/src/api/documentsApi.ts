
/**
 * API functions for document management
 * Handles all document-related backend operations
 */

export interface DocumentData {
  id: string;
  name: string;
  type: 'id' | 'landRegistry' | 'income' | 'property' | 'other';
  status: 'pending' | 'verified' | 'rejected';
  uploadDate: string;
  size: string;
  verificationProgress: number;
}

/**
 * Fetch all documents for the current user
 */
export const fetchUserDocuments = async (): Promise<DocumentData[]> => {
  try {
    // Simulate API call - replace with actual backend endpoint
    const response = await fetch('/api/user/documents');
    if (!response.ok) throw new Error('Failed to fetch documents');
    return await response.json();
  } catch (error) {
    console.error('Error fetching documents:', error);
    // Return mock data for development
    return [
      {
        id: '1',
        name: 'Carte de identitate',
        type: 'id',
        status: 'verified',
        uploadDate: '2024-01-10',
        size: '2.1 MB',
        verificationProgress: 100
      },
      {
        id: '2',
        name: 'Extras carte funciară',
        type: 'landRegistry',
        status: 'pending',
        uploadDate: '2024-01-15',
        size: '1.8 MB',
        verificationProgress: 65
      }
    ];
  }
};

/**
 * Upload a new document
 */
export const uploadDocument = async (file: File, type: string): Promise<DocumentData> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const response = await fetch('/api/documents/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error('Failed to upload document');
    return await response.json();
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
};
