/**
 * Budget Account API
 *
 * Manages user budget accounts for metered compute billing.
 * Implements Phase 0 Minimal Economy spec.
 *
 * GET /api/budget/account?wallet={address}
 * - Fetches current balance and account info
 * - Creates account with initial balance if doesn't exist
 *
 * Based on: docs/specs/v2/autonomy/architecture/minimal_economy_phase0.md
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-26
 */

import { NextRequest, NextResponse } from 'next/server';

// Initial balance for new accounts (in credits)
// 1000 credits = $10 USD (at 100 credits per dollar)
const INITIAL_BALANCE = 1000;

// TODO: Phase 0 uses mock data. Phase 1 will integrate with Python backend via HTTP
// In-memory mock storage (will be replaced with FalkorDB via Python backend)
const mockAccounts = new Map<string, BudgetAccount>();

interface BudgetAccount {
  owner_id: string;
  owner_type: 'human' | 'org' | 'citizen' | 'service';
  balance: number;
  reserved: number;
  initial_balance: number;
  lifetime_spent: number;
  created_at: string;
  updated_at: string;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const walletAddress = searchParams.get('wallet');

    if (!walletAddress) {
      return NextResponse.json(
        { error: 'Missing wallet parameter' },
        { status: 400 }
      );
    }

    // Check if account exists in mock storage
    let account = mockAccounts.get(walletAddress);

    if (!account) {
      // Account doesn't exist - create new account with initial balance
      const now = new Date().toISOString();

      account = {
        owner_id: walletAddress,
        owner_type: 'human',
        balance: INITIAL_BALANCE,
        reserved: 0,
        initial_balance: INITIAL_BALANCE,
        lifetime_spent: 0,
        created_at: now,
        updated_at: now,
      };

      mockAccounts.set(walletAddress, account);

      console.log(`[BudgetAccount] Created new mock account for ${walletAddress} with ${INITIAL_BALANCE} credits`);
    }

    return NextResponse.json({
      success: true,
      account,
    });

  } catch (error) {
    console.error('[BudgetAccount] Failed to fetch account:', error);
    return NextResponse.json(
      {
        error: 'Failed to fetch account',
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
