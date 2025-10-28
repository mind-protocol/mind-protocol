use anchor_lang::prelude::*;
use solana_program::sysvar::instructions as ix_sysvar;

/// Returns the previous program_id from the Instructions sysvar, if any.
/// Pass the AccountInfo of the instructions sysvar.
pub fn prev_program_id(ix_ai: &AccountInfo) -> Option<Pubkey> {
    if let Ok(idx) = ix_sysvar::load_current_index_checked(ix_ai) {
        if idx == 0 { return None; }
        if let Ok(prev) = ix_sysvar::load_instruction_at_checked((idx - 1) as usize, ix_ai) {
            return Some(prev.program_id);
        }
    }
    None
}
