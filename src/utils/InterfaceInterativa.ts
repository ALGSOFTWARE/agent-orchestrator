import readline from 'readline';
import { EventEmitter } from 'events';
import { MITTrackingAgent } from '@/agents/MITTrackingAgent';
import type { CommandResult, InterfaceEvents } from '@/types';

export class InterfaceInterativa extends EventEmitter {
  private readonly agent: MITTrackingAgent;
  private readonly rl: readline.Interface;
  private isRunning: boolean = false;

  constructor() {
    super();
    this.agent = new MITTrackingAgent();
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  public processarComando(input: string): CommandResult {
    const comando = input.trim().toLowerCase();
    
    switch (comando) {
      case '/sair':
      case 'sair':
      case 'exit':
        return { tipo: 'sair', mensagem: '👋 Encerrando MIT Tracking Agent. Até logo!' };
      
      case '/menu':
        return { tipo: 'menu', mensagem: 'Menu de comandos exibido' };
      
      case '/exemplos':
        return { tipo: 'exemplos', mensagem: 'Exemplos de consultas exibidos' };
      
      case '/limpar':
        this.agent.limparHistorico();
        return { tipo: 'limpar', mensagem: '🧹 Histórico da conversa limpo!' };
      
      case '':
        return { tipo: 'vazio', mensagem: '❓ Por favor, digite uma pergunta ou comando.' };
      
      default:
        return { tipo: 'consulta', mensagem: 'Processando consulta normal' };
    }
  }

  public mostrarMenu(): string {
    return `
============================================================
🤖 MIT TRACKING - ASSISTENTE LOGÍSTICO INTERATIVO
============================================================
📋 Comandos disponíveis:
  • Digite sua pergunta sobre logística
  • /menu - Mostrar este menu
  • /exemplos - Ver exemplos de consultas
  • /limpar - Limpar histórico da conversa
  • /sair - Encerrar o programa
============================================================`;
  }

  public mostrarExemplos(): string {
    return `
📝 EXEMPLOS DE CONSULTAS:
─────────────────────────────────────────
• "Onde está o meu BL?"
• "Me mostre o CT-e da carga X"
• "Qual o status da minha entrega?"
• "CT-e número 351234567890123456789012345678901234"
• "Como consultar ETA de um container?"
• "Quais documentos preciso para rastreamento?"
• "Como interpretar status de entrega atrasada?"
─────────────────────────────────────────`;
  }

  public async iniciar(): Promise<void> {
    console.log('🚀 Iniciando MIT Tracking - Agente Conversacional Interativo...\n');
    
    this.mostrarMenuCompleto();
    
    console.log('\n💬 Agente MIT Tracking pronto! Faça sua pergunta sobre logística:');

    this.isRunning = true;
    await this.loopInterativo();
  }

  private mostrarMenuCompleto(): void {
    console.log(this.mostrarMenu());
  }

  private async loopInterativo(): Promise<void> {
    return new Promise((resolve) => {
      const perguntar = (): void => {
        if (!this.isRunning) {
          resolve();
          return;
        }

        this.rl.question('\n👤 Você: ', async (input: string) => {
          const resultado = this.processarComando(input);

          // Emite evento de comando processado
          this.emit('commandProcessed', resultado);

          // Verifica comandos especiais
          switch (resultado.tipo) {
            case 'sair':
              console.log(resultado.mensagem);
              await this.encerrar();
              resolve();
              return;

            case 'menu':
              console.log(this.mostrarMenu());
              perguntar();
              return;

            case 'exemplos':
              console.log(this.mostrarExemplos());
              perguntar();
              return;

            case 'limpar':
              console.log(resultado.mensagem);
              perguntar();
              return;

            case 'vazio':
              console.log(resultado.mensagem);
              perguntar();
              return;

            case 'consulta':
              await this.processarConsultaNormal(input);
              perguntar();
              return;
          }
        });
      };

      perguntar();
    });
  }

  private async processarConsultaNormal(input: string): Promise<void> {
    try {
      // Validação de entrada
      const validation = this.agent.validateInput(input);
      if (!validation.isValid) {
        console.log(`❌ ${validation.error}`);
        return;
      }

      if (!this.agent.isReady) {
        console.log('⏳ Agente está processando. Aguarde...');
        return;
      }

      const resposta = await this.agent.consultarLogistica(input);
      console.log('\n🤖 MIT Tracking:', resposta);
      
      // Emite evento de resposta processada
      this.emit('responseProcessed', { input, response: resposta });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      console.error('\n❌ Erro:', errorMessage);
      this.emit('error', error instanceof Error ? error : new Error(String(error)));
    }
  }

  private async encerrar(): Promise<void> {
    this.isRunning = false;
    
    // Mostra estatísticas da sessão
    const stats = this.agent.getStats();
    if (stats.totalQueries > 0) {
      console.log('\n📊 Estatísticas da sessão:');
      console.log(`   • Total de consultas: ${stats.totalQueries}`);
      console.log(`   • Taxa de sucesso: ${this.agent.successRate.toFixed(1)}%`);
      console.log(`   • Tempo médio de resposta: ${stats.averageResponseTime.toFixed(2)}ms`);
    }

    await this.agent.shutdown();
    this.rl.close();
    this.emit('exit');
  }

  // Método para obter estatísticas
  public getStats(): ReturnType<MITTrackingAgent['getStats']> {
    return this.agent.getStats();
  }

  // Método para verificar se está rodando
  public get running(): boolean {
    return this.isRunning;
  }

  // Método para forçar parada
  public async stop(): Promise<void> {
    if (this.isRunning) {
      await this.encerrar();
    }
  }

  // Método para obter informações da sessão
  public getSessionInfo(): {
    sessionId: string;
    isReady: boolean;
    historyLength: number;
    successRate: number;
  } {
    return {
      sessionId: this.agent.getSessionId(),
      isReady: this.agent.isReady,
      historyLength: this.agent.getHistoryLength(),
      successRate: this.agent.successRate
    };
  }

  // Método para processar comando programaticamente (útil para testes)
  public async executeCommand(command: string): Promise<string> {
    const resultado = this.processarComando(command);
    
    if (resultado.tipo === 'consulta') {
      try {
        return await this.agent.consultarLogistica(command);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
        return `Erro: ${errorMessage}`;
      }
    }
    
    return resultado.mensagem;
  }

  // Override do EventEmitter para tipagem
  public on<K extends keyof InterfaceEvents>(event: K, listener: InterfaceEvents[K]): this {
    return super.on(event, listener);
  }

  public emit<K extends keyof InterfaceEvents>(event: K, ...args: Parameters<InterfaceEvents[K]>): boolean {
    return super.emit(event, ...args);
  }
}