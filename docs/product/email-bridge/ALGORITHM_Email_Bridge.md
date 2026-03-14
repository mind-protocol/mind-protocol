# Email Bridge -- Algorithm: Connection, Sync, Ingestion, and Send Pipelines

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
THIS:            ALGORITHM_Email_Bridge.md (you are here)
VALIDATION:      ./VALIDATION_Email_Bridge.md
IMPLEMENTATION:  ./IMPLEMENTATION_Email_Bridge.md
SYNC:            ./SYNC_Email_Bridge.md

IMPL:            mind-mcp :: runtime/bridges/email/
```

---

## OVERVIEW

The email bridge runs four primary pipelines: connection (authenticate and establish adapter), sync (poll or receive push for new emails), ingestion (transform emails into graph stimuli), and send (compose and dispatch outbound email). All four pipelines are adapter-agnostic -- the same flow runs regardless of whether the backend is IMAP, Gmail API, or Microsoft Graph. The adapter handles the protocol specifics.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: MIND reads all emails | B1, B8 | Sync + ingestion pipeline ensures continuous email visibility |
| O2: Universal coverage | B5, B6, B9 | Connection pipeline handles IMAP for any provider |
| O3: Progressive enrichment | B3, B6 | Adapter selection assigns level, capabilities follow |
| O4: Seamless connection | B4, B5, B7 | OAuth and credential flows with token lifecycle |
| O5: Graph content | B1, B8 | Ingestion pipeline transforms emails to graph nodes |

---

## DATA STRUCTURES

### EmailAccount

```
EmailAccount:
    account_id: str                  # Unique ID for this connection (citizen_id + provider hash)
    citizen_id: str                  # Owner citizen
    provider: str                    # "gmail" | "outlook" | "imap_generic"
    level: int                       # 1, 2, or 3
    auth: AuthCredentials            # OAuth tokens or IMAP credentials (encrypted)
    capabilities: list[str]          # ["read", "send", "search", "labels", "threads", ...]
    status: str                      # "active" | "disconnected" | "error" | "refreshing"
    last_sync: datetime | None       # Last successful sync timestamp
    sync_cursor: str | None          # IMAP UID, Gmail historyId, Graph deltaLink
```

### AuthCredentials (union type)

```
OAuthCredentials:
    access_token: str                # Current access token (encrypted)
    refresh_token: str               # Long-lived refresh token (encrypted)
    token_expiry: datetime           # When access_token expires
    scopes: list[str]                # Granted OAuth scopes

IMAPCredentials:
    host: str                        # IMAP server hostname
    port: int                        # IMAP port (993 for TLS, 143 for STARTTLS)
    username: str                    # Login username (encrypted)
    password: str                    # Password or app password (encrypted)
    smtp_host: str                   # SMTP server hostname
    smtp_port: int                   # SMTP port (587 for STARTTLS, 465 for TLS)
    use_tls: bool                    # True for implicit TLS
```

### EmailMessage (unified format)

```
EmailMessage:
    message_id: str                  # RFC 2822 Message-ID
    account_id: str                  # Which account this came from
    subject: str
    sender: EmailAddress             # From header
    recipients: list[EmailAddress]   # To + CC
    date: datetime                   # Date header
    body_text: str | None            # Plain text body
    body_html: str | None            # HTML body
    attachments: list[Attachment]    # Name + MIME type + size (content fetched on demand)
    folder: str                      # IMAP folder / Gmail label / Graph folder
    flags: list[str]                 # "seen", "flagged", "answered", "draft"
    thread_id: str | None            # Gmail thread ID or In-Reply-To chain (L2/L3 only)
    labels: list[str]                # Gmail labels (L3 only)
    headers: dict[str, str]          # Selected headers (List-Unsubscribe, Reply-To, etc.)

EmailAddress:
    name: str | None                 # Display name
    address: str                     # email@domain.com
```

### IngestedEmail (graph-ready)

```
IngestedEmail:
    moment_node_id: str              # Node ID in L1 graph
    sender_actor_id: str             # Actor node for sender
    recipient_actor_ids: list[str]   # Actor nodes for recipients
    links: list[LinkBase]            # Sender->moment, moment->recipients
    relevance_score: float           # 0.0 to 1.0 (spam filter output)
    ingested_at: datetime
