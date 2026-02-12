#!/usr/bin/env python3
"""
$MIND Pre-Sale Wallet Monitor

Monitors the deployer wallet for incoming SOL transfers.
Tracks buyer wallets and amounts for the airdrop.

Usage:
    python3 monitor_presale.py                    # Check once
    python3 monitor_presale.py --loop             # Continuous monitoring (30s)
    python3 monitor_presale.py --loop --interval 10  # Custom interval
    python3 monitor_presale.py --summary          # Show summary only
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

DEPLOYER_WALLET = "CCsJLZR8b19iDgS9hXUYs9q2c928ihzZdfSgZLPYffWg"
RPC_URL = "https://api.mainnet-beta.solana.com"
PRESALE_FILE = Path(__file__).parent / "deploy_output" / "presale_buyers.json"
TICKET_SIZE_SOL = 2.0
TOKEN_PRICE_USD = 0.20
SOL_PRICE_USD = 195.0  # Update as needed


def get_wallet_balance() -> float:
    """Get current SOL balance."""
    result = subprocess.run(
        ["solana", "balance", DEPLOYER_WALLET, "--url", RPC_URL],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return float(result.stdout.strip().split()[0])
    return 0.0


def get_recent_transactions(limit: int = 20) -> list[str]:
    """Get recent transaction signatures."""
    result = subprocess.run(
        ["solana", "transaction-history", DEPLOYER_WALLET,
         "--url", RPC_URL, "--limit", str(limit)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        sigs = [line.strip() for line in result.stdout.strip().split("\n")
                if line.strip() and "transactions found" not in line]
        return sigs
    return []


def get_transaction_details(signature: str) -> dict | None:
    """Get transaction details."""
    result = subprocess.run(
        ["solana", "confirm", "-v", signature, "--url", RPC_URL],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return {"signature": signature, "raw": result.stdout}
    return None


def load_presale_state() -> dict:
    """Load existing presale tracking state."""
    PRESALE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if PRESALE_FILE.exists():
        with open(PRESALE_FILE) as f:
            return json.load(f)
    return {
        "deployer_wallet": DEPLOYER_WALLET,
        "initial_balance": 0.371258527,
        "ticket_size_sol": TICKET_SIZE_SOL,
        "token_price_usd": TOKEN_PRICE_USD,
        "buyers": {},
        "known_signatures": [],
        "last_check": None,
        "total_raised_sol": 0.0,
    }


def save_presale_state(state: dict):
    """Save presale tracking state."""
    PRESALE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PRESALE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check_for_new_deposits(state: dict) -> list[dict]:
    """Check for new SOL deposits to the deployer wallet."""
    current_balance = get_wallet_balance()
    initial_balance = state["initial_balance"]
    raised = current_balance - initial_balance

    new_deposits = []

    if raised > state["total_raised_sol"] + 0.001:
        new_amount = raised - state["total_raised_sol"]
        tickets = int(new_amount / TICKET_SIZE_SOL + 0.5)
        new_deposits.append({
            "amount_sol": new_amount,
            "tickets": tickets,
            "detected_at": datetime.now().isoformat(),
        })
        state["total_raised_sol"] = raised

    state["current_balance"] = current_balance
    state["last_check"] = datetime.now().isoformat()

    return new_deposits


def print_summary(state: dict):
    """Print presale summary."""
    current_balance = get_wallet_balance()
    raised = current_balance - state["initial_balance"]
    tickets = int(raised / TICKET_SIZE_SOL + 0.5)
    tokens_owed = raised * SOL_PRICE_USD / TOKEN_PRICE_USD

    print("=" * 50)
    print("  $MIND Pre-Sale Monitor")
    print("=" * 50)
    print(f"  Deployer:          {DEPLOYER_WALLET[:16]}...")
    print(f"  Current Balance:   {current_balance:.4f} SOL")
    print(f"  Initial Balance:   {state['initial_balance']:.4f} SOL")
    print(f"  Raised:            {raised:.4f} SOL")
    print(f"  Tickets (2 SOL):   {tickets}")
    print(f"  Tokens Owed:       {tokens_owed:,.0f} $MIND (at ${TOKEN_PRICE_USD})")
    print(f"  Buyers:            {len(state.get('buyers', {}))}")
    print(f"  Last Check:        {state.get('last_check', 'never')}")
    print("=" * 50)

    if state.get("buyers"):
        print("\n  Buyers:")
        for wallet, info in state["buyers"].items():
            print(f"    {wallet[:16]}... — {info['total_sol']} SOL "
                  f"({info['tickets']} tickets)")


def main():
    parser = argparse.ArgumentParser(description="$MIND Pre-Sale Monitor")
    parser.add_argument("--loop", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=30, help="Check interval (seconds)")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    args = parser.parse_args()

    state = load_presale_state()

    if args.summary:
        print_summary(state)
        return

    print(f"[*] Monitoring deployer wallet: {DEPLOYER_WALLET[:20]}...")
    print(f"[*] Initial balance: {state['initial_balance']} SOL")
    print(f"[*] Ticket size: {TICKET_SIZE_SOL} SOL")
    print()

    while True:
        new_deposits = check_for_new_deposits(state)
        save_presale_state(state)

        if new_deposits:
            for dep in new_deposits:
                print(f"[+] NEW DEPOSIT: {dep['amount_sol']:.4f} SOL "
                      f"({dep['tickets']} tickets) at {dep['detected_at']}")
        else:
            balance = state.get("current_balance", 0)
            raised = balance - state["initial_balance"]
            print(f"[*] {datetime.now().strftime('%H:%M:%S')} — "
                  f"Balance: {balance:.4f} SOL | "
                  f"Raised: {raised:.4f} SOL | "
                  f"Tickets: {int(raised / TICKET_SIZE_SOL + 0.5)}")

        if not args.loop:
            print()
            print_summary(state)
            break

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
