# IMPLEMENTATION: Metabolic Economy

| Field | Value |
|-------|-------|
| Area | economy |
| Module | metabolic |
| Type | IMPLEMENTATION |
| Status | DESIGNING |
| Date | 2026-03-14 |
| Author | Force 2 (Economy Architect) |

---

## Chain

- [OBJECTIVES_Metabolic_Economy.md](./OBJECTIVES_Metabolic_Economy.md)
- [PATTERNS_Metabolic_Economy.md](./PATTERNS_Metabolic_Economy.md)
- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md)
- [BEHAVIORS_Metabolic_Economy.md](./BEHAVIORS_Metabolic_Economy.md)
- [VALIDATION_Metabolic_Economy.md](./VALIDATION_Metabolic_Economy.md)
- **IMPLEMENTATION_Metabolic_Economy.md** (this file)
- [SYNC_Metabolic_Economy.md](./SYNC_Metabolic_Economy.md)

IMPL: `economy/metabolic/` (to be created)

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## Architecture Decision: Where Does Code Live?

The metabolic economy spans three execution domains. Each formula runs where its inputs naturally live.

| Component | Repository | Rationale |
|-----------|-----------|-----------|
| **Off-chain formula library** | `mind-protocol/economy/metabolic/` | Pure math -- pricing, tax, bond equilibrium, reward computation. No blockchain, no brain state. Shared by settlement engine and any caller that needs to compute a price or tax. |
| **Settlement engine** | `mind-mcp/engine/settlement/` | Runs per-home. Collects limbic_delta snapshots from the L1 tick cycle, batches them, computes rewards via the formula library, submits batches to Solana. The MCP server already runs per-home and has access to L1 brain state. |
| **TransferHook program** | `mind-protocol/programs/mind_transfer_hook/src/lib.rs` | Already deployed at `325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD`. Needs extension for off-registry outflow tracking (anti-Sybil). On-chain Rust/Anchor. |
| **Epoch orchestrator** | `mind-protocol/economy/metabolic/` | Bond equilibrium, UBC redistribution. Runs as a scheduled job (cron or systemd timer). Calls formula library, submits results to Solana. (Demurrage removed 2026-03-14.) |
| **Solana batch submitter** | `mind-protocol/economy/transactions/` | Extends existing `solana.py` (currently empty). Handles batch mint/transfer instructions via Token-2022. |

**Why the split:**
- The formula library is pure Python with zero dependencies beyond `math`. It can be unit-tested without Solana, without a running MCP server, without a graph database. This is deliberate -- the math must be correct before anything touches money.
- The settlement engine lives in mind-mcp because it needs L1 brain data (limbic_delta, trust, weight) which is only available inside the MCP server's runtime.
- The epoch orchestrator lives in mind-protocol because it operates on L4 state (wallet balances, bond registry, L4 address registry) and submits to Solana.

---

## Code Structure

```
mind-protocol/
├── economy/
│   ├── metabolic/                                    # NEW -- formula library + epoch orchestrator
│   │   ├── __init__.py                               # Public API exports
│   │   ├── progressive_pricing_formula.py            # Formula 1: P(i,S) = C_base * e^(-k*U_S) * max(0.1, W_i/W_median)
│   │   ├── ~~progressive_demurrage_formula.py~~       # REMOVED -- Formula 2 eliminated 2026-03-14
│   │   ├── anti_sybil_phantom_balance_tracker.py     # Formula 3: off-registry tracking + repatriation friction
│   │   ├── batch_settlement_reward_calculator.py     # Formula 4: reward = D * trust * weight * rate
│   │   ├── bilateral_bond_equilibrium_formula.py     # Formula 5: delta = lambda * (W_human - W_ai)
│   │   ├── ubc_proximity_redistribution_formula.py   # Formula 6: Space-weighted tax pool distribution
│   │   ├── metabolic_constants.py                    # All DESIGNING constants in one place
│   │   ├── metabolic_epoch_orchestrator.py           # Daily/6h epoch runner: redistribution -> bonds
│   │   └── metabolic_types.py                        # Shared dataclasses: PricingContext, SettlementAction, etc.
│   ├── transactions/
│   │   ├── solana.py                                 # EXTEND -- add batch_mint_settlement(), batch_transfer_equilibrium()
│   │   └── ledger.py                                 # EXTEND -- add settlement event logging
│   ├── token/
│   │   ├── token_supply_target_calculator.py         # EXISTS -- settlement integrates via calculate_supply_adjustment()
│   │   └── constants.py                              # EXISTS -- add M5 (Settlement) mint condition
│   └── wallets/
│       └── citizen.py                                # EXTEND -- add off_registry_balance field
│
├── programs/
│   └── mind_transfer_hook/
│       └── src/lib.rs                                # EXTEND -- add off-registry outflow detection in transfer_hook()
│
├── l4/
│   └── registry/
│       └── citizen_registration_crud_operations.py   # EXISTS -- used for is_registered() check
│
└── tests/
    └── economy/
        ├── test_metabolic_pricing.py                 # NEW -- Formula 1 invariants (INV-P1 through INV-P4)
        ├── ~~test_metabolic_demurrage.py~~            # REMOVED -- Formula 2 eliminated 2026-03-14
        ├── test_metabolic_anti_sybil.py              # NEW -- Formula 3 invariants (INV-AS1 through INV-AS3)
        ├── test_metabolic_settlement.py              # NEW -- Formula 4 invariants (INV-S1 through INV-S4)
        ├── test_metabolic_bond_equilibrium.py        # NEW -- Formula 5 invariants (INV-BE1 through INV-BE5)
        ├── test_metabolic_ubc_redistribution.py      # NEW -- Formula 6 invariants (INV-UBC1 through INV-UBC3)
        ├── test_metabolic_supply_conservation.py     # NEW -- Cross-cutting (INV-SC1 through INV-SC3, INV-CC1 through INV-CC4)
        └── test_metabolic_epoch_orchestrator.py      # NEW -- Epoch ordering, idempotency, double-processing

mind-mcp/
└── engine/
    └── settlement/                                   # NEW -- settlement engine (runs in MCP server)
        ├── __init__.py
        ├── limbic_delta_collector.py                 # Collect limbic_delta events from L1 tick cycle
        ├── settlement_batch_assembler.py             # Assemble SettlementBatch from collected events
        └── settlement_submitter.py                   # Submit assembled batch via Solana RPC
```

