use anchor_lang::prelude::*;

pub mod error;
pub mod state;
pub mod ix;     // ← your instructions module (renamed folder `ix`)
pub mod utils;

use crate::error::ErrorCode;

declare_id!("94pUHcJGwY3mjAH6R3thJ85qo8BNPjHnXLrKjem952mc");

/// sha256("spl-transfer-hook-interface:execute")[..8] LE bytes
/// This is the native Token-2022 hook entrypoint tag. Route it via `fallback`.
pub const EXECUTE_IX_TAG_LE: [u8; 8] = [105, 37, 101, 197, 75, 251, 102, 26];

#[program]
pub mod mind_transfer_hook {
    use super::*;

    /// The actual hook logic the Token-2022 program wants to call.
    /// Keep this name EXACTLY `transfer_hook` so Anchor generates `__global::transfer_hook`.
    pub fn transfer_hook(ctx: Context<ix::evaluate::Evaluate>, amount: u64) -> Result<()> {
        ix::evaluate::handler(ctx, amount)
    }

    // admin scaffolding you already had:
    pub fn init_admin(ctx: Context<ix::init_admin::InitAdmin>) -> Result<()> {
        ctx.accounts.admin_pda.bump = ctx.bumps.admin_pda;
        Ok(())
    }
    pub fn init_mint_scope(ctx: Context<ix::init_mint_scope::InitMintScope>) -> Result<()> {
        ctx.accounts.policy.bump          = ctx.bumps.policy;
        ctx.accounts.unlock.bump          = ctx.bumps.unlock;
        ctx.accounts.allowed_program.bump = ctx.bumps.allowed_program;
        ctx.accounts.pool_vault.bump      = ctx.bumps.pool_vault;
        Ok(())
    }
    pub fn set_policy(ctx: Context<ix::set_policy::SetPolicy>, paused: bool) -> Result<()> {
        ix::set_policy::handler(ctx, paused)
    }
    pub fn set_unlock(ctx: Context<ix::set_unlock::SetUnlock>, unlock_ts: i64) -> Result<()> {
        ix::set_unlock::handler(ctx, unlock_ts)
    }
    pub fn set_exempt(ctx: Context<ix::set_exempt::SetExempt>, roles: u8) -> Result<()> {
        ix::set_exempt::handler(ctx, roles)
    }
    pub fn set_allowed_program(
        ctx: Context<ix::set_allowed_program::SetAllowedProgram>,
        program_id: Pubkey,
    ) -> Result<()> {
        ix::set_allowed_program::handler(ctx, program_id)
    }
    pub fn set_pool_vault(
        ctx: Context<ix::set_pool_vault::SetPoolVault>,
        token_account: Pubkey,
    ) -> Result<()> {
        ix::set_pool_vault::handler(ctx, token_account)
    }
}

/// Anchor fallback: route native `execute` calls into our Anchor entry
/// Matches the official pattern used by community examples.
#[cfg(not(feature = "no-entrypoint"))]
#[inline(never)]
pub fn fallback(program_id: &Pubkey, accounts: &[AccountInfo], mut ix_data: &[u8]) -> Result<()> {
    // extract the first 8 bytes (discriminator)
    let mut sighash: [u8; 8] = [0; 8];
    sighash.copy_from_slice(&ix_data[..8]);
    ix_data = &ix_data[8..];

    match sighash {
        EXECUTE_IX_TAG_LE => {
            // call the generated Anchor dispatcher for transfer_hook
            // (this symbol name is produced by #[program] above)
            __private::__global::transfer_hook(program_id, accounts, ix_data)
        }
        _ => Err(ProgramError::InvalidInstructionData.into()),
    }
}
