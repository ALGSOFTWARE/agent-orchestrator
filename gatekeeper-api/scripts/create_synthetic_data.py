#!/usr/bin/env python3
"""
Script para criar dados sintéticos para testar as visualizações
Cria Orders e DocumentFiles com embeddings sintéticos para demonstração
"""
import asyncio
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4
import os
from dotenv import load_dotenv

# Import dos modelos
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

from app.models import Order, DocumentFile, OrderType, OrderStatus, DocumentCategory, ProcessingStatus
from app.database import init_database

# Dados sintéticos para geração
CUSTOMER_NAMES = [
    "Transportes Silva Ltda",
    "Logística Moderna S/A", 
    "Comércio Internacional Souza",
    "Importadora Santos & Cia",
    "Exportadora do Porto Ltda",
    "Fretes Rápidos Express",
    "Carga Segura Transportes",
    "Logistics Pro Solutions",
    "Global Trade Partners",
    "Container Master Ltda"
]

ORIGINS = [
    "São Paulo, SP",
    "Santos, SP", 
    "Rio de Janeiro, RJ",
    "Porto Alegre, RS",
    "Recife, PE",
    "Manaus, AM",
    "Vitória, ES",
    "Salvador, BA"
]

DESTINATIONS = [
    "Miami, FL - USA",
    "Buenos Aires - Argentina",
    "Hamburg - Germany",
    "Tokyo - Japan",
    "Shanghai - China", 
    "Rotterdam - Netherlands",
    "Antwerp - Belgium",
    "New York, NY - USA"
]

DOCUMENT_CATEGORIES_DATA = {
    DocumentCategory.CTE: {
        "filenames": [
            "CTE_35210816907985000167550010000000271834567890.xml",
            "CTE_351208169079850001675500100000002718.pdf", 
            "Conhecimento_Transporte_SP_RJ_2024.pdf",
            "CTE_Minasul_Transporte_042024.xml"
        ],
        "text_samples": [
            "CONHECIMENTO DE TRANSPORTE ELETRÔNICO - CT-e Nº 000000027 Emitente: Transportes Silva Ltda CNPJ: 12.345.678/0001-90 Destinatário: Comércio Santos",
            "CT-e Número: 35210816907985000167550010000000271 Data de Emissão: 15/04/2024 Origem: São Paulo/SP Destino: Rio de Janeiro/RJ Valor: R$ 2.850,00",
            "Documento de transporte rodoviário emitido em conformidade com a legislação fiscal. Mercadoria: Produtos diversos. Peso: 15.500 kg"
        ]
    },
    DocumentCategory.BL: {
        "filenames": [
            "BL_MAEU_789456123_Hamburg_Santos.pdf",
            "Bill_of_Lading_MSC_container_MSKU9876543.pdf",
            "BL_CMA_CGM_2024_export_coffee.pdf",
            "Ocean_Bill_Hamburg_Sud_HASU4567890.pdf"
        ],
        "text_samples": [
            "BILL OF LADING No. MAEU789456123 Shipper: Global Export Ltda Consignee: European Import GmbH Port of Loading: Santos, Brazil Port of Discharge: Hamburg, Germany",
            "B/L Number: MSC4567891234 Vessel: MSC VIRTUOSA Voyage: 411W Container: MSKU9876543210 20'GP FCL/FCL Commodity: Coffee Beans 18,000 KG",
            "Ocean Bill of Lading issued by Hamburg Sud. Container HASUABCD123456 from Santos/BR to Antwerp/BE. Seal No: 456789. Total packages: 1200"
        ]
    },
    DocumentCategory.INVOICE: {
        "filenames": [
            "Commercial_Invoice_EXP_2024_001.pdf",
            "Fatura_Comercial_Exportacao_BR_DE_2024.pdf", 
            "Invoice_Coffee_Export_Hamburg_2024.pdf",
            "Nota_Fiscal_Exportacao_35240416.xml"
        ],
        "text_samples": [
            "COMMERCIAL INVOICE Invoice No: EXP-2024-001 Date: 20/04/2024 Exporter: Café Brasil Export Ltda Importer: German Coffee Import GmbH Total Value: USD 45,750.00",
            "FATURA COMERCIAL Número: 001/2024 Exportador: Santos Trading S/A Importador: European Partners Ltd Mercadoria: Produtos manufaturados Valor FOB: USD 28,900.00",
            "Commercial Invoice for export of Brazilian coffee beans. Quality: Santos Grade A. Bags: 300 x 60kg. Total weight: 18,000kg. Unit price: USD 2.54/kg"
        ]
    },
    DocumentCategory.PHOTO: {
        "filenames": [
            "container_loading_santos_20240415.jpg",
            "damage_assessment_container_MSKU123.jpg",
            "seal_verification_HABL456789.jpg",
            "cargo_inspection_port_santos.jpg"
        ],
        "text_samples": [
            "Fotografia do carregamento do container MSKU1234567890 no Porto de Santos. Data: 15/04/2024 14:30. Container em perfeitas condições.",
            "Inspeção visual da carga antes do embarque. Container 20'GP totalmente carregado com café em grãos. Lacre aplicado: 456789.",
            "Verificação do lacre do container após chegada no destino. Lacre íntegro número 456789. Container sem avarias externas."
        ]
    },
    DocumentCategory.EMAIL: {
        "filenames": [
            "email_shipping_instructions_20240415.eml",
            "correspondence_customs_clearance.msg",
            "booking_confirmation_maersk_line.eml", 
            "delivery_notification_hamburg.msg"
        ],
        "text_samples": [
            "From: logistics@silvatransportes.com Subject: Shipping Instructions - BL MAEU789456 Dear Customer, Please find attached the shipping instructions for your cargo...",
            "Subject: Customs Clearance Update - CT-e 000027 The customs clearance process has been completed successfully. Documents are available for pickup...",
            "Booking Confirmation MAEU Line - Booking No: 789456123 Vessel: MAERSK VALENCIA ETD: 20/04/2024 ETA: 05/05/2024 Equipment: 20'GP Container"
        ]
    },
    DocumentCategory.CONTRACT: {
        "filenames": [
            "contrato_transporte_silva_2024.pdf",
            "freight_agreement_global_logistics.pdf",
            "acordo_prestacao_servicos_log_2024.pdf",
            "international_shipping_contract.pdf"
        ],
        "text_samples": [
            "CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE TRANSPORTE Contratante: Comércio Internacional Santos Contratada: Silva Transportes Ltda Objeto: Transporte rodoviário...",
            "FREIGHT FORWARDING AGREEMENT Agreement No: FFA-2024-001 Client: Global Trade Partners Service Provider: Logistics Pro Solutions Term: 12 months",
            "Acordo de prestação de serviços logísticos internacionais. Partes: Exportadora do Porto Ltda e Container Master Ltda. Vigência: 01/01/2024 a 31/12/2024"
        ]
    }
}