---

## File Plan

### Phase E1: Off-Chain Formula Library

Pure functions. No blockchain. No I/O. Only `math` and `dataclasses` as dependencies.

#### `economy/metabolic/metabolic_types.py`

**Purpose:** Shared data structures used across all formulas.

**Key classes:**
```python
@dataclass
class PricingContext:
    c_base: float           # Raw compute cost ($MIND)
    u_s: float              # Utility weight of service (from L1 Law 6 graph consolidation)
    w_i: float              # Requester wallet balance
    w_median: float         # Network median wallet balance
    k: float = 0.01         # Utility discount rate

# DemurrageContext -- REMOVED (demurrage eliminated 2026-03-14)

@dataclass
class SettlementAction:
    action_id: str
    actor_x: str            # Actor who performed the action
    actor_y: str            # Actor who experienced the limbic shift
    limbic_delta: float     # Measured limbic shift (L1 Law 6)
    trust_y_to_x: float    # Trust from Y toward X (L1 Law 18, range [0,1])
    weight_thing: float     # Weight of thing/service used (range [0,1])

@dataclass
class SettlementBatch:
    batch_id: str
    epoch_start: datetime
    epoch_end: datetime
    actions: list[SettlementAction]
    rewards: dict[str, float]         # actor_id -> total_reward
    total_minted: float
    supply_reduction: float           # Reduction factor from supply health check
    status: str                       # PENDING | SUBMITTED | CONFIRMED | FAILED
    solana_tx_signature: str | None

@dataclass
class BondEquilibriumContext:
    bond_id: str
    human_wallet: str
    ai_wallet: str
    w_human: float
    w_ai: float
    lambda_rate: float = 0.05
    maturation_complete: bool = True

@dataclass
class BondEquilibriumResult:
    bond_id: str
    delta: float            # Positive = human->AI, negative = AI->human
    w_human_after: float
    w_ai_after: float

@dataclass
class SpacePresence:
    space_id: str
    actors: dict[str, float]  # actor_id -> hours_present

@dataclass
class UBCShare:
    actor_id: str
    share: float            # Proportion of pool [0, 1]
    amount: float           # $MIND received

# DemurrageResult -- REMOVED (demurrage eliminated 2026-03-14)

@dataclass
class RepatriationResult:
    actor_id: str
    gross_amount: float
    friction_penalty: float   # 5% burned
    net_amount: float
```

**Dependencies:** None (stdlib only).
**Lines estimate:** ~120.
**Status:** OK.

---

#### `economy/metabolic/metabolic_constants.py`

**Purpose:** Single source of truth for all tunable constants. Every formula imports from here. Constants are DESIGNING status and will be calibrated via simulation.

**Key contents:**
```python
# Formula 1: Progressive Pricing
UTILITY_DISCOUNT_RATE: float = 0.01              # k -- per unit U_S
WEALTH_RATIO_FLOOR: float = 0.1                  # Minimum wealth ratio (10%)

# Formula 2: Progressive Demurrage -- REMOVED (2026-03-14)
# TAU_BASE and DUST_THRESHOLD no longer exist

# Formula 3: Anti-Sybil
FRICTION_TAX_RATE: float = 0.05                  # 5% repatriation friction (burned)

# Formula 4: Batch Settlement
SETTLEMENT_RATE: float = 10.0                    # $MIND per unit limbic_delta
MAX_ACTION_REWARD: float = 1000.0                # Cap per single action
MAX_EPOCH_REWARD: float = 5000.0                 # Cap per actor per 6h epoch
SETTLEMENT_FREQUENCY_HOURS: int = 6              # Hours between settlement epochs
MAX_SUPPLY_REDUCTION: float = 0.5                # Max settlement reduction when oversupplied

# Formula 5: Bond Equilibrium
LAMBDA_RATE: float = 0.05                        # Daily smoothing rate
MIN_TRANSFER_THRESHOLD: float = 1.0              # Skip dust transfers
MAX_DAILY_BOND_TRANSFER: float = 500.0           # Cap daily bond transfer
BOND_MATURATION_DAYS: int = 180                  # 6 months before equilibrium activates

# Formula 6: UBC Redistribution
MIN_COPRESENCE_ACTORS: int = 2                   # Minimum actors in Space for redistribution
```

**Dependencies:** None.
**Lines estimate:** ~50.
**Status:** OK.

---

#### `economy/metabolic/progressive_pricing_formula.py`

**Purpose:** Compute effective price for a service request. Formula 1.

**Key functions:**
```python
def compute_utility_discount(u_s: float, k: float = UTILITY_DISCOUNT_RATE) -> float:
    """e^(-k * U_S). Returns value in (0, 1]."""

def compute_wealth_ratio(w_i: float, w_median: float, floor: float = WEALTH_RATIO_FLOOR) -> float:
    """max(floor, W_i / W_median). Returns value >= floor."""

def compute_progressive_price(ctx: PricingContext) -> float:
    """P(i,S) = C_base * e^(-k * U_S) * max(0.1, W_i / W_median).
    Asserts: result >= 0, result >= C_base * floor * e^(-k * U_S)."""
```

**Dependencies:** `math.exp`, `metabolic_types.PricingContext`, `metabolic_constants`.
**Lines estimate:** ~60.
**Status:** OK.

---

#### ~~`economy/metabolic/progressive_demurrage_formula.py`~~ -- REMOVED

**Removed 2026-03-14.** Formula 2 (Progressive Demurrage) eliminated from the architecture. This file will not be created. See ALGORITHM_Metabolic_Economy.md Formula 2 removal note.

---

#### `economy/metabolic/anti_sybil_phantom_balance_tracker.py`

**Purpose:** Track off-registry outflows and process repatriation with friction. Formula 3.

