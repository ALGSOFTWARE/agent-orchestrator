# Exemplos Práticos - Sistema Gatekeeper

## 📋 Índice

1. [Configuração Inicial](#configuração-inicial)
2. [Cenários de Uso das Ferramentas](#cenários-de-uso-das-ferramentas)
3. [Workflows Completos](#workflows-completos)
4. [Casos de Uso Avançados](#casos-de-uso-avançados)
5. [Integração Frontend](#integração-frontend)
6. [Scripts de Automação](#scripts-de-automação)
7. [Troubleshooting com Exemplos](#troubleshooting-com-exemplos)

---

## 🚀 Configuração Inicial

### 1. Setup Rápido para Desenvolvimento

```bash
#!/bin/bash
# quick-setup.sh

echo "🚀 Configuração Rápida do Sistema Gatekeeper"

# 1. Clonar e configurar repositório
git clone <repository-url> gatekeeper-system
cd gatekeeper-system/python-crewai

# 2. Criar ambiente virtual
python3.12 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cat > .env << EOF
# AI APIs
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-gemini-key-here

# Gatekeeper API
GATEKEEPER_API_URL=http://localhost:8001
WEBHOOK_PORT=8002

# OCR Configuration
TESSERACT_PATH=/usr/bin/tesseract
OCR_LANGUAGES=por,eng

# Logging
LOG_LEVEL=INFO
EOF

# 5. Testar instalação
python test_gatekeeper_integration.py

echo "✅ Setup concluído! Execute 'source venv/bin/activate' para ativar o ambiente."
```

### 2. Primeiro Teste das Ferramentas

```python
# test_tools_basic.py
"""
Teste básico das principais ferramentas do sistema
"""
import asyncio
from tools.gatekeeper_api_tool import CrewAIGatekeeperTool
from tools.document_processor import CrewAIDocumentTool
from tools.webhook_processor import CrewAIWebhookTool

async def teste_basico_ferramentas():
    """Teste básico de todas as ferramentas"""
    
    print("🧪 Testando ferramentas do Sistema Gatekeeper")
    print("=" * 50)
    
    # 1. Teste Gatekeeper API Tool
    print("1️⃣ Testando Gatekeeper API Tool...")
    api_tool = CrewAIGatekeeperTool()
    
    try:
        result = api_tool.verificar_saude_sistema()
        print(f"✅ API Tool: {result[:100]}...")
    except Exception as e:
        print(f"❌ API Tool: {e}")
    
    # 2. Teste Document Processor
    print("\n2️⃣ Testando Document Processor...")
    doc_tool = CrewAIDocumentTool()
    
    try:
        # Testar com arquivo inexistente (erro controlado)
        result = doc_tool.extrair_texto_simples("arquivo_inexistente.pdf")
        print(f"✅ Document Tool: {result[:100]}...")
    except Exception as e:
        print(f"❌ Document Tool: {e}")
    
    # 3. Teste Webhook Processor
    print("\n3️⃣ Testando Webhook Processor...")
    webhook_tool = CrewAIWebhookTool()
    
    try:
        stats = webhook_tool.get_webhook_stats()
        print(f"✅ Webhook Tool: {stats[:100]}...")
    except Exception as e:
        print(f"❌ Webhook Tool: {e}")
    
    print("\n🎉 Testes básicos concluídos!")

if __name__ == "__main__":
    asyncio.run(teste_basico_ferramentas())
```

---

## 🔧 Cenários de Uso das Ferramentas

### 1. Gatekeeper API Tool - Consultas Básicas

```python
# exemplos/api_tool_basico.py
"""
Exemplos básicos de uso da Gatekeeper API Tool
"""
from tools.gatekeeper_api_tool import CrewAIGatekeeperTool

def exemplo_consultas_basicas():
    """Demonstra consultas básicas na API"""
    
    tool = CrewAIGatekeeperTool()
    
    print("🔍 Exemplos de Consultas Básicas")
    print("=" * 40)
    
    # 1. Verificar saúde do sistema
    print("1. Verificando saúde do sistema:")
    saude = tool.verificar_saude_sistema()
    print(f"Status: {saude}\n")
    
    # 2. Buscar order específica
    print("2. Buscando order específica:")
    order = tool.consultar_order("ORDER123")
    print(f"Order: {order}\n")
    
    # 3. Listar orders recentes
    print("3. Listando orders recentes:")
    orders = tool.listar_orders(limit=5)
    print(f"Orders: {orders}\n")
    
    # 4. Consultar CT-e
    print("4. Consultando CT-e:")
    cte = tool.consultar_cte("12345678901234567890123456789012345678901234")
    print(f"CT-e: {cte}\n")
    
    # 5. Busca semântica
    print("5. Busca semântica:")
    resultados = tool.busca_semantica("containers com atraso na alfândega")
    print(f"Resultados: {resultados}\n")

if __name__ == "__main__":
    exemplo_consultas_basicas()
```

### 2. Document Processor - Processamento de Documentos

```python
# exemplos/document_processor_exemplos.py
"""
Exemplos de processamento de documentos
"""
from tools.document_processor import CrewAIDocumentTool
import os
from pathlib import Path

def criar_documento_teste():
    """Criar um documento de teste simples"""
    # Criar diretório de teste
    test_dir = Path("test_documents")
    test_dir.mkdir(exist_ok=True)
    
    # Criar arquivo de texto simples (simulando CT-e)
    cte_content = """
    CONHECIMENTO DE TRANSPORTE ELETRÔNICO - CT-e
    
    Número: 12345678901234567890123456789012345678901234
    CNPJ Emitente: 12.345.678/0001-90
    Data de Emissão: 15/08/2024
    
    DADOS DO REMETENTE:
    Nome: Empresa ABC Ltda
    CNPJ: 98.765.432/0001-10
    Endereço: Rua das Flores, 123, São Paulo/SP
    
    DADOS DO DESTINATÁRIO:
    Nome: Empresa XYZ S.A.
    CNPJ: 11.222.333/0001-44
    Endereço: Av. Principal, 456, Rio de Janeiro/RJ
    
    DADOS DA CARGA:
    Produto: Equipamentos Eletrônicos
    Peso: 1.250 kg
    Valor: R$ 25.000,00
    
    DADOS DO TRANSPORTE:
    Valor do Frete: R$ 1.250,00
    Data Prevista: 20/08/2024
    Modal: Rodoviário
    """
    
    test_file = test_dir / "cte_exemplo.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(cte_content)
    
    return str(test_file)

def exemplo_processamento_documentos():
    """Demonstra processamento de documentos"""
    
    tool = CrewAIDocumentTool()
    
    print("📄 Exemplos de Processamento de Documentos")
    print("=" * 50)
    
    # Criar documento de teste
    test_file = criar_documento_teste()
    print(f"✅ Documento de teste criado: {test_file}")
    
    # 1. Extração simples de texto
    print("\n1. Extração simples de texto:")
    texto = tool.extrair_texto_simples(test_file)
    print(f"Texto extraído:\n{texto}\n")
    
    # 2. Processamento completo com análise
    print("2. Processamento completo com análise:")
    analise = tool.processar_documento(test_file)
    print(f"Análise completa:\n{analise}\n")
    
    # 3. Testando com arquivo inexistente
    print("3. Testando tratamento de erro:")
    erro = tool.extrair_texto_simples("arquivo_inexistente.pdf")
    print(f"Resposta de erro:\n{erro}\n")
    
    # Cleanup
    os.remove(test_file)
    os.rmdir("test_documents")
    print("🧹 Arquivos de teste removidos")

if __name__ == "__main__":
    exemplo_processamento_documentos()
```

### 3. Webhook Processor - Eventos em Tempo Real

```python
# exemplos/webhook_exemplos.py
"""
Exemplos de processamento de webhooks
"""
from tools.webhook_processor import CrewAIWebhookTool, WebhookProcessor
import asyncio
import aiohttp
import json

def exemplo_webhook_basico():
    """Exemplos básicos de webhook"""
    
    tool = CrewAIWebhookTool()
    
    print("🎣 Exemplos de Webhook Processing")
    print("=" * 40)
    
    # 1. Verificar status
    print("1. Status do webhook processor:")
    stats = tool.get_webhook_stats()
    print(f"Stats: {stats}\n")
    
    # 2. Listar eventos recentes (se houver)
    print("2. Eventos recentes:")
    events = tool.get_recent_events(limit=5)
    print(f"Eventos: {events}\n")

async def exemplo_webhook_servidor():
    """Exemplo de servidor webhook básico"""
    
    print("🚀 Iniciando servidor webhook de exemplo...")
    
    # Configurar webhook processor
    processor = WebhookProcessor(port=8003)  # Porta diferente para teste
    
    # Simulação de envio de webhook
    async def enviar_webhook_teste():
        await asyncio.sleep(2)  # Aguardar servidor iniciar
        
        webhook_data = {
            "event_type": "CONTAINER_UPDATE",
            "source": "CUSTOMS",
            "container_id": "TCLU1234567",
            "order_id": "ORDER123",
            "description": "Container liberado pela alfândega",
            "timestamp": "2024-08-23T10:30:00Z",
            "location": "Porto de Santos",
            "status": "RELEASED"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8003/webhook/customs",
                    json=webhook_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    print(f"✅ Webhook enviado: {response.status}")
                    print(f"Resposta: {await response.text()}")
        except Exception as e:
            print(f"❌ Erro ao enviar webhook: {e}")
    
    # Executar servidor e teste em paralelo
    try:
        # Iniciar tarefas
        server_task = asyncio.create_task(processor.start_server())
        webhook_task = asyncio.create_task(enviar_webhook_teste())
        
        # Aguardar webhook ser enviado
        await webhook_task
        
        # Aguardar um pouco mais para processar
        await asyncio.sleep(1)
        
        print("🛑 Parando servidor de teste...")
        server_task.cancel()
        
    except asyncio.CancelledError:
        print("✅ Servidor webhook parado")
    except Exception as e:
        print(f"❌ Erro no servidor webhook: {e}")

if __name__ == "__main__":
    print("Escolha o exemplo:")
    print("1. Webhook básico (verificar status)")
    print("2. Servidor webhook com teste")
    
    escolha = input("Digite 1 ou 2: ")
    
    if escolha == "1":
        exemplo_webhook_basico()
    elif escolha == "2":
        asyncio.run(exemplo_webhook_servidor())
    else:
        print("Opção inválida")
```

---

## 🔄 Workflows Completos

### 1. Processamento Completo de CT-e

```python
# workflows/processamento_cte.py
"""
Workflow completo para processamento de CT-e
"""
import asyncio
from pathlib import Path
from datetime import datetime
from agents.specialized_agents import LogisticsAgent, FinanceAgent
from tools.document_processor import CrewAIDocumentTool
from tools.gatekeeper_api_tool import CrewAIGatekeeperTool

class ProcessadorCTe:
    """Processador completo de CT-e"""
    
    def __init__(self):
        self.doc_tool = CrewAIDocumentTool()
        self.api_tool = CrewAIGatekeeperTool()
        self.logistics_agent = LogisticsAgent()
        self.finance_agent = FinanceAgent()
    
    async def processar_cte_completo(self, arquivo_cte: str, order_id: str) -> dict:
        """
        Workflow completo:
        1. Extrair dados do CT-e via OCR
        2. Analisar com agente logístico  
        3. Calcular custos com agente financeiro
        4. Salvar dados na API
        5. Gerar relatório consolidado
        """
        
        resultado = {
            "order_id": order_id,
            "arquivo_processado": arquivo_cte,
            "timestamp_inicio": datetime.now().isoformat(),
            "etapas_concluidas": [],
            "dados_extraidos": None,
            "analise_logistica": None,
            "analise_financeira": None,
            "status_api": None,
            "relatorio": None,
            "erros": []
        }
        
        try:
            # Etapa 1: Extração de dados do documento
            print("📄 Etapa 1: Extraindo dados do CT-e...")
            analise_documento = self.doc_tool.processar_documento(arquivo_cte)
            resultado["dados_extraidos"] = analise_documento
            resultado["etapas_concluidas"].append("extracao_dados")
            print("✅ Dados extraídos com sucesso")
            
            # Etapa 2: Análise logística
            print("🚚 Etapa 2: Análise logística...")
            contexto_logistics = {
                "userId": "system",
                "role": "logistics", 
                "permissions": ["read:cte", "write:cte"]
            }
            
            requisicao_logistics = {
                "type": "cte_analysis",
                "message": f"Analisar CT-e para order {order_id}",
                "document_data": analise_documento,
                "order_id": order_id
            }
            
            analise_logistica = await self.logistics_agent.process_request(
                contexto_logistics, requisicao_logistics
            )
            resultado["analise_logistica"] = analise_logistica
            resultado["etapas_concluidas"].append("analise_logistica")
            print("✅ Análise logística concluída")
            
            # Etapa 3: Análise financeira
            print("💰 Etapa 3: Análise financeira...")
            contexto_finance = {
                "userId": "system",
                "role": "finance",
                "permissions": ["read:financial", "write:financial"]
            }
            
            requisicao_finance = {
                "type": "cost_analysis",
                "message": f"Calcular custos do CT-e para order {order_id}",
                "logistics_data": analise_logistica,
                "document_data": analise_documento,
                "order_id": order_id
            }
            
            analise_financeira = await self.finance_agent.process_request(
                contexto_finance, requisicao_finance
            )
            resultado["analise_financeira"] = analise_financeira
            resultado["etapas_concluidas"].append("analise_financeira")
            print("✅ Análise financeira concluída")
            
            # Etapa 4: Salvar na API
            print("💾 Etapa 4: Salvando dados na API...")
            try:
                # Verificar se order existe
                order_status = self.api_tool.consultar_order(order_id)
                resultado["status_api"] = order_status
                resultado["etapas_concluidas"].append("salvamento_api")
                print("✅ Dados verificados na API")
            except Exception as e:
                print(f"⚠️ Erro ao acessar API: {e}")
                resultado["erros"].append(f"api_error: {e}")
            
            # Etapa 5: Gerar relatório consolidado
            print("📊 Etapa 5: Gerando relatório...")
            relatorio = self.gerar_relatorio_consolidado(resultado)
            resultado["relatorio"] = relatorio
            resultado["etapas_concluidas"].append("relatorio")
            print("✅ Relatório gerado")
            
            resultado["timestamp_fim"] = datetime.now().isoformat()
            resultado["status"] = "sucesso"
            
        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
            resultado["erros"].append(f"processamento_error: {e}")
            resultado["status"] = "erro"
        
        return resultado
    
    def gerar_relatorio_consolidado(self, dados: dict) -> str:
        """Gerar relatório consolidado do processamento"""
        
        relatorio = f"""
# RELATÓRIO DE PROCESSAMENTO DE CT-e

## Informações Gerais
- Order ID: {dados['order_id']}
- Arquivo: {dados['arquivo_processado']}
- Data/Hora: {dados['timestamp_inicio']}
- Status: {dados.get('status', 'processando')}

## Etapas Concluídas
{chr(10).join([f'✅ {etapa}' for etapa in dados['etapas_concluidas']])}

## Dados Extraídos do Documento
{dados['dados_extraidos'][:300] if dados['dados_extraidos'] else 'Não disponível'}...

## Análise Logística
Status: {'✅ Concluída' if dados['analise_logistica'] else '❌ Pendente'}
{str(dados['analise_logistica'])[:200] if dados['analise_logistica'] else 'Não executada'}...

## Análise Financeira  
Status: {'✅ Concluída' if dados['analise_financeira'] else '❌ Pendente'}
{str(dados['analise_financeira'])[:200] if dados['analise_financeira'] else 'Não executada'}...

## Status da API
{dados['status_api'][:200] if dados['status_api'] else 'Não verificado'}...

## Erros Encontrados
{chr(10).join([f'❌ {erro}' for erro in dados['erros']]) if dados['erros'] else '✅ Nenhum erro'}

---
Relatório gerado automaticamente pelo Sistema Gatekeeper
        """
        
        return relatorio.strip()

# Exemplo de uso
async def exemplo_processamento_cte():
    """Exemplo de uso do processador de CT-e"""
    
    # Criar arquivo de teste
    test_file = Path("cte_teste.txt")
    cte_content = """
    CT-e: 12345678901234567890123456789012345678901234
    CNPJ: 12.345.678/0001-90
    Valor do Frete: R$ 1.250,00
    Peso: 2.500 kg
    """
    
    with open(test_file, "w") as f:
        f.write(cte_content)
    
    try:
        # Processar CT-e
        processador = ProcessadorCTe()
        resultado = await processador.processar_cte_completo(
            str(test_file), 
            "ORDER123"
        )
        
        print("\n" + "="*60)
        print("📋 RESULTADO DO PROCESSAMENTO")
        print("="*60)
        print(resultado["relatorio"])
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    asyncio.run(exemplo_processamento_cte())
```

### 2. Sistema de Monitoramento Contínuo

```python
# workflows/monitoramento_continuo.py
"""
Sistema de monitoramento contínuo com alertas
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List
from tools.gatekeeper_api_tool import CrewAIGatekeeperTool
from tools.webhook_processor import CrewAIWebhookTool

class MonitorContinuo:
    """Sistema de monitoramento contínuo"""
    
    def __init__(self):
        self.api_tool = CrewAIGatekeeperTool()
        self.webhook_tool = CrewAIWebhookTool()
        self.alertas_enviados = set()
        self.metricas_historicas = []
    
    async def executar_monitoramento(self, intervalo_segundos: int = 60):
        """Executar monitoramento contínuo"""
        
        print(f"🔄 Iniciando monitoramento contínuo (intervalo: {intervalo_segundos}s)")
        
        while True:
            try:
                # Coletar métricas atuais
                metricas = await self.coletar_metricas()
                
                # Analisar e gerar alertas
                alertas = self.analisar_metricas(metricas)
                
                # Processar alertas
                for alerta in alertas:
                    await self.processar_alerta(alerta)
                
                # Armazenar histórico
                self.metricas_historicas.append(metricas)
                
                # Manter apenas últimas 100 métricas
                if len(self.metricas_historicas) > 100:
                    self.metricas_historicas.pop(0)
                
                # Exibir status
                self.exibir_status_atual(metricas, alertas)
                
                # Aguardar próxima coleta
                await asyncio.sleep(intervalo_segundos)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                await asyncio.sleep(10)  # Aguardar antes de tentar novamente
    
    async def coletar_metricas(self) -> Dict:
        """Coletar métricas do sistema"""
        
        metricas = {
            "timestamp": datetime.now().isoformat(),
            "api_health": None,
            "webhook_stats": None,
            "orders_count": None,
            "response_time": None,
            "errors": []
        }
        
        # Health check da API
        try:
            start_time = datetime.now()
            health_result = self.api_tool.verificar_saude_sistema()
            end_time = datetime.now()
            
            metricas["api_health"] = "ok" if "erro" not in health_result.lower() else "error"
            metricas["response_time"] = (end_time - start_time).total_seconds() * 1000
            
        except Exception as e:
            metricas["api_health"] = "error"
            metricas["errors"].append(f"api_health: {e}")
        
        # Stats de webhook
        try:
            webhook_stats = self.webhook_tool.get_webhook_stats()
            metricas["webhook_stats"] = webhook_stats
            
        except Exception as e:
            metricas["errors"].append(f"webhook_stats: {e}")
        
        # Contar orders (simulado)
        try:
            orders_result = self.api_tool.listar_orders(limit=1)
            metricas["orders_count"] = "available" if orders_result else "empty"
            
        except Exception as e:
            metricas["errors"].append(f"orders_count: {e}")
        
        return metricas
    
    def analisar_metricas(self, metricas: Dict) -> List[Dict]:
        """Analisar métricas e gerar alertas"""
        
        alertas = []
        
        # Alerta de API não saudável
        if metricas["api_health"] == "error":
            alertas.append({
                "tipo": "api_down",
                "severidade": "critica",
                "mensagem": "API Gatekeeper não está respondendo",
                "timestamp": metricas["timestamp"]
            })
        
        # Alerta de tempo de resposta alto
        if metricas["response_time"] and metricas["response_time"] > 5000:  # 5 segundos
            alertas.append({
                "tipo": "slow_response",
                "severidade": "aviso",
                "mensagem": f"Tempo de resposta alto: {metricas['response_time']:.2f}ms",
                "timestamp": metricas["timestamp"]
            })
        
        # Alerta de muitos erros
        if len(metricas["errors"]) > 2:
            alertas.append({
                "tipo": "multiple_errors", 
                "severidade": "alta",
                "mensagem": f"Múltiplos erros detectados: {len(metricas['errors'])}",
                "timestamp": metricas["timestamp"]
            })
        
        # Análise de tendência (comparar com histórico)
        if len(self.metricas_historicas) > 5:
            alertas.extend(self.analisar_tendencias())
        
        return alertas
    
    def analisar_tendencias(self) -> List[Dict]:
        """Analisar tendências baseado no histórico"""
        
        alertas = []
        
        # Últimas 5 métricas
        ultimas_5 = self.metricas_historicas[-5:]
        
        # Contar quantas vezes a API teve problemas
        erros_api = sum(1 for m in ultimas_5 if m.get("api_health") == "error")
        
        if erros_api >= 3:
            alertas.append({
                "tipo": "api_instability",
                "severidade": "alta", 
                "mensagem": f"API instável: {erros_api}/5 falhas recentes",
                "timestamp": datetime.now().isoformat()
            })
        
        # Verificar degradação de performance
        tempos_resposta = [
            m.get("response_time", 0) 
            for m in ultimas_5 
            if m.get("response_time") is not None
        ]
        
        if len(tempos_resposta) >= 3:
            media_tempo = sum(tempos_resposta) / len(tempos_resposta)
            if media_tempo > 3000:  # 3 segundos
                alertas.append({
                    "tipo": "performance_degradation",
                    "severidade": "aviso",
                    "mensagem": f"Performance degradada: {media_tempo:.2f}ms média",
                    "timestamp": datetime.now().isoformat()
                })
        
        return alertas
    
    async def processar_alerta(self, alerta: Dict):
        """Processar e enviar alerta"""
        
        # Evitar spam de alertas iguais
        chave_alerta = f"{alerta['tipo']}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        if chave_alerta in self.alertas_enviados:
            return
        
        self.alertas_enviados.add(chave_alerta)
        
        # Determinar ação baseada na severidade
        if alerta["severidade"] == "critica":
            await self.enviar_alerta_critico(alerta)
        elif alerta["severidade"] == "alta":
            await self.enviar_alerta_alto(alerta)
        else:
            await self.enviar_alerta_aviso(alerta)
    
    async def enviar_alerta_critico(self, alerta: Dict):
        """Enviar alerta crítico"""
        print(f"🚨 ALERTA CRÍTICO: {alerta['mensagem']}")
        # Aqui você implementaria:
        # - Envio de email
        # - Notificação Slack
        # - SMS para equipe de plantão
        # - Webhook para sistema de alertas
    
    async def enviar_alerta_alto(self, alerta: Dict):
        """Enviar alerta de severidade alta"""
        print(f"⚠️ ALERTA ALTO: {alerta['mensagem']}")
        # Implementar notificações de alta prioridade
    
    async def enviar_alerta_aviso(self, alerta: Dict):
        """Enviar alerta de aviso"""
        print(f"ℹ️ AVISO: {alerta['mensagem']}")
        # Implementar notificações de baixa prioridade
    
    def exibir_status_atual(self, metricas: Dict, alertas: List[Dict]):
        """Exibir status atual do sistema"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Status da API
        api_status = "🟢" if metricas["api_health"] == "ok" else "🔴"
        
        # Tempo de resposta
        response_time = metricas.get("response_time", 0)
        time_status = "🟢" if response_time < 1000 else "🟡" if response_time < 3000 else "🔴"
        
        # Contagem de erros
        error_count = len(metricas.get("errors", []))
        error_status = "🟢" if error_count == 0 else "🟡" if error_count <= 2 else "🔴"
        
        # Alertas
        alert_count = len(alertas)
        alert_status = "🟢" if alert_count == 0 else "🟡" if alert_count <= 2 else "🔴"
        
        print(f"\r[{timestamp}] API: {api_status} | Tempo: {time_status} {response_time:.0f}ms | "
              f"Erros: {error_status} {error_count} | Alertas: {alert_status} {alert_count}", end="", flush=True)
    
    def gerar_relatorio_periodo(self, horas: int = 1) -> str:
        """Gerar relatório das últimas N horas"""
        
        agora = datetime.now()
        limite = agora - timedelta(hours=horas)
        
        # Filtrar métricas do período
        metricas_periodo = [
            m for m in self.metricas_historicas
            if datetime.fromisoformat(m["timestamp"]) >= limite
        ]
        
        if not metricas_periodo:
            return "Nenhuma métrica disponível para o período especificado"
        
        # Calcular estatísticas
        total_coletas = len(metricas_periodo)
        api_ok = sum(1 for m in metricas_periodo if m.get("api_health") == "ok")
        tempos_resposta = [m.get("response_time", 0) for m in metricas_periodo if m.get("response_time")]
        
        relatorio = f"""
# RELATÓRIO DE MONITORAMENTO - ÚLTIMAS {horas}h

## Resumo Geral
- Período: {limite.strftime('%H:%M:%S')} - {agora.strftime('%H:%M:%S')}
- Total de coletas: {total_coletas}
- API disponibilidade: {(api_ok/total_coletas)*100:.1f}%
- Tempo resposta médio: {sum(tempos_resposta)/len(tempos_resposta):.1f}ms
- Tempo resposta max: {max(tempos_resposta):.1f}ms

## Status Atual
- API: {'🟢 OK' if metricas_periodo[-1].get('api_health') == 'ok' else '🔴 ERROR'}
- Último erro: {metricas_periodo[-1].get('errors', ['Nenhum'])[-1] if metricas_periodo[-1].get('errors') else 'Nenhum'}

## Alertas Enviados
- Total de alertas únicos: {len(self.alertas_enviados)}

---
Relatório gerado em: {agora.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return relatorio.strip()

# Exemplo de uso
async def exemplo_monitoramento():
    """Exemplo de monitoramento contínuo"""
    
    monitor = MonitorContinuo()
    
    print("🔄 Iniciando monitoramento de exemplo...")
    print("Pressione Ctrl+C para parar")
    
    try:
        # Executar por alguns ciclos de teste
        for i in range(10):
            metricas = await monitor.coletar_metricas()
            alertas = monitor.analisar_metricas(metricas)
            
            for alerta in alertas:
                await monitor.processar_alerta(alerta)
            
            monitor.metricas_historicas.append(metricas)
            monitor.exibir_status_atual(metricas, alertas)
            
            await asyncio.sleep(5)  # 5 segundos entre coletas para teste
        
        print("\n\n📊 Gerando relatório final...")
        relatorio = monitor.gerar_relatorio_periodo(1)
        print(relatorio)
        
    except KeyboardInterrupt:
        print("\n✅ Monitoramento finalizado")

if __name__ == "__main__":
    asyncio.run(exemplo_monitoramento())
```

---

## 🎯 Casos de Uso Avançados

### 1. Análise Preditiva de Atrasos

```python
# casos_avancados/analise_preditiva.py
"""
Sistema de análise preditiva para identificar possíveis atrasos
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import json
from agents.specialized_agents import LogisticsAgent

class AnalisePreditiva:
    """Sistema de análise preditiva para logística"""
    
    def __init__(self):
        self.logistics_agent = LogisticsAgent()
        self.historico_eventos = []
        self.padroes_atraso = {
            "alfandega": {"probabilidade": 0.3, "tempo_medio_horas": 24},
            "clima": {"probabilidade": 0.15, "tempo_medio_horas": 6},
            "transito": {"probabilidade": 0.2, "tempo_medio_horas": 3},
            "documentacao": {"probabilidade": 0.1, "tempo_medio_horas": 12}
        }
    
    async def analisar_risco_atraso(self, order_id: str) -> Dict:
        """Analisar risco de atraso para uma order"""
        
        print(f"🔮 Analisando risco de atraso para Order: {order_id}")
        
        # Coletar dados da order
        dados_order = await self.coletar_dados_order(order_id)
        
        # Analisar fatores de risco
        fatores_risco = self.identificar_fatores_risco(dados_order)
        
        # Calcular probabilidade de atraso
        probabilidade_atraso = self.calcular_probabilidade_atraso(fatores_risco)
        
        # Estimar tempo de atraso potencial
        tempo_atraso_estimado = self.estimar_tempo_atraso(fatores_risco)
        
        # Gerar recomendações
        recomendacoes = self.gerar_recomendacoes(fatores_risco, probabilidade_atraso)
        
        resultado = {
            "order_id": order_id,
            "timestamp_analise": datetime.now().isoformat(),
            "probabilidade_atraso": probabilidade_atraso,
            "tempo_atraso_estimado_horas": tempo_atraso_estimado,
            "nivel_risco": self.classificar_nivel_risco(probabilidade_atraso),
            "fatores_risco": fatores_risco,
            "recomendacoes": recomendacoes,
            "dados_utilizados": dados_order
        }
        
        return resultado
    
    async def coletar_dados_order(self, order_id: str) -> Dict:
        """Coletar dados relevantes da order para análise"""
        
        # Simular coleta de dados (normalmente viria da API)
        dados_simulados = {
            "order_id": order_id,
            "origem": "São Paulo/SP",
            "destino": "Manaus/AM", 
            "modal": "rodoviario",
            "peso_kg": 2500,
            "valor_carga": 50000,
            "data_prevista": (datetime.now() + timedelta(days=5)).isoformat(),
            "rota": ["São Paulo", "Brasília", "Goiânia", "Cuiabá", "Porto Velho", "Manaus"],
            "status_atual": "em_transito",
            "documentacao": {
                "cte": "completo",
                "nfe": "completo", 
                "outros": "pendente"
            },
            "historico_transportadora": {
                "pontualidade": 0.85,
                "total_entregas": 150
            },
            "condicoes_especiais": ["carga_fragil", "temperatura_controlada"]
        }
        
        return dados_simulados
    
    def identificar_fatores_risco(self, dados: Dict) -> List[Dict]:
        """Identificar fatores de risco baseado nos dados"""
        
        fatores = []
        
        # Análise da rota
        rota = dados.get("rota", [])
        if "Manaus" in rota:
            fatores.append({
                "tipo": "rota_complexa",
                "descricao": "Destino na região Norte - maior complexidade logística",
                "impacto": 0.2,
                "categoria": "geografico"
            })
        
        # Análise de documentação
        doc = dados.get("documentacao", {})
        if "pendente" in doc.values():
            fatores.append({
                "tipo": "documentacao_pendente",
                "descricao": "Documentação incompleta pode causar retenções",
                "impacto": 0.15,
                "categoria": "documentacao"
            })
        
        # Análise do modal
        if dados.get("modal") == "rodoviario":
            fatores.append({
                "tipo": "modal_rodoviario",
                "descricao": "Modal rodoviário sujeito a condições de tráfego/clima",
                "impacto": 0.1,
                "categoria": "modal"
            })
        
        # Análise da transportadora
        hist = dados.get("historico_transportadora", {})
        pontualidade = hist.get("pontualidade", 1.0)
        if pontualidade < 0.9:
            fatores.append({
                "tipo": "historico_transportadora",
                "descricao": f"Transportadora com pontualidade de {pontualidade*100:.1f}%",
                "impacto": 0.3 * (1 - pontualidade),
                "categoria": "transportadora"
            })
        
        # Condições especiais
        condicoes = dados.get("condicoes_especiais", [])
        if "temperatura_controlada" in condicoes:
            fatores.append({
                "tipo": "carga_especial",
                "descricao": "Carga com temperatura controlada - maior complexidade",
                "impacto": 0.1,
                "categoria": "carga"
            })
        
        return fatores
    
    def calcular_probabilidade_atraso(self, fatores_risco: List[Dict]) -> float:
        """Calcular probabilidade total de atraso"""
        
        # Probabilidade base (histórica)
        prob_base = 0.1  # 10% base
        
        # Somar impactos dos fatores (não linear)
        impacto_total = sum(fator["impacto"] for fator in fatores_risco)
        
        # Fórmula ajustada para evitar probabilidades > 1
        probabilidade = prob_base + (impacto_total * 0.8)
        
        return min(probabilidade, 0.95)  # Máximo de 95%
    
    def estimar_tempo_atraso(self, fatores_risco: List[Dict]) -> int:
        """Estimar tempo de atraso em horas"""
        
        tempo_base = 2  # 2 horas base
        
        # Somar tempos baseados nos padrões conhecidos
        tempo_adicional = 0
        
        for fator in fatores_risco:
            categoria = fator.get("categoria", "outros")
            
            if categoria == "documentacao":
                tempo_adicional += 8
            elif categoria == "geografico":
                tempo_adicional += 12
            elif categoria == "transportadora":
                tempo_adicional += 6
            elif categoria == "modal":
                tempo_adicional += 3
            else:
                tempo_adicional += 2
        
        return tempo_base + tempo_adicional
    
    def classificar_nivel_risco(self, probabilidade: float) -> str:
        """Classificar nível de risco"""
        
        if probabilidade < 0.2:
            return "BAIXO"
        elif probabilidade < 0.4:
            return "MEDIO"
        elif probabilidade < 0.6:
            return "ALTO"
        else:
            return "CRITICO"
    
    def gerar_recomendacoes(self, fatores_risco: List[Dict], probabilidade: float) -> List[str]:
        """Gerar recomendações baseadas nos fatores de risco"""
        
        recomendacoes = []
        
        # Recomendações baseadas nos fatores
        categorias_encontradas = {fator["categoria"] for fator in fatores_risco}
        
        if "documentacao" in categorias_encontradas:
            recomendacoes.append("🔄 Acelerar regularização da documentação pendente")
            recomendacoes.append("📞 Contato proativo com órgãos competentes")
        
        if "transportadora" in categorias_encontradas:
            recomendacoes.append("📱 Intensificar monitoramento da transportadora")
            recomendacoes.append("🚛 Considerar transportadora alternativa para próximas cargas")
        
        if "geografico" in categorias_encontradas:
            recomendacoes.append("🗺️ Reavaliar rota considerando alternativas")
            recomendacoes.append("⏰ Ajustar expectativas de prazo com cliente")
        
        # Recomendações baseadas na probabilidade
        if probabilidade > 0.5:
            recomendacoes.append("🚨 Notificar cliente sobre possível atraso")
            recomendacoes.append("🔍 Implementar rastreamento intensivo")
            recomendacoes.append("📋 Preparar plano de contingência")
        
        if probabilidade > 0.7:
            recomendacoes.append("⚡ Ativar protocolo de urgência")
            recomendacoes.append("👥 Escalar para gestor sênior")
        
        return recomendacoes
    
    async def relatorio_analise_preditiva(self, orders: List[str]) -> str:
        """Gerar relatório de análise preditiva para múltiplas orders"""
        
        print(f"📊 Gerando relatório preditivo para {len(orders)} orders...")
        
        resultados = []
        for order_id in orders:
            resultado = await self.analisar_risco_atraso(order_id)
            resultados.append(resultado)
        
        # Estatísticas gerais
        total_orders = len(resultados)
        orders_alto_risco = sum(1 for r in resultados if r["nivel_risco"] in ["ALTO", "CRITICO"])
        prob_media = sum(r["probabilidade_atraso"] for r in resultados) / total_orders
        
        # Ordenar por risco
        resultados_ordenados = sorted(resultados, key=lambda x: x["probabilidade_atraso"], reverse=True)
        
        relatorio = f"""
# RELATÓRIO DE ANÁLISE PREDITIVA

## Resumo Executivo
- **Total de Orders Analisadas**: {total_orders}
- **Orders em Alto Risco**: {orders_alto_risco} ({orders_alto_risco/total_orders*100:.1f}%)
- **Probabilidade Média de Atraso**: {prob_media*100:.1f}%
- **Data da Análise**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Orders por Nível de Risco

### 🚨 RISCO CRÍTICO
{chr(10).join([f"- {r['order_id']}: {r['probabilidade_atraso']*100:.1f}% ({r['tempo_atraso_estimado_horas']}h estimado)" 
               for r in resultados_ordenados if r['nivel_risco'] == 'CRITICO'])}

### ⚠️ RISCO ALTO  
{chr(10).join([f"- {r['order_id']}: {r['probabilidade_atraso']*100:.1f}% ({r['tempo_atraso_estimado_horas']}h estimado)"
               for r in resultados_ordenados if r['nivel_risco'] == 'ALTO'])}

### 🟡 RISCO MÉDIO
{chr(10).join([f"- {r['order_id']}: {r['probabilidade_atraso']*100:.1f}%"
               for r in resultados_ordenados if r['nivel_risco'] == 'MEDIO'])}

## Principais Fatores de Risco Identificados
{self._gerar_resumo_fatores_risco(resultados)}

## Recomendações Prioritárias
{self._gerar_recomendacoes_prioritarias(resultados_ordenados[:3])}

---
*Relatório gerado automaticamente pelo Sistema de Análise Preditiva*
        """
        
        return relatorio.strip()
    
    def _gerar_resumo_fatores_risco(self, resultados: List[Dict]) -> str:
        """Gerar resumo dos fatores de risco mais comuns"""
        
        contador_fatores = {}
        
        for resultado in resultados:
            for fator in resultado["fatores_risco"]:
                tipo = fator["tipo"]
                contador_fatores[tipo] = contador_fatores.get(tipo, 0) + 1
        
        fatores_ordenados = sorted(contador_fatores.items(), key=lambda x: x[1], reverse=True)
        
        return "\n".join([
            f"- **{tipo}**: {count} orders ({count/len(resultados)*100:.1f}%)"
            for tipo, count in fatores_ordenados[:5]
        ])
    
    def _gerar_recomendacoes_prioritarias(self, top_orders: List[Dict]) -> str:
        """Gerar recomendações prioritárias para orders de maior risco"""
        
        recomendacoes_prioritarias = []
        
        for order in top_orders[:3]:  # Top 3 orders de risco
            recomendacoes_prioritarias.append(
                f"**{order['order_id']}** ({order['nivel_risco']}):\n" +
                "\n".join([f"  - {rec}" for rec in order["recomendacoes"][:3]])
            )
        
        return "\n\n".join(recomendacoes_prioritarias)

# Exemplo de uso
async def exemplo_analise_preditiva():
    """Exemplo de análise preditiva"""
    
    analisador = AnalisePreditiva()
    
    # Lista de orders para análise
    orders_teste = ["ORDER123", "ORDER456", "ORDER789", "ORDER101", "ORDER202"]
    
    print("🔮 Executando análise preditiva...")
    
    # Análise individual
    print("\n📋 Análise Individual:")
    resultado_individual = await analisador.analisar_risco_atraso("ORDER123")
    
    print(f"Order: {resultado_individual['order_id']}")
    print(f"Nível de Risco: {resultado_individual['nivel_risco']}")
    print(f"Probabilidade: {resultado_individual['probabilidade_atraso']*100:.1f}%")
    print(f"Tempo Estimado: {resultado_individual['tempo_atraso_estimado_horas']}h")
    print("Recomendações:")
    for rec in resultado_individual['recomendacoes']:
        print(f"  - {rec}")
    
    # Relatório consolidado
    print("\n📊 Relatório Consolidado:")
    relatorio = await analisador.relatorio_analise_preditiva(orders_teste)
    print(relatorio)

if __name__ == "__main__":
    asyncio.run(exemplo_analise_preditiva())
```

---

## 🌐 Integração Frontend

### 1. Cliente React para Agentes IA

```javascript
// frontend/hooks/useAgents.js
import { useState, useCallback } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export function useAgents() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const queryAgent = useCallback(async (agentType, query, context = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/agents/${agentType}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          query,
          context: {
            userId: context.userId || 'anonymous',
            role: context.role || 'user',
            permissions: context.permissions || [],
            ...context
          },
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;

    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const processDocument = useCallback(async (file, documentType = 'auto') => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);

      const response = await fetch(`${API_BASE_URL}/agents/document/process`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;

    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    queryAgent,
    processDocument,
    loading,
    error
  };
}
```

```javascript
// frontend/components/AgentChat.jsx
import React, { useState, useRef, useEffect } from 'react';
import { useAgents } from '../hooks/useAgents';

export function AgentChat({ agentType = 'logistics', userContext = {} }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const { queryAgent, loading, error } = useAgents();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await queryAgent(agentType, inputValue, userContext);
      
      const agentMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: response.message || response.response || 'Resposta processada com sucesso',
        timestamp: new Date(),
        agentType,
        metadata: response.metadata || {}
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Erro ao processar mensagem: ${err.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const getAgentDisplayName = () => {
    const names = {
      'logistics': '🚚 Agente Logística',
      'finance': '💰 Agente Financeiro',
      'admin': '⚙️ Agente Administrativo'
    };
    return names[agentType] || '🤖 Agente IA';
  };

  const formatMessage = (message) => {
    // Formatação básica de markdown
    return message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                 .replace(/\*(.*?)\*/g, '<em>$1</em>')
                 .replace(/\n/g, '<br>');
  };

  return (
    <div className="agent-chat">
      <div className="chat-header">
        <h3>{getAgentDisplayName()}</h3>
        <div className="status">
          {loading ? '⏳ Processando...' : '✅ Online'}
        </div>
      </div>

      <div className="messages-container">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              <div 
                className="text"
                dangerouslySetInnerHTML={{ 
                  __html: formatMessage(message.content) 
                }}
              />
              <div className="timestamp">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="message agent typing">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="input-form">
        <div className="input-group">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={`Pergunte algo para o ${getAgentDisplayName()}...`}
            disabled={loading}
            className="message-input"
          />
          <button 
            type="submit" 
            disabled={loading || !inputValue.trim()}
            className="send-button"
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          ⚠️ Erro: {error}
        </div>
      )}

      <style jsx>{`
        .agent-chat {
          display: flex;
          flex-direction: column;
          height: 500px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: white;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
        }

        .chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          border-bottom: 1px solid #eee;
          background: #f8f9fa;
          border-radius: 8px 8px 0 0;
        }

        .chat-header h3 {
          margin: 0;
          font-size: 14px;
          font-weight: 600;
        }

        .status {
          font-size: 12px;
          color: #666;
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          background: #fff;
        }

        .message {
          margin-bottom: 12px;
          display: flex;
        }

        .message.user {
          justify-content: flex-end;
        }

        .message.user .message-content {
          background: #007bff;
          color: white;
          border-radius: 16px 16px 4px 16px;
        }

        .message.agent .message-content {
          background: #f1f3f5;
          color: #333;
          border-radius: 16px 16px 16px 4px;
        }

        .message.error .message-content {
          background: #ffe6e6;
          color: #d32f2f;
          border-radius: 16px;
        }

        .message-content {
          max-width: 70%;
          padding: 8px 12px;
          position: relative;
        }

        .text {
          font-size: 14px;
          line-height: 1.4;
        }

        .timestamp {
          font-size: 10px;
          opacity: 0.7;
          margin-top: 4px;
        }

        .typing-indicator {
          display: flex;
          gap: 4px;
          align-items: center;
        }

        .typing-indicator span {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #999;
          animation: typing 1.4s infinite ease-in-out;
        }

        .typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
          }
          30% {
            transform: translateY(-10px);
          }
        }

        .input-form {
          border-top: 1px solid #eee;
          padding: 12px 16px;
        }

        .input-group {
          display: flex;
          gap: 8px;
        }

        .message-input {
          flex: 1;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 20px;
          outline: none;
          font-size: 14px;
        }

        .message-input:focus {
          border-color: #007bff;
        }

        .send-button {
          padding: 8px 16px;
          border: none;
          border-radius: 20px;
          background: #007bff;
          color: white;
          cursor: pointer;
          font-size: 14px;
        }

        .send-button:hover:not(:disabled) {
          background: #0056b3;
        }

        .send-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .error-message {
          padding: 8px 16px;
          background: #ffe6e6;
          color: #d32f2f;
          font-size: 12px;
          border-top: 1px solid #ffcdd2;
        }
      `}</style>
    </div>
  );
}
```

### 2. Componente de Upload de Documentos

```javascript
// frontend/components/DocumentUpload.jsx
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useAgents } from '../hooks/useAgents';

export function DocumentUpload({ onDocumentProcessed, acceptedTypes = 'pdf,jpg,jpeg,png' }) {
  const [uploadProgress, setUploadProgress] = useState({});
  const [processedDocuments, setProcessedDocuments] = useState([]);
  const { processDocument, loading, error } = useAgents();

  const onDrop = useCallback(async (acceptedFiles) => {
    for (const file of acceptedFiles) {
      const fileId = `${file.name}-${Date.now()}`;
      
      // Inicializar progresso
      setUploadProgress(prev => ({
        ...prev,
        [fileId]: { status: 'uploading', progress: 0 }
      }));

      try {
        // Simular progresso de upload
        for (let progress = 0; progress <= 100; progress += 20) {
          setUploadProgress(prev => ({
            ...prev,
            [fileId]: { status: 'uploading', progress }
          }));
          await new Promise(resolve => setTimeout(resolve, 200));
        }

        // Processar documento
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { status: 'processing', progress: 100 }
        }));

        const result = await processDocument(file, 'auto');

        // Sucesso
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { status: 'completed', progress: 100 }
        }));

        const processedDoc = {
          id: fileId,
          name: file.name,
          size: file.size,
          type: file.type,
          result: result,
          timestamp: new Date()
        };

        setProcessedDocuments(prev => [...prev, processedDoc]);
        
        if (onDocumentProcessed) {
          onDocumentProcessed(processedDoc);
        }

      } catch (err) {
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { 
            status: 'error', 
            progress: 100, 
            error: err.message 
          }
        }));
      }
    }
  }, [processDocument, onDocumentProcessed]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tif', '.tiff']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status) => {
    const icons = {
      uploading: '⏳',
      processing: '🔄',
      completed: '✅',
      error: '❌'
    };
    return icons[status] || '📄';
  };

  const removeDocument = (docId) => {
    setProcessedDocuments(prev => prev.filter(doc => doc.id !== docId));
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[docId];
      return newProgress;
    });
  };

  return (
    <div className="document-upload">
      <div 
        {...getRootProps()} 
        className={`dropzone ${isDragActive ? 'active' : ''} ${isDragReject ? 'reject' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <div className="upload-icon">📤</div>
          {isDragActive ? (
            <p>Solte os documentos aqui...</p>
          ) : (
            <>
              <p>Arraste documentos aqui ou <strong>clique para selecionar</strong></p>
              <p className="file-types">
                Suportados: PDF, JPG, PNG, TIFF (máx. 10MB cada)
              </p>
            </>
          )}
        </div>
      </div>

      {Object.keys(uploadProgress).length > 0 && (
        <div className="upload-progress">
          <h4>📋 Processando Documentos</h4>
          {Object.entries(uploadProgress).map(([fileId, progress]) => (
            <div key={fileId} className="progress-item">
              <div className="progress-header">
                <span className="status-icon">{getStatusIcon(progress.status)}</span>
                <span className="filename">{fileId.split('-')[0]}</span>
                <span className="status-text">
                  {progress.status === 'uploading' && 'Enviando...'}
                  {progress.status === 'processing' && 'Processando com IA...'}
                  {progress.status === 'completed' && 'Concluído'}
                  {progress.status === 'error' && 'Erro'}
                </span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${progress.progress}%` }}
                />
              </div>
              {progress.error && (
                <div className="error-text">{progress.error}</div>
              )}
            </div>
          ))}
        </div>
      )}

      {processedDocuments.length > 0 && (
        <div className="processed-documents">
          <h4>📄 Documentos Processados ({processedDocuments.length})</h4>
          {processedDocuments.map(doc => (
            <div key={doc.id} className="document-item">
              <div className="document-header">
                <div className="document-info">
                  <span className="document-icon">📄</span>
                  <div>
                    <div className="document-name">{doc.name}</div>
                    <div className="document-meta">
                      {formatFileSize(doc.size)} • {doc.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
                <button 
                  onClick={() => removeDocument(doc.id)}
                  className="remove-btn"
                  title="Remover documento"
                >
                  ❌
                </button>
              </div>
              
              <div className="document-result">
                <details>
                  <summary>Ver análise do documento</summary>
                  <div className="analysis-content">
                    <pre>{JSON.stringify(doc.result, null, 2)}</pre>
                  </div>
                </details>
              </div>
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        .document-upload {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
        }

        .dropzone {
          border: 2px dashed #ccc;
          border-radius: 8px;
          padding: 40px 20px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          background: #fafafa;
        }

        .dropzone:hover {
          border-color: #007bff;
          background: #f0f8ff;
        }

        .dropzone.active {
          border-color: #28a745;
          background: #f0fff0;
        }

        .dropzone.reject {
          border-color: #dc3545;
          background: #fff5f5;
        }

        .dropzone-content {
          pointer-events: none;
        }

        .upload-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        .dropzone p {
          margin: 8px 0;
          font-size: 16px;
          color: #666;
        }

        .file-types {
          font-size: 12px !important;
          color: #999 !important;
        }

        .upload-progress {
          margin-top: 20px;
          padding: 16px;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          background: white;
        }

        .upload-progress h4 {
          margin: 0 0 16px 0;
          font-size: 14px;
          font-weight: 600;
        }

        .progress-item {
          margin-bottom: 12px;
        }

        .progress-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 4px;
          font-size: 13px;
        }

        .filename {
          font-weight: 500;
          flex: 1;
          text-align: left;
        }

        .status-text {
          color: #666;
          font-size: 12px;
        }

        .progress-bar {
          height: 6px;
          background: #f0f0f0;
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: #007bff;
          transition: width 0.3s ease;
        }

        .error-text {
          font-size: 11px;
          color: #dc3545;
          margin-top: 4px;
        }

        .processed-documents {
          margin-top: 20px;
        }

        .processed-documents h4 {
          margin: 0 0 16px 0;
          font-size: 14px;
          font-weight: 600;
        }

        .document-item {
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          margin-bottom: 12px;
          background: white;
        }

        .document-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 16px;
        }

        .document-info {
          display: flex;
          align-items: center;
          gap: 12px;
          flex: 1;
        }

        .document-icon {
          font-size: 20px;
        }

        .document-name {
          font-weight: 500;
          font-size: 14px;
        }

        .document-meta {
          font-size: 11px;
          color: #666;
        }

        .remove-btn {
          border: none;
          background: none;
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          font-size: 12px;
        }

        .remove-btn:hover {
          background: #f5f5f5;
        }

        .document-result {
          border-top: 1px solid #f0f0f0;
          padding: 0 16px;
        }

        .document-result details {
          padding: 12px 0;
        }

        .document-result summary {
          cursor: pointer;
          font-size: 12px;
          color: #666;
          user-select: none;
        }

        .document-result summary:hover {
          color: #007bff;
        }

        .analysis-content {
          margin-top: 8px;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 4px;
          font-size: 10px;
          max-height: 200px;
          overflow-y: auto;
        }

        .analysis-content pre {
          margin: 0;
          white-space: pre-wrap;
          word-break: break-word;
        }
      `}</style>
    </div>
  );
}
```

---

## 🔧 Scripts de Automação

### 1. Script de Deploy Automatizado

```bash
#!/bin/bash
# scripts/deploy-automated.sh

set -e  # Sair se qualquer comando falhar

# Configurações
PROJECT_NAME="gatekeeper-system"
ENVIRONMENTS=("staging" "production")
BACKUP_RETENTION_DAYS=30
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
EMAIL_RECIPIENTS="${EMAIL_RECIPIENTS:-admin@company.com}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Função para enviar notificações
send_notification() {
    local message="$1"
    local status="$2"  # success, warning, error
    
    # Slack
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        local emoji
        case $status in
            success) emoji="✅" ;;
            warning) emoji="⚠️" ;;
            error) emoji="❌" ;;
            *) emoji="ℹ️" ;;
        esac
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"${emoji} ${PROJECT_NAME}: ${message}\"}" \
            "$SLACK_WEBHOOK_URL" &>/dev/null || true
    fi
    
    # Email (requires mailutils)
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "${PROJECT_NAME} Deploy Notification" "$EMAIL_RECIPIENTS" || true
    fi
}

# Função para verificar pré-requisitos
check_prerequisites() {
    log "Verificando pré-requisitos..."
    
    local missing_tools=()
    
    # Verificar ferramentas necessárias
    for tool in git docker docker-compose curl; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        error "Ferramentas faltando: ${missing_tools[*]}"
        exit 1
    fi
    
    # Verificar se está no diretório correto
    if [[ ! -f "docker-compose.yml" ]] && [[ ! -f "docker-compose.prod.yml" ]]; then
        error "Não foi encontrado docker-compose.yml no diretório atual"
        exit 1
    fi
    
    success "Pré-requisitos verificados"
}

# Função para executar testes
run_tests() {
    log "Executando testes..."
    
    # Testes do Python-CrewAI
    if [[ -d "python-crewai" ]]; then
        cd python-crewai
        if [[ -f "venv/bin/activate" ]]; then
            source venv/bin/activate
            
            # Executar testes de integração
            if python test_gatekeeper_integration.py; then
                success "Testes de integração passaram"
            else
                error "Testes de integração falharam"
                return 1
            fi
            
            # Executar testes unitários se existirem
            if [[ -d "tests" ]] && command -v pytest &> /dev/null; then
                if pytest tests/ -v; then
                    success "Testes unitários passaram"
                else
                    warning "Alguns testes unitários falharam"
                fi
            fi
        fi
        cd ..
    fi
    
    # Lint checks
    if command -v flake8 &> /dev/null; then
        log "Executando lint checks..."
        flake8 python-crewai/ --max-line-length=100 --statistics || warning "Lint checks com avisos"
    fi
    
    success "Testes concluídos"
}

# Função para fazer backup
create_backup() {
    local environment="$1"
    log "Criando backup para ambiente: $environment"
    
    local backup_dir="/backups/${PROJECT_NAME}/${environment}"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="backup_${timestamp}"
    
    mkdir -p "$backup_dir"
    
    # Backup do MongoDB (se estiver rodando)
    if docker ps | grep -q mongodb; then
        log "Fazendo backup do MongoDB..."
        docker exec -t $(docker ps -q -f name=mongodb) mongodump \
            --out "/tmp/${backup_name}" --gzip || warning "Backup MongoDB falhou"
        
        # Copiar backup para host
        docker cp $(docker ps -q -f name=mongodb):/tmp/${backup_name} \
            "${backup_dir}/${backup_name}_mongodb" || warning "Cópia do backup MongoDB falhou"
    fi
    
    # Backup de arquivos de configuração
    if [[ -d "configs" ]]; then
        tar -czf "${backup_dir}/${backup_name}_configs.tar.gz" configs/
    fi
    
    # Backup de uploads (se existir)
    if [[ -d "uploads" ]]; then
        tar -czf "${backup_dir}/${backup_name}_uploads.tar.gz" uploads/
    fi
    
    # Limpeza de backups antigos
    find "$backup_dir" -name "backup_*" -mtime +$BACKUP_RETENTION_DAYS -delete
    
    success "Backup criado: ${backup_name}"
    echo "$backup_name" > "/tmp/last_backup_${environment}"
}

# Função para fazer rollback
rollback_deployment() {
    local environment="$1"
    local backup_name="$2"
    
    error "Iniciando rollback para ambiente: $environment"
    
    if [[ -z "$backup_name" ]]; then
        if [[ -f "/tmp/last_backup_${environment}" ]]; then
            backup_name=$(cat "/tmp/last_backup_${environment}")
        else
            error "Nome do backup não especificado e nenhum backup recente encontrado"
            return 1
        fi
    fi
    
    log "Fazendo rollback usando backup: $backup_name"
    
    # Parar serviços
    docker-compose -f "docker-compose.${environment}.yml" down
    
    # Restaurar backup (implementar conforme necessário)
    # ... código de restauração ...
    
    # Reiniciar serviços
    docker-compose -f "docker-compose.${environment}.yml" up -d
    
    success "Rollback concluído"
    send_notification "Rollback realizado no ambiente $environment" "warning"
}

# Função para fazer deploy
deploy_environment() {
    local environment="$1"
    local skip_tests="$2"
    
    log "Iniciando deploy no ambiente: $environment"
    send_notification "Iniciando deploy no ambiente $environment" "info"
    
    # Verificar se arquivo de configuração existe
    local compose_file="docker-compose.${environment}.yml"
    if [[ ! -f "$compose_file" ]]; then
        error "Arquivo $compose_file não encontrado"
        return 1
    fi
    
    # Executar testes (se não for skip)
    if [[ "$skip_tests" != "true" ]]; then
        if ! run_tests; then
            error "Testes falharam - abortando deploy"
            send_notification "Deploy abortado - testes falharam no ambiente $environment" "error"
            return 1
        fi
    fi
    
    # Criar backup
    create_backup "$environment"
    local backup_name=$(cat "/tmp/last_backup_${environment}")
    
    # Pull das imagens
    log "Baixando imagens mais recentes..."
    if ! docker-compose -f "$compose_file" pull; then
        warning "Falha ao baixar algumas imagens"
    fi
    
    # Deploy
    log "Iniciando containers..."
    if ! docker-compose -f "$compose_file" up -d; then
        error "Falha no deploy"
        send_notification "Deploy falhou no ambiente $environment" "error"
        
        # Tentar rollback automático
        log "Tentando rollback automático..."
        if rollback_deployment "$environment" "$backup_name"; then
            send_notification "Rollback automático realizado no ambiente $environment" "warning"
        else
            send_notification "Rollback automático falhou no ambiente $environment - intervenção manual necessária" "error"
        fi
        return 1
    fi
    
    # Aguardar inicialização
    log "Aguardando inicialização dos serviços..."
    sleep 30
    
    # Health checks
    log "Verificando saúde dos serviços..."
    local health_check_passed=true
    
    # Verificar API
    for i in {1..10}; do
        if curl -f -s "http://localhost:8001/health" > /dev/null; then
            success "API está respondendo"
            break
        elif [[ $i -eq 10 ]]; then
            error "API não está respondendo após 10 tentativas"
            health_check_passed=false
        else
            log "Tentativa $i/10 - API ainda não está respondendo..."
            sleep 10
        fi
    done
    
    # Verificar outros serviços conforme necessário
    if docker ps | grep -q python-crewai; then
        # Verificar se o serviço de agentes está rodando
        if docker logs python-crewai 2>&1 | grep -q "started successfully\|ready\|listening"; then
            success "Serviço de agentes está rodando"
        else
            warning "Serviço de agentes pode não estar inicializado corretamente"
        fi
    fi
    
    if [[ "$health_check_passed" == "true" ]]; then
        success "Deploy concluído com sucesso no ambiente: $environment"
        send_notification "Deploy realizado com sucesso no ambiente $environment" "success"
        
        # Limpeza
        log "Limpando imagens não utilizadas..."
        docker system prune -f
        
        return 0
    else
        error "Health checks falharam"
        send_notification "Deploy realizado mas health checks falharam no ambiente $environment" "warning"
        
        # Decidir se faz rollback automático
        read -p "Health checks falharam. Fazer rollback? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback_deployment "$environment" "$backup_name"
        fi
        return 1
    fi
}

# Função para mostrar status dos serviços
show_status() {
    log "Status dos serviços:"
    
    echo -e "\n📊 Containers em execução:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n🏥 Health checks:"
    
    # API Health
    if curl -f -s "http://localhost:8001/health" > /dev/null; then
        echo "✅ API: OK"
    else
        echo "❌ API: Não respondendo"
    fi
    
    # MongoDB
    if docker ps | grep -q mongodb; then
        if docker exec -t $(docker ps -q -f name=mongodb) mongo --eval "db.adminCommand('ismaster')" &> /dev/null; then
            echo "✅ MongoDB: OK"
        else
            echo "❌ MongoDB: Problema de conexão"
        fi
    else
        echo "⚠️ MongoDB: Container não encontrado"
    fi
    
    echo -e "\n💾 Uso de recursos:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

# Função para mostrar logs
show_logs() {
    local service="$1"
    local lines="${2:-100}"
    
    if [[ -n "$service" ]]; then
        log "Mostrando logs do serviço: $service"
        docker logs --tail="$lines" "$service"
    else
        log "Mostrando logs de todos os serviços:"
        docker-compose logs --tail="$lines"
    fi
}

# Menu de ajuda
show_help() {
    cat << EOF
🚀 Script de Deploy Automatizado do $PROJECT_NAME

Uso: $0 [COMANDO] [OPÇÕES]

COMANDOS:
  deploy <env>     Deploy em ambiente específico (staging|production)
  rollback <env>   Rollback para backup mais recente
  status           Mostrar status dos serviços
  logs [service]   Mostrar logs (opcionalmente de serviço específico)
  test             Executar apenas os testes
  backup <env>     Criar backup manual
  help             Mostrar esta ajuda

OPÇÕES:
  --skip-tests     Pular execução de testes (usar com cuidado)
  --lines N        Número de linhas de log (padrão: 100)

EXEMPLOS:
  $0 deploy staging
  $0 deploy production --skip-tests
  $0 rollback production
  $0 logs gatekeeper-api
  $0 status

VARIÁVEIS DE AMBIENTE:
  SLACK_WEBHOOK_URL    URL do webhook Slack para notificações
  EMAIL_RECIPIENTS     Emails para notificações (separados por vírgula)

EOF
}

# Main
main() {
    local command="${1:-help}"
    local environment="$2"
    local skip_tests="false"
    local lines="100"
    
    # Processar argumentos
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-tests)
                skip_tests="true"
                shift
                ;;
            --lines)
                lines="$2"
                shift 2
                ;;
            *)
                if [[ -z "$environment" ]]; then
                    environment="$1"
                fi
                shift
                ;;
        esac
    done
    
    # Verificar pré-requisitos para comandos que precisam
    case $command in
        deploy|rollback|status|test|backup)
            check_prerequisites
            ;;
    esac
    
    case $command in
        deploy)
            if [[ -z "$environment" ]]; then
                error "Ambiente não especificado. Use: staging ou production"
                exit 1
            fi
            
            if [[ ! " ${ENVIRONMENTS[@]} " =~ " ${environment} " ]]; then
                error "Ambiente inválido: $environment. Use: ${ENVIRONMENTS[*]}"
                exit 1
            fi
            
            deploy_environment "$environment" "$skip_tests"
            ;;
        rollback)
            if [[ -z "$environment" ]]; then
                error "Ambiente não especificado"
                exit 1
            fi
            rollback_deployment "$environment"
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$environment" "$lines"
            ;;
        test)
            run_tests
            ;;
        backup)
            if [[ -z "$environment" ]]; then
                error "Ambiente não especificado"
                exit 1
            fi
            create_backup "$environment"
            ;;
        help)
            show_help
            ;;
        *)
            error "Comando inválido: $command"
            show_help
            exit 1
            ;;
    esac
}

