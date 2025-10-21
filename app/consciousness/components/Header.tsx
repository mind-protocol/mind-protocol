'use client';

import { useState } from 'react';
import type { Node } from '../hooks/useGraphData';
import { EmergencyControls } from './EmergencyControls';
import { SearchBar } from './SearchBar';
import { SystemStatusIndicator } from './SystemStatusIndicator';

interface HeaderProps {
  currentGraphId: string | null;
  nodeCount: number;
  linkCount: number;
  nodes: Node[];
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
  nodeCount,
  linkCount,
  nodes
}: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);

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

          <div className="text-observatory-cyan font-bold text-lg tracking-wide">
            Mind Protocol
          </div>
        </div>

        {/* Center - Current Graph Name & Search */}
        <div className="flex-1 flex items-center justify-center gap-4 px-4 max-w-3xl">
          {currentGraphId && (
            <>
              <div className="text-sm text-observatory-text/70 whitespace-nowrap">
                {currentGraphId.replace('citizen_', '').replace('org_', '').replace('_', ' ')}
              </div>
              <div className="h-4 w-px bg-observatory-teal/30"></div>
            </>
          )}
          <SearchBar nodes={nodes} />
        </div>

        {/* Right - Stats & System Status */}
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

          <div className="h-6 w-px bg-observatory-teal/30"></div>

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

              {/* Future sections can go here */}
              {/* e.g., Settings, About, etc. */}
            </div>
          </div>
        </>
      )}
    </>
  );
}