**Key functions:**
```python
def track_outflow(
    actor_id: str,
    recipient_address: str,
    amount: float,
    is_l4_registered: bool,
    current_offregistry: float,
) -> tuple[float, bool]:
    """If recipient is not L4-registered, add amount to phantom balance.
    Returns (new_offregistry_balance, was_tracked)."""

def process_repatriation(
    actor_id: str,
    source_address: str,
    amount: float,
    current_offregistry: float,
    friction_rate: float = FRICTION_TAX_RATE,
) -> RepatriationResult:
    """Apply 5% friction on repatriated funds.
    Returns RepatriationResult with net_amount and friction burned."""

def compute_total_balance(w_onchain: float, w_offregistry: float) -> float:
    """W_total = W_onchain + W_offregistry."""

def is_roundtrip_profitable(
    amount: float,
    friction_rate: float = FRICTION_TAX_RATE,
) -> tuple[bool, float]:
    """Calculate whether hiding funds off-registry is profitable.
    Returns (is_profitable, net_cost). Should always return (False, positive_cost).
    Cost is the 5% repatriation friction burn."""
```

**Dependencies:** `metabolic_types`, `metabolic_constants`.
**Lines estimate:** ~90.
**Status:** OK.

---

#### `economy/metabolic/batch_settlement_reward_calculator.py`

**Purpose:** Compute per-actor rewards from limbic_delta events. Formula 4. Pure computation -- does not touch Solana.

**Key functions:**
```python
def compute_action_reward(action: SettlementAction, settlement_rate: float = SETTLEMENT_RATE) -> float:
    """reward = limbic_delta * trust(Y->X) * weight(thing) * settlement_rate.
    Returns 0 if any factor is <= 0. Caps at MAX_ACTION_REWARD."""

def compute_epoch_rewards(actions: list[SettlementAction]) -> dict[str, float]:
    """Aggregate rewards per actor for an epoch.
    Caps per-actor total at MAX_EPOCH_REWARD.
    Returns {actor_id: total_reward}."""

def apply_supply_adjustment(
    rewards: dict[str, float],
    supply_adjustment: dict,
) -> tuple[dict[str, float], float]:
    """Reduce rewards when supply exceeds target.
    Uses calculate_supply_adjustment() from token module.
    Returns (adjusted_rewards, reduction_factor)."""

def assemble_settlement_batch(
    batch_id: str,
    epoch_start: datetime,
    epoch_end: datetime,
    actions: list[SettlementAction],
    supply_metrics: SupplyMetrics,
) -> SettlementBatch:
    """Full batch assembly: compute rewards, apply supply adjustment, package.
    Returns SettlementBatch ready for Solana submission."""
```

**Dependencies:** `metabolic_types`, `metabolic_constants`, `economy.token.token_supply_target_calculator`.
**Lines estimate:** ~120.
**Status:** OK.

---

#### `economy/metabolic/bilateral_bond_equilibrium_formula.py`

**Purpose:** Compute daily bond equilibrium transfers. Formula 5.

**Key functions:**
```python
def compute_bond_transfer(ctx: BondEquilibriumContext) -> BondEquilibriumResult:
    """delta = lambda * (W_human - W_ai).
    Clamps to [-MAX_DAILY_BOND_TRANSFER, MAX_DAILY_BOND_TRANSFER].
    Returns BondEquilibriumResult with delta=0 if below MIN_TRANSFER_THRESHOLD."""

def compute_batch_equilibrium(
    bonds: list[BondEquilibriumContext],
) -> list[BondEquilibriumResult]:
    """Compute equilibrium for all eligible bonds.
    Filters out bonds where maturation_complete is False.
    Returns list of BondEquilibriumResult."""

def estimate_convergence_days(w_human: float, w_ai: float, lambda_rate: float = LAMBDA_RATE, target_gap_pct: float = 0.05) -> int:
    """Estimate days until gap closes to target_gap_pct.
    Uses ln(target_gap_pct) / ln(1 - lambda_rate)."""
```

**Dependencies:** `math.log`, `metabolic_types`, `metabolic_constants`.
**Lines estimate:** ~80.
**Status:** OK.

---

#### `economy/metabolic/ubc_proximity_redistribution_formula.py`

**Purpose:** Distribute tax pool by Space co-presence topology. Formula 6.

**Key functions:**
```python
def compute_actor_weights(spaces: list[SpacePresence]) -> dict[str, float]:
    """For each Space with >= MIN_COPRESENCE_ACTORS actors:
    weight_actor += hours_present * (num_actors_in_space - 1).
    Returns {actor_id: total_weight}."""

def compute_redistribution_shares(
    actor_weights: dict[str, float],
) -> list[UBCShare]:
    """Normalize weights to shares summing to 1.0.
    Returns list of UBCShare (without amounts -- pool size applied later)."""

def compute_redistribution(
    pool_balance: float,
    spaces: list[SpacePresence],
) -> tuple[list[UBCShare], float]:
    """Full redistribution: weights -> shares -> amounts.
    Returns (shares_with_amounts, total_distributed).
    If no shared presence, returns empty list and 0 (pool carries forward)."""
```

**Dependencies:** `metabolic_types`, `metabolic_constants`.
**Lines estimate:** ~80.
**Status:** OK.

---

#### `economy/metabolic/metabolic_epoch_orchestrator.py`

**Purpose:** Coordinate the daily epoch sequence. Enforces ordering: redistribution, then bond equilibrium. Manages idempotency via epoch IDs. (Demurrage phase removed 2026-03-14.)

