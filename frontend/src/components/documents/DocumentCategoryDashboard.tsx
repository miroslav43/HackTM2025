import { Button } from "@/components/ui/button";
import { useDocumentFilter } from "@/hooks/useDocumentFilter";
import { Document, DocumentCategory } from "@/utils/documentUtils";
import { ArrowLeft } from "lucide-react";
import React from "react";
import DocumentFilter from "./DocumentFilter";
import DocumentTable from "./DocumentTable";

interface DocumentCategoryDashboardProps {
  category: DocumentCategory;
  documents: Document[];
  onBackToCategories: () => void;
}

/**
 * Dashboard component for a specific document category
 */
const DocumentCategoryDashboard: React.FC<DocumentCategoryDashboardProps> = ({
  category,
  documents,
  onBackToCategories,
}) => {
  const {
    searchTerm,
    sortBy,
    sortOrder,
    filterAuthority,
    filterDocumentType,
    filteredDocuments,
    hasActiveFilters,
    setSearchTerm,
    setSortBy,
    setFilterAuthority,
    setFilterDocumentType,
    resetFilters,
    toggleSortOrder,
  } = useDocumentFilter({
    documents,
    selectedCategory: category.id,
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header cu navigare înapoi */}
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          onClick={onBackToCategories}
          className="hover:bg-primary-50 hover:text-primary-700"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Înapoi la categorii
        </Button>
        <div className="flex items-center space-x-3">
          <div
            className={`p-3 rounded-lg ${category.color} text-white shadow-sm`}
          >
            <category.icon className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {category.name}
            </h1>
            <p className="text-gray-600">{category.description}</p>
          </div>
        </div>
      </div>

      {/* Filtre și căutare avansată */}
      <DocumentFilter
        searchTerm={searchTerm}
        filterAuthority={filterAuthority}
        filterDocumentType={filterDocumentType}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSearchChange={setSearchTerm}
        onAuthorityChange={setFilterAuthority}
        onDocumentTypeChange={setFilterDocumentType}
        onSortByChange={setSortBy}
        onSortOrderToggle={toggleSortOrder}
      />

      {/* Statistici */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <p className="text-gray-600">
            <span className="font-semibold text-gray-900">
              {filteredDocuments.length}
            </span>{" "}
            documente găsite
          </p>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={resetFilters}
              className="text-primary-600 hover:text-primary-700 hover:bg-primary-50"
            >
              Resetează filtrele
            </Button>
          )}
        </div>
      </div>

      {/* Tabel cu documente */}
      <DocumentTable documents={filteredDocuments} />
    </div>
  );
};

export default DocumentCategoryDashboard;
