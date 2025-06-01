/**
 * Personal Information Section Component
 * Displays AI-extracted personal information from processed documents
 */

import { downloadDocument, getDocumentOCRMetadata } from "@/api/documentsApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import {
  AlertCircle,
  Calendar,
  Copy,
  CreditCard,
  Download,
  FileText,
  MapPin,
  RefreshCw,
  Sparkles,
  User,
} from "lucide-react";
import React, { useEffect, useState } from "react";

interface PersonalDocumentWithOCR {
  id: string;
  name: string;
  type: string;
  status: string;
  file_size: number;
  uploaded_at: string;
  verification_progress: number;
  ocrData?: {
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
    transcribedText?: string;
    processingMethod?: string;
    analyzedAt?: string;
  };
}

const PersonalInfoSection: React.FC = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [personalData, setPersonalData] = useState<PersonalDocumentWithOCR[]>(
    []
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadPersonalData = async () => {
    if (!user?.id) return;

    setIsLoading(true);
    setIsRefreshing(true);

    try {
      // Load user documents from the personal documents API
      const response = await fetch(
        `/api/personal-documents/user/${user.id}/documents`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("authToken")}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to load personal documents");
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error("Failed to load personal documents");
      }

      // For each document, try to load OCR metadata
      const documentsWithOCR = await Promise.all(
        result.documents.map(async (doc: any) => {
          try {
            const ocrData = await getDocumentOCRMetadata(doc.id);
            return {
              ...doc,
              ocrData: ocrData,
            };
          } catch (error) {
            console.error(
              `Failed to load OCR data for document ${doc.id}:`,
              error
            );
            return {
              ...doc,
              ocrData: null,
            };
          }
        })
      );

      setPersonalData(documentsWithOCR);
    } catch (error) {
      console.error("Error loading personal data:", error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca informațiile personale.",
        variant: "destructive",
      });
      setPersonalData([]);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleDownload = async (documentId: string, fileName: string) => {
    try {
      const blob = await downloadDocument(documentId);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: "Succes",
        description: "Documentul a fost descărcat cu succes.",
      });
    } catch (error) {
      console.error("Error downloading document:", error);
      toast({
        title: "Eroare",
        description: "Nu s-a putut descărca documentul.",
        variant: "destructive",
      });
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copiat!",
      description: `${label} a fost copiat în clipboard.`,
    });
  };

  useEffect(() => {
    loadPersonalData();
  }, [user]);

  const getFieldIcon = (field: string) => {
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

  const formatFileSize = (bytes: number) => {
    const sizes = ["Bytes", "KB", "MB", "GB"];
    if (bytes === 0) return "0 Bytes";
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + " " + sizes[i];
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-purple-600" />
            <CardTitle>Informații personale extrase cu AI</CardTitle>
          </div>
          <CardDescription>
            Se încarcă documentele personale procesate...
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            <span className="ml-2 text-gray-600">Se încarcă...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-purple-600" />
            <div>
              <CardTitle>Informații personale extrase cu AI</CardTitle>
              <CardDescription>
                Documentele tale personale procesate cu inteligența artificială
              </CardDescription>
            </div>
          </div>
          <Button
            onClick={loadPersonalData}
            disabled={isRefreshing}
            variant="outline"
            size="sm"
          >
            <RefreshCw
              className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`}
            />
            Actualizează
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {personalData.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nu există documente personale
            </h3>
            <p className="text-gray-500 mb-4">
              Încarcă documente în secțiunea "Documente Personale" pentru a
              vedea informațiile extrase cu AI.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {personalData.map((doc) => (
              <div key={doc.id} className="border rounded-lg p-4 space-y-4">
                {/* Document Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-5 w-5 text-gray-600" />
                    <div>
                      <h3 className="font-medium">{doc.name}</h3>
                      <p className="text-sm text-gray-500">
                        Încărcat la{" "}
                        {new Date(doc.uploaded_at).toLocaleDateString("ro-RO")}{" "}
                        • {formatFileSize(doc.file_size)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={`${getStatusColor(doc.status)} border`}>
                      {getStatusText(doc.status)}
                    </Badge>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownload(doc.id, doc.name)}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {/* OCR Data Display */}
                {doc.ocrData ? (
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-blue-900 flex items-center space-x-2">
                        <Sparkles className="h-4 w-4" />
                        <span>Informații extrase cu AI</span>
                      </h4>
                      <Badge variant="secondary" className="text-xs">
                        Încredere: {Math.round(doc.ocrData.confidence * 100)}%
                      </Badge>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {Object.entries(doc.ocrData.extractedData)
                        .filter(
                          ([_, value]) =>
                            value &&
                            typeof value === "string" &&
                            value.trim() !== ""
                        )
                        .map(([field, value]) => (
                          <div
                            key={field}
                            className="flex items-center space-x-2 p-2 bg-white rounded border"
                          >
                            {getFieldIcon(field)}
                            <span className="font-medium text-gray-700 min-w-0 flex-shrink-0">
                              {getFieldLabel(field)}:
                            </span>
                            <span
                              className="text-gray-900 flex-1 truncate"
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

                    <p className="text-xs text-blue-600 mt-3">
                      Procesat la:{" "}
                      {doc.ocrData.analyzedAt
                        ? new Date(doc.ocrData.analyzedAt).toLocaleDateString(
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
                ) : (
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="flex items-center space-x-2 text-gray-600">
                      <AlertCircle className="h-5 w-5" />
                      <div>
                        <p className="font-medium">
                          Datele personale nu au fost încă extrase din acest
                          document
                        </p>
                        <p className="text-sm">
                          Procesarea cu AI va fi disponibilă în curând
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PersonalInfoSection;
