"""
Master key management backed by the host operating system keyring.

Uses libsodium (via PyNaCl) to generate an X25519 keypair that encrypts
individual wallet secrets stored in the custody vault. The private master key
is stored exclusively in the OS keyring (DPAPI / Keychain / libsecret) to keep
raw material out of workspace files and graphs.
"""

from __future__ import annotations

import base64
import importlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import keyring
from nacl.public import PrivateKey, PublicKey  # type: ignore

from .config import WalletCustodySettings

logger = logging.getLogger(__name__)


def _maybe_configure_backend(backend_path: Optional[str]) -> None:
    """Optionally override the default keyring backend."""
    if not backend_path:
        return
    module_path, _, class_name = backend_path.rpartition(".")
    if not module_path:
        raise ValueError(
            f"WCS_KEYRING_BACKEND must be a full import path, got {backend_path!r}"
        )
    module = importlib.import_module(module_path)
    backend_cls = getattr(module, class_name)
    keyring.set_keyring(backend_cls())
    logger.info("Wallet custody keyring backend configured: %s", backend_path)


@dataclass
class MasterKeyMaterial:
    """Holds master keypair used for sealed box operations."""

    public_key: PublicKey
    private_key: PrivateKey

    @property
    def public_b64(self) -> str:
        return base64.b64encode(bytes(self.public_key)).decode("ascii")

    @property
    def private_b64(self) -> str:
        return base64.b64encode(bytes(self.private_key)).decode("ascii")


class VaultKeyring:
    """Encapsulates master key bootstrap and retrieval."""

    def __init__(self, settings: WalletCustodySettings) -> None:
        self._settings = settings
        _maybe_configure_backend(settings.keyring_backend)
        self._master_public_path = settings.vault_dir / "master_public.key"
        self._service = settings.keyring_service
        self._secret_name = settings.keyring_master_key_name

    def ensure_master_keypair(self) -> MasterKeyMaterial:
        """
        Retrieve the custody master keypair, generating it on first run.

        Returns:
            MasterKeyMaterial containing libsodium X25519 keys.
        """
        private_b64 = keyring.get_password(self._service, self._secret_name)
        if private_b64:
            private_key = PrivateKey(base64.b64decode(private_b64))
            public_key = private_key.public_key
            if not self._master_public_path.exists():
                self._write_public_key(public_key)
            return MasterKeyMaterial(public_key=public_key, private_key=private_key)

        logger.info(
            "Wallet custody master key absent – generating new sealed box keypair"
        )
        private_key = PrivateKey.generate()
        public_key = private_key.public_key
        keyring.set_password(
            self._service, self._secret_name, base64.b64encode(bytes(private_key)).decode("ascii")
        )
        self._write_public_key(public_key)
        return MasterKeyMaterial(public_key=public_key, private_key=private_key)

    def _write_public_key(self, public_key: PublicKey) -> None:
        """Persist the public key alongside the vault for inspection and backup."""
        self._master_public_path.parent.mkdir(parents=True, exist_ok=True)
        self._master_public_path.write_text(
            base64.b64encode(bytes(public_key)).decode("ascii"), encoding="utf-8"
        )
        logger.info("Wallet custody master public key written to %s", self._master_public_path)

    def load_master_public_key(self) -> PublicKey:
        """Load the stored master public key (throws if missing)."""
        data = self._master_public_path.read_text(encoding="utf-8").strip()
        return PublicKey(base64.b64decode(data))
