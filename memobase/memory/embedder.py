"""
Text embedding implementation.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
from concurrent.futures import ProcessPoolExecutor
from typing import List

from memobase.core.interfaces import EmbeddingInterface


class TextEmbedder(EmbeddingInterface):
    """Simple text embedder using TF-IDF and hashing."""
    
    def __init__(self, embedding_dim: int = 384) -> None:
        """Initialize text embedder.
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        self.embedding_dim = embedding_dim
        self.vocab_size = 10000  # Approximate vocabulary size
        self.idf_cache = {}
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not text:
            return [0.0] * self.embedding_dim
        
        # Tokenize text
        tokens = self._tokenize(text)
        
        # Calculate TF-IDF weights
        tfidf_weights = self._calculate_tfidf(tokens)
        
        # Generate embedding using hashing trick
        embedding = [0.0] * self.embedding_dim
        
        for token, weight in tfidf_weights.items():
            # Hash token to multiple dimensions
            hash_values = self._hash_token(token)
            
            for i, hash_val in enumerate(hash_values):
                if hash_val < self.embedding_dim:
                    # Use both positive and negative weights for sparsity
                    if i % 2 == 0:
                        embedding[hash_val] += weight
                    else:
                        embedding[hash_val] -= weight
        
        # Normalize embedding
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            embedding = self.embed(text)
            embeddings.append(embedding)
        return embeddings
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have same dimension")
        
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(a * a for a in embedding1))
        norm2 = math.sqrt(sum(b * b for b in embedding2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def embed_async(self, text: str) -> List[float]:
        """Async version of embed."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.embed, text)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words and subwords."""
        import re
        
        # Convert to lowercase
        text = text.lower()
        
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text)
        
        # Generate subwords for long tokens
        subword_tokens = []
        for token in tokens:
            if len(token) > 6:
                # Generate subwords using character n-grams
                subwords = self._generate_subwords(token)
                subword_tokens.extend(subwords)
            else:
                subword_tokens.append(token)
        
        return subword_tokens
    
    def _generate_subwords(self, token: str, min_length: int = 3, max_length: int = 6) -> List[str]:
        """Generate subwords from token."""
        subwords = []
        
        # Add the full token
        subwords.append(token)
        
        # Add character n-grams
        for length in range(min_length, min(max_length + 1, len(token))):
            for i in range(len(token) - length + 1):
                subword = token[i:i + length]
                subwords.append(subword)
        
        return subwords
    
    def _calculate_tfidf(self, tokens: List[str]) -> dict:
        """Calculate TF-IDF weights for tokens."""
        # Calculate term frequency
        tf = {}
        total_tokens = len(tokens)
        
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        
        # Normalize TF
        for token in tf:
            tf[token] = tf[token] / total_tokens
        
        # Use approximate IDF (simplified)
        tfidf = {}
        for token, tf_score in tf.items():
            # Approximate IDF based on token length and character frequency
            idf_score = self._approximate_idf(token)
            tfidf[token] = tf_score * idf_score
        
        return tfidf
    
    def _approximate_idf(self, token: str) -> float:
        """Approximate IDF score for token."""
        if token in self.idf_cache:
            return self.idf_cache[token]
        
        # Guard: empty token
        if not token or token.strip() == "":
            return 0.0
        
        # Simple heuristic: longer and less common characters get higher IDF
        char_frequency = self._estimate_char_frequency(token)
        
        # Clamp to safe range (IMPORTANT)
        char_frequency = max(-0.99, char_frequency)  # prevents denominator = 0
        
        length_factor = min(2.0, len(token) / 3.0)
        denominator = 1.0 + char_frequency
        
        # Extra safety (paranoid guard)
        if denominator <= 0:
            denominator = 1e-6
        
        try:
            idf = 1.0 + math.log(length_factor / denominator)
        except (ValueError, ZeroDivisionError):
            idf = 0.0
        
        self.idf_cache[token] = idf
        
        return idf
    
    def _estimate_char_frequency(self, token: str) -> float:
        """Estimate character frequency for IDF calculation."""
        # Common characters have lower frequency score
        common_chars = set('etaoinshrdlu')
        uncommon_chars = set('zqxjkvbpygfw')
        
        common_count = sum(1 for c in token if c in common_chars)
        uncommon_count = sum(1 for c in token if c in uncommon_chars)
        
        # Normalize by token length
        if len(token) == 0:
            return 0.0
        
        return (common_count - uncommon_count) / len(token)
    
    def _hash_token(self, token: str) -> List[int]:
        """Hash token to multiple dimensions."""
        hash_values = []
        
        # Use different hash functions for different dimensions
        hash_functions = [
            lambda x: int(hashlib.md5(x.encode()).hexdigest(), 16),
            lambda x: int(hashlib.sha1(x.encode()).hexdigest(), 16),
            lambda x: int(hashlib.sha256(x.encode()).hexdigest(), 16),
        ]
        
        for i, hash_func in enumerate(hash_functions):
            hash_val = hash_func(f"{token}_{i}")
            # Modulo by embedding dimension to get index
            hash_values.append(hash_val % self.embedding_dim)
        
        return hash_values


class AdvancedEmbedder(EmbeddingInterface):
    """Advanced embedder with semantic features."""
    
    def __init__(self, base_embedder: TextEmbedder) -> None:
        """Initialize advanced embedder.
        
        Args:
            base_embedder: Base text embedder
        """
        self.base_embedder = base_embedder
        self.semantic_patterns = self._init_semantic_patterns()
    
    def embed(self, text: str) -> List[float]:
        """Generate enhanced embedding with semantic features."""
        # Get base embedding
        base_embedding = self.base_embedder.embed(text)
        
        # Add semantic features
        semantic_features = self._extract_semantic_features(text)
        
        # Combine embeddings
        combined_embedding = base_embedding + semantic_features
        
        # Ensure correct dimension
        if len(combined_embedding) > self.base_embedder.embedding_dim:
            combined_embedding = combined_embedding[:self.base_embedder.embedding_dim]
        elif len(combined_embedding) < self.base_embedder.embedding_dim:
            combined_embedding.extend([0.0] * (self.base_embedder.embedding_dim - len(combined_embedding)))
        
        return combined_embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed(text) for text in texts]
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate similarity between embeddings."""
        return self.base_embedder.similarity(embedding1, embedding2)
    
    async def embed_async(self, text: str) -> List[float]:
        """Async version of embed."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.embed, text)
    
    def _extract_semantic_features(self, text: str) -> List[float]:
        """Extract semantic features from text."""
        features = []
        
        # Code-specific features
        features.append(self._has_functions(text))
        features.append(self._has_classes(text))
        features.append(self._has_imports(text))
        features.append(self._has_comments(text))
        features.append(self._code_complexity(text))
        features.append(self._identifier_density(text))
        features.append(self._keyword_density(text))
        
        return features
    
    def _has_functions(self, text: str) -> float:
        """Check if text contains function definitions."""
        return 1.0 if any(keyword in text.lower() for keyword in ['def ', 'function ', 'func ']) else 0.0
    
    def _has_classes(self, text: str) -> float:
        """Check if text contains class definitions."""
        return 1.0 if any(keyword in text.lower() for keyword in ['class ', 'interface ', 'struct ']) else 0.0
    
    def _has_imports(self, text: str) -> float:
        """Check if text contains import statements."""
        return 1.0 if any(keyword in text.lower() for keyword in ['import ', 'from ', 'using ', 'include ']) else 0.0
    
    def _has_comments(self, text: str) -> float:
        """Check if text contains comments."""
        comment_patterns = ['#', '//', '/*', '*', '<!--']
        return 1.0 if any(pattern in text for pattern in comment_patterns) else 0.0
    
    def _code_complexity(self, text: str) -> float:
        """Estimate code complexity."""
        complexity_keywords = ['if', 'else', 'for', 'while', 'switch', 'try', 'catch']
        count = sum(text.lower().count(keyword) for keyword in complexity_keywords)
        return min(1.0, count / 10.0)  # Normalize to 0-1
    
    def _identifier_density(self, text: str) -> float:
        """Calculate identifier density."""
        import re
        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text)
        return min(1.0, len(identifiers) / max(1, len(text.split())))
    
    def _keyword_density(self, text: str) -> float:
        """Calculate programming keyword density."""
        keywords = ['def', 'class', 'import', 'return', 'if', 'else', 'for', 'while', 'try', 'except']
        keyword_count = sum(text.lower().count(keyword) for keyword in keywords)
        return min(1.0, keyword_count / max(1, len(text.split())))
    
    def _init_semantic_patterns(self) -> dict:
        """Initialize semantic patterns for feature extraction."""
        return {
            'function_patterns': [r'\bdef\s+\w+\s*\(', r'\bfunction\s+\w+\s*\(', r'\bfunc\s+\w+\s*\('],
            'class_patterns': [r'\bclass\s+\w+', r'\binterface\s+\w+', r'\bstruct\s+\w+'],
            'import_patterns': [r'\bimport\s+', r'\bfrom\s+', r'\busing\s+', r'\binclude\s+'],
        }
