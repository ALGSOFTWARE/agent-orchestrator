"""
Smart Chat Cache System
Intelligent caching for document searches and frequent queries
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("ChatCache")

class ChatCache:
    """Intelligent cache system for chat responses and document searches"""
    
    def __init__(self, default_ttl: int = 3600):  # 1 hour default TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        
        # Start background cleanup task
        asyncio.create_task(self._cleanup_expired())
        
        logger.info("🧠 Smart Chat Cache initialized")
    
    def _generate_key(self, query: str, context: Dict[str, Any]) -> str:
        """Generate cache key from query and context"""
        # Normalize query for better hit rate
        normalized_query = query.lower().strip()
        
        # Include relevant context elements
        context_key = {
            "user_id": context.get("userId"),
            "role": context.get("role"),
            "agent": context.get("agent_name")
        }
        
        # Create hash
        key_data = f"{normalized_query}|{json.dumps(context_key, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached response if available and valid"""
        self.stats["total_requests"] += 1
        
        key = self._generate_key(query, context)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if time.time() > entry["expires_at"]:
                del self.cache[key]
                self.stats["evictions"] += 1
                self.stats["misses"] += 1
                return None
            
            # Check freshness for document queries
            if self._is_document_query(query) and self._needs_fresh_data(entry):
                self.stats["misses"] += 1
                return None
            
            self.stats["hits"] += 1
            logger.debug(f"✅ Cache hit for query: {query[:50]}...")
            return entry["data"]
        
        self.stats["misses"] += 1
        return None
    
    def set(
        self, 
        query: str, 
        context: Dict[str, Any], 
        response: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """Cache a response"""
        key = self._generate_key(query, context)
        ttl = ttl or self.default_ttl
        
        # Adjust TTL based on query type
        if self._is_document_query(query):
            ttl = min(ttl, 1800)  # Max 30 minutes for document queries
        elif self._is_general_query(query):
            ttl = max(ttl, 7200)  # Min 2 hours for general queries
        
        self.cache[key] = {
            "data": response,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
            "query": query[:100],  # Store truncated query for debugging
            "hit_count": 0
        }
        
        logger.debug(f"💾 Cached response for query: {query[:50]}... (TTL: {ttl}s)")
    
    def _is_document_query(self, query: str) -> bool:
        """Check if query is document-related"""
        doc_keywords = [
            'mdf', 'manifesto', 'cte', 'ct-e', 'bl', 'bill', 'awl', 'nf', 'nota',
            'documento', 'container', 'embarque', 'carga', 'order'
        ]
        return any(keyword in query.lower() for keyword in doc_keywords)
    
    def _is_general_query(self, query: str) -> bool:
        """Check if query is general/help-related"""
        general_keywords = [
            'ajuda', 'help', 'como', 'what', 'que', 'posso', 'pode',
            'sistema', 'funciona', 'usar'
        ]
        return any(keyword in query.lower() for keyword in general_keywords)
    
    def _needs_fresh_data(self, entry: Dict[str, Any]) -> bool:
        """Check if document data might be stale"""
        # For document queries, prefer fresher data
        age = time.time() - entry["created_at"]
        return age > 900  # 15 minutes
    
    async def _cleanup_expired(self):
        """Background task to clean expired entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                current_time = time.time()
                expired_keys = [
                    key for key, entry in self.cache.items()
                    if current_time > entry["expires_at"]
                ]
                
                for key in expired_keys:
                    del self.cache[key]
                    self.stats["evictions"] += 1
                
                if expired_keys:
                    logger.debug(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
                    
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching a pattern"""
        keys_to_remove = [
            key for key, entry in self.cache.items()
            if pattern.lower() in entry["query"].lower()
        ]
        
        for key in keys_to_remove:
            del self.cache[key]
            
        logger.info(f"🗑️ Invalidated {len(keys_to_remove)} cache entries matching: {pattern}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = (self.stats["hits"] / max(self.stats["total_requests"], 1)) * 100
        
        return {
            "total_entries": len(self.cache),
            "total_requests": self.stats["total_requests"],
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "hit_rate_percentage": round(hit_rate, 2),
            "evictions": self.stats["evictions"],
            "memory_usage_estimate": sum(
                len(str(entry)) for entry in self.cache.values()
            )
        }
    
    def clear(self):
        """Clear all cache entries"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"🗑️ Cleared {count} cache entries")


# Global cache instance
_cache = None

def get_chat_cache() -> ChatCache:
    """Get global chat cache instance"""
    global _cache
    if _cache is None:
        _cache = ChatCache()
    return _cache

# Convenience functions
def get_cached_response(query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get cached response"""
    cache = get_chat_cache()
    return cache.get(query, context)

def cache_response(query: str, context: Dict[str, Any], response: Dict[str, Any], ttl: Optional[int] = None):
    """Cache a response"""
    cache = get_chat_cache()
    cache.set(query, context, response, ttl)

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    cache = get_chat_cache()
    return cache.get_stats()

def invalidate_cache_pattern(pattern: str):
    """Invalidate cache entries matching pattern"""
    cache = get_chat_cache()
    cache.invalidate_pattern(pattern)