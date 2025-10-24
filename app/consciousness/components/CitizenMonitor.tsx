'use client';

import { useState, useEffect, useRef } from 'react';
import type { Subentity } from '../hooks/useGraphData';
import type { V2ConsciousnessState } from '../hooks/websocket-types';

interface Citizen {
  id: string;
  name: string;
  state: 'active' | 'recently_active' | 'dormant' | 'stopped';
  lastThought: string;
  subentities: Subentity[];
  lastUpdate: string;
  tickInterval: number;
  energyTotal: number;
  energyUsed: number;
}

// Ada's API response type
interface CitizenStatus {
  citizen_id: string;
  running_state: "running" | "frozen" | "slow_motion" | "turbo";
  tick_count: number;
  tick_interval_ms: number;
  tick_frequency_hz: number;
  tick_multiplier: number;
  consciousness_state: "alert" | "engaged" | "calm" | "drowsy" | "dormant";
  time_since_last_event: number;
  sub_entity_count: number;
  sub_entities: string[];
  nodes: number;
  links: number;
}

interface CitizenMonitorProps {
  citizens: Citizen[];
  onFocusNode: (nodeId: string) => void;
  onSelectCitizen: (citizenId: string) => void;
  activeCitizenId: string | null;
  v2State: V2ConsciousnessState;
}

/**
 * CitizenMonitor - Right sidebar accordion
 *
 * Shows all citizens with collapsible sections:
 * - Collapsed: State, last thought, color indicator
 * - Expanded: Full subentity activity stream, CLAUDE_DYNAMIC.md viewer
 *
 * Clicking citizen card or avatar switches to that citizen's graph.
 * Clicking node references focuses that node on the graph.
 */
export function CitizenMonitor({ citizens, onFocusNode, onSelectCitizen, activeCitizenId, v2State }: CitizenMonitorProps) {
  const [expandedCitizen, setExpandedCitizen] = useState<string | null>(null);

  return (
    <div className="fixed right-0 top-16 bottom-0 w-[20rem] consciousness-panel border-l border-observatory-teal overflow-hidden flex flex-col z-20">
      {/* Accordion - takes full height */}
      <div className="flex-1 overflow-y-auto custom-scrollbar pt-4">
        {citizens.map(citizen => (
          <CitizenAccordionItem
            key={citizen.id}
            citizen={citizen}
            isExpanded={expandedCitizen === citizen.id}
            isActive={activeCitizenId === `citizen_${citizen.id}` || activeCitizenId === `org_${citizen.id}`}
            onToggle={() => setExpandedCitizen(
              expandedCitizen === citizen.id ? null : citizen.id
            )}
            onFocusNode={onFocusNode}
            onSelectCitizen={onSelectCitizen}
            v2State={v2State}
          />
        ))}
      </div>
    </div>
  );
}

