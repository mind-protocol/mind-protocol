# How to Integrate Revolut Banking

**Type:** GUIDE
**Purpose:** Step-by-step implementation guide for Revolut account integration

---

## Prerequisites

**Required:**
- Python 3.9+
- Enable Banking account (free signup)
- Revolut account (personal or business)
- Private key stored in `~/.secrets/` (see setup below)

**Python Dependencies:**
```bash
pip install pyjwt requests cryptography python-dotenv
```

---

## Setup Guide

### Step 1: Register Application with Enable Banking

1. **Sign up:** Visit https://enablebanking.com/sign-in/
   - Enter your email
   - Click one-time auth link sent to your email

2. **Create Application:**
   - Go to https://enablebanking.com/applications
   - Click "Add a new application"
   - Fill in the form:
     - **Environment:** Sandbox (for testing)
     - **Application Name:** "Mind Protocol Budget Manager"
     - **Redirect URLs:** `http://localhost:8000/callback` (for local testing)
   - **Important:** Check "Generate private key" option
   - Click "Register"

3. **Save Private Key:**
   ```bash
   # Your browser will download: a027691d-...-eeee.pem
   # Move it to secrets directory
   mv ~/Downloads/a027691d-30a3-43ed-8ff9-ca802e2b37a1.pem ~/.secrets/
   chmod 600 ~/.secrets/a027691d-30a3-43ed-8ff9-ca802e2b37a1.pem
   ```

4. **Note Your Application ID:**
   - The filename IS your application ID: `a027691d-30a3-43ed-8ff9-ca802e2b37a1`
   - Save this - you'll need it in environment variables

### Step 2: Configure Environment Variables

Create `/home/mind-protocol/mind-protocol/.env.local`:

```bash
# Enable Banking Configuration
ENABLE_BANKING_APP_ID=a027691d-30a3-43ed-8ff9-ca802e2b37a1
ENABLE_BANKING_PRIVATE_KEY_PATH=/home/mind-protocol/.secrets/a027691d-30a3-43ed-8ff9-ca802e2b37a1.pem
ENABLE_BANKING_REDIRECT_URL=http://localhost:8000/callback
ENABLE_BANKING_ENV=sandbox  # Change to 'production' when ready

# Revolut Session (will be populated after authorization)
REVOLUT_SESSION_ID=
REVOLUT_ACCOUNT_UID=
```

### Step 3: Implement JWT Token Generator

Create `tools/banking/lib/jwt_generator.py`:

```python
"""
JWT token generation for Enable Banking API authentication
"""
import jwt as pyjwt
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple


class JWTGenerator:
    """Generate JWT tokens for Enable Banking API"""

    def __init__(self, app_id: str, private_key_path: str):
        """
        Initialize JWT generator

        Args:
            app_id: Enable Banking application ID
            private_key_path: Path to RSA private key PEM file
        """
        self.app_id = app_id
        self.private_key_path = Path(private_key_path).expanduser()

        if not self.private_key_path.exists():
            raise FileNotFoundError(
                f"Private key not found: {self.private_key_path}"
            )

    def generate_token(self, ttl: int = 3600) -> Tuple[str, int]:
        """
        Generate JWT token for API authentication

        Args:
            ttl: Token time-to-live in seconds (default: 1 hour)

        Returns:
            (jwt_token, expires_at) tuple

        Raises:
            FileNotFoundError: Private key file not found
            ValueError: Invalid private key format
        """
        # Load private key
        with open(self.private_key_path, 'rb') as f:
            private_key = f.read()

        # Calculate timestamps
        now = datetime.now(timezone.utc)
        iat = int(now.timestamp())
        exp = iat + ttl

        # Construct payload
        payload = {
            "iss": "enablebanking.com",
            "aud": "api.enablebanking.com",
            "iat": iat,
            "exp": exp,
        }

        # Sign JWT
        jwt_token = pyjwt.encode(
            payload,
            private_key,
            algorithm="RS256",
            headers={"kid": self.app_id}
        )

        return (jwt_token, exp)

    def get_auth_header(self) -> dict:
        """
        Get Authorization header for API requests

        Returns:
            Dictionary with Authorization header

        Example:
            >>> generator = JWTGenerator(app_id, key_path)
            >>> headers = generator.get_auth_header()
            >>> requests.get(url, headers=headers)
        """
        token, _ = self.generate_token()
        return {"Authorization": f"Bearer {token}"}
```

### Step 4: Implement Banking Client

Create `tools/banking/lib/enable_banking_client.py`:

```python
"""
Enable Banking API client for Revolut integration
"""
import os
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from dotenv import load_dotenv

from .jwt_generator import JWTGenerator


class EnableBankingClient:
    """Client for Enable Banking API"""

    BASE_URL = "https://api.enablebanking.com"

    def __init__(self):
        """Initialize client from environment variables"""
        load_dotenv()

        app_id = os.getenv("ENABLE_BANKING_APP_ID")
        key_path = os.getenv("ENABLE_BANKING_PRIVATE_KEY_PATH")

        if not app_id or not key_path:
            raise ValueError(
                "Missing environment variables: "
                "ENABLE_BANKING_APP_ID, ENABLE_BANKING_PRIVATE_KEY_PATH"
            )

        self.jwt_generator = JWTGenerator(app_id, key_path)
        self.redirect_url = os.getenv("ENABLE_BANKING_REDIRECT_URL")
        self.session_id = os.getenv("REVOLUT_SESSION_ID")

    def list_banks(self, country: str = "FI") -> List[Dict]:
        """
        Get list of available banks in a country

        Args:
            country: Two-letter ISO 3166 country code

        Returns:
            List of bank dictionaries
        """
        headers = self.jwt_generator.get_auth_header()
        response = requests.get(
            f"{self.BASE_URL}/aspsps",
            params={"country": country},
            headers=headers
        )
        response.raise_for_status()
        return response.json()["aspsps"]

    def initiate_authorization(
        self,
        bank_name: str = "Revolut",
        country: str = "FI",
        access_valid_days: int = 90
    ) -> str:
        """
        Initiate bank account authorization flow

        Args:
            bank_name: Name of the bank (e.g., "Revolut")
            country: Two-letter country code
            access_valid_days: How long access is valid (default: 90 days)

        Returns:
            Authorization URL to redirect user to

        Example:
            >>> client = EnableBankingClient()
            >>> auth_url = client.initiate_authorization()
            >>> print(f"Visit this URL: {auth_url}")
        """
        headers = self.jwt_generator.get_auth_header()

        valid_until = (
            datetime.now(timezone.utc) + timedelta(days=access_valid_days)
        ).isoformat()

        body = {
            "access": {"valid_until": valid_until},
            "aspsp": {"name": bank_name, "country": country},
            "state": "mind_protocol_auth",
            "redirect_url": self.redirect_url,
            "psu_type": "personal",
        }

        response = requests.post(
            f"{self.BASE_URL}/auth",
            json=body,
            headers=headers
        )
        response.raise_for_status()
        return response.json()["url"]

    def create_session(self, authorization_code: str) -> Dict:
        """
        Exchange authorization code for session token

        Args:
            authorization_code: Code from redirect URL after user authorization

        Returns:
            Session object with session_id and authorized accounts

        Example:
            >>> # After user completes OAuth flow, you get code from URL:
            >>> # http://localhost:8000/callback?code=xyz123
            >>> session = client.create_session("xyz123")
            >>> print(session["session_id"])
            >>> print(session["accounts"])
        """
        headers = self.jwt_generator.get_auth_header()
        body = {"code": authorization_code}

        response = requests.post(
            f"{self.BASE_URL}/sessions",
            json=body,
            headers=headers
        )
        response.raise_for_status()

        session = response.json()
        # Save session ID to environment
        self.session_id = session["session_id"]
        return session

    def get_balance(self, account_uid: str) -> Dict:
        """
        Get current balance for an account

        Args:
            account_uid: Account UID from session creation

        Returns:
            Balance information

        Example:
            >>> balance = client.get_balance("acct_xyz789")
            >>> print(f"{balance['amount']} {balance['currency']}")
        """
        if not self.session_id:
            raise ValueError("No active session. Run authorization flow first.")

        headers = self.jwt_generator.get_auth_header()
        response = requests.get(
            f"{self.BASE_URL}/accounts/{account_uid}/balances",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    def get_transactions(
        self,
        account_uid: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict]:
        """
        Get transaction history for an account

        Args:
            account_uid: Account UID
            date_from: Start date (ISO format, optional)
            date_to: End date (ISO format, optional)

        Returns:
            List of transactions

        Example:
            >>> txs = client.get_transactions("acct_xyz789")
            >>> for tx in txs:
            ...     print(f"{tx['date']}: {tx['amount']} - {tx['description']}")
        """
        if not self.session_id:
            raise ValueError("No active session. Run authorization flow first.")

        headers = self.jwt_generator.get_auth_header()
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to

        response = requests.get(
            f"{self.BASE_URL}/accounts/{account_uid}/transactions",
            params=params,
            headers=headers
        )
        response.raise_for_status()
        return response.json()["transactions"]
```

### Step 5: Create Authorization Script

Create `tools/banking/scripts/authorize.py`:

