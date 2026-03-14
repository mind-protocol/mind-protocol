# Email Bridge -- Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Email_Bridge.md
BEHAVIORS:       ./BEHAVIORS_Email_Bridge.md
PATTERNS:        ./PATTERNS_Email_Bridge.md
ALGORITHM:       ./ALGORITHM_Email_Bridge.md
VALIDATION:      ./VALIDATION_Email_Bridge.md
THIS:            IMPLEMENTATION_Email_Bridge.md (you are here)
SYNC:            ./SYNC_Email_Bridge.md

IMPL:            mind-mcp :: runtime/bridges/email/
```

---

## CODE STRUCTURE

```
mind-mcp/runtime/bridges/email/
├── __init__.py                                          # Exports: EmailBridge, connect_email, adapters
├── email_bridge_connection_and_account_manager.py       # Connection flow, account lifecycle, level detection
├── email_bridge_sync_and_polling_scheduler.py           # Polling loop, sync cursor management, initial sync
├── email_bridge_ingestion_to_citizen_graph.py           # Email -> graph nodes, relevance filter, dedup
├── email_bridge_send_and_compose.py                     # Compose, send, draft management
├── email_bridge_search_across_levels.py                 # Unified search interface, level-appropriate dispatch
├── adapters/
│   ├── __init__.py                                      # Exports: BaseAdapter, GmailAdapter, GraphAdapter, IMAPAdapter
│   ├── base_email_adapter.py                            # Abstract base class, capability declarations
│   ├── imap_smtp_universal_adapter.py                   # Level 1: IMAP read + SMTP send
│   ├── gmail_api_adapter.py                             # Level 3: Google Gmail API
│   └── microsoft_graph_api_adapter.py                   # Level 2: Microsoft Graph API
└── models/
    ├── __init__.py                                      # Exports: EmailMessage, EmailAccount, etc.
    ├── email_message_unified_format.py                  # EmailMessage, EmailAddress, Attachment
    └── email_account_and_credentials.py                 # EmailAccount, AuthCredentials, OAuthCredentials, IMAPCredentials
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Est. Lines | Status |
|------|---------|----------------------|------------|--------|
| `email_bridge_connection_and_account_manager.py` | Account lifecycle | `connect_email()`, `determine_level()`, `validate_credentials()`, `activate_account()`, `disconnect_account()` | ~250 | PLANNED |
| `email_bridge_sync_and_polling_scheduler.py` | Sync loop | `sync_account()`, `initial_sync()`, `fetch_new_messages()`, `schedule_polling()` | ~200 | PLANNED |
| `email_bridge_ingestion_to_citizen_graph.py` | Graph ingestion | `ingest_email()`, `evaluate_relevance()`, `find_or_create_actor()` | ~250 | PLANNED |
| `email_bridge_send_and_compose.py` | Outbound email | `compose_email()`, `send_email()`, `create_draft()` | ~150 | PLANNED |
| `email_bridge_search_across_levels.py` | Search dispatch | `search_emails()`, `result_to_email_message()` | ~100 | PLANNED |
| `base_email_adapter.py` | Adapter interface | `BaseAdapter` (ABC) | ~80 | PLANNED |
| `imap_smtp_universal_adapter.py` | IMAP/SMTP impl | `IMAPAdapter`, IMAP connection, SMTP send | ~350 | PLANNED |
| `gmail_api_adapter.py` | Gmail API impl | `GmailAdapter`, history sync, label management | ~300 | PLANNED |
| `microsoft_graph_api_adapter.py` | Graph API impl | `GraphAdapter`, delta sync, calendar hooks | ~250 | PLANNED |
| `email_message_unified_format.py` | Data models | `EmailMessage`, `EmailAddress`, `Attachment` | ~80 | PLANNED |
| `email_account_and_credentials.py` | Account models | `EmailAccount`, `OAuthCredentials`, `IMAPCredentials` | ~80 | PLANNED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Adapter (Strategy)

**Why this pattern:** Multiple email protocols (IMAP, Gmail API, Graph API) must present a uniform interface. The adapter pattern isolates protocol-specific logic. Adding a new provider means adding one adapter class -- no changes to the bridge core.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Adapter/Strategy | `adapters/*.py` | Protocol isolation -- each provider is a separate class with same interface |
| Factory | `email_bridge_connection_and_account_manager.py` | `determine_level()` returns the correct adapter class |
| Observer | `email_bridge_sync_and_polling_scheduler.py` | Polling scheduler notifies ingestion pipeline on new messages |
| Template Method | `base_email_adapter.py` | Abstract methods define what every adapter must implement |

### Anti-Patterns to Avoid

