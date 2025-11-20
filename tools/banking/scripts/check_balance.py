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

    # Get both accounts
    accounts = {
        'Personal (Nicolas Reynolds)': 'e9777e0a-9016-43ff-a9bb-6d82d61f5827',
        'Joint (AURORE & Nicolas)': '040cc6e1-b3bb-44c9-ac34-028f3f15a4dd'
    }

    print("Fetching balances...")
    print()
    print("=" * 70)
    print("Mind Protocol - Revolut Account Balances")
    print("=" * 70)
    print()

    total_balance = 0.0

    for account_name, account_id in accounts.items():
        try:
            balance_data = client.get_balance(account_id)
            balances = balance_data.get("balances", [])

            print(f"{account_name}:")

            if not balances:
                print("  No balance information available")
            else:
                for balance in balances:
                    balance_amount = balance.get("balance_amount", {})
                    amount = balance_amount.get("amount", "0")
                    currency = balance_amount.get("currency", "EUR")
                    balance_type = balance.get("balance_type", "N/A")
                    balance_name = balance.get("name", "Unknown")

                    amount_float = float(amount)
                    total_balance += amount_float

                    # Format with color based on positive/negative
                    sign = "+" if amount_float >= 0 else ""
                    print(f"  {balance_name}")
                    print(f"  Amount: {sign}{amount} {currency}")
                    print(f"  Type: {balance_type}")

            print()

        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()

    print("-" * 70)
    sign = "+" if total_balance >= 0 else ""
    print(f"TOTAL ACROSS ALL ACCOUNTS: {sign}{total_balance:.2f} EUR")
    print("-" * 70)

    print()
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
