import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { 
  Plus, 
  Search, 
  Building2, 
  Phone, 
  Mail, 
  MapPin, 
  TrendingUp, 
  Star,
  MessageCircle,
  FileText,
  Activity,
  Users,
  Package,
  AlertTriangle
} from "lucide-react";

interface Cliente {
  id: string;
  nome: string;
  empresa: string;
  email: string;
  telefone: string;
  endereco: string;
  score: number;
  status: "ativo" | "inativo" | "pendente";
  totalEmbarques: number;
  engajamentoChat: number;
  nps: number;
  ultimaAtividade: string;
}

const clientesData: Cliente[] = [
  {
    id: "1",
    nome: "João Silva",
    empresa: "Tech Corp",
    email: "joao@techcorp.com",
    telefone: "(11) 99999-9999",
    endereco: "São Paulo, SP",
    score: 92,
    status: "ativo",
    totalEmbarques: 45,
    engajamentoChat: 78,
    nps: 9,
    ultimaAtividade: "2 horas atrás"
  },
  {
    id: "2",
    nome: "Maria Santos",
    empresa: "Global Logistics",
    email: "maria@global.com",
    telefone: "(21) 88888-8888",
    endereco: "Rio de Janeiro, RJ",
    score: 87,
    status: "ativo",
    totalEmbarques: 32,
    engajamentoChat: 65,
    nps: 8,
    ultimaAtividade: "1 dia atrás"
  },
  {
    id: "3",
    nome: "Carlos Lima",
    empresa: "Import Express",
    email: "carlos@import.com",
    telefone: "(31) 77777-7777",
    endereco: "Belo Horizonte, MG",
    score: 75,
    status: "pendente",
    totalEmbarques: 18,
    engajamentoChat: 45,
    nps: 7,
    ultimaAtividade: "3 dias atrás"
  }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "ativo": return "bg-success/10 text-success border-success/20";
    case "inativo": return "bg-muted text-muted-foreground border-border";
    case "pendente": return "bg-warning/10 text-warning border-warning/20";
    default: return "bg-muted text-muted-foreground border-border";
  }
};

const getScoreColor = (score: number) => {
  if (score >= 90) return "text-success";
  if (score >= 70) return "text-warning";
  return "text-destructive";
};

