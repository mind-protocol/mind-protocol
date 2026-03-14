"""
Mind Protocol — Space Key Cache tests (Python).

Tests TTL expiry, LRU eviction, invalidation, thread safety, and basic get/put.

Run: python -m pytest tests/crypto/test_key_cache.py -v
  or: python tests/crypto/test_key_cache.py

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import os
import sys
import threading
import time

# Ensure the repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.crypto.key_cache import SpaceKeyCache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _key(n=32):
    """Return n random bytes to simulate a space key."""
    return os.urandom(n)


# ---------------------------------------------------------------------------
# Basic get / put
# ---------------------------------------------------------------------------

def test_get_returns_none_on_empty_cache():
    cache = SpaceKeyCache()
    assert cache.get("actor-1", "space-1") is None


def test_put_then_get():
    cache = SpaceKeyCache()
    sk = _key()
    cache.put("actor-1", "space-1", sk)
    assert cache.get("actor-1", "space-1") == sk


def test_different_actor_same_space():
    cache = SpaceKeyCache()
    sk1 = _key()
    sk2 = _key()
    cache.put("actor-1", "space-1", sk1)
    cache.put("actor-2", "space-1", sk2)
    assert cache.get("actor-1", "space-1") == sk1
    assert cache.get("actor-2", "space-1") == sk2


def test_overwrite_existing_entry():
    cache = SpaceKeyCache()
    sk1 = _key()
    sk2 = _key()
    cache.put("actor-1", "space-1", sk1)
    cache.put("actor-1", "space-1", sk2)
    assert cache.get("actor-1", "space-1") == sk2
    assert len(cache) == 1


# ---------------------------------------------------------------------------
# TTL expiry
# ---------------------------------------------------------------------------

def test_ttl_expiry():
    # Use a very short TTL so we can test expiry without sleeping long
    cache = SpaceKeyCache(ttl_seconds=0.1)
    sk = _key()
    cache.put("actor-1", "space-1", sk)
    assert cache.get("actor-1", "space-1") == sk

    time.sleep(0.15)  # Wait past TTL

    assert cache.get("actor-1", "space-1") is None
    assert len(cache) == 0  # Expired entry should be removed


def test_ttl_not_expired_yet():
    cache = SpaceKeyCache(ttl_seconds=10)
    sk = _key()
    cache.put("actor-1", "space-1", sk)
    assert cache.get("actor-1", "space-1") == sk


# ---------------------------------------------------------------------------
# LRU eviction
# ---------------------------------------------------------------------------

def test_lru_eviction_at_capacity():
    cache = SpaceKeyCache(max_entries=3)
    keys = {}
    for i in range(3):
        k = _key()
        keys[i] = k
        cache.put(f"actor-{i}", "space-0", k)

    assert len(cache) == 3

    # Adding a 4th entry should evict the oldest (actor-0)
    new_key = _key()
    cache.put("actor-new", "space-0", new_key)

    assert len(cache) == 3
    assert cache.get("actor-0", "space-0") is None  # evicted
    assert cache.get("actor-1", "space-0") == keys[1]
    assert cache.get("actor-2", "space-0") == keys[2]
    assert cache.get("actor-new", "space-0") == new_key


def test_lru_access_refreshes_order():
    cache = SpaceKeyCache(max_entries=3)
    sk0, sk1, sk2 = _key(), _key(), _key()

    cache.put("a0", "s", sk0)
    cache.put("a1", "s", sk1)
    cache.put("a2", "s", sk2)

    # Access a0 — moves it to the end (most-recently used)
    cache.get("a0", "s")

    # Insert new entry — should evict a1 (now the oldest)
    sk3 = _key()
    cache.put("a3", "s", sk3)

    assert cache.get("a0", "s") == sk0  # still present
    assert cache.get("a1", "s") is None  # evicted
    assert cache.get("a2", "s") == sk2
    assert cache.get("a3", "s") == sk3


# ---------------------------------------------------------------------------
# Invalidation
# ---------------------------------------------------------------------------

def test_invalidate_removes_all_entries_for_space():
    cache = SpaceKeyCache()
    cache.put("actor-1", "space-A", _key())
    cache.put("actor-2", "space-A", _key())
    cache.put("actor-1", "space-B", _key())

    assert len(cache) == 3

    cache.invalidate("space-A")

    assert cache.get("actor-1", "space-A") is None
    assert cache.get("actor-2", "space-A") is None
    assert cache.get("actor-1", "space-B") is not None
    assert len(cache) == 1


def test_invalidate_nonexistent_space_is_noop():
    cache = SpaceKeyCache()
    cache.put("actor-1", "space-1", _key())
    cache.invalidate("space-999")
    assert len(cache) == 1


# ---------------------------------------------------------------------------
# Clear
# ---------------------------------------------------------------------------

def test_clear():
    cache = SpaceKeyCache()
    for i in range(10):
        cache.put(f"actor-{i}", f"space-{i}", _key())

    assert len(cache) == 10
    cache.clear()
    assert len(cache) == 0


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------

def test_concurrent_access():
    cache = SpaceKeyCache(max_entries=50)
    errors = []

    def writer(thread_id):
        try:
            for i in range(20):
                cache.put(f"actor-{thread_id}", f"space-{i}", _key())
        except Exception as e:
            errors.append(e)

    def reader(thread_id):
        try:
            for i in range(20):
                cache.get(f"actor-{thread_id}", f"space-{i}")
        except Exception as e:
            errors.append(e)

    threads = []
    for t in range(5):
        threads.append(threading.Thread(target=writer, args=(t,)))
        threads.append(threading.Thread(target=reader, args=(t,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == [], f"Concurrent access caused errors: {errors}"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback

    tests = [
        test_get_returns_none_on_empty_cache,
        test_put_then_get,
        test_different_actor_same_space,
        test_overwrite_existing_entry,
        test_ttl_expiry,
        test_ttl_not_expired_yet,
        test_lru_eviction_at_capacity,
        test_lru_access_refreshes_order,
        test_invalidate_removes_all_entries_for_space,
        test_invalidate_nonexistent_space_is_noop,
        test_clear,
        test_concurrent_access,
    ]

    passed = 0
    failed = 0

    print("Mind Protocol — Space Key Cache — Python Test Suite")
    print("=" * 52)

    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception:
            print(f"  FAIL  {t.__name__}")
            traceback.print_exc()
            failed += 1

    print("=" * 52)
    print(f"Results: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed.")
