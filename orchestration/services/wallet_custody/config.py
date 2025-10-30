"""
Configuration helpers for the Codex-C wallet custody service.

Reads process environment to configure storage paths, Solana connectivity,
and capability token validation secrets.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from orchestration.core.settings import Settings


@dataclass(frozen=True)
class WalletCustodySettings:
    """Runtime configuration required by the wallet custody service."""

    vault_dir: Path
    ledger_path: Path
    helius_rpc_url: str
    mind_mint_address: Optional[str]
    seed_amount_mind: int
    treasury_wallet_id: str
    keyring_service: str
    keyring_master_key_name: str
    keyring_backend: Optional[str]
    capability_secret: str
    capability_ttl_seconds: int
    capability_audience: str

    @classmethod
    def from_env(cls) -> "WalletCustodySettings":
        """Construct settings from the current environment."""
        project_root = Settings.PROJECT_ROOT
        vault_dir = Path(
            os.getenv(
                "WCS_VAULT_DIR",
                project_root / "data" / "wallet_custody" / "vault",
            )
        )
        ledger_path = Path(
            os.getenv(
                "WCS_LEDGER_PATH",
                project_root / "data" / "wallet_custody" / "ledger.jsonl",
            )
        )
        helius_api_key = os.getenv("HELIUS_API_KEY")
        default_rpc = (
            f"https://devnet.helius-rpc.com/?api-key={helius_api_key}"
            if helius_api_key
            else "https://api.devnet.solana.com"
        )
        helius_rpc_url = os.getenv("HELIUS_RPC_URL", default_rpc)
        mind_mint_address = os.getenv("MIND_TOKEN_MINT")
        seed_amount_mind = int(os.getenv("WCS_SEED_AMOUNT_MIND", "10"))
        treasury_wallet_id = os.getenv("WCS_TREASURY_ID", "org_treasury")
        keyring_service = os.getenv("WCS_KEYRING_SERVICE", "mind-protocol-wcs")
        keyring_master_key_name = os.getenv(
            "WCS_MASTER_KEY_NAME", "vault_master_private"
        )
        keyring_backend = os.getenv("WCS_KEYRING_BACKEND")
        capability_secret = os.getenv("WCS_CAPABILITY_SECRET", "")
        if not capability_secret:
            raise RuntimeError(
                "WCS_CAPABILITY_SECRET is required for capability token validation."
            )
        capability_ttl_seconds = int(os.getenv("WCS_CAPABILITY_TTL", "120"))
        capability_audience = os.getenv("WCS_CAPABILITY_AUDIENCE", "codex-c-wcs")

        return cls(
            vault_dir=vault_dir,
            ledger_path=ledger_path,
            helius_rpc_url=helius_rpc_url,
            mind_mint_address=mind_mint_address,
            seed_amount_mind=seed_amount_mind,
            treasury_wallet_id=treasury_wallet_id,
            keyring_service=keyring_service,
            keyring_master_key_name=keyring_master_key_name,
            keyring_backend=keyring_backend,
            capability_secret=capability_secret,
            capability_ttl_seconds=capability_ttl_seconds,
            capability_audience=capability_audience,
        )
