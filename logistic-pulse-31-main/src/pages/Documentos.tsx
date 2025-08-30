import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useToast } from "@/components/ui/use-toast";
import { 
  FileText, 
  Upload, 
  Download, 
  Eye, 
  Filter,
  Calendar,
  User,
  Truck,
  Package,
  Plus,
  Search,
  MoreVertical,
  History,
  Mail,
  MessageSquare,
  Database,
  Shield,
  CheckCircle,
  Clock,
  AlertCircle
} from "lucide-react";

// Mock data
const documentosData = [
  {
    id: "DOC-001",
    numero: "CTE-2024-001234",
    tipo: "CT-e",
    cliente: "Empresa ABC Ltda",
    jornada: "JOR-001",
    origem: "São Paulo/SP",
    destino: "Rio de Janeiro/RJ",
    dataUpload: "2024-01-15T08:00:00",
    dataEmissao: "2024-01-15T06:00:00",
    status: "Validado",
    tamanho: "2.5 MB",
    versao: 1,
    uploadPor: "Sistema IA",
    origem_upload: "chat",
    visualizacoes: 12,
    ultimaVisualizacao: "2024-01-15T10:30:00"
  },
  {
    id: "DOC-002",
    numero: "NF-2024-567890",
    tipo: "NF-e",
    cliente: "Empresa DEF S.A",
    jornada: "JOR-002",
    origem: "Belo Horizonte/MG",
    destino: "Salvador/BA",
    dataUpload: "2024-01-14T14:30:00",
    dataEmissao: "2024-01-14T12:00:00",
    status: "Pendente Validação",
    tamanho: "1.8 MB",
    versao: 2,
    uploadPor: "João Silva",
    origem_upload: "manual",
    visualizacoes: 5,
    ultimaVisualizacao: "2024-01-14T16:45:00"
  },
  {
    id: "DOC-003",
    numero: "AWL-2024-789012",
    tipo: "AWB",
    cliente: "Importadora GHI",
    jornada: "JOR-003",
    origem: "Miami/USA",
    destino: "São Paulo/SP",
    dataUpload: "2024-01-13T09:15:00",
    dataEmissao: "2024-01-13T07:00:00",
    status: "Validado",
    tamanho: "3.2 MB",
    versao: 1,
    uploadPor: "API Integration",
    origem_upload: "api",
    visualizacoes: 8,
    ultimaVisualizacao: "2024-01-13T11:20:00"
  },
  {
    id: "DOC-004",
    numero: "BL-2024-345678",
    tipo: "BL",
    cliente: "Empresa JKL Ltd",
    jornada: "JOR-004",
    origem: "Shanghai/China",
    destino: "Santos/SP",
    dataUpload: "2024-01-12T16:00:00",
    dataEmissao: "2024-01-12T14:00:00",
    status: "Rejeitado",
    tamanho: "4.1 MB",
    versao: 3,
    uploadPor: "Maria Costa",
    origem_upload: "email",
    visualizacoes: 15,
    ultimaVisualizacao: "2024-01-12T18:30:00"
  }
];

