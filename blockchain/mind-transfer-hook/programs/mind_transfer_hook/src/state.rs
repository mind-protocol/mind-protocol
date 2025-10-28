use anchor_lang::prelude::*;

#[account]
pub struct Admin {
    pub bump: u8,
}

#[account]
pub struct Policy {
    pub bump: u8,
    pub paused: bool,
}

#[account]
pub struct Unlock {
    pub bump: u8,
    pub unlock_ts: i64,
}

#[account]
pub struct Exempt {
    pub bump: u8,
    /// bitmask of roles; any non-zero = exempt
    pub roles: u8,
}
impl Exempt {
    pub fn any(&self) -> bool { self.roles != 0 }
}

#[account]
pub struct AllowedProgram {
    pub bump: u8,
    pub program_id: Pubkey,
}

#[account]
pub struct PoolVault {
    pub bump: u8,
    pub token_account: Pubkey, // Raydium pool's MIND token account (vault)
}
