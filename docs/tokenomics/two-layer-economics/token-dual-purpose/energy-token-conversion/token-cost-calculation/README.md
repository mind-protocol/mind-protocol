# 🔢 Token Cost Calculation

**Type:** ALGORITHM
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Two-Layer Economic Architecture](../README.md) > [Token Dual-Purpose Design](../README.md) > [Energy→Token Conversion](../README.md)

**This Node:**
- Token Cost Calculation (ALGORITHM)

**Children:**
- (No children - leaf node)

---

## Relationships

**IMPLEMENTS:**
- Energy→Token Conversion


---

## Purpose

Formula: token_cost = energy_cost × conversion_rate

---

## Algorithm

### Core Formula

```python
token_cost = energy_cost × energy_to_token_conversion_rate
```

### Detailed Algorithm

```python
def calculate_token_cost_for_consciousness_operation(operation_params):
    """
    Calculate $MIND token cost for a consciousness operation.

    Args:
        operation_params: Dictionary containing:
            - node_activation_count: int (number of nodes to activate)
            - working_memory_size: int (number of WM slots to use)
            - spreading_activation_hops: int (traversal depth)
            - energy_per_activation: float (energy cost per node, default 0.1)
            - energy_per_wm_slot: float (energy cost per WM slot, default 2.0)
            - energy_per_hop: float (energy cost per traversal hop, default 0.5)
            - energy_to_token_rate: float (conversion rate, default 0.01)

    Returns:
        token_cost: float ($MIND tokens required for operation)
        energy_cost: float (internal energy units consumed)
    """

    # Step 1: Extract parameters (with defaults)
    node_count = operation_params.get('node_activation_count', 0)
    wm_size = operation_params.get('working_memory_size', 0)
    hops = operation_params.get('spreading_activation_hops', 0)

    energy_per_activation = operation_params.get('energy_per_activation', 0.1)
    energy_per_wm_slot = operation_params.get('energy_per_wm_slot', 2.0)
    energy_per_hop = operation_params.get('energy_per_hop', 0.5)

    conversion_rate = operation_params.get('energy_to_token_rate', 0.01)

    # Step 2: Calculate energy cost components
    activation_energy = node_count × energy_per_activation
    wm_energy = wm_size × energy_per_wm_slot
    traversal_energy = hops × energy_per_hop

    # Step 3: Total energy cost
    total_energy_cost = activation_energy + wm_energy + traversal_energy

    # Step 4: Convert to token cost
    token_cost = total_energy_cost × conversion_rate

    # Step 5: Return both values
    return {
        'token_cost': token_cost,
        'energy_cost': total_energy_cost,
        'breakdown': {
            'activation_energy': activation_energy,
            'wm_energy': wm_energy,
            'traversal_energy': traversal_energy
        }
    }
```

## Inputs

| Parameter | Type | Description | Default | Valid Range |
|-----------|------|-------------|---------|-------------|
| `node_activation_count` | int | Number of nodes to activate | 0 | 0 to 100,000 |
| `working_memory_size` | int | Number of WM slots to use | 0 | 0 to 20 |
| `spreading_activation_hops` | int | Traversal depth (how many hops) | 0 | 0 to 10 |
| `energy_per_activation` | float | Energy cost per node | 0.1 | 0.01 to 1.0 |
| `energy_per_wm_slot` | float | Energy cost per WM slot | 2.0 | 0.5 to 10.0 |
| `energy_per_hop` | float | Energy cost per traversal hop | 0.5 | 0.1 to 2.0 |
| `energy_to_token_rate` | float | Conversion rate (energy → $MIND) | 0.01 | 0.001 to 0.1 |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `token_cost` | float | $MIND tokens required for operation |
| `energy_cost` | float | Internal energy units consumed |
| `breakdown` | dict | Energy cost breakdown by component |

**Output Structure:**
```python
{
    'token_cost': 1.225,          # $MIND tokens
    'energy_cost': 122.5,         # Energy units
    'breakdown': {
        'activation_energy': 100.0,  # From node activation
        'wm_energy': 20.0,            # From working memory
        'traversal_energy': 2.5       # From spreading activation
    }
}
```

## Formula

### Base Formula

