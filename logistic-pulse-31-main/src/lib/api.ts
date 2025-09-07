const API_BASE_URL = 'http://localhost:8002';

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  type?: string;
  attachments?: any[];
  action?: string;
  data?: any;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async sendChatMessage(message: string, agent?: string): Promise<ApiResponse<ChatMessage>> {
    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          content: message,
          session_id: 'default',
          agent: agent || 'frontend_logistics_agent'
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || 'Failed to send message',
          status: response.status,
        };
      }

      return {
        data: {
          id: Date.now().toString(),
          content: data.response || data.message || 'Resposta recebida',
          sender: 'assistant',
          timestamp: new Date(),
          attachments: data.attachments || [],
          action: data.action,
          data: data.data,
        },
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  async uploadDocument(file: File): Promise<ApiResponse<any>> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseUrl}/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || 'Failed to upload document',
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  async searchDocuments(query: string): Promise<ApiResponse<any[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/documents/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || 'Failed to search documents',
          status: response.status,
        };
      }

      return {
        data: data.documents || [],
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }
}

export const apiClient = new ApiClient();
export default apiClient;