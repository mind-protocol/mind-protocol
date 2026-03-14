"""
Actor key pair management for Mind Protocol.

X25519 key generation, storage, and loading using PyNaCl.
Key files use the same .b64 format as the JS implementation
(base64-encoded raw 32-byte keys).

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import os
import base64

from nacl.public import PrivateKey


def generate_actor_key_pair() -> dict:
    """Generate an X25519 key pair for an actor.

    Returns:
        dict with keys:
            - "public_key": 32-byte public key (bytes)
            - "private_key": 32-byte private key (bytes)
    """
    private_key = PrivateKey.generate()
    public_key = private_key.public_key

    return {
        "public_key": bytes(public_key),
        "private_key": bytes(private_key),
    }


def store_actor_keys(keys_dir: str, key_pair: dict) -> None:
    """Write an actor's key pair to .b64 files on disk.

    Creates the directory if it does not exist. Writes two files:
        - <keys_dir>/public_key.b64   (base64 of 32 raw bytes)
        - <keys_dir>/private_key.b64  (base64 of 32 raw bytes)

    Args:
        keys_dir: Directory path where key files will be written.
        key_pair: dict with "public_key" and "private_key" as bytes.

    Raises:
        ValueError: If the key pair is missing required fields.
    """
    if "public_key" not in key_pair or "private_key" not in key_pair:
        raise ValueError("key_pair must contain 'public_key' and 'private_key'")

    os.makedirs(keys_dir, exist_ok=True)

    pub_b64 = base64.b64encode(key_pair["public_key"]).decode("ascii")
    priv_b64 = base64.b64encode(key_pair["private_key"]).decode("ascii")

    pub_path = os.path.join(keys_dir, "public_key.b64")
    priv_path = os.path.join(keys_dir, "private_key.b64")

    with open(pub_path, "w") as f:
        f.write(pub_b64)

    with open(priv_path, "w") as f:
        f.write(priv_b64)


def load_actor_keys(keys_dir: str) -> dict:
    """Load an actor's key pair from .b64 files on disk.

    Reads:
        - <keys_dir>/public_key.b64
        - <keys_dir>/private_key.b64

    Args:
        keys_dir: Directory containing the key files.

    Returns:
        dict with keys:
            - "public_key": 32-byte public key (bytes)
            - "private_key": 32-byte private key (bytes)

    Raises:
        FileNotFoundError: If either key file is missing.
        ValueError: If the decoded key lengths are incorrect.
    """
    pub_path = os.path.join(keys_dir, "public_key.b64")
    priv_path = os.path.join(keys_dir, "private_key.b64")

    with open(pub_path, "r") as f:
        pub_bytes = base64.b64decode(f.read().strip())

    with open(priv_path, "r") as f:
        priv_bytes = base64.b64decode(f.read().strip())

    if len(pub_bytes) != 32:
        raise ValueError(f"Public key must be 32 bytes, got {len(pub_bytes)}")
    if len(priv_bytes) != 32:
        raise ValueError(f"Private key must be 32 bytes, got {len(priv_bytes)}")

    return {
        "public_key": pub_bytes,
        "private_key": priv_bytes,
    }
