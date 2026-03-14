"""
Key exchange for Mind Protocol.

Sealed-box encryption for wrapping/unwrapping space keys per actor.
Uses PyNaCl's SealedBox (X25519 + XSalsa20-Poly1305) for anonymous
public-key encryption. Byte-compatible with JS libsodium sealed boxes.

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import base64

from nacl.public import PublicKey, PrivateKey, SealedBox


def encrypt_space_key_for_actor(space_key: bytes, actor_public_key: bytes) -> str:
    """Encrypt a space key so only the target actor can decrypt it.

    Uses a sealed box: the sender is anonymous and only the holder of the
    corresponding private key can open the box.

    Args:
        space_key: The raw space key bytes (typically 32 bytes for AES-256).
        actor_public_key: The actor's 32-byte X25519 public key.

    Returns:
        A base64-encoded string containing the sealed box ciphertext.

    Raises:
        ValueError: If the public key is not 32 bytes.
    """
    if len(actor_public_key) != 32:
        raise ValueError(
            f"Actor public key must be 32 bytes, got {len(actor_public_key)}"
        )

    pub = PublicKey(actor_public_key)
    sealed_box = SealedBox(pub)
    encrypted = sealed_box.encrypt(space_key)

    return base64.b64encode(encrypted).decode("ascii")


def decrypt_space_key_for_actor(
    encrypted_key: str,
    actor_public_key: bytes,
    actor_private_key: bytes,
) -> bytes:
    """Decrypt a sealed-box-wrapped space key using the actor's key pair.

    Args:
        encrypted_key: Base64-encoded sealed box ciphertext.
        actor_public_key: The actor's 32-byte X25519 public key.
        actor_private_key: The actor's 32-byte X25519 private key.

    Returns:
        The decrypted space key bytes.

    Raises:
        ValueError: If key lengths are incorrect.
        nacl.exceptions.CryptoError: If decryption fails.
    """
    if len(actor_public_key) != 32:
        raise ValueError(
            f"Actor public key must be 32 bytes, got {len(actor_public_key)}"
        )
    if len(actor_private_key) != 32:
        raise ValueError(
            f"Actor private key must be 32 bytes, got {len(actor_private_key)}"
        )

    priv = PrivateKey(actor_private_key)
    sealed_box = SealedBox(priv)

    ciphertext = base64.b64decode(encrypted_key)
    return sealed_box.decrypt(ciphertext)