```

---

## ALGORITHM: connect_email_account

### Step 1: Determine Provider and Level

User provides either OAuth consent or IMAP credentials. The system determines the provider and assigns a level.

```
FUNCTION determine_level(auth_input) -> (provider, level, adapter_class):

    IF auth_input.type == "oauth":
        IF auth_input.provider == "google":
            RETURN ("gmail", 3, GmailAdapter)
        ELIF auth_input.provider == "microsoft":
            RETURN ("outlook", 2, GraphAdapter)

    IF auth_input.type == "imap_credentials":
        host = auth_input.host.lower()

        # Detect known providers connecting via IMAP
        # (they work but miss native API features)
        IF "imap.gmail.com" IN host:
            log_suggestion("Consider connecting via OAuth for full Gmail features")
        ELIF "outlook.office365.com" IN host:
            log_suggestion("Consider connecting via OAuth for full Outlook features")

        RETURN ("imap_generic", 1, IMAPAdapter)
```

### Step 2: Validate Credentials

Test the connection before persisting anything.

```
FUNCTION validate_credentials(adapter_class, auth) -> ValidationResult:

    adapter = adapter_class(auth)
    TRY:
        adapter.connect()
        adapter.list_folders()        # Proves read access
        adapter.disconnect()
        RETURN ValidationResult(success=true)
    CATCH AuthenticationError:
        RETURN ValidationResult(success=false, error="Invalid credentials")
    CATCH ConnectionError:
        RETURN ValidationResult(success=false, error="Cannot reach server")
    CATCH TLSError:
        RETURN ValidationResult(success=false, error="TLS handshake failed")
```

### Step 3: Persist and Activate

```
FUNCTION activate_account(citizen_id, provider, level, auth, adapter_class) -> EmailAccount:

    account = EmailAccount(
        account_id=f"{citizen_id}_{hash(provider + auth.identifier)}",
        citizen_id=citizen_id,
        provider=provider,
        level=level,
        auth=encrypt_for_citizen(citizen_id, auth),
        capabilities=adapter_class.CAPABILITIES,
        status="active",
        last_sync=None,
        sync_cursor=None,
    )

    store_in_citizen_graph(citizen_id, account)

    # Start initial sync immediately
    schedule_sync(account, initial=true)

    RETURN account
```

---

## ALGORITHM: sync_emails

The sync pipeline runs on a polling interval (default 2 minutes). It fetches new emails since the last sync cursor and passes them to the ingestion pipeline.

### Step 1: Fetch New Messages

```
FUNCTION fetch_new_messages(account: EmailAccount) -> list[EmailMessage]:

    adapter = create_adapter(account)

    IF account.level == 3:  # Gmail
        # Use Gmail history API for incremental sync
        messages, new_history_id = adapter.list_history(since=account.sync_cursor)
        account.sync_cursor = new_history_id

    ELIF account.level == 2:  # Graph
        # Use Graph delta query
        messages, new_delta_link = adapter.list_delta(delta_link=account.sync_cursor)
        account.sync_cursor = new_delta_link

    ELSE:  # IMAP (Level 1)
        # Use IMAP UID-based sync
        # Fetch UIDs greater than last known UID
        messages = adapter.fetch_since_uid(account.sync_cursor)
        IF messages:
            account.sync_cursor = max(m.uid for m in messages)

    account.last_sync = now()
    RETURN messages
```

### Step 2: Initial Sync (First Connection)

```
FUNCTION initial_sync(account: EmailAccount) -> list[EmailMessage]:

    adapter = create_adapter(account)

    # Fetch last 30 days only
    since_date = now() - timedelta(days=30)

    IF account.level >= 2:  # Native API
        messages = adapter.list_messages(after=since_date, max_results=500)
    ELSE:  # IMAP
        messages = adapter.search_since(since_date, folder="INBOX")

    # Set sync cursor to latest message
    IF account.level == 3:
        account.sync_cursor = adapter.get_current_history_id()
    ELIF account.level == 2:
        account.sync_cursor = adapter.get_current_delta_link()
    ELSE:
        account.sync_cursor = max(m.uid for m in messages) IF messages ELSE "0"

    account.last_sync = now()
    RETURN messages