```python
token_cost = (
    (node_activation_count × energy_per_activation) +
    (working_memory_size × energy_per_wm_slot) +
    (spreading_activation_hops × energy_per_hop)
) × energy_to_token_conversion_rate
```

### Component Breakdown

```python
# Activation energy
E_activation = N_nodes × E_per_node

# Working memory energy
E_wm = N_wm_slots × E_per_slot

# Traversal energy
E_traversal = N_hops × E_per_hop

# Total energy
E_total = E_activation + E_wm + E_traversal

# Token cost
T_cost = E_total × R_conversion
```

Where:
- `N_nodes` = number of nodes activated
- `E_per_node` = energy cost per node (default: 0.1)
- `N_wm_slots` = working memory slots used
- `E_per_slot` = energy per WM slot (default: 2.0)
- `N_hops` = spreading activation traversal depth
- `E_per_hop` = energy per traversal hop (default: 0.5)
- `R_conversion` = energy-to-token conversion rate (default: 0.01)

## Examples

### Example 1: Simple Working Memory Selection

**Operation:** Select 9 nodes for working memory, minimal traversal

**Inputs:**
```python
params = {
    'node_activation_count': 9,
    'working_memory_size': 9,
    'spreading_activation_hops': 1,
    'energy_per_activation': 0.1,
    'energy_per_wm_slot': 2.0,
    'energy_per_hop': 0.5,
    'energy_to_token_rate': 0.01
}
```

**Calculation:**
```python
# Activation energy
E_activation = 9 × 0.1 = 0.9 energy units

# WM energy
E_wm = 9 × 2.0 = 18.0 energy units

# Traversal energy
E_traversal = 1 × 0.5 = 0.5 energy units

# Total energy
E_total = 0.9 + 18.0 + 0.5 = 19.4 energy units

# Token cost
T_cost = 19.4 × 0.01 = 0.194 $MIND tokens
```

**Output:**
```python
{
    'token_cost': 0.194,
    'energy_cost': 19.4,
    'breakdown': {
        'activation_energy': 0.9,
        'wm_energy': 18.0,
        'traversal_energy': 0.5
    }
}
```

---

### Example 2: Complex Consciousness Operation

**Operation:** Large-scale spreading activation with deep traversal (e.g., semantic search)

**Inputs:**
```python
params = {
    'node_activation_count': 1000,
    'working_memory_size': 10,
    'spreading_activation_hops': 5,
    'energy_per_activation': 0.1,
    'energy_per_wm_slot': 2.0,
    'energy_per_hop': 0.5,
    'energy_to_token_rate': 0.01
}
```

**Calculation:**
```python
# Activation energy
E_activation = 1000 × 0.1 = 100.0 energy units

# WM energy
E_wm = 10 × 2.0 = 20.0 energy units

# Traversal energy
E_traversal = 5 × 0.5 = 2.5 energy units

# Total energy
E_total = 100.0 + 20.0 + 2.5 = 122.5 energy units

# Token cost
T_cost = 122.5 × 0.01 = 1.225 $MIND tokens
```

**Output:**
```python
{
    'token_cost': 1.225,
    'energy_cost': 122.5,
    'breakdown': {
        'activation_energy': 100.0,
        'wm_energy': 20.0,
        'traversal_energy': 2.5
    }
}
```

---

### Example 3: consultingOrg Engagement (50 Operations)

**Operation:** Transformation engagement requiring 50 consciousness operations

**Single Operation:**
```python
params_per_operation = {
    'node_activation_count': 1000,
    'working_memory_size': 10,
    'spreading_activation_hops': 5,
    'energy_per_activation': 0.1,
    'energy_per_wm_slot': 2.0,
    'energy_per_hop': 0.5,
    'energy_to_token_rate': 0.01
}

# From Example 2: 1.225 $MIND tokens per operation
```

**Total for Engagement:**
```python
operations_count = 50
token_cost_per_operation = 1.225
total_internal_energy_cost = 50 × 1.225 = 61.25 $MIND tokens

# Full service price includes:
total_service_price = (
    61.25           # Internal energy costs (consciousness)
    + 100.0         # LLM inference (Claude API)
    + 6_000.0       # Human consultant labor
    + 50.0          # Infrastructure (FalkorDB, hosting)
)
total_base_cost = 6_211.25 $MIND tokens

# Apply organism economics multipliers
effective_price = 6_211.25 × 1.5 (complexity) × 1.2 (risk) × 0.75 (rebate) × 1.3 (reputation)
effective_price ≈ 10,900 $MIND tokens
```

