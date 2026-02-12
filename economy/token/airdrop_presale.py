#!/usr/bin/env python3
"""
$MIND Pre-Sale Airdrop Script

Distributes $MIND tokens to pre-sale buyers based on their SOL contributions.

Flow:
1. Read presale_buyers.json (from monitor_presale.py)
2. Calculate token amounts per buyer (SOL × SOL_price / token_price)
3. Create token accounts for each buyer
4. Mint and transfer tokens

Usage:
    python3 airdrop_presale.py --dry-run           # Preview distribution
    python3 airdrop_presale.py --from-file buyers.json --dry-run
    python3 airdrop_presale.py --manual "wallet1:2,wallet2:4"  # Manual: wallet:SOL_amount
    python3 airdrop_presale.py --live               # Execute airdrop

Prerequisites:
    - $MIND token must be minted first (run deploy_mainnet.sh --live)
    - Token mint address must be in deploy_output/deployment_mainnet.json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TOKEN_2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
RPC_URL = "https://api.mainnet-beta.solana.com"
KEYPAIR = str(Path.home() / ".config/solana/id.json")

# Pricing
SOL_PRICE_USD = 195.0
TOKEN_PRICE_USD = 0.20
DECIMALS = 9

DEPLOY_DIR = Path(__file__).parent / "deploy_output"
PRESALE_FILE = DEPLOY_DIR / "presale_buyers.json"
DEPLOYMENT_FILE = DEPLOY_DIR / "deployment_mainnet.json"
AIRDROP_LOG = DEPLOY_DIR / "airdrop_log.json"


def load_mint_address() -> str | None:
    """Load mint address from deployment info."""
    if DEPLOYMENT_FILE.exists():
        with open(DEPLOYMENT_FILE) as f:
            data = json.load(f)
            mint = data.get("mint_address")
            if mint and not mint.startswith("DRY_RUN"):
                return mint
    return None


def calculate_tokens(sol_amount: float) -> float:
    """Calculate $MIND tokens for a given SOL amount."""
    usd_value = sol_amount * SOL_PRICE_USD
    tokens = usd_value / TOKEN_PRICE_USD
    return tokens


def parse_manual_buyers(manual_str: str) -> dict[str, float]:
    """Parse manual buyer string: 'wallet1:sol1,wallet2:sol2'"""
    buyers = {}
    for entry in manual_str.split(","):
        parts = entry.strip().split(":")
        if len(parts) == 2:
            wallet = parts[0].strip()
            sol = float(parts[1].strip())
            buyers[wallet] = sol
    return buyers


def run_cmd(cmd: list[str], dry_run: bool = True) -> tuple[int, str, str]:
    """Run a command, or print it in dry-run mode."""
    if dry_run:
        print(f"  [DRY RUN] {' '.join(cmd)}")
        return 0, "dry_run", ""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def create_token_account(mint: str, owner: str, dry_run: bool) -> str | None:
    """Create an associated token account for the buyer."""
    cmd = [
        "spl-token", "create-account", mint,
        "--owner", owner,
        "--url", RPC_URL,
        "--fee-payer", KEYPAIR,
        "--program-id", TOKEN_2022_PROGRAM,
    ]
    code, out, err = run_cmd(cmd, dry_run)
    if code != 0 and not dry_run:
        # Account might already exist — that's OK
        if "already in use" in err or "already exists" in err:
            print(f"  Account already exists for {owner[:16]}...")
            return "existing"
        print(f"  Error creating account: {err}")
        return None
    return "created" if not dry_run else "dry_run"


def transfer_tokens(mint: str, amount: float, recipient: str, dry_run: bool) -> bool:
    """Transfer tokens to a recipient."""
    cmd = [
        "spl-token", "transfer", mint,
        str(amount), recipient,
        "--url", RPC_URL,
        "--fee-payer", KEYPAIR,
        "--fund-recipient",  # Auto-create ATA if needed
        "--program-id", TOKEN_2022_PROGRAM,
    ]
    code, out, err = run_cmd(cmd, dry_run)
    if code != 0 and not dry_run:
        print(f"  Error transferring to {recipient[:16]}...: {err}")
        return False
    return True


def main():
    global SOL_PRICE_USD
    parser = argparse.ArgumentParser(description="$MIND Pre-Sale Airdrop")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--live", action="store_true", default=False)
    parser.add_argument("--from-file", type=str, help="Path to buyers JSON")
    parser.add_argument("--manual", type=str,
                        help="Manual buyers: 'wallet1:sol1,wallet2:sol2'")
    parser.add_argument("--mint", type=str, help="Override mint address")
    parser.add_argument("--sol-price", type=float, default=SOL_PRICE_USD,
                        help=f"SOL price in USD (default: {SOL_PRICE_USD})")
    args = parser.parse_args()

    dry_run = not args.live
    SOL_PRICE_USD = args.sol_price

    # Get mint address
    mint = args.mint or load_mint_address()
    if not mint:
        print("[-] No mint address found. Run deploy_mainnet.sh --live first,")
        print("    or pass --mint <ADDRESS>")
        if not dry_run:
            sys.exit(1)
        mint = "DRY_RUN_MINT"

    # Load buyers
    buyers: dict[str, float] = {}  # wallet -> SOL amount

    if args.manual:
        buyers = parse_manual_buyers(args.manual)
    elif args.from_file:
        with open(args.from_file) as f:
            data = json.load(f)
            if "buyers" in data:
                buyers = {w: info["total_sol"] for w, info in data["buyers"].items()}
            else:
                buyers = data
    elif PRESALE_FILE.exists():
        with open(PRESALE_FILE) as f:
            data = json.load(f)
            buyers = {w: info["total_sol"] for w, info in data.get("buyers", {}).items()}

    if not buyers:
        print("[!] No buyers found. Use --manual or ensure presale_buyers.json exists.")
        print("[!] Example: --manual 'WalletAddr123...:2,WalletAddr456...:4'")
        if not dry_run:
            sys.exit(1)
        # Demo with placeholder
        buyers = {"ExampleBuyerWallet1234567890abcdefghijk": 2.0}
        print("[*] Using demo buyer for dry-run preview")

    # Calculate distribution
    print("=" * 60)
    print("  $MIND Pre-Sale Airdrop")
    print("=" * 60)
    print(f"  Mint:          {mint[:20]}...")
    print(f"  SOL Price:     ${SOL_PRICE_USD}")
    print(f"  Token Price:   ${TOKEN_PRICE_USD}")
    print(f"  Dry Run:       {dry_run}")
    print(f"  Buyers:        {len(buyers)}")
    print("=" * 60)
    print()

    total_tokens = 0.0
    total_sol = 0.0
    distribution = []

    print("  Distribution Plan:")
    print(f"  {'Wallet':<20} {'SOL':>8} {'$MIND':>12} {'USD Value':>10}")
    print("  " + "-" * 54)

    for wallet, sol_amount in sorted(buyers.items(), key=lambda x: -x[1]):
        tokens = calculate_tokens(sol_amount)
        usd = sol_amount * SOL_PRICE_USD
        total_tokens += tokens
        total_sol += sol_amount
        distribution.append({
            "wallet": wallet,
            "sol_amount": sol_amount,
            "tokens": tokens,
            "usd_value": usd,
        })
        print(f"  {wallet[:20]:20} {sol_amount:>8.2f} {tokens:>12,.0f} ${usd:>9,.0f}")

    print("  " + "-" * 54)
    print(f"  {'TOTAL':20} {total_sol:>8.2f} {total_tokens:>12,.0f} "
          f"${total_sol * SOL_PRICE_USD:>9,.0f}")
    print()

    # Sanity check: total tokens shouldn't exceed initial mint
    if total_tokens > 100_000:
        print(f"[!] WARNING: Total tokens ({total_tokens:,.0f}) exceeds "
              f"initial mint (100,000). Need to mint more.")

    if dry_run:
        print("[!] This was a dry run. Use --live to execute.")
        print()
        # Save plan for review
        plan_file = DEPLOY_DIR / "airdrop_plan.json"
        DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
        with open(plan_file, "w") as f:
            json.dump({
                "mint": mint,
                "sol_price_usd": SOL_PRICE_USD,
                "token_price_usd": TOKEN_PRICE_USD,
                "total_sol": total_sol,
                "total_tokens": total_tokens,
                "distribution": distribution,
                "planned_at": datetime.now().isoformat(),
            }, f, indent=2)
        print(f"[+] Plan saved to {plan_file}")
        return

    # Execute airdrop
    print("[*] Executing airdrop...")
    print()

    input("Press Enter to confirm and start the airdrop... ")

    results = []
    for entry in distribution:
        wallet = entry["wallet"]
        tokens = entry["tokens"]
        print(f"[*] Transferring {tokens:,.0f} $MIND to {wallet[:20]}...")

        success = transfer_tokens(mint, tokens, wallet, dry_run=False)
        results.append({
            **entry,
            "success": success,
            "transferred_at": datetime.now().isoformat(),
        })

        if success:
            print(f"[+] Done: {tokens:,.0f} $MIND -> {wallet[:16]}...")
        else:
            print(f"[-] FAILED: {wallet[:16]}...")

    # Save results
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    with open(AIRDROP_LOG, "w") as f:
        json.dump({
            "mint": mint,
            "results": results,
            "total_transferred": sum(r["tokens"] for r in results if r["success"]),
            "completed_at": datetime.now().isoformat(),
        }, f, indent=2)

    succeeded = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    print()
    print(f"[+] Airdrop complete: {succeeded} succeeded, {failed} failed")
    print(f"[+] Log saved to {AIRDROP_LOG}")


if __name__ == "__main__":
    main()
