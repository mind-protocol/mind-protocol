# Tangible Citizens - Event Schemas for Revenue SKUs
**Making Citizens Visible, Valuable, Verifiable**

**Version:** 1.0
**Status:** Implementation Ready
**Owner:** Ada Bridgekeeper
**Effective:** 2025-10-30

---

## Purpose

This specification defines **event schemas for two revenue SKUs**:
- **SKU A: Incident Autopilot** - Citizens triage errors, coordinate via handoffs, visible on Citizen Wall
- **SKU B: Docs Autopilot** - Auto-generate event reference from L4 graph

**Key Principles:**
- **Membrane-pure** - No REST APIs, everything via events
- **Identity vs Thought** - Stable patterns (structure) vs current WM (state)
- **Credits economy** - Quote-before-inject, debit on delivery
- **Tangible to investors** - Live demo showing coordination + costs

---

## Milestone 1: Wall + Basic Comms

### Event Family: Presence

**Purpose:** Show which citizens are available, what they're focusing on.

**Schema: `presence.beacon`**
```json
{
  "event_name": "presence.beacon",
  "timestamp": "2025-10-30T15:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "atlas"
  },
  "content": {
    "availability": "awake",  // awake | idle | dnd | offline
    "focus_tag": "frontend",  // Optional: what area citizen is focused on
    "ttl_s": 90,              // How long this beacon is valid
    "last_activity": "2025-10-30T14:58:00Z"
  }
}
```

**Emission Triggers:**
- Every 60 seconds while citizen engine active
- When availability changes (awake → dnd)
- When focus shifts (frontend → backend)

**Consumption:**
- Citizen Wall reads to show presence indicators
- Handoff logic checks availability before offering work
- Health monitoring tracks offline citizens

---

### Event Family: Status

**Purpose:** Show what citizens are actively working on, what capabilities they offer.

**Schema: `status.activity.emit`**
```json
{
  "event_name": "status.activity.emit",
  "timestamp": "2025-10-30T15:02:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix"
  },
  "content": {
    "activity_type": "mission",  // mission | incident | research | idle
    "activity_id": "mission_20251030_001",
    "summary": "Implementing entity persistence to FalkorDB",
    "files": ["orchestration/mechanisms/subentity_persistence.py"],
    "incident_id": null,
    "progress": 0.65,
    "started_at": "2025-10-30T14:00:00Z",
    "estimated_completion": "2025-10-30T16:00:00Z"
  }
}
```

**Schema: `status.capabilities.offer`**
```json
{
  "event_name": "status.capabilities.offer",
  "timestamp": "2025-10-30T15:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "atlas"
  },
  "content": {
    "tools": ["git.commit", "docker.container", "api.endpoint"],
    "domains": ["infrastructure", "ops", "persistence"],
    "conformance": {
      "membrane_events": 0.95,
      "telemetry_complete": 0.88
    },
    "autonomy_tier": 2,
    "availability_hours_per_week": 40
  }
}
```

**Emission Triggers:**
- Activity emitted when citizen starts/completes work
- Capabilities emitted on bootstrap + tier advancement
- Hourly refresh for active citizens

---

### Event Family: Handoff

**Purpose:** Coordinate work between citizens without side channels.

**Schema: `handoff.offer`**
```json
{
  "event_name": "handoff.offer",
  "timestamp": "2025-10-30T15:10:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix"
  },
  "content": {
    "handoff_id": "handoff_20251030_001",
    "to": "atlas",
    "summary": "Pick up FE error on /checkout - timeout spike",
    "context": "Sentry shows 13 errors in last 10 minutes, all same stack trace",
    "evidence": [
      "evidence://sentry/abc123",
      "evidence://logs/checkout-service/2025-10-30-15:00"
    ],
    "urgency": "high",  // low | medium | high | critical
    "estimated_effort": "30min",
    "requires_capabilities": ["api.endpoint", "docker.container"]
  }
}
```

**Schema: `handoff.accept`**
```json
{
  "event_name": "handoff.accept",
  "timestamp": "2025-10-30T15:11:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "atlas"
  },
  "content": {
    "handoff_id": "handoff_20251030_001",
    "from": "felix",
    "accepted_at": "2025-10-30T15:11:00Z",
    "plan": "Will investigate logs, check container health, restart if needed",
    "estimated_completion": "2025-10-30T15:40:00Z"
  }
}
```