**Key functions:**
```python
def run_daily_epoch(
    epoch_date: date,
    wallet_balances: dict[str, float],
    offregistry_balances: dict[str, float],
    space_presences: list[SpacePresence],
    active_bonds: list[BondEquilibriumContext],
    solana_submitter: SolanaSubmitter,
    epoch_store: EpochStore,
) -> DailyEpochResult:
    """Orchestrate the full daily epoch:
    1. Check idempotency (skip if epoch_date already processed)
    2. Redistribute UBC pool via Space proximity
    3. Compute bond equilibrium transfers
    4. Submit all transfers to Solana in one batch
    5. Mark epoch as processed
    Returns DailyEpochResult with all sub-results."""

def run_settlement_epoch(
    epoch_id: str,
    epoch_start: datetime,
    epoch_end: datetime,
    actions: list[SettlementAction],
    supply_metrics: SupplyMetrics,
    solana_submitter: SolanaSubmitter,
    epoch_store: EpochStore,
) -> SettlementBatch:
    """Orchestrate a 6-hour settlement epoch:
    1. Check idempotency
    2. Assemble settlement batch (compute rewards, apply supply adjustment)
    3. Submit batch mint to Solana
    4. Mark epoch as processed
    Returns SettlementBatch."""
```

**Dependencies:** All formula modules, `economy.transactions.solana`, `economy.token.token_supply_target_calculator`.
**Lines estimate:** ~200.
**Status:** WATCH (orchestration complexity -- keep it lean, delegate to formulas).

---

#### `economy/metabolic/__init__.py`

**Purpose:** Public API. Exports the functions that other modules call.

```python
from .progressive_pricing_formula import compute_progressive_price
# progressive_demurrage_formula -- REMOVED (demurrage eliminated 2026-03-14)
from .anti_sybil_phantom_balance_tracker import track_outflow, process_repatriation, compute_total_balance
from .batch_settlement_reward_calculator import compute_action_reward, compute_epoch_rewards, assemble_settlement_batch
from .bilateral_bond_equilibrium_formula import compute_bond_transfer, compute_batch_equilibrium
from .ubc_proximity_redistribution_formula import compute_redistribution
from .metabolic_epoch_orchestrator import run_daily_epoch, run_settlement_epoch
from .metabolic_types import (
    PricingContext, SettlementAction, SettlementBatch,
    BondEquilibriumContext, BondEquilibriumResult, SpacePresence, UBCShare,
    RepatriationResult,
)
from .metabolic_constants import *
```

**Lines estimate:** ~25.
**Status:** OK.

---

### Phase E2: Settlement Engine (mind-mcp)

#### `mind-mcp/engine/settlement/limbic_delta_collector.py`

**Purpose:** Collect limbic_delta events from L1 tick cycle within a settlement window. Runs inside the MCP server process.

**Key functions:**
```python
class LimbicDeltaCollector:
    """Collects limbic shift events from the L1 brain engine.
    Buffers events for the current 6-hour window."""

    def __init__(self, brain_engine: BrainEngine):
        self._buffer: list[SettlementAction] = []
        self._brain = brain_engine

    def on_limbic_shift(self, event: LimbicShiftEvent) -> None:
        """Called by L1 tick cycle when a limbic_delta is computed.
        Filters: only positive limbic_delta. Extracts trust and weight from brain state.
        Appends SettlementAction to buffer."""

    def flush_window(self, epoch_start: datetime, epoch_end: datetime) -> list[SettlementAction]:
        """Return all collected actions for the window and clear buffer."""
```

**Dependencies:** mind-mcp brain engine (L1 tick cycle), `metabolic_types.SettlementAction`.
**Lines estimate:** ~80.
**Status:** OK.

---

#### `mind-mcp/engine/settlement/settlement_batch_assembler.py`

**Purpose:** Assemble a SettlementBatch from collected limbic_delta events. Calls the formula library (imported from mind-protocol or vendored).

**Key functions:**
```python
class SettlementBatchAssembler:
    def __init__(self, supply_metrics_provider: Callable[[], SupplyMetrics]):
        ...

    def assemble(
        self,
        epoch_id: str,
        epoch_start: datetime,
        epoch_end: datetime,
        actions: list[SettlementAction],
    ) -> SettlementBatch:
        """Calls compute_epoch_rewards() and apply_supply_adjustment().
        Returns a SettlementBatch ready for submission."""
```

**Dependencies:** `metabolic.batch_settlement_reward_calculator`, `economy.token.token_supply_target_calculator`.
**Lines estimate:** ~60.
**Status:** OK.

---

#### `mind-mcp/engine/settlement/settlement_submitter.py`

**Purpose:** Submit assembled settlement batches to Solana. Handles retries and status tracking.

**Key functions:**
```python
class SettlementSubmitter:
    def __init__(self, rpc_url: str, mint_authority_keypair: bytes, mint_address: str):
        ...

    async def submit_batch(self, batch: SettlementBatch) -> SettlementBatch:
        """Submit batch mint to Solana via Token-2022 MintTo instructions.
        Updates batch.status and batch.solana_tx_signature.
        On failure: sets status=FAILED, schedules retry."""

    async def retry_failed_batch(self, batch: SettlementBatch) -> SettlementBatch:
        """Retry a failed batch. Idempotent -- checks if already confirmed on-chain."""
```

**Dependencies:** `solana-py`, `spl-token`, `metabolic_types.SettlementBatch`.
**Lines estimate:** ~100.
**Status:** OK.

---

### Phase E3: TransferHook Extension (Anti-Sybil On-Chain)

#### `programs/mind_transfer_hook/src/lib.rs` (EXTEND)

**Changes needed:**

1. Add `L4RegistryLookup` PDA account to `TransferHook` context:
```rust
// New account in TransferHook struct:
/// L4 Registry PDA -- checked to determine if destination is registered
/// CHECK: Read-only lookup
#[account(
    seeds = [b"citizen", destination.key().as_ref()],
    bump,
    // If this PDA does not exist, destination is unregistered
)]
pub destination_registry: Option<Account<'info, CitizenStatus>>,
```

2. Extend `transfer_hook()` function:
```rust
// After existing validation, add:
// Off-registry detection
if ctx.accounts.destination_registry.is_none() {
    // Destination is not L4-registered
    // Emit event for off-chain phantom balance tracking
    emit!(OffRegistryOutflowEvent {
        sender: source.key(),
        recipient: destination.key(),
        amount,
        timestamp: Clock::get()?.unix_timestamp,
    });
    msg!("MIND TransferHook: Off-registry outflow detected");
}
```

