import { DocumentType } from "./ChatContainer";

export interface DocumentRequest {
  type: DocumentType | "ANY";
  identifier?: string; // número da carga, embarque, etc.
  client?: string;
  isValidRequest: boolean;
  confidence: number; // 0-1
  suggestedQuery?: string;
}

export interface InterpretationResult {
  isDocumentRequest: boolean;
  documentRequest?: DocumentRequest;
  intent: "document_query" | "status_check" | "general_help" | "unknown";
  suggestedResponse?: string;
  needsMoreInfo?: boolean;
  missingFields?: string[];
}

export class MessageInterpreter {
  private documentKeywords = {
    CTE: ["cte", "ct-e", "conhecimento", "transporte", "frete"],
    AWL: ["awl", "awb", "air waybill", "aéreo", "avião"],
    BL: ["bl", "bill of lading", "conhecimento", "marítimo", "navio"],
    MANIFESTO: ["manifesto", "manifest", "lista", "carga"],
    NF: ["nf", "nfe", "nf-e", "nota fiscal", "fiscal"]
  };

  private actionKeywords = [
    "envie", "enviar", "mandar", "mostrar", "exibir", "ver", "consultar", 
    "buscar", "procurar", "encontrar", "localizar", "quero", "preciso", 
    "gostaria", "pode", "baixar", "download"
  ];

  private identifierPatterns = [
    /\b\d{6,}\b/, // números com 6+ dígitos
    /\b[A-Z]{2,}\d{3,}\b/, // letras seguidas de números
    /\bcarga\s+([A-Z0-9]+)/i,
    /\bembarque\s+([A-Z0-9]+)/i,
    /\bnúmero\s+([A-Z0-9]+)/i
  ];

  interpret(message: string): InterpretationResult {
    const lowerMessage = message.toLowerCase();
    
    // Verificar se é uma solicitação de documento
    const hasActionKeyword = this.actionKeywords.some(keyword => 
      lowerMessage.includes(keyword)
    );

    if (!hasActionKeyword) {
      return this.handleNonDocumentRequest(message);
    }

    // Identificar tipo de documento
    const documentType = this.identifyDocumentType(lowerMessage);
    
    // Extrair identificadores
    const identifier = this.extractIdentifier(message);
    
    // Calcular confiança
    const confidence = this.calculateConfidence(lowerMessage, documentType, identifier);

    if (confidence > 0.6) {
      return {
        isDocumentRequest: true,
        intent: "document_query",
        documentRequest: {
          type: documentType,
          identifier,
          isValidRequest: true,
          confidence,
          suggestedQuery: this.buildSuggestedQuery(documentType, identifier)
        }
      };
    }

    // Se a confiança é baixa, pedir mais informações
    if (confidence > 0.3) {
      return {
        isDocumentRequest: true,
        intent: "document_query",
        needsMoreInfo: true,
        missingFields: this.identifyMissingFields(documentType, identifier),
        suggestedResponse: this.buildClarificationMessage(documentType, identifier)
      };
    }

    return this.handleNonDocumentRequest(message);
  }

  private identifyDocumentType(message: string): DocumentType | "ANY" {
    for (const [type, keywords] of Object.entries(this.documentKeywords)) {
      if (keywords.some(keyword => message.includes(keyword))) {
        return type as DocumentType;
      }
    }
    return "ANY";
  }

  private extractIdentifier(message: string): string | undefined {
    for (const pattern of this.identifierPatterns) {
      const match = message.match(pattern);
      if (match) {
        return match[1] || match[0];
      }
    }
    return undefined;
  }

  private calculateConfidence(message: string, type: DocumentType | "ANY", identifier?: string): number {
    let confidence = 0;

    // Pontuação por tipo de documento identificado
    if (type !== "ANY") confidence += 0.4;

    // Pontuação por identificador encontrado
    if (identifier) confidence += 0.3;

    // Pontuação por palavras-chave de ação
    const actionMatches = this.actionKeywords.filter(keyword => 
      message.includes(keyword)
    ).length;
    confidence += Math.min(actionMatches * 0.1, 0.3);

    return Math.min(confidence, 1);
  }

  private buildSuggestedQuery(type: DocumentType | "ANY", identifier?: string): string {
    if (type === "ANY" && identifier) {
      return `Buscar documentos relacionados a ${identifier}`;
    }
    if (type !== "ANY" && identifier) {
      return `Buscar ${type} do ${identifier}`;
    }
    if (type !== "ANY") {
      return `Buscar documentos do tipo ${type}`;
    }
    return "Buscar documentos";
  }

  private identifyMissingFields(type: DocumentType | "ANY", identifier?: string): string[] {
    const missing: string[] = [];
    
    if (type === "ANY") missing.push("tipo do documento");
    if (!identifier) missing.push("número/identificador");
    
    return missing;
  }

  private buildClarificationMessage(type: DocumentType | "ANY", identifier?: string): string {
    const missing = this.identifyMissingFields(type, identifier);
    
    if (missing.length === 0) return "";
    
    let message = "Para te ajudar melhor, preciso de mais informações. ";
    
    if (missing.includes("tipo do documento")) {
      message += "Que tipo de documento você está procurando? (CT-e, NF-e, BL, Manifesto, etc.) ";
    }
    
    if (missing.includes("número/identificador")) {
      message += "Qual o número da carga, embarque ou documento? ";
    }
    
    return message;
  }

  private handleNonDocumentRequest(message: string): InterpretationResult {
    const lowerMessage = message.toLowerCase();
    
    // Verificar se é consulta de status
    if (lowerMessage.includes("status") || lowerMessage.includes("situação") || 
        lowerMessage.includes("onde está") || lowerMessage.includes("andamento")) {
      return {
        isDocumentRequest: false,
        intent: "status_check",
        suggestedResponse: "Vou verificar o status da sua carga. Você pode me informar o número do embarque ou da carga?"
      };
    }
    
    // Verificar se é pedido de ajuda geral
    if (lowerMessage.includes("ajuda") || lowerMessage.includes("como") || 
        lowerMessage.includes("o que") || lowerMessage.includes("posso")) {
      return {
        isDocumentRequest: false,
        intent: "general_help",
        suggestedResponse: "Posso te ajudar a consultar documentos logísticos (CT-e, NF-e, BL, Manifesto), verificar status de cargas e esclarecer dúvidas sobre suas entregas. O que você gostaria de fazer?"
      };
    }
    
    return {
      isDocumentRequest: false,
      intent: "unknown",
      suggestedResponse: "Como posso te ajudar hoje? Você pode consultar documentos, verificar status de cargas ou tirar dúvidas sobre suas entregas."
    };
  }
}