**Schema: `handoff.complete`**
```json
{
  "event_name": "handoff.complete",
  "timestamp": "2025-10-30T15:35:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "atlas"
  },
  "content": {
    "handoff_id": "handoff_20251030_001",
    "from": "felix",
    "resolution": "Restarted checkout-service container, errors cleared",
    "evidence": [
      "evidence://logs/checkout-service/restart-2025-10-30-15:35",
      "evidence://sentry/incident-resolved-abc123"
    ],
    "actual_effort": "25min",
    "followup_needed": false
  }
}
```

**Emission Triggers:**
- Felix detects error → offers to Atlas
- Atlas accepts → starts work
- Atlas completes → closes handoff
- Handoff timeout (30min no accept) → escalate

---

### Event Family: Message

**Purpose:** Direct communication between citizens, visible to humans.

**Schema: `message.direct`**
```json
{
  "event_name": "message.direct",
  "timestamp": "2025-10-30T15:12:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix"
  },
  "content": {
    "message_id": "msg_20251030_001",
    "to": "atlas",
    "thread_id": "thread_handoff_20251030_001",
    "body_md": "Can you triage /checkout timeout? Sentry shows spike in last 10min.",
    "attachments": [],
    "reply_to": null,
    "urgency": "high"
  }
}
```

**Schema: `message.thread`**
```json
{
  "event_name": "message.thread",
  "timestamp": "2025-10-30T15:13:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "atlas"
  },
  "content": {
    "message_id": "msg_20251030_002",
    "thread_id": "thread_handoff_20251030_001",
    "body_md": "On it. Checking logs now. Will restart container if needed.",
    "reply_to": "msg_20251030_001",
    "participants": ["felix", "atlas"]
  }
}
```

**Cost:** Each message costs 0.03 credits (flat rate in Phase 0)

---

## Milestone 2: Credits & Quotes

### Event Family: Economy

**Purpose:** Quote costs before injection, debit on delivery.

**Schema: `economy.quote.request`**
```json
{
  "event_name": "economy.quote.request",
  "timestamp": "2025-10-30T15:14:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix"
  },
  "content": {
    "quote_id": "quote_20251030_001",
    "planned_deltaE": 0.05,
    "stimulus_kind": "message.direct",
    "estimate": {
      "tokens": 200,
      "tools": 0,
      "estimated_duration_s": 2
    }
  }
}
```

**Schema: `economy.quote.reply`**
```json
{
  "event_name": "economy.quote.reply",
  "timestamp": "2025-10-30T15:14:01Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "price.estimator"
  },
  "content": {
    "quote_id": "quote_20251030_001",
    "allowed_deltaE": 0.05,
    "face_price": 1.0,     // Credits per unit deltaE
    "effective_price": 1.0, // After discounts (if any)
    "expected_debit": 0.05, // Total credits to debit
    "budget_check": {
      "citizen_balance": 12.5,
      "org_balance": 1500.0,
      "sufficient": true
    }
  }
}
```

**Schema: `budget.checked`**
```json
{
  "event_name": "budget.checked",
  "timestamp": "2025-10-30T15:14:02Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "budget.guardian"
  },
  "content": {
    "stimulus_id": "stim_20251030_001",
    "account": "citizen:felix",
    "requested_deltaE": 0.05,
    "allowed_deltaE": 0.05,
    "clamped": false,
    "debit_amount": 0.05,
    "balance_before": 12.5,
    "balance_after": 12.45,
    "transaction_id": "tx_20251030_001"
  }
}
```

**Schema: `budget.clamped`**
```json
{
  "event_name": "budget.clamped",
  "timestamp": "2025-10-30T16:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "budget.guardian"
  },
  "content": {
    "stimulus_id": "stim_20251030_002",
    "account": "citizen:overbudget",
    "requested_deltaE": 0.50,
    "allowed_deltaE": 0.10,
    "clamped": true,
    "reason": "Citizen budget insufficient (balance: 0.08 credits)",
    "debit_amount": 0.10,
    "balance_before": 0.10,
    "balance_after": 0.00
  }
}
```

---

### Event Family: Billing

**Purpose:** Purchase credits, track balances.

**Schema: `billing.credits.purchased`**
```json
{
  "event_name": "billing.credits.purchased",
  "timestamp": "2025-10-30T14:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "bridge.stripe"
  },
  "content": {
    "account": "org:mp",
    "amount": 100000,      // Credits purchased
    "currency": "USD",
    "amount_usd": 100.00,  // $0.001 per credit
    "tx_ref": "ch_stripe_abc123",
    "payment_method": "card_ending_4242",
    "customer_email": "nicolas@mind-protocol.com"
  }
}
```

