import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Truck, 
  MapPin, 
  Clock, 
  Package,
  Target,
  Download,
  Filter
} from "lucide-react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const deliveryData = [
  { month: 'Jan', entregas: 120, atrasadas: 8 },
  { month: 'Fev', entregas: 145, atrasadas: 12 },
  { month: 'Mar', entregas: 167, atrasadas: 6 },
  { month: 'Abr', entregas: 189, atrasadas: 15 },
  { month: 'Mai', entregas: 201, atrasadas: 9 },
  { month: 'Jun', entregas: 234, atrasadas: 11 },
];

const routeEfficiencyData = [
  { rota: 'Rota A', eficiencia: 92 },
  { rota: 'Rota B', eficiencia: 87 },
  { rota: 'Rota C', eficiencia: 95 },
  { rota: 'Rota D', eficiencia: 83 },
  { rota: 'Rota E', eficiencia: 89 },
];

const statusData = [
  { name: 'Entregues', value: 1847, color: '#22c55e' },
  { name: 'Em Trânsito', value: 234, color: '#3b82f6' },
  { name: 'Atrasadas', value: 67, color: '#ef4444' },
  { name: 'Pendentes', value: 89, color: '#f59e0b' },
];

const kpis = [
  {
    title: "Total Entregas",
    value: "2,237",
    change: "+12.5%",
    changeType: "positive",
    icon: Truck,
    description: "Este mês"
  },
  {
    title: "Taxa de Sucesso",
    value: "94.2%",
    change: "+2.1%",
    changeType: "positive",
    icon: Target,
    description: "Meta: 95%"
  },
  {
    title: "Tempo Médio",
    value: "2.4h",
    change: "-15min",
    changeType: "positive",
    icon: Clock,
    description: "Por entrega"
  },
  {
    title: "Rotas Ativas",
    value: "48",
    change: "+3",
    changeType: "positive",
    icon: MapPin,
    description: "Hoje"
  }
];

const Relatorios = () => {
  return (
    <AppLayout>
      <div className="flex-1 overflow-auto bg-background">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Relatórios & BI</h1>
              <p className="text-muted-foreground mt-1">Análise detalhada das operações logísticas</p>
            </div>
            <div className="flex gap-3">
              <Select defaultValue="30days">
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7days">Últimos 7 dias</SelectItem>
                  <SelectItem value="30days">Últimos 30 dias</SelectItem>
                  <SelectItem value="90days">Últimos 90 dias</SelectItem>
                  <SelectItem value="year">Este ano</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm">
                <Filter className="w-4 h-4 mr-2" />
                Filtros
              </Button>
              <Button size="sm">
                <Download className="w-4 h-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>

          {/* KPIs */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {kpis.map((kpi, index) => (
              <Card key={index} className="border-border">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">{kpi.title}</p>
                      <p className="text-3xl font-bold text-foreground mt-2">{kpi.value}</p>
                      <div className="flex items-center mt-2">
                        <Badge 
                          variant={kpi.changeType === "positive" ? "default" : "destructive"}
                          className="text-xs"
                        >
                          {kpi.changeType === "positive" ? (
                            <TrendingUp className="w-3 h-3 mr-1" />
                          ) : (
                            <TrendingDown className="w-3 h-3 mr-1" />
                          )}
                          {kpi.change}
                        </Badge>
                        <span className="text-xs text-muted-foreground ml-2">{kpi.description}</span>
                      </div>
                    </div>
                    <div className="p-3 bg-primary/10 rounded-lg">
                      <kpi.icon className="w-6 h-6 text-primary" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Charts */}
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Visão Geral</TabsTrigger>
              <TabsTrigger value="deliveries">Entregas</TabsTrigger>
              <TabsTrigger value="routes">Rotas</TabsTrigger>
              <TabsTrigger value="performance">Performance</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Entregas por Mês
                    </CardTitle>
                    <CardDescription>
                      Comparativo de entregas realizadas e atrasadas
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={deliveryData}>
                        <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="entregas" fill="hsl(var(--primary))" name="Entregas" />
                        <Bar dataKey="atrasadas" fill="hsl(var(--destructive))" name="Atrasadas" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Package className="w-5 h-5" />
                      Status das Entregas
                    </CardTitle>
                    <CardDescription>
                      Distribuição atual dos status de entrega
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={statusData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={120}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {statusData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="flex flex-wrap gap-4 mt-4">
                      {statusData.map((item, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: item.color }}
                          />
                          <span className="text-sm text-muted-foreground">
                            {item.name}: {item.value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="deliveries" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Análise de Entregas</CardTitle>
                  <CardDescription>
                    Tendência de entregas e performance mensal
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={deliveryData}>
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="entregas" 
                        stroke="hsl(var(--primary))" 
                        strokeWidth={3}
                        name="Entregas Realizadas"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="atrasadas" 
                        stroke="hsl(var(--destructive))" 
                        strokeWidth={3}
                        name="Entregas Atrasadas"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="routes" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Eficiência por Rota</CardTitle>
                  <CardDescription>
                    Performance das rotas em percentual de eficiência
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={routeEfficiencyData} layout="horizontal">
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis type="number" domain={[0, 100]} />
                      <YAxis dataKey="rota" type="category" />
                      <Tooltip formatter={(value) => [`${value}%`, 'Eficiência']} />
                      <Bar dataKey="eficiencia" fill="hsl(var(--primary))" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="performance" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Indicadores de Performance</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center p-4 bg-muted/50 rounded-lg">
                      <span className="font-medium">Taxa de Entrega no Prazo</span>
                      <Badge className="bg-green-100 text-green-800">94.2%</Badge>
                    </div>
                    <div className="flex justify-between items-center p-4 bg-muted/50 rounded-lg">
                      <span className="font-medium">Tempo Médio de Entrega</span>
                      <Badge variant="outline">2h 24min</Badge>
                    </div>
                    <div className="flex justify-between items-center p-4 bg-muted/50 rounded-lg">
                      <span className="font-medium">Satisfação do Cliente</span>
                      <Badge className="bg-blue-100 text-blue-800">4.8/5</Badge>
                    </div>
                    <div className="flex justify-between items-center p-4 bg-muted/50 rounded-lg">
                      <span className="font-medium">Custo por Entrega</span>
                      <Badge variant="outline">R$ 8.50</Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Metas vs Realizado</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Entregas do Mês</span>
                        <span>2,237 / 2,500</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div className="bg-primary h-2 rounded-full" style={{ width: '89.5%' }}></div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Taxa de Sucesso</span>
                        <span>94.2% / 95%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div className="bg-primary h-2 rounded-full" style={{ width: '99.2%' }}></div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Redução de Custos</span>
                        <span>12% / 15%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div className="bg-primary h-2 rounded-full" style={{ width: '80%' }}></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppLayout>
  );
};

export default Relatorios;