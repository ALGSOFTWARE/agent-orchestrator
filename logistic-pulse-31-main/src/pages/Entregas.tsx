import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { 
  Package, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  MapPin, 
  Camera,
  FileText,
  Filter,
  Plus,
  Eye,
  Edit,
  Truck
} from "lucide-react";

// Mock data
const entregasData = [
  {
    id: "ENT-001",
    cliente: "Cliente A",
    destinatario: "João Silva",
    origem: "São Paulo",
    destino: "Av. Paulista, 1000 - São Paulo/SP",
    status: "Em Trânsito",
    dataEntrega: "2024-01-16",
    horaEstimada: "14:00",
    transportadora: "Express Log",
    motorista: "Carlos Santos",
    veiculo: "ABC-1234",
    documentos: ["CT-e", "NF-e", "DACTE"],
    valor: "R$ 2.500,00",
    peso: "150kg",
    volumes: 3,
    ocorrencias: [],
    lat: -23.5505,
    lng: -46.6333
  },
  {
    id: "ENT-002",
    cliente: "Cliente B", 
    destinatario: "Maria Santos",
    origem: "Rio de Janeiro",
    destino: "Rua das Flores, 500 - Rio de Janeiro/RJ",
    status: "Em Espera",
    dataEntrega: "2024-01-15",
    horaEstimada: "16:30",
    transportadora: "Rápido Trans",
    motorista: "Pedro Oliveira",
    veiculo: "XYZ-5678",
    documentos: ["CT-e", "NF-e"],
    valor: "R$ 1.800,00",
    peso: "85kg",
    volumes: 2,
    ocorrencias: [
      { tipo: "Atraso", descricao: "Trânsito intenso na região", data: "2024-01-15 15:00" }
    ],
    lat: -22.9068,
    lng: -43.1729
  },
  {
    id: "ENT-003",
    cliente: "Cliente C",
    destinatario: "Ana Costa",
    origem: "Belo Horizonte",
    destino: "Av. Afonso Pena, 2000 - Belo Horizonte/MG", 
    status: "Entregue",
    dataEntrega: "2024-01-14",
    horaEstimada: "10:00",
    horaEntrega: "09:45",
    transportadora: "Norte Log",
    motorista: "José Lima",
    veiculo: "DEF-9012",
    documentos: ["CT-e", "NF-e", "DACTE", "Comprovante"],
    valor: "R$ 3.200,00",
    peso: "220kg",
    volumes: 5,
    ocorrencias: [],
    comprovante: {
      foto: "entrega-003.jpg",
      assinatura: "Ana Costa",
      coordenadas: "-19.9167, -43.9345",
      dataHora: "2024-01-14 09:45"
    },
    lat: -19.9167,
    lng: -43.9345
  }
];

