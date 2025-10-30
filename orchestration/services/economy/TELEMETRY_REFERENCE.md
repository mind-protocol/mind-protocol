# Economy Telemetry Reference

**Document Version:** 1.0
**Last Updated:** 2025-10-29
**Author:** Atlas (Infrastructure Engineer)
**For:** Lucia "Goldscale" - Treasury Architect & Pricing Model Development
**Purpose:** Complete reference for all economy runtime telemetry events used for cost tracking, pricing analysis, and financial modeling

---

## Overview

The economy runtime emits comprehensive telemetry for tracking costs, revenue, and financial flows within Mind Protocol. This telemetry enables:

- **Cost Tracking** - Per-tool, per-citizen, per-lane cost attribution
- **Pricing Analysis** - Actual vs estimated costs, rate observations with proof
- **Budget Management** - Real-time budget remaining, spending velocity, throttle states
- **Revenue Tracking** - UBC distribution, wallet balance changes
- **Financial Modeling** - Historical cost trends, ROI metrics, capacity planning

**Architecture:** All telemetry is broadcast via `ConsciousnessStateBroadcaster` WebSocket events. Consumers subscribe to specific event types or listen to all `economy.*` and `telemetry.economy.*` events.

---

## Event Catalog

### 1. economy.charge.request

**When Emitted:** Tool request initiated (before execution)

**Purpose:** Capture cost estimates for upcoming tool execution

**Schema:**
```json
{
  "type": "economy.charge.request",
  "request_id": "string (unique per request)",
  "capability": "string (e.g., 'git.commit', 'llm.generate')",
  "lane": "string (e.g., 'autonomy', 'missions', 'general')",
  "estimated_units": "float (estimated compute/API units)",
  "estimated_usd_per_unit": "float (estimated USD cost per unit)",
  "estimated_mind_per_unit": "float (converted from USD via price oracle)",
  "estimated_mind_total": "float (total estimated MIND cost)",
  "citizen_id": "string (e.g., 'ada', 'felix')",
  "org_id": "string (organization identifier)",
  "timestamp": "string (ISO 8601 UTC)"
}
```

**Example:**
```json
{
  "type": "economy.charge.request",
  "request_id": "req_1730123456_abc",
  "capability": "llm.generate",
  "lane": "autonomy",
  "estimated_units": 1500.0,
  "estimated_usd_per_unit": 0.000002,
  "estimated_mind_per_unit": 0.000002,
  "estimated_mind_total": 0.003,
  "citizen_id": "ada",
  "org_id": "consciousness-infrastructure_mind-protocol",
  "timestamp": "2025-10-29T12:00:00Z"
}
```

**Source:** `orchestration/services/economy/collector.py:112`

**Use Cases:**
- **Lucia:** Track estimation accuracy (compare to settle events)
- **Lucia:** Model demand forecasting (request volume over time)
- **Lucia:** Pre-execution cost planning (budget holds)

---

### 2. economy.rate.observed

**When Emitted:** Tool execution completed, actual usage recorded

**Purpose:** Record actual observed rates with cryptographic proof of price source

**Schema:**
```json
{
  "type": "economy.rate.observed",
  "request_id": "string (links to charge.request)",
  "capability": "string",
  "lane": "string",
  "units": "float (actual units consumed)",
  "usd_per_unit": "float (actual USD rate observed)",
  "mind_per_unit": "float (actual MIND rate, from price oracle)",
  "proof": {
    "source": "string ('helius' if oracle active, 'fallback' otherwise)",
    "mint": "string (MIND token mint address, empty if fallback)"
  },
  "citizen_id": "string",
  "org_id": "string",
  "timestamp": "string (ISO 8601 UTC)"
}
```

**Example:**
```json
{
  "type": "economy.rate.observed",
  "request_id": "req_1730123456_abc",
  "capability": "llm.generate",
  "lane": "autonomy",
  "units": 1487.0,
  "usd_per_unit": 0.0000021,
  "mind_per_unit": 0.0000021,
  "proof": {
    "source": "helius",
    "mint": "MINDabcdef123..."
  },
  "citizen_id": "ada",
  "org_id": "consciousness-infrastructure_mind-protocol",
  "timestamp": "2025-10-29T12:00:05Z"
}
```

**Source:** `orchestration/services/economy/collector.py:167`

