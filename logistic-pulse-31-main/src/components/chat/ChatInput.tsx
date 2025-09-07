import { useState } from "react";
import { Send, Paperclip } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { QuickActions } from "./QuickActions";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onOpenSmartMenu: () => void;
}

export const ChatInput = ({ onSendMessage, onOpenSmartMenu }: ChatInputProps) => {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  return (
    <div className="p-4 bg-card border-t border-border space-y-4">
      {/* Quick Actions */}
      <QuickActions 
        onActionClick={onSendMessage}
        onOpenSmartMenu={onOpenSmartMenu}
      />
      
      <form onSubmit={handleSubmit} className="flex items-center space-x-3">
        <Button 
          type="button" 
          variant="ghost" 
          size="sm"
          className="text-muted-foreground hover:text-foreground"
        >
          <Paperclip className="w-4 h-4" />
        </Button>
        
        <div className="flex-1">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ex: 'Me envie o CT-e da carga ABC123' ou 'Status do embarque XPTO'"
            className="border-muted focus:border-brand-primary"
          />
        </div>
        
        <Button 
          type="submit" 
          disabled={!message.trim()}
          className="bg-gradient-primary hover:opacity-90 text-brand-dark"
        >
          <Send className="w-4 h-4" />
        </Button>
      </form>
      
      <div className="mt-2 flex flex-wrap gap-2">
        {[
          "Me envie o CT-e da carga ABC123",
          "Quero ver o BL do embarque XPTO",
          "Status da carga 987654",
          "Documentos da Mercosul Line"
        ].map((suggestion) => (
          <Button
            key={suggestion}
            variant="ghost"
            size="sm"
            onClick={() => onSendMessage(suggestion)}
            className="text-xs text-muted-foreground hover:text-foreground hover:bg-muted"
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
};