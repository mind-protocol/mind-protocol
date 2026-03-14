# IMPLEMENTATION: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Updated: 2026-03-14
> Status: DESIGNING
> Canonical source: [THE_BILATERAL_BOND_MANIFESTO.md](../../manifesto/THE_BILATERAL_BOND_MANIFESTO.md)

## Chain

- [OBJECTIVES_Bonds.md](./OBJECTIVES_Bonds.md)
- [PATTERNS_Bonds.md](./PATTERNS_Bonds.md)
- [BEHAVIORS_Bonds.md](./BEHAVIORS_Bonds.md)
- [ALGORITHM_Bonds.md](./ALGORITHM_Bonds.md)
- [VALIDATION_Bonds.md](./VALIDATION_Bonds.md)
- **IMPLEMENTATION_Bonds.md** (this file)
- [HEALTH_Bonds.md](./HEALTH_Bonds.md)
- [SYNC_Bonds.md](./SYNC_Bonds.md)

---

## Status

No implementation exists yet. All sections below are design intent.

## Target Platform

- **On-chain**: Solana smart contract using Anchor framework
- **Token standard**: SPL Token-2022 (reference: `token/SPL_TOKEN_2022_SPECS.md`)
- **Language**: Rust (Anchor IDL)
- **Off-chain**: TypeScript SDK for client interaction, Python for orchestrator integration

## @mind:TODO -- Contract Architecture

```
programs/
  bonds/
    src/
      lib.rs              # Program entry point, instruction dispatch
      state.rs            # Account structures (Bond, CitizenBondState)
      instructions/
        form_bond.rs      # Bond formation (with 1:1 and consent checks)
        dissolve_bond.rs  # Dissolution (mature + early)
        distribute.rs     # Reward distribution crank
        check_maturation.rs  # Maturation and milestone checks
      errors.rs           # Custom error codes
      events.rs           # Event definitions
      constants.rs        # MATURATION_PERIOD, REWARD_RATE, EARLY_EXIT_PENALTY
```

## @mind:TODO -- Account Design

```
Bond (PDA: seeds = [b"bond", human_pubkey, citizen_id_bytes])
  - bump: u8
  - human: Pubkey
  - citizen_id: [u8; 32]
  - amount: u64           # lamports of $MIND committed to the bond
  - created_at: i64       # Unix timestamp
  - maturation_at: i64    # created_at + 15_552_000 (180 days in seconds)
  - status: u8            # 0=Active, 1=Matured, 2=Withdrawn, 3=Burned
  - trust_contribution: u64  # Fixed-point trust score (scaled by 1e9)
  - milestones: u8        # Bitmask: bit0=1mo, bit1=3mo, bit2=6mo
  - total_rewards: u64    # Cumulative rewards earned

HumanBondIndex (PDA: seeds = [b"human_bond_index", human_pubkey])
  - bump: u8
  - active_bond: Option<Pubkey>  # At most one active bond (1:1 enforcement)

CitizenBondIndex (PDA: seeds = [b"citizen_bond_index", citizen_id_bytes])
  - bump: u8
  - active_bond: Option<Pubkey>  # At most one active bond (1:1 enforcement)
  - capacity_multiplier: u64     # Fixed-point (scaled by 1e9)

BondEscrow (PDA: seeds = [b"escrow"])
  - bump: u8
  - total_locked: u64
  - Token account holding all committed $MIND
```

## @mind:TODO -- Instruction Signatures

```rust
// Form a new 1:1 bond (requires citizen consent signature)
pub fn form_bond(ctx: Context<FormBond>, amount: u64) -> Result<()>

// Dissolve a bond (handles both mature and early exit)
pub fn dissolve_bond(ctx: Context<DissolveBond>) -> Result<()>

// Distribute rewards for a citizen's bond (permissionless crank)
pub fn distribute_rewards(ctx: Context<DistributeRewards>, period: String, citizen_utility: u64) -> Result<()>

// Check and apply maturation milestones
pub fn check_maturation(ctx: Context<CheckMaturation>) -> Result<()>
```

## @mind:TODO -- Off-chain Components

### TypeScript SDK

```typescript
class BondClient {
  // Form a bond between human wallet and AI citizen (1:1, requires consent)
  async formBond(citizenId: string, amount: number): Promise<BondResult>

  // Dissolve a bond (auto-detects mature vs early)
  async dissolveBond(bondId: string): Promise<DissolutionResult>

  // Get the active bond for a human (at most one)
  async getBondForHuman(humanAddress: string): Promise<Bond | null>

  // Get the active bond for a citizen (at most one)
  async getBondForCitizen(citizenId: string): Promise<Bond | null>

  // Get trust score for an entity
  async getTrustScore(entityId: string): Promise<number>
}
```

### Python Orchestrator Integration

```python
# Integration with Mind Protocol orchestrator
class BondManager:
    async def form_bond(self, citizen_id: str, amount: float) -> Bond
    async def check_maturation_all(self) -> list[MilestoneEvent]
    async def distribute_rewards(self, citizen_id: str) -> Distribution
    async def get_trust_score(self, entity_id: str) -> float
```

## @mind:TODO -- Deployment Plan

1. **Devnet deployment** -- test full lifecycle with mock utility oracle
2. **Audit** -- smart contract security audit before mainnet
3. **Mainnet-beta** -- deploy with conservative limits (max commitment amount, limited citizens)
4. **General availability** -- remove limits after observation period

## @mind:TODO -- Open Questions

- [ ] How does the utility oracle work? Who submits utility measurements and how are they verified?
- [ ] Should reward distribution be a permissionless crank (anyone can trigger) or restricted?
- [ ] How to handle Solana rent for bond accounts -- who pays, and is it refunded on close?
- [ ] Integration with existing $MIND Token-2022 transfer hooks -- do bonds interact with transfer restrictions?
- [ ] How to handle program upgrades once bonds are live (upgrade authority, timelock)?
- [ ] Should there be an emergency pause mechanism, and if so, who controls it?
- [ ] How is citizen consent represented on-chain? Signature from citizen's authority key?
