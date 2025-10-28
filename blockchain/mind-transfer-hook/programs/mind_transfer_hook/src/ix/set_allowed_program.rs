use anchor_lang::prelude::*;
use crate::state::AllowedProgram;

#[derive(Accounts)]
pub struct SetAllowedProgram<'info> {
    #[account(mut)]
    pub allowed_program: Account<'info, AllowedProgram>,
}

pub fn handler(ctx: Context<SetAllowedProgram>, program_id: Pubkey) -> Result<()> {
    ctx.accounts.allowed_program.program_id = program_id;
    Ok(())
}
