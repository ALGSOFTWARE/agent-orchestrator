import { useQuery, useMutation } from '@tanstack/react-query';
import api from '@/lib/api';

// Hook para buscar documentos
export const useDocuments = (filters: any = {}) => {
  return useQuery({
    queryKey: ['documents', filters],
    queryFn: async () => {
      const { data } = await api.get('/documents', { params: filters });
      return data.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

// Hook para buscar entregas
export const useDeliveries = (filters: any = {}) => {
  return useQuery({
    queryKey: ['deliveries', filters],
    queryFn: async () => {
      const { data } = await api.get('/deliveries', { params: filters });
      return data.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

// Hook para buscar jornadas
export const useJourneys = (filters: any = {}) => {
  return useQuery({
    queryKey: ['journeys', filters],
    queryFn: async () => {
      const { data } = await api.get('/journeys', { params: filters });
      return data.data;
    },
    staleTime: 2 * 60 * 1000,
  });
};

// Hook para buscar KPIs do dashboard
export const useDashboardKPIs = (userId: string) => {
  return useQuery({
    queryKey: ['dashboard', 'kpis', userId],
    queryFn: async () => {
      const { data } = await api.get('/dashboard/kpis', { params: { user_id: userId } });
      return data.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minuto
    refetchInterval: 30000, // Atualizar a cada 30s
  });
};

// Hook para enviar mensagem do chat
export const useChatMessage = () => {
  return useMutation({
    mutationFn: async ({ message, userContext, sessionId }: { message: string; userContext: any; sessionId?: string }) => {
      const { data } = await api.post('/chat/message', {
        message,
        user_context: userContext,
        session_id: sessionId
      });
      return data.data;
    },
  });
};

// Hook para upload de documento
export const useUploadDocument = () => {
  return useMutation({
    mutationFn: async (fileData: any) => {
      const { data } = await api.post('/documents/upload', {
        file_data: fileData
      });
      return data.data;
    },
  });
};

// Hook para buscar ações inteligentes
export const useSmartActions = (userContext: any) => {
  return useQuery({
    queryKey: ['smart-actions', userContext],
    queryFn: async () => {
      const { data } = await api.post('/chat/smart-actions', {
        user_context: userContext
      });
      return data.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
    enabled: !!userContext, // Só executa se houver contexto do usuário
  });
};