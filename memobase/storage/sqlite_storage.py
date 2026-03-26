"""
SQLite-based storage implementation.
"""

from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite
import orjson

from memobase.core.exceptions import StorageError
from memobase.core.interfaces import StorageInterface


class SQLiteStorage(StorageInterface):
    """SQLite-based storage with JSON support."""
    
    def __init__(self, db_path: Path) -> None:
        """Initialize SQLite storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    data_type TEXT NOT NULL DEFAULT 'json',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_storage_key ON storage(key)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_storage_created_at ON storage(created_at)
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS update_storage_updated_at
                AFTER UPDATE ON storage
                BEGIN
                    UPDATE storage SET updated_at = CURRENT_TIMESTAMP WHERE key = NEW.key;
                END
            """)
            
            conn.commit()
    
    def store(self, data: Any, key: str) -> None:
        """Store data with given key."""
        try:
            # Serialize data
            if hasattr(data, 'to_json'):
                json_data = data.to_json()
            else:
                json_data = orjson.dumps(data).decode()
            
            # Determine data type
            data_type = 'json'
            if not (json_data.strip().startswith('{') or json_data.strip().startswith('[')):
                data_type = 'text'
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO storage (key, data, data_type) VALUES (?, ?, ?)",
                    (key, json_data, data_type)
                )
                conn.commit()
                
        except Exception as e:
            raise StorageError(f"Failed to store data for key '{key}': {str(e)}")
    
    def retrieve(self, key: str) -> Any:
        """Retrieve data by key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data, data_type FROM storage WHERE key = ?", (key,))
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                data_text, data_type = row
                
                # Deserialize data
                if data_type == 'json':
                    return orjson.loads(data_text)
                else:
                    return data_text
                    
        except Exception as e:
            raise StorageError(f"Failed to retrieve data for key '{key}': {str(e)}")
    
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM storage WHERE key = ?", (key,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            raise StorageError(f"Failed to delete data for key '{key}': {str(e)}")
    
    def exists(self, key: str) -> bool:
        """Check if data exists for key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT 1 FROM storage WHERE key = ? LIMIT 1", (key,))
                return cursor.fetchone() is not None
                
        except Exception as e:
            raise StorageError(f"Failed to check existence for key '{key}': {str(e)}")
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with given prefix."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if prefix:
                    cursor = conn.execute(
                        "SELECT key FROM storage WHERE key LIKE ? ORDER BY key",
                        (f"{prefix}%",)
                    )
                else:
                    cursor = conn.execute("SELECT key FROM storage ORDER BY key")
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            raise StorageError(f"Failed to list keys with prefix '{prefix}': {str(e)}")
    
    async def store_async(self, data: Any, key: str) -> None:
        """Async version of store."""
        try:
            # Serialize data
            if hasattr(data, 'to_json'):
                json_data = data.to_json()
            else:
                json_data = orjson.dumps(data).decode()
            
            # Determine data type
            data_type = 'json'
            if not (json_data.strip().startswith('{') or json_data.strip().startswith('[')):
                data_type = 'text'
            
            # Store in database asynchronously
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    "INSERT OR REPLACE INTO storage (key, data, data_type) VALUES (?, ?, ?)",
                    (key, json_data, data_type)
                )
                await conn.commit()
                
        except Exception as e:
            raise StorageError(f"Failed to store data asynchronously for key '{key}': {str(e)}")
    
    async def retrieve_async(self, key: str) -> Any:
        """Async version of retrieve."""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("SELECT data, data_type FROM storage WHERE key = ?", (key,))
                row = await cursor.fetchone()
                
                if row is None:
                    return None
                
                data_text, data_type = row
                
                # Deserialize data
                if data_type == 'json':
                    return orjson.loads(data_text)
                else:
                    return data_text
                    
        except Exception as e:
            raise StorageError(f"Failed to retrieve data asynchronously for key '{key}': {str(e)}")
    
    def store_batch(self, data_items: Dict[str, Any]) -> None:
        """Store multiple data items in a transaction."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for key, data in data_items.items():
                    # Serialize data
                    if hasattr(data, 'to_json'):
                        json_data = data.to_json()
                    else:
                        json_data = orjson.dumps(data).decode()
                    
                    # Determine data type
                    data_type = 'json'
                    if not (json_data.strip().startswith('{') or json_data.strip().startswith('[')):
                        data_type = 'text'
                    
                    # Store in database
                    conn.execute(
                        "INSERT OR REPLACE INTO storage (key, data, data_type) VALUES (?, ?, ?)",
                        (key, json_data, data_type)
                    )
                
                conn.commit()
                
        except Exception as e:
            raise StorageError(f"Failed to store batch data: {str(e)}")
    
    def retrieve_batch(self, keys: List[str]) -> Dict[str, Any]:
        """Retrieve multiple data items."""
        try:
            results = {}
            
            with sqlite3.connect(self.db_path) as conn:
                placeholders = ','.join(['?' for _ in keys])
                cursor = conn.execute(
                    f"SELECT key, data, data_type FROM storage WHERE key IN ({placeholders})",
                    keys
                )
                
                for row in cursor.fetchall():
                    key, data_text, data_type = row
                    
                    # Deserialize data
                    if data_type == 'json':
                        results[key] = orjson.loads(data_text)
                    else:
                        results[key] = data_text
                
                return results
                
        except Exception as e:
            raise StorageError(f"Failed to retrieve batch data: {str(e)}")
    
    def clear_all(self) -> None:
        """Clear all stored data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM storage")
                conn.commit()
                
        except Exception as e:
            raise StorageError(f"Failed to clear storage: {str(e)}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get basic stats
                cursor = conn.execute("SELECT COUNT(*) FROM storage")
                total_keys = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT SUM(LENGTH(data)) FROM storage")
                total_size = cursor.fetchone()[0] or 0
                
                # Get data type distribution
                cursor = conn.execute("SELECT data_type, COUNT(*) FROM storage GROUP BY data_type")
                type_distribution = dict(cursor.fetchall())
                
                # Get oldest and newest records
                cursor = conn.execute("SELECT MIN(created_at), MAX(created_at) FROM storage")
                oldest, newest = cursor.fetchone()
                
                return {
                    'total_keys': total_keys,
                    'total_size_bytes': total_size,
                    'type_distribution': type_distribution,
                    'oldest_record': oldest,
                    'newest_record': newest,
                    'database_path': str(self.db_path),
                }
                
        except Exception as e:
            raise StorageError(f"Failed to get storage stats: {str(e)}")
    
    def vacuum_database(self) -> None:
        """Vacuum database to optimize storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("VACUUM")
                
        except Exception as e:
            raise StorageError(f"Failed to vacuum database: {str(e)}")
    
    def backup_database(self, backup_path: Path) -> None:
        """Backup database to specified path."""
        try:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
                    
        except Exception as e:
            raise StorageError(f"Failed to backup database: {str(e)}")
    
    def restore_database(self, backup_path: Path) -> None:
        """Restore database from backup."""
        try:
            if not backup_path.exists():
                raise StorageError(f"Backup file does not exist: {backup_path}")
            
            # Close any existing connections
            if self.db_path.exists():
                self.db_path.unlink()
            
            # Copy backup file
            import shutil
            shutil.copy2(backup_path, self.db_path)
            
            # Reinitialize database
            self._init_database()
            
        except Exception as e:
            raise StorageError(f"Failed to restore database: {str(e)}")
    
    def query_keys_by_pattern(self, pattern: str) -> List[str]:
        """Query keys using SQL LIKE pattern."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT key FROM storage WHERE key LIKE ? ORDER BY key",
                    (pattern,)
                )
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            raise StorageError(f"Failed to query keys by pattern '{pattern}': {str(e)}")
    
    def get_keys_by_date_range(self, start_date: str, end_date: str) -> List[str]:
        """Get keys created within date range."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT key FROM storage WHERE created_at BETWEEN ? AND ? ORDER BY created_at",
                    (start_date, end_date)
                )
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            raise StorageError(f"Failed to get keys by date range: {str(e)}")
    
    def optimize_database(self) -> None:
        """Optimize database performance."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Analyze query planner
                conn.execute("ANALYZE")
                
                # Rebuild indexes
                conn.execute("REINDEX")
                
                # Vacuum to reclaim space
                conn.execute("VACUUM")
                
        except Exception as e:
            raise StorageError(f"Failed to optimize database: {str(e)}")