# Trap para limpeza em caso de interrupção
trap 'error "Script interrompido"; exit 130' INT TERM

# Executar main
main "$@"
```

### 2. Script de Monitoramento e Alertas

```bash
#!/bin/bash
# scripts/monitoring-alerts.sh

set -e

# Configurações
MONITORING_INTERVAL=60  # segundos
API_ENDPOINT="http://localhost:8001"
WEBHOOK_ENDPOINT="http://localhost:8002"
ALERT_EMAIL="admin@company.com"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"
LOG_FILE="/var/log/gatekeeper-monitoring.log"

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90
RESPONSE_TIME_THRESHOLD=5000  # ms
ERROR_RATE_THRESHOLD=5        # %

# Estado anterior para evitar spam de alertas
LAST_ALERTS_FILE="/tmp/gatekeeper_last_alerts"
touch "$LAST_ALERTS_FILE"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error_log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# Função para enviar alertas
send_alert() {
    local title="$1"
    local message="$2"
    local severity="${3:-warning}"  # info, warning, critical
    local alert_key="$4"
    
    # Verificar se já enviou este alerta recentemente (últimas 2 horas)
    if [[ -n "$alert_key" ]]; then
        local last_sent=$(grep "^${alert_key}:" "$LAST_ALERTS_FILE" 2>/dev/null | cut -d: -f2)
        local current_time=$(date +%s)
        local two_hours_ago=$((current_time - 7200))
        
        if [[ -n "$last_sent" ]] && [[ "$last_sent" -gt "$two_hours_ago" ]]; then
            log "Alerta $alert_key já enviado recentemente, pulando..."
            return
        fi
        
        # Atualizar arquivo de últimos alertas
        grep -v "^${alert_key}:" "$LAST_ALERTS_FILE" > "${LAST_ALERTS_FILE}.tmp" 2>/dev/null || true
        echo "${alert_key}:${current_time}" >> "${LAST_ALERTS_FILE}.tmp"
        mv "${LAST_ALERTS_FILE}.tmp" "$LAST_ALERTS_FILE"
    fi
    
    local emoji
    case $severity in
        info) emoji="ℹ️" ;;
        warning) emoji="⚠️" ;;
        critical) emoji="🚨" ;;
        *) emoji="📢" ;;
    esac
    
    log "Enviando alerta: $title"
    
    # Slack
    if [[ -n "$SLACK_WEBHOOK" ]]; then
        local payload=$(cat << EOF
{
    "text": "${emoji} **${title}**",
    "attachments": [
        {
            "color": $(case $severity in info) echo "\"good\"";; warning) echo "\"warning\"";; critical) echo "\"danger\"";; *) echo "\"#764FA5\"";; esac),
            "fields": [
                {
                    "title": "Sistema",
                    "value": "Gatekeeper System",
                    "short": true
                },
                {
                    "title": "Severidade",
                    "value": "${severity^^}",
                    "short": true
                },
                {
                    "title": "Detalhes",
                    "value": "$message",
                    "short": false
                }
            ],
            "footer": "Gatekeeper Monitoring",
            "ts": $(date +%s)
        }
    ]
}
EOF
        )
        
        curl -X POST -H 'Content-type: application/json' \
             --data "$payload" \
             "$SLACK_WEBHOOK" &>/dev/null || error_log "Falha ao enviar Slack"
    fi
    
    # Email
    if command -v mail &> /dev/null && [[ -n "$ALERT_EMAIL" ]]; then
        echo -e "Alerta do Sistema Gatekeeper\n\n$title\n\n$message\n\nTimestamp: $(date)" | \
            mail -s "[$severity] Gatekeeper Alert: $title" "$ALERT_EMAIL" || \
            error_log "Falha ao enviar email"
    fi
}