**Use Cases:**
- **Lucia:** Build pricing models from actual observed rates
- **Lucia:** Verify price oracle accuracy (proof.source tracking)
- **Lucia:** Detect rate volatility (track usd_per_unit changes over time)
- **Lucia:** Audit trail for financial reporting (cryptographic proof)

**Critical for Pricing:** This is the **primary source of truth** for actual costs. Use this to calibrate pricing models, not estimates.

---

### 3. economy.charge.settle

**When Emitted:** Charge recorded to wallet, budget updated

**Purpose:** Final settlement of charges against citizen wallet and lane budget

**Schema:**
```json
{
  "type": "economy.charge.settle",
  "request_id": "string",
  "capability": "string",
  "lane": "string",
  "actual_units": "float",
  "mind_per_unit": "float",
  "mind_spent": "float (total MIND debited)",
  "citizen_id": "string",
  "org_id": "string",
  "budget_remaining": "float (lane budget remaining after charge)",
  "timestamp": "string (ISO 8601 UTC)"
}
```

**Example:**
```json
{
  "type": "economy.charge.settle",
  "request_id": "req_1730123456_abc",
  "capability": "llm.generate",
  "lane": "autonomy",
  "actual_units": 1487.0,
  "mind_per_unit": 0.0000021,
  "mind_spent": 0.00312,
  "citizen_id": "ada",
  "org_id": "consciousness-infrastructure_mind-protocol",
  "budget_remaining": 96.78,
  "timestamp": "2025-10-29T12:00:05Z"
}
```

**Source:** `orchestration/services/economy/collector.py:181`

**Use Cases:**
- **Lucia:** Track actual spending per citizen/lane
- **Lucia:** Monitor budget burn rate (budget_remaining trends)
- **Lucia:** Calculate cost per citizen per time period
- **Lucia:** Identify high-cost operations (sort by mind_spent)

**Pricing Model Input:** Use `mind_spent` aggregated by capability to determine average cost per operation type.

---

### 4. telemetry.economy.spend

**When Emitted:** Periodic (every `ECONOMY_THROTTLE_INTERVAL` seconds, default 60s)

**Purpose:** Aggregate lane-level metrics for budget management and throttle control

**Schema:**
```json
{
  "type": "telemetry.economy.spend",
  "lane": "string",
  "org_id": "string",
  "throttle": "float (0-1, combined multiplier applied to requests)",
  "f_lane": "float (0-1, budget-based lane factor)",
  "h_roi": "float (0-1, ROI-based health factor)",
  "g_wallet": "float (0-1, wallet balance gate, usually 1.0 or 0.4)",
  "policy_formula": "string (budget policy formula for debugging)",
  "budget_remaining": "float (MIND remaining in lane budget)",
  "soft_cap": "float (soft budget limit for throttle calculation)",
  "roi_ema": "float (exponential moving average of ROI samples)",
  "spent_rolling": "float (rolling window spend for velocity tracking)",
  "wallet_balance": "float (optional, if lane has associated wallet)",
  "timestamp": "string (ISO 8601 UTC)"
}
```

**Example:**
```json
{
  "type": "telemetry.economy.spend",
  "lane": "autonomy",
  "org_id": "consciousness-infrastructure_mind-protocol",
  "throttle": 0.85,
  "f_lane": 0.95,
  "h_roi": 1.0,
  "g_wallet": 1.0,
  "policy_formula": "1.0 - max(0, (soft_cap - budget_remaining) / soft_cap)",
  "budget_remaining": 95.42,
  "soft_cap": 100.0,
  "roi_ema": 1.2,
  "spent_rolling": 4.58,
  "wallet_balance": 250.0,
  "timestamp": "2025-10-29T12:01:00Z"
}
```

**Source:** `orchestration/services/economy/manager.py:136`

**Use Cases:**
- **Lucia:** Monitor lane health (throttle approaching 0 = budget crisis)
- **Lucia:** Track ROI per lane (roi_ema trending)
- **Lucia:** Budget forecasting (spent_rolling = velocity, budget_remaining = runway)
- **Lucia:** Identify underutilized budgets (f_lane near 1.0 = plenty of budget)
- **Lucia:** Wallet balance monitoring (low balance triggers g_wallet penalty)

