"""
Concurrency executor for MemoBase.

Wrapper around ProcessPoolExecutor.

Used for:
- parser
- memory builder
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable, List, TypeVar

T = TypeVar('T')


class Executor:
    """Wrapper for concurrent execution."""
    
    def __init__(self, max_workers: int = 4, use_processes: bool = True) -> None:
        """Initialize executor.
        
        Args:
            max_workers: Maximum number of worker processes/threads
            use_processes: Use ProcessPoolExecutor if True, ThreadPoolExecutor if False
        """
        self.max_workers = max_workers
        self.use_processes = use_processes
        self._executor: ProcessPoolExecutor | ThreadPoolExecutor | None = None
    
    def __enter__(self) -> Executor:
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.shutdown()
    
    def start(self) -> None:
        """Start the executor."""
        if self.use_processes:
            self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
        else:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the executor.
        
        Args:
            wait: Wait for pending futures to complete
        """
        if self._executor:
            self._executor.shutdown(wait=wait)
            self._executor = None
    
    async def map(self, func: Callable[[Any], T], items: List[Any]) -> List[T]:
        """Map function over items concurrently.
        
        Args:
            func: Function to apply
            items: Items to process
            
        Returns:
            List of results
        """
        if self._executor is None:
            self.start()
        
        loop = asyncio.get_event_loop()
        
        # Submit all tasks
        futures = [
            loop.run_in_executor(self._executor, func, item)
            for item in items
        ]
        
        # Wait for all to complete
        results = await asyncio.gather(*futures, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                # Log error but continue
                print(f"Task failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def submit(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Submit single task to executor.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
        """
        if self._executor is None:
            self.start()
        
        loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            self._executor,
            lambda: func(*args, **kwargs)
        )
    
    def batch_map(self, func: Callable[[Any], T], items: List[Any], 
                  batch_size: int = 100) -> List[T]:
        """Map function over items in batches (synchronous).
        
        Args:
            func: Function to apply
            items: Items to process
            batch_size: Size of each batch
            
        Returns:
            List of results
        """
        if self._executor is None:
            self.start()
        
        results = []
        
        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Submit batch
            futures = [
                self._executor.submit(func, item)
                for item in batch
            ]
            
            # Collect results
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Batch task failed: {e}")
        
        return results


class ParallelParser:
    """Parallel parser using executor."""
    
    def __init__(self, executor: Executor) -> None:
        """Initialize parallel parser.
        
        Args:
            executor: Executor instance
        """
        self.executor = executor
    
    async def parse_files(self, file_paths: List[Any], parser_func: Callable) -> List[Any]:
        """Parse multiple files in parallel.
        
        Args:
            file_paths: List of file paths
            parser_func: Parser function
            
        Returns:
            List of parsed results
        """
        return await self.executor.map(parser_func, file_paths)


class ParallelMemoryBuilder:
    """Parallel memory builder using executor."""
    
    def __init__(self, executor: Executor) -> None:
        """Initialize parallel memory builder.
        
        Args:
            executor: Executor instance
        """
        self.executor = executor
    
    async def build_memory_units(self, parsed_files: List[Any], 
                                  builder_func: Callable) -> List[Any]:
        """Build memory units in parallel.
        
        Args:
            parsed_files: List of parsed files
            builder_func: Builder function
            
        Returns:
            List of memory units
        """
        return await self.executor.map(builder_func, parsed_files)
