import { ChatOllama } from '@langchain/community/chat_models/ollama';
import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { PromptTemplate } from '@langchain/core/prompts';
import dotenv from 'dotenv';

// Carrega variáveis de ambiente
dotenv.config();

class MITTrackingAgent {
  constructor() {
    this.llm = new ChatOllama({
      baseUrl: "http://localhost:11434",
      model: "llama3.2:3b",
      temperature: 0.3,
    });

    this.systemPrompt = `Você é um assistente especializado da plataforma MIT Tracking da Move In Tech. 

Sua expertise inclui:
- Consulta e interpretação de CT-e (Conhecimento de Transporte Eletrônico)
- Rastreamento em tempo real de containers e cargas
- Informações sobre BL (Bill of Lading/Conhecimento de Embarque)
- Cálculos e previsões de ETA (Estimated Time of Arrival) e ETD (Estimated Time of Departure)
- Status de entregas e tracking logístico
- Identificação de atrasos e eventos de rota

Você deve responder especificamente sobre:
- Números de CT-e quando questionado
- Status atual de containers e cargas
- Localização de documentos logísticos
- Previsões de chegada e saída

Sempre mantenha um tom profissional e técnico, fornecendo informações claras e objetivas sobre logística e transporte.`;
  }

  async consultarLogistica(consulta) {
    try {
      console.log('🔍 Processando consulta logística...');
      
      const messages = [
        new SystemMessage(this.systemPrompt),
        new HumanMessage(consulta)
      ];

      const response = await this.llm.invoke(messages);
      return response.content;
    } catch (error) {
      console.error('❌ Erro ao consultar:', error.message);
      return `Erro ao processar consulta: ${error.message}`;
    }
  }
}

async function main() {
  try {
    console.log('🚀 Iniciando MIT Tracking - Agente Conversacional de Logística...\n');

    const agent = new MITTrackingAgent();
    
    console.log('✅ Agente MIT Tracking inicializado com sucesso!');
    console.log('🎯 Especialização: Consultas de CT-e, rastreamento de containers e logística\n');
    
    // Consulta de demonstração
    const consultaDemo = `Preciso consultar o status do meu CT-e número 351234567890123456789012345678901234. 
                         Onde posso encontrar informações sobre esta carga e qual o ETA previsto?
                         
                         Forneça uma resposta profissional e técnica, explicando:
                         1. Como consultar CT-e no sistema MIT Tracking
                         2. Tipos de informações disponíveis 
                         3. Como interpretar status de carga
                         4. Processo para obter ETA/ETD atualizados`;

    console.log('📋 Executando consulta de demonstração sobre CT-e...\n');
    
    const resposta = await agent.consultarLogistica(consultaDemo);
    
    console.log('🎯 Resposta do Assistente MIT Tracking:');
    console.log('='.repeat(50));
    console.log(resposta);
    console.log('='.repeat(50));
    
    console.log('\n✅ Demonstração concluída com sucesso!');
    console.log('🔄 O agente está pronto para consultas de CT-e, BL, containers e logística.');

    // Exemplo de consultas interativas
    console.log('\n📝 Exemplos de consultas que você pode fazer:');
    console.log('- "Onde está o meu BL?"');
    console.log('- "Me mostre o CT-e da carga X"');
    console.log('- "Qual o status da minha entrega?"');
    console.log('- "CT-e número [número específico]"');
    
  } catch (error) {
    console.error('❌ Erro ao executar o agente MIT Tracking:', error.message);
    console.error('📋 Detalhes do erro:', error.stack);
    
    if (error.message.includes('ECONNREFUSED') || error.message.includes('fetch')) {
      console.log('\n🔧 Possíveis soluções:');
      console.log('1. Verifique se o Ollama está rodando: ollama serve');
      console.log('2. Confirme se o modelo deepseek-r1:14b está disponível: ollama list');
      console.log('3. Teste a conexão: curl http://localhost:11434/api/tags');
    }
    
    process.exit(1);
  }
}

// Executa o programa
main();