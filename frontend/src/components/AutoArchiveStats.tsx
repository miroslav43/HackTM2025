import { BarChart3, FolderOpen, RefreshCw, Settings } from "lucide-react";
import React, { useEffect, useState } from "react";
import { autoArchiveApi } from "../api/autoArchiveApi";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { useToast } from "./ui/use-toast";

interface CategoryStat {
  id: string;
  name: string;
  description: string;
  document_count: number;
  created_at: string;
}

interface CategoryStatsData {
  success: boolean;
  total_categories: number;
  max_categories: number;
  categories_remaining: number;
  categories: CategoryStat[];
  auto_archive_info: {
    similarity_threshold: number;
    matching_enabled: boolean;
    auto_creation_enabled: boolean;
  };
}

const AutoArchiveStats: React.FC = () => {
  const { toast } = useToast();
  const [stats, setStats] = useState<CategoryStatsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadStats = async () => {
    try {
      setIsRefreshing(true);
      const data = await autoArchiveApi.getCategoryStats();
      setStats(data);
    } catch (error) {
      console.error("Error loading category stats:", error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca statisticile categoriilor.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>Statistici Auto-Archive</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>Statistici Auto-Archive</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Nu s-au putut încărca statisticile.</p>
        </CardContent>
      </Card>
    );
  }

  const usagePercentage = (stats.total_categories / stats.max_categories) * 100;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Categorii Totale
                </p>
                <p className="text-2xl font-bold">{stats.total_categories}</p>
              </div>
              <FolderOpen className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Categorii Rămase
                </p>
                <p className="text-2xl font-bold text-green-600">
                  {stats.categories_remaining}
                </p>
              </div>
              <Settings className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Utilizare</p>
                <p className="text-2xl font-bold">
                  {usagePercentage.toFixed(1)}%
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Configuration Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Configurație Smart Categorization</span>
            <Button
              variant="outline"
              size="sm"
              onClick={loadStats}
              disabled={isRefreshing}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`}
              />
              Actualizează
            </Button>
          </CardTitle>
          <CardDescription>
            Setări pentru matching-ul automat de categorii
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <p className="text-sm font-medium">Prag de Similaritate</p>
              <Badge variant="secondary">
                {stats.auto_archive_info.similarity_threshold}%
              </Badge>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Matching Activat</p>
              <Badge
                variant={
                  stats.auto_archive_info.matching_enabled
                    ? "default"
                    : "destructive"
                }
              >
                {stats.auto_archive_info.matching_enabled ? "Da" : "Nu"}
              </Badge>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Creare Automată</p>
              <Badge
                variant={
                  stats.auto_archive_info.auto_creation_enabled
                    ? "default"
                    : "destructive"
                }
              >
                {stats.auto_archive_info.auto_creation_enabled
                  ? "Activă"
                  : "Dezactivată (limită atinsă)"}
              </Badge>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Limită Categorii</p>
              <Badge variant="outline">
                {stats.total_categories} / {stats.max_categories}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Categories List */}
      <Card>
        <CardHeader>
          <CardTitle>Categorii Existente</CardTitle>
          <CardDescription>
            Lista categoriilor cu numărul de documente în fiecare
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {stats.categories.map((category) => (
              <div
                key={category.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex-1">
                  <h4 className="font-medium">{category.name}</h4>
                  {category.description && (
                    <p className="text-sm text-gray-600 mt-1">
                      {category.description}
                    </p>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">
                    {category.document_count} doc
                    {category.document_count !== 1 ? "s" : ""}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AutoArchiveStats;
