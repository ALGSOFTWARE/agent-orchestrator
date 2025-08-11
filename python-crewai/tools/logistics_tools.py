"""
Ferramentas logísticas para MIT Tracking Agent
Integração entre Agent e banco de dados mockado
"""

from typing import Dict, Any, List
import json
from datetime import datetime

from database.db_manager import (
    get_database, 
    search_cte, 
    search_container, 
    search_bl,
    search_logistics_query
)


class LogisticsTools:
    """Conjunto de ferramentas para consultas logísticas"""
    
    def __init__(self):
        self.db = get_database()
    
    def consultar_cte(self, numero_cte: str) -> str:
        """
        Consulta informações de CT-e por número
        """
        try:
            resultados = search_cte(numero_cte)
            
            if not resultados:
                return f"❌ CT-e não encontrado: {numero_cte}\n\n💡 Verifique se o número está correto. Exemplo: 35240512345678901234567890123456789012"
            
            cte = resultados[0]  # Pega o primeiro resultado
            
            resposta = f"📋 **CT-e Encontrado**: {cte['numero_cte']}\n\n"
            resposta += f"**Status**: {cte['status']}\n"
            resposta += f"**Data Emissão**: {self._format_date(cte['data_emissao'])}\n"
            resposta += f"**Transportadora**: {cte['transportadora']['nome_fantasia']}\n"
            resposta += f"**Origem**: {cte['origem']['municipio']}/{cte['origem']['uf']}\n" 
            resposta += f"**Destino**: {cte['destino']['municipio']}/{cte['destino']['uf']}\n"
            resposta += f"**Peso**: {cte['peso_bruto']} kg\n"
            resposta += f"**Valor**: R$ {cte['valor_total']:,.2f}\n"
            
            if cte['containers']:
                resposta += f"**Containers**: {', '.join(cte['containers'])}\n"
            
            if cte.get('previsao_entrega'):
                resposta += f"**Previsão Entrega**: {self._format_date(cte['previsao_entrega'])}\n"
            
            if cte.get('data_entrega'):
                resposta += f"**Data Entrega**: {self._format_date(cte['data_entrega'])}\n"
            
            if cte.get('observacoes'):
                resposta += f"\n📝 **Observações**: {cte['observacoes']}"
                
            return resposta
            
        except Exception as e:
            return f"❌ Erro ao consultar CT-e: {str(e)}"
    
    def consultar_container(self, numero_container: str) -> str:
        """
        Consulta informações de container por número
        """
        try:
            resultados = search_container(numero_container)
            
            if not resultados:
                return f"❌ Container não encontrado: {numero_container}\n\n💡 Verifique se o número está correto. Exemplo: ABCD1234567"
            
            container = resultados[0]
            
            resposta = f"📦 **Container**: {container['numero_container']}\n\n"
            resposta += f"**Status**: {container['status']}\n"
            resposta += f"**Tipo**: {container['tipo_iso']} ({container['tipo']})\n"
            resposta += f"**Operador**: {container['operador']}\n"
            
            # Localização atual
            loc = container['localizacao_atual']
            resposta += f"**Localização Atual**: {loc['endereco']}\n"
            resposta += f"**Última Atualização**: {self._format_date(loc['data_ultima_atualizacao'])}\n"
            
            # Origem e destino
            resposta += f"**Origem**: {container['origem']['porto']}\n"
            resposta += f"**Destino**: {container['destino']['porto']}\n"
            
            if container['destino'].get('eta'):
                resposta += f"**ETA**: {self._format_date(container['destino']['eta'])}\n"
            
            # Carga
            carga = container['carga']
            resposta += f"**Carga**: {carga['tipo_mercadoria']}\n"
            resposta += f"**Peso Bruto**: {carga['peso_bruto']:,.1f} kg\n"
            resposta += f"**Valor**: R$ {carga['valor_mercadoria']:,.2f}\n"
            
            # Temperatura se for reefer
            if carga.get('temperatura'):
                resposta += f"**Temperatura**: {carga['temperatura']}°C\n"
            
            # Documentos associados
            docs = container['documentos']
            resposta += f"**BL**: {docs['bl_number']}\n"
            
            if docs.get('cte_associados'):
                resposta += f"**CT-e**: {', '.join(docs['cte_associados'])}\n"
            
            # Último evento
            if container.get('historico_movimentacao'):
                ultimo_evento = container['historico_movimentacao'][-1]
                resposta += f"\n📍 **Último Evento**: {ultimo_evento['evento']}\n"
                resposta += f"**Data**: {self._format_date(ultimo_evento['data'])}\n"
                if ultimo_evento.get('observacoes'):
                    resposta += f"**Obs**: {ultimo_evento['observacoes']}"
            
            return resposta
            
        except Exception as e:
            return f"❌ Erro ao consultar container: {str(e)}"
    
    def consultar_bl(self, numero_bl: str) -> str:
        """
        Consulta informações de BL por número
        """
        try:
            resultados = search_bl(numero_bl)
            
            if not resultados:
                return f"❌ BL não encontrado: {numero_bl}\n\n💡 Verifique se o número está correto. Exemplo: ABCD240001"
            
            bl = resultados[0]
            
            resposta = f"🚢 **Bill of Lading**: {bl['bl_number']}\n\n"
            resposta += f"**Status**: {bl['status']}\n"
            resposta += f"**Tipo**: {bl['tipo_bl']}\n"
            resposta += f"**Data Emissão**: {self._format_date(bl['data_emissao'])}\n"
            resposta += f"**Armador**: {bl['armador']['nome']}\n"
            
            # Shipper e Consignee
            resposta += f"**Embarcador**: {bl['shipper']['nome']}\n"
            resposta += f"**Destinatário**: {bl['consignee']['nome']}\n"
            
            # Portos
            resposta += f"**Porto Embarque**: {bl['porto_embarque']['nome']}\n"
            resposta += f"**Porto Descarga**: {bl['porto_descarga']['nome']}\n"
            
            # Navio (se houver)
            if bl.get('navio'):
                navio = bl['navio']
                resposta += f"**Navio**: {navio['nome']} (Viagem: {navio['viagem']})\n"
            
            # Containers
            if bl.get('containers'):
                containers_info = []
                for cont in bl['containers']:
                    info = f"{cont['numero']} ({cont['tipo']})"
                    if cont.get('temperatura'):
                        info += f" - Temp: {cont['temperatura']}°C"
                    containers_info.append(info)
                resposta += f"**Containers**: {', '.join(containers_info)}\n"
            
            # Mercadoria
            merc = bl['mercadoria']
            resposta += f"**Mercadoria**: {merc['descricao']}\n"
            resposta += f"**Peso Bruto**: {merc['peso_bruto']:,.1f} kg\n"
            resposta += f"**Volumes**: {merc['quantidade_volumes']}\n"
            
            # Frete
            frete = bl['frete']
            resposta += f"**Frete**: {frete['moeda']} {frete['valor']:,.2f} ({frete['tipo_pagamento']})\n"
            
            # Datas
            if bl.get('data_embarque'):
                resposta += f"**Data Embarque**: {self._format_date(bl['data_embarque'])}\n"
            
            if bl.get('eta_destino'):
                resposta += f"**ETA Destino**: {self._format_date(bl['eta_destino'])}\n"
            
            if bl.get('data_entrega'):
                resposta += f"**Data Entrega**: {self._format_date(bl['data_entrega'])}\n"
            
            if bl.get('observacoes'):
                resposta += f"\n📝 **Observações**: {bl['observacoes']}"
            
            return resposta
            
        except Exception as e:
            return f"❌ Erro ao consultar BL: {str(e)}"
    
    def busca_inteligente(self, consulta: str) -> str:
        """
        Busca inteligente em todas as coleções logísticas
        Função principal para queries gerais
        """
        try:
            resultados = search_logistics_query(consulta)
            
            resposta = f"🔍 **Resultados para**: '{consulta}'\n\n"
            total_encontrados = 0
            
            # CT-e
            if resultados['cte']:
                resposta += "📋 **CT-e Encontrados**:\n"
                for cte in resultados['cte'][:3]:  # Máximo 3
                    resposta += f"• {cte['numero_cte']} - {cte['status']} - {cte['transportadora']['nome_fantasia']}\n"
                    total_encontrados += 1
                resposta += "\n"
            
            # Containers
            if resultados['containers']:
                resposta += "📦 **Containers Encontrados**:\n"
                for cont in resultados['containers'][:3]:
                    resposta += f"• {cont['numero_container']} - {cont['status']} - {cont['operador']}\n"
                    total_encontrados += 1
                resposta += "\n"
            
            # BL
            if resultados['bl']:
                resposta += "🚢 **Bills of Lading Encontrados**:\n"
                for bl in resultados['bl'][:3]:
                    resposta += f"• {bl['bl_number']} - {bl['status']} - {bl['armador']['nome']}\n"
                    total_encontrados += 1
                resposta += "\n"
            
            # Viagens
            if resultados['viagens']:
                resposta += "🚛 **Viagens Encontradas**:\n"
                for viagem in resultados['viagens'][:3]:
                    resposta += f"• {viagem['codigo_viagem']} - {viagem['status']} - {viagem['tipo_transporte']}\n"
                    total_encontrados += 1
                resposta += "\n"
            
            # Transportadoras
            if resultados['transportadoras']:
                resposta += "🏢 **Transportadoras Encontradas**:\n"
                for transp in resultados['transportadoras'][:3]:
                    resposta += f"• {transp['nome_fantasia']} - {transp['razao_social']}\n"
                    total_encontrados += 1
                resposta += "\n"
            
            if total_encontrados == 0:
                resposta += "❌ Nenhum resultado encontrado.\n\n"
                resposta += "💡 **Dicas**:\n"
                resposta += "• Para CT-e: use números com 44 dígitos\n"
                resposta += "• Para Containers: use formato ABCD1234567\n"
                resposta += "• Para BL: use formato ABCD240001\n"
                resposta += "• Use termos como 'status', 'em trânsito', 'entregue'"
            else:
                resposta += f"📊 **Total encontrado**: {total_encontrados} resultados"
            
            return resposta
            
        except Exception as e:
            return f"❌ Erro na busca: {str(e)}"
    
    def obter_estatisticas(self) -> str:
        """
        Retorna estatísticas do banco de dados
        """
        try:
            stats = self.db.get_statistics()
            
            resposta = "📊 **Estatísticas do Sistema MIT Tracking**\n\n"
            
            for collection, info in stats.items():
                nome_colecao = {
                    'cte_documents': 'CT-e Documents',
                    'containers': 'Containers', 
                    'bl_documents': 'Bills of Lading',
                    'viagens': 'Viagens',
                    'transportadoras': 'Transportadoras',
                    'embarcadores': 'Embarcadores'
                }.get(collection, collection)
                
                resposta += f"**{nome_colecao}**: {info['total_documents']} registros\n"
            
            resposta += f"\n🕐 **Última atualização**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            
            return resposta
            
        except Exception as e:
            return f"❌ Erro ao obter estatísticas: {str(e)}"
    
    def _format_date(self, date_str: str) -> str:
        """Formata data ISO para formato brasileiro"""
        try:
            if not date_str:
                return "N/A"
            
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y %H:%M')
        except:
            return date_str


# Instância global das ferramentas
logistics_tools = LogisticsTools()


# Funções de conveniência para o Agent usar
def consultar_cte_tool(numero_cte: str) -> str:
    """Tool para consultar CT-e"""
    return logistics_tools.consultar_cte(numero_cte)


def consultar_container_tool(numero_container: str) -> str:
    """Tool para consultar Container"""
    return logistics_tools.consultar_container(numero_container)


def consultar_bl_tool(numero_bl: str) -> str:
    """Tool para consultar BL"""
    return logistics_tools.consultar_bl(numero_bl)


def busca_inteligente_tool(consulta: str) -> str:
    """Tool para busca inteligente"""
    return logistics_tools.busca_inteligente(consulta)


def estatisticas_tool() -> str:
    """Tool para obter estatísticas"""
    return logistics_tools.obter_estatisticas()