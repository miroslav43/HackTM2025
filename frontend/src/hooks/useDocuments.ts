
/**
 * Custom hook for document management
 * Handles document state, loading, and error states
 */

import { DocumentData, fetchUserDocuments, uploadDocument } from '@/api/documentsApi';
import { useEffect, useState } from 'react';

export const useDocuments = () => {
  const [documents, setDocuments] = useState<DocumentData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch documents on component mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await fetchUserDocuments();
      setDocuments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (type: string, file: File) => {
    try {
      setError(null);
      const newDocument = await uploadDocument(file, type);
      
      // Update local state immediately for better UX
      setDocuments(prev => [...prev.filter(doc => doc.type !== type), newDocument]);
      
      // Simulate verification progress
      simulateVerificationProgress(newDocument.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload document');
    }
  };

  const simulateVerificationProgress = (documentId: string) => {
    const interval = setInterval(() => {
      setDocuments(prev => prev.map(doc => {
        if (doc.id === documentId && doc.verificationProgress < 100) {
          const newProgress = doc.verificationProgress + Math.random() * 20;
          if (newProgress >= 100) {
            clearInterval(interval);
            return { ...doc, verificationProgress: 100, status: 'verified' as const };
          }
          return { ...doc, verificationProgress: newProgress };
        }
        return doc;
      }));
    }, 1000);
  };

  return {
    documents,
    isLoading,
    error,
    handleFileUpload,
    refreshDocuments: loadDocuments
  };
};