# Verificar saúde da API
check_api_health() {
    local start_time=$(date +%s%3N)
    local http_code
    local response_time
    
    if http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$API_ENDPOINT/health"); then
        local end_time=$(date +%s%3N)
        response_time=$((end_time - start_time))
        
        if [[ "$http_code" == "200" ]]; then
            log "API Health: OK (${response_time}ms)"
            
            # Verificar tempo de resposta
            if [[ "$response_time" -gt "$RESPONSE_TIME_THRESHOLD" ]]; then
                send_alert "API Lenta" \
                          "Tempo de resposta da API: ${response_time}ms (threshold: ${RESPONSE_TIME_THRESHOLD}ms)" \
                          "warning" \
                          "api_slow_response"
            fi
        else
            send_alert "API Não Saudável" \
                      "API retornou código HTTP: $http_code" \
                      "critical" \
                      "api_unhealthy"
        fi
    else
        send_alert "API Não Responsiva" \
                  "API não está respondendo ou timeout" \
                  "critical" \
                  "api_down"
    fi
}

# Verificar uso de recursos dos containers
check_container_resources() {
    log "Verificando recursos dos containers..."
    
    # Obter estatísticas dos containers
    docker stats --no-stream --format "{{.Container}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.MemUsage}}" | \
    while IFS=$'\t' read -r container cpu_perc mem_perc mem_usage; do
        # Remover símbolo % e converter para número
        cpu_value=${cpu_perc%.*}
        cpu_value=${cpu_value%%.*}
        mem_value=${mem_perc%.*}
        mem_value=${mem_value%%.*}
        
        # Verificar CPU
        if [[ "$cpu_value" -gt "$CPU_THRESHOLD" ]]; then
            send_alert "Alto Uso de CPU" \
                      "Container $container usando ${cpu_perc} CPU (threshold: ${CPU_THRESHOLD}%)" \
                      "warning" \
                      "high_cpu_${container}"
        fi
        
        # Verificar Memória
        if [[ "$mem_value" -gt "$MEMORY_THRESHOLD" ]]; then
            send_alert "Alto Uso de Memória" \
                      "Container $container usando ${mem_perc} memória (${mem_usage}) (threshold: ${MEMORY_THRESHOLD}%)" \
                      "warning" \
                      "high_memory_${container}"
        fi
        
        log "Container $container: CPU=${cpu_perc} MEM=${mem_perc}"
    done
}

