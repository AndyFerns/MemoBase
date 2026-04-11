"""
Query processor implementation.
"""

from __future__ import annotations

import asyncio
import re
import time
import logging

from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from typing import Dict, List, Optional

from memobase.core.exceptions import QueryError
from memobase.core.interfaces import QueryInterface
from memobase.core.models import Graph, Index, MemoryUnit, Query, QueryType, Response


class QueryProcessor(QueryInterface):
    """Main query processor with intent classification and retrieval."""
    
    def __init__(self, config=None) -> None:
        """Initialize query processor."""
        self.config = config
        self.query_history = []
        self.performance_stats = {
            'total_queries': 0,
            'avg_latency_ms': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
        }
        self.query_cache = {}
    
    def query(self, query: Query, index: Index, graph: Graph) -> Response:
        """Execute query against index and graph."""
        try:
            start_time = time.time()
            
            # Check cache first
            cache_key = self._generate_cache_key(query)
            if cache_key in self.query_cache:
                cached_response = self.query_cache[cache_key]
                self.performance_stats['cache_hits'] += 1
                return cached_response
            
            self.performance_stats['cache_misses'] += 1
            
            # Execute query based on type
            if query.query_type == QueryType.SEARCH:
                results = self._execute_search_query(query, index, graph)
            elif query.query_type == QueryType.FIND:
                results = self._execute_find_query(query, index, graph)
            elif query.query_type == QueryType.ANALYZE:
                results = self._execute_analyze_query(query, index, graph)
            elif query.query_type == QueryType.GRAPH:
                results = self._execute_graph_query(query, index, graph)
            else:
                results = self._execute_default_query(query, index, graph)
            
            # Apply filters
            filtered_results = self._apply_filters(results, query.filters)
            
            # Apply limit and offset
            paginated_results = self._apply_pagination(filtered_results, query.limit, query.offset)
            
            # Create response
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            response = Response(
                query_id=query.id,
                results=paginated_results,
                total_count=len(filtered_results),
                execution_time_ms=execution_time,
                metadata={
                    'query_type': query.query_type.value,
                    'cache_hit': False,
                    'filters_applied': len(query.filters) > 0,
                }
            )
            
            # Cache response
            self.query_cache[cache_key] = response
            
            # Update stats
            self._update_performance_stats(execution_time)
            self.query_history.append({
                'query': query,
                'response': response,
                'timestamp': datetime.utcnow(),
            })
            
            return response
            
        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}")
    
    def classify_intent(self, query_text: str) -> str:
        """Classify query intent."""
        try:
            query_lower = query_text.lower().strip()
            
            # Check for explicit intent keywords
            intent_patterns = {
                QueryType.SEARCH: ['search', 'find', 'look for', 'show me'],
                QueryType.FIND: ['find:', 'exact:', 'match:'],
                QueryType.ANALYZE: ['analyze', 'analysis', 'stats', 'metrics'],
                QueryType.GRAPH: ['graph', 'relationships', 'connections', 'dependencies'],
                QueryType.HELP: ['help', 'how to', 'what is', 'explain'],
            }
            
            for query_type, patterns in intent_patterns.items():
                for pattern in patterns:
                    if pattern in query_lower:
                        return query_type.value
            
            # Default to search
            return QueryType.SEARCH.value
            
        except Exception as e:
            raise QueryError(f"Intent classification failed: {str(e)}")
    
    def extract_filters(self, query_text: str) -> Dict[str, any]:
        """Extract filters from query text."""
        try:
            filters = {}
            
            # File path filter
            file_pattern = r'file:([^\s]+)'
            file_matches = re.findall(file_pattern, query_text)
            if file_matches:
                filters['file_path'] = file_matches[0]
            
            # Symbol type filter
            type_pattern = r'type:([^\s]+)'
            type_matches = re.findall(type_pattern, query_text)
            if type_matches:
                filters['symbol_type'] = type_matches[0]
            
            # Language filter
            lang_pattern = r'lang:([^\s]+)'
            lang_matches = re.findall(lang_pattern, query_text)
            if lang_matches:
                filters['language'] = lang_matches[0]
            
            # Date range filter
            date_pattern = r'date:(\d{4}-\d{2}-\d{2})'
            date_matches = re.findall(date_pattern, query_text)
            if date_matches:
                filters['date'] = date_matches[0]
            
            return filters
            
        except Exception as e:
            raise QueryError(f"Filter extraction failed: {str(e)}")
    
    def rank_results(self, results: List[MemoryUnit], query: Query) -> List[MemoryUnit]:
        """Rank results by relevance."""
        try:
            if not results:
                return results
            
            # Calculate relevance scores
            scored_results = []
            query_terms = query.text.lower().split()
            
            for result in results:
                score = 0.0
                
                # Text relevance
                if result.content:
                    content_lower = result.content.lower()
                    for term in query_terms:
                        if term in content_lower:
                            score += 1.0
                
                # Keyword relevance
                for keyword in result.keywords:
                    keyword_lower = keyword.lower()
                    for term in query_terms:
                        if term in keyword_lower:
                            score += 0.5
                
                # Symbol name relevance
                if result.symbol:
                    symbol_name_lower = result.symbol.name.lower()
                    for term in query_terms:
                        if term in symbol_name_lower:
                            score += 2.0  # Higher weight for symbol matches
                
                # File path relevance
                file_path_lower = str(result.file_path).lower()
                for term in query_terms:
                    if term in file_path_lower:
                        score += 0.3
                
                scored_results.append((result, score))
            
            # Sort by score (descending)
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            return [result for result, _ in scored_results]
            
        except Exception as e:
            raise QueryError(f"Result ranking failed: {str(e)}")
    
    async def query_async(self, query: Query, index: Index, graph: Graph) -> Response:
        """Async version of query."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.query, query, index, graph)
        
    def _load_memory_unit(self, unit_id: str) -> Optional[MemoryUnit]:
        """Load memory unit from storage."""
        try:
            from memobase.storage.file_storage import FileStorage
            from memobase.core.models import MemoryUnit
            from pathlib import Path

            storage = FileStorage(Path(".memobase/data"))
            data = storage.load(f"memory_unit:{unit_id}")

            if data:
                return MemoryUnit.from_dict(data)

            return None
        except Exception:
            return None
        
    def _simple_stem(self, word: str) -> str:
        suffixes = ['ing', 'ed', 'er', 'est', 'ly', 'tion', 's', 'es']

        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]

        return word
        
    def _process_term(self, term: str) -> str:
        """Process a single term."""
        # Convert to lowercase
        term = term.lower()
        
        # Remove punctuation
        import re
        term = re.sub(r'[^\w\s]', '', term)
        
        # Normalize (simple stemming)
        term = self._simple_stem(term)
        
        return term
    
    def _execute_search_query(self, query: Query, index: Index, graph: Graph) -> List[MemoryUnit]:
        """Execute search query."""
        try:
            # Get matching unit IDs from index
            matching_ids = set()
            
            # Search term index
            query_terms = query.text.lower().split()
            for term in query_terms:
                processed = self._process_term(term)
                if processed in index.term_index:
                    matching_ids.update(index.term_index[processed])
                    
                print("[DEBUG QUERY] term:", term, "processed:", processed)
                print("[DEBUG QUERY] available keys sample:", list(index.term_index.keys())[:10])
            
            # Search symbol index
            for term in query_terms:
                if term in index.symbol_index:
                    matching_ids.update(index.symbol_index[term])
            
            # Get memory units
            results = []
            for unit_id in matching_ids:
                try:
                    unit_data = self._load_memory_unit(unit_id)
                    if unit_data:
                        results.append(unit_data)
                except Exception as e:
                    raise QueryError(f"Failed to load memory unit {unit_id}: {str(e)}")
            
            return results
            
        except Exception as e:
            raise QueryError(f"Search query execution failed: {str(e)}")
    
    def _execute_find_query(self, query: Query, index: Index, graph: Graph) -> List[MemoryUnit]:
        """Execute exact find query."""
        try:
            query_text = query.text.lower()
            matching_ids = set()
            
            # Exact symbol match
            if query_text in index.symbol_index:
                matching_ids.update(index.symbol_index[query_text])
            
            # Exact term match
            if query_text in index.term_index:
                matching_ids.update(index.term_index[query_text])
            
            # Get memory units
            results = []
            for unit_id in matching_ids:
                # In practice, you'd retrieve from storage
                pass
            
            return results
            
        except Exception as e:
            raise QueryError(f"Find query execution failed: {str(e)}")
    
    def _execute_analyze_query(self, query: Query, index: Index, graph: Graph) -> List[MemoryUnit]:
        """Execute analysis query."""
        try:
            # Analysis queries might return aggregated results
            # For now, return empty results
            return []
            
        except Exception as e:
            raise QueryError(f"Analysis query execution failed: {str(e)}")
    
    def _execute_graph_query(self, query: Query, index: Index, graph: Graph) -> List[MemoryUnit]:
        """Execute graph query."""
        try:
            # Graph queries might return relationship information
            # For now, return empty results
            return []
            
        except Exception as e:
            raise QueryError(f"Graph query execution failed: {str(e)}")
    
    def _execute_default_query(self, query: Query, index: Index, graph: Graph) -> List[MemoryUnit]:
        """Execute default query (search)."""
        return self._execute_search_query(query, index, graph)
    
    def _apply_filters(self, results: List[MemoryUnit], filters: Dict[str, any]) -> List[MemoryUnit]:
        """Apply filters to results."""
        if not filters:
            return results
        
        filtered_results = []
        
        for result in results:
            matches_all = True
            
            # File path filter
            if 'file_path' in filters:
                file_pattern = filters['file_path'].lower()
                if file_pattern not in str(result.file_path).lower():
                    matches_all = False
            
            # Symbol type filter
            if 'symbol_type' in filters and result.symbol:
                if result.symbol.symbol_type.value != filters['symbol_type']:
                    matches_all = False
            
            # Language filter
            if 'language' in filters:
                language = filters['language'].lower()
                file_type = result.metadata.get('file_type', '').lower()
                if language not in file_type:
                    matches_all = False
            
            if matches_all:
                filtered_results.append(result)
        
        return filtered_results
    
    def _apply_pagination(self, results: List[MemoryUnit], limit: int, offset: int) -> List[MemoryUnit]:
        """Apply limit and offset to results."""
        start = offset
        end = start + limit if limit > 0 else len(results)
        return results[start:end]
    
    def _generate_cache_key(self, query: Query) -> str:
        """Generate cache key for query."""
        import hashlib
        
        key_data = f"{query.query_type.value}:{query.text}:{query.filters}:{query.limit}:{query.offset}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_performance_stats(self, execution_time_ms: float) -> None:
        """Update performance statistics."""
        self.performance_stats['total_queries'] += 1
        
        # Update average latency
        total = self.performance_stats['total_queries']
        current_avg = self.performance_stats['avg_latency_ms']
        self.performance_stats['avg_latency_ms'] = ((current_avg * (total - 1)) + execution_time_ms) / total
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Get performance statistics."""
        return self.performance_stats.copy()
    
    def clear_cache(self) -> None:
        """Clear query cache."""
        self.query_cache.clear()
    
    def get_query_history(self, limit: int = 10) -> List[Dict]:
        """Get recent query history."""
        return self.query_history[-limit:] if limit > 0 else self.query_history.copy()


