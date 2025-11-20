#!/usr/bin/env python3
"""
Check Revolut transaction history
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.enable_banking_client import EnableBankingClient


def main():
    """Check transaction history"""
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

    # Get last 30 days of transactions
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    date_to = datetime.now().strftime("%Y-%m-%d")

    print(f"Fetching transactions from {date_from} to {date_to}...")
    try:
        transactions = client.get_transactions(
            account_uid,
            date_from=date_from,
            date_to=date_to
        )
    except Exception as e:
        print(f"❌ Failed to fetch transactions: {e}")
        print()
        print("Common issues:")
        print("- Session expired (re-run authorize.py)")
        print("- Invalid account UID (check .env.local)")
        print("- Network connectivity issues")
        sys.exit(1)

    print()
    print("=" * 80)
    print("Mind Protocol - Revolut Transaction History")
    print("=" * 80)
    print()

    if not transactions:
        print("No transactions found for this period")
    else:
        print(f"Found {len(transactions)} transactions:")
        print()
        print(f"{'Date':<12} {'Type':<6} {'Amount':<12} {'Currency':<8} {'Description':<35}")
        print("-" * 80)

        total_debit = 0.0
        total_credit = 0.0

        for tx in sorted(transactions, key=lambda x: x.get('booking_date', ''), reverse=True):
            # Parse transaction data
            date = tx.get('booking_date', tx.get('value_date', 'N/A'))

            # Get amount and currency
            tx_amount = tx.get('transaction_amount', {})
            amount = tx_amount.get('amount', '0')
            currency = tx_amount.get('currency', 'EUR')

            # Get description from remittance_information
            remittance = tx.get('remittance_information', [])
            description = remittance[0] if remittance else 'No description'
            description = description[:35]

            # Credit or Debit
            indicator = tx.get('credit_debit_indicator', 'DBIT')
            tx_type = 'OUT' if indicator == 'DBIT' else 'IN'

            # Format amount with sign
            amount_float = float(amount)
            if indicator == 'DBIT':
                amount_display = f"-{amount}"
                total_debit += amount_float
            else:
                amount_display = f"+{amount}"
                total_credit += amount_float

            print(f"{date:<12} {tx_type:<6} {amount_display:<12} {currency:<8} {description:<35}")

        print("-" * 80)
        net_change = total_credit - total_debit
        print(f"{'IN (credit):':<20} +{total_credit:<11.2f} EUR")
        print(f"{'OUT (debit):':<20} -{total_debit:<11.2f} EUR")
        print(f"{'NET CHANGE:':<20} {net_change:+<12.2f} EUR")

    print()
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