# Verificar espaço em disco
check_disk_space() {
    local disk_usage
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    log "Uso de disco: ${disk_usage}%"
    
    if [[ "$disk_usage" -gt "$DISK_THRESHOLD" ]]; then
        send_alert "Espaço em Disco Baixo" \
                  "Uso de disco: ${disk_usage}% (threshold: ${DISK_THRESHOLD}%)" \
                  "critical" \
                  "disk_space_low"
    fi
}

# Verificar status dos containers
check_container_status() {
    log "Verificando status dos containers..."
    
    local expected_containers=("gatekeeper-api" "python-crewai" "mongodb")
    
    for container in "${expected_containers[@]}"; do
        if ! docker ps --format "{{.Names}}" | grep -q "$container"; then
            send_alert "Container Parado" \
                      "Container $container não está rodando" \
                      "critical" \
                      "container_down_${container}"
        else
            # Verificar se container está saudável
            local status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unknown")
            if [[ "$status" == "unhealthy" ]]; then
                send_alert "Container Não Saudável" \
                          "Container $container está marcado como unhealthy" \
                          "critical" \
                          "container_unhealthy_${container}"
            fi
        fi
    done
}

# Verificar logs por erros
check_error_logs() {
    log "Verificando logs por erros recentes..."
    
    local containers=("gatekeeper-api" "python-crewai")
    local error_patterns=("ERROR" "CRITICAL" "FATAL" "Exception" "Traceback")
    
    for container in "${containers[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "$container"; then
            local recent_logs=$(docker logs --since=5m "$container" 2>&1)
            local error_count=0
            
            for pattern in "${error_patterns[@]}"; do
                local pattern_count=$(echo "$recent_logs" | grep -c "$pattern" || true)
                error_count=$((error_count + pattern_count))
            done
            
            if [[ "$error_count" -gt 10 ]]; then
                send_alert "Muitos Erros em Logs" \
                          "Container $container teve $error_count erros nos últimos 5 minutos" \
                          "warning" \
                          "high_error_rate_${container}"
            fi
            
            log "Container $container: $error_count erros recentes"
        fi
    done
}