class EncryptedSQLiteStorage(SQLiteStorage):
    """SQLite storage with encryption."""
    
    def __init__(self, db_path: Path, encryption_key: str) -> None:
        """Initialize encrypted SQLite storage.
        
        Args:
            db_path: Path to SQLite database file
            encryption_key: Encryption key for data
        """
        self.encryption_key = encryption_key
        super().__init__(db_path)
    
    def store(self, data: Any, key: str) -> None:
        """Store encrypted data."""
        try:
            # Serialize data
            if hasattr(data, 'to_json'):
                json_data = data.to_json()
            else:
                json_data = orjson.dumps(data).decode()
            
            # Encrypt data
            encrypted_data = self._encrypt_data(json_data)
            
            # Store encrypted data
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO storage (key, data, data_type) VALUES (?, ?, ?)",
                    (key, encrypted_data, 'encrypted')
                )
                conn.commit()
                
        except Exception as e:
            raise StorageError(f"Failed to store encrypted data for key '{key}': {str(e)}")
    
    def retrieve(self, key: str) -> Any:
        """Retrieve and decrypt data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data, data_type FROM storage WHERE key = ?", (key,))
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                data_text, data_type = row
                
                # Decrypt data if encrypted
                if data_type == 'encrypted':
                    decrypted_data = self._decrypt_data(data_text)
                    return orjson.loads(decrypted_data)
                else:
                    # Handle unencrypted data
                    if data_type == 'json':
                        return orjson.loads(data_text)
                    else:
                        return data_text
                        
        except Exception as e:
            raise StorageError(f"Failed to retrieve encrypted data for key '{key}': {str(e)}")
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt data using simple XOR cipher (placeholder)."""
        # This is a placeholder implementation
        # In practice, use proper encryption like AES
        key_bytes = self.encryption_key.encode()
        data_bytes = data.encode()
        
        encrypted_bytes = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return encrypted_bytes.hex()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using simple XOR cipher (placeholder)."""
        # This is a placeholder implementation
        # In practice, use proper encryption like AES
        key_bytes = self.encryption_key.encode()
        encrypted_bytes = bytes.fromhex(encrypted_data)
        
        decrypted_bytes = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return decrypted_bytes.decode()
