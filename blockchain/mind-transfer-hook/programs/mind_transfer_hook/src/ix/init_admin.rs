use anchor_lang::prelude::*;
use crate::state::Admin;

#[derive(Accounts)]
pub struct InitAdmin<'info> {
    #[account(mut)]
    pub admin_pda: Account<'info, Admin>,
}

pub fn handler(_ctx: Context<InitAdmin>) -> Result<()> {
    Ok(())
}
