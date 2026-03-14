"""
Cross-language crypto verifier + generator (Python side).

Reads JS-produced artifacts, verifies Python can decrypt them,
then generates its own encrypted artifacts for JS to verify.

Covers 6 critical paths (Python side of 1, 3, 5 + generates for 2, 4, 6):

  Path 1: JS encryptContent        -> Py decrypt_content        (AES-256-GCM)
  Path 3: JS encryptSpaceKeyForActor -> Py decrypt_space_key     (Sealed box)
  Path 5: JS storeActorKeys        -> Py load_actor_keys        (Key file format)
  Generates artifacts for:
  Path 2: Py encrypt_content        -> JS decryptContent
  Path 4: Py encrypt_space_key      -> JS decryptSpaceKeyForActor
  Path 6: Py store_actor_keys       -> JS loadActorKeys

Run: python3 tests/crypto/test_cross_language_verify.py --input <file> --output <file>

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import argparse
import json
import os
import sys
import tempfile

# Ensure repo root is on path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.crypto import (
    encrypt_content,
    decrypt_content,
    generate_space_key,
    generate_actor_key_pair,
    store_actor_keys,
    load_actor_keys,
    encrypt_space_key_for_actor,
    decrypt_space_key_for_actor,
)

passed = 0
failed = 0


def assert_test(condition: bool, label: str) -> None:
    global passed, failed
    if condition:
        print(f"  PASS  {label}")
        passed += 1
    else:
        print(f"  FAIL  {label}")
        failed += 1


def verify_js_artifacts(js_data: dict) -> None:
    """Verify Python can consume JS-produced crypto artifacts."""

    # --- Path 1: JS encryptContent -> Py decrypt_content (AES-256-GCM) ---
    print("\n  Path 1: JS encryptContent -> Py decrypt_content (AES-256-GCM)")

    space_key = bytes.fromhex(js_data["aes_gcm"]["space_key_hex"])

    for item in js_data["aes_gcm"]["encrypted"]:
        plaintext = item["plaintext"]
        ciphertext = item["ciphertext"]
        label = f'Py decrypts JS ciphertext: "{plaintext[:40]}..."'
        try:
            decrypted = decrypt_content(ciphertext, space_key)
            assert_test(decrypted == plaintext, label)
        except Exception as e:
            assert_test(False, f"{label} -- {e}")

    # --- Path 3: JS encryptSpaceKeyForActor -> Py decrypt_space_key (Sealed box) ---
    print("\n  Path 3: JS encryptSpaceKeyForActor -> Py decrypt_space_key (Sealed box)")

    sb = js_data["sealed_box"]
    seal_space_key = bytes.fromhex(sb["space_key_hex"])
    actor_pub = bytes.fromhex(sb["actor_public_key_hex"])
    actor_priv = bytes.fromhex(sb["actor_private_key_hex"])
    wrapped = sb["wrapped_key_b64"]

    try:
        unwrapped = decrypt_space_key_for_actor(wrapped, actor_pub, actor_priv)
        assert_test(
            unwrapped == seal_space_key,
            "Py unwraps JS sealed box -- space key matches",
        )
    except Exception as e:
        assert_test(False, f"Py unwraps JS sealed box -- {e}")

    # --- Path 5: JS storeActorKeys -> Py load_actor_keys (Key file format) ---
    print("\n  Path 5: JS storeActorKeys -> Py load_actor_keys (Key file format)")

    kf = js_data["key_files"]
    js_keys_dir = kf["js_keys_dir"]
    expected_pub = bytes.fromhex(kf["actor_public_key_hex"])
    expected_priv = bytes.fromhex(kf["actor_private_key_hex"])

    if os.path.isdir(js_keys_dir):
        try:
            loaded = load_actor_keys(js_keys_dir)
            assert_test(
                loaded["public_key"] == expected_pub,
                "Py loads JS public key file -- matches",
            )
            assert_test(
                loaded["private_key"] == expected_priv,
                "Py loads JS private key file -- matches",
            )
        except Exception as e:
            assert_test(False, f"Py loads JS key files -- {e}")
    else:
        assert_test(False, f"JS keys dir not found: {js_keys_dir}")


def generate_py_artifacts() -> dict:
    """Generate Python-side crypto artifacts for JS to verify."""

    # --- AES-256-GCM: Py encrypts for JS to decrypt (Path 2) ---
    space_key = generate_space_key()
    space_key_hex = space_key.hex()

    test_strings = [
        "The graph breathes. Nodes pulse. Edges carry energy like blood.",
        "",
        "Unicode test: \u00e8 \u00e0 \u00f2 \u00f9 \U0001f3ad \U0001f31f \U0001f3e0",
    ]

    encrypted = []
    for pt in test_strings:
        ct = encrypt_content(pt, space_key)
        encrypted.append({"plaintext": pt, "ciphertext": ct})

    # --- Sealed box: Py wraps for JS to unwrap (Path 4) ---
    actor_kp = generate_actor_key_pair()
    wrapped = encrypt_space_key_for_actor(space_key, actor_kp["public_key"])

    # --- Key files: Py stores for JS to load (Path 6) ---
    py_keys_dir = tempfile.mkdtemp(prefix="mind-cross-py-keys-")
    store_actor_keys(py_keys_dir, actor_kp)

    return {
        "aes_gcm": {
            "space_key_hex": space_key_hex,
            "encrypted": encrypted,
        },
        "sealed_box": {
            "space_key_hex": space_key_hex,
            "actor_public_key_hex": actor_kp["public_key"].hex(),
            "actor_private_key_hex": actor_kp["private_key"].hex(),
            "wrapped_key_b64": wrapped,
        },
        "key_files": {
            "py_keys_dir": py_keys_dir,
            "actor_public_key_hex": actor_kp["public_key"].hex(),
            "actor_private_key_hex": actor_kp["private_key"].hex(),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Cross-language crypto verifier (Python side)"
    )
    parser.add_argument(
        "--input", required=True, help="Path to JS-produced artifacts JSON"
    )
    parser.add_argument(
        "--output", required=True, help="Path to write Python-produced artifacts JSON"
    )
    args = parser.parse_args()

    print("Mind Protocol Crypto -- Python Cross-Language Verifier")
    print("=" * 55)

    # Step 1: Read and verify JS artifacts
    with open(args.input, "r") as f:
        js_data = json.load(f)

    verify_js_artifacts(js_data)

    # Step 2: Generate Python artifacts for JS to verify
    print("\n--- Python generates artifacts for JS ---")
    py_artifacts = generate_py_artifacts()

    with open(args.output, "w") as f:
        json.dump(py_artifacts, f, indent=2, ensure_ascii=False)
    print(f"  Python artifacts written to {args.output}")

    # Summary
    print("\n" + "=" * 55)
    print(f"Python verifier results: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
    else:
        print("All Python verifications passed.")


if __name__ == "__main__":
    main()
