import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from "@/components/ui/tooltip";
import { 
  HoverCard, 
  HoverCardContent, 
  HoverCardTrigger 
} from "@/components/ui/hover-card";
import { X } from "lucide-react";

interface FeatureTooltipProps {
  title: string;
  description: string;
  benefits: string[];
  children: React.ReactNode;
}

const FeatureTooltip = ({ title, description, benefits, children }: FeatureTooltipProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <HoverCard open={isOpen} onOpenChange={setIsOpen}>
      <HoverCardTrigger asChild>
        <div className="cursor-help">
          {children}
        </div>
      </HoverCardTrigger>
      <HoverCardContent className="w-80 p-0" side="right">
        <div className="relative bg-background border rounded-lg shadow-lg">
          <Button
            variant="ghost"
            size="sm"
            className="absolute top-2 right-2 h-6 w-6 p-0"
            onClick={() => setIsOpen(false)}
          >
            <X className="h-3 w-3" />
          </Button>
          
          <div className="p-4">
            <h4 className="font-semibold text-foreground mb-2">{title}</h4>
            <p className="text-sm text-muted-foreground mb-3">{description}</p>
            
            <div className="space-y-2">
              <h5 className="text-xs font-medium text-foreground">Benefícios:</h5>
              <ul className="text-xs text-muted-foreground space-y-1">
                {benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start gap-1">
                    <span className="text-primary">•</span>
                    <span>{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </HoverCardContent>
    </HoverCard>
  );
};

export const SystemExplanation = () => {
  return (
    <TooltipProvider>
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Stagg Tracking
          </h1>
          <p className="text-muted-foreground">
            Sistema inteligente para gestão completa de documentos logísticos
          </p>
        </div>

        {/* Recursos Principais */}
        <Card>
          <CardHeader>
            <CardTitle>Recursos Principais</CardTitle>
            <CardDescription>
              Funcionalidades inteligentes para otimizar sua operação logística
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              
              <FeatureTooltip
                title="Chat com IA Especializada"
                description="Assistente virtual especializado em logística que entende terminologias específicas do setor e pode responder perguntas complexas sobre documentos e operações."
                benefits={[
                  "Respostas precisas em linguagem natural",
                  "Compreensão de termos técnicos",
                  "Disponibilidade 24/7",
                  "Redução de tempo de consulta em 80%"
                ]}
              >
                <Card className="border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <CardContent className="p-4">
                    <Badge className="mb-2">🤖 IA</Badge>
                    <h3 className="font-medium">Chat Inteligente</h3>
                    <p className="text-sm text-muted-foreground">
                      Converse naturalmente sobre seus documentos
                    </p>
                  </CardContent>
                </Card>
              </FeatureTooltip>

              <FeatureTooltip
                title="Rastreamento em Tempo Real"
                description="Monitoramento contínuo de cargas com atualização automática de status, integração com GPS e alertas proativos para desvios de rota ou atrasos."
                benefits={[
                  "Visibilidade completa da cadeia logística",
                  "Alertas automáticos de irregularidades",
                  "Integração com dispositivos IoT",
                  "Histórico completo de movimentações"
                ]}
              >
                <Card className="border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <CardContent className="p-4">
                    <Badge className="mb-2">📍 GPS</Badge>
                    <h3 className="font-medium">Rastreamento</h3>
                    <p className="text-sm text-muted-foreground">
                      Localização precisa em tempo real
                    </p>
                  </CardContent>
                </Card>
              </FeatureTooltip>

              <FeatureTooltip
                title="Gestão Automatizada de Documentos"
                description="Processamento automático de CT-e, NF-e, BL, AWB e outros documentos com OCR avançado, validação automática e organização inteligente."
                benefits={[
                  "Processamento 95% mais rápido",
                  "Redução de erros humanos",
                  "Validação automática de dados",
                  "Organização inteligente por tipo"
                ]}
              >
                <Card className="border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <CardContent className="p-4">
                    <Badge className="mb-2">📄 OCR</Badge>
                    <h3 className="font-medium">Gestão Documental</h3>
                    <p className="text-sm text-muted-foreground">
                      Processamento automático de documentos
                    </p>
                  </CardContent>
                </Card>
              </FeatureTooltip>

              <FeatureTooltip
                title="Integração com ERPs"
                description="Conectividade nativa com principais sistemas ERP do mercado (SAP, Oracle, Totvs) através de APIs robustas e webhooks configuráveis."
                benefits={[
                  "Sincronização automática de dados",
                  "Redução de trabalho manual",
                  "Dados sempre atualizados",
                  "Compatibilidade com múltiplos sistemas"
                ]}
              >
                <Card className="border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <CardContent className="p-4">
                    <Badge className="mb-2">🔗 API</Badge>
                    <h3 className="font-medium">Integração ERP</h3>
                    <p className="text-sm text-muted-foreground">
                      Conecte-se com seus sistemas existentes
                    </p>
                  </CardContent>
                </Card>
              </FeatureTooltip>

              <FeatureTooltip
                title="Analytics Avançado"
                description="Relatórios inteligentes com insights acionáveis, previsões de demanda, análise de performance e identificação de gargalos operacionais."
                benefits={[
                  "Insights baseados em dados reais",
                  "Previsões de demanda precisas",
                  "Identificação de oportunidades",
                  "ROI mensurável"
                ]}
              >
                <Card className="border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <CardContent className="p-4">
                    <Badge className="mb-2">📊 BI</Badge>
                    <h3 className="font-medium">Analytics</h3>
                    <p className="text-sm text-muted-foreground">
                      Relatórios e insights inteligentes
                    </p>
                  </CardContent>
                </Card>
              </FeatureTooltip>

              <FeatureTooltip
                title="Alertas Proativos"
                description="Sistema de notificações inteligentes que antecipa problemas, monitora KPIs críticos e envia alertas personalizados via múltiplos canais."
                benefits={[
                  "Prevenção de problemas",
                  "Notificações personalizáveis",
                  "Múltiplos canais de comunicação",
                  "Priorização automática"
                ]}
              >
                <Card className="border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <CardContent className="p-4">
                    <Badge className="mb-2">🔔 Smart</Badge>
                    <h3 className="font-medium">Alertas Inteligentes</h3>
                    <p className="text-sm text-muted-foreground">
                      Notificações proativas e personalizadas
                    </p>
                  </CardContent>
                </Card>
              </FeatureTooltip>
            </div>
          </CardContent>
        </Card>

        {/* Benefícios da IA */}
        <Card>
          <CardHeader>
            <CardTitle>Inteligência Artificial Aplicada</CardTitle>
            <CardDescription>
              Como a IA revoluciona sua operação logística
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              <FeatureTooltip
                title="Machine Learning Adaptativo"
                description="Algoritmos que aprendem continuamente com seus dados, melhorando previsões e otimizando rotas automaticamente com base no histórico operacional."
                benefits={[
                  "Melhoria contínua de performance",
                  "Personalização para seu negócio",
                  "Previsões cada vez mais precisas",
                  "Otimização automática de processos"
                ]}
              >
                <Card className="border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <CardContent className="p-4">
                    <Badge variant="secondary" className="mb-2">🧠 ML</Badge>
                    <h3 className="font-medium">Aprendizado Contínuo</h3>
                    <p className="text-sm text-muted-foreground">
                      IA que evolui com sua operação
                    </p>
                  </CardContent>
                </Card>
              </FeatureTooltip>

              <FeatureTooltip
                title="Processamento de Linguagem Natural"
                description="Compreensão avançada de textos em documentos, emails e comunicações, com extração automática de informações relevantes e classificação inteligente."
                benefits={[
                  "Compreensão de contexto complexo",
                  "Extração automática de dados",
                  "Classificação inteligente",
                  "Redução de erros de interpretação"
                ]}
              >
                <Card className="border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <CardContent className="p-4">
                    <Badge variant="secondary" className="mb-2">💬 NLP</Badge>
                    <h3 className="font-medium">Compreensão Textual</h3>
                    <p className="text-sm text-muted-foreground">
                      Entende e processa linguagem natural
                    </p>
                  </CardContent>
                </Card>
              </FeatureTooltip>
            </div>
          </CardContent>
        </Card>

        {/* Vantagens Competitivas */}
        <Card>
          <CardHeader>
            <CardTitle>Vantagens Competitivas</CardTitle>
            <CardDescription>
              Por que escolher o Stagg Tracking
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              
              <FeatureTooltip
                title="ROI Comprovado"
                description="Retorno sobre investimento mensurável com redução de custos operacionais, aumento de eficiência e melhoria na satisfação do cliente."
                benefits={[
                  "Redução de 40% nos custos operacionais",
                  "Aumento de 60% na eficiência",
                  "Payback em menos de 6 meses",
                  "Métricas claras de performance"
                ]}
              >
                <div className="text-center p-4 bg-muted/30 rounded-lg border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <div className="text-2xl font-bold text-primary">40%</div>
                  <div className="text-sm text-muted-foreground">Redução de Custos</div>
                </div>
              </FeatureTooltip>

              <FeatureTooltip
                title="Implementação Rápida"
                description="Setup completo em apenas 48 horas com migração automática de dados, treinamento incluído e suporte técnico dedicado."
                benefits={[
                  "Go-live em 48 horas",
                  "Migração automática de dados",
                  "Treinamento completo incluído",
                  "Suporte técnico 24/7"
                ]}
              >
                <div className="text-center p-4 bg-muted/30 rounded-lg border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <div className="text-2xl font-bold text-primary">48h</div>
                  <div className="text-sm text-muted-foreground">Para Implementar</div>
                </div>
              </FeatureTooltip>

              <FeatureTooltip
                title="Satisfação do Cliente"
                description="Alto índice de satisfação com interface intuitiva, suporte especializado e resultados tangíveis desde o primeiro dia de uso."
                benefits={[
                  "Interface intuitiva e amigável",
                  "Suporte especializado",
                  "Resultados imediatos",
                  "Feedback positivo constante"
                ]}
              >
                <div className="text-center p-4 bg-muted/30 rounded-lg border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <div className="text-2xl font-bold text-primary">98%</div>
                  <div className="text-sm text-muted-foreground">Satisfação</div>
                </div>
              </FeatureTooltip>

              <FeatureTooltip
                title="Escalabilidade"
                description="Arquitetura cloud-native que cresce com seu negócio, suportando desde pequenas operações até grandes volumes de transações."
                benefits={[
                  "Infraestrutura cloud-native",
                  "Escalamento automático",
                  "Performance garantida",
                  "Crescimento sem limites"
                ]}
              >
                <div className="text-center p-4 bg-muted/30 rounded-lg border-2 border-dashed border-muted hover:border-primary transition-colors">
                  <div className="text-2xl font-bold text-primary">∞</div>
                  <div className="text-sm text-muted-foreground">Escalabilidade</div>
                </div>
              </FeatureTooltip>
            </div>
          </CardContent>
        </Card>

        <div className="text-center text-sm text-muted-foreground">
          💡 Passe o mouse sobre qualquer funcionalidade para ver detalhes. As caixas de informação podem ser fechadas clicando no ✕
        </div>
      </div>
    </TooltipProvider>
  );
};