const getDocumentIcon = (tipo: string) => {
  switch (tipo) {
    case "CT-e":
      return { icon: Truck, color: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300" };
    case "AWB":
      return { icon: Package, color: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300" };
    case "BL":
      return { icon: FileText, color: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" };
    case "NF-e":
      return { icon: Calendar, color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300" };
    default:
      return { icon: FileText, color: "bg-gray-100 text-gray-700 dark:bg-gray-900 dark:text-gray-300" };
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "Validado":
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
    case "Pendente Validação":
      return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300";
    case "Rejeitado":
      return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300";
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300";
  }
};

const getOrigemIcon = (origem: string) => {
  switch (origem) {
    case "manual":
      return { icon: Upload, color: "text-blue-500" };
    case "api":
      return { icon: Database, color: "text-green-500" };
    case "chat":
      return { icon: MessageSquare, color: "text-purple-500" };
    case "email":
      return { icon: Mail, color: "text-orange-500" };
    default:
      return { icon: FileText, color: "text-gray-500" };
  }
};

const DocumentUploadModal = ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => {
  const { toast } = useToast();
  const [uploadMethod, setUploadMethod] = useState("manual");
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    toast({
      title: "Upload Simulado",
      description: "Arquivo enviado com sucesso! IA identificou: CT-e",
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Upload de Documentos</DialogTitle>
        </DialogHeader>
        
        <Tabs value={uploadMethod} onValueChange={setUploadMethod}>
          <TabsList className="grid grid-cols-4 mb-4">
            <TabsTrigger value="manual" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Manual
            </TabsTrigger>
            <TabsTrigger value="api" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              API
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Chat
            </TabsTrigger>
            <TabsTrigger value="email" className="flex items-center gap-2">
              <Mail className="h-4 w-4" />
              E-mail
            </TabsTrigger>
          </TabsList>

          <TabsContent value="manual" className="space-y-4">
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive 
                  ? "border-primary bg-primary/10" 
                  : "border-border hover:border-primary"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium">Arraste arquivos aqui ou clique para selecionar</p>
              <p className="text-sm text-muted-foreground mt-2">
                Formatos suportados: PDF, PNG, JPG, XML (máx. 10MB)
              </p>
              <Button className="mt-4">Selecionar Arquivos</Button>
            </div>
            <div className="text-sm text-muted-foreground bg-muted p-3 rounded">
              <strong>IA Automática:</strong> Nosso sistema identificará automaticamente o tipo de documento e o associará à jornada correta.
            </div>
          </TabsContent>

          <TabsContent value="api" className="space-y-4">
            <div className="bg-muted p-4 rounded-lg">
              <h4 className="font-medium mb-2">Integração via API</h4>
              <p className="text-sm text-muted-foreground mb-3">
                Configure a integração automática com seus sistemas ERP/TMS
              </p>
              <div className="space-y-2">
                <Input placeholder="URL do Webhook" />
                <Input placeholder="Token de Autenticação" />
              </div>
              <Button className="mt-3">Configurar Integração</Button>
            </div>
          </TabsContent>

          <TabsContent value="chat" className="space-y-4">
            <div className="bg-muted p-4 rounded-lg">
              <h4 className="font-medium mb-2">Upload via Chat</h4>
              <p className="text-sm text-muted-foreground mb-3">
                Envie documentos diretamente no chat e nossa IA processará automaticamente
              </p>
              <Button>Ir para o Chat</Button>
            </div>
          </TabsContent>

          <TabsContent value="email" className="space-y-4">
            <div className="bg-muted p-4 rounded-lg">
              <h4 className="font-medium mb-2">Upload via E-mail</h4>
              <p className="text-sm text-muted-foreground mb-3">
                Envie documentos para o e-mail dedicado da sua conta
              </p>
              <div className="bg-background p-3 rounded border">
                <code className="text-sm">documentos@sua-empresa.logisticaai.com.br</code>
              </div>
              <Button className="mt-3">Configurar E-mail</Button>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

const DocumentViewer = ({ documento, isOpen, onClose }: { documento: any; isOpen: boolean; onClose: () => void }) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh]">
        <DialogHeader>
          <DialogTitle>{documento?.numero}</DialogTitle>
        </DialogHeader>
        <div className="flex-1 bg-muted rounded-lg flex items-center justify-center">
          <div className="text-center">
            <FileText className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">Visualização do documento</p>
            <p className="text-sm text-muted-foreground mt-2">
              Integração com visualizador PDF seria implementada aqui
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default function Documentos() {
  const [filtro, setFiltro] = useState("");
  const [tipoFiltro, setTipoFiltro] = useState("todos");
  const [statusFiltro, setStatusFiltro] = useState("todos");
  const [origemFiltro, setOrigemFiltro] = useState("todos");
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [documentoSelecionado, setDocumentoSelecionado] = useState(null);
  const { toast } = useToast();

  const documentosFiltrados = documentosData.filter(doc => {
    const matchFiltro = doc.numero.toLowerCase().includes(filtro.toLowerCase()) ||
                       doc.cliente.toLowerCase().includes(filtro.toLowerCase());
    const matchTipo = tipoFiltro === "todos" || doc.tipo === tipoFiltro;
    const matchStatus = statusFiltro === "todos" || doc.status === statusFiltro;
    const matchOrigem = origemFiltro === "todos" || doc.origem_upload === origemFiltro;
    
    return matchFiltro && matchTipo && matchStatus && matchOrigem;
  });

  const handleDownload = (doc: any) => {
    toast({
      title: "Download Iniciado",
      description: `Baixando ${doc.numero}...`,
    });
  };

  const handleView = (doc: any) => {
    setDocumentoSelecionado(doc);
    setViewerOpen(true);
  };

  const estatisticas = {
    total: documentosData.length,
    validados: documentosData.filter(d => d.status === "Validado").length,
    pendentes: documentosData.filter(d => d.status === "Pendente Validação").length,
    rejeitados: documentosData.filter(d => d.status === "Rejeitado").length,
  };

  return (
    <AppLayout>
      <div className="p-6 space-y-6 h-full overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Central de Documentos</h1>
            <p className="text-muted-foreground">Gerencie todos os documentos da jornada logística</p>
          </div>
          <Button onClick={() => setUploadModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Novo Documento
          </Button>
        </div>

        {/* Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <FileText className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-2xl font-bold">{estatisticas.total}</p>
                  <p className="text-xs text-muted-foreground">Total de Documentos</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-8 w-8 text-green-500" />
                <div>
                  <p className="text-2xl font-bold">{estatisticas.validados}</p>
                  <p className="text-xs text-muted-foreground">Validados</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-8 w-8 text-yellow-500" />
                <div>
                  <p className="text-2xl font-bold">{estatisticas.pendentes}</p>
                  <p className="text-xs text-muted-foreground">Pendentes</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-8 w-8 text-red-500" />
                <div>
                  <p className="text-2xl font-bold">{estatisticas.rejeitados}</p>
                  <p className="text-xs text-muted-foreground">Rejeitados</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filtros */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Filter className="h-5 w-5 mr-2" />
              Filtros e Busca
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por número ou cliente..."
                  value={filtro}
                  onChange={(e) => setFiltro(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={tipoFiltro} onValueChange={setTipoFiltro}>
                <SelectTrigger>
                  <SelectValue placeholder="Tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os Tipos</SelectItem>
                  <SelectItem value="CT-e">CT-e</SelectItem>
                  <SelectItem value="NF-e">NF-e</SelectItem>
                  <SelectItem value="AWB">AWB</SelectItem>
                  <SelectItem value="BL">BL</SelectItem>
                </SelectContent>
              </Select>
              <Select value={statusFiltro} onValueChange={setStatusFiltro}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os Status</SelectItem>
                  <SelectItem value="Validado">Validado</SelectItem>
                  <SelectItem value="Pendente Validação">Pendente</SelectItem>
                  <SelectItem value="Rejeitado">Rejeitado</SelectItem>
                </SelectContent>
              </Select>
              <Select value={origemFiltro} onValueChange={setOrigemFiltro}>
                <SelectTrigger>
                  <SelectValue placeholder="Origem" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todas as Origens</SelectItem>
                  <SelectItem value="manual">Upload Manual</SelectItem>
                  <SelectItem value="api">Via API</SelectItem>
                  <SelectItem value="chat">Via Chat</SelectItem>
                  <SelectItem value="email">Via E-mail</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Download em Massa
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Lista de Documentos */}
        <Card>
          <CardHeader>
            <CardTitle>Documentos ({documentosFiltrados.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {documentosFiltrados.map((doc) => {
                const { icon: TipoIcon, color: tipoColor } = getDocumentIcon(doc.tipo);
                const { icon: OrigemIcon, color: origemColor } = getOrigemIcon(doc.origem_upload);
                
                return (
                  <div
                    key={doc.id}
                    className="p-4 border border-border rounded-lg hover:shadow-md transition-all duration-200 bg-card"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 flex-1">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${tipoColor}`}>
                          <TipoIcon className="w-6 h-6" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <h3 className="font-semibold text-foreground truncate">{doc.numero}</h3>
                            <Badge className={`${getStatusColor(doc.status)} text-xs`}>
                              {doc.status}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              v{doc.versao}
                            </Badge>
                          </div>
                          
                          <p className="text-sm text-muted-foreground mb-2">{doc.cliente}</p>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-muted-foreground">
                            <div className="flex items-center space-x-1">
                              <Calendar className="w-3 h-3" />
                              <span>{new Date(doc.dataEmissao).toLocaleDateString('pt-BR')}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <User className="w-3 h-3" />
                              <span className="truncate">{doc.uploadPor}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <OrigemIcon className={`w-3 h-3 ${origemColor}`} />
                              <span className="capitalize">{doc.origem_upload}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Eye className="w-3 h-3" />
                              <span>{doc.visualizacoes} visualizações</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleView(doc)}
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          Ver
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownload(doc)}
                        >
                          <Download className="w-4 h-4 mr-1" />
                          Download
                        </Button>
                        <Button size="sm" variant="outline">
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
              
              {documentosFiltrados.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Nenhum documento encontrado</p>
                  <p className="text-sm">Tente ajustar os filtros de busca</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Modals */}
        <DocumentUploadModal 
          isOpen={uploadModalOpen} 
          onClose={() => setUploadModalOpen(false)} 
        />
        
        <DocumentViewer
          documento={documentoSelecionado}
          isOpen={viewerOpen}
          onClose={() => setViewerOpen(false)}
        />
      </div>
    </AppLayout>
  );
}