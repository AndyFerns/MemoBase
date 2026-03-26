"""
Intent classifier implementation.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from memobase.core.exceptions import QueryError
from memobase.core.models import QueryType


class IntentClassifier:
    """Classifies user query intents using pattern matching and heuristics."""
    
    def __init__(self) -> None:
        """Initialize intent classifier."""
        self.intent_patterns = self._init_intent_patterns()
        self.keyword_weights = self._init_keyword_weights()
        self.context_patterns = self._init_context_patterns()
    
    def classify_intent(self, query_text: str, context: Dict = None) -> QueryType:
        """Classify query intent with high accuracy.
        
        Args:
            query_text: Raw query text
            context: Optional context information
            
        Returns:
            QueryType enum value
        """
        try:
            query_lower = query_text.lower().strip()
            
            # Score each intent type
            intent_scores = {}
            
            for intent_type in QueryType:
                score = self._calculate_intent_score(query_lower, intent_type, context)
                intent_scores[intent_type] = score
            
            # Get highest scoring intent
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            
            # Apply confidence threshold
            if best_intent[1] < 0.3:
                return QueryType.SEARCH  # Default fallback
            
            return best_intent[0]
            
        except Exception as e:
            raise QueryError(f"Intent classification failed: {str(e)}")
    
    def get_intent_confidence(self, query_text: str, context: Dict = None) -> Tuple[QueryType, float]:
        """Get intent with confidence score.
        
        Args:
            query_text: Raw query text
            context: Optional context information
            
        Returns:
            Tuple of (QueryType, confidence_score)
        """
        try:
            query_lower = query_text.lower().strip()
            
            # Score each intent type
            intent_scores = {}
            
            for intent_type in QueryType:
                score = self._calculate_intent_score(query_lower, intent_type, context)
                intent_scores[intent_type] = score
            
            # Get highest scoring intent
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            
            return best_intent[0], best_intent[1]
            
        except Exception as e:
            raise QueryError(f"Intent confidence calculation failed: {str(e)}")
    
    def classify_batch(self, queries: List[str], context: Dict = None) -> List[QueryType]:
        """Classify multiple queries.
        
        Args:
            queries: List of query texts
            context: Optional context information
            
        Returns:
            List of QueryType enum values
        """
        try:
            results = []
            for query in queries:
                intent = self.classify_intent(query, context)
                results.append(intent)
            return results
            
        except Exception as e:
            raise QueryError(f"Batch intent classification failed: {str(e)}")
    
    def _calculate_intent_score(self, query_text: str, intent_type: QueryType, context: Dict = None) -> float:
        """Calculate score for a specific intent type."""
        score = 0.0
        
        # Pattern matching score
        pattern_score = self._pattern_match_score(query_text, intent_type)
        score += pattern_score * 0.4
        
        # Keyword matching score
        keyword_score = self._keyword_match_score(query_text, intent_type)
        score += keyword_score * 0.3
        
        # Context matching score
        if context:
            context_score = self._context_match_score(query_text, intent_type, context)
            score += context_score * 0.2
        
        # Structural score
        structural_score = self._structural_score(query_text, intent_type)
        score += structural_score * 0.1
        
        return min(1.0, score)
    
    def _pattern_match_score(self, query_text: str, intent_type: QueryType) -> float:
        """Calculate pattern matching score."""
        patterns = self.intent_patterns.get(intent_type, [])
        
        if not patterns:
            return 0.0
        
        max_score = 0.0
        for pattern in patterns:
            if re.search(pattern, query_text):
                # Calculate match strength based on pattern specificity
                pattern_specificity = len(pattern.split())
                score = min(1.0, pattern_specificity / 5.0)
                max_score = max(max_score, score)
        
        return max_score
    
    def _keyword_match_score(self, query_text: str, intent_type: QueryType) -> float:
        """Calculate keyword matching score."""
        keywords = self.keyword_weights.get(intent_type, {})
        
        if not keywords:
            return 0.0
        
        total_score = 0.0
        query_words = set(query_text.split())
        
        for keyword, weight in keywords.items():
            if keyword in query_words:
                total_score += weight
        
        # Normalize by maximum possible score
        max_possible = sum(keywords.values())
        return total_score / max_possible if max_possible > 0 else 0.0
    
    def _context_match_score(self, query_text: str, intent_type: QueryType, context: Dict) -> float:
        """Calculate context matching score."""
        patterns = self.context_patterns.get(intent_type, [])
        
        if not patterns or not context:
            return 0.0
        
        score = 0.0
        
        for context_key, expected_values in patterns:
            if context_key in context:
                context_value = str(context[context_key]).lower()
                for expected in expected_values:
                    if expected in context_value:
                        score += 0.5
        
        return min(1.0, score)
    
    def _structural_score(self, query_text: str, intent_type: QueryType) -> float:
        """Calculate structural score based on query characteristics."""
        score = 0.0
        
        # Question marks indicate help/analysis intent
        if '?' in query_text and intent_type in [QueryType.HELP, QueryType.ANALYZE]:
            score += 0.3
        
        # Colons indicate specific commands
        if ':' in query_text and intent_type == QueryType.FIND:
            score += 0.4
        
        # Length considerations
        if len(query_text.split()) > 5 and intent_type == QueryType.ANALYZE:
            score += 0.2
        
        # Technical terms suggest graph/analysis
        technical_terms = ['dependency', 'relationship', 'connection', 'graph', 'network']
        if any(term in query_text for term in technical_terms) and intent_type == QueryType.GRAPH:
            score += 0.3
        
        return score
    
    def _init_intent_patterns(self) -> Dict[QueryType, List[str]]:
        """Initialize regex patterns for each intent type."""
        return {
            QueryType.SEARCH: [
                r'\b(search|find|look for|show me|get|what|where|when|how|why)\b',
                r'\b(search for|find|look for)\b.*\b(in|from|at)\b',
                r'\b(list|display|show)\b.*\b(all|every|each)\b',
            ],
            QueryType.FIND: [
                r'^find:',
                r'^exact:',
                r'^match:',
                r'\b(exactly|precisely|specifically)\b',
                r'\b(file|symbol|function|class|method)\s*:\s*',
            ],
            QueryType.ANALYZE: [
                r'\b(analyze|analysis|stats|statistics|metrics|measure)\b',
                r'\b(how many|count|total|sum|average)\b',
                r'\b(complexity|performance|quality|health)\b',
                r'\b(report|overview|summary)\b',
            ],
            QueryType.GRAPH: [
                r'\b(graph|relationship|connection|dependency|link)\b',
                r'\b(call graph|dependency graph|inheritance)\b',
                r'\b(connected to|related to|depends on|uses)\b',
                r'\b(traverse|path|route|flow)\b',
            ],
            QueryType.HELP: [
                r'\b(help|how to|what is|explain|describe)\b',
                r'\b(tutorial|guide|documentation|manual)\b',
                r'\b(learn|understand|example)\b',
                r'\?$',
            ],
        }
    
    def _init_keyword_weights(self) -> Dict[QueryType, Dict[str, float]]:
        """Initialize keyword weights for each intent type."""
        return {
            QueryType.SEARCH: {
                'search': 1.0,
                'find': 0.9,
                'look': 0.7,
                'show': 0.8,
                'get': 0.8,
                'what': 0.6,
                'where': 0.6,
                'when': 0.5,
                'how': 0.6,
                'why': 0.5,
                'list': 0.7,
                'display': 0.7,
            },
            QueryType.FIND: {
                'find': 1.0,
                'exact': 0.9,
                'match': 0.9,
                'precisely': 0.8,
                'specifically': 0.8,
                'file': 0.7,
                'symbol': 0.7,
                'function': 0.6,
                'class': 0.6,
                'method': 0.6,
            },
            QueryType.ANALYZE: {
                'analyze': 1.0,
                'analysis': 0.9,
                'stats': 0.8,
                'statistics': 0.8,
                'metrics': 0.8,
                'measure': 0.7,
                'count': 0.7,
                'total': 0.6,
                'sum': 0.6,
                'average': 0.6,
                'complexity': 0.7,
                'performance': 0.7,
                'quality': 0.6,
                'health': 0.6,
                'report': 0.7,
                'overview': 0.7,
                'summary': 0.7,
            },
            QueryType.GRAPH: {
                'graph': 1.0,
                'relationship': 0.9,
                'connection': 0.8,
                'dependency': 0.9,
                'link': 0.7,
                'call': 0.6,
                'inheritance': 0.7,
                'connected': 0.7,
                'related': 0.7,
                'depends': 0.8,
                'uses': 0.7,
                'traverse': 0.8,
                'path': 0.7,
                'route': 0.6,
                'flow': 0.6,
            },
            QueryType.HELP: {
                'help': 1.0,
                'how': 0.7,
                'tutorial': 0.8,
                'guide': 0.8,
                'documentation': 0.8,
                'manual': 0.7,
                'learn': 0.7,
                'understand': 0.7,
                'explain': 0.8,
                'describe': 0.8,
                'what': 0.6,
                'example': 0.7,
            },
        }
    
    def _init_context_patterns(self) -> Dict[QueryType, List[Tuple[str, List[str]]]]:
        """Initialize context patterns for each intent type."""
        return {
            QueryType.SEARCH: [
                ('current_file', ['search', 'find', 'look']),
                ('selected_text', ['search', 'find', 'explain']),
            ],
            QueryType.FIND: [
                ('current_file', ['find', 'exact', 'match']),
                ('symbol_under_cursor', ['find', 'go to', 'navigate']),
            ],
            QueryType.ANALYZE: [
                ('current_file', ['analyze', 'stats', 'complexity']),
                ('selected_symbol', ['analyze', 'metrics', 'performance']),
            ],
            QueryType.GRAPH: [
                ('current_file', ['graph', 'relationship', 'dependency']),
                ('selected_symbol', ['graph', 'connection', 'call']),
            ],
            QueryType.HELP: [
                ('current_file', ['help', 'explain', 'understand']),
                ('error_message', ['help', 'fix', 'solve']),
            ],
        }


class MLIntentClassifier(IntentClassifier):
    """Machine learning based intent classifier (placeholder)."""
    
    def __init__(self) -> None:
        """Initialize ML intent classifier."""
        super().__init__()
        self.model = None  # Placeholder for ML model
        self.vectorizer = None  # Placeholder for text vectorizer
        self.is_trained = False
    
    def train(self, training_data: List[Tuple[str, QueryType]]) -> None:
        """Train the intent classifier."""
        try:
            # Placeholder for ML training
            # In practice, you'd use sklearn, transformers, etc.
            self.is_trained = True
            
        except Exception as e:
            raise QueryError(f"Intent classifier training failed: {str(e)}")
    
    def classify_intent(self, query_text: str, context: Dict = None) -> QueryType:
        """Classify intent using ML model."""
        if not self.is_trained:
            # Fall back to rule-based classification
            return super().classify_intent(query_text, context)
        
        try:
            # Placeholder for ML prediction
            # In practice, you'd vectorize and predict
            return QueryType.SEARCH
            
        except Exception as e:
            # Fall back to rule-based classification
            return super().classify_intent(query_text, context)
    
    def get_feature_importance(self, query_text: str) -> Dict[str, float]:
        """Get feature importance for classification."""
        # Placeholder for feature importance
        return {}
