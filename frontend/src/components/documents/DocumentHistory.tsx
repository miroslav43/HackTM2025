/**
 * Document history display component
 * Shows all uploaded documents with their status
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
import { Eye, FileText } from "lucide-react";
import React from "react";

interface DocumentHistoryProps {
  documents: DocumentData[];
}

const DocumentHistory: React.FC<DocumentHistoryProps> = ({ documents }) => {
  const getStatusIcon = (status: string) => {
    const icons = {
      verified: "✓",
      rejected: "✗",
      pending: "⏳",
    };
    return icons[status as keyof typeof icons] || "?";
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

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-gray-800">
          Istoricul documentelor încărcate
        </CardTitle>
        <CardDescription className="text-gray-600">
          Toate documentele încărcate și statusul lor
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {documents.map((doc, index) => (
            <div
              key={doc.id}
              className="p-4 border rounded-lg animate-scale-in hover:bg-gray-50 transition-colors"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="font-medium text-gray-800">{doc.name}</p>
                    <p className="text-sm text-gray-600">
                      {doc.size} •{" "}
                      {new Date(doc.uploadDate).toLocaleDateString("ro-RO")}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={`${getStatusColor(doc.status)} border`}>
                    {getStatusIcon(doc.status)} {getStatusText(doc.status)}
                  </Badge>
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default DocumentHistory;
