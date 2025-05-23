"""Caching layer using SQLite for persistent storage."""

import sqlite3
from pathlib import Path
from typing import Optional


class Cache:
    """Simple SQLite-based cache for storing key-value pairs."""

    def __init__(self) -> None:
        """Initialize cache with SQLite database in user's cache directory."""
        self.cache_dir = Path.home() / ".cache" / "anvil"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "cache.db"
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get(self, key: str) -> Optional[str]:
        """Get value by key from cache.

        Args:
            key: The cache key to look up

        Returns:
            The cached value or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT value FROM cache WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else None

    def set(self, key: str, value: str) -> None:
        """Set key-value pair in cache.

        Args:
            key: The cache key
            value: The value to store
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()

    def clear(self) -> None:
        """Clear all cached data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()


# Global cache instance
cache = Cache()
