# economy/token/spl_token_2022_mint_creator.py
#
# DOCS: docs/economy/token/SPL_TOKEN_2022_SPECS.md
#
# Creates $MIND token using SPL Token 2022 with extensions.
# CRITICAL: Extensions must be activated at creation - cannot be added later.
#
# Extensions activated:
# - TransferFeeConfig: 1% baseline protocol fee
# - TransferHook: Custom logic on each transfer (layer fees, dormancy check)
# - MetadataPointer: Points to on-chain metadata
# - TokenMetadata: Name, symbol, URI on-chain
# - MintCloseAuthority: Option to close the mint
#
# NOT activated (by design):
# - PermanentDelegate: Too much centralized power
# - freezeAuthority: Set to null for censorship resistance

from dataclasses import dataclass
from typing import Optional
import json
import subprocess
import hashlib
import time

from .constants import (
    TOKEN_2022_PROGRAM_ID,
    TOKEN_NAME,
    TOKEN_SYMBOL,
    TOKEN_DECIMALS,
    TOKEN_URI,
    TRANSFER_FEE_BASIS_POINTS,
    TRANSFER_FEE_MAX,
    TRANSFER_HOOK_PROGRAM_ID,
    EXTENSIONS_TO_ACTIVATE,
    RPC_ENDPOINTS,
    validate_configuration,
)


@dataclass
class Token2022Config:
    """Configuration for Token 2022 creation."""

    # Network
    network: str = "devnet"

    # Authorities (public keys as base58 strings)
    mint_authority: Optional[str] = None
    transfer_fee_authority: Optional[str] = None
    withdraw_withheld_authority: Optional[str] = None
    transfer_hook_authority: Optional[str] = None
    metadata_authority: Optional[str] = None
    mint_close_authority: Optional[str] = None

    # Transfer Hook Program (must be deployed first!)
    transfer_hook_program_id: Optional[str] = None

    # Keypair for signing
    payer_keypair_path: Optional[str] = None

    # Mode
    dry_run: bool = True

    @property
    def rpc_url(self) -> str:
        return RPC_ENDPOINTS.get(self.network, RPC_ENDPOINTS["devnet"])


@dataclass
class Token2022CreationResult:
    """Result of token creation."""

    success: bool
    mint_address: Optional[str] = None
    extensions_activated: list = None
    tx_signatures: list = None
    error: Optional[str] = None
    dry_run: bool = True

    def __post_init__(self):
        if self.extensions_activated is None:
            self.extensions_activated = []
        if self.tx_signatures is None:
            self.tx_signatures = []


