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
  const [userProfile, setUserProfile] = useState({
    name: "Eduardo Silva",
    company: "Mercosul Line",
    role: "Operador Logístico"
  });
  
  const { toast } = useToast();
  const interpreter = new MessageInterpreter();
  const chatMutation = useChatMessage();
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "system",
      content: `Olá ${userProfile.name}, vejo que você é ${userProfile.role} da ${userProfile.company}. Bem-vindo ao Smart Tracking Chat! 

Posso te ajudar a:
• Consultar documentos logísticos (CT-e, NF-e, BL, Manifesto)
• Verificar status de cargas e entregas
• Localizar documentos por número de embarque
• Esclarecer dúvidas sobre suas operações

Como posso ajudá-lo hoje?`,
      timestamp: new Date(Date.now() - 60000),
    },
    {
      id: "2",
      type: "user",
      content: "Gostaria de consultar o CT-e da carga ABC123",
      timestamp: new Date(Date.now() - 45000),
    },
    {
      id: "3",
      type: "agent",
      content: "Encontrei o CT-e da carga ABC123. O documento está anexado e disponível para download. Status atual: Em trânsito para São Paulo.",
      timestamp: new Date(Date.now() - 30000),
      attachments: [
        {
          type: "CTE",
          name: "CTE-ABC123-2024.pdf",
          url: "#"
        }
      ]
    },
    {
      id: "4",
      type: "user",
      content: "Preciso consultar alguns documentos específicos",
      timestamp: new Date(Date.now() - 15000),
    },
    {
      id: "5",
      type: "agent",
      content: "Claro! Você pode usar nossa consulta rápida de documentos. Clique no botão abaixo para acessar todos os tipos de documentos disponíveis.",
      timestamp: new Date(Date.now() - 5000),
    }
  ]);

  // Mock data para demonstração
  const mockDocuments = [
    {
      id: "doc-1",
      type: "CTE" as DocumentType,
      number: "CTE-ABC123-2024",
      status: "Processado" as const,
      client: "Mercosul Line",
      embarque: "EMB-2024-001",
      rota: {
        origem: "São Paulo - SP",
        destino: "Porto Alegre - RS", 
        status: "Em trânsito",
        proximaParada: "Curitiba - PR"
      },
      dataRecebimento: new Date(Date.now() - 86400000),
      arquivo: {
        nome: "CTE-ABC123-2024.pdf",
        tamanho: "245 KB",
        url: "#"
      },
      historico: [
        {
          data: new Date(Date.now() - 86400000),
          acao: "Documento recebido via API",
          usuario: "Sistema Automatizado"
        },
        {
          data: new Date(Date.now() - 82800000),
          acao: "Documento validado",
          usuario: "Ana Silva"
        }
      ],
      metadados: {
        transportadora: "Expresso Logística",
        valor: "R$ 2.450,00",
        peso: "1.250 kg"
      }
    }
  ];

  const findDocument = (query: string): any | null => {
    return mockDocuments.find(doc => 
      doc.number.toLowerCase().includes(query.toLowerCase()) ||
      doc.embarque.toLowerCase().includes(query.toLowerCase()) ||
      query.toLowerCase().includes(doc.number.toLowerCase().split('-')[1])
    );
  };

  const handleSendMessage = async (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, newMessage]);
    
    try {
      // Usar a API real para processar a mensagem
      const response = await chatMutation.mutateAsync({
        message: content,
        userContext: userProfile
      });
      
      // Criar mensagem de resposta do agente
      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: "agent",
        content: response.message,
        timestamp: new Date(),
        attachments: response.attachments || []
      };
      
      setMessages(prev => [...prev, agentResponse]);
      
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
        id: (Date.now() + 1).toString(),
        type: "agent",
        content: "Desculpe, estou com dificuldades para processar sua mensagem no momento. Tente novamente em alguns instantes.",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorResponse]);
      
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
      />
    </div>
  );
};