def generate_embedding(text: str, dimension: int = 768) -> List[float]:
    """Gera embedding sintético baseado no texto (para demonstração)"""
    # Usar hash do texto como seed para gerar embedding consistente
    seed = hash(text) % (2**32)
    np.random.seed(seed)
    
    # Gerar embedding sintético
    embedding = np.random.normal(0, 1, dimension)
    
    # Normalizar para simular embeddings reais
    embedding = embedding / np.linalg.norm(embedding)
    
    return embedding.tolist()

async def create_orders_with_documents(num_orders: int = 10, docs_per_order_range: tuple = (3, 8)):
    """Cria Orders com DocumentFiles sintéticos"""
    
    print(f"🚀 Criando {num_orders} Orders com documentos sintéticos...")
    
    created_orders = []
    created_docs = []
    
    for i in range(num_orders):
        # Criar Order
        order = Order(
            title=f"Operação Logística {random.choice(['Import', 'Export'])} - {i+1:03d}",
            description=f"Operação de {random.choice(['importação', 'exportação'])} de mercadorias diversas",
            order_type=random.choice(list(OrderType)),
            status=random.choice(list(OrderStatus)),
            customer_name=random.choice(CUSTOMER_NAMES),
            customer_id=f"CUST_{random.randint(1000, 9999)}",
            origin=random.choice(ORIGINS),
            destination=random.choice(DESTINATIONS),
            estimated_value=random.uniform(10000, 150000),
            currency="USD" if random.random() > 0.3 else "BRL",
            priority=random.randint(1, 5),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
            expected_delivery=datetime.utcnow() + timedelta(days=random.randint(5, 45))
        )
        
        # Adicionar tags
        tags = random.sample([
            "urgente", "café", "containers", "importação", "exportação", 
            "europa", "ásia", "america", "rodoviário", "marítimo"
        ], k=random.randint(1, 3))
        order.tags = tags
        
        # Salvar Order
        await order.create()
        created_orders.append(order)
        
        # Criar DocumentFiles para esta Order
        num_docs = random.randint(*docs_per_order_range)
        
        for doc_idx in range(num_docs):
            # Escolher categoria aleatória
            category = random.choice(list(DocumentCategory))
            category_data = DOCUMENT_CATEGORIES_DATA.get(category, {
                "filenames": [f"document_{doc_idx}.pdf"],
                "text_samples": ["Generic document content"]
            })
            
            filename = random.choice(category_data["filenames"])
            text_content = random.choice(category_data["text_samples"])
            
            # Gerar embedding baseado no texto
            embedding = generate_embedding(text_content)
            
            doc = DocumentFile(
                original_name=filename,
                s3_key=f"synthetic/{order.order_id}/{filename}",
                s3_url=f"https://bucket.s3.amazonaws.com/synthetic/{order.order_id}/{filename}",
                file_type="application/pdf" if filename.endswith('.pdf') else "text/xml" if filename.endswith('.xml') else "message/rfc822",
                file_extension=filename.split('.')[-1],
                size_bytes=random.randint(50000, 2000000),
                category=category,
                order_id=order.order_id,
                processing_status=ProcessingStatus.INDEXED,
                text_content=text_content,
                embedding=embedding,
                embedding_model="text-embedding-3-small",  # Simular OpenAI
                indexed_at=datetime.utcnow(),
                uploaded_at=order.created_at + timedelta(minutes=random.randint(1, 60)),
                tags=["sintético", category.value] + random.sample(order.tags, k=min(2, len(order.tags)))
            )
            
            await doc.create()
            created_docs.append(doc)
            
            # Atualizar contador na Order
            order.document_count += 1
            order.last_activity = max(order.last_activity, doc.uploaded_at)
        
        # Salvar Order atualizada
        await order.save()
        
        print(f"✅ Criada Order '{order.title}' com {num_docs} documentos")
    
    print(f"\n🎉 Processo concluído!")
    print(f"📊 Resumo:")
    print(f"   • Orders criadas: {len(created_orders)}")
    print(f"   • Documentos criados: {len(created_docs)}")
    print(f"   • Embeddings gerados: {len(created_docs)}")
    
    return created_orders, created_docs

