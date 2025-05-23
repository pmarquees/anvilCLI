"""Tests for the cache module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from anvil.cache import Cache


class TestCache:
    """Test cases for the Cache class."""

    def test_cache_init(self) -> None:
        """Test cache initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("anvil.cache.Path.home", return_value=Path(temp_dir)):
                cache = Cache()
                assert cache.cache_dir.exists()
                assert cache.db_path.exists()

    def test_cache_set_and_get(self) -> None:
        """Test setting and getting cache values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("anvil.cache.Path.home", return_value=Path(temp_dir)):
                cache = Cache()

                # Test set and get
                cache.set("test_key", "test_value")
                assert cache.get("test_key") == "test_value"

                # Test non-existent key
                assert cache.get("non_existent") is None

    def test_cache_update(self) -> None:
        """Test updating existing cache values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("anvil.cache.Path.home", return_value=Path(temp_dir)):
                cache = Cache()

                # Set initial value
                cache.set("test_key", "initial_value")
                assert cache.get("test_key") == "initial_value"

                # Update value
                cache.set("test_key", "updated_value")
                assert cache.get("test_key") == "updated_value"

    def test_cache_clear(self) -> None:
        """Test clearing all cache data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("anvil.cache.Path.home", return_value=Path(temp_dir)):
                cache = Cache()

                # Add some data
                cache.set("key1", "value1")
                cache.set("key2", "value2")

                # Verify data exists
                assert cache.get("key1") == "value1"
                assert cache.get("key2") == "value2"

                # Clear cache
                cache.clear()

                # Verify data is gone
                assert cache.get("key1") is None
                assert cache.get("key2") is None