# Verificar conectividade com banco
check_database_connectivity() {
    if docker ps --format "{{.Names}}" | grep -q mongodb; then
        if docker exec -t $(docker ps -q -f name=mongodb) mongo --eval "db.adminCommand('ismaster')" &>/dev/null; then
            log "Database: Conectividade OK"
        else
            send_alert "Problema de Conectividade com BD" \
                      "Não foi possível conectar ao MongoDB" \
                      "critical" \
                      "database_connectivity"
        fi
    else
        send_alert "Container MongoDB Não Encontrado" \
                  "Container do MongoDB não está rodando" \
                  "critical" \
                  "mongodb_missing"
    fi
}

# Verificar webhooks
check_webhook_service() {
    if curl -s --max-time 5 "$WEBHOOK_ENDPOINT/health" &>/dev/null; then
        log "Webhook Service: OK"
    else
        send_alert "Serviço de Webhook Não Responsivo" \
                  "Serviço de webhook não está respondendo" \
                  "warning" \
                  "webhook_service_down"
    fi
}

# Limpar alertas antigos
cleanup_old_alerts() {
    local current_time=$(date +%s)
    local one_day_ago=$((current_time - 86400))
    
    # Manter apenas alertas das últimas 24h
    awk -F: -v threshold="$one_day_ago" '$2 > threshold' "$LAST_ALERTS_FILE" > "${LAST_ALERTS_FILE}.tmp"
    mv "${LAST_ALERTS_FILE}.tmp" "$LAST_ALERTS_FILE"
}

