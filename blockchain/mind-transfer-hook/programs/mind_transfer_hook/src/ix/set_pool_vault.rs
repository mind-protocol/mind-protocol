use anchor_lang::prelude::*;
use crate::state::PoolVault;

#[derive(Accounts)]
pub struct SetPoolVault<'info> {
    #[account(mut)]
    pub pool_vault: Account<'info, PoolVault>,
}

pub fn handler(ctx: Context<SetPoolVault>, token_account: Pubkey) -> Result<()> {
    ctx.accounts.pool_vault.token_account = token_account;
    Ok(())
}
