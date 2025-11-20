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
        # Load from .env.local first (development), then .env (fallback)
        load_dotenv('.env.local')
        load_dotenv()

        app_id = os.getenv("ENABLE_BANKING_APP_ID")
        key_path = os.getenv("ENABLE_BANKING_PRIVATE_KEY_PATH")

        if not app_id or not key_path:
            raise ValueError(
                "Missing environment variables:\n"
                "  ENABLE_BANKING_APP_ID\n"
                "  ENABLE_BANKING_PRIVATE_KEY_PATH\n\n"
                "Add these to .env.local"
            )

        self.jwt_generator = JWTGenerator(app_id, key_path)
        self.redirect_url = os.getenv("ENABLE_BANKING_REDIRECT_URL", "http://localhost:8000/callback")
        self.session_id = os.getenv("REVOLUT_SESSION_ID")

    def list_banks(self, country: str = "FR") -> List[Dict]:
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
        country: str = "FR",
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
            raise ValueError(
                "No active session. Run authorization flow first:\n"
                "  python tools/banking/scripts/authorize.py"
            )

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
            raise ValueError(
                "No active session. Run authorization flow first:\n"
                "  python tools/banking/scripts/authorize.py"
            )

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
