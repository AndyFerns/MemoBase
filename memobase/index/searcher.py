"""
Index searcher implementation.
"""

from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple

from memobase.core.exceptions import IndexError
from memobase.core.interfaces import EmbeddingInterface
from memobase.core.models import Index, MemoryUnit, QueryType


class IndexSearcher:
    """Advanced search functionality for indices."""
    
    def __init__(self, embedder: EmbeddingInterface = None) -> None:
        """Initialize index searcher.
        
        Args:
            embedder: Optional embedder for semantic search
        """
        self.embedder = embedder
        self.query_cache = {}
    
    def search(self, index: Index, query: str, filters: Dict = None, limit: int = 10) -> List[str]:
        """Perform advanced search with filters."""
        try:
            # Process query
            processed_query = self._process_query(query)
            
            # Apply filters
            filtered_units = self._apply_filters(index, filters) if filters else None
            
            # Perform search based on query type
            if processed_query['type'] == QueryType.SEARCH:
                results = self._text_search(index, processed_query, filtered_units, limit)
            elif processed_query['type'] == QueryType.FIND:
                results = self._exact_search(index, processed_query, filtered_units, limit)
            else:
                results = self._text_search(index, processed_query, filtered_units, limit)
            
            return results
            
        except Exception as e:
            raise IndexError(f"Search failed: {str(e)}")
    
    def semantic_search(self, query: str, memory_units: Dict[str, MemoryUnit], limit: int = 10) -> List[str]:
        """Perform semantic search."""
        if not self.embedder:
            raise IndexError("Semantic search requires embedder")
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed(query)
            
            # Calculate similarities
            similarities = []
            for unit_id, unit in memory_units.items():
                if unit.embeddings:
                    similarity = self.embedder.similarity(query_embedding, unit.embeddings)
                    similarities.append((unit_id, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return [unit_id for unit_id, _ in similarities[:limit]]
            
        except Exception as e:
            raise IndexError(f"Semantic search failed: {str(e)}")
    
    def fuzzy_search(self, index: Index, query: str, max_distance: int = 2, limit: int = 10) -> List[str]:
        """Perform fuzzy search with edit distance."""
        try:
            query_terms = query.lower().split()
            results = []
            
            for term in query_terms:
                # Find similar terms in index
                similar_terms = self._find_similar_terms(index, term, max_distance)
                
                # Get unit IDs for similar terms
                for similar_term in similar_terms:
                    if similar_term in index.term_index:
                        results.extend(index.term_index[similar_term])
            
            # Remove duplicates and count occurrences
            result_counts = {}
            for unit_id in results:
                result_counts[unit_id] = result_counts.get(unit_id, 0) + 1
            
            # Sort by count (more matches = higher relevance)
            sorted_results = sorted(result_counts.items(), key=lambda x: x[1], reverse=True)
            
            return [unit_id for unit_id, _ in sorted_results[:limit]]
            
        except Exception as e:
            raise IndexError(f"Fuzzy search failed: {str(e)}")
    
    def regex_search(self, index: Index, pattern: str, limit: int = 10) -> List[str]:
        """Perform regex search."""
        try:
            # Compile regex pattern
            regex = re.compile(pattern, re.IGNORECASE)
            
            # Find matching terms
            matching_terms = []
            for term in index.term_index.keys():
                if regex.search(term):
                    matching_terms.append(term)
            
            # Get unit IDs for matching terms
            results = []
            for term in matching_terms:
                results.extend(index.term_index[term])
            
            # Remove duplicates and return limited results
            unique_results = list(set(results))
            return unique_results[:limit]
            
        except Exception as e:
            raise IndexError(f"Regex search failed: {str(e)}")
    
    def phrase_search(self, index: Index, phrase: str, limit: int = 10) -> List[str]:
        """Search for exact phrases."""
        try:
            # This is a simplified implementation
            # In practice, you'd need to store phrase positions
            
            # Split phrase into words
            words = phrase.lower().split()
            if len(words) < 2:
                return self.search(index, phrase, limit=limit)
            
            # Find documents containing all words
            candidate_sets = []
            for word in words:
                processed_word = self._process_term(word)
                if processed_word in index.term_index:
                    candidate_sets.append(set(index.term_index[processed_word]))
                else:
                    candidate_sets.append(set())
            
            # Find intersection (documents containing all words)
            if candidate_sets:
                candidates = set.intersection(*candidate_sets)
            else:
                candidates = set()
            
            # Return limited results
            return list(candidates)[:limit]
            
        except Exception as e:
            raise IndexError(f"Phrase search failed: {str(e)}")
    
    def autocomplete(self, index: Index, prefix: str, limit: int = 10) -> List[str]:
        """Autocomplete suggestions."""
        try:
            prefix_lower = prefix.lower()
            suggestions = []
            
            # Find terms starting with prefix
            for term in index.term_index.keys():
                if term.startswith(prefix_lower):
                    suggestions.append(term)
            
            # Sort by frequency (number of documents)
            suggestions_with_counts = []
            for term in suggestions:
                count = len(index.term_index[term])
                suggestions_with_counts.append((term, count))
            
            suggestions_with_counts.sort(key=lambda x: x[1], reverse=True)
            
            return [term for term, _ in suggestions_with_counts[:limit]]
            
        except Exception as e:
            raise IndexError(f"Autocomplete failed: {str(e)}")
    
    def get_suggestions(self, index: Index, query: str, limit: int = 5) -> List[str]:
        """Get search suggestions for misspelled queries."""
        try:
            query_terms = query.lower().split()
            suggestions = []
            
            for term in query_terms:
                # Find similar terms
                similar_terms = self._find_similar_terms(index, term, max_distance=1)
                
                # Get most frequent similar terms
                term_suggestions = []
                for similar_term in similar_terms[:3]:
                    count = len(index.term_index.get(similar_term, []))
                    term_suggestions.append((similar_term, count))
                
                term_suggestions.sort(key=lambda x: x[1], reverse=True)
                suggestions.extend([term for term, _ in term_suggestions])
            
            return suggestions[:limit]
            
        except Exception as e:
            raise IndexError(f"Failed to get suggestions: {str(e)}")
    
    def _process_query(self, query: str) -> Dict:
        """Process and classify query."""
        query_lower = query.lower().strip()
        
        # Determine query type
        if query_lower.startswith('find:'):
            return {
                'type': QueryType.FIND,
                'text': query_lower[5:].strip(),
                'original': query
            }
        elif query_lower.startswith('search:'):
            return {
                'type': QueryType.SEARCH,
                'text': query_lower[7:].strip(),
                'original': query
            }
        else:
            return {
                'type': QueryType.SEARCH,
                'text': query_lower,
                'original': query
            }
    
    def _apply_filters(self, index: Index, filters: Dict) -> Set[str]:
        """Apply filters to limit search scope."""
        filtered_units = set()
        
        # File path filter
        if 'file_path' in filters:
            file_pattern = filters['file_path'].lower()
            for file_path, unit_ids in index.file_index.items():
                if file_pattern in file_path.lower():
                    filtered_units.update(unit_ids)
        
        # Symbol type filter
        if 'symbol_type' in filters:
            symbol_type = filters['symbol_type']
            if symbol_type in index.symbol_index:
                filtered_units.update(index.symbol_index[symbol_type])
        
        # If no filters applied, return None (no filtering)
        if not filtered_units:
            return None
        
        return filtered_units
    
    def _text_search(self, index: Index, processed_query: Dict, filtered_units: Set[str] = None, limit: int = 10) -> List[str]:
        """Perform text search."""
        query_terms = processed_query['text'].split()
        scores = {}
        
        for term in query_terms:
            processed_term = self._process_term(term)
            if processed_term in index.term_index:
                for unit_id in index.term_index[processed_term]:
                    if filtered_units is None or unit_id in filtered_units:
                        scores[unit_id] = scores.get(unit_id, 0) + 1
        
        # Sort by score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [unit_id for unit_id, _ in sorted_results[:limit]]
    
    def _exact_search(self, index: Index, processed_query: Dict, filtered_units: Set[str] = None, limit: int = 10) -> List[str]:
        """Perform exact search."""
        query_text = processed_query['text']
        results = set()
        
        # Check symbol index for exact matches
        if query_text in index.symbol_index:
            results.update(index.symbol_index[query_text])
        
        # Check term index for exact matches
        if query_text in index.term_index:
            results.update(index.term_index[query_text])
        
        # Apply filters if needed
        if filtered_units:
            results = results.intersection(filtered_units)
        
        return list(results)[:limit]
    
    def _process_term(self, term: str) -> str:
        """Process a search term."""
        # Convert to lowercase and remove punctuation
        term = term.lower()
        term = re.sub(r'[^\w\s]', '', term)
        return term
    
    def _find_similar_terms(self, index: Index, term: str, max_distance: int = 2) -> List[str]:
        """Find terms similar to given term using edit distance."""
        similar_terms = []
        
        for index_term in index.term_index.keys():
            distance = self._edit_distance(term, index_term)
            if distance <= max_distance and distance > 0:
                similar_terms.append((index_term, distance))
        
        # Sort by distance (closer = better)
        similar_terms.sort(key=lambda x: x[1])
        
        return [term for term, _ in similar_terms[:10]]
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance."""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]


class HybridSearcher(IndexSearcher):
    """Hybrid searcher combining multiple search methods."""
    
    def __init__(self, embedder: EmbeddingInterface = None) -> None:
        """Initialize hybrid searcher."""
        super().__init__(embedder)
        self.weights = {
            'text': 0.4,
            'semantic': 0.3,
            'symbol': 0.2,
            'file': 0.1
        }
    
    def search(self, index: Index, query: str, filters: Dict = None, limit: int = 10) -> List[str]:
        """Perform hybrid search combining multiple methods."""
        try:
            # Get results from different search methods
            text_results = self._get_text_results(index, query, filters)
            semantic_results = self._get_semantic_results(query, filters) if self.embedder else []
            symbol_results = self._get_symbol_results(index, query, filters)
            file_results = self._get_file_results(index, query, filters)
            
            # Combine and weight results
            combined_scores = self._combine_results(
                text_results, semantic_results, symbol_results, file_results
            )
            
            # Sort by combined score
            sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            
            return [unit_id for unit_id, _ in sorted_results[:limit]]
            
        except Exception as e:
            raise IndexError(f"Hybrid search failed: {str(e)}")
    
    def _get_text_results(self, index: Index, query: str, filters: Dict = None) -> List[str]:
        """Get text search results."""
        return super().search(index, query, filters, limit=50)
    
    def _get_semantic_results(self, query: str, filters: Dict = None) -> List[str]:
        """Get semantic search results."""
        # This would require access to memory units with embeddings
        # For now, return empty list
        return []
    
    def _get_symbol_results(self, index: Index, query: str, filters: Dict = None) -> List[str]:
        """Get symbol search results."""
        results = set()
        query_lower = query.lower()
        
        # Search in symbol index
        for symbol, unit_ids in index.symbol_index.items():
            if query_lower in symbol.lower():
                results.update(unit_ids)
        
        return list(results)
    
    def _get_file_results(self, index: Index, query: str, filters: Dict = None) -> List[str]:
        """Get file-based search results."""
        results = set()
        query_lower = query.lower()
        
        # Search in file index
        for file_path, unit_ids in index.file_index.items():
            if query_lower in file_path.lower():
                results.update(unit_ids)
        
        return list(results)
    
    def _combine_results(self, text_results: List[str], semantic_results: List[str],
                        symbol_results: List[str], file_results: List[str]) -> Dict[str, float]:
        """Combine results from different search methods."""
        combined_scores = {}
        
        # Add text search scores
        for i, unit_id in enumerate(text_results):
            score = self.weights['text'] * (1.0 / (i + 1))
            combined_scores[unit_id] = combined_scores.get(unit_id, 0) + score
        
        # Add semantic search scores
        for i, unit_id in enumerate(semantic_results):
            score = self.weights['semantic'] * (1.0 / (i + 1))
            combined_scores[unit_id] = combined_scores.get(unit_id, 0) + score
        
        # Add symbol search scores
        for i, unit_id in enumerate(symbol_results):
            score = self.weights['symbol'] * (1.0 / (i + 1))
            combined_scores[unit_id] = combined_scores.get(unit_id, 0) + score
        
        # Add file search scores
        for i, unit_id in enumerate(file_results):
            score = self.weights['file'] * (1.0 / (i + 1))
            combined_scores[unit_id] = combined_scores.get(unit_id, 0) + score
        
        return combined_scores