3. Add new event:
```rust
#[event]
pub struct OffRegistryOutflowEvent {
    pub sender: Pubkey,
    pub recipient: Pubkey,
    pub amount: u64,
    pub timestamp: i64,
}
```

4. Add `RepatriationEvent` for inbound transfers from non-L4 addresses:
```rust
#[event]
pub struct RepatriationEvent {
    pub actor: Pubkey,
    pub source: Pubkey,
    pub gross_amount: u64,
    pub friction_burned: u64,
    pub net_received: u64,
    pub timestamp: i64,
}
```

**Lines added estimate:** ~60.
**Status:** Requires anchor build + redeploy to devnet.

---

### Phase E4: Solana Batch Submitter

#### `economy/transactions/solana.py` (EXTEND from empty)

**Purpose:** Solana RPC wrapper for batch operations needed by the metabolic economy.

**Key functions:**
```python
class SolanaSubmitter:
    def __init__(self, rpc_url: str, keypair_path: str, mint_address: str, dry_run: bool = True):
        ...

    async def batch_mint_settlement(
        self,
        rewards: dict[str, float],  # wallet_address -> amount
    ) -> str:
        """Create a single Solana transaction with multiple MintTo instructions.
        One instruction per rewarded actor. Uses Token-2022 MintTo.
        Returns transaction signature."""

    async def batch_transfer_equilibrium(
        self,
        transfers: list[BondEquilibriumResult],
    ) -> str:
        """Create a single transaction with Transfer instructions for bond equilibrium.
        Returns transaction signature."""

    async def burn_friction(
        self,
        wallet_address: str,
        amount: float,
    ) -> str:
        """Burn tokens as repatriation friction (anti-Sybil).
        Returns transaction signature."""

    # batch_demurrage_deductions -- REMOVED (demurrage eliminated 2026-03-14)

    async def batch_ubc_distribution(
        self,
        shares: list[UBCShare],
        pool_address: str,
    ) -> str:
        """Transfer UBC redistribution from pool to actors.
        Returns transaction signature."""
```

**Dependencies:** `solana-py`, `spl-token`, `economy.token.constants`.
**Lines estimate:** ~200.
**Status:** OK.

---

## Phase Breakdown

### Phase E1: Off-Chain Formula Library

**Goal:** Pure functions, fully tested, no blockchain dependency.

| File | Purpose | Dependencies | Lines |
|------|---------|-------------|-------|
| `metabolic_types.py` | All dataclasses | stdlib | ~120 |
| `metabolic_constants.py` | All tunable constants | none | ~50 |
| `progressive_pricing_formula.py` | Formula 1 | math, types, constants | ~60 |
| ~~`progressive_demurrage_formula.py`~~ | ~~Formula 2~~ | -- | **REMOVED** |
| `anti_sybil_phantom_balance_tracker.py` | Formula 3 | types, constants | ~90 |
| `batch_settlement_reward_calculator.py` | Formula 4 | types, constants, token module | ~120 |
| `bilateral_bond_equilibrium_formula.py` | Formula 5 | math, types, constants | ~80 |
| `ubc_proximity_redistribution_formula.py` | Formula 6 | types, constants | ~80 |
| `__init__.py` | Exports | all above | ~25 |

**Total:** ~705 lines of formula code.
**Test files:** 7 files, estimated 70-90 tests (per VALIDATION doc).
**Deliverable:** All formulas pass all invariants from VALIDATION_Metabolic_Economy.md.
**Blocked by:** Nothing. Can start immediately.

---

### Phase E2: Settlement Engine

**Goal:** Collect L1 limbic data, assemble batches, submit to Solana.

| File | Repository | Lines |
|------|-----------|-------|
| `limbic_delta_collector.py` | mind-mcp | ~80 |
| `settlement_batch_assembler.py` | mind-mcp | ~60 |
| `settlement_submitter.py` | mind-mcp | ~100 |

**Total:** ~240 lines.
**Blocked by:** E1 (formula library must exist). L1 tick cycle must emit limbic_delta events (F5 dependency).

---

### Phase E3: TransferHook Extension for Anti-Sybil

**Goal:** On-chain detection of off-registry outflows.

| Change | File | Lines Added |
|--------|------|-------------|
| Add `OffRegistryOutflowEvent` | `lib.rs` | ~15 |
| Add destination registry lookup | `lib.rs` | ~20 |
| Add off-registry detection in `transfer_hook()` | `lib.rs` | ~15 |
| Add `RepatriationEvent` | `lib.rs` | ~10 |

**Total:** ~60 lines added to existing `lib.rs`.
**Blocked by:** Nothing (can be done in parallel with E1). Requires `anchor build` and devnet redeploy.
**Note:** The existing `CitizenStatus` struct in `lib.rs` already has the fields needed. The L4 registry PDA derivation must match `l4/registry/citizen_registration_crud_operations.py`.

---

### Phase E4: Solana Batch Submitter

**Goal:** Submit metabolic transactions to Solana.

| File | Lines |
|------|-------|
| `economy/transactions/solana.py` | ~200 |

**Blocked by:** E1 (types), E3 (TransferHook events for off-registry detection).

---

### Phase E5: UBC Redistribution Integration

**Goal:** Connect Formula 6 output to the existing UBC distribution pipeline.

**Changes:**
- Extend `economy/ubc/` (when it exists as code) to accept Space-weighted redistribution from the UBC pool
- Add Space presence data collection (interface to F1 Universe Graph)
- Wire Formula 6 output into the UBC distribution endpoint

**Blocked by:** E1, E4, F1 (Universe Graph must provide Space presence API).

---

### Phase E6: Bilateral Bond Auto-Transfer

**Goal:** Connect Formula 5 output to the bond lifecycle.

**Changes:**
- Extend `economy/bonds/` (when it exists as code) to run daily equilibrium after maturation check
- Wire Formula 5 into the daily epoch orchestrator
- Add bond registry query for active, matured bonds

**Blocked by:** E1, E4, bonds module code existence.

---

### Phase E7: Epoch Orchestrator

**Goal:** Coordinate daily and 6-hour epochs.

