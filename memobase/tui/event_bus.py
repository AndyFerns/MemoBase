"""
Event bus for decoupled UI communication.

Decouples UI components: widget → emit(event) → controller/state → update → re-render
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from collections import defaultdict


class EventBus:
    """Event bus for decoupled communication between TUI components."""
    
    def __init__(self) -> None:
        """Initialize event bus."""
        # Map of event type to list of handlers
        self._handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)
        
        # Event history for debugging
        self._history: List[Dict[str, Any]] = []
        self._max_history = 100
    
    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle the event
        """
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Callback function to remove
        """
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]
    
    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event.
        
        Args:
            event_type: Type of event to emit
            data: Event data payload
        """
        # Add to history
        self._history.append({
            "type": event_type,
            "data": data,
        })
        
        # Trim history
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        # Call handlers
        for handler in self._handlers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                # Log error but don't stop other handlers
                print(f"Event handler error: {e}")
    
    def once(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe to an event once (auto-unsubscribe after first emit).
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle the event
        """
        def one_time_handler(data: Dict[str, Any]) -> None:
            self.unsubscribe(event_type, one_time_handler)
            handler(data)
        
        self.subscribe(event_type, one_time_handler)
    
    def clear(self, event_type: Optional[str] = None) -> None:
        """Clear event handlers.
        
        Args:
            event_type: Specific event type to clear, or None to clear all
        """
        if event_type:
            self._handlers[event_type] = []
        else:
            self._handlers.clear()
    
    def get_history(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get event history.
        
        Args:
            event_type: Filter by event type, or None for all events
            
        Returns:
            List of historical events
        """
        if event_type:
            return [e for e in self._history if e["type"] == event_type]
        return self._history.copy()
    
    def has_handlers(self, event_type: str) -> bool:
        """Check if event type has any handlers.
        
        Args:
            event_type: Event type to check
            
        Returns:
            True if handlers exist, False otherwise
        """
        return len(self._handlers.get(event_type, [])) > 0


class TypedEventBus(EventBus):
    """Type-safe event bus with predefined event types."""
    
    # Predefined event types
    STATE_CHANGED = "state_changed"
    ERROR = "error"
    QUERY_RESULT = "query_result"
    FILE_SELECTED = "file_selected"
    MODE_CHANGED = "mode_changed"
    REFRESH = "refresh"
    LOADING = "loading"
    
    def emit_state_changed(self, **kwargs) -> None:
        """Emit state changed event."""
        self.emit(self.STATE_CHANGED, kwargs)
    
    def emit_error(self, message: str, **kwargs) -> None:
        """Emit error event."""
        self.emit(self.ERROR, {"message": message, **kwargs})
    
    def emit_query_result(self, response, **kwargs) -> None:
        """Emit query result event."""
        self.emit(self.QUERY_RESULT, {"response": response, **kwargs})
    
    def emit_file_selected(self, file_path: str, **kwargs) -> None:
        """Emit file selected event."""
        self.emit(self.FILE_SELECTED, {"file_path": file_path, **kwargs})
    
    def emit_mode_changed(self, mode: str, **kwargs) -> None:
        """Emit mode changed event."""
        self.emit(self.MODE_CHANGED, {"mode": mode, **kwargs})
    
    def emit_refresh(self, **kwargs) -> None:
        """Emit refresh event."""
        self.emit(self.REFRESH, kwargs)
    
    def emit_loading(self, is_loading: bool, **kwargs) -> None:
        """Emit loading event."""
        self.emit(self.LOADING, {"is_loading": is_loading, **kwargs})
