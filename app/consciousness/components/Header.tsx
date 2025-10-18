'use client';

import { useState } from 'react';
import type { AvailableGraphs, Node } from '../hooks/useGraphData';
import { EmergencyControls } from './EmergencyControls';
import { SearchBar } from './SearchBar';

interface HeaderProps {
  availableGraphs: AvailableGraphs;
  currentGraphType: string;
  currentGraphId: string | null;
  onSelectGraph: (type: string, id: string) => void;
  connected: boolean;
  nodeCount: number;
  linkCount: number;
  nodes: Node[];
}

/**
 * Header Component
 *
 * Top bar with graph selector, connection status, and quick stats.
 * Includes hamburger menu with system controls.
 */
export function Header({
  availableGraphs,
  currentGraphType,
  currentGraphId,
  onSelectGraph,
  connected,
  nodeCount,
  linkCount,
  nodes
}: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      <div className="fixed top-0 left-0 right-0 h-16 consciousness-panel border-b border-consciousness-border z-30 flex items-center px-6">
        {/* Left - Hamburger Menu + Title */}
        <div className="flex items-center gap-4">
          {/* Hamburger Menu Button */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex flex-col gap-1 p-2 hover:bg-consciousness-border/30 rounded transition-colors"
            aria-label="System menu"
          >
            <div className={`w-5 h-0.5 bg-consciousness-green transition-all ${menuOpen ? 'rotate-45 translate-y-1.5' : ''}`} />
            <div className={`w-5 h-0.5 bg-consciousness-green transition-all ${menuOpen ? 'opacity-0' : ''}`} />
            <div className={`w-5 h-0.5 bg-consciousness-green transition-all ${menuOpen ? '-rotate-45 -translate-y-1.5' : ''}`} />
          </button>

          <div className="text-consciousness-green font-bold text-lg">
            Mind Protocol
          </div>
        </div>

        {/* Center - Search */}
        <div className="flex-1 flex justify-center px-4 max-w-2xl">
          <SearchBar nodes={nodes} />
        </div>

        {/* Right - Graph selector, Stats & Status */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-400">Graph:</label>
            <select
              value={currentGraphId || ''}
              onChange={(e) => {
                const value = e.target.value;
                if (!value) return;

                // Determine type from value prefix
                const citizen = availableGraphs.citizens.find(g => g.id === value);
                if (citizen) {
                  onSelectGraph('citizen', citizen.id);
                  return;
                }

                const org = availableGraphs.organizations.find(g => g.id === value);
                if (org) {
                  onSelectGraph('organization', org.id);
                  return;
                }

                const eco = availableGraphs.ecosystems.find(g => g.id === value);
                if (eco) {
                  onSelectGraph('ecosystem', eco.id);
                }
              }}
              className="bg-gray-800 text-white text-sm px-3 py-1.5 rounded border border-consciousness-border focus:outline-none focus:border-consciousness-green cursor-pointer"
            >
              {availableGraphs.citizens.length > 0 && (
                <optgroup label="Citizens">
                  {availableGraphs.citizens.map(graph => (
                    <option key={`citizen-${graph.id}`} value={graph.id}>
                      {graph.name}
                    </option>
                  ))}
                </optgroup>
              )}
              {availableGraphs.organizations.length > 0 && (
                <optgroup label="Organizations">
                  {availableGraphs.organizations.map(graph => (
                    <option key={`org-${graph.id}`} value={graph.id}>
                      {graph.name}
                    </option>
                  ))}
                </optgroup>
              )}
              {availableGraphs.ecosystems.length > 0 && (
                <optgroup label="Ecosystems">
                  {availableGraphs.ecosystems.map(graph => (
                    <option key={`eco-${graph.id}`} value={graph.id}>
                      {graph.name}
                    </option>
                  ))}
                </optgroup>
              )}
            </select>
          </div>

          <div className="h-6 w-px bg-consciousness-border"></div>

          {/* Stats */}
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1.5">
              <span className="text-gray-400">Nodes:</span>
              <span className="text-consciousness-green font-medium">{nodeCount}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-gray-400">Links:</span>
              <span className="text-consciousness-green font-medium">{linkCount}</span>
            </div>
          </div>

          <div className="h-6 w-px bg-consciousness-border"></div>

          {/* Connection Status */}
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-consciousness-green' : 'bg-red-500'}
                            ${connected ? 'animate-pulse-glow' : ''}`} />
            <span className="text-xs text-gray-400">
              {connected ? 'Live' : 'Offline'}
            </span>
          </div>
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
          <div className="fixed top-16 left-0 bottom-0 w-80 consciousness-panel border-r border-consciousness-border z-50 overflow-y-auto custom-scrollbar animate-slide-in-left">
            {/* Menu Content */}
            <div className="p-6">
              {/* System Section */}
              <div className="mb-6">
                <h2 className="text-consciousness-green font-semibold text-sm mb-4 flex items-center gap-2">
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
