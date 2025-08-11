"""
MIT Tracking Python Orchestrator
Migração da interface interativa TypeScript para Python
"""

import os
import sys
import asyncio
from datetime import datetime
from colorama import init, Fore, Back, Style

# Inicializa colorama para Windows/Linux
init(autoreset=True)

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.mit_tracking_agent import MITTrackingAgent
from models import LogisticsQuery, QueryType, OllamaConfig


class InteractiveInterface:
    """
    Interface interativa para o MIT Tracking Agent
    Equivalente ao InterfaceInterativa.ts
    """
    
    def __init__(self):
        self.agent: Optional[MITTrackingAgent] = None
        self.running = False
    
    async def initialize_agent(self) -> None:
        """Inicializa o agente MIT Tracking"""
        try:
            print(f"{Fore.YELLOW}🔄 Inicializando MIT Tracking Agent...{Style.RESET_ALL}")
            
            # Configuração do Ollama
            config = OllamaConfig(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
                model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
                temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
            )
            
            self.agent = MITTrackingAgent(config)
            
            print(f"{Fore.GREEN}✅ Agent inicializado com sucesso!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao inicializar agent: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Verifique se o Ollama está rodando em: {config.base_url}{Style.RESET_ALL}")
            sys.exit(1)
    
    def show_banner(self) -> None:
        """Mostra banner de boas-vindas"""
        print(f"\n{Back.BLUE}{Fore.WHITE}{'='*60}{Style.RESET_ALL}")
        print(f"{Back.BLUE}{Fore.WHITE}🤖 MIT TRACKING - ASSISTENTE LOGÍSTICO INTERATIVO{Style.RESET_ALL}")
        print(f"{Back.BLUE}{Fore.WHITE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📋 Comandos disponíveis:{Style.RESET_ALL}")
        print(f"  • Digite sua pergunta sobre logística")
        print(f"  • {Fore.YELLOW}/menu{Style.RESET_ALL} - Mostrar este menu")
        print(f"  • {Fore.YELLOW}/exemplos{Style.RESET_ALL} - Ver exemplos de consultas")
        print(f"  • {Fore.YELLOW}/stats{Style.RESET_ALL} - Mostrar estatísticas da sessão")
        print(f"  • {Fore.YELLOW}/limpar{Style.RESET_ALL} - Limpar histórico da conversa")
        print(f"  • {Fore.YELLOW}/reset{Style.RESET_ALL} - Resetar estado do agente")
        print(f"  • {Fore.YELLOW}/sair{Style.RESET_ALL} - Encerrar o programa")
        print(f"{Back.BLUE}{Fore.WHITE}{'='*60}{Style.RESET_ALL}")
    
    def show_examples(self) -> None:
        """Mostra exemplos de consultas"""
        print(f"\n{Fore.CYAN}📝 Exemplos de consultas logísticas:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}CT-e (Conhecimento de Transporte Eletrônico):{Style.RESET_ALL}")
        print(f"  • \"Onde está o CT-e número 35123456789012345678901234567890123456?\"")
        print(f"  • \"Qual o status do CT-e 35198765432109876543210987654321098765?\"")
        print(f"  • \"Me mostre as informações do CT-e da carga ABC123\"")
        
        print(f"\n{Fore.GREEN}Containers e Rastreamento:{Style.RESET_ALL}")
        print(f"  • \"Onde está o container ABCD1234567?\"")
        print(f"  • \"Qual o status do container XYZ9876543?\"")
        print(f"  • \"Quando chega o container CONT123456?\"")
        
        print(f"\n{Fore.GREEN}BL (Bill of Lading):{Style.RESET_ALL}")
        print(f"  • \"Onde está o meu BL número BL123456789?\"")
        print(f"  • \"Status do conhecimento de embarque marítimo XYZ123\"")
        
        print(f"\n{Fore.GREEN}ETA/ETD e Previsões:{Style.RESET_ALL}")
        print(f"  • \"Qual a previsão de chegada da carga ABC?\"")
        print(f"  • \"ETA do navio MSC MEDITERRANEAN\"")
        print(f"  • \"Quando sai o próximo navio para Santos?\"")
    
    def show_stats(self) -> None:
        """Mostra estatísticas da sessão"""
        if not self.agent:
            return
        
        stats = self.agent.get_stats()
        print(f"\n{Fore.CYAN}📊 Estatísticas da Sessão:{Style.RESET_ALL}")
        print(f"  • Session ID: {self.agent.get_session_id()}")
        print(f"  • Total de consultas: {stats.total_queries}")
        print(f"  • Consultas bem-sucedidas: {stats.successful_queries}")
        print(f"  • Erros: {stats.error_count}")
        print(f"  • Taxa de sucesso: {self.agent.success_rate:.1f}%")
        print(f"  • Tempo médio de resposta: {stats.average_response_time:.2f}s")
        print(f"  • Duração da sessão: {stats.session_duration/60:.2f} minutos")
        print(f"  • Mensagens no histórico: {self.agent.get_history_length()}")
        print(f"  • Estado do agent: {self.agent.get_state().value}")
    
    def detect_query_type(self, query: str) -> QueryType:
        """Detecta o tipo de consulta baseado no conteúdo"""
        query_lower = query.lower()
        
        if "ct-e" in query_lower or "cte" in query_lower or "conhecimento de transporte" in query_lower:
            return QueryType.CTE
        elif "container" in query_lower or "cont" in query_lower:
            return QueryType.CONTAINER
        elif "bl" in query_lower or "bill of lading" in query_lower or "conhecimento de embarque" in query_lower:
            return QueryType.BL
        elif "eta" in query_lower or "etd" in query_lower or "previsão" in query_lower or "chegada" in query_lower:
            return QueryType.ETA_ETD
        elif "status" in query_lower or "entrega" in query_lower or "tracking" in query_lower:
            return QueryType.DELIVERY_STATUS
        else:
            return QueryType.GENERAL
    
    async def process_user_input(self, user_input: str) -> bool:
        """
        Processa entrada do usuário
        Retorna False se deve sair, True para continuar
        """
        
        # Comandos especiais
        if user_input.startswith("/"):
            command = user_input.lower().strip()
            
            if command == "/menu":
                self.show_banner()
                return True
            elif command == "/exemplos":
                self.show_examples()
                return True
            elif command == "/stats":
                self.show_stats()
                return True
            elif command == "/limpar":
                self.agent.limpar_historico()
                return True
            elif command == "/reset":
                self.agent.reset_agent_state()
                return True
            elif command == "/sair":
                print(f"{Fore.YELLOW}👋 Encerrando sessão...{Style.RESET_ALL}")
                return False
            else:
                print(f"{Fore.RED}❌ Comando desconhecido: {command}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}💡 Digite /menu para ver comandos disponíveis{Style.RESET_ALL}")
                return True
        
        # Validar entrada
        validation = self.agent.validate_input(user_input)
        if not validation["is_valid"]:
            print(f"{Fore.RED}❌ {validation['error']}{Style.RESET_ALL}")
            return True
        
        # Processar consulta logística
        try:
            # Detectar tipo de consulta
            query_type = self.detect_query_type(user_input)
            
            # Criar query estruturada
            query = LogisticsQuery(
                content=user_input,
                query_type=query_type,
                session_id=self.agent.get_session_id()
            )
            
            # Processar consulta
            response = await self.agent.process_logistics_query(query)
            
            # Exibir resposta
            print(f"\n{Fore.GREEN}🤖 MIT Tracking:{Style.RESET_ALL}")
            print(f"{response.content}")
            
            # Mostrar metadados se verboso
            if os.getenv("CREW_VERBOSE", "").lower() == "true":
                print(f"\n{Fore.CYAN}📊 Metadados da resposta:{Style.RESET_ALL}")
                print(f"  • Tipo de consulta: {response.query_type.value if response.query_type else 'N/A'}")
                print(f"  • Confiança: {response.confidence:.2f}")
                print(f"  • Tempo de resposta: {response.response_time:.2f}s")
                print(f"  • Fontes: {', '.join(response.sources)}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao processar consulta: {str(e)}{Style.RESET_ALL}")
        
        return True
    
    async def run(self) -> None:
        """Loop principal da interface interativa"""
        await self.initialize_agent()
        
        self.show_banner()
        
        print(f"\n{Fore.GREEN}💬 Agente MIT Tracking pronto! Faça sua pergunta sobre logística:{Style.RESET_ALL}")
        
        self.running = True
        
        try:
            while self.running:
                # Prompt do usuário
                user_input = input(f"\n{Fore.BLUE}👤 Você: {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Processar entrada
                should_continue = await self.process_user_input(user_input)
                
                if not should_continue:
                    self.running = False
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚡ Interrompido pelo usuário{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}💥 Erro inesperado: {str(e)}{Style.RESET_ALL}")
        finally:
            if self.agent:
                await self.agent.shutdown()


async def main():
    """Função principal"""
    print(f"{Fore.CYAN}🚀 Iniciando MIT Tracking - Agente Conversacional Interativo...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🐍 Versão Python com CrewAI Integration{Style.RESET_ALL}\n")
    
    interface = InteractiveInterface()
    await interface.run()


if __name__ == "__main__":
    # Configura event loop para Windows se necessário
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Executa interface
    asyncio.run(main())