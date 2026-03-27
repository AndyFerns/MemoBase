"""
Change detector implementation.
"""

from __future__ import annotations

import asyncio
import hashlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Set, Tuple

from memobase.core.exceptions import QueryError
from memobase.core.interfaces import IncrementalInterface, ScannerInterface
from memobase.core.models import Config


class ChangeDetector(IncrementalInterface):
    """Detects file changes using SHA256 hashing."""
    
    def __init__(self, config: Config) -> None:
        """Initialize change detector.
        
        Args:
            config: Project configuration
        """
        self.config = config
        self.file_hashes: Dict[str, str] = {}
        self.last_scan_time = None
    
    def detect_changes(self, repo_path: Path) -> Tuple[List[Path], List[Path], List[Path]]:
        """Detect file changes in repository."""
        try:
            # Scan current files
            from memobase.infrastructure.filesystem.scanner import FilesystemScanner
            scanner = FilesystemScanner(self.config)
            current_files = set(scanner.scan(repo_path))
            current_hashes = {}
            
            # Calculate current hashes
            for file_path in current_files:
                try:
                    file_hash = self.calculate_file_hash(file_path)
                    current_hashes[str(file_path)] = file_hash
                except Exception:
                    continue  # Skip files that can't be read
            
            # Determine changes
            added_files = []
            modified_files = []
            deleted_files = []
            
            # Check for added and modified files
            for file_path_str, current_hash in current_hashes.items():
                file_path = Path(file_path_str)
                
                if file_path_str not in self.file_hashes:
                    # New file
                    added_files.append(file_path)
                elif self.file_hashes[file_path_str] != current_hash:
                    # Modified file
                    modified_files.append(file_path)
            
            # Check for deleted files
            for file_path_str in self.file_hashes:
                if file_path_str not in current_hashes:
                    deleted_files.append(Path(file_path_str))
            
            # Update stored hashes
            self.file_hashes = current_hashes
            self.last_scan_time = asyncio.get_event_loop().time()
            
            return added_files, modified_files, deleted_files
            
        except Exception as e:
            raise QueryError(f"Change detection failed: {str(e)}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        try:
            hasher = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception as e:
            raise QueryError(f"Failed to calculate hash for {file_path}: {str(e)}")
    
    def update_index(self, index, changed_units: List) -> Index:
        """Update index with changed memory units."""
        # This would be implemented based on the specific index type
        # For now, return the index unchanged
        return index
    
    def update_graph(self, graph, changed_units: List, changed_relationships: List) -> Graph:
        """Update graph with changes."""
        # This would be implemented based on the specific graph type
        # For now, return the graph unchanged
        return graph
    
    async def detect_changes_async(self, repo_path: Path) -> Tuple[List[Path], List[Path], List[Path]]:
        """Async version of detect_changes."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.detect_changes, repo_path)
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get stored hash for file."""
        return self.file_hashes.get(str(file_path))
    
    def set_file_hash(self, file_path: Path, file_hash: str) -> None:
        """Set stored hash for file."""
        self.file_hashes[str(file_path)] = file_hash
    
    def remove_file_hash(self, file_path: Path) -> None:
        """Remove stored hash for file."""
        self.file_hashes.pop(str(file_path), None)
    
    def clear_all_hashes(self) -> None:
        """Clear all stored file hashes."""
        self.file_hashes.clear()
        self.last_scan_time = None
    
    def get_change_statistics(self) -> Dict[str, int]:
        """Get statistics about stored hashes."""
        return {
            'tracked_files': len(self.file_hashes),
            'last_scan_time': self.last_scan_time,
        }
    
    def is_file_tracked(self, file_path: Path) -> bool:
        """Check if file is being tracked."""
        return str(file_path) in self.file_hashes
    
    def get_tracked_files(self) -> List[Path]:
        """Get list of tracked files."""
        return [Path(path_str) for path_str in self.file_hashes.keys()]
    
    def _create_config(self) -> Config:
        """Create default configuration for scanning."""
        from memobase.core.models import Config
        return Config(repo_path=Path.cwd())
    
    def detect_content_changes(self, file_path: Path, old_content: str, new_content: str) -> Dict[str, any]:
        """Detect specific changes in file content."""
        try:
            changes = {
                'lines_added': 0,
                'lines_removed': 0,
                'lines_modified': 0,
                'functions_added': [],
                'functions_removed': [],
                'classes_added': [],
                'classes_removed': [],
            }
            
            old_lines = old_content.split('\n')
            new_lines = new_content.split('\n')
            
            # Simple line-based diff
            import difflib
            differ = difflib.unified_diff(old_lines, new_lines, lineterm='')
            
            for line in differ:
                if line.startswith('+') and not line.startswith('+++'):
                    changes['lines_added'] += 1
                elif line.startswith('-') and not line.startswith('---'):
                    changes['lines_removed'] += 1
            
            # Detect function changes (simplified)
            old_functions = self._extract_function_names(old_content)
            new_functions = self._extract_function_names(new_content)
            
            changes['functions_added'] = list(set(new_functions) - set(old_functions))
            changes['functions_removed'] = list(set(old_functions) - set(new_functions))
            
            # Detect class changes (simplified)
            old_classes = self._extract_class_names(old_content)
            new_classes = self._extract_class_names(new_content)
            
            changes['classes_added'] = list(set(new_classes) - set(old_classes))
            changes['classes_removed'] = list(set(old_classes) - set(new_classes))
            
            changes['lines_modified'] = min(changes['lines_added'], changes['lines_removed'])
            
            return changes
            
        except Exception as e:
            raise QueryError(f"Content change detection failed: {str(e)}")
    
    def detect_import_changes(self, file_path: Path, old_content: str, new_content: str) -> Dict[str, List[str]]:
        """Detect changes in imports."""
        try:
            old_imports = self._extract_imports(old_content)
            new_imports = self._extract_imports(new_content)
            
            return {
                'imports_added': list(set(new_imports) - set(old_imports)),
                'imports_removed': list(set(old_imports) - set(new_imports)),
            }
            
        except Exception as e:
            raise QueryError(f"Import change detection failed: {str(e)}")
    
    def batch_detect_changes(self, file_paths: List[Path]) -> Dict[Path, Tuple[List[str], List[str], List[str]]]:
        """Detect changes for multiple files."""
        changes = {}
        
        for file_path in file_paths:
            try:
                current_hash = self.calculate_file_hash(file_path)
                stored_hash = self.get_file_hash(file_path)
                
                if stored_hash is None:
                    # New file
                    changes[file_path] = ([file_path], [], [])
                elif stored_hash != current_hash:
                    # Modified file
                    changes[file_path] = ([], [file_path], [])
                # else: unchanged
                
                # Update stored hash
                self.set_file_hash(file_path, current_hash)
                
            except Exception:
                continue  # Skip files that can't be processed
        
        return changes
    
    def _extract_function_names(self, content: str) -> List[str]:
        """Extract function names from content (simplified)."""
        import re
        
        # Python functions
        functions = re.findall(r'def\s+(\w+)\s*\(', content)
        
        # JavaScript functions
        functions.extend(re.findall(r'function\s+(\w+)\s*\(', content))
        functions.extend(re.findall(r'const\s+(\w+)\s*=\s*\(', content))
        
        return functions
    
    def _extract_class_names(self, content: str) -> List[str]:
        """Extract class names from content (simplified)."""
        import re
        
        # Python classes
        classes = re.findall(r'class\s+(\w+)\s*\(', content)
        
        # JavaScript classes
        classes.extend(re.findall(r'class\s+(\w+)\s*\{', content))
        
        return classes
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from content (simplified)."""
        import re
        
        imports = []
        
        # Python imports
        imports.extend(re.findall(r'import\s+(.+)', content))
        imports.extend(re.findall(r'from\s+(.+)\s+import', content))
        
        # JavaScript imports
        imports.extend(re.findall(r'import\s+.+\s+from\s+(.+)', content))
        imports.extend(re.findall(r'require\s*\(\s*[\'"](.+)[\'"]', content))
        
        return imports


class GitChangeDetector(ChangeDetector):
    """Change detector that uses Git for change detection."""
    
    def __init__(self, scanner: ScannerInterface, repo_path: Path) -> None:
        """Initialize Git change detector.
        
        Args:
            scanner: File system scanner
            repo_path: Path to Git repository
        """
        super().__init__(scanner)
        self.repo_path = repo_path
        self.is_git_repo = self._check_git_repo()
    
    def detect_changes(self, repo_path: Path) -> Tuple[List[Path], List[Path], List[Path]]:
        """Detect changes using Git."""
        if not self.is_git_repo:
            return super().detect_changes(repo_path)
        
        try:
            import subprocess
            
            # Get Git changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            added_files = []
            modified_files = []
            deleted_files = []
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                status = line[:2]
                file_path = Path(line[3:])
                
                if status[0] in ['A', '?']:  # Added or untracked
                    added_files.append(file_path)
                elif status[0] == 'M' or status[1] == 'M':  # Modified
                    modified_files.append(file_path)
                elif status[0] == 'D':  # Deleted
                    deleted_files.append(file_path)
            
            return added_files, modified_files, deleted_files
            
        except subprocess.CalledProcessError as e:
            raise QueryError(f"Git change detection failed: {e}")
        except Exception as e:
            raise QueryError(f"Git change detection failed: {str(e)}")
    
    def get_git_diff(self, file_path: Path) -> str:
        """Get Git diff for file."""
        try:
            import subprocess
            
            result = subprocess.run(
                ['git', 'diff', 'HEAD', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            raise QueryError(f"Git diff failed: {e}")
    
    def get_committed_files(self, commit_hash: str = 'HEAD') -> List[Path]:
        """Get files in a specific commit."""
        try:
            import subprocess
            
            result = subprocess.run(
                ['git', 'ls-tree', '--name-only', '-r', commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    files.append(Path(line))
            
            return files
            
        except subprocess.CalledProcessError as e:
            raise QueryError(f"Git ls-tree failed: {e}")
    
    def get_changed_files_between_commits(self, from_commit: str, to_commit: str) -> Tuple[List[Path], List[Path], List[Path]]:
        """Get files changed between two commits."""
        try:
            import subprocess
            
            result = subprocess.run(
                ['git', 'diff', '--name-status', f'{from_commit}..{to_commit}'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            added_files = []
            modified_files = []
            deleted_files = []
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                status, file_path = line.split('\t', 1)
                file_path = Path(file_path)
                
                if status == 'A':
                    added_files.append(file_path)
                elif status == 'M':
                    modified_files.append(file_path)
                elif status == 'D':
                    deleted_files.append(file_path)
            
            return added_files, modified_files, deleted_files
            
        except subprocess.CalledProcessError as e:
            raise QueryError(f"Git diff between commits failed: {e}")
    
    def _check_git_repo(self) -> bool:
        """Check if directory is a Git repository."""
        try:
            import subprocess
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
