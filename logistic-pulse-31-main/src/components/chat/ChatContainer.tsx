import { useState, useEffect } from "react";
import { ChatHeader } from "./ChatHeader";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";
import { DocumentModal } from "./DocumentModal";
import { DocumentDetailModal } from "./DocumentDetailModal";
import { SmartMenu, type MenuAction } from "./SmartMenu";
import { MessageInterpreter, type InterpretationResult } from "./MessageInterpreter";
import { useToast } from "@/hooks/use-toast";
import { useChatMessage } from "@/hooks/useApi";

export type DocumentType = "CTE" | "AWL" | "BL" | "MANIFESTO" | "NF";

export interface Message {
  id: string;
  type: "user" | "agent" | "system";
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  attachments?: {
    type: DocumentType;
    name: string;
    url: string;
  }[];
}

export const ChatContainer = () => {
  const [isDocumentModalOpen, setIsDocumentModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isSmartMenuOpen, setIsSmartMenuOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const [sessionId, setSessionId] = useState<string>(() => {
    // Try to get existing session from localStorage or create new one
    const stored = localStorage.getItem('chat_session_id');
    return stored || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  });
  const [userProfile, setUserProfile] = useState({
    name: "Eduardo Silva",
    company: "Mercosul Line",
    role: "Operador Logístico"
  });
  
  // Store session ID in localStorage
  useEffect(() => {
    localStorage.setItem('chat_session_id', sessionId);
  }, [sessionId]);
  
  const { toast } = useToast();
  const interpreter = new MessageInterpreter();
  const chatMutation = useChatMessage();
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      type: "system",
      content: `Olá ${userProfile.name}! Bem-vindo ao Chat Inteligente.

Posso te ajudar a:
• Consultar documentos logísticos
• Verificar status de cargas e entregas
• Buscar informações específicas
• Esclarecer dúvidas sobre suas operações

Como posso ajudá-lo hoje?`,
      timestamp: new Date(),
    }
  ]);

  // Documentos serão buscados via API real quando necessário

  const handleSendMessage = async (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content,
      timestamp: new Date(),
    };
    
    const loadingMessageId = (Date.now() + 1).toString();
    const loadingMessage: Message = {
      id: loadingMessageId,
      type: "agent",
      content: "Analisando sua mensagem...",
      timestamp: new Date(),
      isLoading: true,
    };
    
    // Adicionar mensagem do usuário e mensagem de loading
    setMessages(prev => [...prev, newMessage, loadingMessage]);
    
    try {
      // Usar a API real para processar a mensagem
      const response = await chatMutation.mutateAsync({
        message: content,
        userContext: userProfile,
        sessionId: sessionId
      });
      
      // Criar mensagem de resposta do agente
      const agentResponse: Message = {
        id: loadingMessageId, // Usar o mesmo ID para substituir a mensagem de loading
        type: "agent",
        content: response.message,
        timestamp: new Date(),
        attachments: response.attachments || [],
        isLoading: false,
      };
      
      // Substituir a mensagem de loading pela resposta real
      setMessages(prev => 
        prev.map(msg => 
          msg.id === loadingMessageId ? agentResponse : msg
        )
      );
      
      // Executar ações específicas baseadas na resposta
      if (response.action === 'show_document' && response.data) {
        setTimeout(() => {
          setSelectedDocument(response.data);
          setIsDetailModalOpen(true);
        }, 1000);
      } else if (response.action === 'open_modal') {
        // Implementar outras ações conforme necessário
        console.log('Action:', response.action, 'Data:', response.data);
      }
      
    } catch (error) {
      console.error('Erro no chat:', error);
      
      // Fallback para interpretação local em caso de erro da API
      const interpretation = interpreter.interpret(content);
      
      const errorResponse: Message = {
        id: loadingMessageId, // Usar o mesmo ID para substituir a mensagem de loading
        type: "agent",
        content: "Desculpe, estou com dificuldades para processar sua mensagem no momento. Tente novamente em alguns instantes.",
        timestamp: new Date(),
        isLoading: false,
      };
      
      // Substituir a mensagem de loading pela mensagem de erro
      setMessages(prev => 
        prev.map(msg => 
          msg.id === loadingMessageId ? errorResponse : msg
        )
      );
      
      toast({
        title: "Erro de Conexão",
        description: "Não foi possível conectar com o servidor. Verificando conexão...",
        variant: "destructive"
      });
    }
  };

  const handleSmartMenuAction = (action: MenuAction, inputs?: Record<string, string>) => {
    let finalPrompt = action.suggestedPrompt;
    
    // Construir prompt baseado nos inputs das etapas
    if (inputs && Object.keys(inputs).length > 0) {
      const values = Object.values(inputs).filter(Boolean);
      if (values.length > 0) {
        finalPrompt = `${action.suggestedPrompt}: ${values.join(" - ")}`;
      }
    }
    
    // Enviar como se fosse uma mensagem do usuário
    handleSendMessage(finalPrompt);
    
    toast({
      title: "Ação executada",
      description: `${action.title} foi processado com sucesso.`,
    });
  };

  return (
    <div className="flex flex-col h-full">
      <ChatHeader onOpenDocuments={() => setIsDocumentModalOpen(true)} />
      <ChatMessages messages={messages} />
      <ChatInput 
        onSendMessage={handleSendMessage} 
        onOpenSmartMenu={() => setIsSmartMenuOpen(true)}
      />
      
      <DocumentModal 
        isOpen={isDocumentModalOpen}
        onClose={() => setIsDocumentModalOpen(false)}
      />
      
      <DocumentDetailModal
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        document={selectedDocument}
      />
      
      <SmartMenu
        isVisible={isSmartMenuOpen}
        onClose={() => setIsSmartMenuOpen(false)}
        onActionSelect={handleSmartMenuAction}
        userContext={userProfile}
      />
    </div>
  );
};