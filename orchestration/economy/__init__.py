"""
Token Economy Automation

Automated deployment and management of $MIND token economy.
Based on MIND_TOKEN_ECONOMICS.md specification.

Modules:
- config: Token economy configuration
- deploy_token: SPL Token-2022 deployment
- create_liquidity: Raydium pool + Meteora lock
- distribute_airdrop: Investor airdrops with 6-month locks
- track_otc: OTC investment tracking system
- setup_multisig: 2/3 multi-sig wallet creation
- monitor_finances: Financial tracking and runway monitoring
- orchestrate_launch: Main orchestration script
"""

__version__ = "1.0.0"
