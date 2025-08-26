#!/usr/bin/env python3
"""
Script para corrigir os Links entre Orders e DocumentFiles

Problema identificado:
- Orders têm document_count correto mas document_files array vazio
- DocumentFiles existem e estão vinculados por order_id
- Faltam os Links do Beanie para populer o array document_files

Este script:
1. Encontra todas as Orders com document_count > 0 mas document_files vazio
2. Busca DocumentFiles vinculados por order_id
3. Cria os Links corretos usando Beanie
4. Atualiza as Orders com os Links
"""

import asyncio
import sys
import os
from typing import List

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Order, DocumentFile
from app.database import init_database
from beanie import Link
from datetime import datetime

class OrderDocumentLinksFixor:
    """Classe para corrigir links entre Orders e DocumentFiles"""
    
    def __init__(self):
        self.orders_fixed = 0
        self.links_created = 0
        self.errors = []
    
    async def analyze_current_state(self):
        """Analisa o estado atual do banco"""
        print("🔍 Analisando estado atual do banco...")
        
        # Contar Orders
        total_orders = await Order.count()
        orders_with_count = await Order.find(Order.document_count > 0).count()
        
        # Contar DocumentFiles
        total_docs = await DocumentFile.count()
        
        print(f"📊 Estado atual:")
        print(f"   • Total Orders: {total_orders}")
        print(f"   • Orders com document_count > 0: {orders_with_count}")
        print(f"   • Total DocumentFiles: {total_docs}")
        
        # Encontrar Orders com problema
        problematic_orders = []
        async for order in Order.find(Order.document_count > 0):
            if len(order.document_files) == 0:
                # Verificar se realmente existem documentos
                doc_count = await DocumentFile.find(DocumentFile.order_id == order.order_id).count()
                if doc_count > 0:
                    problematic_orders.append({
                        'order': order,
                        'expected_docs': order.document_count,
                        'actual_docs': doc_count
                    })
        
        print(f"\n🚨 Orders com problema encontradas: {len(problematic_orders)}")
        for item in problematic_orders[:5]:  # Mostrar apenas primeiras 5
            order = item['order']
            print(f"   • {order.order_id}: count={item['expected_docs']}, actual={item['actual_docs']}, links={len(order.document_files)}")
        
        if len(problematic_orders) > 5:
            print(f"   ... e mais {len(problematic_orders) - 5} orders")
            
        return problematic_orders
    
    async def fix_order_links(self, order: Order) -> int:
        """Corrige os links de uma Order específica"""
        try:
            # Buscar DocumentFiles vinculados
            documents = await DocumentFile.find(DocumentFile.order_id == order.order_id).to_list()
            
            if not documents:
                self.errors.append(f"Order {order.order_id}: Nenhum documento encontrado")
                return 0
            
            # Criar Links para cada documento
            new_links = []
            for doc in documents:
                # Criar Link usando o ObjectId do documento
                link = Link(doc.id, DocumentFile)
                new_links.append(link)
            
            # Atualizar a Order com os novos links
            order.document_files = new_links
            order.updated_at = datetime.utcnow()
            order.last_activity = datetime.utcnow()
            
            # Verificar se document_count está correto
            if order.document_count != len(documents):
                print(f"   ⚠️  Corrigindo document_count: {order.document_count} → {len(documents)}")
                order.document_count = len(documents)
            
            # Salvar no banco
            await order.save()
            
            print(f"   ✅ Order {order.order_id}: {len(new_links)} links criados")
            return len(new_links)
            
        except Exception as e:
            error_msg = f"Order {order.order_id}: Erro - {str(e)}"
            self.errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            return 0
    
    async def fix_all_orders(self):
        """Corrige todas as Orders com problema"""
        print("\n🔧 Iniciando correção dos links...")
        
        # Analisar estado atual
        problematic_orders = await self.analyze_current_state()
        
        if not problematic_orders:
            print("\n🎉 Nenhuma Order com problema encontrada!")
            return
        
        print(f"\n🚀 Corrigindo {len(problematic_orders)} Orders...")
        
        for i, item in enumerate(problematic_orders, 1):
            order = item['order']
            print(f"\n📝 [{i}/{len(problematic_orders)}] Processando Order: {order.title[:50]}...")
            print(f"   ID: {order.order_id}")
            print(f"   Cliente: {order.customer_name}")
            
            links_created = await self.fix_order_links(order)
            
            if links_created > 0:
                self.orders_fixed += 1
                self.links_created += links_created
        
        # Relatório final
        print(f"\n📊 Correção concluída:")
        print(f"   ✅ Orders corrigidas: {self.orders_fixed}")
        print(f"   🔗 Links criados: {self.links_created}")
        
        if self.errors:
            print(f"   ❌ Erros encontrados: {len(self.errors)}")
            for error in self.errors[:3]:  # Mostrar apenas primeiros 3 erros
                print(f"      • {error}")
    
    async def validate_fix(self):
        """Valida se a correção funcionou"""
        print("\n🧪 Validando correção...")
        
        # Verificar se ainda há Orders com problema
        remaining_problems = 0
        async for order in Order.find(Order.document_count > 0):
            if len(order.document_files) == 0:
                doc_count = await DocumentFile.find(DocumentFile.order_id == order.order_id).count()
                if doc_count > 0:
                    remaining_problems += 1
        
        if remaining_problems == 0:
            print("✅ Validação passou! Todas as Orders estão com links corretos.")
        else:
            print(f"❌ Ainda existem {remaining_problems} Orders com problemas.")
        
        # Testar algumas Orders aleatoriamente
        print("\n🔍 Testando algumas Orders aleatoriamente:")
        test_orders = await Order.find(Order.document_count > 0).limit(3).to_list()
        
        for order in test_orders:
            linked_docs = len(order.document_files)
            actual_docs = await DocumentFile.find(DocumentFile.order_id == order.order_id).count()
            
            status = "✅" if linked_docs == actual_docs else "❌"
            print(f"   {status} Order {order.order_id}: links={linked_docs}, actual={actual_docs}")

async def main():
    """Função principal"""
    print("🛠️  Iniciando correção dos Links entre Orders e DocumentFiles...\n")
    
    try:
        # Inicializar database
        await init_database()
        
        # Criar fixor e executar correção
        fixor = OrderDocumentLinksFixor()
        await fixor.fix_all_orders()
        
        # Validar correção
        await fixor.validate_fix()
        
        print("\n🎉 Script concluído com sucesso!")
        
        # Instruções para testar
        print("\n📋 Para testar a correção:")
        print("   1. Acesse: http://localhost:3000/documents")
        print("   2. Ou teste via API: curl 'http://localhost:8001/orders/' | python3 -m json.tool")
        print("   3. Verifique se document_files não está mais vazio")
        
    except Exception as e:
        print(f"❌ Erro fatal: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())