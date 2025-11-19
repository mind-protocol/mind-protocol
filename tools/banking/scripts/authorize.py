#!/usr/bin/env python3
"""
Interactive script to authorize Revolut account access
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.enable_banking_client import EnableBankingClient


def main():
    """Run authorization flow"""
    print("=" * 60)
    print("Mind Protocol - Revolut Account Authorization")
    print("=" * 60)
    print()

    try:
        client = EnableBankingClient()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print()
        print("Setup instructions:")
        print("1. Sign up at https://enablebanking.com/sign-in/")
        print("2. Create application and download private key")
        print("3. Move key to ~/.secrets/")
        print("4. Add to .env.local:")
        print("   ENABLE_BANKING_APP_ID=your-app-id")
        print("   ENABLE_BANKING_PRIVATE_KEY_PATH=~/.secrets/your-key.pem")
        sys.exit(1)

    # Step 1: Initiate authorization
    print("Step 1: Initiating authorization flow...")
    try:
        auth_url = client.initiate_authorization(
            bank_name="Revolut",
            country="FI",
            access_valid_days=90
        )
    except Exception as e:
        print(f"❌ Failed to initiate authorization: {e}")
        sys.exit(1)

    print()
    print("Step 2: Complete authorization in your browser:")
    print()
    print(f"  {auth_url}")
    print()
    print("This will redirect you to Revolut to authenticate and grant")
    print("permission for Mind Protocol to access your account data.")
    print()

    # Step 2: Wait for authorization code
    print("After completing authorization, you'll be redirected to:")
    print(f"  {client.redirect_url}?code=AUTHORIZATION_CODE")
    print()
    auth_code = input("Enter the authorization code from the redirect URL: ").strip()

    if not auth_code:
        print("❌ Error: No authorization code provided")
        sys.exit(1)

    # Step 3: Create session
    print()
    print("Step 3: Creating session...")
    try:
        session = client.create_session(auth_code)
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        print()
        print("Common issues:")
        print("- Authorization code already used (codes expire after one use)")
        print("- Authorization code expired (codes expire after 10 minutes)")
        print("- Invalid authorization code (check for typos)")
        sys.exit(1)

    print()
    print("✅ Authorization successful!")
    print()
    print(f"Session ID: {session['session_id']}")
    print(f"Expires: {session.get('expires_at', 'N/A')}")
    print()
    print("Authorized Accounts:")
    for account in session.get("accounts", []):
        print(f"  - {account.get('currency', 'N/A')} Account: {account['uid']}")

    # Step 4: Save to environment
    print()
    print("=" * 60)
    print("Add these to your .env.local file:")
    print("=" * 60)
    print()
    print(f'REVOLUT_SESSION_ID={session["session_id"]}')
    if session.get("accounts"):
        print(f'REVOLUT_ACCOUNT_UID={session["accounts"][0]["uid"]}')

    print()
    print("=" * 60)
    print("Next steps:")
    print("  1. Update .env.local with the above variables")
    print("  2. Run: python tools/banking/scripts/check_balance.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
