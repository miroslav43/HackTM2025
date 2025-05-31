
/**
 * Main document upload section component
 * Refactored to use smaller, focused components
 */

import React from 'react';
import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useDocuments } from '@/hooks/useDocuments';
import DocumentUploadCard from './DocumentUploadCard';
import DocumentHistory from './DocumentHistory';

const documentTypes = [
  { id: 'id', name: 'Carte de identitate', description: 'Copie după cartea de identitate (față și verso)' },
  { id: 'landRegistry', name: 'Extras carte funciară', description: 'Document recent (max. 30 de zile)' },
  { id: 'income', name: 'Adeverință de venit', description: 'Document pentru calculul taxelor' },
  { id: 'property', name: 'Certificat de proprietate', description: 'Dovada proprietății imobiliare' },
  { id: 'other', name: 'Alte documente', description: 'Documente suplimentare relevante' }
];

const DocumentUploadSection: React.FC = () => {
  const { documents, isLoading, error, handleFileUpload } = useDocuments();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Se încarcă documentele...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Document upload cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {documentTypes.map((docType) => {
          const existingDoc = documents.find(doc => doc.type === docType.id);
          
          return (
            <DocumentUploadCard
              key={docType.id}
              docType={docType}
              existingDoc={existingDoc}
              onFileUpload={(type, files) => {
                if (files && files.length > 0) {
                  handleFileUpload(type, files[0]);
                }
              }}
            />
          );
        })}
      </div>

      {/* Documents history */}
      <DocumentHistory documents={documents} />
    </div>
  );
};

export default DocumentUploadSection;
