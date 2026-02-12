#!/usr/bin/env python3
"""
airdrop_investors.py — Distribute $MIND tokens to wallets after minting.

Reads investor list and allocation plan from config/token_distribution.json,
calculates pro-rata investor shares, and executes SPL token transfers using
Token-2022 on Solana mainnet.

Usage:
    python3 airdrop_investors.py --dry-run      # Preview (default)
    python3 airdrop_investors.py --live          # Execute transfers
    python3 airdrop_investors.py --config path   # Custom config file
    python3 airdrop_investors.py --report-only   # Just print the report
"""

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_CONFIG = PROJECT_DIR / "config" / "token_distribution.json"
DEFAULT_KEYPAIR = Path.home() / ".config" / "solana" / "id.json"
DEFAULT_RPC = "https://api.mainnet-beta.solana.com"
TOKEN_2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"


@dataclass
class Transfer:
    """A single token transfer record."""
    category: str
    recipient: str
    wallet: str
    amount: float
    note: str
    status: str = "pending"
    tx_hash: str = ""
    error: str = ""
    account_created: bool = False


@dataclass
class DistributionPlan:
    """Full distribution plan parsed from config."""
    mint_address: str
    total_supply: int
    decimals: int
    transfers: list[Transfer] = field(default_factory=list)

    @property
    def total_allocated(self) -> float:
        return sum(t.amount for t in self.transfers)

    @property
    def allocation_pct(self) -> float:
        if self.total_supply == 0:
            return 0
        return self.total_allocated / self.total_supply * 100


def load_config(config_path: Path) -> dict:
    """Load and validate the distribution config file."""
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    required = ["mint_address", "total_supply", "decimals", "distributions"]
    for key in required:
        if key not in config:
            print(f"Error: Missing required key '{key}' in config", file=sys.stderr)
            sys.exit(1)

    return config


def build_plan(config: dict) -> DistributionPlan:
    """Parse config into a structured distribution plan."""
    plan = DistributionPlan(
        mint_address=config["mint_address"],
        total_supply=config["total_supply"],
        decimals=config["decimals"],
    )

    dist = config["distributions"]

    # Cofounders
    if "cofounders" in dist:
        for name, info in dist["cofounders"].items():
            plan.transfers.append(Transfer(
                category="cofounder",
                recipient=name,
                wallet=info["wallet"],
                amount=info["amount"],
                note=info.get("note", ""),
            ))

    # Investors (pro-rata from value_eur)
    if "investors" in dist:
        inv = dist["investors"]
        pool = inv["total_pool"]
        investors = inv.get("investors", [])

        total_value = sum(i["value_eur"] for i in investors)
        if total_value == 0 and investors:
            print("Warning: Total investor EUR value is 0, "
                  "cannot compute pro-rata shares", file=sys.stderr)
        else:
            for investor in investors:
                share = investor["value_eur"] / total_value if total_value > 0 else 0
                amount = pool * share
                plan.transfers.append(Transfer(
                    category="investor",
                    recipient=investor["name"],
                    wallet=investor["wallet"],
                    amount=amount,
                    note=f"{investor['value_eur']} EUR -> {share*100:.2f}% of pool",
                ))

    # Fixed allocations (community, liquidity, ecosystem, etc.)
    fixed_keys = ["community", "liquidity", "ecosystem"]
    for key in fixed_keys:
        if key in dist:
            info = dist[key]
            plan.transfers.append(Transfer(
                category=key,
                recipient=key,
                wallet=info["wallet"],
                amount=info["amount"],
                note=info.get("note", ""),
            ))

    return plan


def validate_plan(plan: DistributionPlan) -> list[str]:
    """Validate the distribution plan. Returns list of issues."""
    issues = []

    if plan.mint_address == "PENDING":
        issues.append("Mint address is PENDING — set it before running --live")

    pending_wallets = [t for t in plan.transfers if t.wallet == "PENDING"]
    if pending_wallets:
        names = ", ".join(t.recipient for t in pending_wallets)
        issues.append(f"{len(pending_wallets)} wallet(s) still PENDING: {names}")

    if abs(plan.total_allocated - plan.total_supply) > 0.01:
        issues.append(
            f"Allocation mismatch: {plan.total_allocated:,.2f} allocated "
            f"vs {plan.total_supply:,} total supply "
            f"(diff: {plan.total_supply - plan.total_allocated:,.2f})"
        )

    # Check for duplicate wallets (excluding PENDING)
    real_wallets = [t.wallet for t in plan.transfers if t.wallet != "PENDING"]
    seen = set()
    dupes = set()
    for w in real_wallets:
        if w in seen:
            dupes.add(w)
        seen.add(w)
    if dupes:
        issues.append(f"Duplicate wallet addresses: {', '.join(dupes)}")

    return issues


def run_solana_cmd(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a solana/spl-token CLI command and return the result."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Command timed out after {timeout}s: {' '.join(args)}")
    except FileNotFoundError:
        raise RuntimeError(
            f"Command not found: {args[0]}. "
            "Ensure solana-cli and spl-token are installed."
        )


