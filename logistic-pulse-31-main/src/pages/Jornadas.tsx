import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  MapPin, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Package, 
  Truck, 
  Filter,
  Plus,
  Map as MapIcon
} from "lucide-react";

// Mock data
const jornadasData = [
  {
    id: "JOR-001",
    cliente: "Cliente A",
    origem: "São Paulo",
    destino: "Rio de Janeiro",
    status: "Em Trânsito",
    progresso: 65,
    transportadora: "Express Log",
    checkpoints: [
      { nome: "Origem", status: "concluido", data: "2024-01-15 08:00" },
      { nome: "Porto Santos", status: "concluido", data: "2024-01-15 12:00" },
      { nome: "CD Rio", status: "atual", data: "2024-01-15 18:00" },
      { nome: "Entrega", status: "pendente", data: "2024-01-16 14:00" }
    ],
    documentos: ["CT-e", "NF-e", "Manifesto"],
    lat: -22.9068,
    lng: -43.1729
  },
  {
    id: "JOR-002", 
    cliente: "Cliente B",
    origem: "Belo Horizonte",
    destino: "Brasília",
    status: "Aguardando Documento",
    progresso: 30,
    transportadora: "Rápido Trans",
    checkpoints: [
      { nome: "Origem", status: "concluido", data: "2024-01-14 10:00" },
      { nome: "CD Central", status: "atual", data: "2024-01-15 09:00" },
      { nome: "Hub Brasília", status: "pendente", data: "2024-01-16 08:00" },
      { nome: "Entrega", status: "pendente", data: "2024-01-16 16:00" }
    ],
    documentos: ["CT-e", "AWB"],
    lat: -15.7801,
    lng: -47.9292
  },
  {
    id: "JOR-003",
    cliente: "Cliente C", 
    origem: "Salvador",
    destino: "Recife",
    status: "Entregue",
    progresso: 100,
    transportadora: "Norte Log",
    checkpoints: [
      { nome: "Origem", status: "concluido", data: "2024-01-13 07:00" },
      { nome: "Hub Nordeste", status: "concluido", data: "2024-01-13 15:00" },
      { nome: "CD Recife", status: "concluido", data: "2024-01-14 11:00" },
      { nome: "Entrega", status: "concluido", data: "2024-01-14 17:30" }
    ],
    documentos: ["CT-e", "NF-e", "BL", "Comprovante"],
    lat: -8.0476,
    lng: -34.8770
  }
];

const MapComponent = ({ jornadas }: { jornadas: any[] }) => {
  return (
    <div className="w-full h-[400px] bg-muted rounded-lg flex items-center justify-center">
      <div className="text-center">
        <MapIcon className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
        <p className="text-muted-foreground">
          Mapa em tempo real das jornadas
        </p>
        <p className="text-sm text-muted-foreground mt-2">
          Para usar o mapa, configure sua chave Mapbox no Supabase
        </p>
      </div>
    </div>
  );
};

