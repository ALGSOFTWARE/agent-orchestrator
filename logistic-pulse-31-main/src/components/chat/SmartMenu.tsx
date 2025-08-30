import { useState } from "react";
import { 
  FileText, 
  Truck, 
  Search, 
  MessageCircle, 
  Clock, 
  MapPin, 
  ChevronRight,
  ArrowLeft,
  CheckCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface MenuAction {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  category: "document" | "tracking" | "status" | "help";
  suggestedPrompt: string;
  followUpSteps?: MenuStep[];
}

export interface MenuStep {
  id: string;
  title: string;
  type: "input" | "select" | "confirm";
  placeholder?: string;
  options?: { value: string; label: string }[];
  required: boolean;
}

interface SmartMenuProps {
  onActionSelect: (action: MenuAction, inputs?: Record<string, string>) => void;
  isVisible: boolean;
  onClose: () => void;
}

const menuActions: MenuAction[] = [
  {
    id: "consult-document",
    icon: <FileText className="w-5 h-5" />,
    title: "Consultar Documento",
    description: "CT-e, NF-e, BL, Manifesto",
    category: "document",
    suggestedPrompt: "Consultar documento",
    followUpSteps: [
      {
        id: "doc-type",
        title: "Tipo de documento",
        type: "select",
        options: [
          { value: "CTE", label: "CT-e (Conhecimento de Transporte)" },
          { value: "NF", label: "NF-e (Nota Fiscal Eletrônica)" },
          { value: "BL", label: "BL (Bill of Lading)" },
          { value: "MANIFESTO", label: "Manifesto" },
          { value: "AWL", label: "AWB (Air Waybill)" }
        ],
        required: true
      },
      {
        id: "doc-number",
        title: "Número do documento ou carga",
        type: "input",
        placeholder: "Ex: ABC123, EMB-2024-001",
        required: true
      }
    ]
  },
  {
    id: "track-shipment",
    icon: <Truck className="w-5 h-5" />,
    title: "Rastrear Embarque",
    description: "Status e localização atual",
    category: "tracking",
    suggestedPrompt: "Rastrear embarque",
    followUpSteps: [
      {
        id: "shipment-number",
        title: "Número do embarque",
        type: "input",
        placeholder: "Ex: EMB-2024-001, 123456",
        required: true
      }
    ]
  },
  {
    id: "check-delivery-status",
    icon: <MapPin className="w-5 h-5" />,
    title: "Status de Entrega",
    description: "Prazo e última atualização",
    category: "status",
    suggestedPrompt: "Verificar status de entrega",
    followUpSteps: [
      {
        id: "delivery-ref",
        title: "Referência da entrega",
        type: "input",
        placeholder: "Número da carga ou embarque",
        required: true
      }
    ]
  },
  {
    id: "recent-shipments",
    icon: <Clock className="w-5 h-5" />,
    title: "Embarques Recentes",
    description: "Últimos 7 dias",
    category: "status",
    suggestedPrompt: "Mostrar embarques recentes dos últimos 7 dias"
  },
  {
    id: "search-client",
    icon: <Search className="w-5 h-5" />,
    title: "Buscar por Cliente",
    description: "Documentos e embarques",
    category: "document",
    suggestedPrompt: "Buscar documentos por cliente",
    followUpSteps: [
      {
        id: "client-name",
        title: "Nome do cliente",
        type: "input",
        placeholder: "Ex: Mercosul Line, ACME Corp",
        required: true
      }
    ]
  },
  {
    id: "help-guide",
    icon: <MessageCircle className="w-5 h-5" />,
    title: "Guia de Uso",
    description: "Como usar o chat",
    category: "help",
    suggestedPrompt: "Como posso usar este chat para consultar documentos e rastrear cargas?"
  }
];

export const SmartMenu = ({ onActionSelect, isVisible, onClose }: SmartMenuProps) => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [selectedAction, setSelectedAction] = useState<MenuAction | null>(null);
  const [stepInputs, setStepInputs] = useState<Record<string, string>>({});
  const [isProcessing, setIsProcessing] = useState(false);

  const resetMenu = () => {
    setCurrentStep(0);
    setSelectedAction(null);
    setStepInputs({});
    setIsProcessing(false);
  };

  const handleActionClick = (action: MenuAction) => {
    if (!action.followUpSteps || action.followUpSteps.length === 0) {
      // Ação sem etapas - executar diretamente
      onActionSelect(action);
      onClose();
      resetMenu();
    } else {
      // Iniciar fluxo de etapas
      setSelectedAction(action);
      setCurrentStep(0);
    }
  };

  const handleStepInput = (stepId: string, value: string) => {
    setStepInputs(prev => ({
      ...prev,
      [stepId]: value
    }));
  };

  const handleNextStep = () => {
    if (!selectedAction?.followUpSteps) return;

    const currentStepData = selectedAction.followUpSteps[currentStep];
    
    if (currentStepData.required && !stepInputs[currentStepData.id]) {
      return; // Não avança se campo obrigatório não preenchido
    }

    if (currentStep < selectedAction.followUpSteps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      // Último passo - executar ação
      setIsProcessing(true);
      setTimeout(() => {
        onActionSelect(selectedAction, stepInputs);
        onClose();
        resetMenu();
      }, 500);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    } else {
      setSelectedAction(null);
      setStepInputs({});
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "document": return "bg-blue-500/10 text-blue-600 border-blue-200";
      case "tracking": return "bg-green-500/10 text-green-600 border-green-200";
      case "status": return "bg-orange-500/10 text-orange-600 border-orange-200";
      case "help": return "bg-purple-500/10 text-purple-600 border-purple-200";
      default: return "bg-gray-500/10 text-gray-600 border-gray-200";
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto bg-card border-border shadow-elevation">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              {selectedAction && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleBack}
                  className="p-1"
                >
                  <ArrowLeft className="w-4 h-4" />
                </Button>
              )}
              <div>
                <h2 className="text-lg font-semibold text-foreground">
                  {selectedAction ? selectedAction.title : "Menu Inteligente"}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {selectedAction 
                    ? `Passo ${currentStep + 1} de ${selectedAction.followUpSteps?.length || 1}`
                    : "Escolha uma ação para começar"
                  }
                </p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              ✕
            </Button>
          </div>

          {!selectedAction ? (
            /* Menu Principal */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {menuActions.map((action) => (
                <Card
                  key={action.id}
                  className="p-4 cursor-pointer hover:shadow-soft transition-all duration-200 border-border hover:border-brand-primary/30 group"
                  onClick={() => handleActionClick(action)}
                >
                  <div className="flex items-start space-x-3">
                    <div className="p-2 rounded-lg bg-brand-primary/10 text-brand-primary group-hover:bg-brand-primary group-hover:text-brand-dark transition-colors">
                      {action.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-medium text-foreground group-hover:text-brand-primary transition-colors">
                          {action.title}
                        </h3>
                        <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-brand-primary transition-colors" />
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        {action.description}
                      </p>
                      <Badge 
                        variant="outline"
                        className={getCategoryColor(action.category)}
                      >
                        {action.category}
                      </Badge>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            /* Fluxo de Etapas */
            <div className="space-y-6">
              {isProcessing ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-primary mx-auto mb-4"></div>
                  <p className="text-muted-foreground">Processando sua solicitação...</p>
                </div>
              ) : (
                <>
                  {/* Progress Bar */}
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-gradient-primary h-2 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${((currentStep + 1) / (selectedAction.followUpSteps?.length || 1)) * 100}%` 
                      }}
                    />
                  </div>

                  {/* Current Step */}
                  {selectedAction.followUpSteps && selectedAction.followUpSteps[currentStep] && (
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-base font-medium text-foreground mb-2">
                          {selectedAction.followUpSteps[currentStep].title}
                        </h3>
                        
                        {selectedAction.followUpSteps[currentStep].type === "input" && (
                          <input
                            type="text"
                            placeholder={selectedAction.followUpSteps[currentStep].placeholder}
                            value={stepInputs[selectedAction.followUpSteps[currentStep].id] || ""}
                            onChange={(e) => handleStepInput(selectedAction.followUpSteps[currentStep].id, e.target.value)}
                            className="w-full p-3 border border-border rounded-lg bg-background text-foreground focus:border-brand-primary focus:outline-none"
                            autoFocus
                          />
                        )}

                        {selectedAction.followUpSteps[currentStep].type === "select" && (
                          <div className="space-y-2">
                            {selectedAction.followUpSteps[currentStep].options?.map((option) => (
                              <Card
                                key={option.value}
                                className={`p-3 cursor-pointer transition-all border ${
                                  stepInputs[selectedAction.followUpSteps[currentStep].id] === option.value
                                    ? "border-brand-primary bg-brand-primary/5"
                                    : "border-border hover:border-brand-primary/30"
                                }`}
                                onClick={() => handleStepInput(selectedAction.followUpSteps[currentStep].id, option.value)}
                              >
                                <div className="flex items-center justify-between">
                                  <span className="text-foreground">{option.label}</span>
                                  {stepInputs[selectedAction.followUpSteps[currentStep].id] === option.value && (
                                    <CheckCircle className="w-4 h-4 text-brand-primary" />
                                  )}
                                </div>
                              </Card>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Action Buttons */}
                      <div className="flex justify-between pt-4">
                        <Button variant="ghost" onClick={handleBack}>
                          Voltar
                        </Button>
                        
                        <Button 
                          onClick={handleNextStep}
                          disabled={
                            selectedAction.followUpSteps[currentStep].required && 
                            !stepInputs[selectedAction.followUpSteps[currentStep].id]
                          }
                          className="bg-gradient-primary text-brand-dark"
                        >
                          {currentStep < (selectedAction.followUpSteps.length - 1) ? "Próximo" : "Executar"}
                        </Button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};