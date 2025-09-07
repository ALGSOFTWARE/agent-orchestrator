import { FileSearch, MessageCircle, Users } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatHeaderProps {
  onOpenDocuments: () => void;
}

export const ChatHeader = ({ onOpenDocuments }: ChatHeaderProps) => {
  return (
    <div className="bg-card border-b border-border p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center">
            <MessageCircle className="w-5 h-5 text-brand-dark" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-foreground">Chat Smart Tracking</h1>
            <p className="text-sm text-muted-foreground">
              Central de comunicação e consulta de documentos
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={onOpenDocuments}
            className="border-brand-primary text-brand-dark hover:bg-brand-light"
          >
            <FileSearch className="w-4 h-4 mr-2" />
            Consultar Documentos
          </Button>
          
          <div className="flex items-center space-x-1 text-muted-foreground text-sm">
            <Users className="w-4 h-4" />
            <span>3 clientes online</span>
          </div>
        </div>
      </div>
    </div>
  );
};