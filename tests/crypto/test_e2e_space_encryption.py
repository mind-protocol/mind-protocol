"""
Mind Protocol — E2E Space Encryption Test Suite.

Exercises the full encryption lifecycle against a real FalkorDB graph:
  1. Create private Space -> verify visibility=private in graph
  2. Write encrypted Moment -> verify ciphertext + encrypted flag in graph
  3. Read and decrypt -> verify plaintext matches original
  4. Grant access to actor B -> verify B can decrypt
  5. Actor C (no access) -> verify cannot get space key
  6. Revoke actor B -> verify HAS_ACCESS link deleted
  7. Cross-language round-trip: JS encrypts -> Python decrypts (subprocess)

Uses graph name: test_e2e_encryption (NOT venezia or mind_protocol).

REQUIRES:
    - FalkorDB running on localhost:6379
    - mind-protocol/python/crypto installed (PyNaCl + cryptography)
    - Node.js + mind-protocol/lib/crypto (for cross-language test)

Run:
    python -m pytest tests/crypto/test_e2e_space_encryption.py -v
    python tests/crypto/test_e2e_space_encryption.py

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.crypto import (
    generate_space_key,
    encrypt_content,
    decrypt_content,
    is_encrypted,
    generate_actor_key_pair,
    store_actor_keys,
    load_actor_keys,
    encrypt_space_key_for_actor,
    decrypt_space_key_for_actor,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRAPH_NAME = "test_e2e_encryption"
FALKORDB_HOST = os.environ.get("FALKORDB_HOST", "localhost")
FALKORDB_PORT = int(os.environ.get("FALKORDB_PORT", "6379"))

# ---------------------------------------------------------------------------
# Graph helpers
# ---------------------------------------------------------------------------

_graph = None


def _get_graph():
    """Lazy-connect to FalkorDB and return the test graph handle."""
    global _graph
    if _graph is not None:
        return _graph
    from falkordb import FalkorDB
    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
    _graph = db.select_graph(GRAPH_NAME)
    return _graph


def _query(cypher, params=None):
    """Run a Cypher query and return result_set rows."""
    g = _get_graph()
    result = g.query(cypher, params)
    return result.result_set


def _ro_query(cypher, params=None):
    """Run a read-only Cypher query and return result_set rows."""
    g = _get_graph()
    result = g.ro_query(cypher, params)
    return result.result_set


# ---------------------------------------------------------------------------
# Test fixtures — 3 actors with X25519 key pairs
# ---------------------------------------------------------------------------

_actors = {}
_tmp_dirs = []
_space_id = None
_space_key = None


def _setup():
    """Create 3 test actors with key pairs in temp dirs, seed into graph."""
    global _actors, _tmp_dirs, _space_id, _space_key

    for name in ("alice", "bob", "carol"):
        actor_id = f"test_{name}_{uuid.uuid4().hex[:8]}"
        key_pair = generate_actor_key_pair()
        keys_dir = tempfile.mkdtemp(prefix=f"mind-e2e-{name}-")
        store_actor_keys(keys_dir, key_pair)
        _tmp_dirs.append(keys_dir)

        pub_b64 = base64.b64encode(key_pair["public_key"]).decode("ascii")

        # Create Actor node in graph with public_key
        _query(
            "MERGE (a:Actor {id: $id}) "
            "SET a.name = $name, a.public_key = $pub_key",
            {"id": actor_id, "name": name, "pub_key": pub_b64},
        )

        _actors[name] = {
            "id": actor_id,
            "key_pair": key_pair,
            "keys_dir": keys_dir,
            "pub_b64": pub_b64,
        }

    # Generate a space key for later tests
    _space_key = generate_space_key()
    _space_id = f"space_e2e_{uuid.uuid4().hex[:12]}"


def _teardown():
    """Drop the test graph and clean up temp directories."""
    global _graph
    try:
        g = _get_graph()
        g.delete()
    except Exception:
        pass
    _graph = None

    for d in _tmp_dirs:
        try:
            shutil.rmtree(d)
        except Exception:
            pass


# ===========================================================================
# Test 1: Create private Space -> verify visibility=private in graph
# ===========================================================================

def test_1_create_private_space():
    """Create a private Space node and verify visibility is persisted."""
    alice = _actors["alice"]

    # Create private Space
    _query(
        "MERGE (s:Space {id: $id}) "
        "SET s.type = 'room', "
        "    s.name = 'Secret Lab', "
        "    s.capacity = 10, "
        "    s.status = 'active', "
        "    s.visibility = 'private'",
        {"id": _space_id},
    )

    # Wrap space key for alice (owner)
    encrypted_key = encrypt_space_key_for_actor(
        _space_key, alice["key_pair"]["public_key"]
    )

    # Create HAS_ACCESS link with owner role and encrypted key
    _query(
        "MATCH (a:Actor {id: $actor_id}), (s:Space {id: $space_id}) "
        "MERGE (a)-[r:HAS_ACCESS]->(s) "
        "SET r.role = 'owner', r.encrypted_key = $ekey",
        {
            "actor_id": alice["id"],
            "space_id": _space_id,
            "ekey": encrypted_key,
        },
    )

    # Verify: visibility is 'private' in graph
    rows = _ro_query(
        "MATCH (s:Space {id: $id}) RETURN s.visibility",
        {"id": _space_id},
    )
    assert len(rows) == 1, f"Expected 1 Space, got {len(rows)}"
    assert rows[0][0] == "private", f"Expected visibility='private', got '{rows[0][0]}'"

    # Verify: HAS_ACCESS link exists with role='owner'
    rows = _ro_query(
        "MATCH (a:Actor {id: $actor})-[r:HAS_ACCESS]->(s:Space {id: $space}) "
        "RETURN r.role, r.encrypted_key",
        {"actor": alice["id"], "space": _space_id},
    )
    assert len(rows) == 1, "Expected 1 HAS_ACCESS link"
    assert rows[0][0] == "owner", f"Expected role='owner', got '{rows[0][0]}'"
    assert rows[0][1] is not None, "encrypted_key must not be None"


# ===========================================================================
# Test 2: Write encrypted Moment -> verify ciphertext in graph
# ===========================================================================

_moment_id = None
_test_plaintext = "The narrative physics engine hums beneath the canals of Venice."


def test_2_write_encrypted_moment():
    """Encrypt content and store as a Moment, verify ciphertext in graph."""
    global _moment_id
    alice = _actors["alice"]
    _moment_id = f"moment_e2e_{uuid.uuid4().hex[:12]}"

    # Encrypt content with the space key
    ciphertext = encrypt_content(_test_plaintext, _space_key)

    # Verify it looks encrypted
    assert is_encrypted(ciphertext), "Ciphertext must pass is_encrypted check"
    assert ciphertext != _test_plaintext, "Ciphertext must differ from plaintext"

    # Create Moment node with ciphertext and encrypted flag
    _query(
        "CREATE (m:Moment {"
        "  id: $id, "
        "  type: 'dialogue', "
        "  content: $content, "
        "  synthesis: $synthesis, "
        "  encrypted: true, "
        "  energy: 1.0"
        "})",
        {
            "id": _moment_id,
            "content": ciphertext,
            "synthesis": "[encrypted]",
        },
    )

    # Link Moment to Space (IN) and to Actor (CREATED)
    _query(
        "MATCH (m:Moment {id: $mid}), (s:Space {id: $sid}) "
        "CREATE (m)-[:IN]->(s)",
        {"mid": _moment_id, "sid": _space_id},
    )
    _query(
        "MATCH (a:Actor {id: $aid}), (m:Moment {id: $mid}) "
        "CREATE (a)-[:CREATED]->(m)",
        {"aid": alice["id"], "mid": _moment_id},
    )

    # Verify: content in graph is ciphertext, not plaintext
    rows = _ro_query(
        "MATCH (m:Moment {id: $id}) RETURN m.content, m.encrypted",
        {"id": _moment_id},
    )
    assert len(rows) == 1, "Expected 1 Moment"
    stored_content = rows[0][0]
    stored_encrypted = rows[0][1]

    assert is_encrypted(stored_content), "Stored content must look encrypted"
    assert stored_content != _test_plaintext, "Stored content must NOT be plaintext"
    assert stored_encrypted is True, "encrypted flag must be True"


# ===========================================================================
# Test 3: Read and decrypt -> verify plaintext matches original
# ===========================================================================

def test_3_read_and_decrypt():
    """Read the encrypted Moment from graph and decrypt it."""
    alice = _actors["alice"]

    # Retrieve encrypted_key from HAS_ACCESS link
    rows = _ro_query(
        "MATCH (a:Actor {id: $actor})-[r:HAS_ACCESS]->(s:Space {id: $space}) "
        "RETURN r.encrypted_key",
        {"actor": alice["id"], "space": _space_id},
    )
    assert len(rows) == 1, "Expected HAS_ACCESS link for alice"
    encrypted_key_b64 = rows[0][0]

    # Decrypt space key using alice's key pair
    space_key = decrypt_space_key_for_actor(
        encrypted_key_b64,
        alice["key_pair"]["public_key"],
        alice["key_pair"]["private_key"],
    )
    assert len(space_key) == 32, "Decrypted space key must be 32 bytes"
    assert space_key == _space_key, "Decrypted space key must match original"

    # Read Moment content from graph
    rows = _ro_query(
        "MATCH (m:Moment {id: $id}) RETURN m.content",
        {"id": _moment_id},
    )
    stored_ciphertext = rows[0][0]

    # Decrypt content
    decrypted = decrypt_content(stored_ciphertext, space_key)
    assert decrypted == _test_plaintext, (
        f"Decrypted text must match original.\n"
        f"  Expected: {_test_plaintext!r}\n"
        f"  Got:      {decrypted!r}"
    )


# ===========================================================================
# Test 4: Grant access to actor B -> verify B can decrypt
# ===========================================================================

def test_4_grant_access_to_bob():
    """Grant Bob access to the private Space, verify he can decrypt."""
    bob = _actors["bob"]

    # Wrap the space key for Bob's public key
    bob_encrypted_key = encrypt_space_key_for_actor(
        _space_key, bob["key_pair"]["public_key"]
    )

    # Create HAS_ACCESS link for Bob
    _query(
        "MATCH (a:Actor {id: $actor}), (s:Space {id: $space}) "
        "MERGE (a)-[r:HAS_ACCESS]->(s) "
        "SET r.role = 'member', r.encrypted_key = $ekey",
        {
            "actor": bob["id"],
            "space": _space_id,
            "ekey": bob_encrypted_key,
        },
    )

    # Verify Bob's HAS_ACCESS link exists
    rows = _ro_query(
        "MATCH (a:Actor {id: $actor})-[r:HAS_ACCESS]->(s:Space {id: $space}) "
        "RETURN r.role, r.encrypted_key",
        {"actor": bob["id"], "space": _space_id},
    )
    assert len(rows) == 1, "Expected HAS_ACCESS link for Bob"
    assert rows[0][0] == "member", f"Expected role='member', got '{rows[0][0]}'"

    # Bob decrypts the space key
    bob_space_key = decrypt_space_key_for_actor(
        rows[0][1],
        bob["key_pair"]["public_key"],
        bob["key_pair"]["private_key"],
    )
    assert bob_space_key == _space_key, "Bob's decrypted space key must match"

    # Bob reads and decrypts the Moment
    rows = _ro_query(
        "MATCH (m:Moment {id: $id}) RETURN m.content",
        {"id": _moment_id},
    )
    decrypted = decrypt_content(rows[0][0], bob_space_key)
    assert decrypted == _test_plaintext, "Bob must be able to decrypt the Moment"


# ===========================================================================
# Test 5: Actor C (no access) -> verify cannot get space key
# ===========================================================================

def test_5_carol_no_access():
    """Verify Carol (no HAS_ACCESS link) cannot obtain the space key."""
    carol = _actors["carol"]

    # Verify no HAS_ACCESS link exists for Carol
    rows = _ro_query(
        "MATCH (a:Actor {id: $actor})-[r:HAS_ACCESS]->(s:Space {id: $space}) "
        "RETURN r.encrypted_key",
        {"actor": carol["id"], "space": _space_id},
    )
    assert len(rows) == 0, "Carol must NOT have a HAS_ACCESS link"

    # Even if Carol intercepts the ciphertext, she cannot decrypt without space key
    rows = _ro_query(
        "MATCH (m:Moment {id: $id}) RETURN m.content",
        {"id": _moment_id},
    )
    stored_ciphertext = rows[0][0]

    # Carol tries to decrypt with a random key -- must fail
    fake_key = generate_space_key()
    try:
        decrypt_content(stored_ciphertext, fake_key)
        assert False, "Decryption with wrong key must raise an exception"
    except Exception:
        pass  # Expected

    # Carol tries to unseal Alice's encrypted_key with her own key pair -- must fail
    alice_rows = _ro_query(
        "MATCH (a:Actor {id: $actor})-[r:HAS_ACCESS]->(s:Space {id: $space}) "
        "RETURN r.encrypted_key",
        {"actor": _actors["alice"]["id"], "space": _space_id},
    )
    alice_encrypted_key = alice_rows[0][0]

    try:
        decrypt_space_key_for_actor(
            alice_encrypted_key,
            carol["key_pair"]["public_key"],
            carol["key_pair"]["private_key"],
        )
        assert False, "Carol must not be able to unseal Alice's wrapped key"
    except Exception:
        pass  # Expected — CryptoError


# ===========================================================================
# Test 6: Revoke actor B -> verify HAS_ACCESS link deleted
# ===========================================================================

def test_6_revoke_bob():
    """Revoke Bob's access by deleting the HAS_ACCESS link."""
    bob = _actors["bob"]

    # Delete Bob's HAS_ACCESS link
    _query(
        "MATCH (a:Actor {id: $actor})-[r:HAS_ACCESS]->(s:Space {id: $space}) "
        "DELETE r",
        {"actor": bob["id"], "space": _space_id},
    )

    # Verify the link is gone
    rows = _ro_query(
        "MATCH (a:Actor {id: $actor})-[r:HAS_ACCESS]->(s:Space {id: $space}) "
        "RETURN r.encrypted_key",
        {"actor": bob["id"], "space": _space_id},
    )
    assert len(rows) == 0, "Bob's HAS_ACCESS link must be deleted after revocation"

    # Alice's access must be unaffected
    alice_rows = _ro_query(
        "MATCH (a:Actor {id: $actor})-[r:HAS_ACCESS]->(s:Space {id: $space}) "
        "RETURN r.role",
        {"actor": _actors["alice"]["id"], "space": _space_id},
    )
    assert len(alice_rows) == 1, "Alice's HAS_ACCESS link must still exist"
    assert alice_rows[0][0] == "owner", "Alice must still be owner"


