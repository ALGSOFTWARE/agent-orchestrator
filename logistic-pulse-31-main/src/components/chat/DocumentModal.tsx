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
import { 
  Search, 
  Download, 
  Calendar, 
  MapPin,
  Truck,
  Package,
  FileText
} from "lucide-react";
import { DocumentType } from "./ChatContainer";

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
  status: "Processado" | "Pendente" | "Em Análise";
  carrier: string;
}

const mockDocuments: Document[] = [
  {
    id: "1",
    type: "CTE",
    number: "CTE-2024-001234",
    client: "Empresa ABC Ltda",
    origin: "São Paulo/SP",
    destination: "Rio de Janeiro/RJ",
    date: "2024-01-15",
    status: "Processado",
    carrier: "Transportadora XYZ"
  },
  {
    id: "2",
    type: "NF",
    number: "NF-2024-567890",
    client: "Empresa DEF S.A",
    origin: "Belo Horizonte/MG",
    destination: "Salvador/BA", 
    date: "2024-01-14",
    status: "Pendente",
    carrier: "Transportadora ABC"
  },
  {
    id: "3",
    type: "AWL",
    number: "AWL-2024-789012",
    client: "Importadora GHI",
    origin: "Miami/USA",
    destination: "São Paulo/SP",
    date: "2024-01-13",
    status: "Em Análise",
    carrier: "Cargo Airlines"
  },
  {
    id: "4",
    type: "BL",
    number: "BL-2024-345678",
    client: "Empresa JKL Ltd",
    origin: "Shanghai/China",
    destination: "Santos/SP",
    date: "2024-01-12",
    status: "Processado",
    carrier: "Ocean Shipping Co"
  },
  {
    id: "5",
    type: "MANIFESTO",
    number: "MAN-2024-901234",
    client: "Multiple Clients",
    origin: "Campinas/SP",
    destination: "Curitiba/PR",
    date: "2024-01-11",
    status: "Processado",
    carrier: "Transportadora MNO"
  }
];

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
    case "Processado":
      return "bg-success text-white";
    case "Pendente":
      return "bg-warning text-white";
    case "Em Análise":
      return "bg-info text-white";
    default:
      return "bg-muted text-muted-foreground";
  }
};

export const DocumentModal = ({ isOpen, onClose }: DocumentModalProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState<DocumentType | "ALL">("ALL");

  const documentTypes: (DocumentType | "ALL")[] = ["ALL", "CTE", "AWL", "BL", "MANIFESTO", "NF"];

  const filteredDocuments = mockDocuments.filter((doc) => {
    const matchesSearch = doc.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.client.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === "ALL" || doc.type === selectedType;
    return matchesSearch && matchesType;
  });

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold text-foreground">
            Consulta de Documentos
          </DialogTitle>
        </DialogHeader>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-3 p-4 bg-muted rounded-lg">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por número do documento ou cliente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          
          <div className="flex gap-2 flex-wrap">
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
          {filteredDocuments.map((doc) => {
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
                      </div>
                      
                      <p className="text-sm text-muted-foreground mb-2">{doc.client}</p>
                      
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <MapPin className="w-3 h-3" />
                          <span>{doc.origin} → {doc.destination}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(doc.date).toLocaleDateString('pt-BR')}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Truck className="w-3 h-3" />
                          <span>{doc.carrier}</span>
                        </div>
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
          
          {filteredDocuments.length === 0 && (
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