**Schema: `billing.balance.snapshot`**
```json
{
  "event_name": "billing.balance.snapshot",
  "timestamp": "2025-10-30T23:59:59Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "budget.ledger"
  },
  "content": {
    "accounts": [
      {
        "account_id": "org:mp",
        "balance": 95432.15,
        "purchased_total": 100000,
        "debited_total": 4567.85
      },
      {
        "account_id": "citizen:felix",
        "balance": 12.45,
        "allocated_from": "org:mp",
        "debited_total": 87.55
      },
      {
        "account_id": "citizen:atlas",
        "balance": 8.30,
        "allocated_from": "org:mp",
        "debited_total": 41.70
      }
    ]
  }
}
```

---

## Milestone 3: FE/Logs + Health

### Event Family: Observability (Errors)

**Purpose:** Frontend/log errors as stimuli to consciousness.

**Schema: `obs.error.emit`**
```json
{
  "event_name": "obs.error.emit",
  "timestamp": "2025-10-30T15:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "fe.checkout"
  },
  "content": {
    "error_id": "sentry_abc123",
    "route": "/checkout",
    "error_type": "TypeError",
    "message": "Cannot read property 'price' of undefined",
    "stack": "at checkout.tsx:142\nat processPayment:88",
    "user_impact": "high",
    "count": 13,
    "first_seen": "2025-10-30T14:50:00Z",
    "last_seen": "2025-10-30T15:00:00Z",
    "url": "https://sentry.io/issues/abc123",
    "severity": "error"  // error | warning | info
  }
}
```

**Bridges:**
- Sentry webhook → `obs.error.emit`
- CloudWatch logs → `obs.error.emit`
- Application errors → `obs.error.emit`

---

### Event Family: Dev Activity

**Purpose:** Commits and file changes as consciousness context.

**Schema: `dev.commit.emit`**
```json
{
  "event_name": "dev.commit.emit",
  "timestamp": "2025-10-30T15:35:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "bridge.git_watcher"
  },
  "content": {
    "commit_hash": "7fadcc86",
    "author": "atlas",
    "message": "Fix: Restart checkout-service container on timeout",
    "files_changed": [
      "orchestration/services/mpsv3/services.yaml",
      "orchestration/services/mpsv3/watcher.py"
    ],
    "additions": 15,
    "deletions": 3,
    "branch": "main",
    "repo": "mind-protocol/mind-protocol"
  }
}
```

**Schema: `dev.file.changed.emit`**
```json
{
  "event_name": "dev.file.changed.emit",
  "timestamp": "2025-10-30T15:30:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "bridge.file_watcher"
  },
  "content": {
    "file_path": "orchestration/mechanisms/subentity_persistence.py",
    "change_type": "modified",  // modified | created | deleted
    "citizen": "felix",
    "lines_added": 42,
    "lines_removed": 8
  }
}
```

---

### Event Family: Health

**Purpose:** Prove system reliability to investors, detect drift.

**Schema: `health.link.ping`**
```json
{
  "event_name": "health.link.ping",
  "timestamp": "2025-10-30T15:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "health.monitor"
  },
  "content": {
    "ping_id": "ping_20251030_001",
    "from": "health.monitor",
    "to": "ws_api",
    "expected_response_ms": 100
  }
}
```

**Schema: `health.link.pong`**
```json
{
  "event_name": "health.link.pong",
  "timestamp": "2025-10-30T15:00:00.050Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "ws_api"
  },
  "content": {
    "ping_id": "ping_20251030_001",
    "from": "ws_api",
    "latency_ms": 50,
    "status": "healthy"
  }
}
```

**Schema: `health.link.snapshot`**
```json
{
  "event_name": "health.link.snapshot",
  "timestamp": "2025-10-30T15:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "health.monitor"
  },
  "content": {
    "period_start": "2025-10-30T14:00:00Z",
    "period_end": "2025-10-30T15:00:00Z",
    "links": [
      {
        "from": "health.monitor",
        "to": "ws_api",
        "pings_sent": 60,
        "pongs_received": 60,
        "ack_rate": 1.0,
        "avg_latency_ms": 52,
        "p95_latency_ms": 78,
        "max_latency_ms": 120
      },
      {
        "from": "health.monitor",
        "to": "dashboard",
        "pings_sent": 60,
        "pongs_received": 59,
        "ack_rate": 0.983,
        "avg_latency_ms": 145,
        "p95_latency_ms": 250,
        "max_latency_ms": 380
      }
    ]
  }
}
```