```python
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

    client = EnableBankingClient()

    # Step 1: Initiate authorization
    print("Step 1: Initiating authorization flow...")
    auth_url = client.initiate_authorization(
        bank_name="Revolut",
        country="FI",
        access_valid_days=90
    )

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
        print("Error: No authorization code provided")
        sys.exit(1)

    # Step 3: Create session
    print()
    print("Step 3: Creating session...")
    session = client.create_session(auth_code)

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
    print("Add these to your .env.local file:")
    print()
    print(f'REVOLUT_SESSION_ID={session["session_id"]}')
    if session.get("accounts"):
        print(f'REVOLUT_ACCOUNT_UID={session["accounts"][0]["uid"]}')

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
```

Make it executable:
```bash
chmod +x tools/banking/scripts/authorize.py
```

### Step 6: Create Balance Checker

Create `tools/banking/scripts/check_balance.py`:

```python
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
    client = EnableBankingClient()

    account_uid = os.getenv("REVOLUT_ACCOUNT_UID")
    if not account_uid:
        print("Error: REVOLUT_ACCOUNT_UID not set in .env.local")
        print("Run: python tools/banking/scripts/authorize.py first")
        sys.exit(1)

    print("Fetching balance...")
    balance_data = client.get_balance(account_uid)

    print()
    print("=" * 60)
    print("Mind Protocol - Revolut Account Balance")
    print("=" * 60)
    print()

    for balance in balance_data.get("balances", []):
        amount = balance.get("amount", "0")
        currency = balance.get("currency", "EUR")
        balance_type = balance.get("type", "interimAvailable")

        print(f"{balance_type.upper()}: {amount} {currency}")

    print()
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

Make it executable:
```bash
chmod +x tools/banking/scripts/check_balance.py
```

---

## Usage Instructions

### First-Time Setup

1. **Run authorization:**
   ```bash
   cd /home/mind-protocol/mind-protocol
   python tools/banking/scripts/authorize.py
   ```

2. **Follow the prompts:**
   - Opens browser to Revolut authorization
   - Login to Revolut (biometric/PIN)
   - Grant permissions
   - Copy authorization code from redirect URL

3. **Save credentials:**
   - Update `.env.local` with `REVOLUT_SESSION_ID` and `REVOLUT_ACCOUNT_UID`

### Daily Usage

**Check balance:**
```bash
python tools/banking/scripts/check_balance.py
```

**View transactions:**
```bash
python tools/banking/scripts/check_transactions.py
# (Create this following the same pattern as check_balance.py)
```

---

## Production Deployment

### Render Environment Variables

When deploying to production:

1. **In Render Dashboard:**
   ```
   ENABLE_BANKING_APP_ID=a027691d-...
   ENABLE_BANKING_PRIVATE_KEY_PATH=/etc/secrets/banking-key.pem
   ENABLE_BANKING_ENV=production
   REVOLUT_SESSION_ID=sess_...  (after authorization)
   REVOLUT_ACCOUNT_UID=acct_...  (after authorization)
   ```

2. **Upload private key as Secret File in Render**

### Session Refresh

Sessions expire after 90 days. Set up automatic refresh:

```python
# In tools/banking/lib/session_manager.py
def check_and_refresh_session(client):
    """Auto-refresh session if expiring soon"""
    # Check expiry, re-authorize if < 7 days
    # Send notification to admin for manual re-auth
```

---

## Testing

**Sandbox Testing:**
```bash
# .env.local
ENABLE_BANKING_ENV=sandbox

# Use test credentials from Enable Banking docs
```

**Production Testing:**
```bash
# Change to production environment
ENABLE_BANKING_ENV=production

# Authorize with REAL Revolut account
# Test with small amounts first
```

---

## Troubleshooting

**Error: "Private key not found"**
- Check path in `ENABLE_BANKING_PRIVATE_KEY_PATH`
- Verify file permissions: `ls -la ~/.secrets/*.pem`

**Error: "Invalid JWT"**
- Check system time (JWT uses timestamps)
- Verify app_id matches private key filename

**Error: "Session expired"**
- Re-run authorization flow: `python tools/banking/scripts/authorize.py`

**Error: "Insufficient permissions"**
- During authorization, ensure all scopes are granted
- May need to delete old authorization and re-authorize

---

## Security Checklist

✅ Private key stored in `~/.secrets/` with 600 permissions
✅ Private key path in `.env.local` (gitignored)
✅ Session tokens in environment variables, not code
✅ JWT tokens expire after 1 hour
✅ Sessions expire after 90 days
✅ All API calls over HTTPS
✅ No credentials in git repository

---

**Next Steps:**
- Implement budget monitoring dashboard
- Set up balance alerts (< 30 days runway)
- Add transaction categorization (compute vs infrastructure costs)
- Create monthly budget reports
