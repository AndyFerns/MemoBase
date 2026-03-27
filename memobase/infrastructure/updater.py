"""
Project updater module for MemoBase.

Handles incremental updates to the memory index.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

from memobase.core.models import Config
from memobase.incremental.change_detector import ChangeDetector
from memobase.incremental.updater import IncrementalUpdater
from memobase.storage.file_storage import FileStorage


class ProjectUpdater:
    """Handles incremental updates to the project index."""
    
    def __init__(self, config: Config) -> None:
        """Initialize project updater.
        
        Args:
            config: Project configuration
        """
        self.config = config
        self.storage = FileStorage(config.repo_path / config.storage_path)
        self.change_detector = ChangeDetector(config)
        self.incremental_updater = IncrementalUpdater(config, self.storage)
    
    def update_repo(self, force: bool = False) -> Dict[str, Any]:
        """Update the repository index.
        
        Args:
            force: Force full rebuild
            
        Returns:
            Update statistics
        """
        start_time = time.time()
        
        if force:
            # Full rebuild
            from memobase.infrastructure.builder import ProjectBuilder
            builder = ProjectBuilder(self.config)
            stats = builder.build_repo(force=True)
            return {
                'files_added': stats['files_processed'],
                'files_modified': 0,
                'files_deleted': 0,
                'update_time': stats['build_time'],
            }
        
        # Detect changes
        added, modified, deleted = self.change_detector.detect_changes(self.config.repo_path)
        
        if not added and not modified and not deleted:
            return {
                'files_added': 0,
                'files_modified': 0,
                'files_deleted': 0,
                'update_time': 0.0,
            }
        
        # Process changes
        self.incremental_updater.process_changes(added, modified, deleted)
        
        update_time = time.time() - start_time
        
        return {
            'files_added': len(added),
            'files_modified': len(modified),
            'files_deleted': len(deleted),
            'update_time': update_time,
        }
