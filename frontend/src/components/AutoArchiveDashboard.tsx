import {
  AlertTriangle,
  CheckCircle,
  FolderOpen,
  RefreshCw,
  Scan,
  Upload,
  XCircle,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { autoArchiveApi } from "../api/autoArchiveApi";
import AutoArchiveStats from "./AutoArchiveStats";
import { Alert, AlertDescription } from "./ui/alert";
import { Badge } from "./ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { useToast } from "./ui/use-toast";

interface ServiceInfo {
  message: string;
  version: string;
  features: {
    basic_scanning: boolean;
    ocr_processing: boolean;
    auto_archive_upload: boolean;
    auto_archive_scan: boolean;
  };
  naps2_found: boolean;
  ocr_enabled: boolean;
  gemini_model?: string;
  authentication_required: boolean;
  required_role: string;
}

const AutoArchiveDashboard: React.FC = () => {
  const { toast } = useToast();
  const [serviceInfo, setServiceInfo] = useState<ServiceInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showStats, setShowStats] = useState(false);

  const loadServiceInfo = async () => {
    try {
      const info = await autoArchiveApi.getServiceInfo();
      setServiceInfo(info);
    } catch (error) {
      console.error("Error loading service info:", error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca informațiile serviciului.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadServiceInfo();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Status Auto-Archive</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!serviceInfo) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertDescription>
          Serviciul Auto-Archive nu este disponibil momentan.
        </AlertDescription>
      </Alert>
    );
  }

  const getStatusIcon = (status: boolean) => {
    return status ? (
      <CheckCircle className="h-5 w-5 text-green-500" />
    ) : (
      <XCircle className="h-5 w-5 text-red-500" />
    );
  };

  const getStatusBadge = (status: boolean) => {
    return (
      <Badge variant={status ? "default" : "destructive"}>
        {status ? "Activ" : "Inactiv"}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Service Status Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{serviceInfo.message}</span>
            <Badge variant="outline">v{serviceInfo.version}</Badge>
          </CardTitle>
          <CardDescription>
            Serviciu automat de scanare, OCR și arhivare cu AI pentru
            documentele administrative românești
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Authentication Requirements */}
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Acces restricționat:</strong> Funcționalitatea necesită
              autentificare ca{" "}
              {serviceInfo.required_role === "official"
                ? "oficial"
                : "utilizator"}
              .
            </AlertDescription>
          </Alert>

          {/* Core Features Status */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <Upload className="h-4 w-4" />
                <span className="text-sm font-medium">Upload PDF</span>
              </div>
              {getStatusIcon(serviceInfo.features.auto_archive_upload)}
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <Scan className="h-4 w-4" />
                <span className="text-sm font-medium">Scanare</span>
              </div>
              {getStatusIcon(serviceInfo.features.auto_archive_scan)}
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <FolderOpen className="h-4 w-4" />
                <span className="text-sm font-medium">OCR Processing</span>
              </div>
              {getStatusIcon(serviceInfo.features.ocr_processing)}
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span className="text-sm font-medium">Auto-Archive</span>
              </div>
              {getStatusIcon(
                serviceInfo.features.auto_archive_upload &&
                  serviceInfo.features.ocr_processing
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Technical Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Configurație Tehnică</CardTitle>
            <CardDescription>
              Detalii despre componentele sistemului
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">OCR Engine</span>
              <div className="flex items-center space-x-2">
                {getStatusBadge(serviceInfo.ocr_enabled)}
                {serviceInfo.gemini_model && (
                  <Badge variant="secondary">{serviceInfo.gemini_model}</Badge>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">NAPS2 Scanner</span>
              <div className="flex items-center space-x-2">
                {getStatusBadge(serviceInfo.naps2_found)}
                {!serviceInfo.naps2_found && (
                  <span className="text-xs text-gray-500">(Windows only)</span>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Smart Categorization</span>
              {getStatusBadge(serviceInfo.features.ocr_processing)}
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Archive Integration</span>
              {getStatusBadge(true)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Funcționalități Disponibile</CardTitle>
            <CardDescription>
              Ce poți face cu sistemul auto-archive
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <h4 className="font-medium">✅ Upload & Procesare</h4>
              <p className="text-sm text-gray-600">
                Încarcă PDF-uri și obține automat metadate extrase cu AI
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium">🖨️ Scanare Directă</h4>
              <p className="text-sm text-gray-600">
                Scanează direct de la imprimantă cu NAPS2{" "}
                {!serviceInfo.naps2_found && "(necesită instalare)"}
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium">🧠 Categorizare Inteligentă</h4>
              <p className="text-sm text-gray-600">
                Matching automat la categorii existente sau creare automată
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium">📚 Integrare Arhivă</h4>
              <p className="text-sm text-gray-600">
                Documentele sunt adăugate automat în arhiva publică
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Navigation to Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Statistici Avansate</span>
            <button
              onClick={() => setShowStats(!showStats)}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              {showStats ? "Ascunde" : "Afișează"} statistici
            </button>
          </CardTitle>
        </CardHeader>
        {showStats && (
          <CardContent>
            <AutoArchiveStats />
          </CardContent>
        )}
      </Card>
    </div>
  );
};

export default AutoArchiveDashboard;
