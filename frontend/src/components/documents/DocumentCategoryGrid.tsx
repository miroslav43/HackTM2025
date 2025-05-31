
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DocumentCategory } from '@/utils/documentUtils';

interface DocumentCategoryGridProps {
  categories: DocumentCategory[];
  onCategorySelect: (categoryId: string) => void;
}

/**
 * Grid component for displaying document categories
 */
const DocumentCategoryGrid: React.FC<DocumentCategoryGridProps> = ({ 
  categories, 
  onCategorySelect 
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {categories.map((category, index) => (
        <Card 
          key={category.id} 
          className="hover-lift cursor-pointer animate-scale-in shadow-sm border-gray-200 hover:shadow-md hover:border-primary-200 transition-all duration-200"
          style={{ animationDelay: `${index * 0.1}s` }}
          onClick={() => onCategorySelect(category.id)}
        >
          <CardHeader className="text-center">
            <div className={`w-16 h-16 mx-auto rounded-lg ${category.color} flex items-center justify-center text-white mb-4 shadow-sm`}>
              <category.icon className="h-8 w-8" />
            </div>
            <CardTitle className="text-lg text-gray-900">{category.name}</CardTitle>
            <CardDescription className="text-center text-gray-600">
              {category.description}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-center">
              <Badge variant="secondary" className="bg-gray-100 text-gray-700">
                {category.documentCount} documente
              </Badge>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default DocumentCategoryGrid;
