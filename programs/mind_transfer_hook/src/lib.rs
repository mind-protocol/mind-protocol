// programs/mind_transfer_hook/src/lib.rs
//
// $MIND TransferHook Program
// ===========================
//
// This program is called on EVERY $MIND token transfer.
// It implements custom logic for the Mind Protocol economy:
//
// 1. Layer-based fees (1-5% based on sender/receiver layers)
// 2. Dormancy checks (block transfers from dormant accounts)
// 3. Transfer logging (for trust score calculation)
//
// IMPORTANT: This program must be deployed BEFORE creating the $MIND token.
// The token's TransferHook extension points to this program's ID.
//
// Docs: docs/economy/token/SPL_TOKEN_2022_SPECS.md

use anchor_lang::prelude::*;
use anchor_spl::token_interface::{Mint, TokenAccount};

// Program ID - will be set after initial deployment
// Update this after running `anchor deploy`
declare_id!("325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD");

/// $MIND TransferHook Program
///
/// Called automatically on every transfer of $MIND tokens.
/// Validates transfer conditions and logs for off-chain processing.
#[program]
pub mod mind_transfer_hook {
    use super::*;

    /// Initialize the hook with extra account metas
    ///
    /// This is called once during token setup to define which
    /// additional accounts the hook needs during transfers.
    pub fn initialize_extra_account_meta_list(
        ctx: Context<InitializeExtraAccountMetaList>,
    ) -> Result<()> {
        // For now, we don't need extra accounts
        // Future: Add PDA for transfer stats, layer registry, etc.
        msg!("MIND TransferHook: Extra account metas initialized");
        Ok(())
    }

    /// Main transfer hook - called on every $MIND transfer
    ///
    /// This function executes custom logic:
    /// 1. Checks if sender is dormant (blocks transfer if so)
    /// 2. Calculates layer-based fees (if crossing layers)
    /// 3. Logs transfer for off-chain trust score calculation
    ///
    /// Note: The actual fee is collected via TransferFeeConfig extension.
    /// This hook handles additional validation and logging.
    pub fn transfer_hook(ctx: Context<TransferHook>, amount: u64) -> Result<()> {
        let source = &ctx.accounts.source;
        let destination = &ctx.accounts.destination;
        let mint = &ctx.accounts.mint;

        // Log the transfer for off-chain indexing
        msg!(
            "MIND Transfer: {} lamports ({} tokens)",
            amount,
            amount as f64 / 1_000_000_000.0
        );
        msg!("  From: {}", source.key());
        msg!("  To: {}", destination.key());
        msg!("  Mint: {}", mint.key());

        // === VALIDATION CHECKS ===

        // 1. Check sender is not dormant
        // TODO: Implement dormancy check via PDA lookup
        // For now, all transfers are allowed
        // Future: ctx.accounts.sender_status.is_dormant -> Error::SenderDormant

        // 2. Verify transfer amount is reasonable
        // Minimum transfer: 1 lamport (0.000000001 MIND)
        require!(amount > 0, MindTransferError::ZeroTransfer);

        // 3. Layer-based fee calculation (informational)
        // The actual fee is collected by TransferFeeConfig extension
        // This is for logging/verification only
        // TODO: Read sender/receiver layers from PDAs and log additional fee

        // === EMIT EVENTS FOR OFF-CHAIN PROCESSING ===

        emit!(TransferEvent {
            source: source.key(),
            destination: destination.key(),
            amount,
            timestamp: Clock::get()?.unix_timestamp,
        });

        msg!("MIND TransferHook: Transfer validated and logged");
        Ok(())
    }

}

// =============================================================================
// ACCOUNTS
// =============================================================================

#[derive(Accounts)]
pub struct InitializeExtraAccountMetaList<'info> {
    #[account(mut)]
    pub payer: Signer<'info>,

    /// The mint account (must be Token 2022 with TransferHook extension)
    pub mint: InterfaceAccount<'info, Mint>,

    /// PDA that stores extra account metas for the hook
    /// CHECK: Initialized by this instruction
    #[account(
        init,
        payer = payer,
        space = 8 + ExtraAccountMetaList::INIT_SPACE,
        seeds = [b"extra-account-metas", mint.key().as_ref()],
        bump
    )]
    pub extra_account_metas: Account<'info, ExtraAccountMetaList>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct TransferHook<'info> {
    /// Source token account (sender)
    #[account(token::mint = mint)]
    pub source: InterfaceAccount<'info, TokenAccount>,

    /// The $MIND mint
    pub mint: InterfaceAccount<'info, Mint>,

    /// Destination token account (receiver)
    #[account(token::mint = mint)]
    pub destination: InterfaceAccount<'info, TokenAccount>,

    /// Owner of the source account (signer of the transfer)
    /// CHECK: Validated by Token 2022 program
    pub owner: UncheckedAccount<'info>,

    /// Extra account metas PDA
    /// CHECK: Seeds validated
    #[account(
        seeds = [b"extra-account-metas", mint.key().as_ref()],
        bump
    )]
    pub extra_account_metas: UncheckedAccount<'info>,

    // === FUTURE: Additional accounts for layer/dormancy tracking ===
    // pub sender_status: Account<'info, CitizenStatus>,
    // pub receiver_status: Account<'info, CitizenStatus>,
    // pub layer_registry: Account<'info, LayerRegistry>,
}

