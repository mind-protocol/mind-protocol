"""
Space key encryption for Mind Protocol.

AES-256-GCM encryption using the `cryptography` package.
Ciphertext format: "base64(iv):base64(tag):base64(ciphertext)"
Cross-compatible with the JS implementation.

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import os
import re
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

IV_LENGTH = 12   # 96-bit nonce for AES-GCM
TAG_LENGTH = 16  # 128-bit authentication tag
KEY_LENGTH = 32  # 256-bit key


def generate_space_key() -> bytes:
    """Generate a random 256-bit (32-byte) AES key for space encryption.

    Returns:
        32 random bytes suitable for AES-256-GCM.
    """
    return os.urandom(KEY_LENGTH)


def encrypt_content(plaintext: str, key: bytes) -> str:
    """Encrypt plaintext using AES-256-GCM.

    A fresh IV is generated for every call, ensuring unique ciphertexts
    even for identical inputs.

    Args:
        plaintext: The string to encrypt.
        key: A 32-byte AES-256 key.

    Returns:
        Ciphertext in the format "base64(iv):base64(tag):base64(ciphertext)".

    Raises:
        ValueError: If the key length is not 32 bytes.
    """
    if len(key) != KEY_LENGTH:
        raise ValueError(f"Key must be {KEY_LENGTH} bytes, got {len(key)}")

    iv = os.urandom(IV_LENGTH)
    aesgcm = AESGCM(key)

    # AESGCM.encrypt appends the 16-byte tag to the ciphertext
    ct_with_tag = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)

    # Split: last TAG_LENGTH bytes are the tag, the rest is ciphertext
    ciphertext = ct_with_tag[:-TAG_LENGTH]
    tag = ct_with_tag[-TAG_LENGTH:]

    iv_b64 = base64.b64encode(iv).decode("ascii")
    tag_b64 = base64.b64encode(tag).decode("ascii")
    ct_b64 = base64.b64encode(ciphertext).decode("ascii")

    return f"{iv_b64}:{tag_b64}:{ct_b64}"


def decrypt_content(encrypted: str, key: bytes) -> str:
    """Decrypt an AES-256-GCM ciphertext string.

    Args:
        encrypted: Ciphertext in the format "base64(iv):base64(tag):base64(ciphertext)".
        key: The 32-byte AES-256 key used for encryption.

    Returns:
        The original plaintext string.

    Raises:
        ValueError: If the key length is wrong or the ciphertext format is invalid.
        cryptography.exceptions.InvalidTag: If decryption fails (wrong key or tampered data).
    """
    if len(key) != KEY_LENGTH:
        raise ValueError(f"Key must be {KEY_LENGTH} bytes, got {len(key)}")

    parts = encrypted.split(":")
    if len(parts) != 3:
        raise ValueError(
            f"Invalid ciphertext format: expected 3 colon-separated parts, got {len(parts)}"
        )

    iv = base64.b64decode(parts[0])
    tag = base64.b64decode(parts[1])
    ciphertext = base64.b64decode(parts[2])

    if len(iv) != IV_LENGTH:
        raise ValueError(f"IV must be {IV_LENGTH} bytes, got {len(iv)}")
    if len(tag) != TAG_LENGTH:
        raise ValueError(f"Tag must be {TAG_LENGTH} bytes, got {len(tag)}")

    aesgcm = AESGCM(key)

    # Reconstruct the format AESGCM.decrypt expects: ciphertext + tag
    plaintext_bytes = aesgcm.decrypt(iv, ciphertext + tag, None)
    return plaintext_bytes.decode("utf-8")


def is_encrypted(content: str) -> bool:
    """Detect whether a string looks like encrypted content.

    Matches the JS implementation: checks for exactly three colon-separated
    base64 segments (charset A-Za-z0-9+/=, at least one char each).
    Does NOT validate decoded lengths -- this is a format check, not a
    cryptographic validation.

    Args:
        content: The string to test.

    Returns:
        True if the string matches the ciphertext format, False otherwise.
    """
    if not isinstance(content, str):
        return False

    # Same regex logic as JS: three base64 segments separated by colons
    base64_segment = r"[A-Za-z0-9+/]+=*"
    pattern = rf"^{base64_segment}:{base64_segment}:{base64_segment}$"
    return bool(re.match(pattern, content))
