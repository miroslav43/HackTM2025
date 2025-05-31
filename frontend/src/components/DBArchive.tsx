import {
  archiveApi,
  ArchiveDocument,
  DocumentCategory,
} from "@/api/archiveApi";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Building,
  Download,
  FileCheck,
  FileText,
  Search,
  Users,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import DocumentCategoryDashboard from "./documents/DocumentCategoryDashboard";
import DocumentCategoryGrid from "./documents/DocumentCategoryGrid";

// Icon mapping for categories
const iconMap: Record<string, React.ElementType> = {
  file: FileText,
  users: Users,
  building: Building,
  check: FileCheck,
  default: FileText,
};

// Cache for categories to avoid repeated API calls
let categoriesCache: DocumentCategory[] | null = null;

// Transform archive document to match DocumentUtils Document interface
const transformArchiveDocument = (archiveDoc: ArchiveDocument) => {
  // Handle date parsing safely
  let formattedDate = "Data invalidă";
  try {
    const date = new Date(archiveDoc.created_at);
    if (!isNaN(date.getTime())) {
      formattedDate = date.toLocaleDateString("ro-RO");
    }
  } catch (error) {
    console.warn("Invalid date format:", archiveDoc.created_at);
  }

  return {
    id: archiveDoc.id,
    title: archiveDoc.title,
    type: archiveDoc.mime_type || "application/pdf",
    authority: archiveDoc.authority,
    date: formattedDate,
    category: archiveDoc.category_id || "",
    size: `${(archiveDoc.file_size / 1024 / 1024).toFixed(2)} MB`,
    status: "available" as const,
    description: archiveDoc.description,
  };
};

// Transform archive category for the grid component
const transformArchiveCategory = (archiveCat: DocumentCategory) => ({
  id: archiveCat.id,
  name: archiveCat.name,
  icon: iconMap[archiveCat.icon || "default"] || iconMap.default,
  color: archiveCat.color || "#3B82F6",
  description: archiveCat.description,
  documentCount: archiveCat.document_count,
});

/**
 * Main component for the Document Archive functionality
 * Provides access to official documents organized by categories
 */
const DBArchive = () => {
  const [documents, setDocuments] = useState<ArchiveDocument[]>([]);
  const [categories, setCategories] = useState<DocumentCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  // Listen for archive updates
  useEffect(() => {
    const handleArchiveUpdate = () => {
      console.log("Archive updated, refreshing data...");
      loadInitialData();
    };

    window.addEventListener("archiveUpdated", handleArchiveUpdate);

    return () => {
      window.removeEventListener("archiveUpdated", handleArchiveUpdate);
    };
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use cached categories if available, otherwise fetch
      let categoriesPromise;
      if (categoriesCache) {
        categoriesPromise = Promise.resolve(categoriesCache);
      } else {
        categoriesPromise = archiveApi.getCategories().then((data) => {
          categoriesCache = data;
          return data;
        });
      }

      // Load categories and recent documents in parallel with reduced limit for faster initial load
      const [categoriesData, documentsData] = await Promise.all([
        categoriesPromise,
        archiveApi.searchDocuments({ limit: 8 }), // Reduced from 20 to 8 for faster initial load
      ]);

      setCategories(categoriesData);
      setDocuments(documentsData.items);
    } catch (err) {
      console.error("Error loading archive data:", err);
      setError("Failed to load archive data.");
    } finally {
      setLoading(false);
    }
  };

  const handleCategorySelect = async (categoryId: string) => {
    try {
      setLoading(true);
      setSelectedCategory(categoryId);
      const categoryDocuments = await archiveApi.getDocumentsByCategory(
        categoryId,
        1, // page
        15 // Reduced limit for faster category loading
      );
      setDocuments(categoryDocuments);
    } catch (err) {
      console.error("Error loading category documents:", err);
      setError("Failed to load category documents.");
    } finally {
      setLoading(false);
    }
  };

  const handleBackToCategories = () => {
    setSelectedCategory(null);
    loadInitialData();
  };

  const handleDownload = async (doc: ArchiveDocument) => {
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
      setError("Failed to download document.");
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;

    try {
      setLoading(true);
      const searchResults = await archiveApi.searchDocuments({
        q: searchTerm,
        limit: 12, // Reduced from 20 to 12 for faster search
      });
      setDocuments(searchResults.items);
      setSelectedCategory(null); // Clear category selection when searching
    } catch (err) {
      console.error("Error searching documents:", err);
      setError("Failed to search documents.");
    } finally {
      setLoading(false);
    }
  };

  // Memoized transformations for better performance
  const transformedCategories = useMemo(() => {
    return categories.map(transformArchiveCategory);
  }, [categories]);

  const transformedDocuments = useMemo(() => {
    return documents.map(transformArchiveDocument);
  }, [documents]);

  // Dashboard pentru categoria selectată
  if (selectedCategory) {
    const category = categories.find((c) => c.id === selectedCategory);
    if (!category) return null;

    // Transform category and documents for the dashboard
    const transformedCategory = transformArchiveCategory(category);
    const transformedDocuments = documents.map(transformArchiveDocument);

    return (
      <DocumentCategoryDashboard
        category={transformedCategory}
        documents={transformedDocuments}
        onBackToCategories={handleBackToCategories}
      />
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Se încarcă arhiva...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 mb-4">{error}</div>
        <Button onClick={loadInitialData} variant="outline">
          Încercare din nou
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Search section */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Căutați documente în arhivă..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-white"
                  onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                />
              </div>
            </div>
            <Button onClick={handleSearch} disabled={!searchTerm.trim()}>
              <Search className="h-4 w-4 mr-2" />
              Căutare
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Categories grid */}
      {categories.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-4">Categorii de documente</h2>
          <DocumentCategoryGrid
            categories={transformedCategories}
            onCategorySelect={handleCategorySelect}
          />
        </div>
      )}

      {/* Recent documents */}
      {documents.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-4">Documente recente</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.slice(0, 4).map((doc, index) => (
              <Card
                key={doc.id}
                className="hover-lift animate-scale-in shadow-sm border-gray-200 hover:shadow-md transition-all duration-200"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium mb-1 text-gray-900">
                        {doc.title}
                      </h3>
                      <p className="text-sm text-gray-600">{doc.authority}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDownload(doc)}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {categories.length === 0 && documents.length === 0 && (
        <div className="text-center py-8">
          <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Arhiva este goală
          </h3>
          <p className="text-gray-600">
            Nu există documente în arhivă momentan.
          </p>
        </div>
      )}
    </div>
  );
};

export default DBArchive;
