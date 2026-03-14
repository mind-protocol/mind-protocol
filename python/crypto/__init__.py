"""
Mind Protocol — Python Crypto Library

AES-256-GCM space encryption, X25519 actor key management,
and sealed-box key exchange. Cross-compatible with the JS implementation.

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

from .space_key import (
    generate_space_key,
    encrypt_content,
    decrypt_content,
    is_encrypted,
    IV_LENGTH,
    TAG_LENGTH,
    KEY_LENGTH,
)

from .actor_keys import (
    generate_actor_key_pair,
    store_actor_keys,
    load_actor_keys,
)

from .key_exchange import (
    encrypt_space_key_for_actor,
    decrypt_space_key_for_actor,
)

from .key_cache import SpaceKeyCache

__all__ = [
    # space_key
    "generate_space_key",
    "encrypt_content",
    "decrypt_content",
    "is_encrypted",
    "IV_LENGTH",
    "TAG_LENGTH",
    "KEY_LENGTH",
    # actor_keys
    "generate_actor_key_pair",
    "store_actor_keys",
    "load_actor_keys",
    # key_exchange
    "encrypt_space_key_for_actor",
    "decrypt_space_key_for_actor",
    # key_cache
    "SpaceKeyCache",
]
