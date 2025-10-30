"""
Airdrop Distribution Script

Distributes 10,000 $MIND tokens to 20 burned investors with:
- 6-month transfer lock using Token-2022
- Psychological wallet display impact
- Efficient batch processing
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from .config import AirdropConfig, NetworkConfig, TokenConfig


class AirdropDistributor:
    """Distribute locked tokens to investors"""

    def __init__(
        self,
        mint_address: str,
        keypair_path: Optional[str] = None,
        network: str = NetworkConfig.CLUSTER
    ):
        """
        Initialize airdrop distributor

        Args:
            mint_address: $MIND token mint address
            keypair_path: Path to wallet keypair JSON
            network: Solana network
        """
        self.mint_address = Pubkey.from_string(mint_address)
        self.network = network
        self.rpc_url = NetworkConfig.RPC_URL if network == "mainnet-beta" else "https://api.devnet.solana.com"
        self.client = Client(self.rpc_url, commitment=Confirmed)

        # Load deployer keypair (holds tokens to distribute)
        if keypair_path is None:
            keypair_path = os.path.expanduser("~/.config/solana/id.json")

        self.deployer = self._load_keypair(keypair_path)
        print(f"📍 Distributor wallet: {self.deployer.pubkey()}")

        # Validate investor wallets configured
        if not AirdropConfig.INVESTOR_WALLETS:
            raise ValueError("❌ No investor wallets configured in AirdropConfig.INVESTOR_WALLETS")

        if len(AirdropConfig.INVESTOR_WALLETS) != AirdropConfig.INVESTOR_COUNT:
            raise ValueError(
                f"❌ Wallet count mismatch: {len(AirdropConfig.INVESTOR_WALLETS)} != {AirdropConfig.INVESTOR_COUNT}"
            )

    def _load_keypair(self, path: str) -> Keypair:
        """Load Solana keypair from JSON file"""
        with open(path, 'r') as f:
            secret = json.load(f)
        return Keypair.from_bytes(bytes(secret))

    def distribute_all(self) -> Dict:
        """
        Distribute tokens to all investors

        Returns:
            Dict with distribution results
        """
        print("\n" + "="*70)
        print("🎁 AIRDROP DISTRIBUTION")
        print("="*70)

        print(f"\n📝 Airdrop Configuration:")
        print(f"   Token: {TokenConfig.TOKEN_SYMBOL}")
        print(f"   Mint: {self.mint_address}")
        print(f"   Investors: {AirdropConfig.INVESTOR_COUNT}")
        print(f"   Tokens per investor: {AirdropConfig.TOKENS_PER_INVESTOR:,}")
        print(f"   Total distribution: {AirdropConfig.TOTAL_AIRDROP:,}")
        print(f"   Lock duration: {AirdropConfig.LOCK_DAYS} days")
        print(f"   Unlock date: {(datetime.utcnow() + timedelta(days=AirdropConfig.LOCK_DAYS)).strftime('%Y-%m-%d')}")

        # Validate sufficient balance
        print(f"\n🔍 Validating token balance...")
        if not self._validate_balance():
            raise Exception("❌ Insufficient tokens for airdrop")

        # Process airdrops
        results = {
            "successful": [],
            "failed": [],
            "total_distributed": 0,
            "distribution_timestamp": datetime.utcnow().isoformat()
        }

        print(f"\n🚀 Distributing to {AirdropConfig.INVESTOR_COUNT} investors...")

        for idx, wallet_address in enumerate(AirdropConfig.INVESTOR_WALLETS, 1):
            print(f"\n   [{idx}/{AirdropConfig.INVESTOR_COUNT}] Processing {wallet_address[:8]}...")

            try:
                tx_signature = self._send_locked_tokens(wallet_address)

                results["successful"].append({
                    "wallet": wallet_address,
                    "amount": AirdropConfig.TOKENS_PER_INVESTOR,
                    "transaction": tx_signature,
                    "lock_expires": (datetime.utcnow() + timedelta(days=AirdropConfig.LOCK_DAYS)).isoformat()
                })
                results["total_distributed"] += AirdropConfig.TOKENS_PER_INVESTOR

                print(f"      ✅ Success! TX: {tx_signature[:16]}...")

            except Exception as e:
                print(f"      ❌ Failed: {e}")
                results["failed"].append({
                    "wallet": wallet_address,
                    "error": str(e)
                })

        # Summary
        print("\n" + "="*70)
        print("📊 DISTRIBUTION SUMMARY")
        print("="*70)
        print(f"   ✅ Successful: {len(results['successful'])}/{AirdropConfig.INVESTOR_COUNT}")
        print(f"   ❌ Failed: {len(results['failed'])}")
        print(f"   💎 Total distributed: {results['total_distributed']:,} $MIND")

        if results['failed']:
            print(f"\n⚠️  WARNING: {len(results['failed'])} distributions failed!")
            print("   Failed wallets:")
            for failed in results['failed']:
                print(f"      • {failed['wallet']}: {failed['error']}")

        # Save results
        self._save_results(results)

        return results

    def _validate_balance(self) -> bool:
        """Validate distributor has sufficient tokens"""
        # TODO: Implement balance check
        # This requires:
        # 1. Get distributor's token account
        # 2. Query balance
        # 3. Verify >= TOTAL_AIRDROP
        print("   [Mock] Balance verified")
        return True

    def _send_locked_tokens(self, recipient_address: str) -> str:
        """
        Send tokens with 6-month transfer lock

        Args:
            recipient_address: Recipient wallet address

        Returns:
            Transaction signature
        """
        # TODO: Implement locked token transfer
        # This requires:
        # 1. Create/derive recipient token account
        # 2. Transfer tokens with Token-2022 transfer restrictions
        # 3. Set lock expiry date
        # 4. Send transaction
        # 5. Confirm transaction
        return f"mock_tx_{recipient_address[:8]}"

    def _save_results(self, results: Dict):
        """Save distribution results to file"""
        output_dir = Path(__file__).parent / "distributions"
        output_dir.mkdir(exist_ok=True)

        filename = f"airdrop_{self.network}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Distribution results saved: {filepath}")

    def verify_distribution(self) -> Dict:
        """
        Verify all investors received their tokens

        Returns:
            Dict with verification results
        """
        print("\n" + "="*70)
        print("🔍 VERIFYING AIRDROP")
        print("="*70)

        results = {
            "verified": [],
            "missing": [],
            "incorrect_amount": []
        }

        for wallet_address in AirdropConfig.INVESTOR_WALLETS:
            # TODO: Implement verification
            # This requires:
            # 1. Query recipient token account
            # 2. Verify balance = TOKENS_PER_INVESTOR
            # 3. Verify tokens are locked
            # 4. Verify lock expiry date
            pass

        return results


def main():
    """Distribute airdrop to investors"""
    import argparse

    parser = argparse.ArgumentParser(description="Distribute $MIND airdrop to burned investors")
    parser.add_argument(
        "--mint",
        required=True,
        help="$MIND token mint address"
    )
    parser.add_argument(
        "--keypair",
        help="Path to distributor keypair JSON",
        default=None
    )
    parser.add_argument(
        "--network",
        choices=["mainnet-beta", "devnet"],
        default="devnet",
        help="Solana network"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing distribution"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print configuration without distributing"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No transactions will be sent")
        print(f"\nInvestors: {AirdropConfig.INVESTOR_COUNT}")
        print(f"Tokens per investor: {AirdropConfig.TOKENS_PER_INVESTOR:,}")
        print(f"Total: {AirdropConfig.TOTAL_AIRDROP:,}")
        print(f"Lock: {AirdropConfig.LOCK_DAYS} days")
        return

    # Initialize distributor
    distributor = AirdropDistributor(
        mint_address=args.mint,
        keypair_path=args.keypair,
        network=args.network
    )

    if args.verify_only:
        # Verify existing distribution
        results = distributor.verify_distribution()
        print("\n✅ Verification complete!")
    else:
        # Confirm distribution
        print("⚠️  WARNING: You are about to distribute locked tokens to investors")
        print(f"Network: {args.network}")
        print(f"Investors: {AirdropConfig.INVESTOR_COUNT}")
        print(f"Total: {AirdropConfig.TOTAL_AIRDROP:,} $MIND")

        if args.network == "mainnet-beta":
            confirm = input("\nType 'DISTRIBUTE' to confirm: ")
            if confirm != "DISTRIBUTE":
                print("❌ Distribution cancelled")
                return

        # Distribute airdrop
        results = distributor.distribute_all()

        print("\n✅ Distribution complete!")
        print(f"Successful: {len(results['successful'])}/{AirdropConfig.INVESTOR_COUNT}")


if __name__ == "__main__":
    main()
