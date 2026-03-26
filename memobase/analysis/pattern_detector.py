"""
Pattern detector implementation.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from memobase.core.exceptions import QueryError
from memobase.core.models import MemoryUnit, SymbolType


class PatternDetector:
    """Detects design patterns, code smells, and architectural patterns."""
    
    def __init__(self) -> None:
        """Initialize pattern detector."""
        self.design_patterns = self._init_design_patterns()
        self.code_smells = self._init_code_smells()
        self.architectural_patterns = self._init_architectural_patterns()
    
    def detect_all_patterns(self, memory_units: List[MemoryUnit]) -> Dict[str, List[MemoryUnit]]:
        """Detect all types of patterns."""
        try:
            all_patterns = {}
            
            # Design patterns
            design_patterns = self.detect_design_patterns(memory_units)
            all_patterns.update(design_patterns)
            
            # Code smells
            code_smells = self.detect_code_smells(memory_units)
            all_patterns.update(code_smells)
            
            # Architectural patterns
            arch_patterns = self.detect_architectural_patterns(memory_units)
            all_patterns.update(arch_patterns)
            
            return all_patterns
            
        except Exception as e:
            raise QueryError(f"Pattern detection failed: {str(e)}")
    
    def detect_design_patterns(self, memory_units: List[MemoryUnit]) -> Dict[str, List[MemoryUnit]]:
        """Detect design patterns."""
        patterns = defaultdict(list)
        
        # Group units by file for pattern detection
        file_units = defaultdict(list)
        for unit in memory_units:
            file_units[str(unit.file_path)].append(unit)
        
        for file_path, units in file_units.items():
            # Singleton pattern
            singleton_units = self._detect_singleton_pattern(units)
            patterns['singleton'].extend(singleton_units)
            
            # Factory pattern
            factory_units = self._detect_factory_pattern(units)
            patterns['factory'].extend(factory_units)
            
            # Observer pattern
            observer_units = self._detect_observer_pattern(units)
            patterns['observer'].extend(observer_units)
            
            # Strategy pattern
            strategy_units = self._detect_strategy_pattern(units)
            patterns['strategy'].extend(strategy_units)
            
            # Adapter pattern
            adapter_units = self._detect_adapter_pattern(units)
            patterns['adapter'].extend(adapter_units)
            
            # Decorator pattern
            decorator_units = self._detect_decorator_pattern(units)
            patterns['decorator'].extend(decorator_units)
            
            # Command pattern
            command_units = self._detect_command_pattern(units)
            patterns['command'].extend(command_units)
        
        return dict(patterns)
    
    def detect_code_smells(self, memory_units: List[MemoryUnit]) -> Dict[str, List[MemoryUnit]]:
        """Detect code smells."""
        patterns = defaultdict(list)
        
        for unit in memory_units:
            # Long method
            if self._is_long_method(unit):
                patterns['long_method'].append(unit)
            
            # Large class
            if self._is_large_class(unit):
                patterns['large_class'].append(unit)
            
            # God class
            if self._is_god_class(unit):
                patterns['god_class'].append(unit)
            
            # Feature envy
            if self._has_feature_envy(unit, memory_units):
                patterns['feature_envy'].append(unit)
            
            # Data class
            if self._is_data_class(unit):
                patterns['data_class'].append(unit)
            
            # Lazy class
            if self._is_lazy_class(unit):
                patterns['lazy_class'].append(unit)
            
            # Shotgun surgery
            if self._has_shotgun_surgery(unit, memory_units):
                patterns['shotgun_surgery'].append(unit)
            
            # Duplicated code
            if self._has_duplicated_code(unit, memory_units):
                patterns['duplicated_code'].append(unit)
        
        return dict(patterns)
    
    def detect_architectural_patterns(self, memory_units: List[MemoryUnit]) -> Dict[str, List[MemoryUnit]]:
        """Detect architectural patterns."""
        patterns = defaultdict(list)
        
        # Group by file for architectural analysis
        file_units = defaultdict(list)
        for unit in memory_units:
            file_units[str(unit.file_path)].append(unit)
        
        # Layered architecture
        layered_units = self._detect_layered_architecture(file_units)
        patterns['layered_architecture'].extend(layered_units)
        
        # MVC pattern
        mvc_units = self._detect_mvc_pattern(file_units)
        patterns['mvc'].extend(mvc_units)
        
        # Repository pattern
        repo_units = self._detect_repository_pattern(memory_units)
        patterns['repository'].extend(repo_units)
        
        # Service layer
        service_units = self._detect_service_layer(memory_units)
        patterns['service_layer'].extend(service_units)
        
        # Controller pattern
        controller_units = self._detect_controller_pattern(memory_units)
        patterns['controller'].extend(controller_units)
        
        return dict(patterns)
    
    def _detect_singleton_pattern(self, units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect singleton pattern."""
        singleton_units = []
        
        for unit in units:
            if not unit.content or not unit.symbol:
                continue
            
            if unit.symbol.symbol_type == SymbolType.CLASS:
                content = unit.content.lower()
                
                # Check for singleton characteristics
                has_private_constructor = ('def __init__(self' in content and 
                                       '__new__' in content)
                has_static_instance = ('_instance' in content or 'instance' in content)
                has_get_instance = ('get_instance' in content or 'instance' in content)
                
                if has_private_constructor and has_static_instance and has_get_instance:
                    singleton_units.append(unit)
        
        return singleton_units
    
    def _detect_factory_pattern(self, units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect factory pattern."""
        factory_units = []
        
        for unit in units:
            if not unit.content or not unit.symbol:
                continue
            
            content = unit.content.lower()
            
            # Check for factory characteristics
            has_factory_name = ('factory' in unit.symbol.name.lower() or 
                              'create' in unit.symbol.name.lower())
            has_create_method = ('def create' in content or 'def build' in content)
            has_polymorphism = ('if' in content and 'return' in content and 
                               ('class' in content or 'type' in content))
            
            if has_factory_name and (has_create_method or has_polymorphism):
                factory_units.append(unit)
        
        return factory_units
    
    def _detect_observer_pattern(self, units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect observer pattern."""
        observer_units = []
        
        # Look for observer-related classes and methods
        observer_classes = []
        observer_methods = []
        
        for unit in units:
            if not unit.content or not unit.symbol:
                continue
            
            content_lower = unit.content.lower()
            name_lower = unit.symbol.name.lower()
            
            # Observer classes
            if (unit.symbol.symbol_type == SymbolType.CLASS and
                ('observer' in name_lower or 'listener' in name_lower)):
                observer_classes.append(unit)
            
            # Observer methods
            if (unit.symbol.symbol_type in [SymbolType.FUNCTION, SymbolType.METHOD] and
                ('notify' in name_lower or 'update' in name_lower or 'subscribe' in name_lower)):
                observer_methods.append(unit)
        
        # Combine classes and methods
        observer_units.extend(observer_classes)
        observer_units.extend(observer_methods)
        
        return observer_units
    
    def _detect_strategy_pattern(self, units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect strategy pattern."""
        strategy_units = []
        
        # Look for strategy-related classes
        for unit in units:
            if not unit.content or not unit.symbol:
                continue
            
            if unit.symbol.symbol_type == SymbolType.CLASS:
                content_lower = unit.content.lower()
                name_lower = unit.symbol.name.lower()
                
                # Strategy characteristics
                has_strategy_name = ('strategy' in name_lower or 
                                  'algorithm' in name_lower)
                has_execute_method = 'def execute' in content_lower
                has_context_usage = 'context' in content_lower
                
                if has_strategy_name or (has_execute_method and has_context_usage):
                    strategy_units.append(unit)
        
        return strategy_units
    
    def _detect_adapter_pattern(self, units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect adapter pattern."""
        adapter_units = []
        
        for unit in units:
            if not unit.content or not unit.symbol:
                continue
            
            if unit.symbol.symbol_type == SymbolType.CLASS:
                content_lower = unit.content.lower()
                name_lower = unit.symbol.name.lower()
                
                # Adapter characteristics
                has_adapter_name = 'adapter' in name_lower
                has_wrapper_pattern = ('def __init__' in content_lower and 
                                     'self.' in content_lower and
                                     ('wrap' in content_lower or 'adapt' in content_lower))
                
                if has_adapter_name or has_wrapper_pattern:
                    adapter_units.append(unit)
        
        return adapter_units
    
    def _detect_decorator_pattern(self, units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect decorator pattern."""
        decorator_units = []
        
        for unit in units:
            if not unit.content or not unit.symbol:
                continue
            
            content_lower = unit.content.lower()
            name_lower = unit.symbol.name.lower()
            
            # Decorator characteristics
            has_decorator_name = 'decorator' in name_lower
            has_delegation = ('def __init__' in content_lower and 
                            'self.' in content_lower and
                            'component' in content_lower)
            has_same_interface = ('def' in content_lower and 
                                 'return self.' in content_lower)
            
            if has_decorator_name or (has_delegation and has_same_interface):
                decorator_units.append(unit)
        
        return decorator_units
    
    def _detect_command_pattern(self, units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect command pattern."""
        command_units = []
        
        for unit in units:
            if not unit.content or not unit.symbol:
                continue
            
            content_lower = unit.content.lower()
            name_lower = unit.symbol.name.lower()
            
            # Command characteristics
            has_command_name = 'command' in name_lower
            has_execute_method = 'def execute' in content_lower
            has_undo_method = 'def undo' in content_lower
            
            if has_command_name or (has_execute_method and has_undo_method):
                command_units.append(unit)
        
        return command_units
    
    def _is_long_method(self, unit: MemoryUnit) -> bool:
        """Check if method is too long."""
        if not unit.content or not unit.symbol:
            return False
        
        if unit.symbol.symbol_type not in [SymbolType.FUNCTION, SymbolType.METHOD]:
            return False
        
        lines = unit.content.split('\n')
        return len(lines) > 50
    
    def _is_large_class(self, unit: MemoryUnit) -> bool:
        """Check if class is too large."""
        if not unit.symbol or unit.symbol.symbol_type != SymbolType.CLASS:
            return False
        
        # Count methods in class
        method_count = 0
        for relationship in unit.relationships:
            if relationship.relation_type.value == 'contains':
                method_count += 1
        
        return method_count > 20
    
    def _is_god_class(self, unit: MemoryUnit) -> bool:
        """Check if class is a god class."""
        if not unit.symbol or unit.symbol.symbol_type != SymbolType.CLASS:
            return False
        
        # Check for too many responsibilities
        content_lower = unit.content.lower()
        
        # Count different types of operations
        db_operations = content_lower.count('select') + content_lower.count('insert') + content_lower.count('update')
        ui_operations = content_lower.count('button') + content_lower.count('window') + content_lower.count('dialog')
        file_operations = content_lower.count('file') + content_lower.count('read') + content_lower.count('write')
        
        total_operations = db_operations + ui_operations + file_operations
        
        return total_operations > 5
    
    def _has_feature_envy(self, unit: MemoryUnit, all_units: List[MemoryUnit]) -> bool:
        """Check if unit has feature envy."""
        if not unit.content or not unit.symbol:
            return False
        
        # Count calls to other classes
        external_calls = 0
        internal_calls = 0
        
        for relationship in unit.relationships:
            if relationship.relation_type.value == 'calls':
                # Check if target is in same class
                target_in_same_class = False
                for other_unit in all_units:
                    if (other_unit.id == relationship.target_id and
                        other_unit.file_path == unit.file_path):
                        target_in_same_class = True
                        break
                
                if target_in_same_class:
                    internal_calls += 1
                else:
                    external_calls += 1
        
        return external_calls > internal_calls * 2
    
    def _is_data_class(self, unit: MemoryUnit) -> bool:
        """Check if class is a data class."""
        if not unit.content or not unit.symbol:
            return False
        
        if unit.symbol.symbol_type != SymbolType.CLASS:
            return False
        
        content_lower = unit.content.lower()
        
        # Check for mostly getters/setters
        getter_setter_count = content_lower.count('def get_') + content_lower.count('def set_')
        method_count = content_lower.count('def ')
        
        return method_count > 0 and (getter_setter_count / method_count) > 0.7
    
    def _is_lazy_class(self, unit: MemoryUnit) -> bool:
        """Check if class is lazy (does very little)."""
        if not unit.content or not unit.symbol:
            return False
        
        if unit.symbol.symbol_type != SymbolType.CLASS:
            return False
        
        # Count meaningful methods
        content_lower = unit.content.lower()
        method_count = content_lower.count('def ')
        
        # Exclude simple getters/setters
        meaningful_methods = method_count - (content_lower.count('def get_') + content_lower.count('def set_'))
        
        return meaningful_methods < 2
    
    def _has_shotgun_surgery(self, unit: MemoryUnit, all_units: List[MemoryUnit]) -> bool:
        """Check if changing this class would require changes in many classes."""
        if not unit.symbol or unit.symbol.symbol_type != SymbolType.CLASS:
            return False
        
        # Count classes that depend on this class
        dependent_classes = set()
        
        for other_unit in all_units:
            if other_unit.file_path != unit.file_path:  # Different file
                for relationship in other_unit.relationships:
                    if relationship.target_id == unit.id:
                        dependent_classes.add(str(other_unit.file_path))
        
        return len(dependent_classes) > 5
    
    def _has_duplicated_code(self, unit: MemoryUnit, all_units: List[MemoryUnit]) -> bool:
        """Check for duplicated code (simplified)."""
        if not unit.content:
            return False
        
        # Simple check: look for similar content blocks
        content_lines = unit.content.split('\n')
        
        for other_unit in all_units:
            if other_unit.id == unit.id or not other_unit.content:
                continue
            
            other_lines = other_unit.content.split('\n')
            
            # Look for common sequences of lines
            common_sequences = 0
            for i in range(len(content_lines) - 3):
                sequence = content_lines[i:i+4]
                sequence_str = '\n'.join(sequence)
                
                for j in range(len(other_lines) - 3):
                    other_sequence = other_lines[j:j+4]
                    other_sequence_str = '\n'.join(other_sequence)
                    
                    if sequence_str == other_sequence_str:
                        common_sequences += 1
                        break
            
            if common_sequences > 2:
                return True
        
        return False
    
    def _detect_layered_architecture(self, file_units: Dict[str, List[MemoryUnit]]) -> List[MemoryUnit]:
        """Detect layered architecture pattern."""
        layered_units = []
        
        # Look for common layer patterns
        layer_indicators = {
            'controller': ['controller', 'handler', 'endpoint'],
            'service': ['service', 'business', 'logic'],
            'repository': ['repository', 'dao', 'persistence'],
            'model': ['model', 'entity', 'dto'],
        }
        
        for file_path, units in file_units:
            file_name = file_path.lower()
            
            for layer_name, indicators in layer_indicators.items():
                if any(indicator in file_name for indicator in indicators):
                    layered_units.extend(units)
                    break
        
        return layered_units
    
    def _detect_mvc_pattern(self, file_units: Dict[str, List[MemoryUnit]]) -> List[MemoryUnit]:
        """Detect MVC pattern."""
        mvc_units = []
        
        for file_path, units in file_units:
            file_name = file_path.lower()
            
            # Look for MVC components
            if ('controller' in file_name or 'view' in file_name or 'model' in file_name):
                mvc_units.extend(units)
        
        return mvc_units
    
    def _detect_repository_pattern(self, memory_units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect repository pattern."""
        repo_units = []
        
        for unit in memory_units:
            if not unit.content or not unit.symbol:
                continue
            
            content_lower = unit.content.lower()
            name_lower = unit.symbol.name.lower()
            
            # Repository characteristics
            has_repo_name = ('repository' in name_lower or 'dao' in name_lower)
            has_crud_methods = ('def save' in content_lower or 
                               'def find' in content_lower or
                               'def delete' in content_lower)
            
            if has_repo_name or has_crud_methods:
                repo_units.append(unit)
        
        return repo_units
    
    def _detect_service_layer(self, memory_units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect service layer pattern."""
        service_units = []
        
        for unit in memory_units:
            if not unit.content or not unit.symbol:
                continue
            
            content_lower = unit.content.lower()
            name_lower = unit.symbol.name.lower()
            
            # Service characteristics
            has_service_name = 'service' in name_lower
            has_business_logic = ('def calculate' in content_lower or
                                 'def process' in content_lower or
                                 'def validate' in content_lower)
            
            if has_service_name or has_business_logic:
                service_units.append(unit)
        
        return service_units
    
    def _detect_controller_pattern(self, memory_units: List[MemoryUnit]) -> List[MemoryUnit]:
        """Detect controller pattern."""
        controller_units = []
        
        for unit in memory_units:
            if not unit.content or not unit.symbol:
                continue
            
            content_lower = unit.content.lower()
            name_lower = unit.symbol.name.lower()
            
            # Controller characteristics
            has_controller_name = 'controller' in name_lower
            has_http_methods = ('def get' in content_lower or
                               'def post' in content_lower or
                               'def put' in content_lower or
                               'def delete' in content_lower)
            
            if has_controller_name or has_http_methods:
                controller_units.append(unit)
        
        return controller_units
    
    def _init_design_patterns(self) -> Dict[str, List[str]]:
        """Initialize design pattern definitions."""
        return {
            'singleton': ['_instance', '__new__', 'get_instance'],
            'factory': ['factory', 'create', 'build'],
            'observer': ['observer', 'listener', 'notify', 'update'],
            'strategy': ['strategy', 'algorithm', 'execute'],
            'adapter': ['adapter', 'wrap', 'adapt'],
            'decorator': ['decorator', 'component'],
            'command': ['command', 'execute', 'undo'],
        }
    
    def _init_code_smells(self) -> Dict[str, List[str]]:
        """Initialize code smell definitions."""
        return {
            'long_method': ['def', '50+ lines'],
            'large_class': ['class', '20+ methods'],
            'god_class': ['multiple responsibilities'],
            'feature_envy': ['external calls > internal calls'],
            'data_class': ['getters/setters only'],
            'lazy_class': ['minimal functionality'],
            'shotgun_surgery': ['many dependencies'],
            'duplicated_code': ['similar code blocks'],
        }
    
    def _init_architectural_patterns(self) -> Dict[str, List[str]]:
        """Initialize architectural pattern definitions."""
        return {
            'layered_architecture': ['controller', 'service', 'repository', 'model'],
            'mvc': ['model', 'view', 'controller'],
            'repository': ['repository', 'dao', 'persistence'],
            'service_layer': ['service', 'business', 'logic'],
            'controller': ['controller', 'handler', 'endpoint'],
        }