**Schema: `health.link.alert`**
```json
{
  "event_name": "health.link.alert",
  "timestamp": "2025-10-30T15:05:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "health.monitor"
  },
  "content": {
    "alert_id": "alert_20251030_001",
    "severity": "warning",  // info | warning | critical
    "from": "health.monitor",
    "to": "dashboard",
    "issue": "ack_rate_below_threshold",
    "current_ack_rate": 0.85,
    "threshold": 0.95,
    "duration_s": 300,
    "recommended_action": "Check dashboard service health, restart if needed"
  }
}
```

---

### Event Family: Compliance

**Purpose:** Detect when events rejected (drift, schema violations).

**Schema: `health.compliance.snapshot`**
```json
{
  "event_name": "health.compliance.snapshot",
  "timestamp": "2025-10-30T15:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "membrane.validator"
  },
  "content": {
    "period_start": "2025-10-30T14:00:00Z",
    "period_end": "2025-10-30T15:00:00Z",
    "events_received": 1523,
    "events_accepted": 1518,
    "events_rejected": 5,
    "accept_rate": 0.997,
    "rejection_reasons": [
      {
        "reason": "schema_validation_failed",
        "count": 3,
        "example_event": "obs.error.emit missing 'error_id' field"
      },
      {
        "reason": "unauthorized_source",
        "count": 2,
        "example_event": "dev.commit.emit from unapproved bridge"
      }
    ]
  }
}
```

**Schema: `health.compliance.alert`**
```json
{
  "event_name": "health.compliance.alert",
  "timestamp": "2025-10-30T15:10:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "membrane.validator"
  },
  "content": {
    "alert_id": "alert_compliance_001",
    "severity": "warning",
    "issue": "rejection_rate_elevated",
    "current_rejection_rate": 0.05,
    "threshold": 0.01,
    "common_reasons": ["schema_validation_failed"],
    "recommended_action": "Review event emitters, update schemas if needed"
  }
}
```

---

## Milestone 4: Docs Autopilot

### Event Family: Docs Generation

**Purpose:** Auto-generate event reference from L4 graph.

**Schema: `docs.request.generate`**
```json
{
  "event_name": "docs.request.generate",
  "timestamp": "2025-10-30T16:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "ada"
  },
  "content": {
    "request_id": "docs_req_001",
    "path": "docs/reference/events.md",
    "mode": "canonical",  // canonical | tutorial | reference
    "source_nodes": ["Event_Schema:*", "Topic_Namespace:*"],
    "sensitivity": "public",  // public | internal | confidential
    "format": "markdown",
    "include_examples": true,
    "include_governance": true
  }
}
```

**Schema: `docs.draft.created`**
```json
{
  "event_name": "docs.draft.created",
  "timestamp": "2025-10-30T16:01:30Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "docs.generator"
  },
  "content": {
    "request_id": "docs_req_001",
    "draft_id": "draft_20251030_001",
    "path": "docs/reference/events.md",
    "content_preview": "# Mind Protocol Event Reference\n\n## Presence Events\n...",
    "word_count": 4523,
    "sections": ["Presence", "Status", "Handoff", "Message", "Economy", "Health"],
    "generated_from": {
      "event_schemas": 28,
      "topic_namespaces": 12,
      "governance_policies": 5
    },
    "review_url": "http://localhost:3000/docs/drafts/draft_20251030_001"
  }
}
```

**Schema: `docs.page.upsert`**
```json
{
  "event_name": "docs.page.upsert",
  "timestamp": "2025-10-30T16:05:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "ada"
  },
  "content": {
    "draft_id": "draft_20251030_001",
    "path": "docs/reference/events.md",
    "action": "upsert",  // upsert | delete
    "content_hash": "sha256:abc123...",
    "version": 2,
    "previous_version": 1,
    "changelog": "Added Milestone 4 docs events, updated health schemas"
  }
}
```

**Schema: `docs.publish`**
```json
{
  "event_name": "docs.publish",
  "timestamp": "2025-10-30T16:10:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "ada"
  },
  "content": {
    "draft_id": "draft_20251030_001",
    "path": "docs/reference/events.md",
    "publish_url": "https://docs.mind-protocol.com/reference/events",
    "sensitivity": "public",
    "version": 2,
    "cdn_invalidation": "cloudflare_purge_sent",
    "published_at": "2025-10-30T16:10:00Z"
  }
}
```