export default function Entregas() {
  const [filtro, setFiltro] = useState("");
  const [statusFiltro, setStatusFiltro] = useState("todos");
  const [clienteFiltro, setClienteFiltro] = useState("todos");
  const [entregaSelecionada, setEntregaSelecionada] = useState<any>(null);
  const [novaOcorrencia, setNovaOcorrencia] = useState("");

  const entregasFiltradas = entregasData.filter(entrega => {
    const matchFiltro = entrega.id.toLowerCase().includes(filtro.toLowerCase()) ||
                       entrega.cliente.toLowerCase().includes(filtro.toLowerCase()) ||
                       entrega.destinatario.toLowerCase().includes(filtro.toLowerCase());
    const matchStatus = statusFiltro === "todos" || entrega.status === statusFiltro;
    const matchCliente = clienteFiltro === "todos" || entrega.cliente === clienteFiltro;
    
    return matchFiltro && matchStatus && matchCliente;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Entregue": return "default";
      case "Em Trânsito": return "secondary";
      case "Em Espera": return "destructive";
      case "Entrega Parcial": return "outline";
      default: return "outline";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "Entregue": return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "Em Trânsito": return <Truck className="h-4 w-4 text-blue-500" />;
      case "Em Espera": return <Clock className="h-4 w-4 text-yellow-500" />;
      default: return <Package className="h-4 w-4 text-gray-400" />;
    }
  };

  return (
    <AppLayout>
      <div className="p-6 space-y-6 h-full overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Entregas</h1>
            <p className="text-muted-foreground">Gerencie e acompanhe entregas ponto a ponto</p>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nova Entrega
          </Button>
        </div>

        {/* Filtros */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Filter className="h-5 w-5 mr-2" />
              Filtros
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Input
                placeholder="Buscar por ID, cliente ou destinatário..."
                value={filtro}
                onChange={(e) => setFiltro(e.target.value)}
              />
              <Select value={statusFiltro} onValueChange={setStatusFiltro}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os Status</SelectItem>
                  <SelectItem value="Em Trânsito">Em Trânsito</SelectItem>
                  <SelectItem value="Em Espera">Em Espera</SelectItem>
                  <SelectItem value="Entregue">Entregue</SelectItem>
                  <SelectItem value="Entrega Parcial">Entrega Parcial</SelectItem>
                </SelectContent>
              </Select>
              <Select value={clienteFiltro} onValueChange={setClienteFiltro}>
                <SelectTrigger>
                  <SelectValue placeholder="Cliente" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os Clientes</SelectItem>
                  <SelectItem value="Cliente A">Cliente A</SelectItem>
                  <SelectItem value="Cliente B">Cliente B</SelectItem>
                  <SelectItem value="Cliente C">Cliente C</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline">
                Aplicar Filtros
              </Button>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="lista" className="w-full">
          <TabsList>
            <TabsTrigger value="lista">Lista</TabsTrigger>
            <TabsTrigger value="cards">Cards</TabsTrigger>
            <TabsTrigger value="mapa">Mapa</TabsTrigger>
          </TabsList>

          <TabsContent value="lista">
            <Card>
              <CardHeader>
                <CardTitle>Lista de Entregas</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ID</TableHead>
                      <TableHead>Cliente</TableHead>
                      <TableHead>Destinatário</TableHead>
                      <TableHead>Destino</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Data/Hora</TableHead>
                      <TableHead>Valor</TableHead>
                      <TableHead>Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {entregasFiltradas.map((entrega) => (
                      <TableRow key={entrega.id}>
                        <TableCell className="font-medium">{entrega.id}</TableCell>
                        <TableCell>{entrega.cliente}</TableCell>
                        <TableCell>{entrega.destinatario}</TableCell>
                        <TableCell className="max-w-[200px] truncate">{entrega.destino}</TableCell>
                        <TableCell>
                          <Badge variant={getStatusColor(entrega.status)}>
                            {entrega.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div>
                            <div>{entrega.dataEntrega}</div>
                            <div className="text-sm text-muted-foreground">{entrega.horaEstimada}</div>
                          </div>
                        </TableCell>
                        <TableCell>{entrega.valor}</TableCell>
                        <TableCell>
                          <div className="flex space-x-2">
                            <Dialog>
                              <DialogTrigger asChild>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => setEntregaSelecionada(entrega)}
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                                <DialogHeader>
                                  <DialogTitle>Detalhes da Entrega - {entregaSelecionada?.id}</DialogTitle>
                                </DialogHeader>
                                
                                {entregaSelecionada && (
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* Informações Básicas */}
                                    <Card>
                                      <CardHeader>
                                        <CardTitle className="text-lg">Informações da Entrega</CardTitle>
                                      </CardHeader>
                                      <CardContent className="space-y-3">
                                        <div className="flex justify-between">
                                          <span className="font-medium">Status:</span>
                                          <Badge variant={getStatusColor(entregaSelecionada.status)}>
                                            {entregaSelecionada.status}
                                          </Badge>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="font-medium">Cliente:</span>
                                          <span>{entregaSelecionada.cliente}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="font-medium">Destinatário:</span>
                                          <span>{entregaSelecionada.destinatario}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="font-medium">Transportadora:</span>
                                          <span>{entregaSelecionada.transportadora}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="font-medium">Motorista:</span>
                                          <span>{entregaSelecionada.motorista}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="font-medium">Veículo:</span>
                                          <span>{entregaSelecionada.veiculo}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="font-medium">Valor:</span>
                                          <span>{entregaSelecionada.valor}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="font-medium">Peso:</span>
                                          <span>{entregaSelecionada.peso}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="font-medium">Volumes:</span>
                                          <span>{entregaSelecionada.volumes}</span>
                                        </div>
                                      </CardContent>
                                    </Card>

                                    {/* Endereços */}
                                    <Card>
                                      <CardHeader>
                                        <CardTitle className="text-lg">Endereços</CardTitle>
                                      </CardHeader>
                                      <CardContent className="space-y-4">
                                        <div>
                                          <div className="flex items-center mb-2">
                                            <MapPin className="h-4 w-4 mr-2 text-green-500" />
                                            <span className="font-medium">Origem</span>
                                          </div>
                                          <p className="text-sm text-muted-foreground ml-6">{entregaSelecionada.origem}</p>
                                        </div>
                                        <div>
                                          <div className="flex items-center mb-2">
                                            <MapPin className="h-4 w-4 mr-2 text-red-500" />
                                            <span className="font-medium">Destino</span>
                                          </div>
                                          <p className="text-sm text-muted-foreground ml-6">{entregaSelecionada.destino}</p>
                                        </div>
                                      </CardContent>
                                    </Card>

                                    {/* Documentos */}
                                    <Card>
                                      <CardHeader>
                                        <CardTitle className="text-lg">Documentos</CardTitle>
                                      </CardHeader>
                                      <CardContent>
                                        <div className="flex flex-wrap gap-2">
                                          {entregaSelecionada.documentos.map((doc: string) => (
                                            <Badge key={doc} variant="outline" className="cursor-pointer hover:bg-muted">
                                              <FileText className="h-3 w-3 mr-1" />
                                              {doc}
                                            </Badge>
                                          ))}
                                        </div>
                                      </CardContent>
                                    </Card>

                                    {/* Comprovante de Entrega */}
                                    {entregaSelecionada.comprovante && (
                                      <Card>
                                        <CardHeader>
                                          <CardTitle className="text-lg">Comprovante de Entrega</CardTitle>
                                        </CardHeader>
                                        <CardContent className="space-y-3">
                                          <div className="flex justify-between">
                                            <span className="font-medium">Assinatura:</span>
                                            <span>{entregaSelecionada.comprovante.assinatura}</span>
                                          </div>
                                          <div className="flex justify-between">
                                            <span className="font-medium">Data/Hora:</span>
                                            <span>{entregaSelecionada.comprovante.dataHora}</span>
                                          </div>
                                          <div className="flex justify-between">
                                            <span className="font-medium">Coordenadas:</span>
                                            <span className="text-sm">{entregaSelecionada.comprovante.coordenadas}</span>
                                          </div>
                                          <Button variant="outline" size="sm" className="w-full">
                                            <Camera className="h-4 w-4 mr-2" />
                                            Ver Foto da Entrega
                                          </Button>
                                        </CardContent>
                                      </Card>
                                    )}
                                  </div>
                                )}
                              </DialogContent>
                            </Dialog>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="cards">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {entregasFiltradas.map((entrega) => (
                <Card key={entrega.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{entrega.id}</CardTitle>
                        <p className="text-sm text-muted-foreground">{entrega.cliente}</p>
                      </div>
                      <Badge variant={getStatusColor(entrega.status)}>
                        {entrega.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center text-sm">
                      <MapPin className="h-4 w-4 mr-2" />
                      <span className="truncate">{entrega.destino}</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <Clock className="h-4 w-4 mr-2" />
                      <span>{entrega.dataEntrega} - {entrega.horaEstimada}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{entrega.valor}</span>
                      <div className="flex space-x-1">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="mapa">
            <Card>
              <CardHeader>
                <CardTitle>Rastreamento em Tempo Real</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="w-full h-[400px] bg-muted rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <MapPin className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">
                      Mapa de rastreamento das entregas
                    </p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Para usar o mapa, configure sua chave Mapbox no Supabase
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
}