export default function Clientes() {
  const [searchTerm, setSearchTerm] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  
  const form = useForm({
    defaultValues: {
      nome: "",
      empresa: "",
      email: "",
      telefone: "",
      endereco: ""
    }
  });

  const filteredClientes = clientesData.filter(cliente =>
    cliente.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cliente.empresa.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cliente.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const onSubmit = (data: any) => {
    console.log("Novo cliente:", data);
    setIsDialogOpen(false);
    form.reset();
  };

  return (
    <AppLayout>
      <div className="flex-1 space-y-6 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Clientes</h1>
            <p className="text-muted-foreground">Gerencie sua carteira de clientes</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-brand-primary hover:bg-brand-primary/90 text-brand-dark">
                <Plus className="w-4 h-4 mr-2" />
                Novo Cliente
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Adicionar Novo Cliente</DialogTitle>
                <DialogDescription>
                  Preencha os dados do cliente para adicionar à carteira.
                </DialogDescription>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="nome"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Nome Completo</FormLabel>
                        <FormControl>
                          <Input placeholder="João Silva" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="empresa"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Empresa</FormLabel>
                        <FormControl>
                          <Input placeholder="Tech Corp" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input type="email" placeholder="joao@empresa.com" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="telefone"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Telefone</FormLabel>
                        <FormControl>
                          <Input placeholder="(11) 99999-9999" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="endereco"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Endereço</FormLabel>
                        <FormControl>
                          <Input placeholder="São Paulo, SP" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="flex justify-end space-x-2 pt-4">
                    <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                      Cancelar
                    </Button>
                    <Button type="submit" className="bg-brand-primary hover:bg-brand-primary/90 text-brand-dark">
                      Adicionar Cliente
                    </Button>
                  </div>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Métricas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Clientes</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{clientesData.length}</div>
              <p className="text-xs text-muted-foreground">+2 este mês</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Clientes Ativos</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{clientesData.filter(c => c.status === "ativo").length}</div>
              <p className="text-xs text-muted-foreground">66% do total</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Score Médio</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round(clientesData.reduce((acc, c) => acc + c.score, 0) / clientesData.length)}
              </div>
              <p className="text-xs text-muted-foreground">+5% vs mês anterior</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">NPS Médio</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round(clientesData.reduce((acc, c) => acc + c.nps, 0) / clientesData.length)}
              </div>
              <p className="text-xs text-muted-foreground">Excelente</p>
            </CardContent>
          </Card>
        </div>

        {/* Conteúdo Principal */}
        <Tabs defaultValue="lista" className="space-y-6">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="lista">Lista de Clientes</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
              <TabsTrigger value="feedbacks">Feedbacks</TabsTrigger>
            </TabsList>
            
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar clientes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-[300px]"
                />
              </div>
            </div>
          </div>

          <TabsContent value="lista">
            <Card>
              <CardHeader>
                <CardTitle>Lista de Clientes</CardTitle>
                <CardDescription>
                  Visualize e gerencie todos os seus clientes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Cliente</TableHead>
                      <TableHead>Contato</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Embarques</TableHead>
                      <TableHead>Engajamento</TableHead>
                      <TableHead>Última Atividade</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredClientes.map((cliente) => (
                      <TableRow key={cliente.id}>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="font-medium">{cliente.nome}</div>
                            <div className="flex items-center text-sm text-muted-foreground">
                              <Building2 className="w-3 h-3 mr-1" />
                              {cliente.empresa}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="flex items-center text-sm">
                              <Mail className="w-3 h-3 mr-1 text-muted-foreground" />
                              {cliente.email}
                            </div>
                            <div className="flex items-center text-sm">
                              <Phone className="w-3 h-3 mr-1 text-muted-foreground" />
                              {cliente.telefone}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(cliente.status)}>
                            {cliente.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <span className={`font-bold ${getScoreColor(cliente.score)}`}>
                            {cliente.score}
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center">
                            <Package className="w-4 h-4 mr-1 text-muted-foreground" />
                            {cliente.totalEmbarques}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center">
                            <MessageCircle className="w-4 h-4 mr-1 text-muted-foreground" />
                            {cliente.engajamentoChat}%
                          </div>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {cliente.ultimaAtividade}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Performance por Cliente</CardTitle>
                  <CardDescription>Score de performance e entregas</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {clientesData.map((cliente) => (
                      <div key={cliente.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">{cliente.nome}</div>
                          <div className="text-sm text-muted-foreground">{cliente.empresa}</div>
                        </div>
                        <div className="text-right">
                          <div className={`font-bold ${getScoreColor(cliente.score)}`}>
                            {cliente.score}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {cliente.totalEmbarques} embarques
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Engajamento no Chat</CardTitle>
                  <CardDescription>Nível de interação por cliente</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {clientesData.map((cliente) => (
                      <div key={cliente.id} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm font-medium">{cliente.nome}</span>
                          <span className="text-sm text-muted-foreground">{cliente.engajamentoChat}%</span>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div 
                            className="h-2 rounded-full bg-brand-primary"
                            style={{ width: `${cliente.engajamentoChat}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="feedbacks">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>NPS por Cliente</CardTitle>
                  <CardDescription>Net Promoter Score individual</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {clientesData.map((cliente) => (
                      <div key={cliente.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">{cliente.nome}</div>
                          <div className="text-sm text-muted-foreground">{cliente.empresa}</div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="flex">
                            {[...Array(10)].map((_, i) => (
                              <Star
                                key={i}
                                className={`w-4 h-4 ${
                                  i < cliente.nps ? 'text-warning fill-current' : 'text-muted-foreground'
                                }`}
                              />
                            ))}
                          </div>
                          <span className="font-bold">{cliente.nps}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Alertas e Incidentes</CardTitle>
                  <CardDescription>Problemas reportados por cliente</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3 p-3 border rounded-lg border-warning/20 bg-warning/5">
                      <AlertTriangle className="w-5 h-5 text-warning" />
                      <div className="flex-1">
                        <div className="font-medium">Carlos Lima - Import Express</div>
                        <div className="text-sm text-muted-foreground">
                          Atraso na entrega do lote #IE-2024-001
                        </div>
                      </div>
                      <div className="text-sm text-muted-foreground">2h atrás</div>
                    </div>
                    
                    <div className="flex items-center space-x-3 p-3 border rounded-lg">
                      <FileText className="w-5 h-5 text-muted-foreground" />
                      <div className="flex-1">
                        <div className="font-medium">Documentação pendente</div>
                        <div className="text-sm text-muted-foreground">
                          3 clientes com documentos pendentes
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
}