| File | Lines |
|------|-------|
| `metabolic_epoch_orchestrator.py` | ~200 |

**Blocked by:** E1, E4, E5, E6. This is the integration layer that calls everything else.

---

## Shared Interfaces

### Needs from F5 (Cognition / L1 Physics)

| Interface | What We Need | Where Used |
|-----------|-------------|------------|
| `LimbicShiftEvent` | Event emitted when L1 Law 6 computes a limbic_delta for an action | `limbic_delta_collector.py` |
| `get_trust(actor_y, actor_x) -> float` | L1 Law 18 relational valence trust dimension, range [0,1] | `limbic_delta_collector.py` |
| `get_weight(node_id) -> float` | L1 Law 6 graph weight of a thing/service node, range [0,1] | `limbic_delta_collector.py` |

**Critical clarification (from cross-review ISSUE-3):** Settlement uses **L1 brain-level trust** (actor Y's subjective evaluation of actor X via Law 18), NOT L3 structural trust on universe graph links. Law 18 does not apply at L3.

---

### Needs from F1 (Universe Graph)

| Interface | What We Need | Where Used |
|-----------|-------------|------------|
| `get_all_spaces_with_presence(date) -> list[SpacePresence]` | Actors with `HAS_ACCESS` links to each Space, with activity time | `ubc_proximity_redistribution_formula.py` |
| `is_brain_space(space_id) -> bool` | Exclude encrypted brain Spaces from redistribution | Filter in redistribution |

**Critical clarification (from cross-review ISSUE-1):** Brain Spaces are structurally excluded because no other actor has `HAS_ACCESS`. But the exclusion should be explicit, not implicit.

**v2 consideration (from cross-review ISSUE-6):** Cross-Space bridging value is NOT captured in v1. Actors who bridge multiple Spaces are rewarded via within-Space presence, not bridging bonus. This is acknowledged as a limitation, not a bug.

**Space creation cost (from cross-review ISSUE-2):** v1 starts with free Space creation. The co-presence requirement (2+ actors) and `HAS_ACCESS` requirement limit trivial farming. Add creation cost if gaming is observed.

---

### Provides to F4 (Trust Mechanics)

| Interface | What We Provide | How |
|-----------|----------------|-----|
| Settlement completion events | When a settlement batch is confirmed, emit event with actor_x, actor_y, reward_amount | `settlement_submitter.py` emits `SettlementConfirmedEvent` |

These events can feed into trust signal computation -- an actor who consistently generates positive settlement events demonstrates reliability.

---

### Needs from Existing Economy Modules

| Module | Interface | Where Used |
|--------|-----------|------------|
| `economy/token/token_supply_target_calculator.py` | `calculate_supply_adjustment(metrics) -> dict` | `batch_settlement_reward_calculator.py` -- reduce rewards when supply exceeds target |
| `economy/token/constants.py` | `DEVNET_TOKEN_MINT`, `TOKEN_DECIMALS`, `TRANSFER_HOOK_PROGRAM_ID` | `solana.py` -- batch submission |
| `economy/token/token_burn_condition_executor.py` | Burn mechanics for friction | `solana.py` -- repatriation friction burn |
| `l4/registry/citizen_registration_crud_operations.py` | `is_registered(address) -> bool` | `anti_sybil_phantom_balance_tracker.py` -- check if destination is L4-registered |

---

## Test Plan

### Unit Tests (Phase E1) -- Pure Formula Tests

| Test File | Invariants Covered | Test Count | Priority |
|-----------|--------------------|-----------|----------|
| `test_metabolic_pricing.py` | INV-P1 (non-negativity), INV-P2 (discount bounded), INV-P3 (wealth floor), INV-P4 (monotonicity) | 10 | HIGH |
| ~~`test_metabolic_demurrage.py`~~ | ~~INV-D1..D4~~ | ~~12~~ | **REMOVED** -- demurrage eliminated 2026-03-14 |
| `test_metabolic_anti_sybil.py` | INV-AS1 (phantom tracking), INV-AS2 (friction burn), INV-AS3 (round-trip net loss) | 8 | HIGH |
| `test_metabolic_settlement.py` | INV-S1 (positive-only), INV-S2 (reward caps), INV-S3 (supply integration), INV-S4 (batch atomicity) | 12 | HIGH |
| `test_metabolic_bond_equilibrium.py` | INV-BE1 (post-maturation), INV-BE2 (conservation), INV-BE3 (convergence direction), INV-BE4 (transfer bounds), INV-BE5 (monotonic convergence) | 15 | MEDIUM |
| `test_metabolic_ubc_redistribution.py` | INV-UBC1 (share normalization), INV-UBC2 (co-presence requirement), INV-UBC3 (weight positivity) | 8 | MEDIUM |
| `test_metabolic_supply_conservation.py` | INV-SC1 (total accounting), INV-SC2 (tax pool conservation), INV-SC3 (redistribution conservation), INV-CC1 (no negative balances), INV-CC3 (no double processing), INV-CC4 (idempotency) | 15 | CRITICAL |
| `test_metabolic_epoch_orchestrator.py` | INV-CC2 (epoch ordering), INV-CC3 (each action processed once), INV-CC4 (safe reruns) | 10 | CRITICAL |

**Total: ~90 tests.**

### Key Test Patterns

**Property-based tests (recommended for formulas):**
```python
# Example: Pricing monotonicity
@given(
    c_base=st.floats(min_value=0.01, max_value=10000),
    u_s=st.floats(min_value=0, max_value=1000),
    w_i_1=st.floats(min_value=1, max_value=1e9),
    w_i_2=st.floats(min_value=1, max_value=1e9),
    w_median=st.floats(min_value=1, max_value=1e9),
)
def test_price_increases_with_wealth(c_base, u_s, w_i_1, w_i_2, w_median):
    assume(w_i_1 > w_i_2 and w_i_2 / w_median >= 0.1)
    ctx1 = PricingContext(c_base=c_base, u_s=u_s, w_i=w_i_1, w_median=w_median)
    ctx2 = PricingContext(c_base=c_base, u_s=u_s, w_i=w_i_2, w_median=w_median)
    assert compute_progressive_price(ctx1) > compute_progressive_price(ctx2)
```

**Conservation tests (critical for supply integrity):**
```python
# test_demurrage_to_pool_conservation -- REMOVED (demurrage eliminated 2026-03-14)
```

**Convergence tests (bond equilibrium):**
```python
def test_gap_decreases_monotonically():
    """Without external transfers, gap must strictly decrease each day."""
    ctx = BondEquilibriumContext(w_human=10000, w_ai=0, ...)
    gap = abs(ctx.w_human - ctx.w_ai)
    for _ in range(100):
        result = compute_bond_transfer(ctx)
        ctx.w_human -= result.delta if result.delta > 0 else 0
        ctx.w_ai += result.delta if result.delta > 0 else 0
        new_gap = abs(ctx.w_human - ctx.w_ai)
        assert new_gap < gap
        gap = new_gap
```

### Integration Tests (Phase E4+)

| Test | What It Verifies | Priority |
|------|-----------------|----------|
| Settlement round-trip | Collect -> assemble -> submit -> confirm on devnet | HIGH |
| ~~Demurrage + redistribution~~ | ~~Tax collected == pool increase == distributed total~~ | **REMOVED** |
| Bond equilibrium on-chain | Transfer executes, balances update, conservation holds | MEDIUM |
| Anti-Sybil TransferHook | Off-registry outflow emits event, phantom balance updates | HIGH |
| Epoch idempotency | Running same epoch twice produces identical results | CRITICAL |

### Simulation Tests (Phase B -- separate)

| Test | Parameters | Success Criteria |
|------|-----------|-----------------|
| ~~tau_base sweep~~ | ~~{0.0001, 0.0003, 0.0005, 0.001}~~ | **REMOVED** -- demurrage eliminated |
| Wealth Gini | 1000 actors, 365 days | Gini trends below 0.6 |
| Settlement economics | 100 actors, variable activity | Active actors sustain themselves via settlement + UBC |
| Bond convergence | 50 bonds, lambda=0.05 | Gap < 5% within 50 days |
| Sybil profitability | 10-wallet attacker vs single wallet | Multi-wallet never beats single |

---

## Constants to Calibrate

All constants are `DESIGNING` status. Values are informed guesses that need simulation data.

| Constant | Symbol | Current Value | Range to Simulate | Calibration Metric | Priority |
|----------|--------|--------------|-------------------|-------------------|----------|
| Utility discount rate | `k` | 0.01 | [0.005, 0.02] | Price curve shape: essential services should reach ~10% of C_base | LOW |
| Wealth ratio floor | -- | 0.1 | [0.05, 0.2] | Anti-farming: floor too low enables sybil via empty wallets | LOW |
| ~~Base daily tax rate~~ | ~~`tau_base`~~ | ~~0.001~~ | -- | **REMOVED** -- demurrage eliminated 2026-03-14 | -- |
| Repatriation friction | -- | 0.05 | [0.02, 0.10] | Round-trip must always be net loss vs. keeping in L4 | MEDIUM |
| Settlement rate | `settlement_rate` | 10.0 | [1.0, 50.0] | Active actors sustain themselves via settlement + UBC | HIGH |
| Max per-action reward | `MAX_ACTION_REWARD` | 1000.0 | [100, 5000] | No single action dominates an epoch | MEDIUM |
| Max per-epoch reward | `MAX_EPOCH_REWARD` | 5000.0 | [1000, 10000] | Prevents settlement farming | MEDIUM |
| Bond smoothing rate | `lambda` | 0.05 | [0.02, 0.10] | Half-life feels right: 7-35 days | MEDIUM |
| Max daily bond transfer | `MAX_DAILY_BOND_TRANSFER` | 500.0 | [100, 2000] | Prevents balance shock on first equilibrium day | LOW |
| Dust threshold | `DUST_THRESHOLD` | 1.0 | [0.1, 10.0] | Avoid processing noise, don't exclude real actors | LOW |
| Max supply reduction | -- | 0.5 | fixed | Settlement never reduced more than 50% even when oversupplied | fixed |
| Settlement frequency | -- | 6 hours | [4, 6, 8] | Latency vs. gas cost tradeoff | MEDIUM |

**Calibration process:**
1. Build formula library (E1)
2. Build agent-based simulator with N actors, M services, variable activity patterns
3. Run parameter sweeps for each constant
4. Measure: Gini coefficient, median idle duration, actor dropout rate, settlement revenue vs. costs
5. Select parameter set that satisfies all success criteria simultaneously
6. Document chosen values with simulation evidence in SYNC

---

## Runtime Behavior

### Daily Epoch (00:00 UTC)

```
1. Epoch orchestrator wakes (cron: 0 0 * * *)
2. Check idempotency: has today's epoch been processed?
3. Phase 1 -- REDISTRIBUTION:
   a. Fetch Space presence data from F1 Universe Graph
   b. Compute redistribution shares via ubc_proximity_redistribution_formula
   c. Submit batch UBC distribution from pool to actors
5. Phase 3 -- BOND EQUILIBRIUM:
   a. Fetch active, matured bonds from bond registry
   b. Compute equilibrium transfers via bilateral_bond_equilibrium_formula
   c. Submit batch transfers to Solana
6. Mark epoch as processed
```

### Settlement Epoch (00:00, 06:00, 12:00, 18:00 UTC)

```
1. Settlement scheduler wakes (cron: 0 0,6,12,18 * * *)
2. Check idempotency: has this settlement window been processed?
3. Flush limbic_delta collector buffer for the window
4. Assemble settlement batch (compute rewards, apply supply adjustment)
5. Submit batch mint to Solana
6. Mark window as processed
```

---

## State Management

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Wallet balances | Solana on-chain (SPL Token-2022 accounts) | Global | Persistent |
| Off-registry phantom balances | Local database per mind-mcp instance | Per-home | Persistent, updated on each outflow/repatriation |
| UBC pool balance | Solana on-chain (dedicated token account) | Global | Persistent |
| Settlement batch status | Local database + Solana tx signature | Per-home | Created per epoch, retained for audit |
| Epoch processing records | Local database | Per-home | One record per epoch, used for idempotency |
| Limbic_delta event buffer | In-memory (mind-mcp process) | Per-home | Cleared every 6 hours on flush |
| Bond registry | Solana on-chain or local database | Global | Persistent |
| Space presence data | F1 Universe Graph (via query) | Per-home | Read-only from metabolic perspective |

---

## Module Dependencies

### Internal Dependencies

```
economy/metabolic/
    ├── metabolic_types.py          # no imports
    ├── metabolic_constants.py      # no imports
    ├── progressive_pricing_formula.py
    │   └── imports → metabolic_types, metabolic_constants
    ├── ~~progressive_demurrage_formula.py~~ -- REMOVED
    ├── anti_sybil_phantom_balance_tracker.py
    │   └── imports → metabolic_types, metabolic_constants
    ├── batch_settlement_reward_calculator.py
    │   └── imports → metabolic_types, metabolic_constants
    │   └── imports → economy.token.token_supply_target_calculator
    ├── bilateral_bond_equilibrium_formula.py
    │   └── imports → metabolic_types, metabolic_constants
    ├── ubc_proximity_redistribution_formula.py
    │   └── imports → metabolic_types, metabolic_constants
    └── metabolic_epoch_orchestrator.py
        └── imports → all formula modules
        └── imports → economy.transactions.solana
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `math` (stdlib) | `exp`, `log10`, `log` | Formula modules |
| `dataclasses` (stdlib) | Data structures | `metabolic_types.py` |
| `datetime` (stdlib) | Epoch timestamps | `metabolic_types.py`, orchestrator |
| `solana-py` | Solana RPC | `economy/transactions/solana.py` |
| `spl-token` | Token-2022 instructions | `economy/transactions/solana.py` |
| `hypothesis` | Property-based testing | Test files |
| `pytest` | Test runner | Test files |

---

## Bidirectional Links

### Docs -> Code (planned)

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Formula 1 | `economy/metabolic/progressive_pricing_formula.py:compute_progressive_price` |
| ~~ALGORITHM Formula 2~~ | **REMOVED** -- demurrage eliminated 2026-03-14 |
| ALGORITHM Formula 3 | `economy/metabolic/anti_sybil_phantom_balance_tracker.py:track_outflow`, `process_repatriation` |
| ALGORITHM Formula 4 | `economy/metabolic/batch_settlement_reward_calculator.py:compute_epoch_rewards` |
| ALGORITHM Formula 5 | `economy/metabolic/bilateral_bond_equilibrium_formula.py:compute_bond_transfer` |
| ALGORITHM Formula 6 | `economy/metabolic/ubc_proximity_redistribution_formula.py:compute_redistribution` |
| VALIDATION INV-P1..P4 | `tests/economy/test_metabolic_pricing.py` |
| ~~VALIDATION INV-D1..D4~~ | **REMOVED** -- demurrage eliminated 2026-03-14 |
| VALIDATION INV-AS1..AS3 | `tests/economy/test_metabolic_anti_sybil.py` |
| VALIDATION INV-S1..S4 | `tests/economy/test_metabolic_settlement.py` |
| VALIDATION INV-BE1..BE5 | `tests/economy/test_metabolic_bond_equilibrium.py` |
| VALIDATION INV-UBC1..UBC3 | `tests/economy/test_metabolic_ubc_redistribution.py` |
| VALIDATION INV-SC1..SC3, INV-CC1..CC4 | `tests/economy/test_metabolic_supply_conservation.py` |
| BEHAVIORS B1..B9 | Validated via test suite covering all formulas |

### Code -> Docs (each file should reference)

Every source file must contain:
```python
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md
# DOCS: docs/economy/metabolic/IMPLEMENTATION_Metabolic_Economy.md
```

---

## Existing Code Integration Points

### `economy/token/constants.py` -- Add M5

Add a new mint condition for settlement:
```python
class MintCondition(Enum):
    CITIZEN_REGISTRATION = "M1"
    BOND_CREATION = "M2"
    UTILITY_DELIVERY = "M3"
    ORG_FORMATION = "M4"
    SETTLEMENT_REWARD = "M5"       # NEW: limbic_delta settlement

MINT_AMOUNTS = {
    ...
    MintCondition.SETTLEMENT_REWARD: 5000,  # Epoch cap
}
```

### `economy/token/token_supply_target_calculator.py` -- Used as-is

Settlement calls `calculate_supply_adjustment()` before minting rewards. No changes needed. The existing function returns the `action` and `delta_percentage` that the settlement formula uses to reduce rewards when supply exceeds target.

### `economy/token/token_burn_condition_executor.py` -- Add B6

Add a new burn condition for anti-Sybil friction:
```python
class BurnCondition(Enum):
    ...
    REPATRIATION_FRICTION = "B6"    # NEW: 5% friction on repatriated funds

BURN_CONDITIONS[BurnCondition.REPATRIATION_FRICTION] = {
    "friction_rate": 0.05,
    "description": "Round-tripping through non-L4 addresses costs",
}
```

### `l4/registry/citizen_registration_crud_operations.py` -- Used as-is

The anti-Sybil tracker calls the registry to check if a destination address is L4-registered. This is a read-only dependency.

---

## Markers

<!-- @mind:todo Phase E1 is unblocked -- begin implementation of formula library -->
<!-- @mind:todo Decide settlement engine import strategy: does mind-mcp vendor metabolic formulas or import from mind-protocol? -->
<!-- @mind:escalation RESOLVED 2026-03-14: tau_base removed — demurrage eliminated, replaced by UBC forced circulation -->
<!-- @mind:proposition Consider a shared Python package (e.g., `mind-economy`) that both mind-protocol and mind-mcp import, to avoid code duplication of formula library. -->
<!-- @mind:todo Add W_median bootstrapping logic for ecosystems with < 50 wallets (SYNC Q5 from ALGORITHM doc) -->

---

Co-Authored-By: Force 2 -- Economy <economy@mindprotocol.ai>