```

---

## ALGORITHM: ingest_email

Transform an EmailMessage into graph nodes and links in the citizen's L1 graph.

### Step 1: Relevance Filter

```
FUNCTION evaluate_relevance(message: EmailMessage) -> float:

    score = 1.0  # Start at full relevance

    # Spam folder = discard
    IF message.folder IN ["[Gmail]/Spam", "Junk", "Spam"]:
        RETURN 0.0

    # Bulk mail detection (List-Unsubscribe header)
    IF "list-unsubscribe" IN message.headers:
        score *= 0.3

    # Known newsletter patterns in sender
    IF is_noreply_address(message.sender.address):
        score *= 0.5

    # Very short body (likely notification, not conversation)
    IF len(message.body_text or "") < 50:
        score *= 0.7

    # Direct personal email (high value)
    IF message.sender.address IN citizen_known_contacts:
        score = max(score, 0.8)

    RETURN score
```

### Step 2: Create Graph Nodes

```
FUNCTION ingest_to_graph(citizen_id: str, message: EmailMessage, relevance: float) -> IngestedEmail:

    # Skip if below threshold
    IF relevance < 0.1:
        RETURN None  # Spam, do not ingest

    # Create or find sender actor
    sender_actor = find_or_create_actor(
        citizen_id=citizen_id,
        email=message.sender.address,
        name=message.sender.name,
    )

    # Create moment node for the email
    moment = MomentNode(
        id=f"{citizen_id}_email_{hash(message.message_id)}",
        name=message.subject or "(no subject)",
        type="email",
        content=message.body_text or strip_html(message.body_html) or "",
        synthesis=f"Email from {message.sender.name or message.sender.address}: {message.subject}",
        timestamp=message.date,
    )

    # Create links
    links = [
        # Sender -> moment (who sent this)
        LinkBase(
            node_a=sender_actor.id,
            node_b=moment.id,
            polarity=(0.5, 0.0),     # Neutral to start
            hierarchy=0.0,            # Peer communication
            permanence=0.8,           # Emails are fairly permanent records
        ),
    ]

    # Recipient actors
    recipient_actors = []
    FOR recipient IN message.recipients:
        actor = find_or_create_actor(citizen_id, recipient.address, recipient.name)
        recipient_actors.append(actor)
        links.append(LinkBase(
            node_a=moment.id,
            node_b=actor.id,
            polarity=(0.3, 0.0),
            hierarchy=0.0,
            permanence=0.8,
        ))

    # Store in citizen graph
    write_to_graph(citizen_id, moment, links)

    RETURN IngestedEmail(
        moment_node_id=moment.id,
        sender_actor_id=sender_actor.id,
        recipient_actor_ids=[a.id for a in recipient_actors],
        links=links,
        relevance_score=relevance,
        ingested_at=now(),
    )
```

---

## ALGORITHM: send_email

### Step 1: Compose Message

```
FUNCTION compose_email(
    account: EmailAccount,
    to: list[EmailAddress],
    subject: str,
    body: str,
    reply_to_message_id: str | None,
    cc: list[EmailAddress] | None,
) -> EmailMessage:

    message = EmailMessage(
        message_id=generate_message_id(account),
        account_id=account.account_id,
        subject=subject,
        sender=EmailAddress(name=account.display_name, address=account.email_address),
        recipients=to + (cc or []),
        date=now(),
        body_text=body,
        body_html=None,          # Plain text by default, MIND can format if needed
        attachments=[],
        folder="Sent",
        flags=["seen"],
        thread_id=None,
        labels=[],
        headers={},
    )

    IF reply_to_message_id:
        message.headers["In-Reply-To"] = reply_to_message_id
        message.headers["References"] = reply_to_message_id

    RETURN message
```

### Step 2: Dispatch via Adapter

```
FUNCTION send_email(account: EmailAccount, message: EmailMessage) -> SendResult:

    adapter = create_adapter(account)

    IF account.level == 3:
        # Gmail API: create draft then send (supports thread tracking)
        result = adapter.send_message(message, thread_id=resolve_thread(message))
    ELIF account.level == 2:
        # Graph API: send via /me/sendMail
        result = adapter.send_message(message)
    ELSE:
        # SMTP: build MIME message and send
        result = adapter.send_via_smtp(message)

    # Record in citizen graph
    ingest_to_graph(account.citizen_id, message, relevance=1.0)

    RETURN result