function CitizenAccordionItem({
  citizen,
  isExpanded,
  isActive,
  onToggle,
  onFocusNode,
  onSelectCitizen,
  v2State
}: {
  citizen: Citizen;
  isExpanded: boolean;
  isActive: boolean;
  onToggle: () => void;
  onFocusNode: (nodeId: string) => void;
  onSelectCitizen: (citizenId: string) => void;
  v2State: V2ConsciousnessState;
}) {
  const [apiStatus, setApiStatus] = useState<CitizenStatus | null>(null);

  // Poll API for real-time status every 2 seconds
  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/citizen/${citizen.id}/status`);
        if (response.ok) {
          const data = await response.json();
          setApiStatus(data);
        }
      } catch (error) {
        // Backend not running yet - fall back to mock data
        console.log(`API not available for ${citizen.id}:`, error);
      }
    };

    // Initial poll
    pollStatus();

    // Poll every 2 seconds
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [citizen.id]);

  // Use API status if available, otherwise fall back to mock data
  const runningState = apiStatus?.running_state ||
    (citizen.state === 'stopped' ? 'frozen' : 'running');
  const tickFrequency = apiStatus?.tick_frequency_hz ||
    (1000 / citizen.tickInterval);
  const consciousnessState = apiStatus?.consciousness_state || 'unknown';

  const stateColor = {
    running: 'bg-green-500',               // GREEN - healthy running
    frozen: 'bg-blue-500',                 // BLUE - frozen state
    slow_motion: 'bg-yellow-500',          // YELLOW - slow motion
    turbo: 'bg-red-500'                    // RED - turbo mode
  }[runningState] || 'bg-gray-500';

  const stateEmoji = {
    running: '🟢',
    frozen: '❄️',
    slow_motion: '🐌',
    turbo: '⚡'
  }[runningState] || '⚫';

  const stateLabel = {
    running: 'Running',
    frozen: 'Frozen',
    slow_motion: 'Slow Motion',
    turbo: 'Turbo'
  }[runningState] || 'Unknown';

  // Avatar path: Try PNG first, fallback to SVG
  const [avatarPath, setAvatarPath] = useState(`/citizens/${citizen.id}/avatar.png`);
  const [avatarError, setAvatarError] = useState(false);

  return (
    <div className={`border-b border-observatory-teal/20 relative transition-all ${
      isActive ? 'bg-observatory-cyan/10 border-observatory-cyan/40' : ''
    }`}>
      {/* Horizontal Compact Card - Clickable to Switch Graph */}
      <div
        className="p-4 cursor-pointer hover:bg-observatory-cyan/10 transition-colors"
        onClick={() => onSelectCitizen(citizen.id)}
      >
        <div className="flex items-center gap-3">
          {/* Avatar - Smaller, Circular */}
          <div className="relative w-12 h-12 flex-shrink-0">
            <img
              src={avatarPath}
              alt={`${citizen.name} avatar`}
              className={`w-full h-full object-cover rounded-full border-2 transition-all ${
                isActive ? 'border-venice-gold-bright' : 'border-observatory-teal/40'
              }`}
              onError={(e) => {
                if (!avatarError && avatarPath.endsWith('.png')) {
                  setAvatarPath(`/citizens/${citizen.id}/avatar.svg`);
                  setAvatarError(true);
                } else {
                  e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23f5e7c1" width="100" height="100"/><text x="50" y="50" text-anchor="middle" dy=".3em" fill="%23b8860b" font-size="40">?</text></svg>';
                }
              }}
            />
            <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-observatory-dark ${stateColor}`} />
          </div>

          {/* Name + Status - Horizontal Layout */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <div className={`font-semibold text-lg ${
                isActive ? 'text-observatory-cyan' : 'text-observatory-text/80'
              }`}>
                {citizen.name}
              </div>

              {/* Heartbeat Indicator - Inline */}
              <HeartbeatIndicator
                frequency={tickFrequency}
                state={runningState}
                consciousnessState={consciousnessState}
                apiStatus={apiStatus}
                v2State={v2State}
              />
            </div>

            {/* Node/Link Count */}
            <div className="text-xs text-observatory-text/60 truncate mt-1">
              {apiStatus
                ? `${apiStatus.nodes || 0} nodes • ${apiStatus.links || 0} links`
                : (citizen.lastThought || 'No recent activity')}
            </div>
          </div>

          {/* Expand Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggle();
            }}
            className="p-1.5 hover:bg-observatory-cyan/20 rounded transition-colors flex-shrink-0"
          >
            <span className="text-observatory-text/70 text-xs">
              {isExpanded ? '▼' : '▶'}
            </span>
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4">
          {/* Subentity Activity Stream */}
          <div>
            <div className="text-xs text-observatory-text/70 uppercase tracking-wider mb-2">
              Active Subentities
            </div>
            <div className="space-y-2">
              {citizen.subentities.map(subentity => (
                <EntityActivityCard
                  key={subentity.entity_id}
                  subentity={subentity}
                  onFocusNode={onFocusNode}
                />
              ))}
            </div>
          </div>

          {/* CLAUDE_DYNAMIC.md Viewer */}
          <DynamicPromptViewer
            citizenId={citizen.id}
            onFocusNode={onFocusNode}
          />
        </div>
      )}
    </div>
  );
}

