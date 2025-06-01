/**
 * Personal Information Section Component
 * Displays AI-extracted personal information from processed documents
 */

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import {
  AlertCircle,
  Calendar,
  CreditCard,
  Download,
  Eye,
  FileText,
  MapPin,
  Plus,
  RefreshCw,
  Sparkles,
  Upload,
  User,
} from "lucide-react";
import React, { useEffect, useRef, useState } from "react";

interface ExtractedPersonalData {
  id: string;
  name: string;
  type: string;
  status: string;
  file_path: string;
  file_size: number;
  mime_type?: string;
  verification_progress: number;
  uploaded_at: string;
  extractedData?: {
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
  confidence?: number;
}

const PersonalInfoSection: React.FC = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [personalData, setPersonalData] = useState<ExtractedPersonalData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    name: "",
    type: "id",
    file: null as File | null,
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadPersonalData = async () => {
    if (!user?.id) return;

    setIsLoading(true);
    setIsRefreshing(true);

    try {
      // Fetch user's documents
      const response = await fetch("/api/documents/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load documents");
      }

      const documents = await response.json();

      // Filter for personal documents only (like ID, passport, etc.)
      const personalDocs = documents.filter(
        (doc: any) =>
          doc.type === "id" ||
          doc.name.toLowerCase().includes("identitate") ||
          doc.name.toLowerCase().includes("pasaport") ||
          doc.name.toLowerCase().includes("permis")
      );

      setPersonalData(personalDocs);
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

  const downloadDocument = async (documentId: string, fileName: string) => {
    try {
      const response = await fetch(`/api/documents/${documentId}/download`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to download document");
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

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

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadForm((prev) => ({
        ...prev,
        file,
        name: prev.name || file.name.replace(/\.[^/.]+$/, ""), // Use filename without extension if name is empty
      }));
    }
  };

  const uploadDocument = async () => {
    if (!uploadForm.file || !uploadForm.name.trim()) {
      toast({
        title: "Eroare",
        description:
          "Vă rugăm să selectați un fișier și să introduceți un nume.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", uploadForm.file);
      formData.append("name", uploadForm.name.trim());
      formData.append("type", uploadForm.type);
      formData.append(
        "description",
        "Document personal încărcat din profilul utilizatorului"
      );

      const response = await fetch("/api/documents/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to upload document");
      }

      const uploadedDoc = await response.json();

      toast({
        title: "Succes",
        description:
          "Documentul a fost încărcat cu succes și va fi procesat pentru extragerea datelor.",
      });

      // Reset form
      setUploadForm({ name: "", type: "id", file: null });
      setShowUpload(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      // Refresh the documents list
      loadPersonalData();
    } catch (error) {
      console.error("Error uploading document:", error);
      toast({
        title: "Eroare",
        description: `Nu s-a putut încărca documentul: ${
          error instanceof Error ? error.message : "Eroare necunoscută"
        }`,
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
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
      autoritate: "Autoritate emitentă",
      observatii: "Observații",
    };
    return labels[field] || field;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "verified":
        return "text-green-600 bg-green-100 border-green-200";
      case "pending":
        return "text-yellow-600 bg-yellow-100 border-yellow-200";
      case "rejected":
        return "text-red-600 bg-red-100 border-red-200";
      default:
        return "text-gray-600 bg-gray-100 border-gray-200";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "verified":
        return "Verificat";
      case "pending":
        return "În așteptare";
      case "rejected":
        return "Respins";
      default:
        return "Necunoscut";
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Sparkles className="h-5 w-5" />
            <span>Informații personale extrase cu AI</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-purple-600" />
              <span>Informații personale extrase cu AI</span>
            </CardTitle>
            <CardDescription>
              Date extrase automat din documentele procesate cu inteligența
              artificială
            </CardDescription>
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowUpload(!showUpload)}
            >
              <Plus className="h-4 w-4 mr-2" />
              Încarcă Document
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={loadPersonalData}
              disabled={isRefreshing}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`}
              />
              Actualizează
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Upload Section */}
        {showUpload && (
          <Card className="mb-6 bg-blue-50 border-blue-200">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg flex items-center space-x-2">
                <Upload className="h-5 w-5 text-blue-600" />
                <span>Încărcare Document Personal</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="document-name">Nume Document</Label>
                  <Input
                    id="document-name"
                    placeholder="ex: Carte de identitate"
                    value={uploadForm.name}
                    onChange={(e) =>
                      setUploadForm((prev) => ({
                        ...prev,
                        name: e.target.value,
                      }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="document-type">Tip Document</Label>
                  <Select
                    value={uploadForm.type}
                    onValueChange={(value) =>
                      setUploadForm((prev) => ({ ...prev, type: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selectați tipul" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="id">Carte de identitate</SelectItem>
                      <SelectItem value="other">Pașaport</SelectItem>
                      <SelectItem value="other">Permis de conducere</SelectItem>
                      <SelectItem value="other">Certificat naștere</SelectItem>
                      <SelectItem value="other">Alt document</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="document-file">Fișier</Label>
                <Input
                  id="document-file"
                  type="file"
                  ref={fileInputRef}
                  accept=".jpg,.jpeg,.png,.pdf,.webp"
                  onChange={handleFileSelect}
                  className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                />
                <p className="text-xs text-gray-500">
                  Acceptă: JPG, PNG, PDF, WebP (max. 10MB)
                </p>
              </div>
              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowUpload(false);
                    setUploadForm({ name: "", type: "id", file: null });
                    if (fileInputRef.current) fileInputRef.current.value = "";
                  }}
                >
                  Anulează
                </Button>
                <Button
                  onClick={uploadDocument}
                  disabled={isUploading || !uploadForm.file}
                >
                  {isUploading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Se încarcă...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Încarcă
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Documents List */}
        {personalData.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nu există documente personale încărcate încă
            </h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Încărcați documente personale (CI, pașaport, permis) în secțiunea
              "Documente Personale" pentru a vedea informațiile extrase automat
              cu AI.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {personalData.map((document) => {
              // Add safety checks for document properties
              const safeDocument = {
                id: document?.id || "",
                name: document?.name || "Document necunoscut",
                type: document?.type || "unknown",
                status: document?.status || "pending",
                file_size: document?.file_size || 0,
                uploaded_at: document?.uploaded_at || new Date().toISOString(),
                verification_progress: document?.verification_progress || 0,
                extractedData: document?.extractedData || {},
                confidence: document?.confidence || 0,
              };

              return (
                <div
                  key={safeDocument.id}
                  className="border rounded-lg p-6 bg-gradient-to-r from-purple-50 to-blue-50"
                >
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                        <FileText className="h-6 w-6 text-purple-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 text-lg">
                          {safeDocument.name}
                        </h4>
                        <div className="flex items-center space-x-4 mt-1">
                          <p className="text-sm text-gray-500">
                            Încărcat la:{" "}
                            {new Date(
                              safeDocument.uploaded_at
                            ).toLocaleDateString("ro-RO", {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </p>
                          <p className="text-sm text-gray-500">
                            Mărime: {formatFileSize(safeDocument.file_size)}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge
                        className={`${getStatusColor(
                          safeDocument.status
                        )} border`}
                      >
                        {getStatusText(safeDocument.status)}
                      </Badge>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            downloadDocument(safeDocument.id, safeDocument.name)
                          }
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        Progres verificare
                      </span>
                      <span className="text-sm text-gray-500">
                        {safeDocument.verification_progress}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${safeDocument.verification_progress}%`,
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* Extracted Data */}
                  {Object.keys(safeDocument.extractedData || {}).length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {Object.entries(safeDocument.extractedData || {})
                        .filter(
                          ([_, value]) => value && String(value).trim() !== ""
                        )
                        .map(([field, value]) => (
                          <div
                            key={field}
                            className="bg-white rounded-lg p-3 shadow-sm border"
                          >
                            <div className="flex items-center space-x-2 mb-1">
                              {getFieldIcon(field)}
                              <span className="font-medium text-gray-700 text-sm">
                                {getFieldLabel(field)}
                              </span>
                            </div>
                            <p
                              className="text-gray-900 font-medium"
                              title={String(value)}
                            >
                              {String(value)}
                            </p>
                          </div>
                        ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 bg-white rounded-lg border border-dashed border-gray-300">
                      <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500 text-sm">
                        Datele personale nu au fost încă extrase din acest
                        document
                      </p>
                      <p className="text-gray-400 text-xs mt-1">
                        Procesarea cu AI va fi disponibilă în curând
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PersonalInfoSection;
