"""
Helpers for interacting with Solana via the Helius RPC endpoint.

This module provides thin wrappers around solana-py to:
- derive associated token accounts for Token-2022 SPL tokens
- submit SOL + SPL token transfers
- serialize and send transactions built from arbitrary instructions
"""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from typing import Sequence

from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solana.transaction import AccountMeta, Transaction, TransactionInstruction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.system_program import TransferParams, transfer
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID
from spl.token.instructions import (
    create_associated_token_account,
    get_associated_token_address,
    transfer_checked,
)

logger = logging.getLogger(__name__)


class SolanaRpcError(RuntimeError):
    """Raised when the Solana RPC returns an error."""


@dataclass
class TransactionResult:
    """Outcome of a submitted Solana transaction."""

    signature: Signature
    slot: int
    result_meta: dict


def create_client(rpc_url: str) -> Client:
    """Instantiate a synchronous Solana RPC client."""
    return Client(rpc_url, commitment=Confirmed)


def _parse_response(resp: dict) -> dict:
    error = resp.get("error")
    if error:
        raise SolanaRpcError(str(error))
    return resp["result"]


def ensure_associated_token_account(
    client: Client,
    *,
    owner: Pubkey,
    mint: Pubkey,
    payer: Keypair,
) -> Pubkey:
    """
    Ensure the associated token account exists for the given owner + mint.

    Returns:
        Associated token account public key.
    """
    ata = get_associated_token_address(
        owner,
        mint,
        program_id=TOKEN_2022_PROGRAM_ID,
        associated_token_program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
    )

    account_info = client.get_account_info(ata)
    if account_info.get("result", {}).get("value"):
        return ata

    instruction = create_associated_token_account(
        payer=payer.pubkey(),
        owner=owner,
        mint=mint,
        program_id=TOKEN_2022_PROGRAM_ID,
        associated_token_program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
    )

    latest = client.get_latest_blockhash()
    blockhash = _parse_response(latest)["value"]["blockhash"]

    transaction = Transaction(recent_blockhash=blockhash, fee_payer=payer.pubkey())
    transaction.add(instruction)
    transaction.sign(payer)

    send_resp = client.send_raw_transaction(
        bytes(transaction.serialize()),
        opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed),
    )
    result = _parse_response(send_resp)
    logger.info("Created associated token account %s (tx=%s)", ata, result)
    client.confirm_transaction(result, commitment=Confirmed)
    return ata


def submit_instructions(
    client: Client,
    *,
    instructions: Sequence[TransactionInstruction],
    signers: Sequence[Keypair],
    payer: Pubkey,
    recent_blockhash: str | None = None,
) -> TransactionResult:
    """Build, sign, and submit a transaction from arbitrary instructions."""
    if not instructions:
        raise ValueError("No instructions provided for transaction submission")

    if recent_blockhash is None:
        latest = client.get_latest_blockhash()
        recent_blockhash = _parse_response(latest)["value"]["blockhash"]

    transaction = Transaction(recent_blockhash=recent_blockhash, fee_payer=payer)
    for ix in instructions:
        transaction.add(ix)

    transaction.sign(*signers)
    raw_tx = transaction.serialize()
    send_resp = client.send_raw_transaction(
        bytes(raw_tx),
        opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed),
    )
    signature = Signature.from_string(_parse_response(send_resp))

    # Wait for confirmation
    confirm = client.confirm_transaction(signature, commitment=Confirmed)
    if isinstance(confirm, bool):
        slot = 0
        confirm_meta = {"confirmed": confirm}
    else:
        confirm_meta = _parse_response(confirm)
        slot = confirm_meta.get("context", {}).get("slot", 0)

    return TransactionResult(signature=signature, slot=slot, result_meta=confirm_meta)


def decode_instruction_blob(instr: dict) -> TransactionInstruction:
    """Decode a JSON instruction payload into a TransactionInstruction."""
    program_id = Pubkey.from_string(instr["programId"])

    accounts = [
        AccountMeta(
            pubkey=Pubkey.from_string(acc["pubkey"]),
            is_signer=bool(acc.get("isSigner")),
            is_writable=bool(acc.get("isWritable")),
        )
        for acc in instr.get("accounts", [])
    ]

    data_b64 = instr.get("data", "")
    data = base64.b64decode(data_b64) if data_b64 else bytes()

    return TransactionInstruction(program_id=program_id, keys=accounts, data=data)


def transfer_token_2022(
    client: Client,
    *,
    mint: Pubkey,
    source_owner: Keypair,
    destination_owner: Pubkey,
    amount_mind: float,
    decimals: int,
) -> TransactionResult:
    """
    Transfer SPL Token-2022 tokens between wallets, ensuring ATAs first.
    """
    payer = source_owner
    source_ata = ensure_associated_token_account(client, owner=payer.pubkey(), mint=mint, payer=payer)
    destination_ata = ensure_associated_token_account(
        client, owner=destination_owner, mint=mint, payer=payer
    )

    amount = int(round(amount_mind * (10 ** decimals)))
    instruction = transfer_checked(
        program_id=TOKEN_2022_PROGRAM_ID,
        source=source_ata,
        mint=mint,
        dest=destination_ata,
        owner=payer.pubkey(),
        amount=amount,
        decimals=decimals,
        signers=[],
    )

    return submit_instructions(
        client,
        instructions=[instruction],
        signers=[payer],
        payer=payer.pubkey(),
    )


def transfer_sol(
    client: Client,
    *,
    from_keypair: Keypair,
    to_pubkey: Pubkey,
    lamports: int,
) -> TransactionResult:
    """Transfer raw SOL between accounts."""
    params = TransferParams(
        from_pubkey=from_keypair.pubkey(),
        to_pubkey=to_pubkey,
        lamports=lamports,
    )
    instruction = transfer(params)
    return submit_instructions(
        client,
        instructions=[instruction],
        signers=[from_keypair],
        payer=from_keypair.pubkey(),
    )


def submit_serialized_transaction(
    client: Client,
    *,
    transaction_blob: bytes,
    signer: Keypair,
) -> TransactionResult:
    """Sign and submit a serialized transaction message."""
    transaction = Transaction.deserialize(transaction_blob)
    transaction.sign(signer)
    raw_tx = transaction.serialize()
    send_resp = client.send_raw_transaction(
        bytes(raw_tx),
        opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed),
    )
    signature = Signature.from_string(_parse_response(send_resp))
    confirm = client.confirm_transaction(signature, commitment=Confirmed)
    if isinstance(confirm, bool):
        slot = 0
        confirm_meta = {"confirmed": confirm}
    else:
        confirm_meta = _parse_response(confirm)
        slot = confirm_meta.get("context", {}).get("slot", 0)

    return TransactionResult(signature=signature, slot=slot, result_meta=confirm_meta)
