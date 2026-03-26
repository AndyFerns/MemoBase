"""
Unit tests for graph module.
"""

import pytest

from memobase.core.models import Graph, MemoryUnit
from memobase.graph.builder import GraphBuilder
from memobase.graph.traversal import GraphTraversal
from memobase.graph.analyzer import GraphAnalyzer


class TestGraphBuilder:
    """Test graph builder."""
    
    def test_builder_creation(self):
        """Test builder initialization."""
        builder = GraphBuilder()
        assert builder is not None
    
    def test_build_empty_graph(self):
        """Test building empty graph."""
        builder = GraphBuilder()
        graph = builder.build_graph([], [])
        
        assert graph.id is not None
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0


class TestGraphTraversal:
    """Test graph traversal."""
    
    def test_traversal_creation(self):
        """Test traversal initialization."""
        graph = Graph(id="test", nodes={}, edges=[], adjacency_list={})
        traversal = GraphTraversal(graph)
        
        assert traversal.graph == graph


class TestGraphAnalyzer:
    """Test graph analyzer."""
    
    def test_analyzer_creation(self):
        """Test analyzer initialization."""
        graph = Graph(id="test", nodes={}, edges=[], adjacency_list={})
        analyzer = GraphAnalyzer(graph)
        
        assert analyzer.graph == graph
    
    def test_calculate_degree_centrality_empty(self):
        """Test centrality calculation on empty graph."""
        graph = Graph(id="test", nodes={}, edges=[], adjacency_list={})
        analyzer = GraphAnalyzer(graph)
        
        centrality = analyzer.calculate_degree_centrality()
        assert centrality == {}
    
    def test_calculate_density_empty(self):
        """Test density calculation on empty graph."""
        graph = Graph(id="test", nodes={}, edges=[], adjacency_list={})
        analyzer = GraphAnalyzer(graph)
        
        density = analyzer._calculate_density()
        assert density == 0.0
