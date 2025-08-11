"""
Database Manager para MIT Tracking
Sistema de consulta aos dados mockados JSON (MongoDB-like)
"""

import json
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re
from pathlib import Path


class DatabaseManager:
    """
    Gerenciador de banco de dados mockado
    Simula operações MongoDB com arquivos JSON
    """
    
    def __init__(self, database_path: str = None):
        """Inicializa o gerenciador do banco de dados"""
        if database_path is None:
            self.db_path = Path(__file__).parent
        else:
            self.db_path = Path(database_path)
        
        # Cache das coleções para melhor performance
        self._collections_cache = {}
        self._load_collections()
    
    def _load_collections(self):
        """Carrega todas as coleções JSON em cache"""
        json_files = list(self.db_path.glob("*.json"))
        
        for json_file in json_files:
            collection_name = json_file.stem
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'documents' in data:
                        self._collections_cache[collection_name] = data['documents']
                        print(f"✅ Coleção '{collection_name}' carregada: {len(data['documents'])} documentos")
                    else:
                        print(f"⚠️  Arquivo {json_file} não possui estrutura 'documents'")
            except Exception as e:
                print(f"❌ Erro ao carregar {json_file}: {str(e)}")
    
    def get_collection(self, collection_name: str) -> List[Dict[str, Any]]:
        """Retorna todos os documentos de uma coleção"""
        return self._collections_cache.get(collection_name, [])
    
    def find_by_id(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Busca documento por ID"""
        collection = self.get_collection(collection_name)
        for doc in collection:
            if doc.get('_id') == doc_id:
                return doc
        return None
    
    def find_by_field(self, collection_name: str, field: str, value: Any) -> List[Dict[str, Any]]:
        """Busca documentos por campo específico"""
        collection = self.get_collection(collection_name)
        results = []
        
        for doc in collection:
            # Suporte a campos aninhados (ex: "transportadora.cnpj")
            field_value = self._get_nested_field(doc, field)
            if field_value == value:
                results.append(doc)
                
        return results
    
    def find_by_regex(self, collection_name: str, field: str, pattern: str) -> List[Dict[str, Any]]:
        """Busca documentos por regex em campo"""
        collection = self.get_collection(collection_name)
        results = []
        regex = re.compile(pattern, re.IGNORECASE)
        
        for doc in collection:
            field_value = self._get_nested_field(doc, field)
            if field_value and regex.search(str(field_value)):
                results.append(doc)
                
        return results
    
    def find_containers_by_number(self, container_number: str) -> List[Dict[str, Any]]:
        """Busca containers por número - função especializada"""
        # Busca exata
        exact_matches = self.find_by_field('containers', 'numero_container', container_number)
        
        # Busca parcial se não encontrar exato
        if not exact_matches:
            partial_matches = self.find_by_regex('containers', 'numero_container', container_number)
            return partial_matches
            
        return exact_matches
    
    def find_cte_by_number(self, cte_number: str) -> List[Dict[str, Any]]:
        """Busca CT-e por número - função especializada"""
        # Remove caracteres especiais do número
        clean_number = re.sub(r'[^\d]', '', cte_number)
        
        # Busca exata primeiro
        exact_matches = self.find_by_field('cte_documents', 'numero_cte', cte_number)
        
        if not exact_matches:
            # Busca por chave de acesso ou número limpo
            chave_matches = self.find_by_field('cte_documents', 'chave_acesso', clean_number)
            if chave_matches:
                return chave_matches
                
            # Busca parcial
            partial_matches = self.find_by_regex('cte_documents', 'numero_cte', clean_number[-10:])
            return partial_matches
            
        return exact_matches
    
    def find_bl_by_number(self, bl_number: str) -> List[Dict[str, Any]]:
        """Busca BL por número - função especializada"""
        return self.find_by_field('bl_documents', 'bl_number', bl_number)
    
    def find_by_status(self, collection_name: str, status: str) -> List[Dict[str, Any]]:
        """Busca documentos por status"""
        return self.find_by_field(collection_name, 'status', status)
    
    def find_by_transportadora(self, transportadora_name: str) -> List[Dict[str, Any]]:
        """Busca todos os documentos de uma transportadora"""
        results = []
        
        # Busca em CT-e
        cte_results = self.find_by_regex('cte_documents', 'transportadora.razao_social', transportadora_name)
        results.extend([{'tipo': 'CT-e', 'documento': doc} for doc in cte_results])
        
        # Busca em Containers
        container_results = self.find_by_regex('containers', 'operador', transportadora_name)
        results.extend([{'tipo': 'Container', 'documento': doc} for doc in container_results])
        
        # Busca em Viagens
        viagem_results = []
        for viagem in self.get_collection('viagens'):
            transp_id = viagem.get('transportadora_id')
            if transp_id:
                transp = self.find_by_id('transportadoras', transp_id)
                if transp and transportadora_name.lower() in transp.get('razao_social', '').lower():
                    viagem_results.append(viagem)
        
        results.extend([{'tipo': 'Viagem', 'documento': doc} for doc in viagem_results])
        
        return results
    
    def find_by_embarcador(self, embarcador_name: str) -> List[Dict[str, Any]]:
        """Busca todos os documentos de um embarcador"""
        results = []
        
        # Busca em CT-e
        cte_results = self.find_by_regex('cte_documents', 'embarcador.razao_social', embarcador_name)
        results.extend([{'tipo': 'CT-e', 'documento': doc} for doc in cte_results])
        
        return results
    
    def search_logistics(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Busca inteligente em todas as coleções logísticas
        Função principal para consultas do MIT Tracking Agent
        """
        query_lower = query.lower()
        results = {
            'cte': [],
            'containers': [],
            'bl': [],
            'viagens': [],
            'transportadoras': [],
            'embarcadores': []
        }
        
        # Detectar tipos de consulta
        if 'cte' in query_lower or 'ct-e' in query_lower or 'conhecimento' in query_lower:
            # Extrair possível número de CT-e
            cte_pattern = r'(\d{44}|\d{20,})'
            cte_matches = re.findall(cte_pattern, query)
            
            if cte_matches:
                for cte_num in cte_matches:
                    results['cte'].extend(self.find_cte_by_number(cte_num))
            else:
                # Busca geral em CT-e
                results['cte'] = self.get_collection('cte_documents')[:3]  # Limita a 3
        
        if 'container' in query_lower or 'cont' in query_lower:
            # Extrair possível número de container
            container_pattern = r'([A-Z]{4}\d{7})'
            container_matches = re.findall(container_pattern, query.upper())
            
            if container_matches:
                for cont_num in container_matches:
                    results['containers'].extend(self.find_containers_by_number(cont_num))
            else:
                # Busca por status ou geral
                if 'transito' in query_lower or 'em transito' in query_lower:
                    results['containers'] = self.find_by_status('containers', 'EM_TRANSITO')
                elif 'entregue' in query_lower:
                    results['containers'] = self.find_by_status('containers', 'ENTREGUE')
                else:
                    results['containers'] = self.get_collection('containers')[:3]
        
        if 'bl' in query_lower or 'bill of lading' in query_lower or 'conhecimento de embarque' in query_lower:
            # Extrair possível número de BL
            bl_pattern = r'([A-Z]{4}\d{6})'
            bl_matches = re.findall(bl_pattern, query.upper())
            
            if bl_matches:
                for bl_num in bl_matches:
                    results['bl'].extend(self.find_bl_by_number(bl_num))
            else:
                results['bl'] = self.get_collection('bl_documents')[:3]
        
        # Busca por transportadora
        transportadoras = ['rapido', 'logistica', 'maritima', 'aereo', 'ferroviaria']
        for transp in transportadoras:
            if transp in query_lower:
                results['transportadoras'] = self.find_by_regex('transportadoras', 'nome_fantasia', transp)
                break
        
        # Busca por status geral
        if 'status' in query_lower:
            results['viagens'] = self.get_collection('viagens')[:5]
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados"""
        stats = {}
        
        for collection_name, documents in self._collections_cache.items():
            stats[collection_name] = {
                'total_documents': len(documents),
                'sample_fields': list(documents[0].keys()) if documents else []
            }
        
        return stats
    
    def _get_nested_field(self, doc: Dict[str, Any], field_path: str) -> Any:
        """Obtém valor de campo aninhado (ex: 'transportadora.cnpj')"""
        fields = field_path.split('.')
        value = doc
        
        try:
            for field in fields:
                if isinstance(value, dict):
                    value = value.get(field)
                elif isinstance(value, list) and field.isdigit():
                    value = value[int(field)]
                else:
                    return None
            return value
        except (KeyError, IndexError, TypeError):
            return None


# Instância global do gerenciador
db_manager = DatabaseManager()


def get_database() -> DatabaseManager:
    """Retorna instância do gerenciador de banco"""
    return db_manager


# Funções de conveniência para o Agent
def search_cte(cte_number: str) -> List[Dict[str, Any]]:
    """Busca CT-e por número"""
    return db_manager.find_cte_by_number(cte_number)


def search_container(container_number: str) -> List[Dict[str, Any]]:
    """Busca container por número"""
    return db_manager.find_containers_by_number(container_number)


def search_bl(bl_number: str) -> List[Dict[str, Any]]:
    """Busca BL por número"""
    return db_manager.find_bl_by_number(bl_number)


def search_logistics_query(query: str) -> Dict[str, Any]:
    """Busca inteligente para queries do MIT Tracking Agent"""
    return db_manager.search_logistics(query)