import {
  autoArchiveApi,
  AutoArchiveMetadata,
  AutoArchiveResponse,
} from "@/api/autoArchiveApi";
import { Alert, AlertDescription } from "@/components/ui/alert";
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
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Printer,
  Scan,
  Sparkles,
  Tag,
  Zap,
} from "lucide-react";
import React, { useEffect, useState } from "react";

interface ServiceInfo {
  features: {
    basic_scanning: boolean;
    ocr_processing: boolean;
    auto_archive_upload: boolean;
    auto_archive_scan: boolean;
  };
  naps2_found: boolean;
  ocr_enabled: boolean;
}

const AutoArchiveScan: React.FC = () => {
  const { toast } = useToast();
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [documentType, setDocumentType] = useState("");
  const [result, setResult] = useState<AutoArchiveResponse | null>(null);
  const [serviceInfo, setServiceInfo] = useState<ServiceInfo | null>(null);
  const [isLoadingInfo, setIsLoadingInfo] = useState(true);

  // Load service information on component mount
  useEffect(() => {
    loadServiceInfo();
  }, []);

  const loadServiceInfo = async () => {
    try {
      setIsLoadingInfo(true);
      const info = await autoArchiveApi.getServiceInfo();
      setServiceInfo(info);
    } catch (error) {
      console.error("Failed to load service info:", error);
      toast({
        title: "Eroare conectare",
        description: "Nu s-a putut conecta la serviciul de scanare.",
        variant: "destructive",
      });
    } finally {
      setIsLoadingInfo(false);
    }
  };

  const startScan = async () => {
    if (!serviceInfo?.features.auto_archive_scan) {
      toast({
        title: "Serviciu indisponibil",
        description:
          "Scanarea automată nu este disponibilă. Verificați configurația.",
        variant: "destructive",
      });
      return;
    }

    setIsScanning(true);
    setScanProgress(0);
    setResult(null);

    try {
      // Simulate progress stages
      const progressStages = [
        { progress: 20, message: "Inițializare scanner..." },
        { progress: 40, message: "Scanare document..." },
        { progress: 60, message: "Procesare OCR..." },
        { progress: 80, message: "Extragere metadate..." },
        { progress: 95, message: "Salvare în arhivă..." },
      ];

      let currentStage = 0;
      const progressInterval = setInterval(() => {
        if (currentStage < progressStages.length) {
          setScanProgress(progressStages[currentStage].progress);
          currentStage++;
        } else {
          clearInterval(progressInterval);
        }
      }, 1000);

      const response = await autoArchiveApi.scanAndAutoArchive(
        documentType || undefined
      );

      clearInterval(progressInterval);
      setScanProgress(100);

      if (response.success) {
        setResult(response);
        toast({
          title: "Scanare completă",
          description: `Documentul "${response.metadata?.title}" a fost scanat și adăugat automat în arhivă.`,
        });
      } else {
        throw new Error(response.error || "Scanarea a eșuat");
      }
    } catch (error) {
      console.error("Scan error:", error);
      toast({
        title: "Eroare la scanare",
        description:
          error instanceof Error
            ? error.message
            : "A apărut o eroare necunoscută.",
        variant: "destructive",
      });
      setResult({
        success: false,
        error: error instanceof Error ? error.message : "Eroare necunoscută",
      });
    } finally {
      setIsScanning(false);
      setTimeout(() => setScanProgress(0), 2000);
    }
  };

  const resetForm = () => {
    setResult(null);
    setDocumentType("");
    setScanProgress(0);
  };

  if (isLoadingInfo) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">
            Se încarcă informațiile serviciului...
          </p>
        </div>
      </div>
    );
  }

  const canScan =
    serviceInfo?.features.auto_archive_scan &&
    serviceInfo?.naps2_found &&
    serviceInfo?.ocr_enabled;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <Card className="bg-gradient-to-r from-green-600 to-teal-600 text-white">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Zap className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">
                Scan din imprimantă - Automat
              </h1>
              <p className="opacity-90">
                Scanați un document direct din imprimantă cu procesare automată
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Service Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Printer className="h-5 w-5" />
            <span>Status serviciu</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ServiceStatusItem
              label="Scanner (NAPS2)"
              status={serviceInfo?.naps2_found || false}
              description="Software de scanare"
            />
            <ServiceStatusItem
              label="OCR Processing"
              status={serviceInfo?.ocr_enabled || false}
              description="Procesare text cu AI"
            />
            <ServiceStatusItem
              label="Auto Archive"
              status={serviceInfo?.features.auto_archive_scan || false}
              description="Arhivare automată"
            />
          </div>

          {!canScan && (
            <Alert className="mt-4">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                {!serviceInfo?.naps2_found && "NAPS2 nu este instalat. "}
                {!serviceInfo?.ocr_enabled &&
                  "Serviciul OCR nu este configurat. "}
                Verificați configurația pentru a activa scanarea automată.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scan Controls */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Scan className="h-5 w-5" />
              <span>Control scanare</span>
            </CardTitle>
            <CardDescription>
              Configurați și inițiați scanarea documentului
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
                disabled={isScanning || !canScan}
              />
            </div>

            {/* Scan Instructions */}
            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">
                Instrucțiuni scanare:
              </h4>
              <ol className="text-sm text-blue-800 space-y-1">
                <li>1. Plasați documentul în scanner</li>
                <li>2. Asigurați-vă că documentul este drept</li>
                <li>3. Faceți clic pe "Începe scanarea"</li>
                <li>4. Urmați instrucțiunile de pe ecranul scannerului</li>
              </ol>
            </div>

            {/* Scan Button */}
            <Button
              onClick={startScan}
              disabled={isScanning || !canScan}
              className="w-full"
              size="lg"
            >
              {isScanning ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Scanare în curs...
                </>
              ) : (
                <>
                  <Scan className="h-4 w-4 mr-2" />
                  Începe scanarea
                </>
              )}
            </Button>

            {/* Progress Bar */}
            {isScanning && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Procesare automată...</span>
                  <span>{scanProgress}%</span>
                </div>
                <Progress value={scanProgress} className="h-3" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5" />
              <span>Rezultat scanare</span>
            </CardTitle>
            <CardDescription>
              Metadate generate automat din documentul scanat
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!result && !isScanning && (
              <div className="text-center py-8 text-gray-500">
                <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Inițiați scanarea pentru a vedea rezultatele</p>
              </div>
            )}

            {isScanning && (
              <div className="text-center py-8">
                <div className="animate-pulse">
                  <FileText className="h-12 w-12 mx-auto mb-4 text-blue-600" />
                </div>
                <p className="text-gray-600">
                  Scanare și procesare automată...
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Documentul este scanat, procesat cu OCR și adăugat în arhivă
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
                        Scanare completă cu succes
                      </span>
                    </div>

                    {result.metadata && (
                      <MetadataDisplay metadata={result.metadata} />
                    )}

                    {result.document_id && (
                      <div className="mt-4 p-3 bg-green-50 rounded-lg">
                        <p className="text-sm font-medium text-green-900">
                          ID Document: {result.document_id}
                        </p>
                      </div>
                    )}

                    <Button
                      onClick={resetForm}
                      variant="outline"
                      className="w-full"
                    >
                      Scanează alt document
                    </Button>
                  </>
                ) : (
                  <>
                    <div className="flex items-center space-x-2 text-red-600">
                      <AlertCircle className="h-5 w-5" />
                      <span className="font-medium">Eroare la scanare</span>
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

// Service Status Item Component
const ServiceStatusItem: React.FC<{
  label: string;
  status: boolean;
  description: string;
}> = ({ label, status, description }) => {
  return (
    <div className="flex items-center space-x-3 p-3 border rounded-lg">
      <div
        className={`w-3 h-3 rounded-full ${
          status ? "bg-green-500" : "bg-red-500"
        }`}
      />
      <div className="flex-1">
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
      <Badge variant={status ? "default" : "destructive"} className="text-xs">
        {status ? "Activ" : "Inactiv"}
      </Badge>
    </div>
  );
};

// Component for displaying extracted metadata (reused from upload component)
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

export default AutoArchiveScan;