class Token2022MintCreator:
    """
    Creates $MIND token with SPL Token 2022 extensions.

    IMPORTANT: Call validate_pre_deployment() before create_token().
    Extensions cannot be added after token creation.

    Usage:
        config = Token2022Config(
            network="devnet",
            mint_authority="...",
            transfer_hook_program_id="...",
            payer_keypair_path="/path/to/keypair.json",
        )
        creator = Token2022MintCreator(config)

        # Validate first
        is_valid, issues = creator.validate_pre_deployment()
        if not is_valid:
            print(f"Issues: {issues}")
            return

        # Create token
        result = creator.create_token()
    """

    def __init__(self, config: Token2022Config):
        self.config = config
        self.results: list[str] = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        prefix = {"INFO": "[*]", "SUCCESS": "[+]", "ERROR": "[-]", "WARN": "[!]"}
        full_msg = f"{prefix.get(level, '[*]')} {message}"
        print(full_msg)
        self.results.append(full_msg)

    def validate_pre_deployment(self) -> tuple[bool, list[str]]:
        """
        Validate configuration before deployment.

        Returns (is_valid, list of issues).
        """
        issues = []

        # Check transfer hook program is deployed
        if not self.config.transfer_hook_program_id:
            issues.append(
                "transfer_hook_program_id not set. "
                "Deploy TransferHook program first, then set this value."
            )

        # Check authorities are set
        if not self.config.mint_authority:
            issues.append("mint_authority not configured")

        if not self.config.transfer_fee_authority:
            issues.append("transfer_fee_authority not configured")

        if not self.config.withdraw_withheld_authority:
            issues.append("withdraw_withheld_authority not configured")

        # Check payer keypair
        if not self.config.payer_keypair_path and not self.config.dry_run:
            issues.append("payer_keypair_path required for live deployment")

        # Check network
        if self.config.network not in RPC_ENDPOINTS:
            issues.append(f"Unknown network: {self.config.network}")

        return (len(issues) == 0, issues)

    def _generate_mock_address(self, seed: str) -> str:
        """Generate a mock address for dry runs."""
        return hashlib.sha256(f"{seed}{time.time()}".encode()).hexdigest()[:44]

    def _generate_typescript_code(self) -> str:
        """
        Generate TypeScript code for token creation.

        This code should be run with @solana/web3.js and @solana/spl-token.
        """
        return f'''
// Token 2022 Creation Script for $MIND
// Run with: npx ts-node create_mind_token.ts

import {{
  Connection,
  Keypair,
  PublicKey,
  SystemProgram,
  Transaction,
  sendAndConfirmTransaction,
}} from "@solana/web3.js";
import {{
  TOKEN_2022_PROGRAM_ID,
  ExtensionType,
  createInitializeMintInstruction,
  createInitializeTransferFeeConfigInstruction,
  createInitializeTransferHookInstruction,
  createInitializeMetadataPointerInstruction,
  getMintLen,
  createInitializeMintCloseAuthorityInstruction,
}} from "@solana/spl-token";
import {{
  createInitializeInstruction as createInitializeMetadataInstruction,
}} from "@solana/spl-token-metadata";
import * as fs from "fs";

const RPC_URL = "{self.config.rpc_url}";
const TRANSFER_HOOK_PROGRAM_ID = "{self.config.transfer_hook_program_id or 'YOUR_TRANSFER_HOOK_PROGRAM_ID'}";

async function createMindToken() {{
  const connection = new Connection(RPC_URL, "confirmed");

  // Load payer keypair
  const payerKeypair = Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(fs.readFileSync("{self.config.payer_keypair_path or 'PATH_TO_KEYPAIR'}").toString()))
  );

  // Generate mint keypair
  const mintKeypair = Keypair.generate();

  // Calculate mint account size with extensions
  const extensions = [
    ExtensionType.TransferFeeConfig,
    ExtensionType.TransferHook,
    ExtensionType.MetadataPointer,
    ExtensionType.MintCloseAuthority,
  ];
  const mintLen = getMintLen(extensions) + 256; // Extra space for metadata

  // Get rent exemption
  const lamports = await connection.getMinimumBalanceForRentExemption(mintLen);

  // 1. Create account instruction
  const createAccountIx = SystemProgram.createAccount({{
    fromPubkey: payerKeypair.publicKey,
    newAccountPubkey: mintKeypair.publicKey,
    space: mintLen,
    lamports,
    programId: TOKEN_2022_PROGRAM_ID,
  }});

  // 2. Initialize TransferFeeConfig
  const initTransferFeeIx = createInitializeTransferFeeConfigInstruction(
    mintKeypair.publicKey,
    payerKeypair.publicKey,  // transferFeeAuthority
    payerKeypair.publicKey,  // withdrawWithheldAuthority
    {TRANSFER_FEE_BASIS_POINTS},  // feeBasisPoints (1%)
    BigInt({TRANSFER_FEE_MAX}),   // maxFee
    TOKEN_2022_PROGRAM_ID
  );

  // 3. Initialize TransferHook
  const initTransferHookIx = createInitializeTransferHookInstruction(
    mintKeypair.publicKey,
    payerKeypair.publicKey,  // transferHookAuthority
    new PublicKey(TRANSFER_HOOK_PROGRAM_ID),
    TOKEN_2022_PROGRAM_ID
  );

  // 4. Initialize MetadataPointer (self-referencing)
  const initMetadataPointerIx = createInitializeMetadataPointerInstruction(
    mintKeypair.publicKey,
    payerKeypair.publicKey,  // metadataAuthority
    mintKeypair.publicKey,   // metadata stored in mint itself
    TOKEN_2022_PROGRAM_ID
  );

  // 5. Initialize MintCloseAuthority
  const initMintCloseIx = createInitializeMintCloseAuthorityInstruction(
    mintKeypair.publicKey,
    payerKeypair.publicKey,  // mintCloseAuthority
    TOKEN_2022_PROGRAM_ID
  );

  // 6. Initialize Mint
  const initMintIx = createInitializeMintInstruction(
    mintKeypair.publicKey,
    {TOKEN_DECIMALS},  // decimals
    payerKeypair.publicKey,  // mintAuthority
    null,  // freezeAuthority: null = NO FREEZE (censorship resistance)
    TOKEN_2022_PROGRAM_ID
  );

  // 7. Initialize Metadata
  const initMetadataIx = createInitializeMetadataInstruction({{
    programId: TOKEN_2022_PROGRAM_ID,
    mint: mintKeypair.publicKey,
    metadata: mintKeypair.publicKey,
    mintAuthority: payerKeypair.publicKey,
    name: "{TOKEN_NAME}",
    symbol: "{TOKEN_SYMBOL}",
    uri: "{TOKEN_URI}",
    updateAuthority: payerKeypair.publicKey,
  }});

  // Build transaction
  const tx = new Transaction().add(
    createAccountIx,
    initTransferFeeIx,
    initTransferHookIx,
    initMetadataPointerIx,
    initMintCloseIx,
    initMintIx,
    initMetadataIx
  );

  // Send transaction
  console.log("Creating $MIND token...");
  const signature = await sendAndConfirmTransaction(connection, tx, [
    payerKeypair,
    mintKeypair,
  ]);

  console.log("✅ Token created successfully!");
  console.log("Mint Address:", mintKeypair.publicKey.toString());
  console.log("Transaction:", signature);

  // Save mint address to file
  fs.writeFileSync(
    "mind_token_mint.json",
    JSON.stringify({{
      mint: mintKeypair.publicKey.toString(),
      network: "{self.config.network}",
      signature,
      extensions: {json.dumps(EXTENSIONS_TO_ACTIVATE)},
    }}, null, 2)
  );
}}

createMindToken().catch(console.error);
'''

    def create_token(self) -> Token2022CreationResult:
        """
        Create $MIND token with all extensions.

        In dry_run mode, generates TypeScript code and returns mock result.
        In live mode, would execute the TypeScript code.

        Returns Token2022CreationResult.
        """
        self.log("=" * 50)
        self.log("$MIND Token 2022 Creation")
        self.log(f"Network: {self.config.network}")
        self.log(f"Dry Run: {self.config.dry_run}")
        self.log("=" * 50)

        # Validate
        is_valid, issues = self.validate_pre_deployment()
        if not is_valid and not self.config.dry_run:
            return Token2022CreationResult(
                success=False,
                error=f"Pre-deployment validation failed: {', '.join(issues)}",
                dry_run=self.config.dry_run,
            )

        if issues:
            for issue in issues:
                self.log(f"Warning: {issue}", "WARN")

        # Generate TypeScript code
        ts_code = self._generate_typescript_code()

        if self.config.dry_run:
            # Save TypeScript file for manual execution
            ts_file = "create_mind_token.ts"
            with open(ts_file, "w") as f:
                f.write(ts_code)
            self.log(f"TypeScript code saved to {ts_file}", "SUCCESS")

            mock_mint = self._generate_mock_address("mint")
            self.log(f"Mock mint address: {mock_mint}")
            self.log("Extensions that would be activated:", "INFO")
            for ext in EXTENSIONS_TO_ACTIVATE:
                self.log(f"  - {ext}")

            return Token2022CreationResult(
                success=True,
                mint_address=mock_mint,
                extensions_activated=EXTENSIONS_TO_ACTIVATE,
                tx_signatures=["DRY_RUN_NO_TX"],
                dry_run=True,
            )

        # Live execution would run the TypeScript code
        # For now, return instructions to run manually
        self.log("Live deployment not yet automated.", "WARN")
        self.log(f"Run manually: npx ts-node {ts_file}", "INFO")

        return Token2022CreationResult(
            success=False,
            error="Live deployment requires manual TypeScript execution",
            dry_run=False,
        )

    def generate_transfer_hook_template(self) -> str:
        """
        Generate Anchor/Rust template for TransferHook program.

        This program must be deployed BEFORE creating the token.
        """
        return '''
// programs/mind_transfer_hook/src/lib.rs
//
// $MIND TransferHook Program
// Handles custom logic on each transfer:
// - Layer-based fees (1-5%)
// - Dormancy check
// - Transfer logging for trust score

use anchor_lang::prelude::*;
use anchor_spl::token_interface::{Mint, TokenAccount};

declare_id!("YOUR_PROGRAM_ID_HERE"); // Will be set after deployment

#[program]
pub mod mind_transfer_hook {
    use super::*;

    /// Called on every $MIND transfer
    pub fn transfer_hook(ctx: Context<TransferHook>, amount: u64) -> Result<()> {
        let source = &ctx.accounts.source;
        let destination = &ctx.accounts.destination;

        // 1. Check sender is not dormant
        // (dormancy status would be stored in a PDA)

        // 2. Calculate layer fee if crossing layers
        // (layer info would be in account metadata or lookup table)

        // 3. Log transfer for off-chain indexing
        msg!(
            "MIND Transfer: {} tokens from {} to {}",
            amount,
            source.key(),
            destination.key()
        );

        // 4. Update transfer counters (for trust calculation)
        // (would update a PDA with transfer stats)

        Ok(())
    }
}

#[derive(Accounts)]
pub struct TransferHook<'info> {
    /// Source token account
    #[account(token::mint = mint)]
    pub source: InterfaceAccount<'info, TokenAccount>,

    /// The mint
    pub mint: InterfaceAccount<'info, Mint>,

    /// Destination token account
    #[account(token::mint = mint)]
    pub destination: InterfaceAccount<'info, TokenAccount>,

    /// Owner of the source account
    pub owner: UncheckedAccount<'info>,

    /// Extra accounts for hook logic (PDAs, lookup tables, etc.)
    /// CHECK: Validated by the program
    pub extra_account_metas: UncheckedAccount<'info>,
}

// Error codes
#[error_code]
pub enum MindTransferError {
    #[msg("Sender account is dormant")]
    SenderDormant,
    #[msg("Insufficient layer fee")]
    InsufficientLayerFee,
}
'''


def create_token_interactive():
    """Interactive token creation helper."""
    print("=" * 50)
    print("$MIND Token 2022 Creation Wizard")
    print("=" * 50)
    print()
    print("IMPORTANT: Deploy TransferHook program first!")
    print()

    # For now, just create with dry_run
    import sys
    network = "mainnet-beta" if "--mainnet" in sys.argv else "devnet"
    config = Token2022Config(
        network=network,
        dry_run=True,
    )

    creator = Token2022MintCreator(config)

    # Validate
    is_valid, issues = creator.validate_pre_deployment()
    print("\nValidation:")
    if is_valid:
        print("  ✅ All checks passed")
    else:
        for issue in issues:
            print(f"  ❌ {issue}")

    print("\nGenerating TypeScript code...")
    result = creator.create_token()

    print(f"\nResult: {'Success' if result.success else 'Failed'}")
    if result.mint_address:
        print(f"Mint Address: {result.mint_address}")
    if result.error:
        print(f"Error: {result.error}")


if __name__ == "__main__":
    create_token_interactive()
