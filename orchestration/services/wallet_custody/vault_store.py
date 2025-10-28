"""
Local wallet vault persistence with sealed box encryption.

Each wallet record is stored as JSON under the configured vault directory:
    vault/<wallet_id>.json

The private key blob is encrypted with libsodium SealedBox using the master
public key. The corresponding master private key is fetched from the OS
keyring on demand to decrypt for signing operations.
"""

from __future__ import annotations

import base64
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Optional

from nacl.public import PrivateKey, PublicKey, SealedBox  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class WalletRecord:
    """Metadata describing a custody wallet."""

    wallet_id: str
    public_key: str
    encrypted_private_key: str
    created_at: str
    owner_type: str
    owner_id: str
    origin_chain: Optional[Iterable[str]] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "WalletRecord":
        required = {"wallet_id", "public_key", "encrypted_private_key", "created_at", "owner_type", "owner_id"}
        missing = required - payload.keys()
        if missing:
            raise ValueError(f"Wallet record missing fields: {', '.join(sorted(missing))}")
        return cls(
            wallet_id=str(payload["wallet_id"]),
            public_key=str(payload["public_key"]),
            encrypted_private_key=str(payload["encrypted_private_key"]),
            created_at=str(payload["created_at"]),
            owner_type=str(payload["owner_type"]),
            owner_id=str(payload["owner_id"]),
            origin_chain=list(payload.get("origin_chain") or []),
        )


class WalletVault:
    """Filesystem-backed wallet vault."""

    def __init__(self, vault_dir: Path, master_public: PublicKey) -> None:
        self._vault_dir = vault_dir
        self._vault_dir.mkdir(parents=True, exist_ok=True)
        self._seal_box = SealedBox(master_public)

    def _path_for(self, wallet_id: str) -> Path:
        return self._vault_dir / f"{wallet_id}.json"

    def has_wallet(self, wallet_id: str) -> bool:
        return self._path_for(wallet_id).exists()

    def save_wallet(
        self,
        wallet_id: str,
        public_key: str,
        private_key_bytes: bytes,
        *,
        owner_type: str,
        owner_id: str,
        origin_chain: Optional[Iterable[str]] = None,
    ) -> WalletRecord:
        if self.has_wallet(wallet_id):
            raise ValueError(f"Wallet {wallet_id} already exists in vault")

        encrypted_private = self._seal_box.encrypt(private_key_bytes)
        record = WalletRecord(
            wallet_id=wallet_id,
            public_key=public_key,
            encrypted_private_key=base64.b64encode(encrypted_private).decode("ascii"),
            created_at=datetime.now(timezone.utc).isoformat(),
            owner_type=owner_type,
            owner_id=owner_id,
            origin_chain=list(origin_chain or []),
        )
        path = self._path_for(wallet_id)
        path.write_text(record.to_json(), encoding="utf-8")
        logger.info("Stored wallet %s (owner=%s:%s)", wallet_id, owner_type, owner_id)
        return record

    def load_wallet(self, wallet_id: str) -> WalletRecord:
        path = self._path_for(wallet_id)
        data = json.loads(path.read_text(encoding="utf-8"))
        return WalletRecord.from_dict(data)

    def decrypt_private_key(self, wallet: WalletRecord, master_private: PrivateKey) -> bytes:
        sealed_box = SealedBox(master_private)
        decrypted = sealed_box.decrypt(base64.b64decode(wallet.encrypted_private_key))
        return decrypted

    def list_wallet_ids(self) -> Iterable[str]:
        for file in self._vault_dir.glob("*.json"):
            yield file.stem