async def create_semantic_clusters():
    """Cria documentos agrupados semanticamente para demonstrar clustering"""
    
    print("\n🧠 Criando clusters semânticos para demonstração...")
    
    # Definir temas/clusters semânticos
    semantic_themes = {
        "coffee_export": {
            "center_embedding": generate_embedding("Brazilian coffee export to Europe high quality arabica beans", 768),
            "documents": [
                {
                    "filename": "coffee_quality_certificate_santos.pdf",
                    "text": "Certificate of Quality - Brazilian Arabica Coffee Santos Grade A. Origin: São Paulo State. Cupping score: 84/100. Specialty coffee for European market.",
                    "category": DocumentCategory.CERTIFICATE
                },
                {
                    "filename": "coffee_commercial_invoice_export.pdf", 
                    "text": "Commercial Invoice - Coffee Export to Hamburg. Product: Green Coffee Beans Arabica. Quality: Santos Grade A. Bags: 300 x 60kg.",
                    "category": DocumentCategory.INVOICE
                },
                {
                    "filename": "coffee_shipping_bl_maersk.pdf",
                    "text": "Bill of Lading MAERSK Line - Container MSKU7890123456 with Brazilian coffee beans. From Santos to Hamburg. FCL 20'GP.",
                    "category": DocumentCategory.BL
                }
            ]
        },
        "container_damage": {
            "center_embedding": generate_embedding("Container damage inspection report maritime transport", 768),
            "documents": [
                {
                    "filename": "damage_report_container_MSKU123.pdf",
                    "text": "Damage Assessment Report - Container MSKU1234567890 shows external damage on left side. Dents and scratches observed. Cargo integrity maintained.",
                    "category": DocumentCategory.OTHER
                },
                {
                    "filename": "container_inspection_photo_damage.jpg",
                    "text": "Photographic evidence of container damage. External view showing impact marks on container door. Internal inspection shows no cargo damage.",
                    "category": DocumentCategory.PHOTO
                },
                {
                    "filename": "insurance_claim_container_damage.pdf",
                    "text": "Insurance claim for container damage during maritime transport. Policy number: MAR-2024-7890. Damage amount: USD 2,450.00.",
                    "category": DocumentCategory.CONTRACT
                }
            ]
        },
        "customs_clearance": {
            "center_embedding": generate_embedding("Customs clearance procedures import export documentation", 768),
            "documents": [
                {
                    "filename": "customs_declaration_import_2024.xml",
                    "text": "Customs Declaration for Import - DI Number: 24/1234567-8. Importer: Santos Trading Ltda. Goods: Manufactured products. CIF Value: USD 28,900.00",
                    "category": DocumentCategory.OTHER
                },
                {
                    "filename": "import_license_anvisa_2024.pdf",
                    "text": "Import License ANVISA - License No: 2024/LI/12345. Product: Food supplements. Validity: 180 days. Authorized importer: Health Products Ltda.",
                    "category": DocumentCategory.CERTIFICATE
                },
                {
                    "filename": "customs_clearance_email_broker.eml",
                    "text": "Subject: Customs Clearance Completed - DI 24/1234567-8. Dear client, customs clearance has been successfully completed. Goods available for pickup.",
                    "category": DocumentCategory.EMAIL
                }
            ]
        }
    }
    
    # Criar Order para documentos semânticos
    semantic_order = Order(
        title="Demonstração Clusters Semânticos - Documentos Relacionados",
        description="Order especial contendo documentos agrupados por similaridade semântica para demonstração do mapa semântico",
        order_type=OrderType.IMPORT,
        status=OrderStatus.COMPLETED,
        customer_name="Demo Semantic Clustering Inc",
        customer_id="DEMO_SEM_001",
        origin="Santos, SP",
        destination="Hamburg, Germany", 
        estimated_value=75000.0,
        currency="USD",
        priority=5,
        tags=["demo", "semantic", "clustering", "ml"],
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    
    await semantic_order.create()
    
    cluster_docs = []
    
    # Criar documentos para cada cluster
    for theme_name, theme_data in semantic_themes.items():
        center_embedding = theme_data["center_embedding"]
        
        for doc_data in theme_data["documents"]:
            # Gerar embedding próximo ao centro do cluster
            base_embedding = np.array(center_embedding)
            noise = np.random.normal(0, 0.1, len(base_embedding))  # Pequeno ruído
            doc_embedding = base_embedding + noise
            doc_embedding = doc_embedding / np.linalg.norm(doc_embedding)  # Normalizar
            
            doc = DocumentFile(
                original_name=doc_data["filename"],
                s3_key=f"semantic_demo/{theme_name}/{doc_data['filename']}",
                s3_url=f"https://bucket.s3.amazonaws.com/semantic_demo/{theme_name}/{doc_data['filename']}",
                file_type="application/pdf",
                file_extension=doc_data["filename"].split('.')[-1],
                size_bytes=random.randint(100000, 800000),
                category=doc_data["category"],
                order_id=semantic_order.order_id,
                processing_status=ProcessingStatus.INDEXED,
                text_content=doc_data["text"],
                embedding=doc_embedding.tolist(),
                embedding_model="text-embedding-3-small",
                indexed_at=datetime.utcnow(),
                uploaded_at=semantic_order.created_at + timedelta(hours=random.randint(1, 24)),
                tags=["semantic_demo", theme_name, "clustering"]
            )
            
            await doc.create()
            cluster_docs.append(doc)
            semantic_order.document_count += 1
    
    await semantic_order.save()
    
    print(f"✅ Criados {len(cluster_docs)} documentos em clusters semânticos")
    print(f"   • Clusters: {list(semantic_themes.keys())}")
    print(f"   • Documentos por cluster: {[len(theme_data['documents']) for theme_data in semantic_themes.values()]}")
    
    return cluster_docs

async def main():
    """Função principal"""
    print("🎯 Iniciando criação de dados sintéticos para visualizações...\n")
    
    # Inicializar database
    await init_database()
    
    # Verificar se já existem dados
    existing_orders = await Order.find().limit(1).to_list()
    existing_docs = await DocumentFile.find().limit(1).to_list()
    
    if existing_orders or existing_docs:
        print("⚠️  Já existem dados no banco. Continuando com criação de dados sintéticos adicionais...")
        print(f"   • Orders existentes: {len(existing_orders)}")
        print(f"   • Documentos existentes: {len(existing_docs)}")
    
    try:
        # Criar Orders com documentos
        orders, docs = await create_orders_with_documents(
            num_orders=15,  # Mais Orders para visualização rica
            docs_per_order_range=(4, 10)  # Mais documentos por Order
        )
        
        # Criar clusters semânticos
        semantic_docs = await create_semantic_clusters()
        
        # Estatísticas finais
        total_orders = await Order.count()
        total_docs = await DocumentFile.count()
        docs_with_embedding = await DocumentFile.find(DocumentFile.embedding != None).count()
        
        print(f"\n📈 Estatísticas finais do banco de dados:")
        print(f"   • Total Orders: {total_orders}")
        print(f"   • Total DocumentFiles: {total_docs}")
        print(f"   • Documentos com embedding: {docs_with_embedding}")
        print(f"   • Documentos por categoria:")
        
        for category in DocumentCategory:
            count = await DocumentFile.find(DocumentFile.category == category).count()
            if count > 0:
                print(f"     - {category.value}: {count}")
        
        print("\n🎉 Dados sintéticos criados com sucesso!")
        print("🔍 Agora você pode testar as visualizações em: http://localhost:3000/visualizations")
        
    except Exception as e:
        print(f"❌ Erro durante criação dos dados: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())