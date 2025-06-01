/**
 * Single document upload card component
 * Handles individual document type upload and display
 */

import { DocumentData } from "@/api/documentsApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Calendar,
  Check,
  Clock,
  CreditCard,
  Eye,
  FileText,
  MapPin,
  Upload,
  User,
  X,
} from "lucide-react";
import React, { useState } from "react";
import PersonalDocumentUploadDialog from "./PersonalDocumentUploadDialog";

interface DocumentType {
  id: string;
  name: string;
  description: string;
}

interface PersonalDocumentMetadata {
  id: string;
  extractedData: {
    nume?: string;
    prenume?: string;
    cnp?: string;
    dataEmiterii?: string;
    dataExpirarii?: string;
    serieNumar?: string;
    adresa?: string;
    tipDocument?: string;
    autoritate?: string;
    observatii?: string;
  };
  confidence: number;
  filePath: string;
  fileSize: number;
  processingDate: string;
}

interface DocumentUploadCardProps {
  docType: DocumentType;
  existingDoc?: DocumentData;
  onFileUpload: (type: string, files: FileList | null) => void;
}

const DocumentUploadCard: React.FC<DocumentUploadCardProps> = ({
  docType,
  existingDoc,
  onFileUpload,
}) => {
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [extractedMetadata, setExtractedMetadata] =
    useState<PersonalDocumentMetadata | null>(null);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "verified":
        return <Check className="h-4 w-4 text-green-600" />;
      case "rejected":
        return <X className="h-4 w-4 text-red-600" />;
      case "pending":
        return <Clock className="h-4 w-4 text-amber-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "verified":
        return "bg-green-100 text-green-800 border-green-200";
      case "rejected":
        return "bg-red-100 text-red-800 border-red-200";
      case "pending":
        return "bg-amber-100 text-amber-800 border-amber-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "verified":
        return "Verificat";
      case "rejected":
        return "Respins";
      case "pending":
        return "În verificare";
      default:
        return "Necunoscut";
    }
  };

  const handleDocumentProcessed = (metadata: PersonalDocumentMetadata) => {
    setExtractedMetadata(metadata);
    setIsUploadDialogOpen(false);
  };

  const handleReplaceClick = () => {
    setIsUploadDialogOpen(true);
  };

  const getMetadataIcon = (field: string) => {
    switch (field) {
      case "nume":
      case "prenume":
        return <User className="h-4 w-4 text-blue-500" />;
      case "cnp":
      case "serieNumar":
        return <CreditCard className="h-4 w-4 text-purple-500" />;
      case "dataEmiterii":
      case "dataExpirarii":
        return <Calendar className="h-4 w-4 text-green-500" />;
      case "adresa":
        return <MapPin className="h-4 w-4 text-orange-500" />;
      default:
        return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  const getFieldLabel = (field: string) => {
    const labels: Record<string, string> = {
      nume: "Nume",
      prenume: "Prenume",
      cnp: "CNP",
      dataEmiterii: "Data emiterii",
      dataExpirarii: "Data expirării",
      serieNumar: "Serie/Număr",
      adresa: "Adresa",
      tipDocument: "Tip document",
      autoritate: "Autoritate",
      observatii: "Observații",
    };
    return labels[field] || field;
  };

  return (
    <>
      <Card className="animate-scale-in">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-lg text-gray-800">
            <FileText className="h-5 w-5 text-gray-600" />
            <span>{docType.name}</span>
          </CardTitle>
          <CardDescription className="text-gray-600">
            {docType.description}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              {existingDoc ? (
                <div className="space-y-2">
                  <div className="flex items-center space-x-3">
                    <Badge
                      className={`${getStatusColor(existingDoc.status)} border`}
                    >
                      {getStatusIcon(existingDoc.status)}
                      {getStatusText(existingDoc.status)}
                    </Badge>
                    <span className="text-sm text-gray-600">
                      {existingDoc.size}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">
                    Încărcat la{" "}
                    {new Date(existingDoc.uploadDate).toLocaleDateString(
                      "ro-RO"
                    )}
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
              <Button variant="outline" size="sm" onClick={handleReplaceClick}>
                <Upload className="h-4 w-4 mr-2" />
                {existingDoc ? "Înlocuiește" : "Încarcă"}
              </Button>
            </div>
          </div>

          {existingDoc && existingDoc.status === "pending" && (
            <div>
              <div className="flex justify-between text-sm mb-2 text-gray-700">
                <span>Progres verificare</span>
                <span>{Math.round(existingDoc.verificationProgress)}%</span>
              </div>
              <Progress
                value={existingDoc.verificationProgress}
                className="h-2"
              />
            </div>
          )}

          {/* Display extracted metadata if available */}
          {extractedMetadata && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-blue-900 flex items-center space-x-2">
                  <FileText className="h-4 w-4" />
                  <span>Informații extrase cu AI</span>
                </h4>
                <Badge variant="secondary" className="text-xs">
                  Încredere: {Math.round(extractedMetadata.confidence * 100)}%
                </Badge>
              </div>

              <div className="grid grid-cols-1 gap-2 text-sm">
                {Object.entries(extractedMetadata.extractedData)
                  .filter(([_, value]) => value && value.trim() !== "")
                  .map(([field, value]) => (
                    <div key={field} className="flex items-center space-x-2">
                      {getMetadataIcon(field)}
                      <span className="font-medium text-gray-700 min-w-0 flex-shrink-0">
                        {getFieldLabel(field)}:
                      </span>
                      <span className="text-gray-900 truncate" title={value}>
                        {value}
                      </span>
                    </div>
                  ))}
              </div>

              <p className="text-xs text-blue-600 mt-2">
                Procesat la:{" "}
                {new Date(extractedMetadata.processingDate).toLocaleDateString(
                  "ro-RO",
                  {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  }
                )}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Personal Document Upload Dialog */}
      <PersonalDocumentUploadDialog
        isOpen={isUploadDialogOpen}
        onClose={() => setIsUploadDialogOpen(false)}
        onDocumentProcessed={handleDocumentProcessed}
        documentType={docType}
      />
    </>
  );
};

export default DocumentUploadCard;
