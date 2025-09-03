"""
Document Tools for CrewAI Agents
Complete set of tools for document search, analysis, and compliance checking
"""

import requests
import logging
import json
from typing import Dict, Any, List, Optional
from crewai_tools import tool
from datetime import datetime, timedelta
import asyncio

# MongoDB connection
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️ Motor não disponível para MongoDB")

logger = logging.getLogger(__name__)

# Database configuration
MONGODB_URL = "mongodb+srv://dev:JiCoKnCCu6pHpIwZ@dev.fednd1d.mongodb.net/?retryWrites=true&w=majority&appName=dev"
DATABASE_NAME = "mit_logistics"

async def get_mongo_client():
    """Get MongoDB client"""
    if not MONGODB_AVAILABLE:
        raise Exception("MongoDB motor library not available")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    return client[DATABASE_NAME]

def run_async(coro):
    """Run async function in sync context"""
    try:
        # Try to get the current loop
        loop = asyncio.get_running_loop()
        # If we're in an async context, we can't use run_until_complete
        # So we'll create a new thread with a new loop
        import concurrent.futures
        import threading
        
        def run_in_new_loop():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_loop)
            return future.result()
            
    except RuntimeError:
        # No event loop running, safe to use run_until_complete
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)


@tool("search_documents")
def search_documents(query: str, search_type: str = "semantic", limit: int = 10, filters: Optional[str] = None) -> str:
    """
    Search for documents in the logistics system using semantic or traditional search.
    Use this tool to find MDF, CTE, BL, NFe, and other logistics documents.
    Supports both semantic search (understanding context) and traditional keyword search.
    
    Args:
        query: Search query for documents (e.g., "containers from Santos", "CT-e status pending", "MDF")
        search_type: Type of search - 'semantic' for concept-based or 'traditional' for keyword-based (default: semantic)
        limit: Maximum number of documents to return (default: 10)
        filters: Optional JSON string with filters like '{"category": "invoice", "processing_status": "indexed"}'
    
    Returns:
        str: Formatted search results with document information
    """
    async def _search_documents_async():
        try:
            db = await get_mongo_client()
            collection = db.document_files
            
            # Build MongoDB query
            query_filter = {}
            
            # Add filters if provided
            if filters:
                try:
                    filter_dict = json.loads(filters)
                    # Map common filter names to correct field names
                    field_mapping = {
                        'type': 'category',  # Map type to category
                        'status': 'processing_status'
                    }
                    
                    for key, value in filter_dict.items():
                        mapped_key = field_mapping.get(key, key)
                        query_filter[mapped_key] = value
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON filters: {filters}")
            
            # Handle text search
            if query and query.strip():
                # Search in various text fields
                text_search = {
                    "$or": [
                        {"original_name": {"$regex": query, "$options": "i"}},
                        {"category": {"$regex": query, "$options": "i"}},
                        {"text_content": {"$regex": query, "$options": "i"}},
                        {"tags": {"$in": [query.lower()]}},
                        {"s3_key": {"$regex": query, "$options": "i"}}
                    ]
                }
                
                if query_filter:
                    query_filter = {"$and": [text_search, query_filter]}
                else:
                    query_filter = text_search
            
            # Execute query
            cursor = collection.find(query_filter).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            if not documents:
                return f"No documents found for query: '{query}'. Try different keywords or check document categories like 'invoice', 'certificate', 'contract'."
            
            # Format results for agent consumption
            results = []
            results.append(f"🔍 Found {len(documents)} documents for query: '{query}'")
            results.append("=" * 60)
            results.append("")
            
            for i, doc in enumerate(documents, 1):
                # Extract relevant information
                doc_id = str(doc.get('_id', 'N/A'))
                original_name = doc.get('original_name', 'N/A')
                category = doc.get('category', 'N/A')
                processing_status = doc.get('processing_status', 'N/A')
                file_type = doc.get('file_type', 'N/A')
                size_bytes = doc.get('size_bytes', 0)
                uploaded_at = doc.get('uploaded_at', 'N/A')
                order_id = doc.get('order_id', 'N/A')
                tags = doc.get('tags', [])
                
                # Format size
                if size_bytes > 0:
                    if size_bytes > 1024 * 1024:
                        size_str = f"{size_bytes / (1024*1024):.1f} MB"
                    elif size_bytes > 1024:
                        size_str = f"{size_bytes / 1024:.1f} KB"
                    else:
                        size_str = f"{size_bytes} bytes"
                else:
                    size_str = "Unknown"
                
                doc_info = [
                    f"📄 Document {i}:",
                    f"   ID: {doc_id}",
                    f"   Name: {original_name}",
                    f"   Category: {category}",
                    f"   File Type: {file_type}",
                    f"   Status: {processing_status}",
                    f"   Size: {size_str}",
                    f"   Order ID: {order_id}",
                    f"   Upload Date: {uploaded_at}",
                    f"   Tags: {', '.join(tags) if tags else 'None'}",
                ]
                
                results.extend(doc_info)
                results.append("")
            
            results.append(f"💡 Tip: Use analyze_document_content(document_id) to get detailed analysis of any document")
            return "\n".join(results)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in MongoDB document search: {error_msg}")
            return f"❌ Error searching documents: {error_msg}"
    
    if not MONGODB_AVAILABLE:
        return "❌ Busca semântica não disponível: MongoDB motor library not available"
    
    return run_async(_search_documents_async())


