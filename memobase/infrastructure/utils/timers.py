"""
Timing utilities for MemoBase.

Profiling and timing decorators.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, List, Optional


@dataclass
class TimerResult:
    """Result of a timed operation."""
    name: str
    elapsed_seconds: float
    start_time: float
    end_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class Timer:
    """Timer for profiling operations."""
    
    def __init__(self, name: str = "timer", enabled: bool = True) -> None:
        """Initialize timer.
        
        Args:
            name: Timer name
            enabled: Whether timing is enabled
        """
        self.name = name
        self.enabled = enabled
        self._start_time: Optional[float] = None
        self._results: List[TimerResult] = []
    
    def start(self) -> None:
        """Start the timer."""
        if self.enabled:
            self._start_time = time.perf_counter()
    
    def stop(self, metadata: Optional[Dict[str, Any]] = None) -> TimerResult:
        """Stop the timer and return result.
        
        Args:
            metadata: Additional metadata to store
            
        Returns:
            Timer result
        """
        if not self.enabled or self._start_time is None:
            return TimerResult(
                name=self.name,
                elapsed_seconds=0.0,
                start_time=0.0,
                end_time=0.0,
            )
        
        end_time = time.perf_counter()
        elapsed = end_time - self._start_time
        
        result = TimerResult(
            name=self.name,
            elapsed_seconds=elapsed,
            start_time=self._start_time,
            end_time=end_time,
            metadata=metadata or {},
        )
        
        self._results.append(result)
        self._start_time = None
        
        return result
    
    @contextmanager
    def measure(self, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for timing a block of code.
        
        Args:
            metadata: Additional metadata
            
        Yields:
            Self
        """
        self.start()
        try:
            yield self
        finally:
            self.stop(metadata)
    
    def get_results(self) -> List[TimerResult]:
        """Get all timing results.
        
        Returns:
            List of timer results
        """
        return self._results.copy()
    
    def get_total_time(self) -> float:
        """Get total time of all measurements.
        
        Returns:
            Total elapsed time
        """
        return sum(r.elapsed_seconds for r in self._results)
    
    def get_average_time(self) -> float:
        """Get average time of all measurements.
        
        Returns:
            Average elapsed time
        """
        if not self._results:
            return 0.0
        return self.get_total_time() / len(self._results)
    
    def reset(self) -> None:
        """Reset timer and clear results."""
        self._start_time = None
        self._results.clear()
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """Format time in human readable form.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted string
        """
        if seconds < 0.001:
            return f"{seconds * 1000000:.1f} μs"
        elif seconds < 1.0:
            return f"{seconds * 1000:.1f} ms"
        elif seconds < 60.0:
            return f"{seconds:.2f} s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"


class Profiler:
    """Profiler for tracking multiple timed operations."""
    
    def __init__(self, enabled: bool = True) -> None:
        """Initialize profiler.
        
        Args:
            enabled: Whether profiling is enabled
        """
        self.enabled = enabled
        self._timers: Dict[str, Timer] = {}
        self._current_timer: Optional[Timer] = None
    
    def start(self, name: str) -> Timer:
        """Start a named timer.
        
        Args:
            name: Timer name
            
        Returns:
            Timer instance
        """
        timer = Timer(name, self.enabled)
        self._timers[name] = timer
        timer.start()
        self._current_timer = timer
        return timer
    
    def stop(self, name: Optional[str] = None) -> Optional[TimerResult]:
        """Stop a named timer.
        
        Args:
            name: Timer name (uses current if None)
            
        Returns:
            Timer result or None
        """
        if name is None and self._current_timer:
            return self._current_timer.stop()
        
        if name in self._timers:
            return self._timers[name].stop()
        
        return None
    
    @contextmanager
    def profile(self, name: str):
        """Context manager for profiling a block.
        
        Args:
            name: Profile name
            
        Yields:
            Timer
        """
        timer = self.start(name)
        try:
            yield timer
        finally:
            self.stop(name)
    
    def get_report(self) -> str:
        """Generate profiling report.
        
        Returns:
            Formatted report string
        """
        lines = ["Profiling Report", "=" * 40]
        
        for name, timer in self._timers.items():
            total = timer.get_total_time()
            count = len(timer.get_results())
            avg = timer.get_average_time()
            
            lines.append(f"{name}:")
            lines.append(f"  Total: {Timer.format_time(total)}")
            lines.append(f"  Count: {count}")
            lines.append(f"  Average: {Timer.format_time(avg)}")
        
        return "\n".join(lines)
    
    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """Get profiling summary as dictionary.
        
        Returns:
            Dictionary of timer statistics
        """
        summary = {}
        
        for name, timer in self._timers.items():
            summary[name] = {
                'total_seconds': timer.get_total_time(),
                'count': len(timer.get_results()),
                'average_seconds': timer.get_average_time(),
            }
        
        return summary


def timed(func: Callable) -> Callable:
    """Decorator to time function execution.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        timer = Timer(func.__name__)
        timer.start()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            result = timer.stop()
            print(f"{func.__name__}: {Timer.format_time(result.elapsed_seconds)}")
    
    return wrapper


def profiled(profiler: Profiler):
    """Decorator factory for profiling with a profiler instance.
    
    Args:
        profiler: Profiler instance
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with profiler.profile(func.__name__):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Global profiler instance
_global_profiler: Optional[Profiler] = None


def get_profiler() -> Profiler:
    """Get global profiler instance.
    
    Returns:
        Profiler instance
    """
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = Profiler()
    return _global_profiler
