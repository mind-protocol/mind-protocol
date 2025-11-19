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
                f"Private key not found: {self.private_key_path}\n"
                f"Run: mv ~/Downloads/{app_id}.pem ~/.secrets/"
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
