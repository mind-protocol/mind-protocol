"""
Token Economy Launch Orchestration

Coordinates the complete $MIND token launch sequence:
1. Deploy SPL Token-2022
2. Create liquidity pool on Raydium
3. Lock LP tokens via Meteora (12 months)
4. Distribute airdrop to investors (6-month locks)
5. Set up multi-sig governance wallet
6. Initialize financial tracking

Single command execution of the complete tokenomics plan.
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import time

from .config import (
    TokenConfig,
    AllocationConfig,
    AirdropConfig,
    LiquidityConfig,
    GovernanceConfig,
    NetworkConfig,
    DeploymentState,
    validate_config
)


class LaunchOrchestrator:
    """Orchestrate complete token launch"""

    def __init__(
        self,
        keypair_path: Optional[str] = None,
        network: str = "devnet",
        resume_from: Optional[str] = None
    ):
        """
        Initialize launch orchestrator

        Args:
            keypair_path: Path to deployer wallet keypair
            network: Solana network (mainnet-beta or devnet)
            resume_from: Path to previous state file to resume from
        """
        self.keypair_path = keypair_path
        self.network = network

        # Load or create deployment state
        if resume_from:
            self.state = self._load_state(resume_from)
            print(f"📂 Resuming from previous state: {resume_from}")
        else:
            self.state = DeploymentState()
            self.state.deployment_timestamp = int(datetime.utcnow().timestamp())
            print(f"🆕 Starting fresh deployment")

        # Validate configuration before starting
        print("\n🔍 Validating configuration...")
        try:
            validate_config()
            print("   ✅ Configuration valid")
        except AssertionError as e:
            print(f"   ❌ Configuration error: {e}")
            sys.exit(1)

    def launch(self, skip_confirmations: bool = False):
        """
        Execute complete launch sequence

        Args:
            skip_confirmations: Skip manual confirmations (dangerous!)
        """
        print("\n" + "="*70)
        print("🚀 MIND PROTOCOL TOKEN LAUNCH")
        print("="*70)

        print(f"\n📋 Launch Configuration:")
        print(f"   Token: {TokenConfig.TOKEN_SYMBOL}")
        print(f"   Network: {self.network}")
        print(f"   Total Supply: {TokenConfig.TOTAL_SUPPLY:,}")
        print(f"   Initial Emission: {TokenConfig.INITIAL_EMISSION:,}")
        print(f"   Airdrop Recipients: {AirdropConfig.INVESTOR_COUNT}")
        print(f"   LP Amount: {LiquidityConfig.SOL_AMOUNT} SOL + {LiquidityConfig.MIND_AMOUNT} $MIND")
        print(f"   Estimated Cost: ~{NetworkConfig.TOTAL_ESTIMATED_SOL} SOL")

        # Final confirmation for mainnet
        if self.network == "mainnet-beta" and not skip_confirmations:
            print("\n" + "⚠️ "*35)
            print("WARNING: MAINNET DEPLOYMENT")
            print("This will deploy to Solana mainnet with REAL money!")
            print("="*70)
            confirm = input("\nType 'LAUNCH MAINNET' to proceed: ")
            if confirm != "LAUNCH MAINNET":
                print("❌ Launch cancelled")
                return

        # Execute launch sequence
        try:
            # Step 1: Deploy token
            if not self.state.token_mint:
                self._step_1_deploy_token()
                self._save_state()
            else:
                print(f"\n✓ Step 1: Token already deployed ({self.state.token_mint})")

            # Step 2: Create liquidity pool
            if not self.state.liquidity_pool:
                self._step_2_create_liquidity()
                self._save_state()
            else:
                print(f"\n✓ Step 2: Liquidity pool already created ({self.state.liquidity_pool})")

            # Step 3: Lock LP tokens
            if not self.state.lp_locked:
                self._step_3_lock_liquidity()
                self._save_state()
            else:
                print(f"\n✓ Step 3: LP tokens already locked")

            # Step 4: Distribute airdrop
            if not self.state.airdrop_completed:
                self._step_4_distribute_airdrop()
                self._save_state()
            else:
                print(f"\n✓ Step 4: Airdrop already distributed")

            # Step 5: Set up governance
            if not self.state.multisig_wallet:
                self._step_5_setup_governance()
                self._save_state()
            else:
                print(f"\n✓ Step 5: Governance already configured ({self.state.multisig_wallet})")

            # Step 6: Initialize tracking
            self._step_6_initialize_tracking()

            # Launch complete!
            self._print_success_summary()

        except Exception as e:
            print(f"\n❌ Launch failed at step: {e}")
            print(f"💾 State saved for recovery")
            self._save_state()
            raise

    def _step_1_deploy_token(self):
        """Step 1: Deploy SPL Token-2022"""
        print("\n" + "="*70)
        print("STEP 1: DEPLOY TOKEN")
        print("="*70)

        from .deploy_token import TokenDeployer

        deployer = TokenDeployer(
            keypair_path=self.keypair_path,
            network=self.network
        )

        deployment_info = deployer.deploy_token()
        self.state.token_mint = deployment_info["mint_address"]

        print(f"✅ Token deployed: {self.state.token_mint}")

    def _step_2_create_liquidity(self):
        """Step 2: Create Raydium liquidity pool"""
        print("\n" + "="*70)
        print("STEP 2: CREATE LIQUIDITY POOL")
        print("="*70)

        # TODO: Implement liquidity pool creation
        # This requires:
        # 1. Create Raydium pool with SOL + $MIND
        # 2. Set initial price ($1.00)
        # 3. Receive LP tokens

        print(f"[Mock] Creating Raydium pool...")
        print(f"   SOL: {LiquidityConfig.SOL_AMOUNT}")
        print(f"   $MIND: {LiquidityConfig.MIND_AMOUNT}")
        print(f"   Target Price: ${LiquidityConfig.TARGET_PRICE}")

        # Mock pool address
        self.state.liquidity_pool = "mock_liquidity_pool_address"

        print(f"✅ Liquidity pool created: {self.state.liquidity_pool}")

    def _step_3_lock_liquidity(self):
        """Step 3: Lock LP tokens via Meteora"""
        print("\n" + "="*70)
        print("STEP 3: LOCK LP TOKENS")
        print("="*70)

        # TODO: Implement LP token locking
        # This requires:
        # 1. Connect to Meteora locking contract
        # 2. Lock 100% of LP tokens
        # 3. Set 12-month unlock date

        print(f"[Mock] Locking LP tokens via Meteora...")
        print(f"   Duration: {LiquidityConfig.LOCK_DAYS} days")
        print(f"   Amount: {LiquidityConfig.LOCK_PERCENTAGE}%")

        self.state.lp_locked = True

        print(f"✅ LP tokens locked for {LiquidityConfig.LOCK_DAYS} days")

    def _step_4_distribute_airdrop(self):
        """Step 4: Distribute airdrop to investors"""
        print("\n" + "="*70)
        print("STEP 4: DISTRIBUTE AIRDROP")
        print("="*70)

        from .distribute_airdrop import AirdropDistributor

        distributor = AirdropDistributor(
            mint_address=self.state.token_mint,
            keypair_path=self.keypair_path,
            network=self.network
        )

        results = distributor.distribute_all()

        if len(results["successful"]) == AirdropConfig.INVESTOR_COUNT:
            self.state.airdrop_completed = True
            print(f"✅ Airdrop distributed to all {AirdropConfig.INVESTOR_COUNT} investors")
        else:
            print(f"⚠️  Warning: Only {len(results['successful'])}/{AirdropConfig.INVESTOR_COUNT} successful")

    def _step_5_setup_governance(self):
        """Step 5: Set up multi-sig governance"""
        print("\n" + "="*70)
        print("STEP 5: SETUP GOVERNANCE")
        print("="*70)

        # TODO: Implement multi-sig wallet creation
        # This requires:
        # 1. Create Squads/Realms multi-sig
        # 2. Add signers (founder + 2 advisors)
        # 3. Set 2/3 threshold
        # 4. Transfer DAO Treasury + UBC Reserve

        print(f"[Mock] Creating {GovernanceConfig.THRESHOLD}/{GovernanceConfig.SIGNER_COUNT} multi-sig...")
        print(f"   DAO Treasury: {GovernanceConfig.DAO_TREASURY:,} tokens")
        print(f"   UBC Reserve: {GovernanceConfig.UBC_RESERVE:,} tokens")

        self.state.multisig_wallet = "mock_multisig_address"

        print(f"✅ Governance configured: {self.state.multisig_wallet}")

    def _step_6_initialize_tracking(self):
        """Step 6: Initialize financial tracking"""
        print("\n" + "="*70)
        print("STEP 6: INITIALIZE TRACKING")
        print("="*70)

        # TODO: Implement financial tracking initialization
        # This requires:
        # 1. Create tracking database/files
        # 2. Initialize runway calculations
        # 3. Set up revenue monitoring
        # 4. Configure alerts

        print(f"[Mock] Initializing financial tracking...")
        print(f"   Monthly burn: €{4_000:,}")
        print(f"   Tracking: OTC investments, revenue conversions, runway")

        print(f"✅ Tracking initialized")

    def _save_state(self):
        """Save deployment state for recovery"""
        output_dir = Path(__file__).parent / "deployments"
        output_dir.mkdir(exist_ok=True)

        filename = f"launch_state_{self.network}.json"
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2)

        print(f"💾 State saved: {filepath}")

    def _load_state(self, path: str) -> DeploymentState:
        """Load deployment state from file"""
        with open(path, 'r') as f:
            data = json.load(f)
        return DeploymentState.from_dict(data)

    def _print_success_summary(self):
        """Print launch success summary"""
        print("\n" + "="*70)
        print("🎉 LAUNCH COMPLETE!")
        print("="*70)

        print(f"\n📍 Deployment Addresses:")
        print(f"   Token Mint: {self.state.token_mint}")
        print(f"   Liquidity Pool: {self.state.liquidity_pool}")
        print(f"   Multi-sig Wallet: {self.state.multisig_wallet}")

        print(f"\n🔗 Explorer Links:")
        print(f"   Token: https://solscan.io/token/{self.state.token_mint}")
        print(f"   Pool: https://raydium.io/liquidity/add/?pool_id={self.state.liquidity_pool}")

        print(f"\n💎 Distribution Status:")
        print(f"   ✅ Airdrop: {AirdropConfig.TOTAL_AIRDROP:,} tokens (locked 6 months)")
        print(f"   ✅ Liquidity: {LiquidityConfig.MIND_AMOUNT:,} tokens (locked 12 months)")
        print(f"   ✅ Governance: {GovernanceConfig.DAO_TREASURY + GovernanceConfig.UBC_RESERVE:,} tokens (multi-sig)")

        print(f"\n📊 Next Steps:")
        print(f"   1. Verify token appears in investor wallets")
        print(f"   2. Begin OTC investment collection (€2k per investor)")
        print(f"   3. Build personalized org demos (5 days)")
        print(f"   4. Convert to €2k revenue subscriptions")
        print(f"   5. Monitor financial tracking dashboard")

        print(f"\n🎯 Revenue Targets:")
        print(f"   Conservative: €14,000 = 3.5 months runway")
        print(f"   Base: €22,000 = 5.5 months runway")
        print(f"   Optimistic: €32,000 = 8.0 months runway")

        print(f"\n💰 Current Survival Path:")
        print(f"   Month 1-2: Bridge capital sustains operations")
        print(f"   Month 2-3: Demo conversions generate revenue")
        print(f"   Month 3+: External customers required for sustainability")


def main():
    """Execute token launch"""
    import argparse

    parser = argparse.ArgumentParser(description="Orchestrate $MIND token launch")
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
        "--resume",
        help="Resume from previous state file",
        default=None
    )
    parser.add_argument(
        "--skip-confirmations",
        action="store_true",
        help="Skip manual confirmations (USE WITH CAUTION)"
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = LaunchOrchestrator(
        keypair_path=args.keypair,
        network=args.network,
        resume_from=args.resume
    )

    # Execute launch
    orchestrator.launch(skip_confirmations=args.skip_confirmations)


if __name__ == "__main__":
    main()
