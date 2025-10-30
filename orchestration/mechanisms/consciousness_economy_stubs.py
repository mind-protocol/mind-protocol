"""
Consciousness Economy Implementation Stubs

Pydantic schemas, PriceEstimator quoter(), and helper stubs for implementing
the $MIND accounting layer.

Author: Luca (Consciousness Architect)
Created: 2025-10-26
Status: Implementation reference (stubs to be filled by Felix/Atlas)
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ============================================================================
# Pydantic Schemas
# ============================================================================

class BudgetAccount(BaseModel):
    """
    Budget account tracking $MIND credits for sources and compartments.

    Tracks balance, lifetime spending, and reservation status.
    """
    owner_type: str = Field(..., description="citizen|human|service|compartment")
    owner_id: str = Field(..., description="Unique identifier for owner")
    balance: float = Field(..., description="Available credits", ge=0.0)
    reserved: float = Field(default=0.0, description="Reserved but not yet settled", ge=0.0)
    initial_balance: float = Field(..., description="Starting allocation")
    lifetime_minted: float = Field(default=0.0, description="Total credits minted from outcomes")
    lifetime_burned: float = Field(default=0.0, description="Total credits burned from failures")
    lifetime_spent: float = Field(default=0.0, description="Total credits spent on stimuli")
    utility_ema: float = Field(default=0.5, description="Utility score EMA [0,1]", ge=0.0, le=1.0)
    harm_ema: float = Field(default=0.0, description="Harm score EMA [0,1]", ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "owner_type": "citizen",
                "owner_id": "felix",
                "balance": 18500.0,
                "reserved": 0.0,
                "initial_balance": 20000.0,
                "lifetime_minted": 1200.0,
                "lifetime_burned": 300.0,
                "lifetime_spent": 2400.0,
                "utility_ema": 0.87,
                "harm_ema": 0.05,
            }
        }


class Quote(BaseModel):
    """
    Price quote for stimulus injection.

    Returned before injection to provide cost predictability.
    """
    planned_delta_e: float = Field(..., description="Requested energy injection", ge=0.0, le=1.0)
    allowed_delta_e: float = Field(..., description="Allowed after budget check", ge=0.0, le=1.0)
    face_price: float = Field(..., description="Credits per unit ΔE (before rebate)", gt=0.0)
    rebate: float = Field(..., description="Discount fraction [0, 0.5]", ge=0.0, le=0.5)
    effective_price: float = Field(..., description="Credits per unit ΔE (after rebate)", gt=0.0)
    expected_debit: float = Field(..., description="Estimated cost in credits", ge=0.0)
    compute_estimate: Dict = Field(default_factory=dict, description="Predicted LLM tokens, tools")
    confidence: float = Field(default=0.8, description="Prediction confidence [0,1]", ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "planned_delta_e": 0.75,
                "allowed_delta_e": 0.42,
                "face_price": 1.90,
                "rebate": 0.22,
                "effective_price": 1.48,
                "expected_debit": 0.62,
                "compute_estimate": {"llm_tokens": 0, "tools": 0, "cost": 0.0},
                "confidence": 0.86,
            }
        }


class MembraneProperties(BaseModel):
    """
    Properties stored on MEMBRANE_TO edge.

    Tracks permeability, effectiveness, and emission history.
    """
    k_up: float = Field(default=0.5, description="Upward permeability [0,1]", ge=0.0, le=1.0)
    k_down: float = Field(default=0.9, description="Downward permeability [0,1]", ge=0.0, le=1.0)
    flow_ema: float = Field(default=0.0, description="Long-run flow volume EMA", ge=0.0, le=1.0)
    eff_ema: float = Field(default=0.5, description="Effectiveness EMA from receiving level", ge=0.0, le=1.0)
    last_emit_up: str = Field(default="", description="Last upward event ID")
    last_emit_down: str = Field(default="", description="Last downward event ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "k_up": 0.5,
                "k_down": 0.9,
                "flow_ema": 0.65,
                "eff_ema": 0.72,
                "last_emit_up": "membrane_up_felix_16234",
                "last_emit_down": "membrane_down_mission_impl_atlas_3421",
            }
        }


class AlignmentProperties(BaseModel):
    """
    Properties stored on LIFTS_TO and related alignment edges.

    Tracks structural correspondence between L1 and L2 entities.
    """
    fit: float = Field(..., description="Alignment strength [0,1]", ge=0.0, le=1.0)
    basis: str = Field(..., description="How fit was computed: centroid|usage|manual")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "fit": 0.82,
                "basis": "centroid_similarity",
            }
        }


# ============================================================================
# PriceEstimator Class
# ============================================================================

class PriceEstimator:
    """
    Computes face price P_t and effective price P^eff based on load, risk, cost.

    Provides quote() method for predictable pricing before injection.
    """

    def __init__(self, config: Dict):
        """
        Args:
            config: Configuration with learned parameters
        """
        self.config = config
        self.load_index = LoadIndex()  # Computes L_t from ρ, backlog, etc.

    def quote(
        self,
        source_id: str,
        planned_delta_e: float,
        stimulus_features: Dict,
        account: BudgetAccount
    ) -> Quote:
        """
        Return price quote before injection.

        Args:
            source_id: Who is requesting injection
            planned_delta_e: Requested energy magnitude
            stimulus_features: novelty, trust, uncertainty, etc.
            account: Source's budget account

        Returns:
            Quote with allowed ΔE and expected cost
        """
        # Compute face price
        L_t = self.load_index.compute()  # Composite load [0,1]
        f_scarcity = self._f_scarcity(L_t)
        f_risk = self._f_risk(
            stimulus_features["trust"],
            stimulus_features["uncertainty"],
            account.harm_ema,
            stimulus_features.get("guardian_weight", 0.0)
        )
        f_cost = self._f_cost(stimulus_features)

        face_price = f_scarcity * f_risk * f_cost

        # Compute rebate (effective price discount)
        rebate = self._compute_rebate(account.utility_ema, account.harm_ema)
        effective_price = face_price * (1 - rebate)

        # Check budget
        max_affordable = account.balance / effective_price if effective_price > 0 else float('inf')
        allowed_delta_e = min(planned_delta_e, max_affordable)

        # Expected cost
        expected_debit = effective_price * allowed_delta_e

        # Compute estimate
        compute_est = self._estimate_compute(stimulus_features)
        confidence = self._compute_confidence(compute_est)

        return Quote(
            planned_delta_e=planned_delta_e,
            allowed_delta_e=allowed_delta_e,
            face_price=face_price,
            rebate=rebate,
            effective_price=effective_price,
            expected_debit=expected_debit,
            compute_estimate=compute_est,
            confidence=confidence
        )

    def _f_scarcity(self, L_t: float) -> float:
        """
        Scarcity pricing based on composite load.

        Returns multiplier [1.0, 10.0].
        """
        # Sigmoid transform: 1.0 → 10.0 as L_t goes 0→1
        steepness = self.config.get("scarcity_steepness", 5.0)
        scarcity = 1.0 + 9.0 * self._sigmoid(L_t, steepness)
        return scarcity

    def _f_risk(self, trust: float, uncertainty: float, harm_ema: float, guardian_weight: float) -> float:
        """
        Risk multiplier based on trust, uncertainty, harm.

        Returns multiplier [0.5, 2.0].
        """
        guardian_caution = guardian_weight * 0.3
        risk = (
            (1.0 - trust) * 0.4 +
            uncertainty * 0.3 +
            harm_ema * 0.2 +
            guardian_caution * 0.1
        )
        caution = 0.5 + 1.5 * risk
        return caution

    def _f_cost(self, stimulus_features: Dict) -> float:
        """
        Compute cost multiplier based on predicted LLM tokens and tools.

        Returns multiplier [0.5, 5.0].
        """
        # Stub: implement based on stimulus complexity
        # For now, return neutral
        return 1.0

    def _compute_rebate(self, utility_ema: float, harm_ema: float) -> float:
        """
        Compute rebate for source based on historical usefulness.

        Returns rebate [0, 0.5].
        """
        usefulness_score = utility_ema * (1.0 - harm_ema)
        rebate = 0.5 * usefulness_score
        return rebate

    def _estimate_compute(self, stimulus_features: Dict) -> Dict:
        """
        Estimate LLM tokens and tool actions for this stimulus.

        Returns:
            {"llm_tokens": int, "tools": int, "cost": float}
        """
        # Stub: implement prediction model
        return {"llm_tokens": 0, "tools": 0, "cost": 0.0}

    def _compute_confidence(self, compute_est: Dict) -> float:
        """Compute confidence in compute estimate."""
        # Stub: implement based on historical accuracy
        return 0.8

    def _sigmoid(self, x: float, steepness: float) -> float:
        """Sigmoid function."""
        import math
        return 1.0 / (1.0 + math.exp(-steepness * (x - 0.5)))


# ============================================================================
# Load Index
# ============================================================================

class LoadIndex:
    """
    Computes composite load index L_t from substrate signals.

    L_t ∈ [0,1] reflects current system capacity pressure.
    """

    def __init__(self):
        self.rho = 0.0
        self.backlog = 0
        self.latency_slip = 0.0
        self.occupancy = 0.0
        self.deferral = 0.0

    def update(
        self,
        rho: float,
        backlog: int,
        latency_slip: float,
        occupancy: float,
        deferral: float
    ):
        """Update constituent signals."""
        self.rho = rho
        self.backlog = backlog
        self.latency_slip = latency_slip
        self.occupancy = occupancy
        self.deferral = deferral

    def compute(self) -> float:
        """
        Compute composite load L_t.

        Returns:
            L_t ∈ [0,1] normalized load index
        """
        # Stub: implement g_load() with change-point normalization
        # For now, simple weighted average
        L_t = (
            self.rho * 0.3 +
            min(self.backlog / 100.0, 1.0) * 0.2 +
            self.latency_slip * 0.2 +
            self.occupancy * 0.2 +
            self.deferral * 0.1
        )
        return min(L_t, 1.0)


# ============================================================================
# Cypher Queries (for FalkorDB integration)
# ============================================================================

# === Budget Account ===

CYPHER_CREATE_BUDGET_ACCOUNT = """
MERGE (account:BudgetAccount {owner_id: $owner_id})
ON CREATE SET
  account.owner_type = $owner_type,
  account.balance = $initial_balance,
  account.reserved = 0.0,
  account.initial_balance = $initial_balance,
  account.lifetime_minted = 0.0,
  account.lifetime_burned = 0.0,
  account.lifetime_spent = 0.0,
  account.utility_ema = 0.5,
  account.harm_ema = 0.0,
  account.created_at = $timestamp,
  account.updated_at = $timestamp
