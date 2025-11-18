'use client';

import Image from "next/image";
import { useState } from 'react';
import type { Node } from '../hooks/useGraphData';
import { EmergencyControls } from './EmergencyControls';
import { SearchBar } from './SearchBar';
import { SystemStatusIndicator } from './SystemStatusIndicator';
// REMOVED: WalletConnectionButton - Solana wallet not needed right now
// import { WalletConnectionButton } from '../../components/WalletConnectionButton';
import { useWebSocket } from '../hooks/useWebSocket';

interface HeaderProps {
  currentGraphId: string | null;
  currentGraphLabel?: string;
  nodeCount: number;
  linkCount: number;
  nodes: Node[];
  onToggleForgedIdentity?: () => void;
  showForgedIdentityViewer?: boolean;
}

/**
 * Header Component
 *
 * Top bar with system status, search, and quick stats.
 * Graph switching happens via clicking citizens in sidebar.
 * Includes hamburger menu with system controls.
 */
export function Header({
  currentGraphId,
  currentGraphLabel,
  nodeCount,
  linkCount,
  nodes,
  onToggleForgedIdentity,
  showForgedIdentityViewer = false
}: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const { walletContext, economyOverlays } = useWebSocket();
  const primaryCitizen = walletContext?.citizenIds?.[0];
  const econ = primaryCitizen ? economyOverlays[primaryCitizen] : undefined;

  return (
    <>
      <div className="fixed top-0 left-0 right-0 h-16 consciousness-panel border-b border-observatory-teal z-30 flex items-center px-6">
        {/* Left - Hamburger Menu + Title */}
        <div className="flex items-center gap-4">
          {/* Hamburger Menu Button */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex flex-col gap-1 p-2 hover:bg-observatory-cyan/20 rounded transition-colors"
            aria-label="System menu"
          >
            <div className={`w-5 h-0.5 bg-observatory-cyan transition-all ${menuOpen ? 'rotate-45 translate-y-1.5' : ''}`} />
            <div className={`w-5 h-0.5 bg-observatory-cyan transition-all ${menuOpen ? 'opacity-0' : ''}`} />
            <div className={`w-5 h-0.5 bg-observatory-cyan transition-all ${menuOpen ? '-rotate-45 -translate-y-1.5' : ''}`} />
          </button>

          <div className="flex items-center gap-3">
            <Image
              src="/images/logo-transparent-512.png"
              alt="Mind Protocol logo"
              width={36}
              height={36}
              priority
              className="drop-shadow-[0_0_8px_rgba(243,227,186,0.25)]"
            />
            <div className="text-observatory-cyan font-bold text-lg tracking-wide whitespace-nowrap">
              Mind Protocol
            </div>
          </div>
        </div>

        {/* Center - Current Graph Name & Search */}
        <div className="flex-1 flex items-center justify-center gap-4 px-4 max-w-3xl">
          {(currentGraphLabel || currentGraphId) && (
            <>
              <div className="text-sm text-observatory-text/70 whitespace-nowrap">
                {currentGraphLabel || currentGraphId?.replace(/_/g, ' ')}
              </div>
              <div className="h-4 w-px bg-observatory-teal/30"></div>
            </>
          )}
          <SearchBar nodes={nodes} currentGraphId={currentGraphId} />
        </div>

        {/* Right - Stats, Credits, Wallet & System Status */}
        <div className="flex items-center gap-4">
          {/* Stats */}
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1.5">
              <span className="text-observatory-text/70">Nodes:</span>
              <span className="text-observatory-cyan font-semibold">{nodeCount}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-observatory-text/70">Links:</span>
              <span className="text-observatory-cyan font-semibold">{linkCount}</span>
            </div>
          </div>

          {econ && (
            <>
              <div className="h-6 w-px bg-observatory-teal/30"></div>
              {/* TODO: Add EconomyBadge import */}
              {/* <EconomyBadge overlay={econ} /> */}
            </>
          )}


          {/* REMOVED: Wallet Connection - not needed right now */}
          {/* <WalletConnectionButton /> */}
          {/* <div className="h-6 w-px bg-observatory-teal/30"></div> */}

          {/* System Status with Hover Popup */}
          <SystemStatusIndicator />
        </div>
      </div>

      {/* Sliding Menu Panel */}
      {menuOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 animate-fade-in"
            onClick={() => setMenuOpen(false)}
          />

          {/* Menu Panel */}
          <div className="fixed top-16 left-0 bottom-0 w-80 consciousness-panel border-r border-observatory-teal z-50 overflow-y-auto custom-scrollbar animate-slide-in-left">
            {/* Menu Content */}
            <div className="p-6">
              {/* View Section */}
              <div className="mb-6">
                <h2 className="text-observatory-cyan font-semibold text-sm mb-4 flex items-center gap-2 uppercase tracking-wider">
                  <span>👁️</span>
                  <span>VIEW</span>
                </h2>

                <div className="consciousness-panel p-4">
                  <button
                    onClick={() => {
                      onToggleForgedIdentity?.();
                      setMenuOpen(false);
                    }}
                    className={`
                      w-full px-4 py-3 rounded-lg text-left transition-all
                      ${showForgedIdentityViewer
                        ? 'bg-observatory-cyan/20 border-2 border-observatory-cyan text-observatory-cyan'
                        : 'bg-zinc-800/50 border border-observatory-cyan/30 text-observatory-text hover:bg-observatory-cyan/10'
                      }
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">🧠</span>
                        <span className="text-sm font-medium">Forged Identity Prompts</span>
                      </div>
                      <span className="text-xs px-2 py-1 rounded bg-yellow-500/10 border border-yellow-500/30 text-yellow-400">
                        Phase 3A
                      </span>
                    </div>
                    <div className="text-xs text-observatory-text/60 mt-1 ml-7">
                      {showForgedIdentityViewer ? 'Hide' : 'Show'} system prompts generated from consciousness state
                    </div>
                  </button>
                </div>
              </div>

              {/* System Section */}
              <div className="mb-6">
                <h2 className="text-observatory-cyan font-semibold text-sm mb-4 flex items-center gap-2 uppercase tracking-wider">
                  <span>⚙️</span>
                  <span>SYSTEM</span>
                </h2>

                {/* Emergency Controls - Embedded */}
                <div className="consciousness-panel p-4">
                  <EmergencyControls />
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}

