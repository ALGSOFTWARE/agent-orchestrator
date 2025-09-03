"""
Conversation Context Analyzer
Advanced conversation understanding and context tracking
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger("ConversationAnalyzer")

@dataclass
class ConversationTurn:
    """Single conversation turn"""
    message: str
    timestamp: datetime
    user_id: str
    intent: str
    entities: Dict[str, Any]
    doc_types: List[str]

@dataclass
class ConversationContext:
    """Current conversation context"""
    session_id: str
    user_id: str
    turns: List[ConversationTurn]
    current_topic: Optional[str]
    active_documents: List[str]
    user_expertise_level: str  # novice, intermediate, expert
    conversation_flow: str  # exploration, task_focused, help_seeking

class ConversationAnalyzer:
    """Analyzes conversation context and provides intelligent insights"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ConversationContext] = {}
        self.entity_patterns = self._build_entity_patterns()
        self.intent_patterns = self._build_intent_patterns()
        
        logger.info("🧠 Conversation Analyzer initialized")
    
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """Build entity extraction patterns"""
        return {
            "order_id": [
                r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b',
                r'\border\s+([a-f0-9-]{36})\b',
                r'\bid[:\s]+([a-f0-9-]{36})\b'
            ],
            "document_number": [
                r'\b\d{6,12}\b',  # Common doc numbers
                r'\bmdf[:\s]*(\d+)\b',
                r'\bcte[:\s]*(\d+)\b',
                r'\bnf[:\s]*(\d+)\b'
            ],
            "date_range": [
                r'\bultimos?\s+(\d+)\s+dias?\b',
                r'\bpast\s+(\d+)\s+days?\b',
                r'\bh[aá]\s+(\d+)\s+dias?\b'
            ],
            "container_number": [
                r'\b[A-Z]{4}\d{7}\b',  # Standard container format
                r'\bcontainer[:\s]*([A-Z0-9]+)\b'
            ]
        }
    
    def _build_intent_patterns(self) -> Dict[str, List[str]]:
        """Build intent detection patterns"""
        return {
            "document_search": [
                r'\bbuscar?\b', r'\bprocurar?\b', r'\bencontrar?\b',
                r'\bmostrar?\b', r'\bver\b', r'\bexibir?\b'
            ],
            "document_analysis": [
                r'\banalis[ae]r?\b', r'\banalys[ei]s?\b', r'\bevalu[ae]r?\b',
                r'\binsight[s]?\b', r'\brelatório\b', r'\breport\b'
            ],
            "status_check": [
                r'\bstatus\b', r'\bestado\b', r'\bsitua[çc][aã]o\b',
                r'\bcomo\s+est[aá]\b', r'\bprogresso\b'
            ],
            "help_request": [
                r'\bajud[ae]r?\b', r'\bhelp\b', r'\bcomo\b', r'\bque\b',
                r'\bposso\b', r'\bsaber\b', r'\bentender\b'
            ],
            "presupposed_query": [
                r'\bo\s+que\s+voc[eê]\s+pode\s+me\s+dizer\s+sobre\b',
                r'\bme\s+fale\s+sobre\b', r'\bconte\s+sobre\b',
                r'\bquais\s+s[aã]o\b', r'\bhá\s+algum\b'
            ]
        }
    
    def analyze_message(
        self,
        message: str,
        user_context: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Analyze a single message and update conversation context"""
        
        # Extract entities
        entities = self._extract_entities(message)
        
        # Detect intent
        intent = self._detect_intent(message)
        
        # Extract document types
        doc_types = self._extract_document_types(message)
        
        # Get or create conversation context
        context = self._get_conversation_context(session_id, user_context.get('userId', 'unknown'))
        
        # Create conversation turn
        turn = ConversationTurn(
            message=message,
            timestamp=datetime.now(),
            user_id=user_context.get('userId', 'unknown'),
            intent=intent,
            entities=entities,
            doc_types=doc_types
        )
        
        # Add turn to context
        context.turns.append(turn)
        
        # Update context intelligence
        self._update_context_intelligence(context)
        
        # Generate conversation insights
        insights = self._generate_insights(context)
        
        return {
            "intent": intent,
            "entities": entities,
            "doc_types": doc_types,
            "conversation_insights": insights,
            "context_summary": self._summarize_context(context),
            "suggested_followups": self._suggest_followups(context),
            "expertise_level": context.user_expertise_level,
            "conversation_flow": context.conversation_flow
        }
    
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Extract entities from message"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            for pattern in patterns:
                matches.extend(re.findall(pattern, message, re.IGNORECASE))
            
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return entities
    
    def _detect_intent(self, message: str) -> str:
        """Detect primary intent from message"""
        message_lower = message.lower()
        
        # Score each intent
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, message_lower))
            if score > 0:
                intent_scores[intent] = score
        
        # Return highest scoring intent
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return "general_query"
    
    def _extract_document_types(self, message: str) -> List[str]:
        """Extract mentioned document types"""
        doc_type_map = {
            'mdf': 'MDF', 'manifesto': 'MANIFESTO',
            'cte': 'CTE', 'ct-e': 'CTE',
            'bl': 'BL', 'bill': 'BL',
            'awl': 'AWL', 'nf': 'NF', 'nota': 'NF',
            'invoice': 'INVOICE', 'fatura': 'INVOICE'
        }
        
        message_lower = message.lower()
        found_types = []
        
        for keyword, doc_type in doc_type_map.items():
            if keyword in message_lower:
                found_types.append(doc_type)
        
        return list(set(found_types))  # Remove duplicates
    
    def _get_conversation_context(self, session_id: str, user_id: str) -> ConversationContext:
        """Get or create conversation context"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = ConversationContext(
                session_id=session_id,
                user_id=user_id,
                turns=[],
                current_topic=None,
                active_documents=[],
                user_expertise_level="novice",
                conversation_flow="exploration"
            )
        
        return self.active_sessions[session_id]
    
    def _update_context_intelligence(self, context: ConversationContext):
        """Update conversation context with intelligence"""
        if len(context.turns) < 2:
            return
        
        recent_turns = context.turns[-5:]  # Last 5 turns
        
        # Detect expertise level
        technical_terms = sum(1 for turn in recent_turns 
                            if any(term in turn.message.lower() 
                                 for term in ['mongodb', 'query', 'api', 'endpoint', 'collection']))
        
        if technical_terms >= 2:
            context.user_expertise_level = "expert"
        elif technical_terms >= 1:
            context.user_expertise_level = "intermediate"
        else:
            context.user_expertise_level = "novice"
        
        # Detect conversation flow
        intents = [turn.intent for turn in recent_turns]
        
        if intents.count('help_request') >= 2:
            context.conversation_flow = "help_seeking"
        elif intents.count('document_search') >= 2:
            context.conversation_flow = "task_focused"
        else:
            context.conversation_flow = "exploration"
        
        # Update active documents
        all_entities = {}
        for turn in recent_turns:
            for entity_type, values in turn.entities.items():
                if entity_type not in all_entities:
                    all_entities[entity_type] = []
                all_entities[entity_type].extend(values)
        
        context.active_documents = all_entities.get('order_id', [])[:3]  # Keep last 3 orders
    
    def _generate_insights(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate conversation insights"""
        if len(context.turns) < 2:
            return {}
        
        recent_turns = context.turns[-3:]
        
        # Pattern analysis
        patterns = {
            "repeating_questions": self._detect_repeating_patterns(context),
            "escalating_complexity": self._detect_complexity_escalation(recent_turns),
            "document_focus": self._detect_document_focus(recent_turns),
            "user_frustration": self._detect_frustration_signals(recent_turns)
        }
        
        return patterns
    
    def _detect_repeating_patterns(self, context: ConversationContext) -> bool:
        """Detect if user is asking similar questions"""
        if len(context.turns) < 3:
            return False
        
        recent_intents = [turn.intent for turn in context.turns[-3:]]
        return len(set(recent_intents)) == 1 and recent_intents[0] != "general_query"
    
    def _detect_complexity_escalation(self, turns: List[ConversationTurn]) -> bool:
        """Detect if queries are becoming more complex"""
        if len(turns) < 2:
            return False
        
        complexity_scores = []
        for turn in turns:
            score = len(turn.entities) + len(turn.doc_types)
            complexity_scores.append(score)
        
        return len(complexity_scores) >= 2 and complexity_scores[-1] > complexity_scores[0]
    
    def _detect_document_focus(self, turns: List[ConversationTurn]) -> Optional[str]:
        """Detect primary document focus"""
        doc_counts = {}
        for turn in turns:
            for doc_type in turn.doc_types:
                doc_counts[doc_type] = doc_counts.get(doc_type, 0) + 1
        
        if doc_counts:
            return max(doc_counts, key=doc_counts.get)
        return None
    
    def _detect_frustration_signals(self, turns: List[ConversationTurn]) -> bool:
        """Detect signs of user frustration"""
        frustration_words = [
            'não funciona', 'não encontra', 'erro', 'problema',
            'não consegue', 'bug', 'falha', 'incorreto'
        ]
        
        for turn in turns:
            message_lower = turn.message.lower()
            if any(word in message_lower for word in frustration_words):
                return True
        
        return False
    
    def _summarize_context(self, context: ConversationContext) -> str:
        """Generate context summary"""
        if not context.turns:
            return "Conversa iniciada"
        
        recent_topics = []
        if context.current_topic:
            recent_topics.append(context.current_topic)
        
        doc_types = set()
        for turn in context.turns[-3:]:
            doc_types.update(turn.doc_types)
        
        if doc_types:
            recent_topics.append(f"Documentos: {', '.join(doc_types)}")
        
        summary = f"Conversa {context.conversation_flow} com {len(context.turns)} mensagens"
        if recent_topics:
            summary += f" - Tópicos: {'; '.join(recent_topics)}"
        
        return summary
    
    def _suggest_followups(self, context: ConversationContext) -> List[str]:
        """Suggest followup actions"""
        if not context.turns:
            return []
        
        last_turn = context.turns[-1]
        suggestions = []
        
        # Based on last intent
        if last_turn.intent == "document_search":
            suggestions.extend([
                "Gostaria de ver detalhes específicos destes documentos?",
                "Precisa analisar compliance ou status destes documentos?",
                "Quer exportar estes resultados?"
            ])
        elif last_turn.intent == "help_request":
            suggestions.extend([
                "Posso demonstrar com um exemplo prático?",
                "Gostaria de ver um tutorial passo a passo?",
                "Precisa de informações sobre outros recursos?"
            ])
        
        # Based on document types mentioned
        if last_turn.doc_types:
            suggestions.append(f"Quer ver estatísticas detalhadas sobre {', '.join(last_turn.doc_types)}?")
        
        return suggestions[:3]  # Return max 3 suggestions
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get conversation analyzer statistics"""
        total_sessions = len(self.active_sessions)
        total_turns = sum(len(ctx.turns) for ctx in self.active_sessions.values())
        
        expertise_distribution = {}
        flow_distribution = {}
        
        for ctx in self.active_sessions.values():
            expertise_distribution[ctx.user_expertise_level] = expertise_distribution.get(ctx.user_expertise_level, 0) + 1
            flow_distribution[ctx.conversation_flow] = flow_distribution.get(ctx.conversation_flow, 0) + 1
        
        return {
            "total_active_sessions": total_sessions,
            "total_conversation_turns": total_turns,
            "average_turns_per_session": total_turns / max(total_sessions, 1),
            "expertise_distribution": expertise_distribution,
            "conversation_flow_distribution": flow_distribution
        }

# Global analyzer instance
_analyzer = None

def get_conversation_analyzer() -> ConversationAnalyzer:
    """Get global conversation analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ConversationAnalyzer()
    return _analyzer

# Convenience function
def analyze_conversation(
    message: str,
    user_context: Dict[str, Any],
    session_id: str
) -> Dict[str, Any]:
    """Analyze conversation message"""
    analyzer = get_conversation_analyzer()
    return analyzer.analyze_message(message, user_context, session_id)