RETURN account
"""

CYPHER_UPDATE_BUDGET_BALANCE = """
MATCH (account:BudgetAccount {owner_id: $owner_id})
SET
  account.balance = account.balance + $delta,
  account.lifetime_spent = account.lifetime_spent + CASE WHEN $delta < 0 THEN -$delta ELSE 0 END,
  account.updated_at = $timestamp
RETURN account
"""

CYPHER_MINT_CREDITS = """
MATCH (account:BudgetAccount {owner_id: $owner_id})
SET
  account.balance = account.balance + $amount,
  account.lifetime_minted = account.lifetime_minted + $amount,
  account.updated_at = $timestamp
RETURN account
"""

CYPHER_BURN_CREDITS = """
MATCH (account:BudgetAccount {owner_id: $owner_id})
SET
  account.balance = account.balance - $amount,
  account.lifetime_burned = account.lifetime_burned + $amount,
  account.updated_at = $timestamp
RETURN account
"""

# === MEMBRANE_TO Edge ===

CYPHER_INIT_MEMBRANE_TO = """
MATCH (c:Compartment {level: $level_from, citizen: $citizen_id})
MATCH (o:Compartment {level: $level_to, org: $org_id})
MERGE (c)-[m:MEMBRANE_TO]->(o)
ON CREATE SET
  m.k_up = 0.5,
  m.k_down = 0.9,
  m.flow_ema = 0.0,
  m.eff_ema = 0.5,
  m.last_emit_up = '',
  m.last_emit_down = '',
  m.created_at = $timestamp,
  m.updated_at = $timestamp
