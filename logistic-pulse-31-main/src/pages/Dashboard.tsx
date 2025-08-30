import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, CartesianGrid } from "recharts";
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Clock, 
  CheckCircle, 
  Users, 
  FileText,
  Truck,
  Package,
  Target
} from "lucide-react";

// Mock data
const kpiData = [
  {
    title: "Tempo Médio de Entrega",
    value: "3.2 dias",
    change: "-0.3",
    trend: "down",
    icon: Clock
  },
  {
    title: "SLA Atendido",
    value: "94.2%",
    change: "+2.1",
    trend: "up",
    icon: Target
  },
  {
    title: "NPS",
    value: "8.7",
    change: "+0.5",
    trend: "up", 
    icon: TrendingUp
  },
  {
    title: "Incidentes",
    value: "12",
    change: "+3",
    trend: "up",
    icon: AlertTriangle
  }
];

const statusData = [
  { status: "Em Trânsito", value: 45, color: "hsl(var(--chart-1))" },
  { status: "Entregue", value: 30, color: "hsl(var(--chart-2))" },
  { status: "Aguardando Doc", value: 15, color: "hsl(var(--chart-3))" },
  { status: "Pendente", value: 10, color: "hsl(var(--chart-4))" }
];

const clienteData = [
  { name: "Cliente A", entregas: 45, sla: 96 },
  { name: "Cliente B", entregas: 32, sla: 89 },
  { name: "Cliente C", entregas: 28, sla: 94 },
  { name: "Cliente D", entregas: 21, sla: 91 }
];

const alertas = [
  { tipo: "Atraso", descricao: "Entrega XYZ-001 com atraso de 2h", criticidade: "alta" },
  { tipo: "Falha", descricao: "Sistema de rastreamento offline", criticidade: "media" },
  { tipo: "Tempo Parado", descricao: "Veículo ABC-123 parado há 4h", criticidade: "alta" }
];

const documentosChat = [
  { tipo: "CT-e", quantidade: 23, hoje: 5 },
  { tipo: "NF-e", quantidade: 18, hoje: 3 },
  { tipo: "BL", quantidade: 12, hoje: 2 },
  { tipo: "AWB", quantidade: 8, hoje: 1 }
];

const ultimosEmbarques = [
  { id: "EMB-001", cliente: "Cliente A", destino: "São Paulo", status: "Em Trânsito", data: "2024-01-15" },
  { id: "EMB-002", cliente: "Cliente B", destino: "Rio de Janeiro", status: "Entregue", data: "2024-01-14" },
  { id: "EMB-003", cliente: "Cliente C", destino: "Belo Horizonte", status: "Aguardando Doc", data: "2024-01-13" }
];

const chartConfig = {
  entregas: { label: "Entregas", color: "hsl(var(--chart-1))" },
  sla: { label: "SLA %", color: "hsl(var(--chart-2))" }
};

export default function Dashboard() {
  return (
    <AppLayout>
      <div className="p-6 space-y-6 h-full overflow-y-auto">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">Visão macro da operação logística em tempo real</p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {kpiData.map((kpi, index) => (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{kpi.title}</CardTitle>
                <kpi.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{kpi.value}</div>
                <p className="text-xs text-muted-foreground flex items-center">
                  {kpi.trend === "up" ? (
                    <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                  ) : (
                    <TrendingDown className="h-3 w-3 mr-1 text-red-500" />
                  )}
                  {kpi.change} vs mês anterior
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico de Status */}
          <Card>
            <CardHeader>
              <CardTitle>Cargas por Status</CardTitle>
              <CardDescription>Distribuição atual das cargas</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      dataKey="value"
                      label={({ status, value }) => `${status}: ${value}`}
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <ChartTooltip content={<ChartTooltipContent />} />
                  </PieChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Performance por Cliente */}
          <Card>
            <CardHeader>
              <CardTitle>Performance por Cliente</CardTitle>
              <CardDescription>Entregas e SLA por cliente</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={clienteData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="entregas" fill="hsl(var(--chart-1))" />
                    <Bar dataKey="sla" fill="hsl(var(--chart-2))" />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Alertas Operacionais */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2" />
                Alertas Operacionais
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {alertas.map((alerta, index) => (
                <Alert key={index} variant={alerta.criticidade === "alta" ? "destructive" : "default"}>
                  <AlertDescription>
                    <div className="flex justify-between items-start">
                      <div>
                        <Badge variant={alerta.criticidade === "alta" ? "destructive" : "secondary"}>
                          {alerta.tipo}
                        </Badge>
                        <p className="mt-1 text-sm">{alerta.descricao}</p>
                      </div>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </CardContent>
          </Card>

          {/* Documentos via Chat */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Documentos Recebidos
              </CardTitle>
              <CardDescription>Resumo de documentos via chat</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {documentosChat.map((doc, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <div>
                      <Badge variant="outline">{doc.tipo}</Badge>
                      <p className="text-sm text-muted-foreground">Total: {doc.quantidade}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-primary">{doc.hoje}</div>
                      <p className="text-xs text-muted-foreground">hoje</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Últimos Embarques */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Truck className="h-5 w-5 mr-2" />
                Últimos Embarques
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {ultimosEmbarques.map((embarque) => (
                    <TableRow key={embarque.id}>
                      <TableCell className="font-medium">{embarque.id}</TableCell>
                      <TableCell>{embarque.cliente}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={
                            embarque.status === "Entregue" ? "default" : 
                            embarque.status === "Em Trânsito" ? "secondary" : 
                            "destructive"
                          }
                        >
                          {embarque.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}