def check_token_account(
    mint: str,
    owner_wallet: str,
    keypair: str,
    rpc: str,
) -> str | None:
    """Check if a token account exists for the given mint and owner.
    Returns the token account address if found, None otherwise."""
    result = run_solana_cmd([
        "spl-token", "accounts",
        "--owner", owner_wallet,
        "--url", rpc,
        "--output", "json",
        "--program-id", TOKEN_2022_PROGRAM,
    ])

    if result.returncode != 0:
        return None

    try:
        data = json.loads(result.stdout)
        accounts = data.get("accounts", [])
        for acct in accounts:
            if acct.get("mint") == mint:
                return acct.get("address")
    except (json.JSONDecodeError, KeyError):
        pass

    return None


def create_token_account(
    mint: str,
    owner_wallet: str,
    keypair: str,
    rpc: str,
) -> tuple[bool, str]:
    """Create a token account for the owner. Returns (success, address_or_error)."""
    result = run_solana_cmd([
        "spl-token", "create-account",
        mint,
        "--owner", owner_wallet,
        "--fee-payer", keypair,
        "--url", rpc,
        "--program-id", TOKEN_2022_PROGRAM,
    ])

    if result.returncode != 0:
        return False, result.stderr.strip()

    # Parse account address from output
    for line in result.stdout.splitlines():
        if "Creating account" in line:
            parts = line.strip().split()
            if parts:
                return True, parts[-1]

    return True, result.stdout.strip()


def transfer_tokens(
    mint: str,
    amount: float,
    recipient_wallet: str,
    keypair: str,
    rpc: str,
    decimals: int,
) -> tuple[bool, str]:
    """Transfer tokens to a recipient. Returns (success, tx_hash_or_error)."""
    # spl-token transfer handles account creation with --fund-recipient
    result = run_solana_cmd([
        "spl-token", "transfer",
        mint,
        str(amount),
        recipient_wallet,
        "--fund-recipient",
        "--allow-unfunded-recipient",
        "--fee-payer", keypair,
        "--owner", keypair,
        "--url", rpc,
        "--program-id", TOKEN_2022_PROGRAM,
    ], timeout=120)

    if result.returncode != 0:
        return False, result.stderr.strip()

    # Try to extract signature
    for line in result.stdout.splitlines():
        line = line.strip()
        if "Signature:" in line:
            return True, line.split("Signature:")[-1].strip()
        # Sometimes the tx hash is just a long base58 string
        if len(line) >= 64 and line.isalnum():
            return True, line

    return True, result.stdout.strip()[:120]


def execute_plan(
    plan: DistributionPlan,
    keypair: str,
    rpc: str,
    live: bool = False,
) -> None:
    """Execute or simulate the distribution plan."""

    mode = "LIVE" if live else "DRY RUN"
    print(f"\n{'='*60}")
    print(f"  $MIND Token Distribution — {mode}")
    print(f"{'='*60}")
    print(f"  Mint:      {plan.mint_address}")
    print(f"  Supply:    {plan.total_supply:,}")
    print(f"  Decimals:  {plan.decimals}")
    print(f"  Transfers: {len(plan.transfers)}")
    print(f"  Allocated: {plan.total_allocated:,.2f} ({plan.allocation_pct:.1f}%)")
    print(f"  Keypair:   {keypair}")
    print(f"  RPC:       {rpc}")
    print(f"{'='*60}\n")

    # Validate
    issues = validate_plan(plan)
    if issues:
        print("  Validation issues:")
        for issue in issues:
            print(f"    - {issue}")
        print()
        if live:
            print("  Cannot proceed with --live while validation issues exist.")
            print("  Fix the issues above and try again.")
            sys.exit(1)
        else:
            print("  (Continuing in dry-run mode despite issues)\n")

    # Check keypair exists for live mode
    if live and not Path(keypair).exists():
        print(f"  Error: Keypair file not found: {keypair}", file=sys.stderr)
        sys.exit(1)

    # Process each transfer
    succeeded = 0
    failed = 0
    skipped = 0

    for i, transfer in enumerate(plan.transfers, 1):
        print(f"  [{i}/{len(plan.transfers)}] {transfer.category}: "
              f"{transfer.recipient}")
        print(f"    Wallet: {transfer.wallet}")
        print(f"    Amount: {transfer.amount:,.2f} MIND")
        print(f"    Note:   {transfer.note}")

        if transfer.wallet == "PENDING":
            transfer.status = "skipped"
            transfer.error = "Wallet address is PENDING"
            print(f"    Status: SKIPPED (wallet PENDING)")
            skipped += 1
            print()
            continue

        if not live:
            transfer.status = "dry_run"
            print(f"    Status: DRY RUN (would transfer {transfer.amount:,.2f} MIND)")
            succeeded += 1
            print()
            continue

        # Live execution
        print(f"    Transferring...")
        try:
            success, result = transfer_tokens(
                mint=plan.mint_address,
                amount=transfer.amount,
                recipient_wallet=transfer.wallet,
                keypair=keypair,
                rpc=rpc,
                decimals=plan.decimals,
            )

            if success:
                transfer.status = "success"
                transfer.tx_hash = result
                print(f"    Status: SUCCESS")
                print(f"    TX:     {result}")
                succeeded += 1
            else:
                transfer.status = "failed"
                transfer.error = result
                print(f"    Status: FAILED")
                print(f"    Error:  {result}")
                failed += 1

        except RuntimeError as exc:
            transfer.status = "failed"
            transfer.error = str(exc)
            print(f"    Status: FAILED")
            print(f"    Error:  {exc}")
            failed += 1

        print()

        # Brief pause between live transfers to avoid rate limits
        if live and i < len(plan.transfers):
            time.sleep(2)

    # Summary
    print(f"{'='*60}")
    print(f"  Distribution Summary ({mode})")
    print(f"{'='*60}")
    print(f"  Succeeded: {succeeded}")
    print(f"  Failed:    {failed}")
    print(f"  Skipped:   {skipped}")
    print(f"  Total:     {len(plan.transfers)}")
    print(f"{'='*60}")

    return plan


