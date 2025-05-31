import {
  AddToArchiveRequest,
  archiveApi,
  DocumentCategory,
} from "@/api/archiveApi";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { FileText, Plus, Save, Upload } from "lucide-react";
import React, { useEffect, useState } from "react";

const authorities = [
  { id: "primaria", name: "Primăria" },
  { id: "consiliul-local", name: "Consiliul Local" },
  { id: "anaf", name: "ANAF" },
  { id: "prefectura", name: "Prefectura" },
  { id: "politia-locala", name: "Poliția Locală" },
];

const AddToArchive: React.FC = () => {
  const { toast } = useToast();
  const [categories, setCategories] = useState<DocumentCategory[]>([]);
  const [formData, setFormData] = useState({
    title: "",
    category_id: "",
    authority: "",
    date: "",
    description: "",
    tags: "",
    documentNumber: "",
  });
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Load categories from API
  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setIsLoading(true);
      const categoriesData = await archiveApi.getCategories();
      setCategories(categoriesData);
    } catch (error) {
      console.error("Error loading categories:", error);
      toast({
        title: "Eroare",
        description: "Nu s-au putut încărca categoriile. Încercați din nou.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleFileUpload = (files: FileList | null) => {
    if (files && files.length > 0) {
      const file = files[0];

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: "Fișier prea mare",
          description: "Fișierul nu poate depăși 10MB.",
          variant: "destructive",
        });
        return;
      }

      // Validate file type (PDF only)
      if (file.type !== "application/pdf") {
        toast({
          title: "Format invalid",
          description: "Doar fișierele PDF sunt acceptate.",
          variant: "destructive",
        });
        return;
      }

      setUploadedFile(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !formData.title ||
      !formData.category_id ||
      !formData.authority ||
      !uploadedFile
    ) {
      toast({
        title: "Date incomplete",
        description:
          "Vă rugăm să completați toate câmpurile obligatorii și să încărcați un document.",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      // Prepare metadata for API
      const metadata: AddToArchiveRequest = {
        title: formData.title,
        category_id: formData.category_id,
        authority: formData.authority,
        description: formData.description || undefined,
        tags: formData.tags
          ? formData.tags
              .split(",")
              .map((tag) => tag.trim())
              .filter(Boolean)
          : undefined,
      };

      // Add document to archive
      const result = await archiveApi.addToArchive(uploadedFile, metadata);

      toast({
        title: "Document adăugat cu succes",
        description: `Documentul "${formData.title}" a fost adăugat în arhiva oficială.`,
      });

      // Reset form
      setFormData({
        title: "",
        category_id: "",
        authority: "",
        date: "",
        description: "",
        tags: "",
        documentNumber: "",
      });
      setUploadedFile(null);

      // Trigger a custom event to refresh the archive list
      window.dispatchEvent(new CustomEvent("archiveUpdated"));

      console.log("Document added successfully:", result);
    } catch (error) {
      console.error("Error adding document:", error);

      let errorMessage =
        "A apărut o eroare la adăugarea documentului. Încercați din nou.";
      if (error instanceof Error) {
        errorMessage = error.message;
      }

      toast({
        title: "Eroare",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Se încarcă formularul...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <Card className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Plus className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Adaugă Document în Arhivă</h1>
              <p className="opacity-90">
                Încărcați documente oficiale în baza de date arhivă
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Document details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Detalii document</span>
              </CardTitle>
              <CardDescription>
                Informații de bază despre document
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Denumire document *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleInputChange("title", e.target.value)}
                  placeholder="Ex: Regulament urbanism 2024"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="documentNumber">Număr document</Label>
                <Input
                  id="documentNumber"
                  value={formData.documentNumber}
                  onChange={(e) =>
                    handleInputChange("documentNumber", e.target.value)
                  }
                  placeholder="Ex: 123/2024"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="category">Categorie *</Label>
                  <Select
                    value={formData.category_id}
                    onValueChange={(value) =>
                      handleInputChange("category_id", value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selectează categoria" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="authority">Autoritate emitentă *</Label>
                  <Select
                    value={formData.authority}
                    onValueChange={(value) =>
                      handleInputChange("authority", value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selectează autoritatea" />
                    </SelectTrigger>
                    <SelectContent>
                      {authorities.map((authority) => (
                        <SelectItem key={authority.id} value={authority.name}>
                          {authority.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="date">Data documentului</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => handleInputChange("date", e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tags">Etichete (separate prin virgulă)</Label>
                <Input
                  id="tags"
                  value={formData.tags}
                  onChange={(e) => handleInputChange("tags", e.target.value)}
                  placeholder="Ex: urbanism, construcții, autorizații"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Descriere</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) =>
                    handleInputChange("description", e.target.value)
                  }
                  placeholder="Descriere detaliată a documentului..."
                  rows={4}
                />
              </div>
            </CardContent>
          </Card>

          {/* File upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="h-5 w-5" />
                <span>Încărcare fișier</span>
              </CardTitle>
              <CardDescription>
                Încărcați documentul în format PDF
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => handleFileUpload(e.target.files)}
                    className="hidden"
                    id="file-upload"
                  />
                  <Label htmlFor="file-upload" className="cursor-pointer">
                    <div className="space-y-2">
                      <Upload className="h-8 w-8 mx-auto text-gray-400" />
                      <p className="text-sm text-gray-600">
                        Faceți clic pentru a încărca sau trageți și plasați
                        fișierul
                      </p>
                      <p className="text-xs text-gray-400">
                        Doar fișiere PDF (max. 10MB)
                      </p>
                    </div>
                  </Label>
                </div>

                {uploadedFile && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-green-600" />
                      <div className="flex-1">
                        <p className="font-medium text-green-800">
                          {uploadedFile.name}
                        </p>
                        <p className="text-sm text-green-600">
                          {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-800 mb-2">
                    Cerințe pentru document:
                  </h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Format: PDF</li>
                    <li>• Dimensiune maximă: 10MB</li>
                    <li>• Documentul trebuie să fie lizibil</li>
                    <li>• Conținut oficial și autentificat</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Submit button */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Gata să adăugați documentul?</p>
                <p className="text-sm text-gray-600">
                  Verificați toate informațiile înainte de a salva.
                </p>
              </div>
              <Button type="submit" disabled={isSubmitting} size="lg">
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Se salvează...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Adaugă în arhivă
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
};

export default AddToArchive;
