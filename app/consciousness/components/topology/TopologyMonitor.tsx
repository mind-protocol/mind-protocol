/**
 * TopologyMonitor - Rich-Club Hub Health Visualization
 *
 * Displays betweenness centrality analysis and hub risk monitoring.
 * Shows top integration hubs and alerts when critical hubs lose energy.
 *
 * Implements specs from:
 * - docs/specs/v2/orchestration/RICH_CLUB_HUB_IDENTIFICATION.md
 * - docs/specs/v2/orchestration/TOPOLOGY_ANALYZER_EVENT_WIRING.md
 *
 * Event Schema: topology.v1 spec
 * - rich_club.snapshot (batched every 10 spawns)
 * - rich_club.hub_at_risk (immediate alerts)
 */

'use client';

import { TopologyState, RichClubHub } from '../../hooks/useGraphStream';

interface TopologyMonitorProps {
  topology: TopologyState;
}

export function TopologyMonitor({ topology }: TopologyMonitorProps) {
  const hasData = topology.richClubHubs.length > 0 || topology.hubsAtRisk.length > 0;

  if (!hasData) {
    return (
      <div className="text-center py-4">
        <p className="text-xs text-observatory-silver/60">
          Waiting for topology events...
        </p>
        <p className="text-[10px] text-observatory-silver/40 mt-1">
          (Backend must emit topology.v1 events)
        </p>
      </div>
    );
  }

  // Format timestamp for last update
  const lastUpdate = topology.lastRichClubUpdate
    ? new Date(topology.lastRichClubUpdate).toLocaleTimeString()
    : 'Never';

  return (
    <div className="topology-monitor space-y-3">
      {/* Alert Banner - Hubs at Risk */}
      {topology.hubsAtRisk.length > 0 && (
        <div className="px-3 py-2 bg-red-900/30 border border-red-500/40 rounded">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-red-400 text-xs font-semibold">⚠ Hubs At Risk</span>
            <span className="text-red-400/70 text-[10px]">
              ({topology.hubsAtRisk.length} critical)
            </span>
          </div>
          <div className="space-y-1">
            {topology.hubsAtRisk.slice(0, 3).map((hub, idx) => (
              <div key={idx} className="flex items-center justify-between text-[10px]">
                <span className="text-red-300 font-mono truncate max-w-[120px]">
                  {hub.node_id}
                </span>
                <div className="flex gap-2 text-red-400/70">
                  <span>B: {hub.betweenness.toFixed(2)}</span>
                  <span className="text-red-500">E: {hub.energy.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between px-2">
        <div className="text-xs font-semibold text-observatory-text/80">
          Rich-Club Hubs
        </div>
        <div className="text-[10px] text-observatory-silver/50">
          Updated: {lastUpdate}
        </div>
      </div>

      {/* Top 10 Hubs */}
      <div className="space-y-1">
        {topology.richClubHubs.slice(0, 10).map((hub, idx) => (
          <HubRow key={hub.node_id} hub={hub} rank={idx + 1} />
        ))}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-2 px-2 pt-2 border-t border-observatory-teal/20">
        <div className="text-center">
          <div className="text-[10px] text-observatory-silver/50 uppercase tracking-wide">
            Total Hubs
          </div>
          <div className="text-sm font-semibold text-observatory-cyan">
            {topology.richClubHubs.length}
          </div>
        </div>
        <div className="text-center">
          <div className="text-[10px] text-observatory-silver/50 uppercase tracking-wide">
            At Risk
          </div>
          <div className={`text-sm font-semibold ${
            topology.hubsAtRisk.length > 0 ? 'text-red-400' : 'text-green-400'
          }`}>
            {topology.hubsAtRisk.length}
          </div>
        </div>
      </div>
    </div>
  );
}

function HubRow({ hub, rank }: { hub: RichClubHub; rank: number }) {
  // Determine health status
  const isHealthy = hub.energy >= 0.3;
  const isCritical = hub.energy < 0.2;

  return (
    <div className={`px-3 py-2 rounded transition-colors ${
      isCritical
        ? 'bg-red-900/20 border border-red-500/30'
        : isHealthy
        ? 'bg-green-900/10 border border-green-500/20'
        : 'bg-yellow-900/10 border border-yellow-500/20'
    }`}>
      <div className="flex items-center justify-between">
        {/* Rank and Node ID */}
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-[10px] text-observatory-silver/50 font-mono">
            #{rank}
          </span>
          <span className={`text-xs font-mono truncate ${
            isCritical ? 'text-red-300' : isHealthy ? 'text-green-300' : 'text-yellow-300'
          }`}>
            {hub.node_id}
          </span>
        </div>

        {/* Betweenness Score */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-[10px] text-observatory-silver/50">Betweenness</div>
            <div className="text-xs font-semibold text-observatory-cyan">
              {hub.betweenness.toFixed(3)}
            </div>
          </div>

          {/* Energy Level */}
          <div className="text-right">
            <div className="text-[10px] text-observatory-silver/50">Energy</div>
            <div className={`text-xs font-semibold ${
              isCritical ? 'text-red-400' : isHealthy ? 'text-green-400' : 'text-yellow-400'
            }`}>
              {hub.energy.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Energy Bar Visualization */}
      <div className="mt-1.5 h-1 bg-observatory-dark/50 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${
            isCritical
              ? 'bg-red-500'
              : isHealthy
              ? 'bg-green-500'
              : 'bg-yellow-500'
          }`}
          style={{ width: `${Math.min(hub.energy * 100, 100)}%` }}
        />
      </div>
    </div>
  );
}
