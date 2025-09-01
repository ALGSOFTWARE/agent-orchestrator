import { useState } from "react";
import * as React from "react";
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
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import DocumentVersioning from "@/components/ui/DocumentVersioning";
import DocumentApproval from "@/components/ui/DocumentApproval";
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
  AlertCircle,
  GitBranch,
  UserCheck
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

const DocumentUploadModal = ({ isOpen, onClose, onUploadSuccess }: { 
  isOpen: boolean; 
  onClose: () => void; 
  onUploadSuccess?: () => void;
}) => {
  const { toast } = useToast();
  const [uploadMethod, setUploadMethod] = useState("manual");
  const [dragActive, setDragActive] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<string>("");
  const [orders, setOrders] = useState<any[]>([]);
  const [orderSearch, setOrderSearch] = useState("");
  const [loadingOrders, setLoadingOrders] = useState(false);

  // Carregar Orders quando o modal abre
  React.useEffect(() => {
    if (isOpen) {
      loadOrders();
    }
  }, [isOpen]);

  const loadOrders = async () => {
    setLoadingOrders(true);
    try {
      const searchParam = orderSearch ? `?search=${encodeURIComponent(orderSearch)}` : '';
      const response = await fetch(`http://localhost:8001/api/frontend/orders${searchParam}`);
      const result = await response.json();
      
      if (result.success) {
        setOrders(result.data);
      } else {
        toast({
          title: "Erro ao carregar Orders",
          description: "Não foi possível carregar as orders disponíveis",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('Erro ao buscar orders:', error);
      toast({
        title: "Erro de conexão",
        description: "Verifique se a API está funcionando",
        variant: "destructive"
      });
    } finally {
      setLoadingOrders(false);
    }
  };

  // Buscar Orders quando o usuário digita
  React.useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (isOpen) {
        loadOrders();
      }
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [orderSearch, isOpen]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (!selectedOrder) {
      toast({
        title: "Order não selecionada",
        description: "Selecione uma Order antes de fazer o upload do documento",
        variant: "destructive"
      });
      return;
    }
    
    const files = Array.from(e.dataTransfer.files);
    
    if (files.length === 0) return;
    
    // Upload do primeiro arquivo (pode ser expandido para múltiplos arquivos)
    const file = files[0];
    await uploadFile(file);
  };

  const handleFileUpload = () => {
    if (!selectedOrder) {
      toast({
        title: "Order não selecionada",
        description: "Selecione uma Order antes de fazer o upload do documento",
        variant: "destructive"
      });
      return;
    }
    
    // Criar input file hidden e triggar
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.png,.jpg,.jpeg,.xml,.txt,.doc,.docx';
    input.onchange = handleFileSelected;
    input.click();
  };

  const handleFileSelected = async (e: Event) => {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    
    if (!file) return;
    
    await uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    if (!selectedOrder) return;
    
    const selectedOrderData = orders.find(o => o.id === selectedOrder);
    
    // Mostrar toast de início
    toast({
      title: "Processando documento...",
      description: `Enviando ${file.name} para Order ${selectedOrderData?.order_number}`,
    });
    
    try {
      // Criar FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('order_id', selectedOrder);
      formData.append('user_id', 'frontend-user');
      
      // Fazer upload
      const response = await fetch('http://localhost:8001/api/frontend/documents/upload', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast({
          title: "Upload concluído!",
          description: `${file.name} processado com sucesso. Categoria: ${result.data.category}${result.data.embedding_generated ? ', Embeddings gerados' : ''}`,
        });
        
        // Recarregar documentos e fechar modal após sucesso
        if (onUploadSuccess) {
          onUploadSuccess();
        }
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        throw new Error(result.message || 'Erro no upload');
      }
    } catch (error) {
      console.error('Erro no upload:', error);
      toast({
        title: "Erro no upload",
        description: `Falha ao processar ${file.name}. Tente novamente.`,
        variant: "destructive"
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Upload de Documentos</DialogTitle>
        </DialogHeader>
        
        {/* Seletor de Order */}
        <div className="space-y-3 p-4 bg-muted rounded-lg">
          <div className="flex items-center gap-2">
            <Package className="h-4 w-4 text-primary" />
            <h4 className="font-medium">Associar à Order</h4>
          </div>
          <p className="text-sm text-muted-foreground">
            Todo documento deve estar associado a uma Order. Busque e selecione a Order correspondente.
          </p>
          
          <div className="space-y-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por ID, cliente ou título da Order..."
                value={orderSearch}
                onChange={(e) => setOrderSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedOrder} onValueChange={setSelectedOrder}>
              <SelectTrigger>
                <SelectValue placeholder={loadingOrders ? "Carregando Orders..." : "Selecione uma Order"} />
              </SelectTrigger>
              <SelectContent>
                {orders.map((order) => (
                  <SelectItem key={order.id} value={order.id}>
                    <div className="flex flex-col text-left">
                      <span className="font-medium">{order.order_number}</span>
                      <span className="text-xs text-muted-foreground">
                        {order.customer_name} • {order.origin} → {order.destination}
                      </span>
                    </div>
                  </SelectItem>
                ))}
                {orders.length === 0 && !loadingOrders && (
                  <SelectItem value="" disabled>
                    Nenhuma Order encontrada
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
            
            {selectedOrder && (
              <div className="p-2 bg-primary/10 rounded text-sm">
                <span className="text-primary font-medium">Order selecionada:</span>{" "}
                {orders.find(o => o.id === selectedOrder)?.order_number}
              </div>
            )}
          </div>
        </div>
        
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
              <Button 
                className="mt-4" 
                onClick={handleFileUpload}
                disabled={!selectedOrder}
              >
                Selecionar Arquivos
              </Button>
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
  const getDocumentType = (filename: string): "PDF" | "XML" | "IMAGEM" | "DESCONHECIDO" => {
    if (!filename) return "DESCONHECIDO";
    
    const ext = filename.toLowerCase().split('.').pop();
    if (ext === 'pdf') return "PDF";
    if (ext === 'xml') return "XML";
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext || '')) return "IMAGEM";
    return "DESCONHECIDO";
  };

  const documentType = getDocumentType(documento?.numero || '');
  const hasValidUrl = documento?.s3_url && documento?.has_valid_s3;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh]">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle>{documento?.numero}</DialogTitle>
            {hasValidUrl && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleDownload(documento)}
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            )}
          </div>
          {documento && (
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <span>Cliente: {documento.cliente}</span>
              <span>Status: {documento.status}</span>
              {documento.current_version && <span>Versão: {documento.current_version}</span>}
            </div>
          )}
        </DialogHeader>
        
        <div className="flex-1 bg-muted rounded-lg overflow-hidden">
          {!hasValidUrl ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <FileText className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">Arquivo não disponível</p>
                <p className="text-sm text-muted-foreground mt-2">
                  O documento não possui URL válida para visualização
                </p>
              </div>
            </div>
          ) : (
            <div className="h-full">
              {/* Usar endpoint proxy para todos os tipos de documento */}
              <iframe
                src={`http://localhost:8001/api/frontend/documents/${documento.id}/view`}
                title={documento.numero}
                className="w-full h-full rounded border-0"
                style={{ minHeight: '400px' }}
                onError={() => {
                  console.log('Erro ao carregar documento via proxy:', documento.id);
                }}
              />
            </div>
          )}
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
  const [documentosReais, setDocumentosReais] = useState<any[]>([]);
  const [carregandoDocumentos, setCarregandoDocumentos] = useState(true);
  const [versioningModalOpen, setVersioningModalOpen] = useState(false);
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);
  const [selectedDocumentForVersioning, setSelectedDocumentForVersioning] = useState<any>(null);
  const [documentVersions, setDocumentVersions] = useState<any[]>([]);
  const [documentApproval, setDocumentApproval] = useState<any>(null);
  const { toast } = useToast();

  // Carregar documentos reais quando componente monta
  React.useEffect(() => {
    carregarDocumentos();
  }, []);

  const carregarDocumentos = async () => {
    setCarregandoDocumentos(true);
    try {
      const response = await fetch('http://localhost:8001/api/frontend/documents');
      const result = await response.json();
      
      if (result.success || result.data) {
        // Converter formato da API para formato do frontend
        const documentosFormatados = (result.data || []).map((doc: any) => ({
          id: doc.id,
          numero: doc.number,
          tipo: doc.type === 'CTE' ? 'CT-e' : doc.type === 'INVOICE' ? 'NF-e' : doc.type,
          cliente: doc.client,
          jornada: doc.order_id?.substring(0, 8) || "N/A",
          origem: doc.origin,
          destino: doc.destination,
          dataUpload: doc.date,
          dataEmissao: doc.date,
          status: doc.status,
          tamanho: doc.size,
          versao: doc.current_version || doc.version_count || 1,
          uploadPor: "Sistema",
          origem_upload: "api",
          visualizacoes: 0,
          ultimaVisualizacao: doc.date,
          // Incluir dados reais do S3
          s3_url: doc.s3_url,
          s3_key: doc.s3_key,
          has_valid_s3: doc.has_valid_s3,
          current_version: doc.current_version,
          version_count: doc.version_count,
          approval_status: doc.approval_status
        }));
        
        setDocumentosReais(documentosFormatados);
      }
    } catch (error) {
      console.error('Erro ao carregar documentos:', error);
      toast({
        title: "Erro ao carregar documentos",
        description: "Usando dados de exemplo",
        variant: "destructive"
      });
      // Em caso de erro, usar dados mock
      setDocumentosReais([]);
    } finally {
      setCarregandoDocumentos(false);
    }
  };

  // Usar documentos reais se disponíveis, senão usar mock
  const todosDocumentos = documentosReais.length > 0 ? documentosReais : documentosData;

  const documentosFiltrados = todosDocumentos.filter(doc => {
    const matchFiltro = doc.numero.toLowerCase().includes(filtro.toLowerCase()) ||
                       doc.cliente.toLowerCase().includes(filtro.toLowerCase());
    const matchTipo = tipoFiltro === "todos" || doc.tipo === tipoFiltro;
    const matchStatus = statusFiltro === "todos" || doc.status === statusFiltro;
    const matchOrigem = origemFiltro === "todos" || doc.origem_upload === origemFiltro;
    
    return matchFiltro && matchTipo && matchStatus && matchOrigem;
  });

  const handleDownload = async (doc: any) => {
    try {
      if (!doc.id) {
        throw new Error('ID do documento não disponível');
      }

      toast({
        title: "Download Iniciado",
        description: `Baixando ${doc.numero}...`,
      });

      // Usar endpoint proxy para download
      const downloadUrl = `http://localhost:8001/api/frontend/documents/${doc.id}/download`;
      
      // Criar link temporário para download
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = doc.numero;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast({
        title: "Download Concluído",
        description: `${doc.numero} baixado com sucesso!`,
      });

    } catch (error) {
      console.error('Erro no download:', error);
      toast({
        title: "Erro no Download",
        description: error instanceof Error ? error.message : "Não foi possível baixar o documento.",
        variant: "destructive"
      });
    }
  };

  const handleView = async (doc: any) => {
    try {
      // Documento já tem todos os dados necessários incluindo URL do S3
      setDocumentoSelecionado(doc);
      setViewerOpen(true);
      
      // Incrementar contador de visualizações (opcional)
      if (doc.id) {
        fetch(`http://localhost:8001/files/${doc.id}/increment-access`, {
          method: 'POST'
        }).catch(err => console.log('Erro ao incrementar acesso:', err));
      }
      
    } catch (error) {
      console.error('Erro ao abrir documento:', error);
      toast({
        title: "Erro ao Visualizar",
        description: "Não foi possível abrir o documento.",
        variant: "destructive"
      });
    }
  };

  const handleVersioning = async (doc: any) => {
    try {
      setSelectedDocumentForVersioning(doc);
      
      // Carregar versões do documento
      const response = await fetch(`http://localhost:8001/api/frontend/documents/${doc.id}/versions`);
      const result = await response.json();
      
      if (result.success) {
        setDocumentVersions(result.data || []);
      } else {
        setDocumentVersions([]);
      }
      
      setVersioningModalOpen(true);
    } catch (error) {
      console.error('Erro ao carregar versões:', error);
      toast({
        title: "Erro",
        description: "Não foi possível carregar as versões do documento",
        variant: "destructive"
      });
    }
  };

  const handleApproval = async (doc: any) => {
    try {
      setSelectedDocumentForVersioning(doc);
      
      // Carregar informações de aprovação do documento
      const response = await fetch(`http://localhost:8001/api/frontend/documents/${doc.id}/approval`);
      const result = await response.json();
      
      if (result.success && result.data) {
        setDocumentApproval(result.data);
      } else {
        setDocumentApproval(null);
      }
      
      setApprovalModalOpen(true);
    } catch (error) {
      console.error('Erro ao carregar aprovação:', error);
      setDocumentApproval(null);
      setApprovalModalOpen(true);
    }
  };

  const handleCreateVersion = async (data: {
    version_type: "major" | "minor" | "revision" | "auto";
    changes_description: string;
    file?: File;
  }) => {
    if (!selectedDocumentForVersioning) return;

    const formData = new FormData();
    formData.append('version_type', data.version_type);
    formData.append('changes_description', data.changes_description);
    if (data.file) {
      formData.append('file', data.file);
    }

    const response = await fetch(
      `http://localhost:8001/api/frontend/documents/${selectedDocumentForVersioning.id}/versions`,
      {
        method: 'POST',
        body: formData
      }
    );

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Erro ao criar versão');
    }

    // Recarregar versões
    await handleVersioning(selectedDocumentForVersioning);
    await carregarDocumentos(); // Atualizar lista principal
  };

  const handleViewVersion = (versionId: string) => {
    const downloadUrl = `http://localhost:8001/api/frontend/documents/versions/${versionId}/view`;
    window.open(downloadUrl, '_blank');
  };

  const handleDownloadVersion = (versionId: string) => {
    const downloadUrl = `http://localhost:8001/api/frontend/documents/versions/${versionId}/download`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `version-${versionId}`;
    link.click();
  };

  const handleSubmitApproval = async (decision: "approved" | "rejected" | "request_changes", comment: string) => {
    if (!selectedDocumentForVersioning || !documentApproval) return;

    const response = await fetch(
      `http://localhost:8001/api/frontend/documents/approval/${documentApproval.approval_id}/decision`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          decision,
          comment,
          approver_id: 'current-user', // Should be from auth context
        })
      }
    );

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Erro ao enviar aprovação');
    }

    // Recarregar informações de aprovação
    await handleApproval(selectedDocumentForVersioning);
    await carregarDocumentos(); // Atualizar lista principal
  };

  const handleRequestApproval = async (workflowId: string) => {
    if (!selectedDocumentForVersioning) return;

    const response = await fetch(
      `http://localhost:8001/api/frontend/documents/${selectedDocumentForVersioning.id}/request-approval`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          workflow_id: workflowId,
          version_id: selectedDocumentForVersioning.current_version_id,
        })
      }
    );

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Erro ao solicitar aprovação');
    }

    // Recarregar informações de aprovação
    await handleApproval(selectedDocumentForVersioning);
  };

  const estatisticas = {
    total: todosDocumentos.length,
    validados: todosDocumentos.filter(d => d.status === "Validado").length,
    pendentes: todosDocumentos.filter(d => d.status === "Pendente Validação").length,
    rejeitados: todosDocumentos.filter(d => d.status === "Rejeitado").length,
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
                              v{doc.current_version || doc.versao}
                            </Badge>
                            {doc.version_count && doc.version_count > 1 && (
                              <Badge variant="secondary" className="text-xs">
                                {doc.version_count} versões
                              </Badge>
                            )}
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
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button size="sm" variant="outline">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleVersioning(doc)}>
                              <GitBranch className="w-4 h-4 mr-2" />
                              Versões
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleApproval(doc)}>
                              <UserCheck className="w-4 h-4 mr-2" />
                              Aprovação
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleView(doc)}>
                              <Eye className="w-4 h-4 mr-2" />
                              Visualizar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDownload(doc)}>
                              <Download className="w-4 h-4 mr-2" />
                              Download
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-red-600">
                              <AlertCircle className="w-4 h-4 mr-2" />
                              Excluir
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
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
          onUploadSuccess={carregarDocumentos}
        />
        
        <DocumentViewer
          documento={documentoSelecionado}
          isOpen={viewerOpen}
          onClose={() => setViewerOpen(false)}
        />

        {/* Versioning Modal */}
        <Dialog open={versioningModalOpen} onOpenChange={setVersioningModalOpen}>
          <DialogContent className="max-w-4xl h-[80vh]">
            <DialogHeader>
              <DialogTitle>
                Controle de Versões - {selectedDocumentForVersioning?.numero}
              </DialogTitle>
            </DialogHeader>
            <div className="flex-1 overflow-y-auto">
              {selectedDocumentForVersioning && (
                <DocumentVersioning
                  documentId={selectedDocumentForVersioning.id}
                  currentVersion={selectedDocumentForVersioning.current_version || selectedDocumentForVersioning.versao?.toString() || "1.0"}
                  versions={documentVersions}
                  onCreateVersion={handleCreateVersion}
                  onViewVersion={handleViewVersion}
                  onDownloadVersion={handleDownloadVersion}
                  isLoading={false}
                />
              )}
            </div>
          </DialogContent>
        </Dialog>

        {/* Approval Modal */}
        <Dialog open={approvalModalOpen} onOpenChange={setApprovalModalOpen}>
          <DialogContent className="max-w-4xl h-[80vh]">
            <DialogHeader>
              <DialogTitle>
                Aprovação de Documento - {selectedDocumentForVersioning?.numero}
              </DialogTitle>
            </DialogHeader>
            <div className="flex-1 overflow-y-auto">
              {selectedDocumentForVersioning && (
                <DocumentApproval
                  documentId={selectedDocumentForVersioning.id}
                  versionId={selectedDocumentForVersioning.current_version_id}
                  approval={documentApproval}
                  canApprove={true} // This should be determined by user permissions
                  currentUserId="current-user" // This should come from auth context
                  onSubmitApproval={handleSubmitApproval}
                  onRequestApproval={handleRequestApproval}
                  isLoading={false}
                />
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}