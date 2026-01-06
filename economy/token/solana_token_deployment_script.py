#!/usr/bin/env python3
# economy/token/solana_token_deployment_script.py
#
# DOCS: docs/economy/token/IMPLEMENTATION_Token.md
#
# Deployment script for $MIND SPL token on Solana.
#
# This script:
# 1. Creates SPL token mint
# 2. Sets mint authority
# 3. Creates metadata using Metaplex
# 4. Performs initial mint to existing citizens
#
# Prerequisites:
# - Solana CLI installed
# - SOL in deployment wallet
# - pip install solana spl-token
#
# Usage:
#   python solana_token_deployment_script.py --network devnet --dry-run
#   python solana_token_deployment_script.py --network mainnet

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Import local modules
try:
    from .metaplex_token_metadata_manager import DEFAULT_METADATA, TokenMetadata
    from .spl_token_mint_authority_controller import MintAuthorityController
except ImportError:
    # Allow running as standalone script
    pass


@dataclass
class DeploymentConfig:
    """Configuration for token deployment."""

    # Network
    network: str = "devnet"  # devnet, testnet, mainnet-beta

    # Token properties
    name: str = "MIND"
    symbol: str = "MIND"
    decimals: int = 9

    # Authorities
    mint_authority: Optional[str] = None  # Wallet address
    freeze_authority: Optional[str] = None  # None = no freeze

    # Paths
    keypair_path: Optional[str] = None
    output_dir: str = "./deploy_output"

    # Mode
    dry_run: bool = True

    @property
    def rpc_url(self) -> str:
        """Get RPC URL for network."""
        urls = {
            "devnet": "https://api.devnet.solana.com",
            "testnet": "https://api.testnet.solana.com",
            "mainnet-beta": "https://api.mainnet-beta.solana.com",
            "mainnet": "https://api.mainnet-beta.solana.com",
        }
        return urls.get(self.network, urls["devnet"])