@tool("analyze_document_content")
def analyze_document_content(document_id: str) -> str:
    """
    Analyze the content and metadata of a specific document.
    Use this tool to understand what's inside a document, extract key information,
    analyze document structure, and get business insights.
    
    Args:
        document_id: ID of the document to analyze (from search results)
    
    Returns:
        str: Detailed document analysis with content, metadata, and business insights
    """
    try:
        url = f"{GATEKEEPER_API_BASE}/frontend/documents/{document_id}"
        logger.info(f"🔍 Analyzing document: {url}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            doc = data.get("data", {})
            
            analysis = []
            analysis.append(f"📊 Document Analysis for ID: {document_id}")
            analysis.append("=" * 60)
            analysis.append("")
            
            # Basic Information
            analysis.extend([
                "📋 Basic Information:",
                f"   Name: {doc.get('original_name', doc.get('file_name', 'N/A'))}",
                f"   Type: {doc.get('file_type', doc.get('type', 'N/A'))}",
                f"   Category: {doc.get('category', 'N/A')}",
                f"   Status: {doc.get('processing_status', doc.get('status', 'N/A'))}",
                f"   Size: {doc.get('size_bytes', 'N/A')} bytes",
                f"   Upload Date: {doc.get('uploaded_at', doc.get('date', 'N/A'))}",
                f"   Order ID: {doc.get('order_id', 'N/A')}",
                ""
            ])
            
            # Content Analysis
            analysis.append("🔍 Content Analysis:")
            has_text = bool(doc.get('text_content'))
            has_embedding = bool(doc.get('embedding'))
            analysis.extend([
                f"   Text Content: {'✅ Available' if has_text else '❌ Not available'}",
                f"   AI Embedding: {'✅ Generated' if has_embedding else '❌ Not generated'}",
                f"   Access Count: {doc.get('access_count', 0)}",
                ""
            ])
            
            # Business Context
            if doc.get('client') or doc.get('origin') or doc.get('destination'):
                analysis.append("🏢 Business Context:")
                if doc.get('client'):
                    analysis.append(f"   Client: {doc['client']}")
                if doc.get('origin'):
                    analysis.append(f"   Origin: {doc['origin']}")
                if doc.get('destination'):
                    analysis.append(f"   Destination: {doc['destination']}")
                if doc.get('value'):
                    analysis.append(f"   Value: {doc['value']}")
                analysis.append("")
            
            # Document Text Content (if available)
            if doc.get('text_content'):
                content = doc['text_content']
                analysis.append("📄 Document Content:")
                analysis.append("-" * 30)
                
                # Show first 800 characters
                if len(content) > 800:
                    content = content[:800] + "\n\n... [Content truncated for readability]"
                
                analysis.append(content)
                analysis.append("")
            
            # Recommendations
            analysis.append("💡 Recommendations:")
            recommendations = []
            
            if not has_text:
                recommendations.append("   • Consider re-processing document to extract text content")
            if not has_embedding:
                recommendations.append("   • Generate AI embedding for better semantic search")
            if doc.get('processing_status') == 'pending':
                recommendations.append("   • Document processing incomplete - check for errors")
            if doc.get('access_count', 0) == 0:
                recommendations.append("   • Document hasn't been accessed - verify relevance")
            
            if not recommendations:
                recommendations.append("   • Document appears to be properly processed and ready for use")
            
            analysis.extend(recommendations)
            
            return "\n".join(analysis)
            
        elif response.status_code == 404:
            return f"❌ Document with ID '{document_id}' not found. Please verify the document ID from search results."
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return f"❌ {error_msg}"
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error analyzing document: {error_msg}")
        return f"❌ Error analyzing document: {error_msg}"


@tool("check_document_compliance")
def check_document_compliance(document_id: str, regulation_type: str = "brazilian") -> str:
    """
    Check document compliance against regulatory requirements.
    Validates document completeness, format, and regulatory compliance.
    
    Args:
        document_id: ID of the document to check compliance
        regulation_type: Type of regulations to check - 'brazilian', 'international', or 'all' (default: brazilian)
    
    Returns:
        str: Detailed compliance analysis with issues and recommendations
    """
    try:
        # First get document details
        url = f"{GATEKEEPER_API_BASE}/frontend/documents/{document_id}"
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            return f"❌ Cannot retrieve document {document_id} for compliance check"
        
        data = response.json()
        doc = data.get("data", {})
        
        compliance = []
        compliance.append(f"⚖️  Compliance Check for Document: {document_id}")
        compliance.append("=" * 60)
        compliance.append("")
        
        doc_type = doc.get('file_type', doc.get('type', 'unknown')).upper()
        doc_name = doc.get('original_name', doc.get('file_name', 'N/A'))
        
        compliance.extend([
            f"📋 Document: {doc_name}",
            f"📄 Type: {doc_type}",
            f"🔍 Regulation Scope: {regulation_type.title()}",
            ""
        ])
        
        # Compliance checks based on document type
        issues = []
        warnings = []
        passed = []
        
        # Basic document checks
        if not doc.get('original_name'):
            issues.append("Missing original file name")
        else:
            passed.append("Document has proper file name")
            
        if not doc.get('text_content'):
            warnings.append("No extracted text content - may limit compliance validation")
        else:
            passed.append("Document content is accessible for validation")
            
        if doc.get('processing_status') != 'completed':
            warnings.append(f"Document processing status is '{doc.get('processing_status')}' - may affect compliance")
        else:
            passed.append("Document processing completed successfully")
        
        # Document type specific checks
        if doc_type in ['CTE', 'CT-E']:
            compliance.append("🚛 CT-e Specific Compliance Checks:")
            
            # Check for required CT-e fields
            required_fields = ['number', 'client', 'origin', 'destination']
            for field in required_fields:
                if doc.get(field):
                    passed.append(f"CT-e has required field: {field}")
                else:
                    issues.append(f"Missing required CT-e field: {field}")
            
            # Brazilian specific checks
            if regulation_type in ['brazilian', 'all']:
                if doc.get('text_content'):
                    content = doc['text_content'].lower()
                    if 'cnpj' in content:
                        passed.append("Document contains CNPJ identification")
                    else:
                        warnings.append("No CNPJ found in document content")
                        
                    if any(keyword in content for keyword in ['sefaz', 'danfe', 'nfe']):
                        passed.append("Document appears to follow Brazilian fiscal standards")
                    else:
                        warnings.append("May not comply with Brazilian fiscal document standards")
        
        elif doc_type in ['BL', 'BILL_OF_LADING']:
            compliance.append("🚢 Bill of Lading Compliance Checks:")
            
            required_fields = ['origin', 'destination', 'client']
            for field in required_fields:
                if doc.get(field):
                    passed.append(f"BL has required field: {field}")
                else:
                    issues.append(f"Missing required BL field: {field}")
            
            # International checks
            if regulation_type in ['international', 'all']:
                if doc.get('text_content'):
                    content = doc['text_content'].lower()
                    international_terms = ['incoterms', 'fob', 'cif', 'exw', 'shipping']
                    if any(term in content for term in international_terms):
                        passed.append("Document contains international shipping terms")
                    else:
                        warnings.append("Missing standard international shipping terms")
        
        elif doc_type in ['MDF', 'MANIFESTO']:
            compliance.append("📦 Manifest Document Compliance Checks:")
            
            if doc.get('text_content'):
                content = doc['text_content'].lower()
                if 'peso' in content or 'weight' in content:
                    passed.append("Document contains weight information")
                else:
                    warnings.append("No weight information found")
                    
                if 'volume' in content or 'quantity' in content:
                    passed.append("Document contains volume/quantity information")
                else:
                    warnings.append("No volume/quantity information found")
        
        # Generic document validation
        file_size = doc.get('size_bytes', 0)
        if file_size > 0:
            if file_size < 50000:  # Less than 50KB
                warnings.append("Document file size is very small - may be incomplete")
            elif file_size > 50000000:  # More than 50MB
                warnings.append("Document file size is very large - may cause processing issues")
            else:
                passed.append("Document file size is within normal range")
        
        # Compile results
        compliance.append("")
        
        if passed:
            compliance.append("✅ Passed Checks:")
            for check in passed:
                compliance.append(f"   • {check}")
            compliance.append("")
        
        if warnings:
            compliance.append("⚠️  Warnings:")
            for warning in warnings:
                compliance.append(f"   • {warning}")
            compliance.append("")
        
        if issues:
            compliance.append("❌ Compliance Issues:")
            for issue in issues:
                compliance.append(f"   • {issue}")
            compliance.append("")
        
        # Overall assessment
        compliance.append("📊 Overall Assessment:")
        if not issues:
            if not warnings:
                compliance.append("   🟢 COMPLIANT - Document meets all requirements")
            else:
                compliance.append("   🟡 MOSTLY COMPLIANT - Minor issues to address")
        else:
            compliance.append("   🔴 NON-COMPLIANT - Critical issues must be resolved")
        
        compliance.append("")
        compliance.append("💡 Recommendations:")
        
        if issues:
            compliance.append("   • Address all compliance issues immediately")
            compliance.append("   • Review document against regulatory requirements")
        if warnings:
            compliance.append("   • Consider addressing warnings for best practices")
        if not issues and not warnings:
            compliance.append("   • Document is ready for processing and submission")
            
        return "\n".join(compliance)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in compliance check: {error_msg}")
        return f"❌ Error checking compliance: {error_msg}"


@tool("get_document_statistics")
def get_document_statistics(timeframe: str = "30d", doc_type: Optional[str] = None) -> str:
    """
    Get statistical information about documents in the system.
    Provides insights into document volumes, types, processing status, etc.
    
    Args:
        timeframe: Time period for statistics - '7d', '30d', '90d', '1y' (default: 30d)
        doc_type: Optional filter by document category - 'invoice', 'certificate', 'contract', etc.
    
    Returns:
        str: Statistical summary of document data
    """
    async def _get_statistics_async():
        try:
            db = await get_mongo_client()
            collection = db.document_files
            
            # Calculate time filter
            days = 30  # default
            if timeframe == "7d":
                days = 7
            elif timeframe == "90d":
                days = 90
            elif timeframe == "1y":
                days = 365
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Build query filter
            query_filter = {"uploaded_at": {"$gte": cutoff_date}}
            
            if doc_type:
                query_filter["category"] = doc_type
            
            # Get documents
            cursor = collection.find(query_filter)
            documents = await cursor.to_list(length=None)
            
            report = []
            report.append(f"📊 Document Statistics Report")
            report.append("=" * 50)
            report.append(f"📅 Time Period: {timeframe}")
            if doc_type:
                report.append(f"📄 Document Category: {doc_type}")
            report.append("")
            
            # Basic counts
            total_docs = len(documents)
            report.append(f"📈 Total Documents: {total_docs:,}")
            
            if documents:
                # Analyze document categories
                category_counts = {}
                status_counts = {}
                order_counts = {}
                
                for doc in documents:
                    category = doc.get('category', 'Unknown')
                    category_counts[category] = category_counts.get(category, 0) + 1
                    
                    status = doc.get('processing_status', 'Unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    order_id = doc.get('order_id', 'Unknown')
                    if order_id != 'Unknown':
                        order_counts[order_id] = order_counts.get(order_id, 0) + 1
                
                # Document categories breakdown
                if category_counts:
                    report.append("")
                    report.append("📄 Document Categories:")
                    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total_docs) * 100
                        report.append(f"   {category}: {count:,} ({percentage:.1f}%)")
                
                # Status breakdown
                if status_counts:
                    report.append("")
                    report.append("⚡ Processing Status:")
                    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total_docs) * 100
                        report.append(f"   {status}: {count:,} ({percentage:.1f}%)")
                
                # Top orders by document count
                if order_counts:
                    report.append("")
                    report.append("📦 Top Orders by Document Count:")
                    top_orders = sorted(order_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    for order_id, count in top_orders:
                        percentage = (count / total_docs) * 100
                        report.append(f"   {order_id[:20]}...: {count:,} ({percentage:.1f}%)")
                
                # Calculate file size stats
                sizes = [doc.get('size_bytes', 0) for doc in documents if doc.get('size_bytes')]
                if sizes:
                    avg_size = sum(sizes) / len(sizes)
                    total_size = sum(sizes)
                    
                    report.append("")
                    report.append("💾 Storage Statistics:")
                    report.append(f"   Total Storage: {total_size / (1024*1024):.1f} MB")
                    report.append(f"   Average File Size: {avg_size / 1024:.1f} KB")
                    report.append(f"   Largest File: {max(sizes) / (1024*1024):.1f} MB")
                    report.append(f"   Smallest File: {min(sizes) / 1024:.1f} KB")
                
                # Tags analysis
                all_tags = []
                for doc in documents:
                    if doc.get('tags'):
                        all_tags.extend(doc['tags'])
                
                if all_tags:
                    from collections import Counter
                    tag_counts = Counter(all_tags)
                    report.append("")
                    report.append("🏷️  Most Common Tags:")
                    for tag, count in tag_counts.most_common(5):
                        percentage = (count / total_docs) * 100
                        report.append(f"   {tag}: {count:,} ({percentage:.1f}%)")
            
            else:
                report.append("No documents found for the specified criteria.")
            
            return "\n".join(report)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error getting MongoDB document statistics: {error_msg}")
            return f"❌ Error retrieving document statistics: {error_msg}"
    
    if not MONGODB_AVAILABLE:
        return "❌ Estatísticas não disponíveis: MongoDB motor library not available"
    
    return run_async(_get_statistics_async())