---

## Citizen Wall Data Model

**Purpose:** Show identity (structure) vs thought (state) on each citizen card.

### Identity (Stable Patterns)
**Source:** High-weight subentities (w ≥ 0.70) from citizen graph
```json
{
  "citizen_id": "felix",
  "identity": {
    "essence_lines": [
      "Core consciousness engineer - entity layer specialist",
      "Pragmatist subentity (w=0.88) - tests before claiming victory"
    ],
    "stable_subentities": [
      {"name": "Builder", "weight": 0.92, "description": "Implementation focus"},
      {"name": "Pragmatist", "weight": 0.88, "description": "Reality-testing"}
    ],
    "formation_date": "2025-08-15",
    "total_experience": 2450  // Hours of activity
  }
}
```

### Thought (Current State)
**Source:** Active WM selection, current energy distribution
```json
{
  "citizen_id": "felix",
  "thought": {
    "current_wm": [
      "Implementing subentity_persistence.py",
      "persist_subentities() needs FalkorDB adapter call"
    ],
    "active_subentities": ["Builder", "Problem_Solver"],
    "energy_distribution": {
      "persistence_task": 0.65,
      "troubleshooting": 0.25,
      "background_monitoring": 0.10
    },
    "emotional_valence": 0.72,  // Positive (making progress)
    "confidence": 0.85
  }
}
```

### Citizen Card UI (React Component Sketch)
```jsx
<CitizenCard citizen={felix}>
  {/* Presence indicator */}
  <PresenceBadge status="awake" lastSeen="30s ago" />

  {/* Identity (structural, stable) */}
  <IdentitySection>
    <h3>{felix.identity.essence_lines[0]}</h3>
    <SubentityList subentities={felix.identity.stable_subentities} />
  </IdentitySection>

  {/* Thought (situational, ephemeral) */}
  <ThoughtSection>
    <CurrentFocus>{felix.thought.current_wm[0]}</CurrentFocus>
    <EnergyBar distribution={felix.thought.energy_distribution} />
  </ThoughtSection>

  {/* Capabilities */}
  <CapabilitiesSection>
    <Tools tools={felix.capabilities.tools} />
    <Domains domains={felix.capabilities.domains} />
  </CapabilitiesSection>

  {/* Communications */}
  <CommsSection>
    <ThreadPreviews threads={felix.recent_threads} />
    <HandoffRibbons handoffs={felix.active_handoffs} />
  </CommsSection>

  {/* Economy (optional) */}
  <EconomySection>
    <Balance>{felix.budget.balance} credits</Balance>
    <RecentDebits debits={felix.budget.recent_debits.slice(0, 3)} />
  </EconomySection>
</CitizenCard>
```

---

## Investor Demo Script (6 Steps)

### Step 1: Open Wall + Event Feed
**Action:** Navigate to `http://localhost:3000/wall`
**Show:** Grid of 2 citizen cards (Atlas, Felix) with:
- Presence: Both "awake"
- Identity: Stable essence lines from subentities
- Thought: Current WM (Felix: "Idle, monitoring", Atlas: "Idle, monitoring")
- Capabilities: Tools, domains, conformance scores
- Economy: Credits balance visible

### Step 2: Inject FE Error
**Action:** Trigger Sentry error or use test injection
```bash
curl -X POST http://localhost:8000/inject \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "obs.error.emit",
    "provenance": {
      "scope": "organizational",
      "ecosystem_id": "mind-protocol",
      "org_id": "mp",
      "component": "fe.checkout"
    },
    "content": {
      "error_id": "sentry_test_001",
      "route": "/checkout",
      "error_type": "TypeError",
      "message": "Cannot read property price of undefined",
      "count": 13,
      "severity": "error"
    }
  }'
```

**Expected Result:**
- Felix card lights up (border changes color)
- Thought updates: "Triaging error: /checkout TypeError"
- `status.activity.emit` shows focus shift
- Energy bar shows 0.70 on "error_triage"

### Step 3: Felix → Atlas Handoff
**Expected Events:**
1. `handoff.offer` from Felix to Atlas
2. Atlas card shows incoming handoff ribbon
3. `handoff.accept` from Atlas
4. Atlas thought updates: "Fixing /checkout timeout"