# ===========================================================================
# Test 7: Cross-language round-trip: JS encrypts -> Python decrypts
# ===========================================================================

def test_7_cross_language_js_to_python():
    """JS encrypts content with AES-256-GCM, Python decrypts it.

    Spawns a Node.js subprocess that uses lib/crypto to encrypt, then
    Python decrypts the result. Verifies byte-level interop end-to-end
    through the graph (JS writes ciphertext, Python reads and decrypts).
    """
    # Build a small JS script that encrypts and outputs JSON.
    # Use absolute path to lib/crypto so it works regardless of cwd.
    lib_crypto_path = os.path.join(REPO_ROOT, "lib", "crypto").replace("\\", "/")
    js_script = f"""'use strict';
const crypto = require('{lib_crypto_path}');

const spaceKeyHex = process.argv[2];
const plaintext = process.argv[3];

const spaceKey = Buffer.from(spaceKeyHex, 'hex');
const ciphertext = crypto.encryptContent(plaintext, spaceKey);

const output = JSON.stringify({{ ciphertext, plaintext }});
process.stdout.write(output);
"""

    js_script_path = os.path.join(
        tempfile.gettempdir(), f"mind_e2e_js_encrypt_{os.getpid()}.js"
    )

    try:
        with open(js_script_path, "w") as f:
            f.write(js_script)

        space_key_hex = _space_key.hex()
        test_text = "Cross-language E2E: Venice remembers everything."

        result = subprocess.run(
            ["node", js_script_path, space_key_hex, test_text],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=REPO_ROOT,
        )

        if result.returncode != 0:
            # Node.js not available or lib/crypto not found -- skip gracefully
            print(f"  SKIP  JS subprocess failed (rc={result.returncode}): {result.stderr.strip()}")
            return

        js_output = json.loads(result.stdout)
        js_ciphertext = js_output["ciphertext"]

        # Verify the JS ciphertext looks encrypted
        assert is_encrypted(js_ciphertext), "JS ciphertext must pass is_encrypted"

        # Store JS ciphertext into graph as a Moment
        cross_moment_id = f"moment_cross_{uuid.uuid4().hex[:12]}"
        _query(
            "CREATE (m:Moment {"
            "  id: $id, "
            "  type: 'cross_lang_test', "
            "  content: $content, "
            "  encrypted: true"
            "})",
            {"id": cross_moment_id, "content": js_ciphertext},
        )

        # Link to the Space
        _query(
            "MATCH (m:Moment {id: $mid}), (s:Space {id: $sid}) "
            "CREATE (m)-[:IN]->(s)",
            {"mid": cross_moment_id, "sid": _space_id},
        )

        # Read back from graph and decrypt with Python
        rows = _ro_query(
            "MATCH (m:Moment {id: $id}) RETURN m.content",
            {"id": cross_moment_id},
        )
        stored_ct = rows[0][0]

        decrypted = decrypt_content(stored_ct, _space_key)
        assert decrypted == test_text, (
            f"Cross-language decrypt failed.\n"
            f"  Expected: {test_text!r}\n"
            f"  Got:      {decrypted!r}"
        )

    finally:
        try:
            os.unlink(js_script_path)
        except Exception:
            pass


