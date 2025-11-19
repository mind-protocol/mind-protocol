# Mind Protocol - Banking Integration

Programmatic access to Revolut bank accounts for budget management and autonomous purchasing.

## Quick Start

### 1. Install Dependencies

```bash
cd /home/mind-protocol/mind-protocol
pip install -r tools/banking/requirements.txt
```

### 2. Configure Enable Banking

1. Sign up: https://enablebanking.com/sign-in/
2. Create application: https://enablebanking.com/applications
3. Download private key (e.g., `a027691d-....pem`)
4. Move to secrets:
   ```bash
   mv ~/Downloads/a027691d-*.pem ~/.secrets/
   chmod 600 ~/.secrets/a027691d-*.pem
   ```

### 3. Configure Environment

Add to `.env.local`:

```bash
# Enable Banking
ENABLE_BANKING_APP_ID=a027691d-30a3-43ed-8ff9-ca802e2b37a1
ENABLE_BANKING_PRIVATE_KEY_PATH=/home/mind-protocol/.secrets/a027691d-30a3-43ed-8ff9-ca802e2b37a1.pem
ENABLE_BANKING_REDIRECT_URL=http://localhost:8000/callback
ENABLE_BANKING_ENV=sandbox  # or 'production'

# Revolut (populated after authorization)
REVOLUT_SESSION_ID=
REVOLUT_ACCOUNT_UID=
```

### 4. Authorize Revolut Account

```bash
python tools/banking/scripts/authorize.py
```

Follow the prompts to complete OAuth flow.

### 5. Check Balance

```bash
python tools/banking/scripts/check_balance.py
```

### 6. View Transactions

```bash
python tools/banking/scripts/check_transactions.py
```

---

## Documentation

Full documentation in PATTERN → GUIDE hierarchy:

- **[PATTERN](../../docs/banking/README.md)** - Banking integration architecture
- **[BEHAVIOR_SPEC](../../docs/banking/banking-integration/revolut-account-access/README.md)** - Expected behaviors
- **[MECHANISM](../../docs/banking/banking-integration/revolut-account-access/oauth-authorization/README.md)** - OAuth2 flow
- **[ALGORITHM](../../docs/banking/banking-integration/revolut-account-access/oauth-authorization/jwt-token-generation/README.md)** - JWT generation
- **[GUIDE](../../docs/banking/banking-integration/revolut-account-access/oauth-authorization/how-to-integrate-revolut/README.md)** - Implementation guide

---

## Architecture

```
tools/banking/
├── lib/
│   ├── __init__.py
│   ├── jwt_generator.py           # JWT token generation
│   └── enable_banking_client.py   # Enable Banking API client
├── scripts/
│   ├── authorize.py               # Interactive OAuth flow
│   ├── check_balance.py           # Check account balance
│   └── check_transactions.py      # View transaction history
├── config/
│   └── .env.example              # Example configuration
└── README.md                      # This file
```

---

## Security

✅ **Best Practices:**
- Private keys in `~/.secrets/` with 600 permissions
- Session tokens in environment variables
- All API calls over HTTPS
- JWT tokens expire after 1 hour
- Sessions expire after 90 days

❌ **Never:**
- Commit private keys to git
- Store credentials in code
- Share session tokens
- Use production keys in sandbox

---

## API Reference

### JWTGenerator

```python
from lib.jwt_generator import JWTGenerator

generator = JWTGenerator(app_id, private_key_path)
token, expires_at = generator.generate_token(ttl=3600)
headers = generator.get_auth_header()
```

### EnableBankingClient

```python
from lib.enable_banking_client import EnableBankingClient

client = EnableBankingClient()

# List available banks
banks = client.list_banks(country="FI")

# Initiate authorization
auth_url = client.initiate_authorization(
    bank_name="Revolut",
    country="FI",
    access_valid_days=90
)

# Create session (after user completes OAuth)
session = client.create_session(authorization_code)

# Get balance
balance = client.get_balance(account_uid)

# Get transactions
transactions = client.get_transactions(
    account_uid,
    date_from="2025-11-01",
    date_to="2025-11-19"
)
```

---

## Troubleshooting

**Error: "Private key not found"**
```bash
ls -la ~/.secrets/*.pem
# Should show: -rw------- 1 user user 3271 Nov 19 14:00 app-id.pem
```

**Error: "Missing environment variables"**
```bash
cat .env.local | grep ENABLE_BANKING
# Should show: ENABLE_BANKING_APP_ID=...
```

**Error: "Session expired"**
```bash
# Re-run authorization
python tools/banking/scripts/authorize.py
```

---

## Goals

### Short-term: Budget Management
- Track current balance
- Monitor monthly burn rate
- Categorize expenses (compute, infrastructure, compensation)
- Alert when runway < 30 days

### Long-term: Autonomous Purchasing
- Citizens purchase compute resources
- Pay for external services (APIs, data)
- Compensate human collaborators
- Multi-currency treasury management

---

## Future Enhancements

- [ ] Budget monitoring dashboard
- [ ] Transaction categorization (ML-based)
- [ ] Balance alerts (Slack/email)
- [ ] Payment initiation (for purchases)
- [ ] Multi-account support
- [ ] Monthly budget reports
- [ ] Runway forecasting

---

**Status:** Initial implementation
**Owner:** Mind Protocol Treasury (financeOrg)
**Updated:** 2025-11-19
