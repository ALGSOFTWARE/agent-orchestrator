import { useState } from "react";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { 
  Search, 
  Download, 
  Calendar, 
  MapPin,
  Truck,
  Package,
  FileText,
  Loader2,
  Brain,
  Zap
} from "lucide-react";
import { DocumentType } from "./ChatContainer";
import { useDocuments } from "@/hooks/useApi";

interface DocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Document {
  id: string;
  type: DocumentType;
  number: string;
  client: string;
  origin: string;
  destination: string;
  date: string;
  status: "Validado" | "Pendente Validação" | "Rejeitado" | "Processado" | "Pendente" | "Em Análise";
  carrier?: string;
  created_at?: string;
  upload_date?: string;
}

const getDocumentIcon = (type: DocumentType) => {
  switch (type) {
    case "CTE":
      return { icon: Truck, color: "bg-blue-100 text-blue-700" };
    case "AWL":
      return { icon: Package, color: "bg-purple-100 text-purple-700" };
    case "BL":
      return { icon: MapPin, color: "bg-green-100 text-green-700" };
    case "MANIFESTO":
      return { icon: FileText, color: "bg-orange-100 text-orange-700" };
    case "NF":
      return { icon: Calendar, color: "bg-yellow-100 text-yellow-700" };
    default:
      return { icon: FileText, color: "bg-gray-100 text-gray-700" };
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "Validado":
    case "Processado":
      return "bg-green-500 text-white";
    case "Pendente Validação":
    case "Pendente":
      return "bg-yellow-500 text-white";
    case "Em Análise":
      return "bg-blue-500 text-white";
    case "Rejeitado":
      return "bg-red-500 text-white";
    default:
      return "bg-muted text-muted-foreground";
  }
};

export const DocumentModal = ({ isOpen, onClose }: DocumentModalProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState<DocumentType | "ALL">("ALL");
  const [useSemanticSearch, setUseSemanticSearch] = useState(false);

  const documentTypes: (DocumentType | "ALL")[] = ["ALL", "CTE", "AWL", "BL", "MANIFESTO", "NF"];

  // Usar dados reais da API com busca semântica opcional
  const { 
    data: apiDocuments = [], 
    isLoading, 
    error 
  } = useDocuments({ 
    type: selectedType === "ALL" ? undefined : selectedType,
    search: searchTerm || undefined,
    semantic_search: useSemanticSearch && searchTerm.length > 0
  });

  const filteredDocuments = apiDocuments;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold text-foreground">
            Consulta de Documentos
          </DialogTitle>
        </DialogHeader>

        {/* Filters */}
        <div className="space-y-4">
          {/* Search Bar and Semantic Toggle */}
          <div className="flex flex-col sm:flex-row gap-3 p-4 bg-muted rounded-lg">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por número do documento, cliente ou conteúdo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            {/* Semantic Search Toggle */}
            <div className="flex items-center space-x-2 px-3 py-2 bg-background rounded-md border">
              <Brain className={`w-4 h-4 ${useSemanticSearch ? 'text-blue-500' : 'text-muted-foreground'}`} />
              <Label htmlFor="semantic-search" className="text-sm font-medium">
                IA Semântica
              </Label>
              <Switch
                id="semantic-search"
                checked={useSemanticSearch}
                onCheckedChange={setUseSemanticSearch}
                disabled={!searchTerm}
              />
              {useSemanticSearch && searchTerm && (
                <Zap className="w-3 h-3 text-yellow-500 animate-pulse" />
              )}
            </div>
          </div>
          
          {/* Search Info */}
          {searchTerm && (
            <div className="px-4 py-2 bg-blue-50 border border-blue-200 rounded-md">
              <div className="flex items-center gap-2 text-sm text-blue-700">
                {useSemanticSearch ? (
                  <>
                    <Brain className="w-4 h-4" />
                    <span><strong>Busca Semântica Ativa:</strong> Usando IA para encontrar documentos por similaridade de conteúdo</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span><strong>Busca Tradicional:</strong> Buscando por texto exato. Ative a IA Semântica para busca mais inteligente</span>
                  </>
                )}
              </div>
            </div>
          )}
          
          {/* Type Filters */}
          <div className="flex gap-2 flex-wrap px-4">
            {documentTypes.map((type) => (
              <Button
                key={type}
                variant={selectedType === type ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedType(type)}
                className={selectedType === type ? "bg-brand-primary text-brand-dark" : ""}
              >
                {type === "ALL" ? "Todos" : type}
              </Button>
            ))}
          </div>
        </div>

        {/* Documents List */}
        <div className="flex-1 overflow-y-auto space-y-3">
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Carregando documentos...</span>
            </div>
          )}

          {error && (
            <div className="text-center py-8 text-red-500">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Erro ao carregar documentos</p>
              <p className="text-sm">Tente novamente em alguns instantes</p>
            </div>
          )}

          {!isLoading && !error && filteredDocuments.map((doc) => {
            const { icon: Icon, color } = getDocumentIcon(doc.type);
            
            return (
              <div
                key={doc.id}
                className="p-4 border border-border rounded-lg hover:shadow-medium transition-all duration-200 bg-card"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-semibold text-foreground">{doc.number}</h3>
                        <Badge className={getStatusColor(doc.status)}>
                          {doc.status}
                        </Badge>
                        {useSemanticSearch && doc.similarity_score && (
                          <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                            <Brain className="w-3 h-3 mr-1" />
                            {(doc.similarity_score * 100).toFixed(1)}% relevante
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-sm text-muted-foreground mb-2">{doc.client}</p>
                      
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <MapPin className="w-3 h-3" />
                          <span>{doc.origin} → {doc.destination}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(doc.date || doc.created_at || doc.upload_date).toLocaleDateString('pt-BR')}</span>
                        </div>
                        {doc.carrier && (
                          <div className="flex items-center space-x-1">
                            <Truck className="w-3 h-3" />
                            <span>{doc.carrier}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <Button size="sm" variant="outline">
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>
              </div>
            );
          })}
          
          {!isLoading && !error && filteredDocuments.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Nenhum documento encontrado</p>
              <p className="text-sm">Tente ajustar os filtros de busca</p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};