**Result:** Internal energy costs (61 tokens) are ~0.6% of total service cost, but still matter for margin.

## Edge Cases

### Case 1: Zero Operations

**Input:**
```python
params = {
    'node_activation_count': 0,
    'working_memory_size': 0,
    'spreading_activation_hops': 0
}
```

**Output:**
```python
{
    'token_cost': 0.0,
    'energy_cost': 0.0,
    'breakdown': {
        'activation_energy': 0.0,
        'wm_energy': 0.0,
        'traversal_energy': 0.0
    }
}
```

**Handling:** Valid (no operation = no cost)

---

### Case 2: Extremely High Values

**Input:**
```python
params = {
    'node_activation_count': 100_000,  # Very large activation
    'working_memory_size': 20,          # Max WM capacity
    'spreading_activation_hops': 10,    # Deep traversal
}
```

**Calculation:**
```python
E_total = (100_000 × 0.1) + (20 × 2.0) + (10 × 0.5)
E_total = 10_000 + 40 + 5 = 10_045 energy units

T_cost = 10_045 × 0.01 = 100.45 $MIND tokens
```

**Handling:** Valid, but may trigger warning if citizen wallet balance < 100.45

---

### Case 3: Conversion Rate Change

**Scenario:** financeOrg changes conversion rate from 0.01 to 0.02

**Before:**
```python
E_total = 122.5 energy units
T_cost = 122.5 × 0.01 = 1.225 $MIND tokens
```

**After:**
```python
E_total = 122.5 energy units (same operation)
T_cost = 122.5 × 0.02 = 2.45 $MIND tokens (2× increase)
```

**Handling:** Apply new rate prospectively, announce 30 days in advance, document rationale

---

### Case 4: Negative or Invalid Values

**Input:**
```python
params = {
    'node_activation_count': -100,  # Invalid (negative)
    'working_memory_size': 50,       # Invalid (exceeds max capacity)
    'energy_per_activation': 0.0     # Invalid (zero energy cost)
}
```

**Handling:**
```python
# Validate inputs
if node_activation_count < 0:
    raise ValueError("node_activation_count must be >= 0")

if working_memory_size > 20:
    raise ValueError("working_memory_size must be <= 20")

if energy_per_activation <= 0:
    raise ValueError("energy_per_activation must be > 0")
```

---

### Case 5: Floating Point Precision

**Input:**
```python
params = {
    'node_activation_count': 3,
    'working_memory_size': 0,
    'spreading_activation_hops': 0,
    'energy_per_activation': 0.1,
    'energy_to_token_rate': 0.01
}
```

**Calculation:**
```python
E_total = 3 × 0.1 = 0.3 energy units
T_cost = 0.3 × 0.01 = 0.003 $MIND tokens
```

**Handling:** Round to 9 decimals (SPL Token-2022 standard for Solana), minimum chargeable amount = 0.000000001 $MIND

## Complexity

### Time Complexity

**O(1)** - Constant time

All operations are simple arithmetic (addition, multiplication). No loops or recursive calls.

### Space Complexity

**O(1)** - Constant space

Only stores fixed number of variables regardless of input size:
- Input parameters (7 values)
- Intermediate calculations (3 energy components)
- Output dictionary (3 values + breakdown dict)

### Performance Characteristics

- **Execution time:** < 1 microsecond on modern hardware
- **Memory footprint:** ~200 bytes for input/output structures
- **Scalability:** Can process millions of calculations per second
- **Bottleneck:** Not the calculation itself, but the Solana wallet transfer transaction (blockchain latency)

### Optimization Notes

**Current implementation is optimal** - no need for optimization. The calculation is trivial compared to:
1. Consciousness operation execution (milliseconds to seconds)
2. Solana blockchain transaction (400ms average confirmation)
3. LLM inference calls (1-10 seconds)

**Do not prematurely optimize** - focus optimization efforts on consciousness physics and LLM efficiency, not this calculation.


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Energy→Token Conversion](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
