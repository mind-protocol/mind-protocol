use anchor_lang::prelude::*;
use crate::state::{Policy, Unlock, AllowedProgram, PoolVault};

#[derive(Accounts)]
pub struct InitMintScope<'info> {
    #[account(mut)]
    pub policy: Account<'info, Policy>,
    #[account(mut)]
    pub unlock: Account<'info, Unlock>,
    #[account(mut)]
    pub allowed_program: Account<'info, AllowedProgram>,
    #[account(mut)]
    pub pool_vault: Account<'info, PoolVault>,
}

pub fn handler(_ctx: Context<InitMintScope>) -> Result<()> {
    Ok(())
}