- **Provider switch statements**: No `if provider == "gmail"` in bridge core. All provider logic lives in adapters.
- **Shared mutable state between accounts**: Each account has its own adapter instance, its own sync cursor, its own polling schedule. No shared state.
- **Credential passing through call chains**: Credentials are decrypted at adapter construction time. No credential objects flowing through function parameters beyond that point.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Adapter boundary | Protocol-specific logic (IMAP commands, API calls, auth headers) | Bridge core (sync, ingestion, search) | `BaseAdapter` abstract methods |
| Ingestion boundary | Email-to-graph transformation, relevance filtering | Graph storage, node physics | `write_to_graph()`, `graph_query()` calls |
| Auth boundary | Token storage, refresh logic, encryption | Provider OAuth servers | `oauth_flow()`, `refresh_token()` |

---

## SCHEMA

### EmailMessage (Pydantic model)

```yaml
EmailMessage:
  required:
    - message_id: str              # RFC 2822 Message-ID
    - account_id: str              # Owning account
    - subject: str                 # May be empty string
    - sender: EmailAddress         # From header
    - recipients: list[EmailAddress]
    - date: datetime               # UTC
    - folder: str                  # Current folder/label
    - flags: list[str]             # IMAP flags
  optional:
    - body_text: str | None        # Plain text
    - body_html: str | None        # HTML
    - attachments: list[Attachment]
    - thread_id: str | None        # L2/L3 only
    - labels: list[str]            # L3 only
    - headers: dict[str, str]      # Selected headers
  constraints:
    - message_id must be unique per account
    - sender must have valid email address
    - date must be UTC timezone-aware
```

### EmailAccount (Pydantic model)

```yaml
EmailAccount:
  required:
    - account_id: str              # citizen_id + provider hash
    - citizen_id: str              # Owner
    - provider: str                # "gmail" | "outlook" | "imap_generic"
    - level: int                   # 1, 2, or 3
    - auth: AuthCredentials        # Encrypted
    - capabilities: list[str]      # Available operations
    - status: str                  # "active" | "disconnected" | "error" | "refreshing"
  optional:
    - last_sync: datetime | None
    - sync_cursor: str | None      # Provider-specific position marker
  constraints:
    - level must be 1, 2, or 3
    - status must be one of the defined values
    - auth must be encrypted at rest
```

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `connect_email(citizen_id, auth_input)` | `email_bridge_connection_and_account_manager.py` | MCP tool, user action |
| `sync_account(account)` | `email_bridge_sync_and_polling_scheduler.py` | Polling scheduler (every 2 min) |
| `send_email(account, message)` | `email_bridge_send_and_compose.py` | MCP `send` tool |
| `search_emails(account, query)` | `email_bridge_search_across_levels.py` | MCP `graph_query` or direct call |
| `disconnect_account(account_id)` | `email_bridge_connection_and_account_manager.py` | User action |

---

## DATA FLOW AND DOCKING

### Flow 1: Email Sync and Ingestion

This is the primary flow. Runs every 2 minutes per account. Transforms provider-specific email data into citizen graph nodes.

```yaml
flow:
  name: email_sync_and_ingestion
  purpose: Continuously ingest new emails into citizen graph
  scope: From polling trigger through graph node creation
  steps:
    - id: poll_trigger
      description: Scheduler fires sync for each active account
      file: email_bridge_sync_and_polling_scheduler.py
      function: sync_account()
      input: EmailAccount
      output: list[EmailMessage]
      trigger: Timer (2 min interval)
      side_effects: Updates sync_cursor, last_sync
    - id: fetch
      description: Adapter fetches new messages from provider
      file: adapters/{adapter}.py
      function: fetch_since_uid() / list_history() / list_delta()
      input: sync_cursor
      output: list[EmailMessage]
      trigger: Called by sync_account()
      side_effects: Network IO to mail server
    - id: filter
      description: Evaluate relevance of each message
      file: email_bridge_ingestion_to_citizen_graph.py
      function: evaluate_relevance()
      input: EmailMessage
      output: float (0.0 to 1.0)
      trigger: Called per message
      side_effects: None
    - id: ingest
      description: Create graph nodes for relevant messages
      file: email_bridge_ingestion_to_citizen_graph.py
      function: ingest_email()
      input: EmailMessage + relevance score
      output: IngestedEmail
      trigger: Called per relevant message
      side_effects: Creates moment node + actor nodes + links in L1 graph
```

### Flow 2: Outbound Email Send

Transforms MIND's intent to send into a dispatched email via the appropriate protocol.

