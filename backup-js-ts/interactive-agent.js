import { ChatOllama } from '@langchain/community/chat_models/ollama';
import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import readline from 'readline';
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

Sempre mantenha um tom profissional e técnico, fornecendo informações claras e objetivas sobre logística e transporte.
Responda sempre em português, de forma clara e concisa.`;

    this.conversationHistory = [
      new SystemMessage(this.systemPrompt)
    ];
  }

  async consultarLogistica(consulta) {
    try {
      console.log('\n🔍 Processando sua consulta...');
      
      // Adiciona a nova pergunta ao histórico
      this.conversationHistory.push(new HumanMessage(consulta));

      const response = await this.llm.invoke(this.conversationHistory);
      
      // Adiciona a resposta ao histórico para manter contexto
      this.conversationHistory.push(response);

      return response.content;
    } catch (error) {
      console.error('❌ Erro ao consultar:', error.message);
      return `Erro ao processar consulta: ${error.message}`;
    }
  }

  limparHistorico() {
    this.conversationHistory = [new SystemMessage(this.systemPrompt)];
    console.log('🧹 Histórico da conversa limpo!');
  }
}

class InterfaceInterativa {
  constructor() {
    this.agent = new MITTrackingAgent();
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  mostrarMenu() {
    console.log('\n' + '='.repeat(60));
    console.log('🤖 MIT TRACKING - ASSISTENTE LOGÍSTICO INTERATIVO');
    console.log('='.repeat(60));
    console.log('📋 Comandos disponíveis:');
    console.log('  • Digite sua pergunta sobre logística');
    console.log('  • /menu - Mostrar este menu');
    console.log('  • /exemplos - Ver exemplos de consultas');
    console.log('  • /limpar - Limpar histórico da conversa');
    console.log('  • /sair - Encerrar o programa');
    console.log('='.repeat(60));
  }

  mostrarExemplos() {
    console.log('\n📝 EXEMPLOS DE CONSULTAS:');
    console.log('─'.repeat(40));
    console.log('• "Onde está o meu BL?"');
    console.log('• "Me mostre o CT-e da carga X"');
    console.log('• "Qual o status da minha entrega?"');
    console.log('• "CT-e número 351234567890123456789012345678901234"');
    console.log('• "Como consultar ETA de um container?"');
    console.log('• "Quais documentos preciso para rastreamento?"');
    console.log('• "Como interpretar status de entrega atrasada?"');
    console.log('─'.repeat(40));
  }

  async iniciar() {
    console.log('🚀 Iniciando MIT Tracking - Agente Conversacional Interativo...\n');
    
    this.mostrarMenu();
    
    console.log('\n💬 Agente MIT Tracking pronto! Faça sua pergunta sobre logística:');

    await this.loopInterativo();
  }

  async loopInterativo() {
    return new Promise((resolve) => {
      const perguntar = () => {
        this.rl.question('\n👤 Você: ', async (input) => {
          const comando = input.trim().toLowerCase();

          // Verifica comandos especiais
          switch (comando) {
            case '/sair':
            case 'sair':
            case 'exit':
              console.log('\n👋 Encerrando MIT Tracking Agent. Até logo!');
              this.rl.close();
              resolve();
              return;

            case '/menu':
              this.mostrarMenu();
              perguntar();
              return;

            case '/exemplos':
              this.mostrarExemplos();
              perguntar();
              return;

            case '/limpar':
              this.agent.limparHistorico();
              perguntar();
              return;

            case '':
              console.log('❓ Por favor, digite uma pergunta ou comando.');
              perguntar();
              return;
          }

          // Processa consulta normal
          try {
            const resposta = await this.agent.consultarLogistica(input);
            console.log('\n🤖 MIT Tracking:', resposta);
          } catch (error) {
            console.error('\n❌ Erro:', error.message);
          }

          perguntar();
        });
      };

      perguntar();
    });
  }
}

// Tratamento para encerramento gracioso
process.on('SIGINT', () => {
  console.log('\n\n👋 Programa encerrado pelo usuário. Até logo!');
  process.exit(0);
});

async function main() {
  try {
    const interfaceChat = new InterfaceInterativa();
    await interfaceChat.iniciar();
  } catch (error) {
    console.error('❌ Erro ao executar o agente MIT Tracking:', error.message);
    
    if (error.message.includes('ECONNREFUSED') || error.message.includes('fetch')) {
      console.log('\n🔧 Possíveis soluções:');
      console.log('1. Verifique se o Ollama está rodando: ollama serve');
      console.log('2. Confirme se o modelo llama3.2:3b está disponível: ollama list');
      console.log('3. Teste a conexão: curl http://localhost:11434/api/tags');
    }
    
    process.exit(1);
  }
}

// Executa o programa
main();