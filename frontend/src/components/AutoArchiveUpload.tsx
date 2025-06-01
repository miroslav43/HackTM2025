import {
  autoArchiveApi,
  AutoArchiveMetadata,
  AutoArchiveResponse,
} from "@/api/autoArchiveApi";
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
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import {
  AlertCircle,
  CheckCircle,
  Clock,
  FileText,
  Sparkles,
  Tag,
  Upload,
} from "lucide-react";
import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

const AutoArchiveUpload: React.FC = () => {
  const { toast } = useToast();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentType, setDocumentType] = useState("");
  const [result, setResult] = useState<AutoArchiveResponse | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];

      if (!file) return;

      // Validate file type
      if (file.type !== "application/pdf") {
        toast({
          title: "Format invalid",
          description: "Doar fișierele PDF sunt acceptate.",
          variant: "destructive",
        });
        return;
      }

      // Validate file size (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        toast({
          title: "Fișier prea mare",
          description: "Fișierul nu poate depăși 50MB.",
          variant: "destructive",
        });
        return;
      }

      await processFile(file);
    },
    [documentType, toast]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
    },
    multiple: false,
    disabled: isUploading,
  });

  const processFile = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);
    setResult(null);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await autoArchiveApi.uploadPdfForAutoArchive(
        file,
        documentType || undefined
      );

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.success) {
        setResult(response);
        toast({
          title: "Procesare completă!",
          description: `Documentul a fost procesat și adăugat automat în arhivă.`,
        });
      } else {
        throw new Error(response.error || "Procesarea a eșuat");
      }
    } catch (error) {
      console.error("Upload error:", error);

      let errorMessage = "A apărut o eroare la procesarea documentului.";
      let errorTitle = "Eroare la procesare";

      if (error instanceof Error) {
        if (
          error.message.includes("Not authenticated") ||
          error.message.includes("403")
        ) {
          errorTitle = "Acces restricționat";
          errorMessage =
            "Doar oficialii pot folosi funcția de auto-arhivare. Vă rugăm să vă autentificați cu un cont oficial.";
        } else if (error.message.includes("401")) {
          errorTitle = "Sesiune expirată";
          errorMessage =
            "Sesiunea dvs. a expirat. Vă rugăm să vă autentificați din nou.";
        } else {
          errorMessage = error.message;
        }
      }

      toast({
        title: errorTitle,
        description: errorMessage,
        variant: "destructive",
      });

      setResult({
        success: false,
        error: errorMessage,
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const resetForm = () => {
    setResult(null);
    setDocumentType("");
    setUploadProgress(0);
  };

  const formatConfidenceScore = (score?: number) => {
    if (!score) return "N/A";
    return `${Math.round(score * 100)}%`;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Sparkles className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Upload PDF - Automat</h1>
              <p className="opacity-90">
                Încărcați un PDF și generați automat metadate pentru arhivă
                folosind AI
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="h-5 w-5" />
              <span>Încărcare document</span>
            </CardTitle>
            <CardDescription>
              Trageți și plasați un fișier PDF sau faceți clic pentru a selecta
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Document Type Input */}
            <div className="space-y-2">
              <Label htmlFor="documentType">Tip document (opțional)</Label>
              <Input
                id="documentType"
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                placeholder="Ex: Regulament, Hotărâre, Contract..."
                disabled={isUploading}
              />
            </div>

            {/* File Upload Area */}
            <div
              {...getRootProps()}
              className={`
                border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
                ${
                  isDragActive
                    ? "border-primary-500 bg-primary-50"
                    : "border-gray-300 hover:border-primary-400 hover:bg-gray-50"
                }
                ${isUploading ? "pointer-events-none opacity-50" : ""}
              `}
            >
              <input {...getInputProps()} />
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
                  <FileText className="h-8 w-8 text-gray-400" />
                </div>
                {isDragActive ? (
                  <p className="text-primary-600 font-medium">
                    Plasați fișierul aici...
                  </p>
                ) : (
                  <div>
                    <p className="text-gray-600 font-medium">
                      Trageți și plasați un fișier PDF aici
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      sau faceți clic pentru a selecta un fișier
                    </p>
                  </div>
                )}
                <p className="text-xs text-gray-400">
                  Doar fișiere PDF, maximum 50MB
                </p>
              </div>
            </div>

            {/* Progress Bar */}
            {isUploading && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Procesare cu AI...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} className="h-2" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5" />
              <span>Rezultat procesare</span>
            </CardTitle>
            <CardDescription>
              Metadate generate automat de inteligența artificială
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!result && !isUploading && (
              <div className="text-center py-8 text-gray-500">
                <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Încărcați un document pentru a vedea rezultatele</p>
              </div>
            )}

            {isUploading && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">
                  Procesare cu inteligența artificială...
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Se extrag metadatele și se adaugă în arhivă
                </p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                {result.success ? (
                  <>
                    <div className="flex items-center space-x-2 text-green-600">
                      <CheckCircle className="h-5 w-5" />
                      <span className="font-medium">
                        Document procesat cu succes
                      </span>
                    </div>

                    {result.metadata && (
                      <MetadataDisplay metadata={result.metadata} />
                    )}

                    {result.document_id && (
                      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm font-medium text-blue-900">
                          ID Document: {result.document_id}
                        </p>
                      </div>
                    )}

                    <Button
                      onClick={resetForm}
                      variant="outline"
                      className="w-full"
                    >
                      Procesează alt document
                    </Button>
                  </>
                ) : (
                  <>
                    <div className="flex items-center space-x-2 text-red-600">
                      <AlertCircle className="h-5 w-5" />
                      <span className="font-medium">Eroare la procesare</span>
                    </div>
                    <p className="text-sm text-gray-600">{result.error}</p>
                    <Button
                      onClick={resetForm}
                      variant="outline"
                      className="w-full"
                    >
                      Încearcă din nou
                    </Button>
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Component for displaying extracted metadata
const MetadataDisplay: React.FC<{ metadata: AutoArchiveMetadata }> = ({
  metadata,
}) => {
  return (
    <div className="space-y-4">
      <Separator />

      <div className="grid grid-cols-1 gap-3">
        <div>
          <Label className="text-sm font-medium text-gray-700">Titlu</Label>
          <p className="text-sm text-gray-900 mt-1">{metadata.title}</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label className="text-sm font-medium text-gray-700">
              Categorie
            </Label>
            <Badge variant="secondary" className="mt-1">
              {metadata.category}
            </Badge>
          </div>
          <div>
            <Label className="text-sm font-medium text-gray-700">
              Autoritate
            </Label>
            <Badge variant="outline" className="mt-1">
              {metadata.authority}
            </Badge>
          </div>
        </div>

        {metadata.document_number && (
          <div>
            <Label className="text-sm font-medium text-gray-700">
              Număr document
            </Label>
            <p className="text-sm text-gray-900 mt-1">
              {metadata.document_number}
            </p>
          </div>
        )}

        {metadata.issue_date && (
          <div>
            <Label className="text-sm font-medium text-gray-700">
              Data emiterii
            </Label>
            <p className="text-sm text-gray-900 mt-1">{metadata.issue_date}</p>
          </div>
        )}

        {metadata.description && (
          <div>
            <Label className="text-sm font-medium text-gray-700">
              Descriere
            </Label>
            <p className="text-sm text-gray-600 mt-1">{metadata.description}</p>
          </div>
        )}

        {metadata.tags && metadata.tags.length > 0 && (
          <div>
            <Label className="text-sm font-medium text-gray-700 flex items-center space-x-1">
              <Tag className="h-3 w-3" />
              <span>Etichete</span>
            </Label>
            <div className="flex flex-wrap gap-1 mt-1">
              {metadata.tags.map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <div className="pt-2">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Încredere AI:</span>
            <span
              className={`font-medium ${
                (metadata.confidence_score || 0) > 0.7
                  ? "text-green-600"
                  : (metadata.confidence_score || 0) > 0.4
                  ? "text-blue-600"
                  : "text-red-600"
              }`}
            >
              {((metadata.confidence_score || 0) * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutoArchiveUpload;
