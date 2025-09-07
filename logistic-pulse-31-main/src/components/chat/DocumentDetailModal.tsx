import { useState } from "react";
import { X, Download, Share2, Eye, Clock, User, MapPin, FileText, Truck } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { DocumentType } from "./ChatContainer";

interface DocumentDetail {
  id: string;
  type: DocumentType;
  number: string;
  status: "Processado" | "Pendente" | "Em Análise" | "Validado";
  client: string;
  embarque: string;
  rota: {
    origem: string;
    destino: string;
    status: string;
    proximaParada?: string;
  };
  dataRecebimento: Date;
  dataValidade?: Date;
  arquivo: {
    nome: string;
    tamanho: string;
    url: string;
  };
  historico: {
    data: Date;
    acao: string;
    usuario: string;
  }[];
  metadados: {
    transportadora?: string;
    valor?: string;
    peso?: string;
  };
}

interface DocumentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  document: DocumentDetail | null;
}

const getDocumentIcon = (type: DocumentType) => {
  switch (type) {
    case "CTE": return { icon: "🚛", label: "Conhecimento de Transporte Eletrônico" };
    case "AWL": return { icon: "✈️", label: "Air Waybill" };
    case "BL": return { icon: "🚢", label: "Bill of Lading" };
    case "MANIFESTO": return { icon: "📋", label: "Manifesto de Carga" };
    case "NF": return { icon: "🧾", label: "Nota Fiscal" };
    default: return { icon: "📄", label: "Documento" };
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "Processado": return "bg-success text-success-foreground";
    case "Validado": return "bg-brand-primary text-brand-dark";
    case "Pendente": return "bg-warning text-warning-foreground";
    case "Em Análise": return "bg-accent text-accent-foreground";
    default: return "bg-muted text-muted-foreground";
  }
};

export const DocumentDetailModal = ({ isOpen, onClose, document }: DocumentDetailModalProps) => {
  const [selectedTab, setSelectedTab] = useState<"detalhes" | "historico" | "visualizar">("detalhes");

  if (!isOpen || !document) return null;

  const docInfo = getDocumentIcon(document.type);

  const handleShare = () => {
    // Implementar compartilhamento
    console.log("Compartilhar documento:", document.id);
  };

  const handleDownload = () => {
    // Implementar download
    console.log("Download documento:", document.arquivo.url);
  };

  const handleViewPDF = () => {
    setSelectedTab("visualizar");
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-lg w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center text-2xl">
              {docInfo.icon}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-foreground">{document.number}</h2>
              <p className="text-sm text-muted-foreground">{docInfo.label}</p>
              <div className="flex items-center space-x-2 mt-1">
                <Badge className={getStatusColor(document.status)}>
                  {document.status}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  Cliente: {document.client}
                </span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={handleDownload}>
              <Download className="w-4 h-4 mr-2" />
              Baixar
            </Button>
            <Button variant="outline" size="sm" onClick={handleShare}>
              <Share2 className="w-4 h-4 mr-2" />
              Compartilhar
            </Button>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border">
          {[
            { id: "detalhes", label: "Detalhes", icon: FileText },
            { id: "historico", label: "Histórico", icon: Clock },
            { id: "visualizar", label: "Visualizar", icon: Eye }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setSelectedTab(id as any)}
              className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                selectedTab === id
                  ? "border-brand-primary text-brand-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {selectedTab === "detalhes" && (
            <ScrollArea className="h-full p-6">
              <div className="space-y-6">
                {/* Informações do Embarque */}
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center">
                    <Truck className="w-5 h-5 mr-2" />
                    Informações do Embarque
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">Número do Embarque</label>
                      <p className="text-foreground">{document.embarque}</p>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">Status da Rota</label>
                      <p className="text-foreground">{document.rota.status}</p>
                    </div>
                  </div>
                  
                  <div className="mt-4 p-4 bg-muted rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <MapPin className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{document.rota.origem}</span>
                      </div>
                      <div className="flex-1 border-t border-dashed border-muted-foreground mx-4"></div>
                      <div className="flex items-center space-x-2">
                        <MapPin className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{document.rota.destino}</span>
                      </div>
                    </div>
                    {document.rota.proximaParada && (
                      <div className="mt-2 text-xs text-muted-foreground">
                        Próxima parada: {document.rota.proximaParada}
                      </div>
                    )}
                  </div>
                </div>

                <Separator />

                {/* Informações do Documento */}
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-3">Informações do Documento</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">Data de Recebimento</label>
                      <p className="text-foreground">{format(document.dataRecebimento, "dd/MM/yyyy HH:mm", { locale: ptBR })}</p>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">Arquivo</label>
                      <p className="text-foreground">{document.arquivo.nome} ({document.arquivo.tamanho})</p>
                    </div>
                    {document.dataValidade && (
                      <>
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-muted-foreground">Validade</label>
                          <p className="text-foreground">{format(document.dataValidade, "dd/MM/yyyy", { locale: ptBR })}</p>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Metadados */}
                {Object.keys(document.metadados).length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h3 className="text-lg font-semibold text-foreground mb-3">Dados Adicionais</h3>
                      <div className="grid grid-cols-2 gap-4">
                        {document.metadados.transportadora && (
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-muted-foreground">Transportadora</label>
                            <p className="text-foreground">{document.metadados.transportadora}</p>
                          </div>
                        )}
                        {document.metadados.valor && (
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-muted-foreground">Valor</label>
                            <p className="text-foreground">{document.metadados.valor}</p>
                          </div>
                        )}
                        {document.metadados.peso && (
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-muted-foreground">Peso</label>
                            <p className="text-foreground">{document.metadados.peso}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </ScrollArea>
          )}

          {selectedTab === "historico" && (
            <ScrollArea className="h-full p-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-foreground">Histórico de Atividades</h3>
                {document.historico.map((item, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 border border-border rounded-lg">
                    <div className="w-8 h-8 bg-brand-light rounded-full flex items-center justify-center mt-1">
                      <User className="w-4 h-4 text-brand-primary" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-foreground">{item.acao}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-muted-foreground">{item.usuario}</span>
                        <span className="text-xs text-muted-foreground">•</span>
                        <span className="text-xs text-muted-foreground">
                          {format(item.data, "dd/MM/yyyy HH:mm", { locale: ptBR })}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}

          {selectedTab === "visualizar" && (
            <div className="h-full bg-muted flex items-center justify-center">
              <div className="text-center space-y-4">
                <FileText className="w-16 h-16 text-muted-foreground mx-auto" />
                <div>
                  <h3 className="text-lg font-semibold text-foreground">Visualização do Documento</h3>
                  <p className="text-muted-foreground">A visualização inline será implementada aqui</p>
                  <Button className="mt-4" onClick={handleViewPDF}>
                    <Eye className="w-4 h-4 mr-2" />
                    Abrir PDF
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};