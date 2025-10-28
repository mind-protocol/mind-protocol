'use client';

/**
 * WalletConnectionButton Component
 *
 * Displays wallet connection status and allows users to connect/disconnect
 * Solana wallets for authentication and credit purchases.
 *
 * States:
 * - Disconnected: Shows "Connect Wallet" button
 * - Connected: Shows truncated wallet address + disconnect option
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-26 (Phase 0 Minimal Economy)
 */

import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { useState } from 'react';

// Import wallet adapter styles
import '@solana/wallet-adapter-react-ui/styles.css';

export function WalletConnectionButton() {
  const { publicKey, disconnect, connected } = useWallet();
  const [showMenu, setShowMenu] = useState(false);

  // Truncate wallet address for display
  const truncatedAddress = publicKey
    ? `${publicKey.toBase58().slice(0, 4)}...${publicKey.toBase58().slice(-4)}`
    : null;

  if (!connected) {
    // Use the wallet adapter's built-in multi-button for wallet selection
    return (
      <WalletMultiButton className="!bg-blue-600 !hover:bg-blue-700 !text-white !rounded-lg !px-4 !py-2 !text-sm !font-medium !transition-colors">
        Connect Wallet
      </WalletMultiButton>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors border border-gray-700"
      >
        <div className="w-2 h-2 bg-green-500 rounded-full" />
        <span className="font-mono">{truncatedAddress}</span>
        <svg
          className={`w-4 h-4 transition-transform ${showMenu ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {showMenu && (
        <>
          {/* Backdrop to close menu when clicking outside */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowMenu(false)}
          />

          {/* Dropdown menu */}
          <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-20">
            <div className="p-2">
              <button
                onClick={() => {
                  disconnect();
                  setShowMenu(false);
                }}
                className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-gray-700 rounded-md transition-colors"
              >
                Disconnect
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