# Função principal de monitoramento
run_monitoring_cycle() {
    log "Iniciando ciclo de monitoramento..."
    
    check_api_health
    check_container_resources
    check_disk_space
    check_container_status
    check_error_logs
    check_database_connectivity
    check_webhook_service
    cleanup_old_alerts
    
    log "Ciclo de monitoramento concluído"
    echo "---" >> "$LOG_FILE"
}

# Relatório de status
generate_status_report() {
    local report_file="/tmp/gatekeeper_status_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "RELATÓRIO DE STATUS DO SISTEMA GATEKEEPER"
        echo "=========================================="
        echo "Gerado em: $(date)"
        echo ""
        
        echo "CONTAINERS EM EXECUÇÃO:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        
        echo "USO DE RECURSOS:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
        echo ""
        
        echo "ESPAÇO EM DISCO:"
        df -h /
        echo ""
        
        echo "ÚLTIMOS ALERTAS (24h):"
        local current_time=$(date +%s)
        local one_day_ago=$((current_time - 86400))
        
        awk -F: -v threshold="$one_day_ago" '$2 > threshold {print $1, strftime("%Y-%m-%d %H:%M:%S", $2)}' "$LAST_ALERTS_FILE" | \
        while read -r alert_key timestamp_str; do
            echo "- $alert_key em $timestamp_str"
        done
        echo ""
        
        echo "LOGS RECENTES (últimas 50 linhas):"
        tail -50 "$LOG_FILE"
        
    } > "$report_file"
    
    echo "$report_file"
}

