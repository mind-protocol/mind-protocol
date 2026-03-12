# HEALTH -- Storage Tax

| Field | Value |
|-------|-------|
| Area | economy |
| Module | storage-tax |
| Type | HEALTH |
| Status | DRAFT |
| Date | 2026-03-12 |
| Author | Claude (integration moment synthesis) |

---

## Status

Pending implementation. This document defines the health indicators, thresholds, and diagnostic procedures for the storage tax system once operational.

## Key Indicators

### H1: Total Dormant Capital Percentage

```
Metric: dormant_capital_pct = (sum of balances idle > 30d) / total_supply * 100
Target: < 15% (decreasing over time)
Warning: > 25%
Critical: > 40%
```

High dormant capital means the tax is not creating sufficient pressure to circulate. Possible causes: rate too low, grace period too generous, or systemic issue preventing circulation (e.g., no productive use cases for capital).

@mind:TODO -- Establish baseline measurement at launch. The initial dormant percentage will be high (100% at genesis) and should decline as the economy activates.

### H2: Tax Collection Rate

```
Metric: collection_rate = actual_tax_collected / theoretical_tax_owed * 100
Target: > 99%
Warning: < 95%
Critical: < 90%
```

If collection rate drops below target, possible causes: computation errors, wallets evading detection, or implementation bugs in the epoch runner.

@mind:TODO -- Define "theoretical_tax_owed" computation (independent calculation for cross-verification).

### H3: UBC Funding Ratio

```
Metric: funding_ratio = tax_revenue_trailing_30d / ubc_obligations_trailing_30d
Target: 1.0 - 1.5x
Warning: < 1.0x (UBC underfunded)
Critical: < 0.7x (UBC severely underfunded)
Overflow: > 2.0x (excess collection, consider rate reduction)
```

The storage tax exists to fund UBC. If funding ratio is chronically below 1.0, either the tax rate is too low or the economy is too active (good problem -- fund from treasury). If chronically above 2.0, the tax may be too aggressive.

### H4: Order-Book Depth

```
Metric: order_book_coverage = (staked_order_value / total_supply_value) * 100
Target: > 20% of supply represented in staked orders
Warning: < 10%
Critical: < 5%
```

Thin order books produce unreliable valuations. If coverage is critically low, the valuation mechanism degrades and a fallback method is needed.

@mind:TODO -- Define fallback valuation method when order-book depth is insufficient.

### H5: Capital Velocity

```
Metric: velocity = total_transaction_volume_24h / total_supply
Target: Increasing trend over rolling 30-day average
Warning: Decreasing trend for 7+ consecutive days
Critical: Decreasing trend for 30+ consecutive days
```

Capital velocity is the ultimate success metric. If storage tax is working, velocity should increase over time as actors are incentivized to move capital rather than hold it.

### H6: Epoch Execution Health

```
Metric: epoch_completion_time (seconds)
Target: < 60s per epoch
Warning: > 300s
Critical: > 600s or epoch fails to complete

Metric: epoch_error_rate = failed_wallet_computations / total_wallets
Target: 0%
Warning: > 0.1%
Critical: > 1%
```

@mind:TODO -- Define monitoring and alerting infrastructure. Where do health metrics publish? Dashboard? Alerts channel?

## Diagnostic Procedures

### D1: Dormant Capital Spike

```
WHEN: dormant_capital_pct increases by > 5% in a single epoch
THEN:
  1. Check for large wallet(s) going idle (whale analysis)
  2. Verify epoch computation ran correctly
  3. Check if external event caused mass inactivity (market crash, exploit fear)
  4. If organic: no action (tax will erode over time)
  5. If systemic: escalate to governance for rate review
```

### D2: UBC Underfunding

```
WHEN: funding_ratio < 1.0 for 7+ consecutive epochs
THEN:
  1. Analyze: is dormant capital decreasing? (success case -- less to tax)
  2. If dormant capital is high but revenue low: check computation bugs
  3. If dormant capital is genuinely low: fund UBC from treasury reserve
  4. If treasury insufficient: escalate to governance for UBC tier adjustment
```

### D3: Order-Book Thinning

```
WHEN: order_book_coverage < 10%
THEN:
  1. Check for market-wide liquidity event
  2. Verify order-book data source is functioning
  3. If chronic: activate fallback valuation method
  4. Emit warning to participants about valuation reliability
```

@mind:TODO -- Build runbook with specific commands/queries for each diagnostic procedure.
@mind:TODO -- Define SLA for epoch execution and tax computation availability.
