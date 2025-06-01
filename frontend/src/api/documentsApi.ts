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
    const response = await fetch('/api/documents/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });
    
    if (!response.ok) throw new Error('Failed to fetch documents');
    
    const data = await response.json();
    
    // Transform the backend response to match frontend interface
    return data.map((doc: any) => ({
      id: doc.id,
      name: doc.name,
      type: doc.type,
      status: doc.status,
      uploadDate: doc.uploaded_at ? new Date(doc.uploaded_at).toISOString().split('T')[0] : '',
      size: doc.file_size ? `${(doc.file_size / 1024 / 1024).toFixed(1)} MB` : '0 MB',
      verificationProgress: doc.verification_progress || 0
    }));
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
    formData.append('name', file.name);
    formData.append('type', type);

    const response = await fetch('/api/documents/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
      body: formData
    });

    if (!response.ok) throw new Error('Failed to upload document');
    const data = await response.json();
    
    // Transform response to match frontend interface
    return {
      id: data.id,
      name: data.name,
      type: data.type,
      status: data.status,
      uploadDate: data.uploaded_at ? new Date(data.uploaded_at).toISOString().split('T')[0] : '',
      size: data.file_size ? `${(data.file_size / 1024 / 1024).toFixed(1)} MB` : '0 MB',
      verificationProgress: data.verification_progress || 0
    };
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
};
