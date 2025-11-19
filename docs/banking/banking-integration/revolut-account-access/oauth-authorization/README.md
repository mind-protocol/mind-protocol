# OAuth2-based Bank Authorization Flow

**Type:** MECHANISM
**Purpose:** Implement secure bank account authorization using OAuth2 + JWT authentication

---

## Mechanism Overview

The authorization mechanism uses a two-stage process:

1. **Application Authentication** - Your app authenticates to Enable Banking API using JWT signed with private key
2. **User Authorization** - User grants permission for your app to access their Revolut account

This separates *app identity* (JWT) from *user permission* (OAuth2), following PSD2 requirements.

## Components

### 1. Private Key Management

**Location:** `~/.secrets/[app-id].pem` (generated during app registration)

**Usage:**
- Signs JWT tokens for API authentication
- Never transmitted over network
- Permissions: 600 (owner read/write only)

**Lifecycle:**
- Generated once during app registration
- Rotated annually (security best practice)
- Backed up in secure vault

### 2. JWT Token Generation

**Purpose:** Authenticate the application (not the user) to Enable Banking API

**Structure:**
```json
{
  "header": {
    "alg": "RS256",
    "kid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
  },
  "payload": {
    "iss": "enablebanking.com",
    "aud": "api.enablebanking.com",
    "iat": 1700000000,
    "exp": 1700003600
  },
  "signature": "<RSA signature using private key>"
}
```

**Expiration:** 1 hour (3600 seconds)
**Algorithm:** RS256 (RSA signature with SHA-256)

See [JWT Token Generation Algorithm](./jwt-token-generation/README.md) for implementation details.

### 3. OAuth2 Authorization Flow

**Step-by-step:**

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ Mind Protocol│         │Enable Banking│         │   Revolut   │
│  Citizen     │         │     API      │         │    Bank     │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘
       │                        │                        │
       │ 1. Initiate auth       │                        │
       │───────────────────────>│                        │
       │    (with JWT token)    │                        │
       │                        │                        │
       │ 2. Return auth URL     │                        │
       │<───────────────────────│                        │
       │                        │                        │
       │ 3. Redirect user       │                        │
       │──────────────────────────────────────────────>│
       │                        │  (OAuth consent page)  │
       │                        │                        │
       │ 4. User authenticates  │                        │
       │                        │<───────────────────────│
       │                        │   (biometric/PIN)      │
       │                        │                        │
       │ 5. User grants permission                       │
       │                        │<───────────────────────│
       │                        │                        │
       │ 6. Redirect with code  │                        │
       │<──────────────────────────────────────────────│
       │   (?code=xyz123)       │                        │
       │                        │                        │
       │ 7. Exchange code for session                    │
       │───────────────────────>│                        │
       │    (with JWT token)    │                        │
       │                        │                        │
       │ 8. Return session + account UIDs               │
       │<───────────────────────│                        │
       │                        │                        │
       │ 9. Access account data │                        │
       │───────────────────────>│───────────────────────>│
       │    (with session ID)   │   (using PSD2 API)    │
       │                        │                        │
       │ 10. Return balances/txs│                        │
       │<───────────────────────│<───────────────────────│
```

### 4. Session Management

**Session Object:**
```json
{
  "session_id": "sess_abc123",
  "created_at": "2025-11-19T14:00:00Z",
  "expires_at": "2026-02-17T14:00:00Z",
  "accounts": [
    {
      "uid": "acct_xyz789",
      "currency": "EUR",
      "account_type": "current"
    }
  ]
}
```

**Storage:** Environment variable `REVOLUT_SESSION_ID`
**Refresh:** Automatic when expiry < 7 days
**Revocation:** Via Enable Banking dashboard or DELETE /sessions/:id

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `invalid_jwt` | JWT expired or malformed | Regenerate JWT with current timestamp |
| `unauthorized` | User denied permission | Re-initiate auth flow with explanation |
| `session_expired` | Session > 90 days old | Re-authorize with user consent |
| `insufficient_scope` | Missing permission | Request additional scopes in auth flow |
| `rate_limit_exceeded` | Too many API calls | Implement exponential backoff |

## Security Considerations

**Threats Mitigated:**
- ✅ Credential theft: No passwords stored
- ✅ Token interception: HTTPS only, short expiry
- ✅ Replay attacks: JWT includes timestamp (iat)
- ✅ Unauthorized access: OAuth2 requires explicit user consent

**Threats Remaining:**
- ⚠️ Private key compromise: Mitigate with key rotation + 600 permissions
- ⚠️ Session hijacking: Mitigate with session binding to IP (future)
- ⚠️ Man-in-the-middle: Mitigate with certificate pinning (future)

## Performance Characteristics

**JWT Generation:** < 10ms
**Auth flow initiation:** < 500ms
**User authorization:** 30-60 seconds (human interaction)
**Session creation:** < 1 second
**API calls with session:** < 2 seconds

---

**Algorithms:**
- [JWT Token Generation](./jwt-token-generation/README.md)

**Guides:**
- [How to Integrate Revolut Banking](./how-to-integrate-revolut/README.md)
