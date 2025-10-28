use anchor_lang::prelude::*;
use crate::state::Unlock;

#[derive(Accounts)]
pub struct SetUnlock<'info> {
    #[account(mut)]
    pub unlock: Account<'info, Unlock>,
}

pub fn handler(ctx: Context<SetUnlock>, ts: i64) -> Result<()> {
    ctx.accounts.unlock.unlock_ts = ts;
    Ok(())
}
