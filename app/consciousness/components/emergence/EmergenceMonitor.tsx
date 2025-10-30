/**
 * EmergenceMonitor - Real-time SubEntity emergence telemetry
 *
 * Visualizes the emergence process from consciousness_engine_v2.py:
 * 1. Gap Detection - Semantic/quality/structural gaps in working memory
 * 2. Coalition Validation - Zero-constants scoring against quantile gates
 * 3. Emergence Decisions - spawn, redirect, reject
 * 4. Membership Learning - Weight adjustments via weak priors
 *
 * Event Schema: emergence.v1 spec (see EMERGENCE_ENGINE_INTEGRATION_GUIDE.md)
 */

'use client';

import { EmergenceState, EmergenceEvent } from '../../hooks/useGraphStream';

interface EmergenceMonitorProps {
  emergence: EmergenceState;
}

export function EmergenceMonitor({ emergence }: EmergenceMonitorProps) {
  const hasAnyActivity = emergence.totalGapsDetected > 0 ||
                         emergence.totalSpawned > 0 ||
                         emergence.totalRejected > 0;

  if (!hasAnyActivity) {
    return (
      <div className="text-center py-4">
        <p className="text-xs text-observatory-silver/60">
          Waiting for emergence events...
        </p>
        <p className="text-[10px] text-observatory-silver/40 mt-1">
          (Backend must emit emergence.v1 events)
        </p>
      </div>
    );
  }

  return (
    <div className="emergence-monitor space-y-3">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-2 px-2">
        <StatBox label="Gaps" value={emergence.totalGapsDetected} color="yellow" />
        <StatBox label="Spawned" value={emergence.totalSpawned} color="green" />
        <StatBox label="Rejected" value={emergence.totalRejected} color="red" />
      </div>

      {/* Recent Activity */}
      <div className="space-y-2">
        {/* Recent Spawns */}
        {emergence.recentSpawns.length > 0 && (
          <ActivitySection
            title="Recent Spawns"
            events={emergence.recentSpawns}
            renderEvent={(event) => (
              <div className="flex items-center justify-between">
                <span className="text-xs text-green-400 font-mono">
                  {event.payload.subentity_id}
                </span>
                <span className="text-[10px] text-observatory-silver/50">
                  {event.payload.member_count} nodes
                </span>
              </div>
            )}
          />
        )}

        {/* Recent Gaps */}
        {emergence.recentGaps.length > 0 && (
          <ActivitySection
            title="Recent Gaps"
            events={emergence.recentGaps.slice(0, 5)}
            renderEvent={(event) => (
              <div className="flex items-center justify-between">
                <span className="text-xs text-yellow-400 font-mono">
                  {event.payload.gap_id}
                </span>
                <span className="text-[10px] text-observatory-silver/50">
                  {event.payload.locus_nodes?.length || 0} locus nodes
                </span>
              </div>
            )}
          />
        )}

        {/* Recent Candidates */}
        {emergence.recentCandidates.length > 0 && (
          <ActivitySection
            title="Candidates"
            events={emergence.recentCandidates.slice(0, 3)}
            renderEvent={(event) => (
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-observatory-cyan font-mono">
                    {event.payload.decision}
                  </span>
                  <span className="text-[10px] text-observatory-silver/50">
                    {event.payload.nodes?.length || 0} nodes
                  </span>
                </div>
                {event.payload.scores && (
                  <div className="text-[10px] text-observatory-silver/40 pl-2">
                    P:{event.payload.scores.persistence_q?.toFixed(2)} |
                    C:{event.payload.scores.cohesion_q?.toFixed(2)} |
                    B:{event.payload.scores.boundary_q?.toFixed(2)}
                  </div>
                )}
              </div>
            )}
          />
        )}

        {/* Recent Redirects */}
        {emergence.recentRedirects.length > 0 && (
          <ActivitySection
            title="Redirects"
            events={emergence.recentRedirects.slice(0, 3)}
            renderEvent={(event) => (
              <div className="flex items-center justify-between">
                <span className="text-xs text-blue-400 font-mono">
                  → {event.payload.target_subentity}
                </span>
                <span className="text-[10px] text-observatory-silver/50">
                  {event.payload.reason}
                </span>
              </div>
            )}
          />
        )}

        {/* Recent Rejects */}
        {emergence.recentRejects.length > 0 && (
          <ActivitySection
            title="Rejects"
            events={emergence.recentRejects.slice(0, 3)}
            renderEvent={(event) => (
              <div className="space-y-1">
                <div className="text-xs text-red-400">
                  {event.payload.reason}
                </div>
                {event.payload.scores && (
                  <div className="text-[10px] text-observatory-silver/40 pl-2">
                    P:{event.payload.scores.persistence_q?.toFixed(2)} |
                    C:{event.payload.scores.cohesion_q?.toFixed(2)} |
                    B:{event.payload.scores.boundary_q?.toFixed(2)}
                  </div>
                )}
              </div>
            )}
          />
        )}

        {/* Recent Membership Updates */}
        {emergence.recentMembershipUpdates.length > 0 && (
          <ActivitySection
            title="Membership Updates"
            events={emergence.recentMembershipUpdates.slice(0, 3)}
            renderEvent={(event) => (
              <div className="space-y-1">
                <div className="text-xs text-observatory-silver/70">
                  {event.payload.subentity_id}
                </div>
                <div className="text-[10px] text-observatory-silver/50 pl-2">
                  {event.payload.deltas?.length || 0} weight adjustments
                </div>
              </div>
            )}
          />
        )}
      </div>
    </div>
  );
}

interface StatBoxProps {
  label: string;
  value: number;
  color: 'yellow' | 'green' | 'red';
}

function StatBox({ label, value, color }: StatBoxProps) {
  const colorClasses = {
    yellow: 'bg-yellow-500/10 text-yellow-400',
    green: 'bg-green-500/10 text-green-400',
    red: 'bg-red-500/10 text-red-400'
  };

  return (
    <div className={`${colorClasses[color]} rounded px-2 py-1.5 text-center`}>
      <div className="text-lg font-bold">{value}</div>
      <div className="text-[10px] opacity-70">{label}</div>
    </div>
  );
}

interface ActivitySectionProps {
  title: string;
  events: EmergenceEvent[];
  renderEvent: (event: EmergenceEvent) => React.ReactNode;
}

function ActivitySection({ title, events, renderEvent }: ActivitySectionProps) {
  return (
    <div className="space-y-1">
      <div className="text-[10px] text-observatory-silver/50 px-2 uppercase tracking-wide">
        {title}
      </div>
      <div className="space-y-1">
        {events.map((event) => (
          <div
            key={event.id}
            className="bg-observatory-bg/30 rounded px-2 py-1.5 hover:bg-observatory-bg/50 transition-colors"
          >
            <div className="flex items-start justify-between mb-1">
              <div className="flex-1">
                {renderEvent(event)}
              </div>
              <span className="text-[9px] text-observatory-silver/30 ml-2 whitespace-nowrap">
                Frame {event.frame}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
