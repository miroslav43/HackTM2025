/**
 * Single document upload card component
 * Handles individual document type upload and display
 */

import {
  DocumentData,
  downloadDocument,
  getDocumentOCRMetadata,
  OCRMetadata,
} from "@/api/documentsApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Calendar,
  Check,
  Clock,
  Copy,
  CreditCard,
  Download,
  Eye,
  FileText,
  MapPin,
  Upload,
  User,
  UserPlus,
  X,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { toast } from "sonner";
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
  onProfileDataUpdate?: (data: any) => void;
}

const DocumentUploadCard: React.FC<DocumentUploadCardProps> = ({
  docType,
  existingDoc,
  onFileUpload,
  onProfileDataUpdate,
}) => {
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [extractedMetadata, setExtractedMetadata] =
    useState<PersonalDocumentMetadata | null>(null);
  const [ocrMetadata, setOcrMetadata] = useState<OCRMetadata | null>(null);
  const [isLoadingOCR, setIsLoadingOCR] = useState(false);
  const [showJsonView, setShowJsonView] = useState(false);
  const [isDetailViewOpen, setIsDetailViewOpen] = useState(false);

  // Load OCR metadata when document exists
  useEffect(() => {
    if (existingDoc && existingDoc.id) {
      loadOCRMetadata();
    }
  }, [existingDoc]);

  const loadOCRMetadata = async () => {
    if (!existingDoc?.id) return;

    try {
      setIsLoadingOCR(true);
      const metadata = await getDocumentOCRMetadata(existingDoc.id);
      setOcrMetadata(metadata);
    } catch (error) {
      console.error("Error loading OCR metadata:", error);
    } finally {
      setIsLoadingOCR(false);
    }
  };

  const handleDownload = async () => {
    if (!existingDoc?.id) return;

    try {
      const blob = await downloadDocument(existingDoc.id);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = existingDoc.name || "document";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success("Document descărcat cu succes!");
    } catch (error) {
      console.error("Error downloading document:", error);
      toast.error("Eroare la descărcarea documentului");
    }
  };

  const handleViewDetails = () => {
    setIsDetailViewOpen(true);
  };

  const handleUpdateProfile = () => {
    if (!ocrMetadata?.extractedData && !extractedMetadata?.extractedData) {
      toast.error("Nu există date pentru actualizarea profilului");
      return;
    }

    const dataToUpdate =
      ocrMetadata?.extractedData || extractedMetadata?.extractedData;

    // Prepare profile data from OCR
    const profileData = {
      name: `${dataToUpdate?.prenume || ""} ${dataToUpdate?.nume || ""}`.trim(),
      cnp: dataToUpdate?.cnp,
      address: dataToUpdate?.adresa,
      // Add more fields as needed
    };

    if (onProfileDataUpdate) {
      onProfileDataUpdate(profileData);
      toast.success("Datele din document au fost aplicate la profil!");
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copiat în clipboard!`);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "verified":
        return <Check className="h-4 w-4 text-green-600" />;
      case "rejected":
        return <X className="h-4 w-4 text-red-600" />;
      case "pending":
        return <Clock className="h-4 w-4 text-blue-600" />;
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
        return "bg-blue-100 text-blue-800 border-blue-200";
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
    // Reload OCR metadata after new upload
    loadOCRMetadata();
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
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleViewDetails}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleDownload}>
                    <Download className="h-4 w-4" />
                  </Button>
                </>
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

          {/* Display OCR metadata from backend */}
          {ocrMetadata && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-blue-900 flex items-center space-x-2">
                  <FileText className="h-4 w-4" />
                  <span>Informații extrase cu AI</span>
                </h4>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary" className="text-xs">
                    Încredere: {Math.round(ocrMetadata.confidence * 100)}%
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowJsonView(!showJsonView)}
                    className="text-xs h-6"
                  >
                    {showJsonView ? "Ascunde JSON" : "Vezi JSON"}
                  </Button>
                  {(ocrMetadata.extractedData.nume ||
                    ocrMetadata.extractedData.prenume) && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleUpdateProfile}
                      className="text-xs h-6"
                    >
                      <UserPlus className="h-3 w-3 mr-1" />
                      Aplică la Profil
                    </Button>
                  )}
                </div>
              </div>

              {showJsonView ? (
                <div className="bg-gray-800 text-green-400 p-3 rounded font-mono text-xs overflow-auto max-h-60">
                  <pre>
                    {JSON.stringify(ocrMetadata.extractedData, null, 2)}
                  </pre>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-2 text-sm">
                  {Object.entries(ocrMetadata.extractedData)
                    .filter(
                      ([_, value]) =>
                        value &&
                        typeof value === "string" &&
                        value.trim() !== ""
                    )
                    .map(([field, value]) => (
                      <div key={field} className="flex items-center space-x-2">
                        {getMetadataIcon(field)}
                        <span className="font-medium text-gray-700 min-w-0 flex-shrink-0">
                          {getFieldLabel(field)}:
                        </span>
                        <span
                          className="text-gray-900 truncate flex-1"
                          title={value}
                        >
                          {value}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            copyToClipboard(value, getFieldLabel(field))
                          }
                          className="h-6 w-6 p-0 hover:bg-blue-100"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                </div>
              )}

              <p className="text-xs text-blue-600 mt-2">
                Procesat la:{" "}
                {ocrMetadata.analyzedAt
                  ? new Date(ocrMetadata.analyzedAt).toLocaleDateString(
                      "ro-RO",
                      {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      }
                    )
                  : "Necunoscut"}
              </p>
            </div>
          )}

          {/* Loading state for OCR */}
          {isLoadingOCR && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-sm text-gray-600">
                  Se încarcă datele OCR...
                </span>
              </div>
            </div>
          )}

          {/* Display old extracted metadata if available (fallback) */}
          {extractedMetadata && !ocrMetadata && (
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
                  .filter(
                    ([_, value]) =>
                      value && typeof value === "string" && value.trim() !== ""
                  )
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

      {/* Detail View Dialog */}
      <Dialog open={isDetailViewOpen} onOpenChange={setIsDetailViewOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5" />
              <span>Detalii Complete Document</span>
            </DialogTitle>
            <DialogDescription>
              Vizualizează și copiază informațiile extrase din document
            </DialogDescription>
          </DialogHeader>

          {(ocrMetadata || extractedMetadata) && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Informații Extrase</h3>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">
                    Încredere:{" "}
                    {Math.round(
                      (ocrMetadata?.confidence ||
                        extractedMetadata?.confidence ||
                        0) * 100
                    )}
                    %
                  </Badge>
                  {(ocrMetadata?.extractedData.nume ||
                    extractedMetadata?.extractedData.nume) && (
                    <Button onClick={handleUpdateProfile} size="sm">
                      <UserPlus className="h-4 w-4 mr-2" />
                      Aplică la Profil
                    </Button>
                  )}
                </div>
              </div>

              <div className="grid gap-3">
                {Object.entries(
                  ocrMetadata?.extractedData ||
                    extractedMetadata?.extractedData ||
                    {}
                )
                  .filter(
                    ([_, value]) =>
                      value && typeof value === "string" && value.trim() !== ""
                  )
                  .map(([field, value]) => (
                    <div
                      key={field}
                      className="grid grid-cols-4 items-center gap-4 p-3 border rounded-lg"
                    >
                      <div className="flex items-center space-x-2">
                        {getMetadataIcon(field)}
                        <Label className="text-sm font-medium">
                          {getFieldLabel(field)}:
                        </Label>
                      </div>
                      <div className="col-span-2">
                        <Input
                          value={value}
                          readOnly
                          className="bg-gray-50 border-gray-200"
                        />
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          copyToClipboard(value, getFieldLabel(field))
                        }
                        className="w-full"
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        Copiază
                      </Button>
                    </div>
                  ))}
              </div>

              {(ocrMetadata?.transcribedText || extractedMetadata) && (
                <div className="mt-6">
                  <h4 className="text-md font-medium mb-2">Text Complet OCR</h4>
                  <div className="bg-gray-50 p-3 rounded-lg border max-h-40 overflow-y-auto">
                    <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                      {ocrMetadata?.transcribedText ||
                        "Text OCR nu este disponibil"}
                    </pre>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      copyToClipboard(
                        ocrMetadata?.transcribedText || "",
                        "Text OCR"
                      )
                    }
                    className="mt-2"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copiază Text Complet
                  </Button>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default DocumentUploadCard;