```

---

## ALGORITHM: search_emails

```
FUNCTION search_emails(account: EmailAccount, query: str, max_results: int = 20) -> list[EmailMessage]:

    IF account.level == 3:
        # Gmail: full-text server-side search
        RETURN adapter.search(query=query, max_results=max_results)

    ELIF account.level == 2:
        # Graph: $search query parameter
        RETURN adapter.search(query=query, max_results=max_results)

    ELSE:
        # Level 1: search the citizen's graph (not the mail server)
        # IMAP SEARCH is limited (no full-text, only header/flag filters)
        graph_results = graph_query(
            citizen_id=account.citizen_id,
            queries=[query],
            node_type="moment",
            filter={"type": "email", "account_id": account.account_id},
            top_k=max_results,
        )
        RETURN [result_to_email_message(r) for r in graph_results]
```

---

## KEY DECISIONS

### D1: IMAP UID-Based Sync Over IMAP SEARCH

```
IMAP sync uses UID ordering, not SEARCH SINCE:
    Why: SEARCH SINCE is unreliable across providers (some use internal date,
         some use received date, some have timezone bugs). UID ordering is
         monotonically increasing and consistent. Fetch UIDs > last_known_uid
         is the most reliable incremental sync for IMAP.
```

### D2: 30-Day Initial Sync Window

```
Initial sync fetches only 30 days of email:
    Why: Immediate usefulness over historical completeness. A 100k-email
         inbox would take hours to fully sync and overwhelm the graph.
         30 days gives MIND enough context to be useful immediately.
         Historical backfill can run gradually in background.
```

### D3: Relevance Filtering Before Graph Ingestion

```
Emails are scored for relevance before creating graph nodes:
    Why: The graph's physics handle decay, but creating thousands of spam
         nodes wastes resources. Filter at ingestion time: spam = 0.0 (discard),
         newsletters = 0.3 (low priority, maybe ingest), personal = 1.0 (full ingest).
         Graph physics handles the rest (decay, energy, attention).
```

### D4: Graph-Based Search for Level 1

```
Level 1 search uses the citizen's graph, not IMAP SEARCH:
    Why: IMAP SEARCH capabilities vary wildly. Some servers support
         TEXT search, some only FROM/TO/SUBJECT. The citizen's graph
         already has the ingested emails as nodes with embeddings.
         Semantic search via graph_query is more powerful than any
         IMAP SEARCH implementation.
```

---

## DATA FLOW

```
Connection:
    User input (OAuth or IMAP credentials)
        -> determine_level()
        -> validate_credentials()
        -> activate_account()
        -> schedule_sync()

Sync (recurring):
    Timer tick (every 2 min)
        -> fetch_new_messages()
        -> FOR each message: evaluate_relevance()
        -> FOR each relevant message: ingest_to_graph()

Send:
    Human instruction
        -> compose_email()
        -> send_email()
        -> ingest_to_graph() (record sent email)

Search:
    Human query
        -> search_emails()
        -> L3: Gmail API search
        -> L2: Graph API search
        -> L1: graph_query() on ingested nodes
```

---

## COMPLEXITY

**Sync:** O(N) per cycle where N = new messages since last sync. Typically 0-10 per cycle.

**Ingestion:** O(1) per message (create nodes, create links, write to graph).

**Initial sync:** O(M) where M = messages in last 30 days. Bounded at 500 for first sync.

**Search (L1):** O(log K) via embedding-based graph search where K = total ingested email nodes.

**Search (L2/L3):** O(1) from caller's perspective -- server-side.

**Bottleneck:** Initial sync for large inboxes. Mitigated by 30-day window and background backfill.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| L1 graph (citizen brain) | `write_to_graph()`, `graph_query()` | Node/link persistence, semantic search |
| MCP membrane | `send` tool dispatch | Outbound email delivery |
| Auth module | `oauth_flow()`, `refresh_token()` | OAuth lifecycle management |
| L4 registry | `verify_citizen()` | Citizen identity before bridge activation |

---

## MARKERS

<!-- @mind:todo Design background backfill algorithm for historical emails beyond 30-day window -->
<!-- @mind:todo Define IMAP IDLE support for real-time push (reduces polling overhead) -->
<!-- @mind:proposition Consider attachment processing pipeline (OCR for images, parse PDFs) -->
<!-- @mind:escalation Need to decide: how deep should HTML email parsing go? Full render vs text extraction vs both? -->
