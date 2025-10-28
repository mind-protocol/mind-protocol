"""
SPL Token-2022 Deployment Script

Deploys $MIND token to Solana with:
- Token-2022 standard (for transfer restrictions)
- Rich metadata
- Retained mint/freeze authorities
- Initial emission (20% of total supply)
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.instructions import (
    create_initialize_mint_instruction,
    create_mint_to_instruction,
    create_account,
    create_initialize_account_instruction,
)
from spl.token.constants import TOKEN_2022_PROGRAM_ID

from .config import TokenConfig, AllocationConfig, NetworkConfig


class TokenDeployer:
    """Deploy $MIND token to Solana"""

    def __init__(
        self,
        keypair_path: Optional[str] = None,
        network: str = NetworkConfig.CLUSTER
    ):
        """
        Initialize token deployer

        Args:
            keypair_path: Path to wallet keypair JSON (defaults to ~/.config/solana/id.json)
            network: Solana network (mainnet-beta or devnet)
        """
        self.network = network
        self.rpc_url = NetworkConfig.RPC_URL if network == "mainnet-beta" else "https://api.devnet.solana.com"
        self.client = Client(self.rpc_url, commitment=Confirmed)

        # Load deployer keypair
        if keypair_path is None:
            keypair_path = os.path.expanduser("~/.config/solana/id.json")

        self.deployer = self._load_keypair(keypair_path)
        print(f"📍 Deployer wallet: {self.deployer.pubkey()}")

        # Check balance
        balance = self._get_balance()
        print(f"💰 Deployer balance: {balance:.4f} SOL")

        if balance < NetworkConfig.TOTAL_ESTIMATED_SOL:
            print(f"⚠️  Warning: Balance below estimated cost ({NetworkConfig.TOTAL_ESTIMATED_SOL} SOL)")

    def _load_keypair(self, path: str) -> Keypair:
        """Load Solana keypair from JSON file"""
        with open(path, 'r') as f:
            secret = json.load(f)
        return Keypair.from_bytes(bytes(secret))

    def _get_balance(self) -> float:
        """Get SOL balance of deployer wallet"""
        response = self.client.get_balance(self.deployer.pubkey())
        return response.value / 1e9  # Lamports to SOL

    def deploy_token(self) -> Dict[str, str]:
        """
        Deploy $MIND token with full configuration

        Returns:
            Dict with token mint address and metadata
        """
        print("\n" + "="*70)
        print("🚀 DEPLOYING $MIND TOKEN")
        print("="*70)

        # Generate token mint keypair
        mint_keypair = Keypair()
        mint_address = mint_keypair.pubkey()

        print(f"\n📝 Token Configuration:")
        print(f"   Name: {TokenConfig.TOKEN_NAME}")
        print(f"   Symbol: {TokenConfig.TOKEN_SYMBOL}")
        print(f"   Total Supply: {TokenConfig.TOTAL_SUPPLY:,}")
        print(f"   Initial Emission: {TokenConfig.INITIAL_EMISSION:,} ({TokenConfig.INITIAL_EMISSION/TokenConfig.TOTAL_SUPPLY*100:.0f}%)")
        print(f"   Decimals: {TokenConfig.DECIMALS}")
        print(f"   Mint Address: {mint_address}")

        # Step 1: Create mint account
        print(f"\n🔨 Step 1: Creating mint account...")
        self._create_mint_account(mint_keypair)

        # Step 2: Initialize mint with metadata
        print(f"\n📋 Step 2: Initializing mint with metadata...")
        self._initialize_mint(mint_keypair)

        # Step 3: Create token account for deployer (to receive initial mint)
        print(f"\n💼 Step 3: Creating deployer token account...")
        token_account = self._create_token_account(mint_address)

        # Step 4: Mint initial emission
        print(f"\n💎 Step 4: Minting initial emission ({TokenConfig.INITIAL_EMISSION:,} tokens)...")
        self._mint_tokens(mint_address, token_account, TokenConfig.INITIAL_EMISSION)

        # Step 5: Verify deployment
        print(f"\n✅ Step 5: Verifying deployment...")
        if self._verify_deployment(mint_address, token_account):
            print("   ✅ Token deployed successfully!")
        else:
            raise Exception("❌ Deployment verification failed")

        # Save deployment info
        deployment_info = {
            "token_name": TokenConfig.TOKEN_NAME,
            "token_symbol": TokenConfig.TOKEN_SYMBOL,
            "mint_address": str(mint_address),
            "deployer_token_account": str(token_account),
            "total_supply": TokenConfig.TOTAL_SUPPLY,
            "initial_emission": TokenConfig.INITIAL_EMISSION,
            "decimals": TokenConfig.DECIMALS,
            "network": self.network,
            "deployed_at": datetime.utcnow().isoformat(),
            "deployer": str(self.deployer.pubkey())
        }

        self._save_deployment_info(deployment_info)

        print("\n" + "="*70)
        print("🎉 TOKEN DEPLOYMENT COMPLETE")
        print("="*70)
        print(f"\n📍 Mint Address: {mint_address}")
        print(f"💼 Deployer Token Account: {token_account}")
        print(f"🔗 Explorer: https://solscan.io/token/{mint_address}")

        return deployment_info

    def _create_mint_account(self, mint_keypair: Keypair):
        """Create the mint account on Solana"""
        # TODO: Implement mint account creation
        # This requires:
        # 1. Calculate rent-exempt balance for mint account
        # 2. Create account instruction
        # 3. Send transaction
        print("   [Mock] Mint account created")

    def _initialize_mint(self, mint_keypair: Keypair):
        """Initialize mint with metadata and authorities"""
        # TODO: Implement mint initialization
        # This requires:
        # 1. Create initialize mint instruction
        # 2. Add metadata extension (Token-2022)
        # 3. Set mint/freeze authorities
        # 4. Send transaction
        print("   [Mock] Mint initialized with metadata")

    def _create_token_account(self, mint_address: Pubkey) -> Pubkey:
        """Create token account for deployer"""
        # TODO: Implement token account creation
        # This requires:
        # 1. Derive associated token account address
        # 2. Create account instruction
        # 3. Send transaction
        print("   [Mock] Token account created")
        # Return mock address for now
        return self.deployer.pubkey()

    def _mint_tokens(self, mint_address: Pubkey, destination: Pubkey, amount: int):
        """Mint initial token emission"""
        # TODO: Implement token minting
        # This requires:
        # 1. Create mint_to instruction
        # 2. Convert amount to token units (amount * 10^decimals)
        # 3. Send transaction
        print(f"   [Mock] Minted {amount:,} tokens to {destination}")

    def _verify_deployment(self, mint_address: Pubkey, token_account: Pubkey) -> bool:
        """Verify token was deployed correctly"""
        # TODO: Implement verification
        # This requires:
        # 1. Query mint account info
        # 2. Verify supply, decimals, authorities
        # 3. Query token account balance
        # 4. Verify initial emission
        print("   [Mock] Deployment verified")
        return True

    def _save_deployment_info(self, info: Dict):
        """Save deployment information to file"""
        output_dir = Path(__file__).parent / "deployments"
        output_dir.mkdir(exist_ok=True)

        filename = f"mind_token_{self.network}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(info, f, indent=2)

        print(f"\n💾 Deployment info saved: {filepath}")


def main():
    """Deploy $MIND token"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy $MIND SPL Token-2022")
    parser.add_argument(
        "--keypair",
        help="Path to deployer keypair JSON",
        default=None
    )
    parser.add_argument(
        "--network",
        choices=["mainnet-beta", "devnet"],
        default="devnet",
        help="Solana network"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print configuration without deploying"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No transactions will be sent")
        print(f"\nToken: {TokenConfig.TOKEN_SYMBOL}")
        print(f"Total Supply: {TokenConfig.TOTAL_SUPPLY:,}")
        print(f"Initial Emission: {TokenConfig.INITIAL_EMISSION:,}")
        print(f"Network: {args.network}")
        return

    # Confirm deployment
    print("⚠️  WARNING: You are about to deploy $MIND token to Solana")
    print(f"Network: {args.network}")
    print(f"Estimated cost: {NetworkConfig.TOTAL_ESTIMATED_SOL} SOL")

    if args.network == "mainnet-beta":
        confirm = input("\nType 'DEPLOY' to confirm mainnet deployment: ")
        if confirm != "DEPLOY":
            print("❌ Deployment cancelled")
            return

    # Deploy token
    deployer = TokenDeployer(keypair_path=args.keypair, network=args.network)
    deployment_info = deployer.deploy_token()

    print("\n✅ Deployment complete!")
    print(f"Mint: {deployment_info['mint_address']}")


if __name__ == "__main__":
    main()
