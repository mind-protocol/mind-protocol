"""
Capability token validation for wallet custody requests.

Tokens are short-lived JWTs signed with an HMAC shared secret. Claims:
- `sub`: request subject (e.g., citizen id or mission id)
- `aud`: must match configured audience (default: codex-c-wcs)
- `exp`: expiry epoch seconds (enforced by PyJWT)
- `cap`: capability string or list (e.g., ["wallet.sign"])
- `citizen_id`: optional explicit citizen identifier binding
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List, Mapping, Sequence

import jwt
from jwt import InvalidTokenError

from .config import WalletCustodySettings

logger = logging.getLogger(__name__)


@dataclass
class CapabilityToken:
    """Decoded capability token payload."""

    subject: str
    audience: str
    capabilities: List[str]
    citizen_id: str | None
    raw_claims: Mapping[str, object]


class CapabilityTokenValidator:
    """Validates HMAC/JWT capability tokens for custody operations."""

    def __init__(self, settings: WalletCustodySettings) -> None:
        self._secret = settings.capability_secret
        self._audience = settings.capability_audience

    def decode(self, token: str) -> CapabilityToken:
        """Decode and verify token signature + expiry."""
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                audience=self._audience,
                options={"require": ["sub", "aud", "exp", "cap"]},
            )
        except InvalidTokenError as exc:
            logger.warning("Capability token invalid: %s", exc)
            raise

        capabilities = claims["cap"]
        if isinstance(capabilities, str):
            capabilities = [capabilities]

        citizen_id = claims.get("citizen_id")

        return CapabilityToken(
            subject=str(claims["sub"]),
            audience=str(claims["aud"]),
            capabilities=list(capabilities),
            citizen_id=str(citizen_id) if citizen_id is not None else None,
            raw_claims=claims,
        )

    @staticmethod
    def ensure_capability(token: CapabilityToken, required: str) -> None:
        """Ensure the token includes the required capability identifier."""
        if required not in token.capabilities:
            raise PermissionError(
                f"Capability token missing permission: {required}"
            )

