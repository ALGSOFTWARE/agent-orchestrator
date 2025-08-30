import { useState } from "react";
import { FileText, Truck, Clock, Search, Zap, EyeOff, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface QuickActionsProps {
  onActionClick: (action: string) => void;
  onOpenSmartMenu: () => void;
}

const quickActions = [
  {
    id: "recent-docs",
    icon: <Clock className="w-4 h-4" />,
    label: "Docs Recentes",
    prompt: "Mostrar meus documentos mais recentes"
  },
  {
    id: "track-shipment",
    icon: <Truck className="w-4 h-4" />,
    label: "Rastrear",
    prompt: "Quero rastrear um embarque"
  },
  {
    id: "search-docs",
    icon: <Search className="w-4 h-4" />,
    label: "Buscar Docs",
    prompt: "Buscar documentos específicos"
  },
  {
    id: "status-summary",
    icon: <FileText className="w-4 h-4" />,
    label: "Resumo Status",
    prompt: "Mostrar resumo do status das minhas cargas"
  }
];

export const QuickActions = ({ onActionClick, onOpenSmartMenu }: QuickActionsProps) => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) {
    return (
      <div className="flex justify-center">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsVisible(true)}
          className="text-brand-primary hover:text-brand-primary hover:bg-brand-primary/10"
        >
          <Eye className="w-4 h-4 mr-1" />
          Mostrar Ações Rápidas
        </Button>
      </div>
    );
  }

  return (
    <Card className="p-4 bg-gradient-to-r from-brand-primary/5 to-brand-secondary/5 border-brand-primary/20">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-foreground">Ações Rápidas</h3>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsVisible(false)}
            className="text-muted-foreground hover:text-foreground hover:bg-muted/50"
          >
            <EyeOff className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onOpenSmartMenu}
            className="text-brand-primary hover:text-brand-primary hover:bg-brand-primary/10"
          >
            <Zap className="w-4 h-4 mr-1" />
            Menu Inteligente
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2">
        {quickActions.map((action) => (
          <Button
            key={action.id}
            variant="ghost"
            size="sm"
            onClick={() => onActionClick(action.prompt)}
            className="h-auto p-2 flex flex-col items-center space-y-1 hover:bg-brand-primary/10 hover:text-brand-primary"
          >
            {action.icon}
            <span className="text-xs">{action.label}</span>
          </Button>
        ))}
      </div>
      
      <div className="mt-3 pt-3 border-t border-border/50">
        <p className="text-xs text-muted-foreground text-center">
          Use o <strong>Menu Inteligente</strong> para fluxos guiados
        </p>
      </div>
    </Card>
  );
};