// =============================================================================
// STATE
// =============================================================================

/// Stores the extra account metas required by the transfer hook
#[account]
#[derive(InitSpace)]
pub struct ExtraAccountMetaList {
    /// Bump seed for the PDA
    pub bump: u8,
    /// Reserved for future use
    pub reserved: [u8; 7],
}

impl ExtraAccountMetaList {
    pub const INIT_SPACE: usize = 1 + 7; // bump + reserved
}

/// Citizen status account (future implementation)
#[account]
pub struct CitizenStatus {
    /// Citizen ID (from L4 Registry)
    pub citizen_id: Pubkey,
    /// Last activity timestamp
    pub last_activity: i64,
    /// Is account dormant?
    pub is_dormant: bool,
    /// Layer this citizen operates in (1-4)
    pub layer: u8,
    /// Transfer count (for trust calculation)
    pub transfer_count: u64,
    /// Total transferred (for trust calculation)
    pub total_transferred: u64,
}

// =============================================================================
// EVENTS
// =============================================================================

/// Emitted on every successful transfer
#[event]
pub struct TransferEvent {
    pub source: Pubkey,
    pub destination: Pubkey,
    pub amount: u64,
    pub timestamp: i64,
}

/// Emitted when a transfer is blocked
#[event]
pub struct TransferBlockedEvent {
    pub source: Pubkey,
    pub destination: Pubkey,
    pub amount: u64,
    pub reason: String,
}

// =============================================================================
// ERRORS
// =============================================================================

#[error_code]
pub enum MindTransferError {
    #[msg("Sender account is dormant - reactivate by signing a transaction")]
    SenderDormant,

    #[msg("Transfer amount must be greater than zero")]
    ZeroTransfer,

    #[msg("Insufficient layer fee - additional fee required for cross-layer transfer")]
    InsufficientLayerFee,

    #[msg("Destination account not registered in Mind Protocol")]
    UnregisteredDestination,

    #[msg("Transfer rate limit exceeded")]
    RateLimitExceeded,
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/// Calculate layer-based fee (1% per layer crossed)
///
/// Examples:
/// - L1 -> L1: 0% (same layer)
/// - L1 -> L2: 1%
/// - L1 -> L3: 2%
/// - L1 -> L4: 3%
pub fn calculate_layer_fee(
    source_layer: u8,
    dest_layer: u8,
    amount: u64,
) -> u64 {
    let layer_gap = (source_layer as i8 - dest_layer as i8).unsigned_abs();
    let fee_bps = layer_gap as u64 * 100; // 1% = 100 basis points per layer
    (amount * fee_bps) / 10_000
}

/// Check if account is dormant (inactive > 30 days)
pub fn is_dormant(last_activity: i64, current_time: i64) -> bool {
    const DORMANCY_THRESHOLD: i64 = 30 * 24 * 60 * 60; // 30 days in seconds
    current_time - last_activity > DORMANCY_THRESHOLD
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_layer_fee_calculation() {
        // Same layer: 0%
        assert_eq!(calculate_layer_fee(1, 1, 1000), 0);
        assert_eq!(calculate_layer_fee(2, 2, 1000), 0);

        // 1 layer: 1%
        assert_eq!(calculate_layer_fee(1, 2, 1000), 10);
        assert_eq!(calculate_layer_fee(2, 1, 1000), 10);

        // 2 layers: 2%
        assert_eq!(calculate_layer_fee(1, 3, 1000), 20);

        // 3 layers: 3%
        assert_eq!(calculate_layer_fee(1, 4, 1000), 30);
    }

    #[test]
    fn test_dormancy_check() {
        let current_time = 1704067200; // 2024-01-01
        let active_time = current_time - (29 * 24 * 60 * 60); // 29 days ago
        let dormant_time = current_time - (31 * 24 * 60 * 60); // 31 days ago

        assert!(!is_dormant(active_time, current_time));
        assert!(is_dormant(dormant_time, current_time));
    }
}
