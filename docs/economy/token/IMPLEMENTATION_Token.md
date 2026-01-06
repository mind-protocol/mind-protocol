# IMPLEMENTATION: Token Module

```
STATUS: ACTIVE
PURPOSE: Code architecture for $MIND token infrastructure
UPDATED: 2025-01-06
```

---

## Directory Structure

```
economy/token/
├── __init__.py                              # Module exports
├── spl_token_mint_authority_controller.py   # Mint operations
├── token_burn_condition_executor.py         # Burn operations
├── metaplex_token_metadata_manager.py       # Token metadata
├── token_supply_target_calculator.py        # Supply calculations
└── solana_token_deployment_script.py        # Deployment automation

docs/economy/token/
├── OBJECTIVES_Token.md                      # What we're building
├── PATTERNS_Token.md                        # Design philosophy
├── BEHAVIORS_Token.md                       # Observable effects
├── ALGORITHM_Token.md                       # Exact formulas
├── VALIDATION_Token.md                      # Invariants/tests
├── IMPLEMENTATION_Token.md                  # This file
└── SYNC_Token.md                            # Current state

tests/economy/
├── test_token_mint_conditions.py            # M1-M4 tests
├── test_token_burn_conditions.py            # B1-B5 tests
├── test_token_supply_calculations.py        # Supply formula tests
└── test_token_authority_controls.py         # Security tests
```

---

## Key Files

### spl_token_mint_authority_controller.py

**Purpose:** Control all minting operations through defined conditions.

**Key Classes:**
- `MintCondition` — Enum of mint triggers (M1-M4)
- `MintResult` — Result dataclass with success, amount, tx_signature
- `MintAuthorityController` — Main controller class

**Key Methods:**
```python
mint_for_citizen_registration(citizen_wallet, citizen_id) -> MintResult
mint_for_bond_creation(recipient_wallet, stake_amount, bond_id) -> MintResult
mint_for_utility_delivery(citizen_wallet, citizen_id, utility_ema, rate) -> MintResult
mint_for_org_formation(org_wallet, org_id) -> MintResult
get_daily_mint_remaining(citizen_id) -> float
```

**Configuration:**
- `DECIMALS = 9` — Solana standard
- `dry_run` mode for testing without blockchain

---

### token_burn_condition_executor.py

**Purpose:** Execute burns only through defined friction conditions.

**Key Classes:**
- `BurnCondition` — Enum of burn triggers (B1-B5)
- `BurnResult` — Result dataclass with success, amount, tx_signature
- `BurnConditionExecutor` — Main executor class

**Key Methods:**
```python
calculate_membrane_fee(amount, source_layer, dest_layer, trust_score) -> float
burn_membrane_fee(source_wallet, amount, source_layer, dest_layer, trust_score) -> BurnResult
calculate_compute_burn(compute_cost) -> float
burn_for_compute(source_wallet, compute_cost) -> BurnResult
calculate_dormancy_decay(balance, days_inactive) -> float
burn_dormancy_decay(source_wallet, balance, days_inactive) -> BurnResult
calculate_early_withdrawal_penalty(stake_amount, days_staked) -> float
burn_early_withdrawal_penalty(source_wallet, stake_amount, days_staked) -> BurnResult
calculate_deregistration_burn(balance) -> float
burn_for_deregistration(source_wallet, balance, citizen_id) -> BurnResult
```

---

### metaplex_token_metadata_manager.py

**Purpose:** Manage token metadata for wallets and explorers.

**Key Classes:**
- `TokenMetadata` — Dataclass with name, symbol, image, description
- `MetadataManager` — Manager for on-chain metadata

**Key Methods:**
```python
get_metadata() -> TokenMetadata
set_image_uri(image_uri)
set_metadata_uri(metadata_uri)
validate_metadata() -> tuple[bool, list[str]]
create_on_chain_metadata() -> dict
to_json_metadata() -> dict  # For off-chain JSON
```

**Default Metadata:**
```python
DEFAULT_METADATA = TokenMetadata(
    name="MIND",
    symbol="MIND",
    decimals=9,
    description="Crystallized alignment...",
)
```

---

### token_supply_target_calculator.py

**Purpose:** Calculate healthy supply target and health indicators.

**Key Classes:**
- `SupplyMetrics` — Input metrics dataclass