```yaml
flow:
  name: outbound_email_send
  purpose: Send emails on behalf of the human via the appropriate protocol
  scope: From human instruction through email dispatch and graph recording
  steps:
    - id: compose
      description: Build EmailMessage from MIND's draft
      file: email_bridge_send_and_compose.py
      function: compose_email()
      input: recipients, subject, body, reply context
      output: EmailMessage
      trigger: MCP send tool
      side_effects: None
    - id: dispatch
      description: Send via adapter (SMTP or native API)
      file: email_bridge_send_and_compose.py
      function: send_email()
      input: EmailMessage
      output: SendResult
      trigger: After compose
      side_effects: Email dispatched to recipients
    - id: record
      description: Record sent email in citizen graph
      file: email_bridge_ingestion_to_citizen_graph.py
      function: ingest_email()
      input: EmailMessage (sent)
      output: IngestedEmail
      trigger: After successful dispatch
      side_effects: Creates moment node for sent email
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
email_bridge_connection_and_account_manager
    imports -> models/email_account_and_credentials
    imports -> adapters/ (factory for adapter selection)

email_bridge_sync_and_polling_scheduler
    imports -> email_bridge_connection_and_account_manager (adapter creation)
    imports -> email_bridge_ingestion_to_citizen_graph (ingest pipeline)
    imports -> models/email_message_unified_format

email_bridge_ingestion_to_citizen_graph
    imports -> models/email_message_unified_format
    calls   -> L1 graph (write_to_graph, find_or_create_actor)

email_bridge_send_and_compose
    imports -> models/email_message_unified_format
    imports -> email_bridge_connection_and_account_manager (adapter creation)

email_bridge_search_across_levels
    imports -> email_bridge_connection_and_account_manager (adapter creation)
    calls   -> L1 graph (graph_query for L1 search)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `imaplib` (stdlib) | IMAP connection and commands | `imap_smtp_universal_adapter.py` |
| `smtplib` (stdlib) | SMTP email sending | `imap_smtp_universal_adapter.py` |
| `email` (stdlib) | MIME message parsing and construction | `imap_smtp_universal_adapter.py` |
| `google-api-python-client` | Gmail API calls | `gmail_api_adapter.py` |
| `google-auth-oauthlib` | Google OAuth 2.0 flow | `gmail_api_adapter.py` |
| `msal` | Microsoft OAuth 2.0 + Graph API auth | `microsoft_graph_api_adapter.py` |
| `httpx` | HTTP client for Graph API calls | `microsoft_graph_api_adapter.py` |
| `pydantic` | Data model validation | `models/*.py` |
| `cryptography` | Credential encryption/decryption | `email_bridge_connection_and_account_manager.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| EmailAccount (incl. encrypted credentials) | Citizen's L1 graph | Per-citizen, per-account | Created on connect, deleted on disconnect |
| sync_cursor | EmailAccount.sync_cursor in L1 graph | Per-account | Updated after each successful sync |
| Adapter instance | In-memory | Per-account, per-process | Created when polling starts, destroyed on disconnect |
| OAuth tokens | Encrypted in L1 graph, decrypted in memory | Per-account | Refreshed at 75% of expiry lifetime |

### State Transitions

```
disconnected --[connect_email()]--> validating --[success]--> active
                                                --[failure]--> error

active --[sync success]--> active (cursor advanced)
active --[sync failure]--> error
active --[token expired]--> refreshing --[refresh success]--> active
                                        --[refresh failure]--> disconnected

active --[disconnect_account()]--> disconnected
error  --[reconnect()]--> validating
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Load all EmailAccounts for this citizen from L1 graph
2. For each active account:
   a. Decrypt credentials
   b. Create adapter instance
   c. Validate connection (quick connect test)
   d. Start polling scheduler (2 min interval)
3. Bridge ready -- accepting sync, send, and search requests
```

### Main Loop (Polling)

```
1. Timer fires (every 2 min per account)
2. fetch_new_messages(account)
3. For each message:
   a. evaluate_relevance() -> score
   b. If score >= 0.1: ingest_to_graph()
4. Update sync_cursor and last_sync
5. If errors: update account status, notify MIND
```

### Shutdown

```
1. Stop all polling schedulers
2. Close all adapter connections (IMAP LOGOUT, release API clients)
3. Persist final sync cursors to L1 graph
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Polling scheduler | async (asyncio) | One task per account, non-blocking |
| IMAP connection | sync (imaplib is blocking) | Runs in thread executor within async loop |
| Gmail/Graph API calls | async (httpx) | Native async HTTP |
| Graph writes | async | Via existing graph ops async interface |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `POLL_INTERVAL_SECONDS` | runtime config | `120` | Seconds between sync polls |
| `INITIAL_SYNC_DAYS` | runtime config | `30` | Days of history to fetch on first connect |
| `INITIAL_SYNC_MAX_MESSAGES` | runtime config | `500` | Max messages to fetch on first connect |
| `RELEVANCE_THRESHOLD` | runtime config | `0.1` | Minimum relevance score for ingestion |
| `TOKEN_REFRESH_THRESHOLD` | runtime config | `0.75` | Refresh OAuth token at this fraction of lifetime |
| `IMAP_DEFAULT_PORT` | runtime config | `993` | Default IMAP TLS port |
| `SMTP_DEFAULT_PORT` | runtime config | `587` | Default SMTP STARTTLS port |

---

## MARKERS

<!-- @mind:todo Create base_email_adapter.py with abstract interface definition -->
<!-- @mind:todo Implement imap_smtp_universal_adapter.py first (Week 1) -->
<!-- @mind:todo Implement microsoft_graph_api_adapter.py second (Week 2, days 1-4) -->
<!-- @mind:proposition Gmail adapter may already be partially built from auth flow -- verify in mind-mcp -->
