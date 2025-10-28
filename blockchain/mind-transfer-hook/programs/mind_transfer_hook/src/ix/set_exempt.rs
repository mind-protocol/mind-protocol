use anchor_lang::prelude::*;
use crate::state::Exempt;

#[derive(Accounts)]
pub struct SetExempt<'info> {
    #[account(mut)]
    pub exempt: Account<'info, Exempt>,
}

pub fn handler(ctx: Context<SetExempt>, roles: u8) -> Result<()> {
    ctx.accounts.exempt.roles = roles;
    Ok(())
}
