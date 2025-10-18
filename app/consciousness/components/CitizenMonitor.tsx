'use client';

import { useState, useEffect } from 'react';
import type { Entity } from '../hooks/useGraphData';

interface Citizen {
  id: string;
  name: string;
  state: 'active' | 'recently_active' | 'dormant' | 'stopped';
  lastThought: string;
  entities: Entity[];
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
}

interface CitizenMonitorProps {
  citizens: Citizen[];
  onFocusNode: (nodeId: string) => void;
}

/**
 * CitizenMonitor - Right sidebar accordion
 *
 * Shows all citizens with collapsible sections:
 * - Collapsed: State, last thought, color indicator
 * - Expanded: Full entity activity stream, CLAUDE_DYNAMIC.md viewer
 *
 * Clicking node references focuses that node on the graph.
 */
export function CitizenMonitor({ citizens, onFocusNode }: CitizenMonitorProps) {
  const [expandedCitizen, setExpandedCitizen] = useState<string | null>(null);

  return (
    <div className="fixed right-0 top-16 bottom-0 w-[28rem] consciousness-panel border-l border-consciousness-border overflow-hidden flex flex-col z-20">
      {/* Accordion - takes full height */}
      <div className="flex-1 overflow-y-auto custom-scrollbar pt-4">
        {citizens.map(citizen => (
          <CitizenAccordionItem
            key={citizen.id}
            citizen={citizen}
            isExpanded={expandedCitizen === citizen.id}
            onToggle={() => setExpandedCitizen(
              expandedCitizen === citizen.id ? null : citizen.id
            )}
            onFocusNode={onFocusNode}
          />
        ))}
      </div>
    </div>
  );
}

