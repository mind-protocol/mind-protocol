"""
Mind Protocol — Space Key Cache (Python)

In-memory LRU cache for decrypted space keys, keyed on (actor_id, space_id).
Avoids repeated sealed-box decryption on every private-Space read.

- Max 100 entries
- 5-minute TTL per entry
- Thread-safe (threading.Lock)

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import threading
import time
from collections import OrderedDict

# Defaults — importable for tests that need to override
DEFAULT_MAX_ENTRIES = 100
DEFAULT_TTL_SECONDS = 300  # 5 minutes


class SpaceKeyCache:
    """LRU cache for decrypted space keys, keyed on (actor_id, space_id)."""

    def __init__(self, max_entries=DEFAULT_MAX_ENTRIES, ttl_seconds=DEFAULT_TTL_SECONDS):
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        # OrderedDict maintains insertion/access order for LRU eviction.
        # Values are (space_key: bytes, inserted_at: float).
        self._cache = OrderedDict()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, actor_id, space_id):
        """Return the cached space key, or None if missing / expired."""
        key = (actor_id, space_id)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            space_key, inserted_at = entry
            if time.monotonic() - inserted_at >= self._ttl_seconds:
                # Expired — remove and return None
                del self._cache[key]
                return None

            # Move to end (most-recently used)
            self._cache.move_to_end(key)
            return space_key

    def put(self, actor_id, space_id, space_key):
        """Store a space key. Evicts the oldest entry if the cache is full."""
        key = (actor_id, space_id)
        with self._lock:
            if key in self._cache:
                # Update existing — move to end
                del self._cache[key]

            # Evict oldest if at capacity
            while len(self._cache) >= self._max_entries:
                self._cache.popitem(last=False)

            self._cache[key] = (space_key, time.monotonic())

    def invalidate(self, space_id):
        """Remove ALL entries for a given space_id (used on key rotation)."""
        with self._lock:
            to_delete = [k for k in self._cache if k[1] == space_id]
            for k in to_delete:
                del self._cache[k]

    def clear(self):
        """Remove all entries."""
        with self._lock:
            self._cache.clear()

    # ------------------------------------------------------------------
    # Introspection (useful for tests / debugging)
    # ------------------------------------------------------------------

    def __len__(self):
        with self._lock:
            return len(self._cache)
