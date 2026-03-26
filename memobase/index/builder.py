"""
Index builder implementation.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from typing import Dict, List, Set

from memobase.core.exceptions import IndexError
from memobase.core.interfaces import EmbeddingInterface, IndexInterface
from memobase.core.models import Index, MemoryUnit


class IndexBuilder(IndexInterface):
    """Builds and maintains search indices."""
    
    def __init__(self, embedder: EmbeddingInterface) -> None:
        """Initialize index builder.
        
        Args:
            embedder: Embedding interface for semantic search
        """
        self.embedder = embedder
        self.stop_words = self._init_stop_words()
    
    def index(self, memory_units: List[MemoryUnit]) -> Index:
        """Create index from memory units."""
        try:
            index_id = hashlib.sha256(f"index_{datetime.utcnow().isoformat()}".encode()).hexdigest()
            
            # Initialize index structures
            term_index = defaultdict(set)
            symbol_index = defaultdict(set)
            file_index = defaultdict(set)
            
            # Process memory units
            for unit in memory_units:
                self._index_memory_unit(unit, term_index, symbol_index, file_index)
            
            # Create Index object
            index = Index(
                id=index_id,
                term_index=dict(term_index),
                symbol_index=dict(symbol_index),
                file_index=dict(file_index)
            )
            
            return index
            
        except Exception as e:
            raise IndexError(f"Failed to create index: {str(e)}")
    
    def update_index(self, index: Index, memory_units: List[MemoryUnit]) -> Index:
        """Update existing index with new memory units."""
        try:
            # Process new memory units
            for unit in memory_units:
                self._index_memory_unit(unit, index.term_index, index.symbol_index, index.file_index)
            
            # Update timestamp
            index.updated_at = datetime.utcnow()
            
            return index
            
        except Exception as e:
            raise IndexError(f"Failed to update index: {str(e)}")
    
    def search(self, index: Index, query: str, limit: int = 10) -> List[str]:
        """Search index for matching memory unit IDs."""
        try:
            # Process query
            query_terms = self._process_query(query)
            
            # Calculate scores
            scores = defaultdict(float)
            
            # Term-based search
            for term in query_terms:
                if term in index.term_index:
                    for unit_id in index.term_index[term]:
                        scores[unit_id] += self._calculate_term_score(term, unit_id, index)
            
            # Symbol-based search
            if query_terms:
                for term in query_terms:
                    if term in index.symbol_index:
                        for unit_id in index.symbol_index[term]:
                            scores[unit_id] += self._calculate_symbol_score(term, unit_id, index)
            
            # Sort by score and return top results
            sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return [unit_id for unit_id, _ in sorted_results[:limit]]
            
        except Exception as e:
            raise IndexError(f"Failed to search index: {str(e)}")
    
    def get_term_frequency(self, index: Index, term: str) -> Dict[str, int]:
        """Get term frequency across all documents."""
        try:
            frequencies = {}
            
            if term in index.term_index:
                for unit_id in index.term_index[term]:
                    # In practice, you'd store actual term frequencies
                    # For now, we'll use a simple presence indicator
                    frequencies[unit_id] = 1
            
            return frequencies
            
        except Exception as e:
            raise IndexError(f"Failed to get term frequency: {str(e)}")
    
    async def index_async(self, memory_units: List[MemoryUnit]) -> Index:
        """Async version of index."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.index, memory_units)
    
    def _index_memory_unit(self, unit: MemoryUnit, term_index: Dict, symbol_index: Dict, file_index: Dict) -> None:
        """Index a single memory unit."""
        # Index file path
        file_key = str(unit.file_path)
        if file_key not in file_index:
            file_index[file_key] = set()
        file_index[file_key].add(unit.id)
        
        # Index keywords
        for keyword in unit.keywords:
            processed_keyword = self._process_term(keyword)
            if processed_keyword and processed_keyword not in self.stop_words:
                term_index[processed_keyword].add(unit.id)
        
        # Index content terms
        if unit.content:
            content_terms = self._extract_content_terms(unit.content)
            for term in content_terms:
                if term not in self.stop_words:
                    term_index[term].add(unit.id)
        
        # Index symbol information
        if unit.symbol:
            # Index symbol name
            symbol_name = self._process_term(unit.symbol.name)
            if symbol_name:
                symbol_index[symbol_name].add(unit.id)
            
            # Index symbol type
            symbol_type = unit.symbol.symbol_type.value
            symbol_index[symbol_type].add(unit.id)
            
            # Index parameters
            for param in unit.symbol.parameters:
                param_term = self._process_term(param)
                if param_term:
                    symbol_index[param_term].add(unit.id)
    
    def _process_query(self, query: str) -> List[str]:
        """Process search query into terms."""
        # Convert to lowercase and split
        terms = query.lower().split()
        
        # Process each term
        processed_terms = []
        for term in terms:
            processed = self._process_term(term)
            if processed and processed not in self.stop_words:
                processed_terms.append(processed)
        
        return processed_terms
    
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
    
    def _extract_content_terms(self, content: str) -> List[str]:
        """Extract terms from content."""
        import re
        
        # Split on word boundaries
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Process and filter terms
        terms = []
        for word in words:
            processed = self._simple_stem(word)
            if processed and len(processed) > 2 and processed not in self.stop_words:
                terms.append(processed)
        
        return terms
    
    def _simple_stem(self, word: str) -> str:
        """Simple stemming implementation."""
        # Remove common suffixes
        suffixes = ['ing', 'ed', 'er', 'est', 'ly', 'tion', 's', 'es']
        
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        
        return word
    
    def _calculate_term_score(self, term: str, unit_id: str, index: Index) -> float:
        """Calculate term relevance score."""
        # Simple TF-IDF-like scoring
        df = len(index.term_index.get(term, set()))  # Document frequency
        idf = math.log(len(index.term_index) / (df + 1)) if df > 0 else 0
        
        # In practice, you'd use actual term frequency
        tf = 1.0  # Placeholder
        
        return tf * idf
    
    def _calculate_symbol_score(self, symbol: str, unit_id: str, index: Index) -> float:
        """Calculate symbol relevance score."""
        # Symbol matches get higher weight
        df = len(index.symbol_index.get(symbol, set()))  # Document frequency
        idf = math.log(len(index.symbol_index) / (df + 1)) if df > 0 else 0
        
        return 2.0 * idf  # Higher weight for symbol matches
    
    def _init_stop_words(self) -> Set[str]:
        """Initialize stop words."""
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if',
            'up', 'out', 'many', 'then', 'them', 'can', 'would', 'there',
            'all', 'so', 'also', 'her', 'much', 'more', 'very', 'when',
            'make', 'like', 'no', 'just', 'him', 'know', 'take', 'people',
            'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see',
            'other', 'than', 'then', 'now', 'look', 'only', 'come', 'over',
            'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our',
            'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because',
            'any', 'these', 'give', 'day', 'most', 'us', 'is', 'was', 'are',
            'been', 'being', 'did', 'do', 'does', 'had', 'has', 'have',
            'may', 'might', 'must', 'shall', 'should', 'will', 'would',
        }


