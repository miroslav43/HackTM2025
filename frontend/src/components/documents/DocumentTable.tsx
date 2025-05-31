import { archiveApi } from "@/api/archiveApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Document, getStatusColor, getStatusText } from "@/utils/documentUtils";
import { Building, Calendar, Download, FileText } from "lucide-react";
import React from "react";

interface DocumentTableProps {
  documents: Document[];
}

/**
 * Handle document download from archive
 */
const handleArchiveDownload = async (doc: Document) => {
  try {
    console.log(`Descărcare document: ${doc.title}`);
    const blob = await archiveApi.downloadDocument(doc.id);

    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = doc.title;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Error downloading document:", err);
    alert("Eroare la descărcarea documentului. Vă rugăm să încercați din nou.");
  }
};

/**
 * Table component for displaying documents with download functionality
 */
const DocumentTable: React.FC<DocumentTableProps> = ({ documents }) => {
  if (documents.length === 0) {
    return (
      <Card className="shadow-sm border-gray-200">
        <CardContent className="p-0">
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nu s-au găsit documente
            </h3>
            <p className="text-gray-500">
              Încearcă să modifici filtrele pentru a găsi documentele dorite.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm border-gray-200">
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-gray-200 bg-gray-50">
              <TableHead className="font-semibold text-gray-900">
                Document
              </TableHead>
              <TableHead className="font-semibold text-gray-900">Tip</TableHead>
              <TableHead className="font-semibold text-gray-900">
                Autoritate
              </TableHead>
              <TableHead className="font-semibold text-gray-900">
                Data
              </TableHead>
              <TableHead className="font-semibold text-gray-900">
                Status
              </TableHead>
              <TableHead className="font-semibold text-gray-900 text-right">
                Acțiuni
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((doc, index) => (
              <TableRow
                key={doc.id}
                className="hover:bg-gray-50 transition-colors animate-scale-in border-b border-gray-100"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <TableCell>
                  <div>
                    <div className="font-medium text-gray-900 mb-1">
                      {doc.title}
                    </div>
                    {doc.description && (
                      <div className="text-sm text-gray-500">
                        {doc.description}
                      </div>
                    )}
                    <div className="text-xs text-gray-400 mt-1">{doc.size}</div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-gray-400" />
                    <span className="text-sm">{doc.type}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center space-x-2">
                    <Building className="h-4 w-4 text-gray-400" />
                    <span className="text-sm">{doc.authority}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <span className="text-sm">{doc.date}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge className={`${getStatusColor(doc.status)} border`}>
                    {getStatusText(doc.status)}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    size="sm"
                    onClick={() => handleArchiveDownload(doc)}
                    className="bg-primary-600 hover:bg-primary-700 text-white"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Descarcă
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};

export default DocumentTable;
