"""
Result ranking implementation.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from memobase.core.interfaces import EmbeddingInterface
from memobase.core.models import MemoryUnit, Query


class ResultRanker:
    """Advanced result ranking with multiple signals."""
    
    def __init__(self, embedder: EmbeddingInterface = None) -> None:
        """Initialize result ranker.
        
        Args:
            embedder: Optional embedder for semantic similarity
        """
        self.embedder = embedder
        self.rank_signals = {
            'text_relevance': 0.3,
            'semantic_similarity': 0.25,
            'recency': 0.15,
            'popularity': 0.15,
            'symbol_type': 0.1,
            'file_type': 0.05
        }
    
    def rank_results(self, results: List[MemoryUnit], query: Query) -> List[MemoryUnit]:
        """Rank results by relevance."""
        try:
            scored_results = []
            
            for result in results:
                score = self._calculate_score(result, query)
                scored_results.append((result, score))
            
            # Sort by score (descending)
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            return [result for result, _ in scored_results]
            
        except Exception as e:
            # If ranking fails, return original order
            return results
    
    def rank_with_diversity(self, results: List[MemoryUnit], query: Query, 
                           diversity_factor: float = 0.3) -> List[MemoryUnit]:
        """Rank results with diversity consideration."""
        try:
            if not results:
                return results
            
            # First, get basic scores
            scored_results = []
            for result in results:
                score = self._calculate_score(result, query)
                scored_results.append((result, score))
            
            # Sort by initial score
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            # Apply diversity re-ranking
            diverse_results = []
            remaining_results = scored_results.copy()
            
            while remaining_results and len(diverse_results) < len(results):
                # Take the top result
                best_result, best_score = remaining_results.pop(0)
                diverse_results.append(best_result)
                
                # Reduce scores of similar results
                for i, (result, score) in enumerate(remaining_results):
                    similarity = self._calculate_similarity(best_result, result)
                    diversity_penalty = diversity_factor * similarity
                    remaining_results[i] = (result, score * (1.0 - diversity_penalty))
                
                # Re-sort remaining results
                remaining_results.sort(key=lambda x: x[1], reverse=True)
            
            return diverse_results
            
        except Exception as e:
            # If diversity ranking fails, return basic ranking
            return self.rank_results(results, query)
    
    def rank_by_recency(self, results: List[MemoryUnit]) -> List[MemoryUnit]:
        """Rank results by recency."""
        try:
            return sorted(results, key=lambda x: x.updated_at, reverse=True)
        except Exception:
            return results
    
    def rank_by_popularity(self, results: List[MemoryUnit]) -> List[MemoryUnit]:
        """Rank results by popularity (placeholder implementation)."""
        try:
            # In practice, you'd track access counts or other popularity metrics
            # For now, sort by size as a proxy
            return sorted(results, key=lambda x: len(x.content or ''), reverse=True)
        except Exception:
            return results
    
    def _calculate_score(self, result: MemoryUnit, query: Query) -> float:
        """Calculate relevance score for a result."""
        score = 0.0
        
        # Text relevance
        text_score = self._calculate_text_relevance(result, query.text)
        score += self.rank_signals['text_relevance'] * text_score
        
        # Semantic similarity
        if self.embedder and result.embeddings:
            semantic_score = self._calculate_semantic_similarity(result, query.text)
            score += self.rank_signals['semantic_similarity'] * semantic_score
        
        # Recency
        recency_score = self._calculate_recency_score(result)
        score += self.rank_signals['recency'] * recency_score
        
        # Popularity (placeholder)
        popularity_score = self._calculate_popularity_score(result)
        score += self.rank_signals['popularity'] * popularity_score
        
        # Symbol type bonus
        if result.symbol:
            symbol_score = self._calculate_symbol_type_score(result.symbol.symbol_type.value)
            score += self.rank_signals['symbol_type'] * symbol_score
        
        # File type bonus
        file_type_score = self._calculate_file_type_score(result)
        score += self.rank_signals['file_type'] * file_type_score
        
        return score
    
    def _calculate_text_relevance(self, result: MemoryUnit, query_text: str) -> float:
        """Calculate text relevance score."""
        if not result.content and not result.keywords:
            return 0.0
        
        query_terms = query_text.lower().split()
        relevance = 0.0
        
        # Check content matches
        if result.content:
            content_lower = result.content.lower()
            for term in query_terms:
                if term in content_lower:
                    relevance += 1.0
        
        # Check keyword matches
        for keyword in result.keywords:
            keyword_lower = keyword.lower()
            for term in query_terms:
                if term in keyword_lower:
                    relevance += 0.5
        
        # Normalize
        max_possible = len(query_terms) * 2  # Content + keywords
        return min(1.0, relevance / max_possible) if max_possible > 0 else 0.0
    
    def _calculate_semantic_similarity(self, result: MemoryUnit, query_text: str) -> float:
        """Calculate semantic similarity score."""
        try:
            query_embedding = self.embedder.embed(query_text)
            similarity = self.embedder.similarity(query_embedding, result.embeddings)
            return similarity
        except Exception:
            return 0.0
    
    def _calculate_recency_score(self, result: MemoryUnit) -> float:
        """Calculate recency score."""
        try:
            import datetime
            now = datetime.datetime.utcnow()
            age_days = (now - result.updated_at).days
            
            # Newer items get higher scores
            if age_days < 1:
                return 1.0
            elif age_days < 7:
                return 0.8
            elif age_days < 30:
                return 0.6
            elif age_days < 90:
                return 0.4
            else:
                return 0.2
        except Exception:
            return 0.5
    
    def _calculate_popularity_score(self, result: MemoryUnit) -> float:
        """Calculate popularity score (placeholder)."""
        # In practice, you'd use actual usage metrics
        # For now, use content length as a proxy
        try:
            content_length = len(result.content or '')
            if content_length > 1000:
                return 1.0
            elif content_length > 500:
                return 0.8
            elif content_length > 100:
                return 0.6
            else:
                return 0.4
        except Exception:
            return 0.5
    
    def _calculate_symbol_type_score(self, symbol_type: str) -> float:
        """Calculate symbol type relevance score."""
        # Different symbol types have different importance
        type_scores = {
            'class': 1.0,
            'function': 0.9,
            'method': 0.8,
            'interface': 0.85,
            'variable': 0.6,
            'constant': 0.7,
            'import': 0.5,
            'export': 0.5,
            'type': 0.7,
            'enum': 0.6,
            'namespace': 0.8,
            'module': 0.7,
            'unknown': 0.3
        }
        
        return type_scores.get(symbol_type, 0.3)
    
    def _calculate_file_type_score(self, result: MemoryUnit) -> float:
        """Calculate file type relevance score."""
        try:
            # Prefer certain file types
            file_type = result.metadata.get('file_type', '')
            type_scores = {
                'python': 1.0,
                'javascript': 0.9,
                'typescript': 0.9,
                'java': 0.8,
                'cpp': 0.8,
                'rust': 0.85,
                'go': 0.8,
                'c': 0.7,
                'ruby': 0.6,
                'php': 0.6,
                'unknown': 0.3
            }
            
            return type_scores.get(file_type, 0.3)
        except Exception:
            return 0.5
    
    def _calculate_similarity(self, result1: MemoryUnit, result2: MemoryUnit) -> float:
        """Calculate similarity between two results for diversity."""
        try:
            similarity = 0.0
            
            # Same file
            if result1.file_path == result2.file_path:
                similarity += 0.4
            
            # Same symbol type
            if (result1.symbol and result2.symbol and 
                result1.symbol.symbol_type == result2.symbol.symbol_type):
                similarity += 0.3
            
            # Similar content length
            len1 = len(result1.content or '')
            len2 = len(result2.content or '')
            if len1 > 0 and len2 > 0:
                length_ratio = min(len1, len2) / max(len1, len2)
                similarity += 0.3 * length_ratio
            
            return min(1.0, similarity)
        except Exception:
            return 0.0


class LearningRanker(ResultRanker):
    """Ranker that learns from user feedback."""
    
    def __init__(self, embedder: EmbeddingInterface = None) -> None:
        """Initialize learning ranker."""
        super().__init__(embedder)
        self.feedback_history = []
        self.signal_weights = self.rank_signals.copy()
    
    def add_feedback(self, query: str, results: List[MemoryUnit], 
                    clicked_results: List[MemoryUnit], position: int) -> None:
        """Add user feedback for learning."""
        feedback = {
            'query': query,
            'results': results,
            'clicked': clicked_results,
            'position': position,
            'timestamp': datetime.datetime.utcnow()
        }
        self.feedback_history.append(feedback)
        
        # Update weights based on feedback
        self._update_weights(feedback)
    
    def rank_results(self, results: List[MemoryUnit], query: Query) -> List[MemoryUnit]:
        """Rank results using learned weights."""
        # Temporarily use learned weights
        original_weights = self.rank_signals.copy()
        self.rank_signals = self.signal_weights.copy()
        
        try:
            ranked = super().rank_results(results, query)
            return ranked
        finally:
            # Restore original weights
            self.rank_signals = original_weights
    
    def _update_weights(self, feedback: Dict) -> None:
        """Update ranking weights based on feedback."""
        try:
            # Simple learning algorithm: boost signals that led to good results
            query = feedback['query']
            clicked = feedback['clicked']
            position = feedback['position']
            
            # Calculate position-based learning rate
            learning_rate = 0.1 * (1.0 - position / 10.0)  # Higher rate for top positions
            
            # Boost weights for successful signals
            for clicked_result in clicked:
                # Analyze what made this result good
                self._boost_result_signals(clicked_result, query, learning_rate)
            
        except Exception:
            pass  # Ignore learning errors
    
    def _boost_result_signals(self, result: MemoryUnit, query: str, learning_rate: float) -> None:
        """Boost weights for signals that contributed to a good result."""
        try:
            query_terms = query.lower().split()
            
            # Check which signals were strong
            signals = {}
            
            # Text relevance
            text_relevance = self._calculate_text_relevance(result, query)
            if text_relevance > 0.7:
                signals['text_relevance'] = text_relevance
            
            # Symbol type
            if result.symbol:
                symbol_score = self._calculate_symbol_type_score(result.symbol.symbol_type.value)
                if symbol_score > 0.8:
                    signals['symbol_type'] = symbol_score
            
            # File type
            file_score = self._calculate_file_type_score(result)
            if file_score > 0.8:
                signals['file_type'] = file_score
            
            # Update weights
            for signal, strength in signals.items():
                if signal in self.signal_weights:
                    self.signal_weights[signal] *= (1.0 + learning_rate * strength)
            
            # Normalize weights
            total_weight = sum(self.signal_weights.values())
            if total_weight > 0:
                for signal in self.signal_weights:
                    self.signal_weights[signal] /= total_weight
            
        except Exception:
            pass
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics."""
        return {
            'feedback_count': len(self.feedback_history),
            'current_weights': self.signal_weights,
            'weight_changes': {
                signal: {
                    'original': self.rank_signals[signal],
                    'current': self.signal_weights[signal],
                    'change': self.signal_weights[signal] - self.rank_signals[signal]
                }
                for signal in self.rank_signals
            }
        }
