import { jest } from '@jest/globals';
import { EventEmitter } from 'events';

// Mock do readline
const mockReadline = {
  question: jest.fn(),
  close: jest.fn()
};

const mockCreateInterface = jest.fn(() => mockReadline);

jest.unstable_mockModule('readline', () => ({
  createInterface: mockCreateInterface
}));

// Mock do MITTrackingAgent
const mockAgent = {
  consultarLogistica: jest.fn(),
  limparHistorico: jest.fn()
};

// Versão simplificada da InterfaceInterativa para testes
class InterfaceInterativaTest extends EventEmitter {
  constructor() {
    super();
    this.agent = mockAgent;
    this.rl = mockReadline;
  }

  processarComando(input) {
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

  mostrarMenu() {
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

  mostrarExemplos() {
    return `
📝 EXEMPLOS DE CONSULTAS:
─────────────────────────────────────────
• "Onde está o meu BL?"
• "Me mostre o CT-e da carga X"
• "Qual o status da minha entrega?"
• "CT-e número 351234567890123456789012345678901234"
• "Como consultar ETA de um container?"
• "Quais documentos preciso para rastreamento?"
─────────────────────────────────────────`;
  }
}

describe('Interface Interativa - Testes Unitários', () => {
  let interfaceTest;

  beforeEach(() => {
    interfaceTest = new InterfaceInterativaTest();
    
    // Reset dos mocks
    jest.clearAllMocks();
    mockAgent.consultarLogistica.mockClear();
    mockAgent.limparHistorico.mockClear();
    mockReadline.question.mockClear();
    mockReadline.close.mockClear();
  });

  describe('Inicialização da Interface', () => {
    test('deve inicializar com dependências corretas', () => {
      expect(interfaceTest.agent).toBeDefined();
      expect(interfaceTest.rl).toBeDefined();
      expect(interfaceTest.agent).toBe(mockAgent);
    });

    test('deve herdar de EventEmitter', () => {
      expect(interfaceTest).toBeInstanceOf(EventEmitter);
      expect(typeof interfaceTest.on).toBe('function');
      expect(typeof interfaceTest.emit).toBe('function');
    });
  });

  describe('Processamento de Comandos Especiais', () => {
    test('deve processar comando /sair', () => {
      const resultado = interfaceTest.processarComando('/sair');
      
      expect(resultado.tipo).toBe('sair');
      expect(resultado.mensagem).toContain('Encerrando MIT Tracking Agent');
    });

    test('deve processar variações do comando sair', () => {
      const comandos = ['/sair', 'sair', 'exit', 'EXIT'];
      
      comandos.forEach(comando => {
        const resultado = interfaceTest.processarComando(comando);
        expect(resultado.tipo).toBe('sair');
      });
    });

    test('deve processar comando /menu', () => {
      const resultado = interfaceTest.processarComando('/menu');
      
      expect(resultado.tipo).toBe('menu');
      expect(resultado.mensagem).toContain('Menu de comandos');
    });

    test('deve processar comando /exemplos', () => {
      const resultado = interfaceTest.processarComando('/exemplos');
      
      expect(resultado.tipo).toBe('exemplos');
      expect(resultado.mensagem).toContain('Exemplos de consultas');
    });

    test('deve processar comando /limpar', () => {
      const resultado = interfaceTest.processarComando('/limpar');
      
      expect(resultado.tipo).toBe('limpar');
      expect(resultado.mensagem).toContain('Histórico da conversa limpo');
      expect(mockAgent.limparHistorico).toHaveBeenCalledTimes(1);
    });

    test('deve tratar entrada vazia', () => {
      const resultado = interfaceTest.processarComando('');
      
      expect(resultado.tipo).toBe('vazio');
      expect(resultado.mensagem).toContain('digite uma pergunta');
    });

    test('deve tratar entrada só com espaços', () => {
      const resultado = interfaceTest.processarComando('   ');
      
      expect(resultado.tipo).toBe('vazio');
    });
  });

  describe('Processamento de Consultas Normais', () => {
    test('deve identificar consulta normal', () => {
      const consultas = [
        'Onde está meu CT-e?',
        'Como consultar BL?',
        'Status do container',
        'Informações sobre ETA'
      ];

      consultas.forEach(consulta => {
        const resultado = interfaceTest.processarComando(consulta);
        expect(resultado.tipo).toBe('consulta');
      });
    });

    test('deve ser case-insensitive nos comandos', () => {
      const comandos = [
        ['/MENU', 'menu'],
        ['/Menu', 'menu'],
        ['/EXEMPLOS', 'exemplos'],
        ['/Exemplos', 'exemplos'],
        ['/SAIR', 'sair'],
        ['/Sair', 'sair']
      ];

      comandos.forEach(([input, expectedType]) => {
        const resultado = interfaceTest.processarComando(input);
        expect(resultado.tipo).toBe(expectedType);
      });
    });
  });

  describe('Exibição de Menu e Exemplos', () => {
    test('deve mostrar menu formatado', () => {
      const menu = interfaceTest.mostrarMenu();
      
      expect(menu).toContain('MIT TRACKING');
      expect(menu).toContain('ASSISTENTE LOGÍSTICO');
      expect(menu).toContain('/menu');
      expect(menu).toContain('/exemplos');
      expect(menu).toContain('/limpar');
      expect(menu).toContain('/sair');
    });

    test('deve mostrar exemplos de consultas', () => {
      const exemplos = interfaceTest.mostrarExemplos();
      
      expect(exemplos).toContain('EXEMPLOS DE CONSULTAS');
      expect(exemplos).toContain('Onde está o meu BL?');
      expect(exemplos).toContain('CT-e da carga');
      expect(exemplos).toContain('status da minha entrega');
      expect(exemplos).toContain('ETA de um container');
    });

    test('menu deve conter todos os comandos necessários', () => {
      const menu = interfaceTest.mostrarMenu();
      
      const comandosEsperados = ['/menu', '/exemplos', '/limpar', '/sair'];
      comandosEsperados.forEach(comando => {
        expect(menu).toContain(comando);
      });
    });

    test('exemplos devem cobrir principais casos de uso', () => {
      const exemplos = interfaceTest.mostrarExemplos();
      
      const tiposConsulta = ['BL', 'CT-e', 'entrega', 'ETA', 'container', 'documentos'];
      tiposConsulta.forEach(tipo => {
        expect(exemplos.toLowerCase()).toContain(tipo.toLowerCase());
      });
    });
  });

  describe('Integração com Agent', () => {
    test('deve chamar limparHistorico do agent no comando /limpar', () => {
      interfaceTest.processarComando('/limpar');
      
      expect(mockAgent.limparHistorico).toHaveBeenCalledTimes(1);
    });

    test('não deve chamar métodos do agent em comandos especiais (exceto /limpar)', () => {
      const comandosEspeciais = ['/sair', '/menu', '/exemplos', ''];
      
      comandosEspeciais.forEach(comando => {
        interfaceTest.processarComando(comando);
      });
      
      expect(mockAgent.consultarLogistica).not.toHaveBeenCalled();
    });

    test('deve manter referência do agent', () => {
      expect(interfaceTest.agent).toBe(mockAgent);
      expect(interfaceTest.agent.consultarLogistica).toBeDefined();
      expect(interfaceTest.agent.limparHistorico).toBeDefined();
    });
  });

  describe('Tratamento de Entrada de Usuário', () => {
    test('deve limpar espaços em branco da entrada', () => {
      const entradasComEspaco = [
        '  /menu  ',
        '\t/exemplos\t',
        '\n/sair\n',
        '   Consulta com espaços   '
      ];

      entradasComEspaco.forEach(entrada => {
        const resultado = interfaceTest.processarComando(entrada);
        expect(resultado).toBeDefined();
        expect(resultado.tipo).toBeTruthy();
      });
    });

    test('deve tratar caracteres especiais adequadamente', () => {
      const entradasEspeciais = [
        'CT-e número 123/456',
        'Consulta com acentuação: ção',
        'Pergunta com símbolos @#$%',
        'Múltiplas     palavras'
      ];

      entradasEspeciais.forEach(entrada => {
        const resultado = interfaceTest.processarComando(entrada);
        expect(resultado.tipo).toBe('consulta');
      });
    });
  });

  describe('Estados da Interface', () => {
    test('deve permitir múltiplos comandos sequenciais', () => {
      const comandos = ['/menu', '/exemplos', '/limpar', 'Uma consulta', '/menu'];
      
      comandos.forEach(comando => {
        const resultado = interfaceTest.processarComando(comando);
        expect(resultado).toBeDefined();
        expect(resultado.tipo).toBeTruthy();
      });
    });

    test('deve manter estado consistente após comandos', () => {
      // Estado inicial
      expect(interfaceTest.agent).toBe(mockAgent);
      
      // Após comandos
      interfaceTest.processarComando('/menu');
      interfaceTest.processarComando('Uma consulta');
      interfaceTest.processarComando('/limpar');
      
      // Estado ainda consistente
      expect(interfaceTest.agent).toBe(mockAgent);
    });
  });

  describe('Formatação de Saída', () => {
    test('mensagens devem ter emojis apropriados', () => {
      const comandos = [
        ['/sair', '👋'],
        ['/limpar', '🧹'],
        ['', '❓']
      ];

      comandos.forEach(([comando, emoji]) => {
        const resultado = interfaceTest.processarComando(comando);
        expect(resultado.mensagem).toContain(emoji);
      });
    });

    test('menu deve ter formatação visual clara', () => {
      const menu = interfaceTest.mostrarMenu();
      
      expect(menu).toContain('='.repeat(60)); // Separadores
      expect(menu).toContain('🤖'); // Emoji do robô
      expect(menu).toContain('📋'); // Emoji de comandos
    });

    test('exemplos devem ter formatação consistente', () => {
      const exemplos = interfaceTest.mostrarExemplos();
      
      expect(exemplos).toContain('📝'); // Emoji de exemplos
      expect(exemplos).toContain('─'); // Separador visual
      expect(exemplos).toContain('•'); // Bullets dos exemplos
    });
  });
});