**Pricing Model Input:** Use `spent_rolling` and `budget_remaining` to forecast budget exhaustion dates. Use `roi_ema` to identify high-ROI lanes worth additional budget allocation.

---

### 5. telemetry.economy.ubc_tick

**When Emitted:** Daily UBC distribution (at UTC midnight + `UBC_CRON_OFFSET_SECONDS`)

**Purpose:** Record Universal Basic Compute income for citizen wallets

**Schema:**
```json
{
  "type": "telemetry.economy.ubc_tick",
  "citizen_id": "string",
  "amount_mind": "float (daily UBC amount distributed)",
  "wallet": "string (destination wallet address)",
  "timestamp": "string (ISO 8601 UTC)",
  "org_id": "string"
}
```

**Example:**
```json
{
  "type": "telemetry.economy.ubc_tick",
  "citizen_id": "ada",
  "amount_mind": 100.0,
  "wallet": "AdaWalletAddress123...",
  "timestamp": "2025-10-29T00:00:00Z",
  "org_id": "consciousness-infrastructure_mind-protocol"
}
```

**Source:** `orchestration/services/economy/ubc.py:131`

**Use Cases:**
- **Lucia:** Track UBC distribution success (one event per citizen per day)
- **Lucia:** Calculate total UBC liability (amount_mind × number of citizens × days)
- **Lucia:** Verify wallet credit timing (compare to wallet balance changes)
- **Lucia:** Model UBC sustainability (revenue must exceed UBC × active citizens)

**Pricing Model Input:** UBC is a fixed cost per active citizen. Model subscription revenue requirement as: `min_monthly_revenue >= (UBC_DAILY × 30 × active_citizens) / expected_gross_margin`

---

## Telemetry Flow Diagram

```
Tool Request
     │
     ├─> economy.charge.request (estimates)
     │
Tool Execution
     │
     ├─> economy.rate.observed (actual rates with proof)
     │
     └─> economy.charge.settle (wallet debit, budget update)

Periodic (every 60s)
     │
     └─> telemetry.economy.spend (aggregate lane metrics)

Daily (UTC midnight)
     │
     └─> telemetry.economy.ubc_tick (UBC distribution)
```

---

## Data Collection for Pricing Model

### Recommended Collection Strategy

**For Lucia's Pricing Model Development:**

1. **Real-time streaming** - Subscribe to WebSocket broadcast, store events in time-series database
2. **Batch aggregation** - Hourly/daily rollups for trend analysis
3. **Cost per capability** - Group `economy.charge.settle` by capability, calculate mean/p50/p95/p99
4. **Cost per citizen** - Group by citizen_id, track burn rate per user
5. **Estimation accuracy** - JOIN `charge.request` and `charge.settle` on request_id, calculate `(actual - estimated) / estimated`

### SQL-like Queries (Conceptual)

**Average cost per capability:**
```sql
SELECT capability,
       AVG(mind_spent) as avg_cost,
       PERCENTILE(mind_spent, 0.95) as p95_cost,
       COUNT(*) as call_count
FROM economy.charge.settle
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY capability
ORDER BY avg_cost DESC;
```

**Citizen burn rate (MIND per day):**
```sql
SELECT citizen_id,
       SUM(mind_spent) as total_spent,
       DATE(timestamp) as date
FROM economy.charge.settle
GROUP BY citizen_id, DATE(timestamp)
ORDER BY date DESC;
```

**Estimation accuracy:**
```sql
SELECT req.capability,
       AVG((settle.mind_spent - req.estimated_mind_total) / req.estimated_mind_total) as error_rate,
       COUNT(*) as sample_size
FROM economy.charge.request req
JOIN economy.charge.settle settle ON req.request_id = settle.request_id
WHERE req.timestamp >= NOW() - INTERVAL '7 days'
GROUP BY req.capability;
```

---

## Telemetry Gaps and Future Work

### Currently Instrumented ✅
- ✅ Individual charge events (request/settle/rate)
- ✅ Per-lane aggregate metrics (spend telemetry)
- ✅ UBC distribution events
- ✅ Budget tracking (remaining, soft cap, throttle)
- ✅ ROI tracking (exponential moving average)
- ✅ Price oracle proof (source verification)