**Key Functions:**
```python
calculate_target_supply(metrics: SupplyMetrics) -> float
calculate_supply_adjustment(metrics: SupplyMetrics) -> dict
calculate_per_citizen_target(metrics: SupplyMetrics) -> float
calculate_health_indicators(metrics: SupplyMetrics) -> dict
```

**Pre-configured Scenarios:**
```python
SCENARIO_BOOTSTRAP  # 21 citizens, 0 supply
SCENARIO_MONTH_1    # 50 citizens, 500K supply
SCENARIO_MATURE     # 1000 citizens, 50M supply
```

---

### solana_token_deployment_script.py

**Purpose:** Automate token deployment to Solana.

**Key Classes:**
- `DeploymentConfig` — Configuration dataclass
- `TokenDeployer` — Main deployment orchestrator

**Key Methods:**
```python
check_prerequisites() -> bool
create_token_mint() -> Optional[str]
set_mint_authority(new_authority) -> bool
disable_freeze_authority() -> bool
mint_initial_supply(recipient, amount) -> bool
deploy() -> bool  # Full deployment
```

**Usage:**
```bash
# Dry run (default)
python solana_token_deployment_script.py --network devnet

# Live deployment
python solana_token_deployment_script.py --network mainnet-beta --live --keypair /path/to/keypair.json
```

---

## Data Flow

### Mint Flow

```
Trigger (e.g., citizen registration)
    ↓
MintAuthorityController.mint_for_citizen_registration()
    ↓
Check condition (citizen exists, not already minted)
    ↓
Calculate amount (10,000 $MIND)
    ↓
[dry_run] Return mock result
[live] Execute SPL token mint instruction
    ↓
Return MintResult
```

### Burn Flow

```
Trigger (e.g., cross-layer transaction)
    ↓
BurnConditionExecutor.burn_membrane_fee()
    ↓
Calculate fee (with trust discount)
    ↓
[dry_run] Return mock result
[live] Execute SPL token burn instruction
    ↓
Return BurnResult
```

### Supply Calculation Flow

```
Collect SupplyMetrics from:
- L4 Registry (citizens, orgs)
- Staking module (bonds)
- Utility oracle (monthly utility)
- On-chain data (burns, current supply)
    ↓
calculate_target_supply(metrics)
    ↓
calculate_supply_adjustment(metrics)
    ↓
Return action recommendation (HOLD/MINT/ALLOW_BURN)
```

---

## Dependencies

### Internal

| Dependency | Purpose |
|------------|---------|
| L4 Registry | Citizen/org existence checks |
| Staking module | Bond data |
| Utility oracle | Utility delivery data |

### External

| Dependency | Purpose | Installation |
|------------|---------|--------------|
| solana-py | Solana RPC | `pip install solana` |
| spl-token | Token operations | `pip install spl-token` |
| Solana CLI | Deployment | [solana.com/docs](https://solana.com/docs/intro/installation) |

---

## Configuration

### Environment Variables

```bash
# RPC endpoints
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Keypair paths
SOLANA_KEYPAIR_PATH=/path/to/keypair.json

# Token addresses (after deployment)
MIND_TOKEN_MINT=<mint_address>
```

### Module Constants

```python
# In spl_token_mint_authority_controller.py
DECIMALS = 9
MINT_CONDITIONS = {
    M1: {"base_amount": 10_000},
    M2: {"rate": 0.10},
    M3: {"daily_cap": 1000},
    M4: {"base_amount": 50_000},
}

# In token_burn_condition_executor.py
BURN_CONDITIONS = {
    B1: {"min_rate": 0.01, "max_rate": 0.05},
    B2: {"burn_rate": 0.10},
    B3: {"grace_period_days": 30, "weekly_rate": 0.01},
    B4: {"penalty_rate": 0.20, "maturation_days": 180},
    B5: {"burn_rate": 0.50},
}
```

---

## Extension Points

### Adding New Mint Condition

1. Add to `MintCondition` enum
2. Add to `MINT_CONDITIONS` dict
3. Create `mint_for_<condition>` method
4. Add to `__init__.py` exports
5. Write tests
6. Update docs

### Adding New Burn Condition

1. Add to `BurnCondition` enum
2. Add to `BURN_CONDITIONS` dict
3. Create `calculate_<condition>_burn` method
4. Create `burn_for_<condition>` method
5. Add to `__init__.py` exports
6. Write tests
7. Update docs

---

## Related

- `ALGORITHM_Token.md` — Formulas implemented here
- `VALIDATION_Token.md` — What to test
- `SYNC_Token.md` — Current state