# Menu de ajuda
show_help() {
    cat << EOF
🔍 Script de Monitoramento e Alertas do Gatekeeper

Uso: $0 [COMANDO] [OPÇÕES]

COMANDOS:
  monitor          Executar monitoramento contínuo
  check            Executar uma verificação única
  report           Gerar relatório de status
  test-alerts      Testar sistema de alertas
  help             Mostrar esta ajuda

OPÇÕES:
  --interval N     Intervalo entre verificações em segundos (padrão: 60)
  --once           Executar apenas uma vez (não contínuo)

CONFIGURAÇÃO:
  Edite as variáveis no topo do script para ajustar:
  - Thresholds de alertas
  - Endpoints de monitoramento  
  - Destinatários de alertas

VARIÁVEIS DE AMBIENTE:
  SLACK_WEBHOOK_URL    URL do webhook Slack
  
EXEMPLOS:
  $0 monitor --interval 30
  $0 check
  $0 report
  $0 test-alerts

EOF
}

# Testar sistema de alertas
test_alerts() {
    log "Testando sistema de alertas..."
    
    send_alert "Teste de Alerta" \
              "Este é um teste do sistema de alertas do Gatekeeper" \
              "info" \
              "test_alert_$(date +%s)"
              
    log "Teste de alerta enviado"
}

