"""
Mind Protocol Crypto — Python test suite.

Round-trip verification for all crypto modules:
  1. Space key encrypt/decrypt
  2. Actor key pair generate/store/load
  3. Key exchange (wrap/unwrap space key)
  4. is_encrypted detection

Run: python -m pytest tests/crypto/test_crypto.py -v
  or: python tests/crypto/test_crypto.py

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import logging
import os
import sys
import tempfile
import shutil

logger = logging.getLogger(__name__)

# Ensure the repo root is on sys.path so `python.crypto` resolves
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
# 1. Space key: round-trip encrypt / decrypt
# ---------------------------------------------------------------------------

def test_generate_space_key():
    key = generate_space_key()
    assert isinstance(key, bytes), "generate_space_key must return bytes"
    assert len(key) == 32, "space key must be 32 bytes"


def test_encrypt_decrypt_round_trip():
    key = generate_space_key()
    plaintext = "The graph breathes. Nodes pulse. Edges carry energy like blood."

    encrypted = encrypt_content(plaintext, key)
    assert isinstance(encrypted, str), "encrypt_content must return a string"
    assert encrypted.count(":") == 2, "ciphertext must have 3 colon-separated parts"

    decrypted = decrypt_content(encrypted, key)
    assert decrypted == plaintext, "decrypt must recover original plaintext"


def test_fresh_iv_each_call():
    key = generate_space_key()
    plaintext = "same input"
    ct1 = encrypt_content(plaintext, key)
    ct2 = encrypt_content(plaintext, key)
    assert ct1 != ct2, "two encryptions of the same plaintext must produce different ciphertext (fresh IV)"

    # Both must still decrypt correctly
    assert decrypt_content(ct1, key) == plaintext
    assert decrypt_content(ct2, key) == plaintext


def test_encrypt_wrong_key_size():
    try:
        encrypt_content("test", b"\x00" * 16)
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_decrypt_corrupted_ciphertext():
    key = generate_space_key()
    try:
        decrypt_content("bad:data:here", key)
        assert False, "should have raised an exception"
    except Exception as e:
        logger.debug("Expected failure decrypting corrupted ciphertext: %s", e)


def test_decrypt_wrong_key():
    key1 = generate_space_key()
    key2 = generate_space_key()
    ct = encrypt_content("secret", key1)
    try:
        decrypt_content(ct, key2)
        assert False, "should have raised an exception"
    except Exception as e:
        logger.debug("Expected failure decrypting with wrong key: %s", e)


# ---------------------------------------------------------------------------
# 2. is_encrypted detection
# ---------------------------------------------------------------------------

def test_is_encrypted_true_for_ciphertext():
    key = generate_space_key()
    ct = encrypt_content("test", key)
    assert is_encrypted(ct) is True, "is_encrypted must return True for ciphertext"


def test_is_encrypted_false_for_plaintext():
    assert is_encrypted("hello world") is False
    assert is_encrypted("") is False


def test_is_encrypted_false_for_two_parts():
    assert is_encrypted("a:b") is False


def test_is_encrypted_false_for_non_string():
    assert is_encrypted(123) is False  # type: ignore[arg-type]


def test_is_encrypted_true_for_valid_looking_base64():
    # Matches JS behavior: three base64 segments = True
    assert is_encrypted("abc:def:ghi") is True


# ---------------------------------------------------------------------------
# 3. Actor keys: generate / store / load
# ---------------------------------------------------------------------------

def test_generate_actor_key_pair():
    kp = generate_actor_key_pair()
    assert "public_key" in kp and "private_key" in kp
    assert isinstance(kp["public_key"], bytes) and len(kp["public_key"]) == 32
    assert isinstance(kp["private_key"], bytes) and len(kp["private_key"]) == 32


def test_store_and_load_actor_keys():
    kp = generate_actor_key_pair()
    tmp_dir = tempfile.mkdtemp(prefix="mind-crypto-test-")

    try:
        store_actor_keys(tmp_dir, kp)

        pub_path = os.path.join(tmp_dir, "public_key.b64")
        priv_path = os.path.join(tmp_dir, "private_key.b64")
        assert os.path.isfile(pub_path), "public_key.b64 must be written"
        assert os.path.isfile(priv_path), "private_key.b64 must be written"

        loaded = load_actor_keys(tmp_dir)
        assert loaded["public_key"] == kp["public_key"], "loaded public key must match"
        assert loaded["private_key"] == kp["private_key"], "loaded private key must match"
    finally:
        shutil.rmtree(tmp_dir)


def test_load_actor_keys_missing_dir():
    try:
        load_actor_keys("/tmp/nonexistent-mind-crypto-test-xyz")
        assert False, "should have raised an exception"
    except Exception as e:
        logger.debug("Expected failure loading keys from missing dir: %s", e)


# ---------------------------------------------------------------------------
# 4. Key exchange: wrap / unwrap space key
# ---------------------------------------------------------------------------

def test_key_exchange_round_trip():
    space_key = generate_space_key()
    actor = generate_actor_key_pair()

    wrapped = encrypt_space_key_for_actor(space_key, actor["public_key"])
    assert isinstance(wrapped, str), "wrapped key must be a base64 string"
    assert ":" not in wrapped, "sealed box must be a single base64 blob (no colons)"

    unwrapped = decrypt_space_key_for_actor(
        wrapped, actor["public_key"], actor["private_key"]
    )
    assert isinstance(unwrapped, bytes), "unwrapped key must be bytes"
    assert unwrapped == space_key, "unwrapped space key must match original"


def test_key_exchange_wrong_key_pair():
    space_key = generate_space_key()
    actor = generate_actor_key_pair()
    other = generate_actor_key_pair()

    wrapped = encrypt_space_key_for_actor(space_key, actor["public_key"])

    try:
        decrypt_space_key_for_actor(wrapped, other["public_key"], other["private_key"])
        assert False, "should have raised an exception"
    except Exception as e:
        logger.debug("Expected failure decrypting with wrong key pair: %s", e)


# ---------------------------------------------------------------------------
# Runner — so the file works both as pytest and as standalone script
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback

    tests = [
        test_generate_space_key,
        test_encrypt_decrypt_round_trip,
        test_fresh_iv_each_call,
        test_encrypt_wrong_key_size,
        test_decrypt_corrupted_ciphertext,
        test_decrypt_wrong_key,
        test_is_encrypted_true_for_ciphertext,
        test_is_encrypted_false_for_plaintext,
        test_is_encrypted_false_for_two_parts,
        test_is_encrypted_false_for_non_string,
        test_is_encrypted_true_for_valid_looking_base64,
        test_generate_actor_key_pair,
        test_store_and_load_actor_keys,
        test_load_actor_keys_missing_dir,
        test_key_exchange_round_trip,
        test_key_exchange_wrong_key_pair,
    ]

    passed = 0
    failed = 0

    print("Mind Protocol Crypto — Python Test Suite")
    print("=" * 42)

    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception:
            print(f"  FAIL  {t.__name__}")
            traceback.print_exc()
            failed += 1

    print("=" * 42)
    print(f"Results: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed.")
