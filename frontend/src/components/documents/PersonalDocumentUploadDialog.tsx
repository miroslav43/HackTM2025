/**
 * Personal Document Upload Dialog
 * Provides options for scanning from printer or manual upload
 * Uses Gemini AI for metadata extraction from personal documents
 */

import { uploadDocumentWithOCR } from "@/api/documentsApi";
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
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { AlertCircle, Check, FileText, Scan, Upload } from "lucide-react";
import React, { useState } from "react";

interface PersonalDocumentUploadDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onDocumentProcessed: (metadata: PersonalDocumentMetadata) => void;
  documentType: {
    id: string;
    name: string;
    description: string;
  };
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

const PersonalDocumentUploadDialog: React.FC<
  PersonalDocumentUploadDialogProps
> = ({ isOpen, onClose, onDocumentProcessed, documentType }) => {
  const { toast } = useToast();
  const [selectedMethod, setSelectedMethod] = useState<
    "scan" | "upload" | null
  >(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<PersonalDocumentMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleMethodSelect = (method: "scan" | "upload") => {
    setSelectedMethod(method);
    setError(null);
    setResult(null);
    setProgress(0);
  };

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
      "application/pdf",
    ];
    if (!allowedTypes.includes(file.type)) {
      toast({
        title: "Format neacceptat",
        description: "Doar imagini (JPG, PNG, WebP) și PDF-uri sunt acceptate.",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: "Fișier prea mare",
        description: "Fișierul nu poate depăși 10MB.",
        variant: "destructive",
      });
      return;
    }

    await processDocument(file);
  };

  const handleScanFromPrinter = async () => {
    setIsProcessing(true);
    setProgress(10);

    try {
      // Call scanning API
      const response = await fetch("/api/personal-documents/scan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          documentType: documentType.id,
        }),
      });

      setProgress(50);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Scanarea a eșuat");
      }

      const result = await response.json();
      setProgress(100);

      if (result.success) {
        setResult(result.metadata);
        onDocumentProcessed(result.metadata);
        toast({
          title: "Scanare completă!",
          description: `Documentul a fost scanat și procesat cu succes.`,
        });
      } else {
        throw new Error(result.error || "Procesarea a eșuat");
      }
    } catch (error) {
      console.error("Scan error:", error);
      setError(error instanceof Error ? error.message : "Eroare la scanare");
      toast({
        title: "Eroare la scanare",
        description:
          error instanceof Error
            ? error.message
            : "A apărut o eroare neprevăzută",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const processDocument = async (file: File) => {
    setIsProcessing(true);
    setProgress(10);

    try {
      setProgress(30);

      // Use the new API function for upload with OCR
      const result = await uploadDocumentWithOCR(file, documentType.id);

      setProgress(70);

      if (result.success && result.metadata) {
        setProgress(100);

        // Convert OCR metadata to PersonalDocumentMetadata format
        const personalMetadata: PersonalDocumentMetadata = {
          id: result.metadata.id || "temp-id",
          extractedData: result.metadata.extractedData,
          confidence: result.metadata.confidence,
          filePath: result.metadata.filePath || "",
          fileSize: result.metadata.fileSize || file.size,
          processingDate:
            result.metadata.processingDate || new Date().toISOString(),
        };

        setResult(personalMetadata);
        onDocumentProcessed(personalMetadata);

        toast({
          title: "Document procesat cu succes!",
          description: `Informațiile au fost extrase automat cu ${Math.round(
            result.metadata.confidence * 100
          )}% încredere.`,
        });
      } else {
        throw new Error(result.error || "Procesarea a eșuat");
      }
    } catch (error) {
      console.error("Upload error:", error);
      setError(error instanceof Error ? error.message : "Eroare la încărcare");
      toast({
        title: "Eroare la încărcare",
        description:
          error instanceof Error
            ? error.message
            : "A apărut o eroare neprevăzută",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    setSelectedMethod(null);
    setIsProcessing(false);
    setProgress(0);
    setResult(null);
    setError(null);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>Înlocuire: {documentType.name}</span>
          </DialogTitle>
          <DialogDescription>
            Alegeți modul de încărcare și procesare cu AI pentru extragerea
            metadatelor
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {!selectedMethod && !result && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Scan Option */}
              <Card
                className="cursor-pointer hover:shadow-md transition-shadow border-2 hover:border-primary-200"
                onClick={() => handleMethodSelect("scan")}
              >
                <CardHeader className="text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <Scan className="h-6 w-6 text-blue-600" />
                  </div>
                  <CardTitle className="text-lg">
                    Scanare din imprimantă
                  </CardTitle>
                  <CardDescription>
                    Scanează direct prin NAPS2 și procesează cu AI
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center space-x-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Scanare automată</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Procesare AI imediată</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Calitate optimă</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Upload Option */}
              <Card
                className="cursor-pointer hover:shadow-md transition-shadow border-2 hover:border-primary-200"
                onClick={() => handleMethodSelect("upload")}
              >
                <CardHeader className="text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <Upload className="h-6 w-6 text-green-600" />
                  </div>
                  <CardTitle className="text-lg">Încărcare manuală</CardTitle>
                  <CardDescription>
                    Încarcă imagine sau PDF și procesează cu AI
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center space-x-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Imagini și PDF-uri</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Procesare AI imediată</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Flexibilitate maximă</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* File Upload Interface */}
          {selectedMethod === "upload" && !result && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="h-5 w-5" />
                  <span>Selectați fișierul</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                    disabled={isProcessing}
                  />
                  <label
                    htmlFor="file-upload"
                    className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-400 transition-colors block"
                  >
                    <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                    <p className="text-gray-600 font-medium">
                      Faceți clic pentru a selecta fișierul
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      JPG, PNG, WebP sau PDF (max. 10MB)
                    </p>
                  </label>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Scan Interface */}
          {selectedMethod === "scan" && !result && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Scan className="h-5 w-5" />
                  <span>Scanare document</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center space-y-4">
                  <p className="text-gray-600">
                    Pregătiți documentul în scanner și apăsați butonul pentru a
                    începe scanarea.
                  </p>
                  <Button
                    onClick={handleScanFromPrinter}
                    disabled={isProcessing}
                    size="lg"
                    className="w-full"
                  >
                    {isProcessing ? (
                      <>Se scanează...</>
                    ) : (
                      <>
                        <Scan className="h-5 w-5 mr-2" />
                        Începe scanarea
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Progress Bar */}
          {isProcessing && (
            <Card>
              <CardContent className="p-6">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Procesare cu inteligența artificială...</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} className="h-2" />
                  <p className="text-xs text-gray-500 text-center">
                    Se extrag metadatele din document...
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error Display */}
          {error && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2 text-red-600">
                  <AlertCircle className="h-5 w-5" />
                  <span className="font-medium">Eroare</span>
                </div>
                <p className="text-red-700 mt-1">{error}</p>
                <Button
                  onClick={() => setSelectedMethod(null)}
                  variant="outline"
                  size="sm"
                  className="mt-3"
                >
                  Încearcă din nou
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Results Display */}
          {result && (
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-green-800">
                  <Check className="h-5 w-5" />
                  <span>Document procesat cu succes</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    {result.extractedData.nume && (
                      <div>
                        <span className="font-medium text-gray-700">Nume:</span>
                        <p className="text-gray-900">
                          {result.extractedData.nume}
                        </p>
                      </div>
                    )}
                    {result.extractedData.cnp && (
                      <div>
                        <span className="font-medium text-gray-700">CNP:</span>
                        <p className="text-gray-900">
                          {result.extractedData.cnp}
                        </p>
                      </div>
                    )}
                    {result.extractedData.serieNumar && (
                      <div>
                        <span className="font-medium text-gray-700">
                          Serie/Număr:
                        </span>
                        <p className="text-gray-900">
                          {result.extractedData.serieNumar}
                        </p>
                      </div>
                    )}
                    {result.extractedData.dataEmiterii && (
                      <div>
                        <span className="font-medium text-gray-700">
                          Data emiterii:
                        </span>
                        <p className="text-gray-900">
                          {result.extractedData.dataEmiterii}
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t">
                    <Badge variant="secondary">
                      Încredere AI: {Math.round(result.confidence * 100)}%
                    </Badge>
                    <Button onClick={handleClose}>Închide</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PersonalDocumentUploadDialog;