RETURN m
"""

CYPHER_UPDATE_MEMBRANE_PERMEABILITY = """
MATCH (c:Compartment {level: $level_from, citizen: $citizen_id})
      -[m:MEMBRANE_TO]->
      (o:Compartment {level: $level_to, org: $org_id})
SET
  m.k_up = $k_up,
  m.k_down = $k_down,
  m.eff_ema = $eff_ema,
  m.updated_at = $timestamp
RETURN m
"""

CYPHER_UPDATE_MEMBRANE_EMISSION = """
MATCH (c:Compartment {level: $level_from, citizen: $citizen_id})
      -[m:MEMBRANE_TO]->
      (o:Compartment {level: $level_to, org: $org_id})
SET
  m.last_emit_up = CASE WHEN $direction = 'up' THEN $event_id ELSE m.last_emit_up END,
  m.last_emit_down = CASE WHEN $direction = 'down' THEN $event_id ELSE m.last_emit_down END,
  m.flow_ema = $flow_ema,
  m.updated_at = $timestamp
RETURN m
"""

# === LIFTS_TO Edge (Structural Alignment) ===

CYPHER_INIT_LIFTS_TO = """
MATCH (se1:SubEntity {scope: 'L1', id: $subentity_l1_id})
MATCH (se2:SubEntity {scope: 'L2', id: $subentity_l2_id})
MERGE (se1)-[r:LIFTS_TO]->(se2)
ON CREATE SET
  r.fit = $fit,
  r.basis = $basis,
  r.last_updated = $timestamp