# Main
main() {
    local command="${1:-monitor}"
    local interval="$MONITORING_INTERVAL"
    local run_once=false
    
    # Processar argumentos
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --interval)
                interval="$2"
                shift 2
                ;;
            --once)
                run_once=true
                shift
                ;;
            *)
                echo "Argumento desconhecido: $1"
                exit 1
                ;;
        esac
    done
    
    case $command in
        monitor)
            log "Iniciando monitoramento contínuo (intervalo: ${interval}s)"
            
            if [[ "$run_once" == "true" ]]; then
                run_monitoring_cycle
            else
                while true; do
                    run_monitoring_cycle
                    sleep "$interval"
                done
            fi
            ;;
        check)
            run_monitoring_cycle
            ;;
        report)
            local report_file
            report_file=$(generate_status_report)
            log "Relatório gerado: $report_file"
            cat "$report_file"
            ;;
        test-alerts)
            test_alerts
            ;;
        help)
            show_help
            ;;
        *)
            echo "Comando inválido: $command"
            show_help
            exit 1
            ;;
    esac
}

# Garantir que o arquivo de log existe e tem permissões adequadas
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

# Executar
main "$@"
```

---

## 🔧 Troubleshooting com Exemplos

### 1. Problemas Comuns e Soluções

```bash
#!/bin/bash
# troubleshooting/common-issues.sh

# Problema 1: Containers não inicializam
troubleshoot_containers() {
    echo "🔍 Diagnosticando problemas de containers..."
    
    # Verificar se Docker está rodando
    if ! docker info &> /dev/null; then
        echo "❌ Docker não está rodando"
        echo "Solução: sudo systemctl start docker"
        return 1
    fi
    
    # Verificar containers parados
    local stopped_containers
    stopped_containers=$(docker ps -a --filter "status=exited" --format "{{.Names}}")
    
    if [[ -n "$stopped_containers" ]]; then
        echo "⚠️ Containers parados encontrados:"
        echo "$stopped_containers"
        
        echo "📋 Logs dos containers parados:"
        for container in $stopped_containers; do
            echo "--- Logs do $container ---"
            docker logs --tail=20 "$container"
            echo ""
        done
        
        echo "💡 Possíveis soluções:"
        echo "1. docker-compose up -d --force-recreate"
        echo "2. docker-compose down && docker-compose up -d"
        echo "3. Verificar variáveis de ambiente no .env"
    fi
    
    # Verificar uso de portas
    echo "🔍 Verificando portas em uso:"
    netstat -tlnp | grep -E ':(8001|8002|27017)\s'
    
    echo "✅ Diagnóstico de containers concluído"
}

# Problema 2: API não responde
troubleshoot_api() {
    echo "🔍 Diagnosticando problemas da API..."
    
    # Testar conectividade
    if curl -f -s "http://localhost:8001/health" > /dev/null; then
        echo "✅ API está respondendo"
    else
        echo "❌ API não está respondendo"
        
        # Verificar se container está rodando
        if docker ps | grep -q gatekeeper-api; then
            echo "✅ Container da API está rodando"
            
            # Verificar logs
            echo "📋 Últimos logs da API:"
            docker logs --tail=20 gatekeeper-api
            
            # Verificar processo dentro do container
            echo "🔍 Processos no container:"
            docker exec gatekeeper-api ps aux
            
        else
            echo "❌ Container da API não está rodando"
            echo "💡 Tente: docker-compose up -d gatekeeper-api"
        fi
    fi
}

# Problema 3: Agentes não funcionam
troubleshoot_agents() {
    echo "🔍 Diagnosticando problemas dos agentes..."
    
    # Testar import dos módulos
    echo "📦 Testando imports dos agentes..."
    
    if docker exec python-crewai python -c "
from agents.specialized_agents import AdminAgent, LogisticsAgent, FinanceAgent
from tools.gatekeeper_api_tool import CrewAIGatekeeperTool
from tools.document_processor import CrewAIDocumentTool
print('✅ Todos os imports ok')
    " 2>/dev/null; then
        echo "✅ Imports dos agentes ok"
    else
        echo "❌ Problema nos imports dos agentes"
        
        echo "📋 Testando dependências:"
        docker exec python-crewai python -c "
import sys
modules = ['crewai', 'langchain_openai', 'aiohttp', 'PIL', 'PyPDF2']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        "
    fi
    
    # Testar variáveis de ambiente
    echo "🔍 Verificando variáveis de ambiente dos agentes:"
    docker exec python-crewai printenv | grep -E "(OPENAI|GOOGLE|GATEKEEPER)" || echo "⚠️ Variáveis de ambiente não encontradas"
    
    # Testar conectividade com API
    echo "🔗 Testando conectividade com Gatekeeper API:"
    if docker exec python-crewai python -c "
import requests
try:
    response = requests.get('http://gatekeeper-api:8001/health', timeout=5)
    print(f'✅ Conectividade OK: {response.status_code}')
except Exception as e:
    print(f'❌ Erro de conectividade: {e}')
    "; then
        echo "✅ Conectividade com API ok"
    else
        echo "❌ Problema de conectividade com API"
    fi
}

# Problema 4: MongoDB não conecta
troubleshoot_mongodb() {
    echo "🔍 Diagnosticando problemas do MongoDB..."
    
    if docker ps | grep -q mongodb; then
        echo "✅ Container MongoDB está rodando"
        
        # Testar conexão
        if docker exec -t $(docker ps -q -f name=mongodb) mongo --eval "db.adminCommand('ismaster')" &> /dev/null; then
            echo "✅ MongoDB está respondendo"
            
            # Verificar databases
            echo "📊 Databases disponíveis:"
            docker exec -t $(docker ps -q -f name=mongodb) mongo --eval "show dbs"
            
        else
            echo "❌ MongoDB não está respondendo"
            echo "📋 Logs do MongoDB:"
            docker logs --tail=20 $(docker ps -q -f name=mongodb)
        fi
    else
        echo "❌ Container MongoDB não está rodando"
        echo "💡 Tente: docker-compose up -d mongodb"
    fi
}

# Problema 5: OCR não funciona
troubleshoot_ocr() {
    echo "🔍 Diagnosticando problemas de OCR..."
    
    # Verificar se Tesseract está instalado
    if docker exec python-crewai which tesseract > /dev/null; then
        echo "✅ Tesseract encontrado"
        
        # Verificar versão
        echo "📋 Versão do Tesseract:"
        docker exec python-crewai tesseract --version
        
        # Verificar idiomas
        echo "🌍 Idiomas disponíveis:"
        docker exec python-crewai tesseract --list-langs
        
        # Testar OCR básico
        echo "🧪 Testando OCR básico..."
        docker exec python-crewai python -c "
import pytesseract
from PIL import Image
import numpy as np

# Criar imagem de teste
img = Image.fromarray(np.ones((100, 200, 3), dtype=np.uint8) * 255)
try:
    text = pytesseract.image_to_string(img)
    print('✅ OCR básico funcionando')
except Exception as e:
    print(f'❌ Erro no OCR: {e}')
    "
        
    else
        echo "❌ Tesseract não encontrado"
        echo "💡 Instale com: apt-get install tesseract-ocr tesseract-ocr-por"
    fi
}

# Função principal de diagnóstico
run_full_diagnostic() {
    echo "🩺 Executando diagnóstico completo do Sistema Gatekeeper"
    echo "=" * 60
    
    troubleshoot_containers
    echo ""
    troubleshoot_api
    echo ""
    troubleshoot_agents
    echo ""
    troubleshoot_mongodb
    echo ""
    troubleshoot_ocr
    
    echo ""
    echo "📋 Resumo do Diagnóstico:"
    echo "- Verifique os logs acima para problemas específicos"
    echo "- Use as soluções sugeridas para resolver problemas"
    echo "- Se problemas persistirem, consulte a documentação completa"
    
    echo ""
    echo "🔧 Comandos úteis para troubleshooting:"
    echo "docker-compose logs -f                    # Ver logs em tempo real"
    echo "docker-compose down && docker-compose up -d  # Reiniciar tudo"
    echo "docker system prune -f                   # Limpar recursos não usados"
    echo "docker exec -it <container> bash         # Entrar no container"
}

# Menu principal
case "${1:-full}" in
    containers)
        troubleshoot_containers
        ;;
    api)
        troubleshoot_api
        ;;
    agents)
        troubleshoot_agents
        ;;
    mongodb)
        troubleshoot_mongodb
        ;;
    ocr)
        troubleshoot_ocr
        ;;
    full)
        run_full_diagnostic
        ;;
    *)
        echo "Uso: $0 [containers|api|agents|mongodb|ocr|full]"
        echo "  containers - Diagnosticar problemas de containers"
        echo "  api        - Diagnosticar problemas da API"
        echo "  agents     - Diagnosticar problemas dos agentes"
        echo "  mongodb    - Diagnosticar problemas do MongoDB"
        echo "  ocr        - Diagnosticar problemas de OCR"
        echo "  full       - Executar diagnóstico completo"
        ;;
esac
```

---

## 📝 Conclusão dos Exemplos Práticos

Esta documentação fornece exemplos práticos abrangentes para o uso completo do Sistema Gatekeeper:

### ✅ O que foi coberto:

1. **Configuração Inicial**: Scripts de setup rápido e testes básicos
2. **Uso das Ferramentas**: Exemplos detalhados de cada ferramenta
3. **Workflows Completos**: Processamento de CT-e e monitoramento contínuo  
4. **Casos Avançados**: Análise preditiva de atrasos
5. **Integração Frontend**: Componentes React para chat e upload
6. **Scripts de Automação**: Deploy e monitoramento automatizado
7. **Troubleshooting**: Diagnóstico completo de problemas

### 🎯 Próximos Passos:

1. **Execute o setup rápido** para começar
2. **Teste as ferramentas básicas** com os exemplos fornecidos
3. **Implemente os workflows** conforme suas necessidades
4. **Configure monitoramento** para produção
5. **Use os scripts de troubleshooting** quando necessário

### 📞 Suporte:

- **Documentação Principal**: SISTEMA_GATEKEEPER.md
- **Guia DevOps**: DEVOPS_GUIDE.md  
- **Issues**: GitHub Issues do repositório
- **Comunidade**: Slack/Discord da equipe

Todos os exemplos são funcionais e podem ser adaptados para suas necessidades específicas. O sistema está pronto para uso em produção seguindo estes guias.

---

*Documentação de Exemplos Práticos - Versão 2.0.0*
*Última atualização: Agosto 2024*