export default function Jornadas() {
  const [filtro, setFiltro] = useState("");
  const [statusFiltro, setStatusFiltro] = useState("todos");
  const [clienteFiltro, setClienteFiltro] = useState("todos");

  const jornadasFiltradas = jornadasData.filter(jornada => {
    const matchFiltro = jornada.id.toLowerCase().includes(filtro.toLowerCase()) ||
                       jornada.cliente.toLowerCase().includes(filtro.toLowerCase());
    const matchStatus = statusFiltro === "todos" || jornada.status === statusFiltro;
    const matchCliente = clienteFiltro === "todos" || jornada.cliente === clienteFiltro;
    
    return matchFiltro && matchStatus && matchCliente;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Entregue": return "default";
      case "Em Trânsito": return "secondary";
      case "Aguardando Documento": return "destructive";
      default: return "outline";
    }
  };

  const getCheckpointIcon = (status: string) => {
    switch (status) {
      case "concluido": return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "atual": return <Clock className="h-4 w-4 text-blue-500" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  return (
    <AppLayout>
      <div className="p-6 space-y-6 h-full overflow-y-auto">
        {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Jornadas</h1>
          <p className="text-muted-foreground">Acompanhe a jornada logística de cada embarque</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Nova Jornada
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
              placeholder="Buscar por ID ou cliente..."
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
                <SelectItem value="Entregue">Entregue</SelectItem>
                <SelectItem value="Aguardando Documento">Aguardando Documento</SelectItem>
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

      <Tabs defaultValue="kanban" className="w-full">
        <TabsList>
          <TabsTrigger value="kanban">Kanban</TabsTrigger>
          <TabsTrigger value="mapa">Mapa</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="kanban" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Coluna Em Trânsito */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg flex items-center">
                <Truck className="h-5 w-5 mr-2 text-blue-500" />
                Em Trânsito
                <Badge className="ml-2">{jornadasFiltradas.filter(j => j.status === "Em Trânsito").length}</Badge>
              </h3>
              {jornadasFiltradas
                .filter(jornada => jornada.status === "Em Trânsito")
                .map(jornada => (
                <Card key={jornada.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-sm">{jornada.id}</CardTitle>
                      <Badge variant={getStatusColor(jornada.status)}>{jornada.status}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{jornada.cliente}</p>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center text-sm">
                      <MapPin className="h-4 w-4 mr-2" />
                      {jornada.origem} → {jornada.destino}
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Progresso</span>
                        <span>{jornada.progresso}%</span>
                      </div>
                      <Progress value={jornada.progresso} className="h-2" />
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {jornada.documentos.map(doc => (
                        <Badge key={doc} variant="outline" className="text-xs">{doc}</Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Coluna Aguardando Documento */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg flex items-center">
                <AlertCircle className="h-5 w-5 mr-2 text-yellow-500" />
                Aguardando Documento
                <Badge className="ml-2">{jornadasFiltradas.filter(j => j.status === "Aguardando Documento").length}</Badge>
              </h3>
              {jornadasFiltradas
                .filter(jornada => jornada.status === "Aguardando Documento")
                .map(jornada => (
                <Card key={jornada.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-sm">{jornada.id}</CardTitle>
                      <Badge variant={getStatusColor(jornada.status)}>{jornada.status}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{jornada.cliente}</p>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center text-sm">
                      <MapPin className="h-4 w-4 mr-2" />
                      {jornada.origem} → {jornada.destino}
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Progresso</span>
                        <span>{jornada.progresso}%</span>
                      </div>
                      <Progress value={jornada.progresso} className="h-2" />
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {jornada.documentos.map(doc => (
                        <Badge key={doc} variant="outline" className="text-xs">{doc}</Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Coluna Entregue */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg flex items-center">
                <CheckCircle className="h-5 w-5 mr-2 text-green-500" />
                Entregue
                <Badge className="ml-2">{jornadasFiltradas.filter(j => j.status === "Entregue").length}</Badge>
              </h3>
              {jornadasFiltradas
                .filter(jornada => jornada.status === "Entregue")
                .map(jornada => (
                <Card key={jornada.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-sm">{jornada.id}</CardTitle>
                      <Badge variant={getStatusColor(jornada.status)}>{jornada.status}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{jornada.cliente}</p>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center text-sm">
                      <MapPin className="h-4 w-4 mr-2" />
                      {jornada.origem} → {jornada.destino}
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Progresso</span>
                        <span>{jornada.progresso}%</span>
                      </div>
                      <Progress value={jornada.progresso} className="h-2" />
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {jornada.documentos.map(doc => (
                        <Badge key={doc} variant="outline" className="text-xs">{doc}</Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="mapa">
          <Card>
            <CardHeader>
              <CardTitle>Visualização em Tempo Real</CardTitle>
            </CardHeader>
            <CardContent>
              <MapComponent jornadas={jornadasFiltradas} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="timeline" className="space-y-4">
          {jornadasFiltradas.map(jornada => (
            <Card key={jornada.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>{jornada.id} - {jornada.cliente}</CardTitle>
                    <p className="text-muted-foreground">{jornada.origem} → {jornada.destino}</p>
                  </div>
                  <Badge variant={getStatusColor(jornada.status)}>{jornada.status}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {jornada.checkpoints.map((checkpoint, index) => (
                    <div key={index} className="flex items-center space-x-4">
                      {getCheckpointIcon(checkpoint.status)}
                      <div className="flex-1">
                        <p className="font-medium">{checkpoint.nome}</p>
                        <p className="text-sm text-muted-foreground">{checkpoint.data}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
      </div>
    </AppLayout>
  );
}