use anchor_lang::prelude::*;
#[error_code]
pub enum ErrorCode {
    #[msg("Transfers paused")] Paused,
    #[msg("Sells disabled until unlock")] SellsDisabled,
    #[msg("Program not allowed during lock")] ProgramNotAllowed,
}
