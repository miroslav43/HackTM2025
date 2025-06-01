import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
import { useAuth } from "@/contexts/AuthContext";
import {
  CheckCircle,
  Clock,
  Download,
  Edit,
  Eye,
  FileText,
  Save,
  Send,
  Zap,
} from "lucide-react";
import React, { useState } from "react";

interface DocumentTemplate {
  id: string;
  title: string;
  description: string;
  category: string;
  icon: React.ElementType;
  fields: DocumentField[];
  estimatedTime: string;
  popularity: number;
}

interface DocumentField {
  id: string;
  label: string;
  type: "text" | "select" | "textarea" | "date" | "number";
  required: boolean;
  placeholder?: string;
  options?: string[];
  autoFill?: string; // Campo din profilul utilizatorului
}

const AutoDocuments = () => {
  const { user } = useAuth();
  const [selectedDocument, setSelectedDocument] =
    useState<DocumentTemplate | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  const documentTemplates: DocumentTemplate[] = [
    {
      id: "cerere-certificat-urbanism",
      title: "Cerere pentru certificat de urbanism",
      description:
        "Solicitare certificat de urbanism pentru construcții noi sau modificări",
      category: "urbanism",
      icon: FileText,
      estimatedTime: "5 min",
      popularity: 95,
      fields: [
        {
          id: "nume",
          label: "Nume complet",
          type: "text",
          required: true,
          autoFill: "name",
        },
        {
          id: "cnp",
          label: "CNP",
          type: "text",
          required: true,
          autoFill: "cnp",
        },
        {
          id: "adresa",
          label: "Adresa solicitant",
          type: "text",
          required: true,
          autoFill: "address",
        },
        {
          id: "telefon",
          label: "Telefon",
          type: "text",
          required: true,
          autoFill: "phone",
        },
        {
          id: "email",
          label: "Email",
          type: "text",
          required: true,
          autoFill: "email",
        },
        {
          id: "tip_lucrare",
          label: "Tip lucrare",
          type: "select",
          required: true,
          options: ["Construcție nouă", "Extindere", "Modificare", "Demolare"],
        },
        {
          id: "adresa_imobil",
          label: "Adresa imobilului",
          type: "text",
          required: true,
        },
        {
          id: "descriere",
          label: "Descrierea lucrării",
          type: "textarea",
          required: true,
          placeholder: "Descrieți detaliat lucrarea propusă...",
        },
      ],
    },
    {
      id: "declaratie-venit",
      title: "Declarație unică de venit",
      description: "Declarația anuală de venituri pentru persoane fizice",
      category: "fiscal",
      icon: FileText,
      estimatedTime: "15 min",
      popularity: 88,
      fields: [
        {
          id: "nume",
          label: "Nume și prenume",
          type: "text",
          required: true,
          autoFill: "name",
        },
        {
          id: "cnp",
          label: "CNP",
          type: "text",
          required: true,
          autoFill: "cnp",
        },
        {
          id: "adresa",
          label: "Domiciliul",
          type: "text",
          required: true,
          autoFill: "address",
        },
        {
          id: "an_fiscal",
          label: "Anul fiscal",
          type: "select",
          required: true,
          options: ["2024", "2023", "2022"],
        },
        {
          id: "tip_venit",
          label: "Tipul venitului",
          type: "select",
          required: true,
          options: [
            "Salarii",
            "Activități independente",
            "Dividende",
            "Altele",
          ],
        },
        {
          id: "suma_venit",
          label: "Suma totală (RON)",
          type: "number",
          required: true,
        },
        {
          id: "mentiuni",
          label: "Mențiuni speciale",
          type: "textarea",
          required: false,
        },
      ],
    },
    {
      id: "cerere-pasaport",
      title: "Cerere pentru eliberare pașaport",
      description: "Solicitare pentru eliberarea unui pașaport românesc",
      category: "documente",
      icon: FileText,
      estimatedTime: "8 min",
      popularity: 76,
      fields: [
        {
          id: "nume",
          label: "Nume",
          type: "text",
          required: true,
          autoFill: "name",
        },
        {
          id: "cnp",
          label: "CNP",
          type: "text",
          required: true,
          autoFill: "cnp",
        },
        {
          id: "adresa",
          label: "Domiciliul",
          type: "text",
          required: true,
          autoFill: "address",
        },
        {
          id: "telefon",
          label: "Telefon",
          type: "text",
          required: true,
          autoFill: "phone",
        },
        {
          id: "tip_pasaport",
          label: "Tip pașaport",
          type: "select",
          required: true,
          options: ["Simplu", "Simplu electronic", "Temporar"],
        },
        {
          id: "valabilitate",
          label: "Perioada de valabilitate",
          type: "select",
          required: true,
          options: ["5 ani", "10 ani"],
        },
        {
          id: "motiv",
          label: "Motivul solicitării",
          type: "select",
          required: true,
          options: [
            "Prima eliberare",
            "Reînnoire",
            "Înlocuire document deteriorat",
            "Înlocuire document pierdut",
          ],
        },
      ],
    },
    {
      id: "declaratie-propria-raspundere",
      title: "Declarație pe propria răspundere",
      description: "Declarație standard pe propria răspundere",
      category: "generale",
      icon: FileText,
      estimatedTime: "3 min",
      popularity: 92,
      fields: [
        {
          id: "nume",
          label: "Nume și prenume",
          type: "text",
          required: true,
          autoFill: "name",
        },
        {
          id: "cnp",
          label: "CNP",
          type: "text",
          required: true,
          autoFill: "cnp",
        },
        {
          id: "adresa",
          label: "Domiciliul",
          type: "text",
          required: true,
          autoFill: "address",
        },
        {
          id: "continut",
          label: "Conținutul declarației",
          type: "textarea",
          required: true,
          placeholder: "Declar pe propria răspundere că...",
        },
        { id: "data", label: "Data", type: "date", required: true },
      ],
    },
  ];

  const getUserData = () => ({
    name: user?.name || "",
    email: user?.email || "",
    phone: "",
    address: "",
    cnp: "",
  });

  const autoFillForm = (template: DocumentTemplate) => {
    const userData = getUserData();
    const filledData: Record<string, string> = {};

    template.fields.forEach((field) => {
      if (field.autoFill && userData[field.autoFill as keyof typeof userData]) {
        filledData[field.id] =
          userData[field.autoFill as keyof typeof userData];
      }
    });

    setFormData(filledData);
  };

  const handleDocumentSelect = (template: DocumentTemplate) => {
    setSelectedDocument(template);
    autoFillForm(template);
  };

  const handleFieldChange = (fieldId: string, value: string) => {
    setFormData((prev) => ({ ...prev, [fieldId]: value }));
  };

  const handleSubmit = () => {
    console.log("Submitting document:", selectedDocument?.title, formData);
    // Simulate submission
    alert("Documentul a fost trimis cu succes!");
    setSelectedDocument(null);
    setFormData({});
  };

  const handleSaveDraft = () => {
    console.log("Saving draft:", selectedDocument?.title, formData);
    alert("Schiță salvată!");
  };

  const handleDownloadPDF = () => {
    console.log("Downloading PDF:", selectedDocument?.title, formData);
    alert("PDF descărcat!");
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "urbanism":
        return "bg-blue-100 text-blue-800";
      case "fiscal":
        return "bg-green-100 text-green-800";
      case "documente":
        return "bg-purple-100 text-purple-800";
      case "generale":
        return "bg-orange-100 text-orange-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getCategoryName = (category: string) => {
    switch (category) {
      case "urbanism":
        return "Urbanism";
      case "fiscal":
        return "Fiscal";
      case "documente":
        return "Documente";
      case "generale":
        return "Generale";
      default:
        return "Altele";
    }
  };

  if (selectedDocument) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" onClick={() => setSelectedDocument(null)}>
              ← Înapoi
            </Button>
            <div>
              <h1 className="text-2xl font-bold">{selectedDocument.title}</h1>
              <p className="text-gray-600">{selectedDocument.description}</p>
            </div>
          </div>
          <Badge className={getCategoryColor(selectedDocument.category)}>
            {getCategoryName(selectedDocument.category)}
          </Badge>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Edit className="h-5 w-5" />
                  <span>Completare formular</span>
                </CardTitle>
                <CardDescription>
                  Câmpurile marcate cu * sunt obligatorii. Datele sunt
                  completate automat din profilul tău.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {selectedDocument.fields.map((field) => (
                  <div key={field.id} className="space-y-2">
                    <Label htmlFor={field.id}>
                      {field.label}
                      {field.required && (
                        <span className="text-red-500 ml-1">*</span>
                      )}
                    </Label>

                    {field.type === "text" && (
                      <Input
                        id={field.id}
                        value={formData[field.id] || ""}
                        onChange={(e) =>
                          handleFieldChange(field.id, e.target.value)
                        }
                        placeholder={field.placeholder}
                        required={field.required}
                      />
                    )}

                    {field.type === "textarea" && (
                      <Textarea
                        id={field.id}
                        value={formData[field.id] || ""}
                        onChange={(e) =>
                          handleFieldChange(field.id, e.target.value)
                        }
                        placeholder={field.placeholder}
                        required={field.required}
                        rows={4}
                      />
                    )}

                    {field.type === "select" && (
                      <Select
                        value={formData[field.id] || ""}
                        onValueChange={(value) =>
                          handleFieldChange(field.id, value)
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Selectează o opțiune" />
                        </SelectTrigger>
                        <SelectContent>
                          {field.options?.map((option) => (
                            <SelectItem key={option} value={option}>
                              {option}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}

                    {field.type === "date" && (
                      <Input
                        id={field.id}
                        type="date"
                        value={formData[field.id] || ""}
                        onChange={(e) =>
                          handleFieldChange(field.id, e.target.value)
                        }
                        required={field.required}
                      />
                    )}

                    {field.type === "number" && (
                      <Input
                        id={field.id}
                        type="number"
                        value={formData[field.id] || ""}
                        onChange={(e) =>
                          handleFieldChange(field.id, e.target.value)
                        }
                        placeholder={field.placeholder}
                        required={field.required}
                      />
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Acțiuni</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Dialog open={isPreviewOpen} onOpenChange={setIsPreviewOpen}>
                  <DialogTrigger asChild>
                    <Button variant="outline" className="w-full">
                      <Eye className="h-4 w-4 mr-2" />
                      Previzualizează
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Previzualizare document</DialogTitle>
                      <DialogDescription>
                        {selectedDocument.title}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="max-h-96 overflow-y-auto p-4 bg-gray-50 rounded">
                      <div className="space-y-4 text-sm">
                        {selectedDocument.fields.map((field) => (
                          <div key={field.id}>
                            <strong>{field.label}:</strong>{" "}
                            {formData[field.id] || "(necompletat)"}
                          </div>
                        ))}
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>

                <Button
                  onClick={handleDownloadPDF}
                  variant="outline"
                  className="w-full"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Descarcă PDF
                </Button>

                <Button
                  onClick={handleSaveDraft}
                  variant="outline"
                  className="w-full"
                >
                  <Save className="h-4 w-4 mr-2" />
                  Salvează schiță
                </Button>

                <Button onClick={handleSubmit} className="w-full">
                  <Send className="h-4 w-4 mr-2" />
                  Trimite document
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Informații</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-gray-500" />
                  <span>Timp estimat: {selectedDocument.estimatedTime}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Auto-completare activă</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Zap className="h-4 w-4 text-blue-500" />
                  <span>Popularitate: {selectedDocument.popularity}%</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold mb-2">
          Documente Completabile Automat
        </h1>
        <p className="text-gray-600">
          Completează rapid formulare și documente folosind datele din profilul
          tău
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {documentTemplates.map((template, index) => (
          <Card
            key={template.id}
            className="hover-lift cursor-pointer animate-scale-in"
            style={{ animationDelay: `${index * 0.1}s` }}
            onClick={() => handleDocumentSelect(template)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <template.icon className="h-8 w-8 text-primary-600" />
                <Badge className={getCategoryColor(template.category)}>
                  {getCategoryName(template.category)}
                </Badge>
              </div>
              <CardTitle className="text-lg">{template.title}</CardTitle>
              <CardDescription>{template.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4" />
                  <span>{template.estimatedTime}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Zap className="h-4 w-4 text-blue-500" />
                  <span>{template.popularity}%</span>
                </div>
              </div>
              <Button className="w-full mt-4" variant="outline">
                <Zap className="h-4 w-4 mr-2" />
                Completează automat
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Schiţe salvate</CardTitle>
          <CardDescription>
            Documentele pe care le-ai început dar nu le-ai finalizat încă
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>Nu ai schiţe salvate</p>
            <p className="text-sm">
              Începe să completezi un document pentru a vedea schiţele aici
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AutoDocuments;