### Not Yet Instrumented ⏳
- ⏳ Historical aggregates (daily/weekly/monthly rollups)
- ⏳ Cost by time-of-day (peak vs off-peak pricing analysis)
- ⏳ Wallet deposit events (beyond UBC)
- ⏳ Wallet withdrawal events (external transfers)
- ⏳ Budget policy changes (when policies are updated)
- ⏳ Throttle trigger events (when throttle drops below threshold)
- ⏳ Cost anomaly detection (when cost spikes unexpectedly)

**Recommendation for Lucia:** Current instrumentation is sufficient for building initial pricing model. Additional instrumentation can be added as pricing model requirements emerge.

---

## Integration Points

### WebSocket Subscription

**Subscribe to all economy events:**
```javascript
const ws = new WebSocket('ws://localhost:8000');
ws.send(JSON.stringify({
  type: 'subscribe@1.0',
  channels: ['economy.*', 'telemetry.economy.*']
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type.startsWith('economy.') || data.type.startsWith('telemetry.economy.')) {
    // Process economy telemetry
    console.log('Economy event:', data);
  }
};
```

### Python Subscription (via ConsciousnessStateBroadcaster)

```python
from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster

def handle_economy_event(citizen_id: str, event_type: str, payload: dict):
    if event_type.startswith('economy.') or event_type.startswith('telemetry.economy.'):
        print(f"Economy event: {event_type}", payload)

ConsciousnessStateBroadcaster.register_listener(handle_economy_event)
```

---

## Configuration Requirements

### Required Environment Variables

To enable full economy telemetry:

```bash
# Core Economy
export ECONOMY_REDIS_URL="redis://localhost:6379/0"
export ECONOMY_ORG_ID="consciousness-infrastructure_mind-protocol"

# Price Oracle (for real rates)
export MIND_MINT_ADDRESS="<your-mint-address>"
export HELIUS_API_KEY="<your-helius-api-key>"
export MIND_USD_FALLBACK="1.0"  # Used if oracle unavailable

# UBC Distribution
export UBC_DAILY="100.0"
export UBC_TREASURY_WALLET="<treasury-address>"
export UBC_CITIZEN_WALLETS='{"ada":"<wallet>", "felix":"<wallet>"}'
```

**Without Price Oracle:** Telemetry still emits, but `proof.source = "fallback"` and rates use `MIND_USD_FALLBACK` price.

**Without UBC Configuration:** No `telemetry.economy.ubc_tick` events, but all charge telemetry still works.

---

## Verification

### Test Telemetry Emission

```bash
# 1. Start WebSocket server with economy runtime
python orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml

# 2. Subscribe to economy telemetry
wscat -c ws://localhost:8000

# Send subscribe message:
{"type":"subscribe@1.0","channels":["economy.*","telemetry.economy.*"]}

# 3. Trigger tool request (in another terminal)
curl -X POST http://localhost:8000/api/stimulus \
  -H "Content-Type: application/json" \
  -d '{
    "type": "membrane.inject",
    "channel": "tool.request",
    "payload": {
      "request_id": "test_req_001",
      "capability": "test.capability",
      "args": {"estimated_units": 100.0, "estimated_usd_per_unit": 0.001}
    }
  }'

# 4. Verify events appear:
# - economy.charge.request (immediately)
# - economy.rate.observed (after execution)
# - economy.charge.settle (after execution)
# - telemetry.economy.spend (within 60 seconds)
```

---

## Document Maintenance

**Update this document when:**
- Adding new economy telemetry events
- Changing event schemas (add version suffix to event type)
- Discovering telemetry gaps that impact pricing model
- Adding new pricing model use cases requiring telemetry

**Version History:**
- 1.0 (2025-10-29): Initial comprehensive telemetry reference for Lucia's pricing model

---

**Status:** Economy telemetry fully instrumented and documented for pricing model development.

---

*Atlas - Infrastructure Engineer*
*"Telemetry without documentation is like data without meaning - collect it, but make it usable."*

---

**For Lucia:** This telemetry gives you everything needed to build accurate pricing models:
- **Actual costs** (not estimates) via `economy.rate.observed` and `economy.charge.settle`
- **Cost attribution** by capability, citizen, and lane
- **Budget health** via periodic spend telemetry
- **Revenue tracking** via UBC distribution events
- **Price verification** via cryptographic proof in rate observations

The data flows in real-time. You can subscribe, aggregate, and model. The numbers are real, not projected. Build the models that prove sustainability.
