# JWT Token Generation Algorithm

**Type:** ALGORITHM
**Purpose:** Generate RS256-signed JWT tokens for Enable Banking API authentication

---

## Algorithm Specification

### Inputs

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `app_id` | UUID | Application ID from Enable Banking | `a027691d-30a3-43ed-8ff9-ca802e2b37a1` |
| `private_key_path` | Path | Path to PEM private key | `~/.secrets/a027691d-30a3-43ed-8ff9-ca802e2b37a1.pem` |
| `ttl` | Integer | Token time-to-live in seconds | `3600` (1 hour) |

### Outputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `jwt_token` | String | Signed JWT token for Authorization header |
| `expires_at` | Timestamp | When token becomes invalid |

### Algorithm Steps

**1. Load Private Key**
```python
def load_private_key(key_path: str) -> bytes:
    """
    Load RSA private key from PEM file

    Preconditions:
    - key_path exists and is readable
    - File contains valid RSA private key in PEM format

    Postconditions:
    - Returns key bytes suitable for RS256 signing
    """
    with open(key_path, 'rb') as f:
        return f.read()
```

**2. Calculate Timestamps**
```python
from datetime import datetime, timezone

def calculate_timestamps(ttl: int) -> tuple[int, int]:
    """
    Calculate JWT issued-at and expiration timestamps

    Args:
        ttl: Time-to-live in seconds

    Returns:
        (iat, exp) - Unix timestamps

    Example:
        >>> calculate_timestamps(3600)
        (1700000000, 1700003600)  # 1 hour apart
    """
    now = datetime.now(timezone.utc)
    iat = int(now.timestamp())
    exp = iat + ttl
    return (iat, exp)
```

**3. Construct JWT Payload**
```python
def construct_payload(iat: int, exp: int) -> dict:
    """
    Build JWT payload (claims)

    Required claims:
    - iss: Token issuer (always 'enablebanking.com')
    - aud: Intended audience (always 'api.enablebanking.com')
    - iat: Issued at (Unix timestamp)
    - exp: Expires at (Unix timestamp)

    Returns:
        Dictionary with JWT claims
    """
    return {
        "iss": "enablebanking.com",
        "aud": "api.enablebanking.com",
        "iat": iat,
        "exp": exp,
    }
```

**4. Sign JWT**
```python
import jwt as pyjwt

def sign_jwt(
    payload: dict,
    private_key: bytes,
    app_id: str
) -> str:
    """
    Sign JWT using RS256 algorithm

    Args:
        payload: JWT claims
        private_key: RSA private key (PEM format)
        app_id: Application ID (used as 'kid' header)

    Returns:
        Encoded JWT string

    Algorithm: RS256 (RSA Signature with SHA-256)
    """
    return pyjwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={"kid": app_id}
    )
```

**5. Complete Function**
```python
def generate_jwt_token(
    app_id: str,
    private_key_path: str,
    ttl: int = 3600
) -> tuple[str, int]:
    """
    Generate JWT token for Enable Banking API authentication

    Args:
        app_id: Enable Banking application ID
        private_key_path: Path to RSA private key PEM file
        ttl: Token lifetime in seconds (default: 1 hour)

    Returns:
        (jwt_token, expires_at) - Token string and expiry timestamp

    Raises:
        FileNotFoundError: Private key file not found
        ValueError: Invalid private key format

    Example:
        >>> token, exp = generate_jwt_token(
        ...     "a027691d-30a3-43ed-8ff9-ca802e2b37a1",
        ...     "~/.secrets/a027691d-30a3-43ed-8ff9-ca802e2b37a1.pem"
        ... )
        >>> print(token[:20])
        'eyJhbGciOiJSUzI1NiI...'
    """
    # Step 1: Load private key
    private_key = load_private_key(private_key_path)

    # Step 2: Calculate timestamps
    iat, exp = calculate_timestamps(ttl)

    # Step 3: Construct payload
    payload = construct_payload(iat, exp)

    # Step 4: Sign JWT
    jwt_token = sign_jwt(payload, private_key, app_id)

    return (jwt_token, exp)
```

## Complexity Analysis

**Time Complexity:** O(1)
- Key loading: O(1) - fixed file size
- Timestamp calculation: O(1)
- JWT signing: O(1) - RSA signature is constant time for fixed key size

**Space Complexity:** O(1)
- Private key: ~2-4 KB (fixed)
- JWT token: ~500-800 bytes (fixed)

**Performance:**
- Typical execution time: 5-10ms
- No network calls (pure computation)

## Security Properties

**Cryptographic Guarantees:**
- **Integrity:** RS256 signature prevents tampering
- **Authenticity:** Only holder of private key can generate valid tokens
- **Non-repudiation:** Signature proves token origin

**Expiration:**
- Short TTL (1 hour) limits damage from token leakage
- No revocation mechanism (rely on expiration)

**Key Security:**
- Private key never transmitted
- Should be rotated annually
- File permissions: 600 (owner read/write only)

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Private key missing | Raise `FileNotFoundError` with clear message |
| Private key corrupted | Raise `ValueError` from PyJWT library |
| System time incorrect | Token rejected by API (iat in future) |
| TTL too long | API may reject (max 24 hours recommended) |
| TTL negative | Raise `ValueError` before signing |

## Testing Strategy

**Unit Tests:**
```python
def test_jwt_generation():
    """Verify JWT token structure and signature"""
    token, exp = generate_jwt_token(app_id, key_path)

    # Decode without verification (check structure)
    decoded = pyjwt.decode(token, options={"verify_signature": False})

    assert decoded["iss"] == "enablebanking.com"
    assert decoded["aud"] == "api.enablebanking.com"
    assert decoded["exp"] - decoded["iat"] == 3600

def test_token_verification():
    """Verify token can be validated with public key"""
    token, _ = generate_jwt_token(app_id, key_path)

    # Load corresponding public key
    with open(public_key_path, 'rb') as f:
        public_key = f.read()

    # Should not raise exception
    pyjwt.decode(token, public_key, algorithms=["RS256"])
```

**Integration Test:**
```python
def test_api_authentication():
    """Verify token works with Enable Banking API"""
    token, _ = generate_jwt_token(app_id, key_path)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "https://api.enablebanking.com/aspsps?country=FI",
        headers=headers
    )

    assert response.status_code == 200
```

---

**Implementation:** See [How to Integrate Revolut Banking](../how-to-integrate-revolut/README.md) for complete code
