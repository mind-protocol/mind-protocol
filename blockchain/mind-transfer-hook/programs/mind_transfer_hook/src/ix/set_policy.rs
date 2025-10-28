use anchor_lang::prelude::*;
use crate::state::Policy;

#[derive(Accounts)]
pub struct SetPolicy<'info> {
    #[account(mut)]
    pub policy: Account<'info, Policy>,
}

pub fn handler(ctx: Context<SetPolicy>, paused: bool) -> Result<()> {
    let p = &mut ctx.accounts.policy;
    p.paused = paused;
    Ok(())
}
