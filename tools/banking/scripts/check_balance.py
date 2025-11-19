#!/usr/bin/env python3
"""
Check Revolut account balance
"""
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.enable_banking_client import EnableBankingClient


def main():
    """Check account balance"""
    try:
        client = EnableBankingClient()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)

    account_uid = os.getenv("REVOLUT_ACCOUNT_UID")
    if not account_uid:
        print("❌ Error: REVOLUT_ACCOUNT_UID not set in .env.local")
        print()
        print("Run authorization first:")
        print("  python tools/banking/scripts/authorize.py")
        sys.exit(1)

    print("Fetching balance...")
    try:
        balance_data = client.get_balance(account_uid)
    except Exception as e:
        print(f"❌ Failed to fetch balance: {e}")
        print()
        print("Common issues:")
        print("- Session expired (re-run authorize.py)")
        print("- Invalid account UID (check .env.local)")
        print("- Network connectivity issues")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Mind Protocol - Revolut Account Balance")
    print("=" * 60)
    print()

    balances = balance_data.get("balances", [])
    if not balances:
        print("No balance information available")
    else:
        for balance in balances:
            amount = balance.get("amount", "0")
            currency = balance.get("currency", "EUR")
            balance_type = balance.get("type", "interimAvailable")

            print(f"{balance_type.upper()}: {amount} {currency}")

    print()
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
