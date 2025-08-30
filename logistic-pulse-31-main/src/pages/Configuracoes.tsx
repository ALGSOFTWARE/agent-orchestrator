import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { 
  Users, 
  Settings, 
  Plug, 
  Route, 
  Zap, 
  Bell, 
  Globe, 
  Bot,
  Plus,
  Trash2,
  Edit
} from "lucide-react";
import { toast } from "sonner";

const Configuracoes = () => {
  const [activeTab, setActiveTab] = useState("usuarios");

  const handleSave = () => {
    toast.success("Configurações salvas com sucesso!");
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h1 className="text-3xl font-bold">Configurações</h1>
            <p className="text-muted-foreground">
              Personalize a plataforma de acordo com as regras do cliente
            </p>
          </div>
          <Button onClick={handleSave}>Salvar Alterações</Button>
        </div>

        <div className="flex-1 p-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-8">
              <TabsTrigger value="usuarios" className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                Usuários
              </TabsTrigger>
              <TabsTrigger value="integracoes" className="flex items-center gap-2">
                <Plug className="h-4 w-4" />
                Integrações
              </TabsTrigger>
              <TabsTrigger value="jornadas" className="flex items-center gap-2">
                <Route className="h-4 w-4" />
                Jornadas
              </TabsTrigger>
              <TabsTrigger value="gatilhos" className="flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Gatilhos
              </TabsTrigger>
              <TabsTrigger value="notificacoes" className="flex items-center gap-2">
                <Bell className="h-4 w-4" />
                Notificações
              </TabsTrigger>
              <TabsTrigger value="localizacao" className="flex items-center gap-2">
                <Globe className="h-4 w-4" />
                Localização
              </TabsTrigger>
              <TabsTrigger value="ia" className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                IA
              </TabsTrigger>
              <TabsTrigger value="geral" className="flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Geral
              </TabsTrigger>
            </TabsList>

            {/* Usuários e Permissões */}
            <TabsContent value="usuarios">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Usuários e Permissões</CardTitle>
                    <CardDescription>
                      Gerencie usuários e suas permissões no sistema
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-lg font-medium">Usuários Cadastrados</h3>
                      <Button>
                        <Plus className="h-4 w-4 mr-2" />
                        Novo Usuário
                      </Button>
                    </div>
                    
                    <div className="border rounded-lg">
                      <div className="grid grid-cols-5 gap-4 p-4 border-b font-medium">
                        <div>Nome</div>
                        <div>E-mail</div>
                        <div>Perfil</div>
                        <div>Status</div>
                        <div>Ações</div>
                      </div>
                      <div className="grid grid-cols-5 gap-4 p-4">
                        <div>João Silva</div>
                        <div>joao@empresa.com</div>
                        <div><Badge>Administrador</Badge></div>
                        <div><Badge variant="outline">Ativo</Badge></div>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Perfis de Permissão</h3>
                      <div className="grid grid-cols-3 gap-4">
                        <Card>
                          <CardHeader>
                            <CardTitle className="text-base">Administrador</CardTitle>
                            <CardDescription>Acesso total ao sistema</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2 text-sm">
                              <div className="flex items-center gap-2">
                                <Switch checked />
                                <span>Configurações</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Switch checked />
                                <span>Usuários</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Switch checked />
                                <span>Relatórios</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        <Card>
                          <CardHeader>
                            <CardTitle className="text-base">Operador</CardTitle>
                            <CardDescription>Operações básicas</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2 text-sm">
                              <div className="flex items-center gap-2">
                                <Switch />
                                <span>Configurações</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Switch checked />
                                <span>Jornadas</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Switch checked />
                                <span>Entregas</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        <Card>
                          <CardHeader>
                            <CardTitle className="text-base">Visualizador</CardTitle>
                            <CardDescription>Apenas leitura</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2 text-sm">
                              <div className="flex items-center gap-2">
                                <Switch />
                                <span>Editar dados</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Switch checked />
                                <span>Visualizar relatórios</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Switch checked />
                                <span>Dashboard</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Integrações */}
            <TabsContent value="integracoes">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Configuração de Integrações</CardTitle>
                    <CardDescription>
                      Configure conexões com TMS, ERPs e APIs externas
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium mb-4">TMS (Transportation Management System)</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="tms-url">URL da API</Label>
                          <Input id="tms-url" placeholder="https://api.tms.com/v1" />
                        </div>
                        <div>
                          <Label htmlFor="tms-key">Chave de API</Label>
                          <Input id="tms-key" type="password" placeholder="••••••••" />
                        </div>
                        <div>
                          <Label htmlFor="tms-timeout">Timeout (ms)</Label>
                          <Input id="tms-timeout" placeholder="30000" />
                        </div>
                        <div>
                          <Label htmlFor="tms-status">Status</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o status" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="ativo">Ativo</SelectItem>
                              <SelectItem value="inativo">Inativo</SelectItem>
                              <SelectItem value="teste">Teste</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">ERP</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="erp-sistema">Sistema ERP</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o ERP" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="sap">SAP</SelectItem>
                              <SelectItem value="oracle">Oracle</SelectItem>
                              <SelectItem value="totvs">TOTVS</SelectItem>
                              <SelectItem value="outros">Outros</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="erp-database">Servidor de Banco</Label>
                          <Input id="erp-database" placeholder="servidor.empresa.com" />
                        </div>
                        <div>
                          <Label htmlFor="erp-user">Usuário</Label>
                          <Input id="erp-user" placeholder="usuario_integracao" />
                        </div>
                        <div>
                          <Label htmlFor="erp-password">Senha</Label>
                          <Input id="erp-password" type="password" placeholder="••••••••" />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">APIs Externas</h3>
                      <div className="space-y-4">
                        <Button variant="outline">
                          <Plus className="h-4 w-4 mr-2" />
                          Adicionar Nova API
                        </Button>
                        
                        <div className="border rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="font-medium">Google Maps API</h4>
                              <p className="text-sm text-muted-foreground">Geocodificação e cálculo de rotas</p>
                            </div>
                            <Badge>Ativo</Badge>
                          </div>
                          <div className="grid grid-cols-2 gap-4 mt-4">
                            <div>
                              <Label>Endpoint</Label>
                              <Input value="https://maps.googleapis.com/maps/api" readOnly />
                            </div>
                            <div>
                              <Label>Chave</Label>
                              <Input type="password" value="••••••••••••••••" readOnly />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Templates de Jornadas */}
            <TabsContent value="jornadas">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Templates de Jornadas</CardTitle>
                    <CardDescription>
                      Cadastre e configure templates padrão para jornadas
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-lg font-medium">Templates Disponíveis</h3>
                      <Button>
                        <Plus className="h-4 w-4 mr-2" />
                        Novo Template
                      </Button>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base">Entrega Expressa</CardTitle>
                          <CardDescription>Template para entregas urgentes</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2 text-sm">
                            <div>• Coleta automática</div>
                            <div>• Notificação a cada 30min</div>
                            <div>• SLA: 4 horas</div>
                            <div>• Prioridade: Alta</div>
                          </div>
                          <div className="flex gap-2 mt-4">
                            <Button size="sm" variant="outline">Editar</Button>
                            <Button size="sm" variant="outline">Duplicar</Button>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base">Entrega Padrão</CardTitle>
                          <CardDescription>Template para entregas normais</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2 text-sm">
                            <div>• Coleta programada</div>
                            <div>• Notificação diária</div>
                            <div>• SLA: 24 horas</div>
                            <div>• Prioridade: Normal</div>
                          </div>
                          <div className="flex gap-2 mt-4">
                            <Button size="sm" variant="outline">Editar</Button>
                            <Button size="sm" variant="outline">Duplicar</Button>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Configuração de Template</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="template-nome">Nome do Template</Label>
                          <Input id="template-nome" placeholder="Nome do template" />
                        </div>
                        <div>
                          <Label htmlFor="template-categoria">Categoria</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione a categoria" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="expressa">Expressa</SelectItem>
                              <SelectItem value="normal">Normal</SelectItem>
                              <SelectItem value="agendada">Agendada</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="template-sla">SLA (horas)</Label>
                          <Input id="template-sla" type="number" placeholder="24" />
                        </div>
                        <div>
                          <Label htmlFor="template-prioridade">Prioridade</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione a prioridade" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="baixa">Baixa</SelectItem>
                              <SelectItem value="normal">Normal</SelectItem>
                              <SelectItem value="alta">Alta</SelectItem>
                              <SelectItem value="critica">Crítica</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="col-span-2">
                          <Label htmlFor="template-descricao">Descrição</Label>
                          <Textarea id="template-descricao" placeholder="Descreva o template..." />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Gatilhos */}
            <TabsContent value="gatilhos">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Gatilhos Personalizados</CardTitle>
                    <CardDescription>
                      Configure ações automáticas baseadas em eventos
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-lg font-medium">Gatilhos Ativos</h3>
                      <Button>
                        <Plus className="h-4 w-4 mr-2" />
                        Novo Gatilho
                      </Button>
                    </div>

                    <div className="space-y-4">
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base flex items-center gap-2">
                            <Zap className="h-4 w-4" />
                            Atraso na Entrega
                          </CardTitle>
                          <CardDescription>
                            Aciona quando uma entrega está atrasada
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <Label className="text-xs">Condição</Label>
                              <p>SLA &gt; 2 horas</p>
                            </div>
                            <div>
                              <Label className="text-xs">Ação</Label>
                              <p>Enviar notificação + Criar ticket</p>
                            </div>
                            <div>
                              <Label className="text-xs">Status</Label>
                              <Badge>Ativo</Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base flex items-center gap-2">
                            <Zap className="h-4 w-4" />
                            Cliente VIP
                          </CardTitle>
                          <CardDescription>
                            Prioriza entregas de clientes VIP
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <Label className="text-xs">Condição</Label>
                              <p>Cliente.tipo = VIP</p>
                            </div>
                            <div>
                              <Label className="text-xs">Ação</Label>
                              <p>Prioridade Alta + Notificar gestor</p>
                            </div>
                            <div>
                              <Label className="text-xs">Status</Label>
                              <Badge>Ativo</Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Criar Novo Gatilho</h3>
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="gatilho-nome">Nome do Gatilho</Label>
                          <Input id="gatilho-nome" placeholder="Nome descritivo do gatilho" />
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="gatilho-evento">Evento Disparador</Label>
                            <Select>
                              <SelectTrigger>
                                <SelectValue placeholder="Selecione o evento" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="entrega-criada">Entrega Criada</SelectItem>
                                <SelectItem value="entrega-atrasada">Entrega Atrasada</SelectItem>
                                <SelectItem value="cliente-vip">Cliente VIP</SelectItem>
                                <SelectItem value="sla-vencido">SLA Vencido</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div>
                            <Label htmlFor="gatilho-acao">Ação</Label>
                            <Select>
                              <SelectTrigger>
                                <SelectValue placeholder="Selecione a ação" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="notificar">Enviar Notificação</SelectItem>
                                <SelectItem value="email">Enviar E-mail</SelectItem>
                                <SelectItem value="webhook">Chamar Webhook</SelectItem>
                                <SelectItem value="priorizar">Alterar Prioridade</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>

                        <div>
                          <Label htmlFor="gatilho-condicao">Condição (opcional)</Label>
                          <Textarea 
                            id="gatilho-condicao" 
                            placeholder="Ex: cliente.tipo === 'VIP' && entrega.valor > 1000"
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Notificações */}
            <TabsContent value="notificacoes">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Canais de Notificação</CardTitle>
                    <CardDescription>
                      Configure e-mail, webhook, push notifications
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium mb-4">E-mail</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="email-servidor">Servidor SMTP</Label>
                          <Input id="email-servidor" placeholder="smtp.gmail.com" />
                        </div>
                        <div>
                          <Label htmlFor="email-porta">Porta</Label>
                          <Input id="email-porta" placeholder="587" />
                        </div>
                        <div>
                          <Label htmlFor="email-usuario">Usuário</Label>
                          <Input id="email-usuario" placeholder="noreply@empresa.com" />
                        </div>
                        <div>
                          <Label htmlFor="email-senha">Senha</Label>
                          <Input id="email-senha" type="password" placeholder="••••••••" />
                        </div>
                        <div className="col-span-2">
                          <div className="flex items-center space-x-2">
                            <Switch id="email-ssl" />
                            <Label htmlFor="email-ssl">Usar SSL/TLS</Label>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Webhook</h3>
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="webhook-url">URL do Webhook</Label>
                          <Input id="webhook-url" placeholder="https://api.empresa.com/webhook" />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="webhook-metodo">Método HTTP</Label>
                            <Select>
                              <SelectTrigger>
                                <SelectValue placeholder="Selecione o método" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="POST">POST</SelectItem>
                                <SelectItem value="PUT">PUT</SelectItem>
                                <SelectItem value="PATCH">PATCH</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div>
                            <Label htmlFor="webhook-timeout">Timeout (ms)</Label>
                            <Input id="webhook-timeout" placeholder="30000" />
                          </div>
                        </div>
                        <div>
                          <Label htmlFor="webhook-headers">Headers Personalizados</Label>
                          <Textarea 
                            id="webhook-headers" 
                            placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}'
                          />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Push Notifications</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="push-service">Serviço</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o serviço" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="firebase">Firebase</SelectItem>
                              <SelectItem value="onesignal">OneSignal</SelectItem>
                              <SelectItem value="pusher">Pusher</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="push-key">Chave da API</Label>
                          <Input id="push-key" type="password" placeholder="••••••••" />
                        </div>
                        <div className="col-span-2">
                          <Label htmlFor="push-config">Configuração JSON</Label>
                          <Textarea 
                            id="push-config" 
                            placeholder='{"projectId": "projeto", "apiKey": "chave"}'
                          />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Preferências de Notificação</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <Label>Notificações de Entrega</Label>
                            <p className="text-sm text-muted-foreground">Receber notificações sobre status de entregas</p>
                          </div>
                          <Switch />
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <Label>Alertas de SLA</Label>
                            <p className="text-sm text-muted-foreground">Alertas quando SLA está próximo do vencimento</p>
                          </div>
                          <Switch />
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <Label>Relatórios Automáticos</Label>
                            <p className="text-sm text-muted-foreground">Envio automático de relatórios periódicos</p>
                          </div>
                          <Switch />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Localização */}
            <TabsContent value="localizacao">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Idiomas e Unidades de Medida</CardTitle>
                    <CardDescription>
                      Configure idiomas suportados e unidades de medida
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium mb-4">Configurações de Idioma</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="idioma-padrao">Idioma Padrão</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o idioma" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="pt-BR">Português (Brasil)</SelectItem>
                              <SelectItem value="en-US">English (US)</SelectItem>
                              <SelectItem value="es-ES">Español</SelectItem>
                              <SelectItem value="fr-FR">Français</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="fuso-horario">Fuso Horário</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o fuso" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="America/Sao_Paulo">América/São Paulo (BRT)</SelectItem>
                              <SelectItem value="America/New_York">América/Nova York (EST)</SelectItem>
                              <SelectItem value="Europe/London">Europa/Londres (GMT)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div className="mt-4">
                        <Label className="text-base font-medium">Idiomas Disponíveis</Label>
                        <div className="grid grid-cols-2 gap-2 mt-2">
                          <div className="flex items-center space-x-2">
                            <Switch checked />
                            <Label>Português (Brasil)</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch />
                            <Label>English (US)</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch />
                            <Label>Español</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch />
                            <Label>Français</Label>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Unidades de Medida</h3>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <Label htmlFor="unidade-distancia">Distância</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="km">Quilômetros (km)</SelectItem>
                              <SelectItem value="mi">Milhas (mi)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="unidade-peso">Peso</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="kg">Quilogramas (kg)</SelectItem>
                              <SelectItem value="lb">Libras (lb)</SelectItem>
                              <SelectItem value="ton">Toneladas (ton)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="unidade-volume">Volume</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="m3">Metros Cúbicos (m³)</SelectItem>
                              <SelectItem value="l">Litros (L)</SelectItem>
                              <SelectItem value="ft3">Pés Cúbicos (ft³)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Formatação</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="formato-data">Formato de Data</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o formato" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="dd/mm/yyyy">DD/MM/AAAA</SelectItem>
                              <SelectItem value="mm/dd/yyyy">MM/DD/AAAA</SelectItem>
                              <SelectItem value="yyyy-mm-dd">AAAA-MM-DD</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="formato-hora">Formato de Hora</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o formato" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="24h">24 horas (HH:MM)</SelectItem>
                              <SelectItem value="12h">12 horas (HH:MM AM/PM)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="separador-decimal">Separador Decimal</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value=",">, (vírgula)</SelectItem>
                              <SelectItem value=".">. (ponto)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="separador-milhares">Separador de Milhares</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value=".">. (ponto)</SelectItem>
                              <SelectItem value=",">, (vírgula)</SelectItem>
                              <SelectItem value=" "> (espaço)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* IA */}
            <TabsContent value="ia">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Configuração da IA</CardTitle>
                    <CardDescription>
                      Configure nível de resposta, idiomas e limites da IA
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium mb-4">Configurações Gerais</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="ia-modelo">Modelo de IA</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o modelo" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="gpt-4">GPT-4 (Avançado)</SelectItem>
                              <SelectItem value="gpt-3.5">GPT-3.5 (Padrão)</SelectItem>
                              <SelectItem value="claude">Claude (Anthropic)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="ia-temperatura">Criatividade (0-1)</Label>
                          <Input id="ia-temperatura" type="number" min="0" max="1" step="0.1" placeholder="0.7" />
                        </div>
                        <div>
                          <Label htmlFor="ia-max-tokens">Máximo de Tokens</Label>
                          <Input id="ia-max-tokens" type="number" placeholder="2048" />
                        </div>
                        <div>
                          <Label htmlFor="ia-timeout">Timeout (segundos)</Label>
                          <Input id="ia-timeout" type="number" placeholder="30" />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Nível de Resposta</h3>
                      <div className="space-y-4">
                            <div className="flex items-center space-x-2">
                              <input type="radio" id="nivel-basico" name="nivel" value="basico" />
                              <Label htmlFor="nivel-basico">
                                <span className="font-medium">Básico</span>
                                <p className="text-sm text-muted-foreground">Respostas diretas e objetivas</p>
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="radio" id="nivel-intermediario" name="nivel" value="intermediario" defaultChecked />
                              <Label htmlFor="nivel-intermediario">
                                <span className="font-medium">Intermediário</span>
                                <p className="text-sm text-muted-foreground">Respostas detalhadas com contexto</p>
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="radio" id="nivel-avancado" name="nivel" value="avancado" />
                              <Label htmlFor="nivel-avancado">
                                <span className="font-medium">Avançado</span>
                                <p className="text-sm text-muted-foreground">Respostas completas com análises e sugestões</p>
                              </Label>
                            </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Idiomas Suportados pela IA</h3>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="flex items-center space-x-2">
                          <Switch checked />
                          <Label>Português</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Switch checked />
                          <Label>Inglês</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Switch />
                          <Label>Espanhol</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Switch />
                          <Label>Francês</Label>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Limites e Controles</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="ia-limite-diario">Limite Diário de Consultas</Label>
                          <Input id="ia-limite-diario" type="number" placeholder="1000" />
                        </div>
                        <div>
                          <Label htmlFor="ia-limite-usuario">Limite por Usuário/Hora</Label>
                          <Input id="ia-limite-usuario" type="number" placeholder="50" />
                        </div>
                        <div className="col-span-2">
                          <div className="flex items-center space-x-2">
                            <Switch />
                            <Label>Permitir análise de documentos</Label>
                          </div>
                        </div>
                        <div className="col-span-2">
                          <div className="flex items-center space-x-2">
                            <Switch />
                            <Label>Ativar modo de aprendizado contínuo</Label>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Contexto Personalizado</h3>
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="ia-contexto">Instruções Personalizadas</Label>
                          <Textarea 
                            id="ia-contexto" 
                            placeholder="Adicione instruções específicas para a IA sobre como responder no contexto da sua empresa..."
                            rows={4}
                          />
                        </div>
                        <div>
                          <Label htmlFor="ia-conhecimento">Base de Conhecimento</Label>
                          <Textarea 
                            id="ia-conhecimento" 
                            placeholder="Informações específicas da empresa que a IA deve conhecer..."
                            rows={4}
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Configurações Gerais */}
            <TabsContent value="geral">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Configurações Gerais</CardTitle>
                    <CardDescription>
                      Configurações básicas do sistema
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium mb-4">Informações da Empresa</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="empresa-nome">Nome da Empresa</Label>
                          <Input id="empresa-nome" placeholder="Nome da empresa" />
                        </div>
                        <div>
                          <Label htmlFor="empresa-cnpj">CNPJ</Label>
                          <Input id="empresa-cnpj" placeholder="00.000.000/0000-00" />
                        </div>
                        <div className="col-span-2">
                          <Label htmlFor="empresa-endereco">Endereço</Label>
                          <Input id="empresa-endereco" placeholder="Endereço completo" />
                        </div>
                        <div>
                          <Label htmlFor="empresa-telefone">Telefone</Label>
                          <Input id="empresa-telefone" placeholder="(11) 9999-9999" />
                        </div>
                        <div>
                          <Label htmlFor="empresa-email">E-mail</Label>
                          <Input id="empresa-email" type="email" placeholder="contato@empresa.com" />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Configurações de Sistema</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <Label>Modo de Manutenção</Label>
                            <p className="text-sm text-muted-foreground">Ativar quando necessário realizar manutenções</p>
                          </div>
                          <Switch />
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <Label>Logs Detalhados</Label>
                            <p className="text-sm text-muted-foreground">Ativar logs detalhados para debugging</p>
                          </div>
                          <Switch />
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <Label>Backup Automático</Label>
                            <p className="text-sm text-muted-foreground">Realizar backup automático dos dados</p>
                          </div>
                          <Switch checked />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Segurança</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="session-timeout">Timeout de Sessão (minutos)</Label>
                          <Input id="session-timeout" type="number" placeholder="60" />
                        </div>
                        <div>
                          <Label htmlFor="password-policy">Política de Senha</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione a política" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="basica">Básica (8 caracteres)</SelectItem>
                              <SelectItem value="media">Média (8 char + maiúscula + número)</SelectItem>
                              <SelectItem value="forte">Forte (12 char + símbolos)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="col-span-2">
                          <div className="flex items-center space-x-2">
                            <Switch />
                            <Label>Ativar autenticação de dois fatores (2FA)</Label>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h3 className="text-lg font-medium mb-4">Performance</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="cache-timeout">Cache Timeout (segundos)</Label>
                          <Input id="cache-timeout" type="number" placeholder="300" />
                        </div>
                        <div>
                          <Label htmlFor="max-connections">Máximo de Conexões</Label>
                          <Input id="max-connections" type="number" placeholder="100" />
                        </div>
                        <div className="col-span-2">
                          <div className="flex items-center space-x-2">
                            <Switch checked />
                            <Label>Ativar compressão de dados</Label>
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
      </div>
    </AppLayout>
  );
};

export default Configuracoes;