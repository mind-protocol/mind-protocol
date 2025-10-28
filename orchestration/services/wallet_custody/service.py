"""
Wallet Custody Service core implementation.

Handles wallet.ensure/sign/transfer events coming over the membrane bus.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from solana.rpc.api import Client
from solana.transaction import TransactionInstruction
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from orchestration.adapters.api.control_api import websocket_manager

from .capability_tokens import CapabilityTokenValidator
from .config import WalletCustodySettings
from .keyring_manager import MasterKeyMaterial, VaultKeyring
from .ledger import Ledger, LedgerEntry
from .solana_client import (
    SolanaRpcError,
    create_client,
    decode_instruction_blob,
    submit_instructions,
    submit_serialized_transaction,
    transfer_sol,
    transfer_token_2022,
)
from .vault_store import WalletRecord, WalletVault

logger = logging.getLogger(__name__)


class WalletNotFoundError(RuntimeError):
    """Raised when a referenced wallet does not exist."""


@dataclass
class WalletEnsureRequest:
    org: str
    subject: str
    identifier: str

    @property
    def wallet_id(self) -> str:
        return f"wallet:{self.subject}:{self.identifier}"


class WalletCustodyService:
    """Main entry point for custody operations."""

    def __init__(self, settings: WalletCustodySettings) -> None:
        self._settings = settings
        self._keyring = VaultKeyring(settings)
        self._master: MasterKeyMaterial = self._keyring.ensure_master_keypair()
        self._vault = WalletVault(settings.vault_dir, self._master.public_key)
        self._ledger = Ledger(settings.ledger_path)
        self._cap_validator = CapabilityTokenValidator(settings)
        self._client: Client = create_client(settings.helius_rpc_url)
        self._mind_mint_pubkey: Optional[Pubkey] = (
            Pubkey.from_string(settings.mind_mint_address)
            if settings.mind_mint_address
            else None
        )
        self._token_decimals = 9
        logger.info(
            "[WCS] Wallet custody service initialized (vault=%s, ledger=%s)",
            settings.vault_dir,
            settings.ledger_path,
        )

    # ------------------------------------------------------------------ helpers

    def _load_wallet(self, wallet_id: str) -> WalletRecord:
        if not self._vault.has_wallet(wallet_id):
            raise WalletNotFoundError(wallet_id)
        return self._vault.load_wallet(wallet_id)

    def _wallet_public_key(self, wallet: WalletRecord) -> Pubkey:
        return Pubkey.from_string(wallet.public_key)

    def _wallet_keypair(self, wallet: WalletRecord) -> Keypair:
        decrypted = self._vault.decrypt_private_key(wallet, self._master.private_key)
        return Keypair.from_bytes(decrypted)

    async def _broadcast(self, event: Dict[str, Any]) -> None:
        try:
            await websocket_manager.broadcast(event)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("[WCS] Failed to broadcast event %s: %s", event.get("type"), exc)

    def _append_ledger(self, entry_type: str, wallet_id: str, payload: Dict[str, Any]) -> None:
        try:
            entry = LedgerEntry.create(entry_type, wallet_id, payload)
            self._ledger.append(entry)
        except Exception as exc:  # pragma: no cover - ledger must not crash service
            logger.error("[WCS] Failed to append ledger entry: %s", exc)

    # ------------------------------------------------------------------ event handlers

    async def handle_wallet_ensure(self, org: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        request = WalletEnsureRequest(
            org=org,
            subject=payload["subject"],
            identifier=payload["id"],
        )
        wallet_id = request.wallet_id
        created = False

        if self._vault.has_wallet(wallet_id):
            record = self._vault.load_wallet(wallet_id)
        else:
            keypair = Keypair()
            record = self._vault.save_wallet(
                wallet_id=wallet_id,
                public_key=str(keypair.pubkey()),
                private_key_bytes=bytes(keypair),
                owner_type=request.subject,
                owner_id=request.identifier,
                origin_chain=payload.get("origin_chain"),
            )
            created = True
            self._append_ledger(
                "wallet.created",
                wallet_id,
                {"org": org, "subject": request.subject, "id": request.identifier},
            )

        broadcast_payload = {
            "type": "wallet.created@1.0",
            "org": org,
            "payload": {
                "subject": request.subject,
                "id": request.identifier,
                "address": record.public_key,
                "blockchain": "solana",
                "wallet_type": "eoa",
                "decimals": 9,
                "created": created,
            },
        }

        await self._broadcast(broadcast_payload)
        return broadcast_payload

    async def handle_wallet_transfer(self, org: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        request_mint = payload.get("mint")
        if not self._mind_mint_pubkey and request_mint:
            self._mind_mint_pubkey = Pubkey.from_string(request_mint)
        elif request_mint and self._mind_mint_pubkey:
            req_pubkey = Pubkey.from_string(request_mint)
            if req_pubkey != self._mind_mint_pubkey:
                raise ValueError("Mint mismatch with configured MIND mint")
        mint_pubkey = self._mind_mint_pubkey
        if not mint_pubkey:
            raise ValueError("MIND mint address is not configured")

        amount_mind = float(payload.get("amount_mind", 0.0))
        if amount_mind <= 0:
            raise ValueError("amount_mind must be greater than zero")
        lamports = int(payload.get("seed_sol_lamports") or 0)

        from_wallet = self._load_wallet(payload["from"])
        to_wallet = self._load_wallet(payload["to"])
        from_keypair = self._wallet_keypair(from_wallet)

        try:
            result_token = await asyncio.to_thread(
                transfer_token_2022,
                self._client,
                mint=mint_pubkey,
                source_owner=from_keypair,
                destination_owner=self._wallet_public_key(to_wallet),
                amount_mind=amount_mind,
                decimals=self._token_decimals,
            )
        except SolanaRpcError as exc:
            error_event = {
                "type": "wallet.transfer.result@1.0",
                "org": org,
                "payload": {
                    "ok": False,
                    "error": str(exc),
                    "from": payload["from"],
                    "to": payload["to"],
                    "amount_mind": amount_mind,
                },
            }
            await self._broadcast(error_event)
            return error_event

        sol_signature = None
        if lamports > 0:
            try:
                sol_result = await asyncio.to_thread(
                    transfer_sol,
                    self._client,
                    from_keypair=from_keypair,
                    to_pubkey=self._wallet_public_key(to_wallet),
                    lamports=lamports,
                )
            except SolanaRpcError as exc:
                error_event = {
                    "type": "wallet.transfer.result@1.0",
                    "org": org,
                    "payload": {
                        "ok": False,
                        "error": str(exc),
                        "from": payload["from"],
                        "to": payload["to"],
                        "amount_mind": amount_mind,
                        "seed_sol_lamports": lamports,
                    },
                }
                await self._broadcast(error_event)
                return error_event
            sol_signature = str(sol_result.signature)

        broadcast_payload = {
            "type": "wallet.transfer.result@1.0",
            "org": org,
            "payload": {
                "ok": True,
                "tx_ref": str(result_token.signature),
                "mint": str(mint_pubkey),
                "from": payload["from"],
                "to": payload["to"],
                "amount_mind": amount_mind,
                "seed_sol_lamports": lamports or None,
                "sol_tx": sol_signature,
                "memo": payload.get("memo"),
            },
        }

        self._append_ledger(
            "wallet.transfer",
            payload["from"],
            {
                "org": org,
                "to": payload["to"],
                "amount_mind": amount_mind,
                "seed_sol_lamports": lamports or 0,
                "tx_ref": str(result_token.signature),
                "sol_tx": sol_signature,
            },
        )

        await self._broadcast(broadcast_payload)
        return broadcast_payload

    async def handle_wallet_sign(self, org: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        citizen_id = payload["citizen_id"]
        token_raw = payload["capability_token"]

        token = self._cap_validator.decode(token_raw)
        CapabilityTokenValidator.ensure_capability(token, "wallet.sign")
        if token.citizen_id and token.citizen_id != citizen_id:
            raise PermissionError("Capability token bound to different citizen")

        wallet_id = f"wallet:citizen:{citizen_id}"
        wallet = self._load_wallet(wallet_id)
        keypair = self._wallet_keypair(wallet)

        mode = payload.get("mode")
        ttl_ms = int(payload.get("ttl_ms") or 0)
        if ttl_ms and ttl_ms < 0:
            raise ValueError("ttl_ms must be positive")

        recent_blockhash = payload.get("recent_blockhash")
        payer_str = payload.get("payer")
        payer = self._wallet_public_key(wallet) if not payer_str else Pubkey.from_string(payer_str)

        if payer_str and payer != self._wallet_public_key(wallet):
            logger.warning(
                "[WCS] Signing request uses external payer (%s) for wallet %s",
                payer_str,
                wallet_id,
            )

        instructions: Optional[list[TransactionInstruction]] = None
        tx_blob_bytes: Optional[bytes] = None

        if mode == "instrs":
            instr_dicts = payload.get("instrs", [])
            if not instr_dicts:
                raise ValueError("instrs array is required for mode=instrs")
            instructions = [decode_instruction_blob(ix) for ix in instr_dicts]
        elif mode == "tx_blob":
            blob_b64 = payload.get("tx_blob")
            if not blob_b64:
                raise ValueError("tx_blob missing in sign.request payload")
            tx_blob_bytes = base64.b64decode(blob_b64)
        else:
            raise ValueError("Unsupported sign mode")

        tx_signature = None
        if instructions:
            try:
                result = await asyncio.to_thread(
                    submit_instructions,
                    self._client,
                    instructions=instructions,
                    signers=[keypair],
                    payer=payer,
                    recent_blockhash=recent_blockhash,
                )
                tx_signature = str(result.signature)
            except SolanaRpcError as exc:
                return await self._signature_error(org, payload, str(exc))
        elif tx_blob_bytes:
            try:
                result = await asyncio.to_thread(
                    submit_serialized_transaction,
                    self._client,
                    transaction_blob=tx_blob_bytes,
                    signer=keypair,
                )
                tx_signature = str(result.signature)
            except SolanaRpcError as exc:
                return await self._signature_error(org, payload, str(exc))

        if not tx_signature:
            return await self._signature_error(org, payload, "signature_unavailable")

        mission_id = payload.get("mission_id")
        result_event = {
            "type": "wallet.signature.result@1.0",
            "org": org,
            "payload": {
                "ok": True,
                "sig": tx_signature,
                "tx_hash": tx_signature,
                "mode": mode,
            },
        }

        origin_chain = payload.get("origin_chain") or []
        if not isinstance(origin_chain, list):
            origin_chain = [origin_chain]

        attestation = {
            "type": "wallet.signature.attested@1.0",
            "org": org,
            "citizen_id": citizen_id,
            "mission_id": mission_id,
            "sig": tx_signature,
            "tx_hash": tx_signature,
            "origin_chain": origin_chain,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        self._append_ledger(
            "wallet.signature",
            wallet_id,
            {
                "org": org,
                "citizen_id": citizen_id,
                "mission_id": mission_id,
                "sig": tx_signature,
                "mode": mode,
            },
        )

        await self._broadcast(result_event)
        await self._broadcast(attestation)
        return result_event

    # ------------------------------------------------------------------ helpers

    async def _signature_error(self, org: str, payload: Dict[str, Any], error: str) -> Dict[str, Any]:
        event = {
            "type": "wallet.signature.result@1.0",
            "org": org,
            "payload": {
                "ok": False,
                "error": error,
                "mode": payload.get("mode"),
                "citizen_id": payload.get("citizen_id"),
            },
        }
        await self._broadcast(event)
        return event
