
import React from 'react';
import { Search, Filter, SortAsc, SortDesc } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { SortField } from '@/utils/documentUtils';

interface DocumentFilterProps {
  searchTerm: string;
  filterAuthority: string;
  filterDocumentType: string;
  sortBy: SortField;
  sortOrder: 'asc' | 'desc';
  onSearchChange: (value: string) => void;
  onAuthorityChange: (value: string) => void;
  onDocumentTypeChange: (value: string) => void;
  onSortByChange: (value: SortField) => void;
  onSortOrderToggle: () => void;
}

/**
 * Advanced filtering component for documents
 */
const DocumentFilter: React.FC<DocumentFilterProps> = ({
  searchTerm,
  filterAuthority,
  filterDocumentType,
  sortBy,
  sortOrder,
  onSearchChange,
  onAuthorityChange,
  onDocumentTypeChange,
  onSortByChange,
  onSortOrderToggle
}) => {
  return (
    <Card className="shadow-sm border-gray-200">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center space-x-2 text-lg">
          <Filter className="h-5 w-5 text-primary-600" />
          <span>Filtrare și căutare avansată</span>
        </CardTitle>
        <CardDescription>
          Utilizează filtrele de mai jos pentru a găsi rapid documentele dorite
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="relative lg:col-span-2">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Caută în documente..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-10 h-10"
            />
          </div>
          
          <Select value={filterAuthority} onValueChange={onAuthorityChange}>
            <SelectTrigger className="h-10">
              <SelectValue placeholder="Toate autoritățile" />
            </SelectTrigger>
            <SelectContent className="bg-white border shadow-lg">
              <SelectItem value="all">Toate autoritățile</SelectItem>
              <SelectItem value="Primăria">Primăria</SelectItem>
              <SelectItem value="ANAF">ANAF</SelectItem>
              <SelectItem value="DEPABD">DEPABD</SelectItem>
              <SelectItem value="Consiliul">Consiliul Local</SelectItem>
              <SelectItem value="Tribunalul">Tribunalul</SelectItem>
              <SelectItem value="Notariat">Notariat Public</SelectItem>
            </SelectContent>
          </Select>

          <Select value={filterDocumentType} onValueChange={onDocumentTypeChange}>
            <SelectTrigger className="h-10">
              <SelectValue placeholder="Tip document" />
            </SelectTrigger>
            <SelectContent className="bg-white border shadow-lg">
              <SelectItem value="all">Toate tipurile</SelectItem>
              <SelectItem value="Certificat">Certificate</SelectItem>
              <SelectItem value="Autorizație">Autorizații</SelectItem>
              <SelectItem value="Declarație">Declarații</SelectItem>
              <SelectItem value="Contract">Contracte</SelectItem>
              <SelectItem value="Formular">Formulare</SelectItem>
            </SelectContent>
          </Select>

          <div className="flex items-center space-x-2">
            <Select value={sortBy} onValueChange={onSortByChange}>
              <SelectTrigger className="h-10">
                <SelectValue placeholder="Sortează după" />
              </SelectTrigger>
              <SelectContent className="bg-white border shadow-lg">
                <SelectItem value="date">Data</SelectItem>
                <SelectItem value="name">Nume</SelectItem>
                <SelectItem value="authority">Autoritate</SelectItem>
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              size="sm"
              onClick={onSortOrderToggle}
              className="h-10 px-3"
            >
              {sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default DocumentFilter;