def print_report(plan: DistributionPlan) -> None:
    """Print a detailed distribution report."""
    print(f"\n{'='*72}")
    print(f"  $MIND Token Distribution Report")
    print(f"  Generated: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*72}")
    print(f"  Mint:         {plan.mint_address}")
    print(f"  Total Supply: {plan.total_supply:>14,} MIND")
    print(f"  Allocated:    {plan.total_allocated:>14,.2f} MIND "
          f"({plan.allocation_pct:.1f}%)")
    unallocated = plan.total_supply - plan.total_allocated
    print(f"  Unallocated:  {unallocated:>14,.2f} MIND "
          f"({unallocated/plan.total_supply*100:.1f}%)")
    print(f"{'='*72}")

    # Group by category
    categories: dict[str, list[Transfer]] = {}
    for t in plan.transfers:
        categories.setdefault(t.category, []).append(t)

    for cat, transfers in categories.items():
        cat_total = sum(t.amount for t in transfers)
        cat_pct = cat_total / plan.total_supply * 100 if plan.total_supply else 0
        print(f"\n  {cat.upper()} — {cat_total:,.2f} MIND ({cat_pct:.1f}%)")
        print(f"  {'-'*68}")
        print(f"  {'Recipient':<25} {'Amount':>14} {'Status':<10} {'Wallet/TX'}")
        print(f"  {'-'*68}")

        for t in transfers:
            wallet_display = t.wallet[:8] + "..." + t.wallet[-4:] if (
                len(t.wallet) > 16 and t.wallet != "PENDING"
            ) else t.wallet

            extra = ""
            if t.tx_hash:
                extra = t.tx_hash[:12] + "..."
            elif t.error:
                extra = t.error[:30]
            else:
                extra = wallet_display

            print(f"  {t.recipient:<25} {t.amount:>14,.2f} {t.status:<10} {extra}")

    print(f"\n{'='*72}")

    # Save report to file
    report_path = PROJECT_DIR / "config" / "distribution_report.json"
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mint_address": plan.mint_address,
        "total_supply": plan.total_supply,
        "total_allocated": plan.total_allocated,
        "transfers": [
            {
                "category": t.category,
                "recipient": t.recipient,
                "wallet": t.wallet,
                "amount": t.amount,
                "note": t.note,
                "status": t.status,
                "tx_hash": t.tx_hash,
                "error": t.error,
            }
            for t in plan.transfers
        ],
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  Report saved to: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Distribute $MIND tokens to wallets (Token-2022 on Solana mainnet)",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simulate transfers without executing (default)",
    )
    mode_group.add_argument(
        "--live",
        action="store_true",
        help="Execute real transfers on mainnet",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Path to distribution config (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--keypair",
        type=str,
        default=str(DEFAULT_KEYPAIR),
        help=f"Path to Solana keypair (default: {DEFAULT_KEYPAIR})",
    )
    parser.add_argument(
        "--rpc",
        type=str,
        default=DEFAULT_RPC,
        help=f"Solana RPC endpoint (default: {DEFAULT_RPC})",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only print the distribution report, do not execute",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    plan = build_plan(config)

    if args.report_only:
        print_report(plan)
        return

    live = args.live
    if live:
        print("\n  *** LIVE MODE — Real transfers will be executed ***")
        print(f"  Mint:    {plan.mint_address}")
        print(f"  Keypair: {args.keypair}")
        print()
        confirm = input("  Type 'CONFIRM' to proceed: ")
        if confirm.strip() != "CONFIRM":
            print("  Aborted.")
            sys.exit(1)
        print()

    execute_plan(plan, keypair=args.keypair, rpc=args.rpc, live=live)
    print_report(plan)

    # Exit code based on results
    failed = sum(1 for t in plan.transfers if t.status == "failed")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