class SemanticIndexBuilder(IndexBuilder):
    """Index builder with semantic search capabilities."""
    
    def __init__(self, embedder: EmbeddingInterface) -> None:
        """Initialize semantic index builder."""
        super().__init__(embedder)
        self.embedding_index = {}  # unit_id -> embedding
    
    def index(self, memory_units: List[MemoryUnit]) -> Index:
        """Create index with semantic search."""
        # Create base index
        index = super().index(memory_units)
        
        # Add embeddings
        for unit in memory_units:
            if unit.embeddings:
                self.embedding_index[unit.id] = unit.embeddings
        
        return index
    
    def search(self, index: Index, query: str, limit: int = 10) -> List[str]:
        """Search with semantic similarity."""
        # Get base search results
        base_results = super().search(index, query, limit * 2)  # Get more for re-ranking
        
        # Generate query embedding
        query_embedding = self.embedder.embed(query)
        
        # Calculate semantic similarities
        semantic_scores = {}
        for unit_id in base_results:
            if unit_id in self.embedding_index:
                similarity = self.embedder.similarity(query_embedding, self.embedding_index[unit_id])
                semantic_scores[unit_id] = similarity
        
        # Combine with base scores (simplified)
        # In practice, you'd want more sophisticated ranking
        combined_scores = {}
        for unit_id in base_results:
            base_score = 1.0 / (base_results.index(unit_id) + 1)  # Simple ranking score
            semantic_score = semantic_scores.get(unit_id, 0.0)
            combined_scores[unit_id] = 0.7 * base_score + 0.3 * semantic_score
        
        # Sort and return top results
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return [unit_id for unit_id, _ in sorted_results[:limit]]
    
    def semantic_search(self, query: str, limit: int = 10) -> List[str]:
        """Pure semantic search."""
        try:
            query_embedding = self.embedder.embed(query)
            
            # Calculate similarities
            similarities = []
            for unit_id, embedding in self.embedding_index.items():
                similarity = self.embedder.similarity(query_embedding, embedding)
                similarities.append((unit_id, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return [unit_id for unit_id, _ in similarities[:limit]]
            
        except Exception as e:
            raise IndexError(f"Failed to perform semantic search: {str(e)}")
    
    def find_similar_units(self, unit_id: str, limit: int = 10) -> List[str]:
        """Find units similar to given unit."""
        try:
            if unit_id not in self.embedding_index:
                return []
            
            target_embedding = self.embedding_index[unit_id]
            
            # Calculate similarities
            similarities = []
            for other_id, embedding in self.embedding_index.items():
                if other_id != unit_id:
                    similarity = self.embedder.similarity(target_embedding, embedding)
                    similarities.append((other_id, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return [other_id for other_id, _ in similarities[:limit]]
            
        except Exception as e:
            raise IndexError(f"Failed to find similar units: {str(e)}")


class IncrementalIndexBuilder(IndexBuilder):
    """Index builder with incremental updates."""
    
    def __init__(self, embedder: EmbeddingInterface) -> None:
        """Initialize incremental index builder."""
        super().__init__(embedder)
        self.unit_versions = {}  # unit_id -> version
    
    def update_index_incremental(self, index: Index, added_units: List[MemoryUnit], 
                               removed_unit_ids: List[str], modified_units: List[MemoryUnit]) -> Index:
        """Update index incrementally."""
        try:
            # Remove old units
            for unit_id in removed_unit_ids:
                self._remove_unit_from_index(index, unit_id)
            
            # Remove old versions of modified units
            for unit in modified_units:
                self._remove_unit_from_index(index, unit.id)
            
            # Add new and modified units
            all_new_units = added_units + modified_units
            for unit in all_new_units:
                self._index_memory_unit(unit, index.term_index, index.symbol_index, index.file_index)
                self.unit_versions[unit.id] = unit.updated_at
            
            # Update timestamp
            index.updated_at = datetime.utcnow()
            
            return index
            
        except Exception as e:
            raise IndexError(f"Failed to update index incrementally: {str(e)}")
    
    def _remove_unit_from_index(self, index: Index, unit_id: str) -> None:
        """Remove unit from all indices."""
        # Remove from term index
        for term, unit_set in index.term_index.items():
            unit_set.discard(unit_id)
        
        # Remove from symbol index
        for symbol, unit_set in index.symbol_index.items():
            unit_set.discard(unit_id)
        
        # Remove from file index
        for file_path, unit_set in index.file_index.items():
            unit_set.discard(unit_id)
        
        # Clean up empty sets
        index.term_index = {k: v for k, v in index.term_index.items() if v}
        index.symbol_index = {k: v for k, v in index.symbol_index.items() if v}
        index.file_index = {k: v for k, v in index.file_index.items() if v}
        
        # Remove from versions
        self.unit_versions.pop(unit_id, None)
