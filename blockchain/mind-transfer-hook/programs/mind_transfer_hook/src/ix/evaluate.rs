use anchor_lang::prelude::*;
use solana_program::sysvar::instructions as ix_sysvar;
use crate::{ErrorCode, state::{Policy, Unlock, Exempt, AllowedProgram, PoolVault}, utils::prev_program_id};
#[derive(Accounts)]
pub struct Evaluate<'info> {
    /// CHECK: passed by token-2022
    pub from_token_account: UncheckedAccount<'info>,
    /// CHECK: passed by token-2022
    pub to_token_account: UncheckedAccount<'info>,
    /// Mint-scoped PDAs
    /// CHECK: policy pda
    #[account(mut)]
    pub policy: Account<'info, Policy>,
    /// CHECK: unlock pda
    pub unlock: Account<'info, Unlock>,
    /// CHECK: exemptions
    pub exempt_from: Account<'info, Exempt>,
    /// CHECK: exemptions
    pub exempt_to: Account<'info, Exempt>,
    /// CHECK: allowed program (optional; may be a default dummy account when none)
    pub allowed_program: Account<'info, AllowedProgram>,
    /// CHECK: pool vault
    pub pool_vault: Account<'info, PoolVault>,
    /// SYSVARS
    /// CHECK: instruction sysvar
    #[account(address = solana_program::sysvar::instructions::ID)]
    pub ix_sysvar: UncheckedAccount<'info>,
}
pub fn handler(ctx: Context<Evaluate>, _amount: u64) -> Result<()> {
    let policy = &ctx.accounts.policy;
    let unlock = &ctx.accounts.unlock;
    let exempt_from = &ctx.accounts.exempt_from;
    let exempt_to = &ctx.accounts.exempt_to;
    let pool_vault = &ctx.accounts.pool_vault;
    if policy.paused && !exempt_from.any() { return err!(ErrorCode::Paused); }
    // Exemptions always allow
    if exempt_from.any() || exempt_to.any() { return Ok(()); }
    let clock = Clock::get()?;
let ix_ai = &ctx.accounts.ix_sysvar.to_account_info();
    let caller = crate::utils::prev_program_id(ix_ai);
let ix_ai = &ctx.accounts.ix_sysvar.to_account_info();
    // Before unlock: block sells to pool vault, allow buys from pool vault, allow P2P
    if clock.unix_timestamp < unlock.unlock_ts {
        let to_is_vault = ctx.accounts.to_token_account.key() == pool_vault.token_account;
        let from_is_vault = ctx.accounts.from_token_account.key() == pool_vault.token_account;
        // SELL: user -> pool vault (block)
        if to_is_vault { return err!(ErrorCode::SellsDisabled); }
        // BUY: pool vault -> user (allow) only if call came via allowed AMM program (optional)
        if from_is_vault {
            if caller.is_some() && caller.unwrap() == ctx.accounts.allowed_program.program_id { return Ok(()); }
            // If you want buys to work even without checking caller, uncomment next line:
            // return Ok(());
            return err!(ErrorCode::ProgramNotAllowed);
        }
        // P2P: direct wallet call (no caller program) -> allow
        if caller.is_none() { return Ok(()); }
        // Other CPIs during lock -> block
        return err!(ErrorCode::ProgramNotAllowed);
    }
    // After unlock: allow
    Ok(())

}