function CitizenAccordionItem({
  citizen,
  isExpanded,
  onToggle,
  onFocusNode
}: {
  citizen: Citizen;
  isExpanded: boolean;
  onToggle: () => void;
  onFocusNode: (nodeId: string) => void;
}) {
  const [apiStatus, setApiStatus] = useState<CitizenStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

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

  // Control handlers
  const handleFreeze = async () => {
    setIsLoading(true);
    try {
      await fetch(`/api/citizen/${citizen.id}/pause`, { method: 'POST' });
    } catch (error) {
      console.error('Failed to freeze:', error);
    }
    setIsLoading(false);
  };

  const handleResume = async () => {
    setIsLoading(true);
    try {
      await fetch(`/api/citizen/${citizen.id}/resume`, { method: 'POST' });
    } catch (error) {
      console.error('Failed to resume:', error);
    }
    setIsLoading(false);
  };

  // Use API status if available, otherwise fall back to mock data
  const runningState = apiStatus?.running_state ||
    (citizen.state === 'stopped' ? 'frozen' : 'running');
  const tickFrequency = apiStatus?.tick_frequency_hz ||
    (1000 / citizen.tickInterval);
  const consciousnessState = apiStatus?.consciousness_state || 'unknown';

  const stateColor = {
    running: 'bg-consciousness-green',
    frozen: 'bg-blue-500',
    slow_motion: 'bg-orange-500',
    turbo: 'bg-red-500'
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
    <div className="border-b border-consciousness-border relative">
      {/* Collapsed Header - Always Visible */}
      <div className="p-6">
        {/* Avatar + Name Row */}
        <div className="flex items-center gap-4 mb-4">
          {/* Avatar Image - Much Larger */}
          <div className="relative w-24 h-24 flex-shrink-0">
            <img
              src={avatarPath}
              alt={`${citizen.name} avatar`}
              className="w-full h-full object-cover rounded-xl border-3 border-consciousness-green/50"
              onError={(e) => {
                // Try SVG if PNG failed, otherwise use placeholder
                if (!avatarError && avatarPath.endsWith('.png')) {
                  setAvatarPath(`/citizens/${citizen.id}/avatar.svg`);
                  setAvatarError(true);
                } else {
                  e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23222" width="100" height="100"/><text x="50" y="50" text-anchor="middle" dy=".3em" fill="%235efc82" font-size="40">?</text></svg>';
                }
              }}
            />
            <div className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full border-2 border-consciousness-dark ${stateColor}`} />
          </div>

          {/* Name + Controls */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <button
                onClick={onToggle}
                className="flex-1 text-left min-w-0"
              >
                <div className="text-consciousness-green font-semibold text-lg">
                  {citizen.name}
                </div>
              </button>

              {/* Three-dot menu */}
              <div className="relative flex-shrink-0">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setMenuOpen(!menuOpen);
                  }}
                  className="p-2 hover:bg-consciousness-border/30 rounded transition-colors"
                >
                  <span className="text-gray-400 text-lg">⋮</span>
                </button>

                {/* Dropdown Menu */}
                {menuOpen && (
                  <>
                    {/* Backdrop to close menu */}
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setMenuOpen(false)}
                    />
                    {/* Menu */}
                    <div className="absolute right-0 top-full mt-1 w-48 consciousness-panel border border-consciousness-border rounded shadow-xl z-20">
                      {runningState === 'frozen' ? (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleResume();
                            setMenuOpen(false);
                          }}
                          disabled={isLoading}
                          className="w-full px-4 py-2 text-left text-sm hover:bg-consciousness-border/30 transition-colors flex items-center gap-2 disabled:opacity-50"
                        >
                          <span>▶️</span>
                          <span>{isLoading ? 'Resuming...' : 'Resume'}</span>
                        </button>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleFreeze();
                            setMenuOpen(false);
                          }}
                          disabled={isLoading}
                          className="w-full px-4 py-2 text-left text-sm hover:bg-consciousness-border/30 transition-colors flex items-center gap-2 disabled:opacity-50"
                        >
                          <span>❄️</span>
                          <span>{isLoading ? 'Freezing...' : 'Freeze'}</span>
                        </button>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Last Thought + Heartbeat */}
        <button
          onClick={onToggle}
          className="w-full text-left"
        >
          <div className="flex items-center gap-3 mb-2">
            {/* Last Thought - Preview */}
            <div className="text-sm text-gray-400 flex-1">
              {citizen.lastThought || 'No recent activity'}
            </div>

            {/* Compact Heartbeat Indicator */}
            <HeartbeatIndicator
              frequency={tickFrequency}
              state={runningState}
              consciousnessState={consciousnessState}
            />
          </div>

          {/* Entity count if available */}
          {apiStatus && apiStatus.sub_entity_count > 0 && (
            <div className="text-sm text-gray-500">
              {apiStatus.sub_entity_count} active {apiStatus.sub_entity_count === 1 ? 'entity' : 'entities'}
            </div>
          )}
        </button>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4">
          {/* Entity Activity Stream */}
          <div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">
              Active Entities
            </div>
            <div className="space-y-2">
              {citizen.entities.map(entity => (
                <EntityActivityCard
                  key={entity.entity_id}
                  entity={entity}
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
  entity,
  onFocusNode
}: {
  entity: Entity;
  onFocusNode: (nodeId: string) => void;
}) {
  return (
    <div className="consciousness-panel p-3 text-xs">
      <div className="flex items-center justify-between mb-2">
        <span className="text-consciousness-green font-medium">
          {entity.entity_id}
        </span>
        <span className="text-gray-500">
          {entity.energy_used}/{entity.energy_budget}
        </span>
      </div>

      {/* Current Yearning */}
      {entity.current_yearning && (
        <div className="text-gray-300 mb-2">
          {entity.current_yearning}
        </div>
      )}

      {/* Recent Path - Clickable */}
      {entity.recent_path && entity.recent_path.length > 0 && (
        <div className="space-y-1">
          <div className="text-gray-500">Recent path:</div>
          {entity.recent_path.slice(-5).map((node, i) => (
            <button
              key={i}
              onClick={() => onFocusNode(node.id)}
              className="block w-full text-left px-2 py-1 rounded hover:bg-consciousness-border/30 text-gray-400 hover:text-consciousness-green transition-colors"
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
        className="w-full text-left text-xs text-gray-400 uppercase tracking-wider mb-2 hover:text-consciousness-green transition-colors"
      >
        CLAUDE_DYNAMIC.md {isOpen ? '▼' : '▶'}
      </button>

      {isOpen && (
        <div className="consciousness-panel p-3 max-h-96 overflow-y-auto custom-scrollbar">
          <div className="text-xs text-gray-300 whitespace-pre-wrap">
            <div className="text-gray-500 italic">
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
 * Pulses at the actual tick frequency to make consciousness rhythm visible.
 * Color-coded by consciousness state for immediate status recognition.
 */
function HeartbeatIndicator({
  frequency,
  state,
  consciousnessState
}: {
  frequency: number;
  state: string;
  consciousnessState: string;
}) {
  const [pulseKey, setPulseKey] = useState(0);

  // Trigger pulse animation at actual tick frequency
  useEffect(() => {
    if (state === 'frozen' || frequency === 0) return;

    const interval = setInterval(() => {
      setPulseKey(prev => prev + 1);
    }, 1000 / frequency); // Pulse at actual tick rate

    return () => clearInterval(interval);
  }, [frequency, state]);

  // Color mapping for consciousness states
  const stateColors: Record<string, { bg: string; pulse: string; text: string }> = {
    alert: { bg: 'bg-red-500/20', pulse: 'bg-red-500', text: 'text-red-400' },
    engaged: { bg: 'bg-consciousness-green/20', pulse: 'bg-consciousness-green', text: 'text-consciousness-green' },
    calm: { bg: 'bg-blue-500/20', pulse: 'bg-blue-500', text: 'text-blue-400' },
    drowsy: { bg: 'bg-yellow-500/20', pulse: 'bg-yellow-500', text: 'text-yellow-400' },
    dormant: { bg: 'bg-gray-500/20', pulse: 'bg-gray-500', text: 'text-gray-400' },
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

  return (
    <div className="flex items-center gap-1.5 flex-shrink-0">
      {/* Animated pulse dot */}
      <div
        key={`pulse-${pulseKey}`}
        className={`w-1.5 h-1.5 rounded-full ${colors.pulse}`}
        style={{
          animation: `heartbeat ${1000 / frequency}ms ease-out`
        }}
      />
      <span className={`text-xs font-mono ${colors.text}`}>
        {displayText}
      </span>
    </div>
  );
}