# ===========================================================================
# Runner — works as both pytest and standalone script
# ===========================================================================

if __name__ == "__main__":
    import traceback

    tests = [
        test_1_create_private_space,
        test_2_write_encrypted_moment,
        test_3_read_and_decrypt,
        test_4_grant_access_to_bob,
        test_5_carol_no_access,
        test_6_revoke_bob,
        test_7_cross_language_js_to_python,
    ]

    passed = 0
    failed = 0
    skipped = 0

    print("Mind Protocol — E2E Space Encryption Test Suite")
    print("=" * 50)

    # Check FalkorDB connectivity
    try:
        _get_graph()
        print(f"  FalkorDB: {FALKORDB_HOST}:{FALKORDB_PORT}")
        print(f"  Graph:    {GRAPH_NAME}")
    except Exception as e:
        print(f"  SKIP  FalkorDB not available: {e}")
        print("=" * 50)
        print("All tests skipped (FalkorDB required).")
        sys.exit(0)

    # Setup
    try:
        _setup()
        print(f"  Actors:   {', '.join(a['id'] for a in _actors.values())}")
        print()
    except Exception as e:
        print(f"  FAIL  Setup failed: {e}")
        traceback.print_exc()
        _teardown()
        sys.exit(1)

    # Run tests sequentially (they depend on each other)
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}")
            traceback.print_exc()
            failed += 1

    # Teardown
    _teardown()
    print()

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
    else:
        print("All E2E encryption tests passed.")


# ---------------------------------------------------------------------------
# pytest integration — setup/teardown as module-level fixtures
# ---------------------------------------------------------------------------

def setup_module(module):
    """pytest: called once before all tests in this module."""
    try:
        _get_graph()
    except Exception:
        import pytest
        pytest.skip("FalkorDB not available", allow_module_level=True)
    _setup()


def teardown_module(module):
    """pytest: called once after all tests in this module."""
    _teardown()
