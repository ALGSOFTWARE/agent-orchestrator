import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

// Hook para buscar documentos
export const useDocuments = (filters: any = {}) => {
  return useQuery({
    queryKey: ['documents', filters],
    queryFn: async () => {
      // Mock data para desenvolvimento - substituir por chamada real quando API estiver pronta
      return [];
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

// Hook para buscar entregas
export const useDeliveries = (filters: any = {}) => {
  return useQuery({
    queryKey: ['deliveries', filters],
    queryFn: async () => {
      // Mock data para desenvolvimento - substituir por chamada real quando API estiver pronta
      return [];
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

// Hook para buscar jornadas
export const useJourneys = (filters: any = {}) => {
  return useQuery({
    queryKey: ['journeys', filters],
    queryFn: async () => {
      // Mock data para desenvolvimento - substituir por chamada real quando API estiver pronta
      return [];
    },
    staleTime: 2 * 60 * 1000,
  });
};

// Hook para buscar KPIs do dashboard
export const useDashboardKPIs = (userId: string) => {
  return useQuery({
    queryKey: ['dashboard', 'kpis', userId],
    queryFn: async () => {
      // Mock data para desenvolvimento - substituir por chamada real quando API estiver pronta
      return {
        totalDeliveries: 156,
        completedDeliveries: 142,
        pendingDeliveries: 14,
        deliveryRate: 91.0
      };
    },
    staleTime: 1 * 60 * 1000, // 1 minuto
    refetchInterval: 30000, // Atualizar a cada 30s
  });
};

// Hook para enviar mensagem do chat
export const useChatMessage = () => {
  return useMutation({
    mutationFn: async ({ message, userContext, sessionId }: { message: string; userContext: any; sessionId?: string }) => {
      const response = await apiClient.sendChatMessage(message);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
  });
};

// Hook para upload de documento
export const useUploadDocument = () => {
  return useMutation({
    mutationFn: async (file: File) => {
      const response = await apiClient.uploadDocument(file);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
  });
};

// Hook para buscar ações inteligentes
export const useSmartActions = (userContext: any) => {
  return useQuery({
    queryKey: ['smart-actions', userContext],
    queryFn: async () => {
      // Mock data para desenvolvimento - substituir por chamada real quando API estiver pronta
      return [
        { id: '1', title: 'Consultar documentos recentes', description: 'Ver documentos dos últimos 7 dias', action: 'search_recent' },
        { id: '2', title: 'Status de entregas', description: 'Verificar entregas pendentes', action: 'check_deliveries' },
        { id: '3', title: 'Relatório semanal', description: 'Gerar relatório da semana', action: 'generate_report' }
      ];
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
    enabled: !!userContext, // Só executa se houver contexto do usuário
  });
};