function EntityActivityCard({
  subentity,
  onFocusNode
}: {
  subentity: Subentity;
  onFocusNode: (nodeId: string) => void;
}) {
  return (
    <div className="consciousness-panel p-3 text-xs">
      <div className="flex items-center justify-between mb-2">
        <span className="text-observatory-cyan font-medium">
          {subentity.entity_id}
        </span>
        {(subentity as any).energy_used !== undefined && (subentity as any).energy_budget !== undefined && (
          <span className="text-venice-gold-bright">
            {(subentity as any).energy_used}/{(subentity as any).energy_budget}
          </span>
        )}
      </div>

      {/* Current Yearning */}
      {(subentity as any).current_yearning && (
        <div className="text-observatory-text/70 mb-2">
          {(subentity as any).current_yearning}
        </div>
      )}

      {/* Recent Path - Clickable */}
      {(subentity as any).recent_path && (subentity as any).recent_path.length > 0 && (
        <div className="space-y-1">
          <div className="text-observatory-text/50">Recent path:</div>
          {(subentity as any).recent_path.slice(-5).map((node: any, i: number) => (
            <button
              key={i}
              onClick={() => onFocusNode(node.id)}
              className="block w-full text-left px-2 py-1 rounded hover:bg-observatory-cyan/20 text-observatory-text/60 hover:text-observatory-cyan transition-colors"
            >
              {i + 1}. {node.text?.slice(0, 40)}...
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function DynamicPromptViewer({
  citizenId,
  onFocusNode
}: {
  citizenId: string;
  onFocusNode: (nodeId: string) => void;
}) {
  const [isOpen, setIsOpen] = useState(false);

  // TODO: Load CLAUDE_DYNAMIC.md via file watcher when backend implements it

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full text-left text-xs text-observatory-text/60 uppercase tracking-wider mb-2 hover:text-observatory-cyan transition-colors"
      >
        CLAUDE_DYNAMIC.md {isOpen ? '▼' : '▶'}
      </button>

      {isOpen && (
        <div className="consciousness-panel p-3 max-h-96 overflow-y-auto custom-scrollbar">
          <div className="text-xs text-observatory-text/70 whitespace-pre-wrap">
            <div className="text-observatory-text/50 italic">
              Waiting for backend implementation...
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * HeartbeatIndicator - Visual representation of consciousness rhythm
 *
 * Uses live v2 frame events for smooth 1-by-1 tick updates.
 * Displays branching ratio (ρ) as "Thought Flow" metric.
 * Color-coded by consciousness state for immediate status recognition.
 */
function HeartbeatIndicator({
  frequency,
  state,
  consciousnessState,
  apiStatus,
  v2State
}: {
  frequency: number;
  state: string;
  consciousnessState: string;
  apiStatus?: CitizenStatus | null;
  v2State: V2ConsciousnessState;
}) {
  const [pulseKey, setPulseKey] = useState(0);

  // Trigger pulse animation on each new frame (live from WebSocket)
  const prevFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (v2State.currentFrame !== null && v2State.currentFrame !== prevFrameRef.current) {
      setPulseKey(prev => prev + 1);
      prevFrameRef.current = v2State.currentFrame;
    }
  }, [v2State.currentFrame]);

  // Color mapping for consciousness states
  const stateColors: Record<string, { bg: string; pulse: string; text: string }> = {
    alert: { bg: 'bg-red-500/20', pulse: 'bg-red-500', text: 'text-red-400' },
    engaged: { bg: 'bg-green-500/20', pulse: 'bg-green-500', text: 'text-green-400' },
    calm: { bg: 'bg-blue-500/20', pulse: 'bg-blue-500', text: 'text-blue-400' },
    drowsy: { bg: 'bg-yellow-500/20', pulse: 'bg-yellow-500', text: 'text-yellow-400' },
    dormant: { bg: 'bg-green-500/20', pulse: 'bg-green-500', text: 'text-green-400' },  // GREEN - idle but ready
    unknown: { bg: 'bg-gray-500/20', pulse: 'bg-gray-500', text: 'text-gray-400' }
  };

  const colors = stateColors[consciousnessState] || stateColors.unknown;

  // For frozen state, show static indicator
  if (state === 'frozen') {
    return (
      <div className="flex items-center gap-1.5">
        <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
        <span className="text-xs text-gray-500">frozen</span>
      </div>
    );
  }

  // Calculate tick interval in ms
  const tickInterval = frequency > 0 ? (1000 / frequency) : 0;
  const displayText = tickInterval >= 1000
    ? `${(tickInterval / 1000).toFixed(1)}s`
    : `${Math.round(tickInterval)}ms`;

  // Get human-readable state label
  const getStateLabel = () => {
    if (consciousnessState === 'dormant') return '(idle)';
    if (consciousnessState === 'drowsy') return '(resting)';
    if (consciousnessState === 'calm') return '(thinking)';
    if (consciousnessState === 'engaged') return '(active)';
    if (consciousnessState === 'alert') return '(focused)';
    return '';
  };

  // Use live v2 frame count if available, otherwise fall back to API polling
  const displayFrame = v2State.currentFrame ?? apiStatus?.tick_count ?? 0;
  const displayRho = v2State.rho;

  // Format rho as "Thought Flow" with visual indicator
  const getRhoDisplay = () => {
    if (displayRho === null || displayRho === undefined) return null;

    // ρ > 1.0 = expanding (discovering new connections)
    // ρ ≈ 1.0 = stable (steady exploration)
    // ρ < 1.0 = contracting (narrowing focus)
    if (displayRho > 1.05) return { emoji: '📈', label: 'expanding', color: 'text-green-400' };
    if (displayRho > 0.95) return { emoji: '⚖️', label: 'balanced', color: 'text-blue-400' };
    return { emoji: '🎯', label: 'focusing', color: 'text-yellow-400' };
  };

  const rhoDisplay = getRhoDisplay();

  // Get safety state classification per criticality.md spec
  const getSafetyState = () => {
    // Use explicit safety_state if provided, otherwise derive from rho
    if (v2State.safety_state) {
      return {
        state: v2State.safety_state,
        emoji: v2State.safety_state === 'critical' ? '⚖️' :
               v2State.safety_state === 'subcritical' ? '🎯' : '📈',
        color: v2State.safety_state === 'critical' ? 'text-green-400' :
               v2State.safety_state === 'subcritical' ? 'text-yellow-400' : 'text-red-400'
      };
    }

    // Fallback: derive from rho if safety_state not provided
    if (displayRho === null || displayRho === undefined) return null;
    if (displayRho > 1.2) return { state: 'supercritical', emoji: '⚠️', color: 'text-red-400' };
    if (displayRho < 0.8) return { state: 'subcritical', emoji: '🎯', color: 'text-yellow-400' };
    return { state: 'critical', emoji: '⚖️', color: 'text-green-400' };
  };

  const safetyState = getSafetyState();

  // Get conservation error status
  const getConservationStatus = () => {
    if (v2State.conservation_error_pct === null || v2State.conservation_error_pct === undefined) {
      return null;
    }
    const errorPct = Math.abs(v2State.conservation_error_pct);
    if (errorPct < 0.01) return { emoji: '✅', label: `${errorPct.toFixed(3)}%`, color: 'text-green-400' };
    if (errorPct < 1.0) return { emoji: '⚠️', label: `${errorPct.toFixed(2)}%`, color: 'text-yellow-400' };
    return { emoji: '🔴', label: `${errorPct.toFixed(1)}%`, color: 'text-red-400' };
  };

  const conservationStatus = getConservationStatus();

  // Get frontier metrics
  const frontierDisplay = (v2State.active_count !== null && v2State.shadow_count !== null) ? {
    active: v2State.active_count,
    shadow: v2State.shadow_count,
    total: v2State.active_count + v2State.shadow_count
  } : null;

  return (
    <div className="flex flex-col items-end gap-0.5 flex-shrink-0">
      {/* Frame counter with live pulse */}
      <div className="flex items-center gap-1.5">
        <div
          key={`pulse-${pulseKey}`}
          className={`w-1.5 h-1.5 rounded-full ${colors.pulse} animate-pulse`}
        />
        <span className={`text-xs ${colors.text}`}>
          frame {displayFrame} {getStateLabel()}
        </span>
      </div>

      {/* Thought Flow (rho) indicator */}
      {rhoDisplay && (
        <div className={`text-xs ${rhoDisplay.color} flex items-center gap-1`}>
          <span>{rhoDisplay.emoji}</span>
          <span>flow: {rhoDisplay.label}</span>
        </div>
      )}

      {/* Safety state (criticality) */}
      {safetyState && (
        <div className={`text-xs ${safetyState.color} flex items-center gap-1`}>
          <span>{safetyState.emoji}</span>
          <span>{safetyState.state}</span>
        </div>
      )}

      {/* Conservation error */}
      {conservationStatus && (
        <div className={`text-xs ${conservationStatus.color} flex items-center gap-1`}>
          <span>{conservationStatus.emoji}</span>
          <span>ΔE: {conservationStatus.label}</span>
        </div>
      )}

      {/* Frontier metrics */}
      {frontierDisplay && (
        <div className="text-xs text-gray-400 flex items-center gap-1">
          <span>🎯</span>
          <span>{frontierDisplay.active}+{frontierDisplay.shadow} nodes</span>
        </div>
      )}
    </div>
  );
}