class AdvancedQueryProcessor(QueryProcessor):
    """Advanced query processor with semantic search and learning."""
    
    def __init__(self, embedder=None) -> None:
        """Initialize advanced query processor."""
        super().__init__()
        self.embedder = embedder
        self.user_feedback = []
    
    def query(self, query: Query, index: Index, graph: Graph) -> Response:
        """Execute query with advanced features."""
        try:
            # Try semantic search if embedder is available
            if self.embedder and query.query_type == QueryType.SEARCH:
                return self._execute_semantic_query(query, index, graph)
            else:
                return super().query(query, index, graph)
                
        except Exception as e:
            raise QueryError(f"Advanced query execution failed: {str(e)}")
    
    def _execute_semantic_query(self, query: Query, index: Index, graph: Graph) -> Response:
        """Execute semantic search query."""
        try:
            start_time = time.time()
            
            # Generate query embedding
            query_embedding = self.embedder.embed(query.text)
            
            # Find similar memory units (placeholder implementation)
            # In practice, you'd compare with stored embeddings
            results = []
            
            # Create response
            execution_time = (time.time() - start_time) * 1000
            
            return Response(
                query_id=query.id,
                results=results,
                total_count=len(results),
                execution_time_ms=execution_time,
                metadata={
                    'query_type': query.query_type.value,
                    'semantic_search': True,
                }
            )
            
        except Exception as e:
            raise QueryError(f"Semantic query execution failed: {str(e)}")
    
    def add_feedback(self, query_id: str, relevance_scores: Dict[str, float]) -> None:
        """Add user feedback for learning."""
        feedback = {
            'query_id': query_id,
            'relevance_scores': relevance_scores,
            'timestamp': datetime.utcnow(),
        }
        self.user_feedback.append(feedback)
    
    def learn_from_feedback(self) -> None:
        """Learn from user feedback to improve ranking."""
        # Placeholder for learning algorithm
        # In practice, you'd use machine learning to improve ranking
        pass
