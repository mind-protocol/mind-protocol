# IMPLEMENTATION: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Status: DRAFT

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
        create_bond.rs    # Bond creation instruction
        withdraw_bond.rs  # Withdrawal (mature + early)
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
  - amount: u64           # lamports of $MIND
  - created_at: i64       # Unix timestamp
  - maturation_at: i64    # created_at + 15_552_000 (180 days in seconds)
  - status: u8            # 0=Active, 1=Matured, 2=Withdrawn, 3=Burned
  - trust_contribution: u64  # Fixed-point trust score (scaled by 1e9)
  - milestones: u8        # Bitmask: bit0=1mo, bit1=3mo, bit2=6mo
  - total_rewards: u64    # Cumulative rewards earned

CitizenBondState (PDA: seeds = [b"citizen_bonds", citizen_id_bytes])
  - bump: u8
  - citizen_id: [u8; 32]
  - total_bonded: u64
  - active_count: u32
  - capacity_multiplier: u64  # Fixed-point (scaled by 1e9)

BondEscrow (PDA: seeds = [b"escrow"])
  - bump: u8
  - total_locked: u64
  - Token account holding all staked $MIND
```

## @mind:TODO -- Instruction Signatures

```rust
// Create a new bond
pub fn create_bond(ctx: Context<CreateBond>, amount: u64) -> Result<()>

// Withdraw a bond (handles both mature and early exit)
pub fn withdraw_bond(ctx: Context<WithdrawBond>) -> Result<()>

// Distribute rewards for a citizen's bonds (permissionless crank)
pub fn distribute_rewards(ctx: Context<DistributeRewards>, period: String, citizen_utility: u64) -> Result<()>

// Check and apply maturation milestones
pub fn check_maturation(ctx: Context<CheckMaturation>) -> Result<()>
```

## @mind:TODO -- Off-chain Components

### TypeScript SDK

```typescript
class BondClient {
  // Create a bond between human wallet and AI citizen
  async createBond(citizenId: string, amount: number): Promise<BondResult>

  // Withdraw a bond (auto-detects mature vs early)
  async withdrawBond(bondId: string): Promise<WithdrawalResult>

  // Get all bonds for a human
  async getBondsForHuman(humanAddress: string): Promise<Bond[]>

  // Get all bonds on a citizen
  async getBondsForCitizen(citizenId: string): Promise<Bond[]>

  // Get trust score for an entity
  async getTrustScore(entityId: string): Promise<number>
}
```

### Python Orchestrator Integration

```python
# Integration with Mind Protocol orchestrator
class BondManager:
    async def create_bond(self, citizen_id: str, amount: float) -> Bond
    async def check_maturation_all(self) -> list[MilestoneEvent]
    async def distribute_rewards(self, citizen_id: str) -> list[Distribution]
    async def get_trust_score(self, entity_id: str) -> float
```

## @mind:TODO -- Deployment Plan

1. **Devnet deployment** -- test full lifecycle with mock utility oracle
2. **Audit** -- smart contract security audit before mainnet
3. **Mainnet-beta** -- deploy with conservative limits (max bond amount, limited citizens)
4. **General availability** -- remove limits after observation period

## @mind:TODO -- Open Questions

- [ ] How does the utility oracle work? Who submits utility measurements and how are they verified?
- [ ] Should reward distribution be a permissionless crank (anyone can trigger) or restricted?
- [ ] How to handle Solana rent for bond accounts -- who pays, and is it refunded on close?
- [ ] Integration with existing $MIND Token-2022 transfer hooks -- do bonds interact with transfer restrictions?
- [ ] How to handle program upgrades once bonds are live (upgrade authority, timelock)?
- [ ] Should there be an emergency pause mechanism, and if so, who controls it?
