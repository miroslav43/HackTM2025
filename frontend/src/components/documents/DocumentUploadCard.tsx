
/**
 * Single document upload card component
 * Handles individual document type upload and display
 */

import React from 'react';
import { Upload, Check, X, Clock, FileText, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { DocumentData } from '@/api/documentsApi';

interface DocumentType {
  id: string;
  name: string;
  description: string;
}

interface DocumentUploadCardProps {
  docType: DocumentType;
  existingDoc?: DocumentData;
  onFileUpload: (type: string, files: FileList | null) => void;
}

const DocumentUploadCard: React.FC<DocumentUploadCardProps> = ({
  docType,
  existingDoc,
  onFileUpload
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified': return <Check className="h-4 w-4 text-green-600" />;
      case 'rejected': return <X className="h-4 w-4 text-red-600" />;
      case 'pending': return <Clock className="h-4 w-4 text-amber-600" />;
      default: return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified': return 'bg-green-100 text-green-800 border-green-200';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-200';
      case 'pending': return 'bg-amber-100 text-amber-800 border-amber-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'verified': return 'Verificat';
      case 'rejected': return 'Respins';
      case 'pending': return 'În verificare';
      default: return 'Necunoscut';
    }
  };

  return (
    <Card className="animate-scale-in">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2 text-lg text-gray-800">
          <FileText className="h-5 w-5 text-gray-600" />
          <span>{docType.name}</span>
        </CardTitle>
        <CardDescription className="text-gray-600">{docType.description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            {existingDoc ? (
              <div className="space-y-2">
                <div className="flex items-center space-x-3">
                  <Badge className={`${getStatusColor(existingDoc.status)} border`}>
                    {getStatusIcon(existingDoc.status)}
                    {getStatusText(existingDoc.status)}
                  </Badge>
                  <span className="text-sm text-gray-600">
                    {existingDoc.size}
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Încărcat la {new Date(existingDoc.uploadDate).toLocaleDateString('ro-RO')}
                </p>
              </div>
            ) : (
              <p className="text-gray-600">Nu a fost încărcat încă</p>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {existingDoc && (
              <Button variant="outline" size="sm">
                <Eye className="h-4 w-4" />
              </Button>
            )}
            <input
              type="file"
              accept={docType.id === 'landRegistry' ? '.pdf' : 'image/*,.pdf'}
              onChange={(e) => onFileUpload(docType.id, e.target.files)}
              className="hidden"
              id={`${docType.id}-upload`}
            />
            <Label htmlFor={`${docType.id}-upload`} className="cursor-pointer">
              <Button variant="outline" size="sm" asChild>
                <span>
                  <Upload className="h-4 w-4 mr-2" />
                  {existingDoc ? 'Înlocuiește' : 'Încarcă'}
                </span>
              </Button>
            </Label>
          </div>
        </div>
        
        {existingDoc && existingDoc.status === 'pending' && (
          <div>
            <div className="flex justify-between text-sm mb-2 text-gray-700">
              <span>Progres verificare</span>
              <span>{Math.round(existingDoc.verificationProgress)}%</span>
            </div>
            <Progress value={existingDoc.verificationProgress} className="h-2" />
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default DocumentUploadCard;