RETURN r
"""

CYPHER_UPDATE_LIFTS_TO_FIT = """
MATCH (se1:SubEntity {scope: 'L1', id: $subentity_l1_id})
      -[r:LIFTS_TO]->
      (se2:SubEntity {scope: 'L2', id: $subentity_l2_id})
SET
  r.fit = $fit,
  r.basis = $basis,
  r.last_updated = $timestamp
RETURN r
"""

# === Query Example Usage ===

def example_create_account(graph, owner_type: str, owner_id: str, initial_balance: float):
    """Create budget account in FalkorDB."""
    from datetime import datetime
    result = graph.query(
        CYPHER_CREATE_BUDGET_ACCOUNT,
        {
            "owner_type": owner_type,
            "owner_id": owner_id,
            "initial_balance": initial_balance,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    return result.result_set[0][0] if result.result_set else None


def example_init_membrane(graph, citizen_id: str, org_id: str):
    """Initialize MEMBRANE_TO edge between L1 citizen and L2 org."""
    from datetime import datetime
    result = graph.query(
        CYPHER_INIT_MEMBRANE_TO,
        {
            "level_from": "L1",
            "citizen_id": citizen_id,
            "level_to": "L2",
            "org_id": org_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    return result.result_set[0][0] if result.result_set else None


def example_init_lifts_to(graph, subentity_l1_id: str, subentity_l2_id: str, fit: float, basis: str):
    """Initialize LIFTS_TO alignment edge."""
    from datetime import datetime
    result = graph.query(
        CYPHER_INIT_LIFTS_TO,
        {
            "subentity_l1_id": subentity_l1_id,
            "subentity_l2_id": subentity_l2_id,
            "fit": fit,
            "basis": basis,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    return result.result_set[0][0] if result.result_set else None


# ============================================================================
# Minimal Integration Example
# ============================================================================

def example_quote_and_inject(
    source_id: str,
    planned_delta_e: float,
    stimulus_features: Dict
) -> Tuple[Quote, float]:
    """
    Example flow: quote → inject → settle.

    Returns:
        (Quote, actual_debit)
    """
    # 1. Get account
    account = get_account(source_id)  # Stub: fetch from DB

    # 2. Request quote
    estimator = PriceEstimator(config={})
    quote = estimator.quote(source_id, planned_delta_e, stimulus_features, account)

    print(f"Quote: {quote.dict()}")

    # 3. Check if acceptable (slippage protection)
    max_spend = 2.0  # Example limit
    if quote.expected_debit > max_spend:
        raise Exception(f"Quote exceeds max spend: {quote.expected_debit} > {max_spend}")

    # 4. Reserve credits
    account.balance -= quote.expected_debit
    account.reserved += quote.expected_debit

    # 5. Inject stimulus (stub)
    delta_e_delivered = inject_stimulus(stimulus_features, quote.allowed_delta_e)

    # 6. Settle actual cost
    actual_debit = quote.expected_debit  # Simplified (would compute from actual compute)
    account.reserved -= quote.expected_debit
    account.lifetime_spent += actual_debit

    # 7. Update DB (stub)
    update_account(account)

    return (quote, actual_debit)


# ============================================================================
# Stubs (to be implemented)
# ============================================================================

def get_account(source_id: str) -> BudgetAccount:
    """Fetch account from FalkorDB."""
    # Stub: implement query
    return BudgetAccount(
        owner_type="citizen",
        owner_id=source_id,
        balance=20000.0,
        initial_balance=20000.0,
        utility_ema=0.85,
        harm_ema=0.05
    )


def update_account(account: BudgetAccount):
    """Update account in FalkorDB."""
    # Stub: implement mutation
    pass


def inject_stimulus(stimulus_features: Dict, allowed_delta_e: float) -> float:
    """Inject stimulus through integrator."""
    # Stub: call stimulus_integrator
    return allowed_delta_e * 0.85  # Example: integrator delivers 85% of allowed
