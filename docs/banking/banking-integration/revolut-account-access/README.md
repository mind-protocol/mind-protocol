# Revolut Account Access via Enable Banking API

**Type:** BEHAVIOR_SPEC
**Purpose:** Define the expected behavior for accessing Revolut bank accounts programmatically

---

## Behavioral Requirements

### 1. Account Authorization

**Expected Behavior:**
- Citizen initiates bank account access request
- User is redirected to Enable Banking → Revolut OAuth flow
- User authenticates with Revolut (biometric/PIN)
- User grants specific permissions (read balances, read transactions, initiate payments)
- Authorization code is returned to application
- Application exchanges code for session token
- Session token valid for specified duration (e.g., 90 days)

**Security Constraints:**
- No bank credentials stored in application
- Session tokens stored in encrypted environment variables
- Tokens auto-refresh before expiration
- Revocation possible via Enable Banking dashboard

### 2. Balance Retrieval

**Expected Behavior:**
```
Input: Account UID
Output: {
  "currency": "EUR",
  "amount": "12,450.75",
  "type": "interimAvailable",
  "timestamp": "2025-11-19T14:30:00Z"
}
```

**Constraints:**
- Real-time data (not cached > 5 minutes)
- Supports multi-currency accounts
- Handles multiple account types (current, savings, etc.)

### 3. Transaction History

**Expected Behavior:**
```
Input: Account UID, date_from, date_to
Output: [
  {
    "transaction_id": "tx_abc123",
    "date": "2025-11-18",
    "amount": "-89.99",
    "currency": "EUR",
    "description": "Anthropic API - Claude usage",
    "merchant": "Anthropic PBC",
    "category": "compute_costs"
  },
  ...
]
```

**Constraints:**
- Support pagination (max 100 transactions per request)
- Date range limited to 90 days per query
- Automatic categorization of transactions
- Deduplication of pending transactions

### 4. Budget Monitoring

**Expected Behavior:**
- Calculate monthly burn rate from transaction history
- Categorize expenses (compute, infrastructure, compensation, other)
- Alert when balance < 30 days runway at current burn rate
- Forecast balance based on known upcoming expenses

**Thresholds:**
- 🟢 Green: > 90 days runway
- 🟡 Yellow: 30-90 days runway
- 🔴 Red: < 30 days runway
- 🚨 Critical: < 7 days runway

### 5. Error Handling

**Expected Behaviors:**
- **Token expired:** Auto-refresh if refresh token valid, else notify for re-authorization
- **Network timeout:** Retry with exponential backoff (3 attempts)
- **Bank service down:** Cache last known state, poll for recovery
- **Insufficient permissions:** Clear error message indicating missing scopes

## State Transitions

```
[No Authorization]
  → initiate_auth()
  → [Pending Authorization]
  → user_completes_oauth()
  → [Authorized]

[Authorized]
  → get_balance() → [Balance Retrieved]
  → get_transactions() → [Transactions Retrieved]
  → token_expires() → [Token Expired] → refresh_token() → [Authorized]
```

## Integration Points

**Upstream:**
- Enable Banking API (external dependency)
- Revolut bank account (user's financial institution)

**Downstream:**
- Mind Protocol backend (`/api/budget/account` endpoint)
- Dashboard budget visualization
- Alerting system (Slack/email notifications)
- Treasury management (financeOrg entity)

## Success Criteria

✅ **Authorization:**
- Citizen can complete OAuth flow without manual intervention
- Session tokens remain valid for 90 days
- Token refresh happens automatically

✅ **Data Access:**
- Balance retrieval < 2 seconds
- Transaction history retrieval < 5 seconds
- Data accuracy matches Revolut app

✅ **Budget Monitoring:**
- Burn rate calculation accurate to ±5%
- Alerts trigger within 1 hour of crossing threshold
- Category predictions > 80% accurate

## Non-Functional Requirements

**Performance:**
- API response time < 3 seconds (95th percentile)
- Support 100 requests/hour (Enable Banking sandbox limit)

**Reliability:**
- 99% uptime (dependent on Enable Banking uptime)
- Graceful degradation when bank API unavailable

**Security:**
- All API calls over HTTPS
- Secrets stored in environment variables, never in code
- Audit log of all API requests with citizen attribution

---

**Related Mechanisms:**
- [OAuth2 Authorization Flow](./oauth-authorization/README.md)
- [Budget Monitoring](./budget-monitoring/README.md)

**Implementation Guide:**
- [How to Integrate Revolut](./oauth-authorization/how-to-integrate-revolut/README.md)