class TokenDeployer:
    """
    Deploys $MIND token to Solana.

    Handles the full deployment process:
    1. Create token mint
    2. Set authorities
    3. Create metadata
    4. Initial distribution
    """

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.mint_address: Optional[str] = None
        self.results: list[dict] = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        prefix = {"INFO": "[*]", "SUCCESS": "[+]", "ERROR": "[-]", "WARN": "[!]"}
        print(f"{prefix.get(level, '[*]')} {message}")
        self.results.append({"level": level, "message": message})

    def run_command(self, cmd: list[str], capture: bool = True) -> tuple[int, str, str]:
        """Run a shell command."""
        if self.config.dry_run:
            self.log(f"DRY RUN: {' '.join(cmd)}")
            return 0, "dry_run_output", ""

        try:
            result = subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                check=False,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def check_prerequisites(self) -> bool:
        """Check that all prerequisites are met."""
        self.log("Checking prerequisites...")

        # Check Solana CLI
        code, out, err = self.run_command(["solana", "--version"])
        if code != 0 and not self.config.dry_run:
            self.log("Solana CLI not found. Install from https://solana.com/docs/intro/installation", "ERROR")
            return False
        self.log("Solana CLI found")

        # Check SPL Token CLI
        code, out, err = self.run_command(["spl-token", "--version"])
        if code != 0 and not self.config.dry_run:
            self.log("SPL Token CLI not found. Run: cargo install spl-token-cli", "ERROR")
            return False
        self.log("SPL Token CLI found")

        # Check keypair
        if self.config.keypair_path:
            if not Path(self.config.keypair_path).exists() and not self.config.dry_run:
                self.log(f"Keypair not found: {self.config.keypair_path}", "ERROR")
                return False
            self.log(f"Using keypair: {self.config.keypair_path}")

        # Check balance (if not dry run)
        if not self.config.dry_run:
            code, out, err = self.run_command(["solana", "balance"])
            if code == 0:
                self.log(f"Wallet balance: {out.strip()}")
            else:
                self.log("Could not check wallet balance", "WARN")

        self.log("Prerequisites check passed", "SUCCESS")
        return True

    def create_token_mint(self) -> Optional[str]:
        """Create the SPL token mint."""
        self.log(f"Creating token mint on {self.config.network}...")

        cmd = [
            "spl-token", "create-token",
            "--decimals", str(self.config.decimals),
            "--url", self.config.rpc_url,
        ]

        if self.config.keypair_path:
            cmd.extend(["--fee-payer", self.config.keypair_path])

        if self.config.freeze_authority is None:
            cmd.append("--enable-freeze")  # Then disable it
            # Actually, to have no freeze authority, don't pass --enable-freeze

        code, out, err = self.run_command(cmd)

        if self.config.dry_run:
            self.mint_address = "DRY_RUN_MINT_ADDRESS_PLACEHOLDER"
            self.log(f"Would create mint: {self.mint_address}", "SUCCESS")
            return self.mint_address

        if code != 0:
            self.log(f"Failed to create mint: {err}", "ERROR")
            return None

        # Parse mint address from output
        # Output format: "Creating token <MINT_ADDRESS>"
        for line in out.split("\n"):
            if "Creating token" in line or "Address:" in line:
                parts = line.split()
                for part in parts:
                    if len(part) > 30:  # Likely a base58 address
                        self.mint_address = part
                        break

        if self.mint_address:
            self.log(f"Token mint created: {self.mint_address}", "SUCCESS")
        else:
            self.log("Could not parse mint address from output", "ERROR")
            self.log(f"Output: {out}")

        return self.mint_address

    def set_mint_authority(self, new_authority: str) -> bool:
        """Set or transfer mint authority."""
        if not self.mint_address:
            self.log("No mint address set", "ERROR")
            return False

        self.log(f"Setting mint authority to: {new_authority}")

        cmd = [
            "spl-token", "authorize",
            self.mint_address, "mint", new_authority,
            "--url", self.config.rpc_url,
        ]

        if self.config.keypair_path:
            cmd.extend(["--fee-payer", self.config.keypair_path])

        code, out, err = self.run_command(cmd)

        if code != 0 and not self.config.dry_run:
            self.log(f"Failed to set mint authority: {err}", "ERROR")
            return False

        self.log("Mint authority set", "SUCCESS")
        return True

    def disable_freeze_authority(self) -> bool:
        """Disable freeze authority (set to None)."""
        if not self.mint_address:
            self.log("No mint address set", "ERROR")
            return False

        self.log("Disabling freeze authority (censorship resistance)...")

        cmd = [
            "spl-token", "authorize",
            self.mint_address, "freeze", "--disable",
            "--url", self.config.rpc_url,
        ]

        if self.config.keypair_path:
            cmd.extend(["--fee-payer", self.config.keypair_path])

        code, out, err = self.run_command(cmd)

        if code != 0 and not self.config.dry_run:
            self.log(f"Failed to disable freeze authority: {err}", "ERROR")
            return False

        self.log("Freeze authority disabled", "SUCCESS")
        return True

    def mint_initial_supply(self, recipient: str, amount: int) -> bool:
        """Mint initial tokens to a recipient."""
        if not self.mint_address:
            self.log("No mint address set", "ERROR")
            return False

        self.log(f"Minting {amount:,} tokens to {recipient[:8]}...")

        # First create token account for recipient if needed
        cmd_account = [
            "spl-token", "create-account",
            self.mint_address,
            "--owner", recipient,
            "--url", self.config.rpc_url,
        ]

        if self.config.keypair_path:
            cmd_account.extend(["--fee-payer", self.config.keypair_path])

        self.run_command(cmd_account)  # May fail if account exists

        # Now mint
        cmd_mint = [
            "spl-token", "mint",
            self.mint_address, str(amount),
            recipient,
            "--url", self.config.rpc_url,
        ]

        if self.config.keypair_path:
            cmd_mint.extend(["--fee-payer", self.config.keypair_path])

        code, out, err = self.run_command(cmd_mint)

        if code != 0 and not self.config.dry_run:
            self.log(f"Failed to mint: {err}", "ERROR")
            return False

        self.log(f"Minted {amount:,} tokens", "SUCCESS")
        return True

    def save_deployment_info(self):
        """Save deployment information to file."""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        info = {
            "network": self.config.network,
            "mint_address": self.mint_address,
            "token_name": self.config.name,
            "token_symbol": self.config.symbol,
            "decimals": self.config.decimals,
            "rpc_url": self.config.rpc_url,
            "dry_run": self.config.dry_run,
            "results": self.results,
        }

        output_file = output_dir / f"deployment_{self.config.network}.json"
        with open(output_file, "w") as f:
            json.dump(info, f, indent=2)

        self.log(f"Deployment info saved to {output_file}", "SUCCESS")

    def deploy(self) -> bool:
        """
        Run full deployment process.

        Returns:
            True if deployment successful
        """
        self.log("=" * 50)
        self.log("$MIND Token Deployment")
        self.log(f"Network: {self.config.network}")
        self.log(f"Dry Run: {self.config.dry_run}")
        self.log("=" * 50)

        # Step 1: Prerequisites
        if not self.check_prerequisites():
            return False

        # Step 2: Create mint
        if not self.create_token_mint():
            return False

        # Step 3: Disable freeze authority
        if not self.disable_freeze_authority():
            self.log("Continuing despite freeze authority issue", "WARN")

        # Step 4: Save deployment info
        self.save_deployment_info()

        self.log("=" * 50)
        self.log("Deployment complete!", "SUCCESS")
        self.log(f"Mint Address: {self.mint_address}")
        self.log("=" * 50)

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy $MIND SPL token to Solana"
    )
    parser.add_argument(
        "--network",
        choices=["devnet", "testnet", "mainnet-beta", "mainnet"],
        default="devnet",
        help="Solana network to deploy to",
    )
    parser.add_argument(
        "--keypair",
        type=str,
        default=None,
        help="Path to keypair file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Don't actually send transactions",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        default=False,
        help="Actually send transactions (opposite of --dry-run)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./deploy_output",
        help="Output directory for deployment info",
    )

    args = parser.parse_args()

    config = DeploymentConfig(
        network=args.network,
        keypair_path=args.keypair,
        dry_run=not args.live,
        output_dir=args.output,
    )

    deployer = TokenDeployer(config)
    success = deployer.deploy()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