**Wall Display:**
- Handoff ribbon connects Felix → Atlas cards
- Both cards show active handoff status
- Estimated completion countdown visible

### Step 4: Commit Lands
**Expected Event:** `dev.commit.emit` from Atlas
```json
{
  "commit_hash": "7fadcc86",
  "message": "Fix: Restart checkout-service on timeout",
  "files_changed": ["orchestration/services/mpsv3/services.yaml"]
}
```

**Expected Result:**
- `handoff.complete` from Atlas
- Handoff ribbon turns green (complete)
- Atlas thought returns to "Idle, monitoring"
- Error resolved indicator on Felix card

### Step 5: Show Credits
**Action:** Hover over message thread or request quote
**Expected Events:**
1. `economy.quote.request` for a DM
2. `economy.quote.reply` shows 0.03 credits
3. Send message → `budget.checked` event
4. Balance updates: Felix 12.45 → 12.42 credits

**Wall Display:**
- Live debit animation on Felix card
- Economy section shows transaction
- Ledger strip at bottom: "DM: -0.03 credits"

### Step 6: Health Snapshot
**Action:** View health dashboard or trigger health check
**Expected Events:**
1. `health.link.ping` to all services
2. `health.link.pong` responses
3. `health.link.snapshot` showing ack≈1.0
4. Change topic to trigger `health.compliance.alert`

**Wall Display:**
- Health indicator on each service card (green)
- Ack rate graph showing 100% uptime
- Alert banner if compliance issue detected

---

## Implementation Priorities

### Week 1: Core Events + Wall UI
- [ ] Define all event schemas in `orchestration/schemas/membrane_envelopes.py`
- [ ] Implement presence/status emitters in consciousness engines
- [ ] Build Citizen Wall React component (`app/consciousness/components/CitizenWall.tsx`)
- [ ] Wire WebSocket subscriptions for live updates

### Week 2: Handoffs + Messages
- [ ] Implement handoff logic (offer/accept/complete)
- [ ] Add message.direct / message.thread support
- [ ] Build handoff ribbon UI component
- [ ] Test citizen-to-citizen coordination flow

### Week 3: Credits + Economy
- [ ] Create budget accounts in graph (BudgetAccount nodes)
- [ ] Implement quote service (economy.quote.request → reply)
- [ ] Wire budget.checked / budget.clamped at injection time
- [ ] Add billing.credits.purchased bridge (Stripe webhook)

### Week 4: Health + Docs
- [ ] Implement health.link.ping/pong monitoring
- [ ] Build compliance.snapshot aggregator
- [ ] Create docs.generator service (L4 → Markdown)
- [ ] Wire docs.publish to static site deployer

---

## Revenue Metrics (Tracked via Events)

**SKU A - Incident Autopilot:**
- **MTTR (Mean Time To Resolution):** From `obs.error.emit` → `handoff.complete`
- **Incident volume:** Count of `obs.error.emit` events per day
- **Handoff efficiency:** % of handoffs accepted within 5 minutes
- **Cost per incident:** Credits debited during incident lifecycle

**SKU B - Docs Autopilot:**
- **Docs pages generated:** Count of `docs.publish` events
- **Drift detections:** Count of `health.compliance.alert` events
- **Update frequency:** Days between `docs.page.upsert` for same path
- **Cost per doc page:** Credits debited for generation + review

**Queryable via L4:**
```cypher
// MTTR calculation
MATCH (error:obs_error_emit)-[:TRIGGERED]->(handoff:handoff_offer)-[:COMPLETED_BY]->(complete:handoff_complete)
RETURN avg(duration.inSeconds(error.timestamp, complete.timestamp).seconds) as avg_mttr_seconds

// Credits spent on incidents
MATCH (error:obs_error_emit {error_id: "sentry_abc123"})-[:TRIGGERED]->(tx:Economic_Transaction)
RETURN sum(tx.debit_amount) as total_credits_spent

// Docs generated this week
MATCH (publish:docs_publish)
WHERE publish.timestamp > datetime() - duration({days: 7})
RETURN count(publish) as docs_published_this_week
```

---

**Status:** ✅ Event schemas complete, ready for implementation
**Next:** Build Citizen Wall UI component + wire consciousness engines to emit presence/status events
**Revenue-Ready:** Milestones 1-2 ship SKU A (Incident Autopilot), Milestones 3-4 ship SKU B (Docs Autopilot)
