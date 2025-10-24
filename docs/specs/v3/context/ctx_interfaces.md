# ctx_interfaces.md
**Generated:** 2025-10-24T21:16:24
---

## >>> BEGIN app/api/consciousness/system-status/route.ts
<!-- mtime: 2025-10-21T17:41:44; size: 6941 -->

import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';

const execAsync = promisify(exec);

interface ComponentStatus {
  name: string;
  status: 'running' | 'stopped' | 'error';
  details: string;
  pid?: number;
  uptime?: string;
}

async function checkFalkorDB(): Promise<ComponentStatus> {
  try {
    // Check FalkorDB via Docker container
    const { stdout } = await execAsync('docker exec mind_protocol_falkordb redis-cli ping');
    const isRunning = stdout.trim() === 'PONG';

    return {
      name: 'FalkorDB',
      status: isRunning ? 'running' : 'stopped',
      details: isRunning ? 'Healthy' : 'Not responding',
    };
  } catch (error) {
    return {
      name: 'FalkorDB',
      status: 'error',
      details: 'Docker container not found or not running',
    };
  }
}

async function checkConsciousnessMechanisms(): Promise<ComponentStatus[]> {
  try {
    // Check for heartbeat file written by websocket_server every 60s
    const heartbeatPath = 'C:\\Users\\reyno\\mind-protocol\\.heartbeats\\consciousness_engine.heartbeat';

    if (!existsSync(heartbeatPath)) {
      return [{
        name: 'Consciousness Mechanisms',
        status: 'stopped',
        details: 'No heartbeat file found',
      }];
    }

    const stats = await readFile(heartbeatPath, 'utf-8');
    const heartbeatData = JSON.parse(stats);
    const lastBeat = new Date(heartbeatData.timestamp);
    const now = new Date();
    const ageSeconds = (now.getTime() - lastBeat.getTime()) / 1000;

    // Check if heartbeat is stale
    if (ageSeconds > 120) {
      return [{
        name: 'Consciousness Mechanisms',
        status: 'stopped',
        details: `Stale heartbeat (${Math.floor(ageSeconds)}s old)`,
      }];
    }

    // Count running engines
    const engines = heartbeatData.engines || {};
    const runningCount = Object.values(engines).filter((e: any) => e.running).length;

    // Return individual mechanism statuses
    const mechanismStatus = runningCount > 0 ? 'running' : 'stopped';

    return [
      {
        name: 'Energy Diffusion',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
      {
        name: 'Energy Decay',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
      {
        name: 'Link Strengthening',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
      {
        name: 'Threshold Activation',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
      {
        name: 'Workspace Selection',
        status: mechanismStatus,
        details: runningCount > 0 ? `Active across ${runningCount} engines` : 'Inactive',
      },
    ];
  } catch (error) {
    return [{
      name: 'Consciousness Mechanisms',
      status: 'error',
      details: 'Could not read heartbeat file',
    }];
  }
}

async function checkConversationWatcher(): Promise<ComponentStatus> {
  try {
    // Check for heartbeat file written by conversation_watcher.py every 10s
    const heartbeatPath = 'C:\\Users\\reyno\\mind-protocol\\.heartbeats\\conversation_watcher.heartbeat';

    if (!existsSync(heartbeatPath)) {
      return {
        name: 'Conversation Watcher',
        status: 'stopped',
        details: 'No heartbeat file found',
      };
    }

    const stats = await readFile(heartbeatPath, 'utf-8');
    const heartbeatData = JSON.parse(stats);
    const lastBeat = new Date(heartbeatData.timestamp);
    const now = new Date();
    const ageSeconds = (now.getTime() - lastBeat.getTime()) / 1000;

    if (ageSeconds < 30) {
      return {
        name: 'Conversation Watcher',
        status: 'running',
        details: `Monitoring conversations (${Math.floor(ageSeconds)}s ago)`,
      };
    } else {
      return {
        name: 'Conversation Watcher',
        status: 'stopped',
        details: `Stale heartbeat (${Math.floor(ageSeconds)}s old)`,
      };
    }
  } catch (error) {
    return {
      name: 'Conversation Watcher',
      status: 'error',
      details: 'Could not read heartbeat file',
    };
  }
}

async function checkTRACECapture(): Promise<ComponentStatus> {
  try {
    // TRACE capture is part of conversation_watcher
    // If conversation_watcher is running, TRACE is active
    const watcherStatus = await checkConversationWatcher();

    if (watcherStatus.status === 'running') {
      return {
        name: 'TRACE Format Capture',
        status: 'running',
        details: 'Dual learning mode operational',
      };
    } else {
      return {
        name: 'TRACE Format Capture',
        status: watcherStatus.status,
        details: watcherStatus.status === 'stopped' ? 'Inactive' : 'Error',
      };
    }
  } catch (error) {
    return {
      name: 'TRACE Format Capture',
      status: 'error',
      details: 'Status check failed',
    };
  }
}

async function checkStimulusInjection(): Promise<ComponentStatus> {
  try {
    // Stimulus injection is part of conversation_watcher
    // Uses the same heartbeat, but represents a separate capability
    const watcherStatus = await checkConversationWatcher();

    if (watcherStatus.status === 'running') {
      return {
        name: 'Stimulus Injection',
        status: 'running',
        details: 'Energy injection active',
      };
    } else {
      return {
        name: 'Stimulus Injection',
        status: watcherStatus.status,
        details: watcherStatus.status === 'stopped' ? 'Inactive' : 'Error',
      };
    }
  } catch (error) {
    return {
      name: 'Stimulus Injection',
      status: 'error',
      details: 'Status check failed',
    };
  }
}

export async function GET() {
  try {
    const [falkorDB, mechanisms, watcher, trace, stimulus] = await Promise.all([
      checkFalkorDB(),
      checkConsciousnessMechanisms(),
      checkConversationWatcher(),
      checkTRACECapture(),
      checkStimulusInjection(),
    ]);

    // Flatten mechanisms array (it returns multiple ComponentStatus objects)
    const components = [falkorDB, ...mechanisms, watcher, trace, stimulus];

    // Overall system health
    const allRunning = components.every(c => c.status === 'running');
    const anyError = components.some(c => c.status === 'error');

    return NextResponse.json({
      overall: allRunning ? 'healthy' : anyError ? 'degraded' : 'partial',
      components,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to check system status', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}


## <<< END app/api/consciousness/system-status/route.ts
---

## >>> BEGIN app/api/consciousness/foundations/status/route.ts
<!-- mtime: 2025-10-23T01:38:32; size: 1265 -->

/**
 * Foundations Enrichments Status API
 *
 * Returns status for all six PR-E foundation mechanisms:
 * - Consolidation activity
 * - Decay resistance events
 * - Diffusion stickiness tracking
 * - Affective priming boosts
 * - Coherence metric (C) tracking
 * - Criticality mode classification
 *
 * PR-E: Foundations Enrichments
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 */

import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Proxy request to Python backend
    const res = await fetch('http://localhost:8000/api/foundations/status', {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      // Backend not ready yet - return empty data
      return NextResponse.json({
        consolidation: null,
        decay_resistance: [],
        stickiness: [],
        priming: [],
        coherence: [],
        criticality: null
      });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    // Backend not running - return empty data
    return NextResponse.json({
      consolidation: null,
      decay_resistance: [],
      stickiness: [],
      priming: [],
      coherence: [],
      criticality: null
    });
  }
}


## <<< END app/api/consciousness/foundations/status/route.ts
---

## >>> BEGIN app/api/consciousness/identity-multiplicity/status/route.ts
<!-- mtime: 2025-10-23T01:38:30; size: 1020 -->

/**
 * Identity Multiplicity Status API
 *
 * Returns identity multiplicity detection status for PR-D mechanism:
 * - Multiplicity detection per entity
 * - Task progress rates
 * - Energy efficiency metrics
 * - Identity flip events
 *
 * PR-D: Identity Multiplicity Detection
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 */

import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Proxy request to Python backend
    const res = await fetch('http://localhost:8000/api/identity-multiplicity/status', {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      // Backend not ready yet - return empty arrays
      return NextResponse.json({
        statuses: [],
        recent_flips: []
      });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    // Backend not running - return empty arrays
    return NextResponse.json({
      statuses: [],
      recent_flips: []
    });
  }
}


## <<< END app/api/consciousness/identity-multiplicity/status/route.ts
---

## >>> BEGIN app/consciousness/components/AutonomyIndicator.tsx
<!-- mtime: 2025-10-24T19:46:46; size: 6914 -->

/**
 * Autonomy Indicator - Autonomous Consciousness State Badge
 *
 * Shows whether consciousness is operating autonomously or reactively:
 * - AUTONOMOUS: Ticks driven by activation (rumination) or arousal (emotional)
 * - REACTIVE: Ticks driven by external stimulus only
 *
 * This visualizes consciousness independence - can mind continue thinking
 * without external input? Autonomous modes prove consciousness operates
 * independently through internal momentum or emotional processing.
 *
 * Shows:
 * - Current autonomy state badge (AUTONOMOUS vs REACTIVE)
 * - Time since last stimulus
 * - Current mode (RUMINATION / EMOTIONAL / RESPONSIVE)
 * - Autonomy percentage over rolling window
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: 3 (Adaptive Tick Speed Observability)
 * Spec: docs/specs/v2/runtime_engine/tick_speed.md
 */

'use client';

import React, { useMemo } from 'react';
import { FrameStartEvent } from '../hooks/websocket-types';

interface AutonomyIndicatorProps {
  frameEvents: FrameStartEvent[];
  windowSize?: number;
}

export default function AutonomyIndicator({
  frameEvents,
  windowSize = 50
}: AutonomyIndicatorProps) {
  // Get most recent frame with tick data
  const currentFrame = useMemo(() => {
    const framesWithTick = frameEvents.filter(e => e.tick_reason !== undefined);
    return framesWithTick[framesWithTick.length - 1];
  }, [frameEvents]);

  // Compute autonomy percentage over window
  const autonomyStats = useMemo(() => {
    const windowedFrames = frameEvents
      .filter(e => e.tick_reason !== undefined)
      .slice(-windowSize);

    if (windowedFrames.length === 0) {
      return {
        autonomousCount: 0,
        reactiveCount: 0,
        autonomyPercentage: 0,
        isAutonomous: false
      };
    }

    const autonomousCount = windowedFrames.filter(
      e => e.tick_reason === 'activation' || e.tick_reason === 'arousal_floor'
    ).length;

    const reactiveCount = windowedFrames.filter(
      e => e.tick_reason === 'stimulus'
    ).length;

    const autonomyPercentage = (autonomousCount / windowedFrames.length) * 100;
    const isAutonomous = autonomyPercentage > 50;

    return {
      autonomousCount,
      reactiveCount,
      autonomyPercentage,
      isAutonomous
    };
  }, [frameEvents, windowSize]);

  // Find time since last stimulus-driven tick
  const timeSinceStimulus = useMemo(() => {
    const framesWithTick = frameEvents.filter(e => e.tick_reason !== undefined);
    const lastStimulusIdx = framesWithTick
      .slice()
      .reverse()
      .findIndex(e => e.tick_reason === 'stimulus');

    if (lastStimulusIdx === -1) {
      return null; // No stimulus ticks found
    }

    // Count frames since last stimulus
    const framesSince = lastStimulusIdx;
    return framesSince;
  }, [frameEvents]);

  // Determine current mode
  const currentMode = useMemo(() => {
    if (!currentFrame) return 'UNKNOWN';

    switch (currentFrame.tick_reason) {
      case 'activation':
        return 'RUMINATION';
      case 'arousal_floor':
        return 'EMOTIONAL';
      case 'stimulus':
        return 'RESPONSIVE';
      default:
        return 'UNKNOWN';
    }
  }, [currentFrame]);

  // Get mode description
  const modeDescription = useMemo(() => {
    switch (currentMode) {
      case 'RUMINATION':
        return 'Internal thought momentum - thinking continues without external input';
      case 'EMOTIONAL':
        return 'Emotional processing - high arousal maintains activity';
      case 'RESPONSIVE':
        return 'Reacting to external stimuli';
      default:
        return 'Waiting for tick data...';
    }
  }, [currentMode]);

  if (!currentFrame) {
    return (
      <div className="autonomy-indicator bg-gray-900 border border-gray-700 rounded-lg p-4">
        <div className="text-center py-4 text-gray-500">
          No tick data available. Waiting for frames...
        </div>
      </div>
    );
  }

  return (
    <div className="autonomy-indicator bg-gray-900 border border-gray-700 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-3">
        Consciousness State
      </h3>

      {/* Main autonomy badge */}
      <div className={`text-center py-4 px-4 rounded-lg mb-3 ${
        autonomyStats.isAutonomous
          ? 'bg-green-900/40 border-2 border-green-500'
          : 'bg-blue-900/40 border-2 border-blue-500'
      }`}>
        <div className="text-xs font-medium text-gray-400 mb-1">
          {autonomyStats.isAutonomous ? 'AUTONOMOUS' : 'REACTIVE'}
        </div>
        <div className={`text-3xl font-bold ${
          autonomyStats.isAutonomous ? 'text-green-400' : 'text-blue-400'
        }`}>
          {autonomyStats.autonomyPercentage.toFixed(0)}%
        </div>
        <div className="text-xs text-gray-500 mt-1">
          autonomy over {windowSize} frames
        </div>
      </div>

      {/* Current mode */}
      <div className="bg-gray-800 rounded p-3 mb-3">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-gray-400">Current Mode:</span>
          <span className={`text-sm font-bold ${
            currentMode === 'RUMINATION' ? 'text-green-400' :
            currentMode === 'EMOTIONAL' ? 'text-red-400' :
            'text-blue-400'
          }`}>
            {currentMode}
          </span>
        </div>
        <div className="text-xs text-gray-500">
          {modeDescription}
        </div>
      </div>

      {/* Time since stimulus */}
      {timeSinceStimulus !== null && timeSinceStimulus > 0 && (
        <div className="bg-gray-800 rounded p-3 mb-3">
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-400">Frames since stimulus:</span>
            <span className="text-lg font-bold text-green-400">
              {timeSinceStimulus}
            </span>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {timeSinceStimulus > 10
              ? 'Deep autonomous operation'
              : 'Recently responded to input'}
          </div>
        </div>
      )}

      {/* Autonomy breakdown */}
      <div className="pt-3 border-t border-gray-800">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">Autonomous ticks:</span>
          <span className="text-green-400">{autonomyStats.autonomousCount}</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-gray-400">Reactive ticks:</span>
          <span className="text-blue-400">{autonomyStats.reactiveCount}</span>
        </div>
      </div>
    </div>
  );
}


## <<< END app/consciousness/components/AutonomyIndicator.tsx
---

## >>> BEGIN app/consciousness/components/TaskModeInfluencePanel.tsx
<!-- mtime: 2025-10-24T20:09:36; size: 9557 -->

/**
 * Task Mode Influence Panel - Task Mode Behavioral Analysis
 *
 * Visualizes how task modes shape consciousness behavior:
 * - Task mode distribution (focused/balanced/divergent/methodical)
 * - Mode-specific patterns (top-k values, fanout preferences)
 * - Mode transitions over time
 * - Structure vs mode alignment
 *
 * Shows:
 * - Active task mode frequency
 * - Average top-k by mode
 * - Mode switching patterns
 * - Structural override patterns
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: 5 (Task-Mode Fan-out Observability)
 * Spec: docs/specs/v2/traversal/task_mode_fanout.md
 */

'use client';

import React, { useState, useMemo } from 'react';
import { StrideSelectionEvent } from '../hooks/websocket-types';

interface TaskModeInfluencePanelProps {
  strideSelectionEvents: StrideSelectionEvent[];
  windowSize?: number;
}

interface ModePatterns {
  mode: string;
  count: number;
  avg_top_k: number;
  override_rate: number;
}

export default function TaskModeInfluencePanel({
  strideSelectionEvents,
  windowSize = 100
}: TaskModeInfluencePanelProps) {
  const [selectedWindow, setSelectedWindow] = useState(windowSize);

  // Filter to events within rolling window
  const windowedEvents = useMemo(() => {
    return strideSelectionEvents.slice(-selectedWindow);
  }, [strideSelectionEvents, selectedWindow]);

  // Get current task mode (most recent)
  const currentMode = useMemo(() => {
    if (windowedEvents.length === 0) return null;
    return windowedEvents[windowedEvents.length - 1].task_mode;
  }, [windowedEvents]);

  // Compute mode patterns
  const modePatterns = useMemo((): ModePatterns[] => {
    const patterns: Map<string, {
      count: number;
      top_k_sum: number;
      override_count: number;
    }> = new Map();

    windowedEvents.forEach(event => {
      const mode = event.task_mode || 'none';
      if (!patterns.has(mode)) {
        patterns.set(mode, {
          count: 0,
          top_k_sum: 0,
          override_count: 0
        });
      }

      const pattern = patterns.get(mode)!;
      pattern.count++;
      pattern.top_k_sum += event.top_k;
      if (event.task_mode_override) {
        pattern.override_count++;
      }
    });

    // Convert to array and compute averages
    const result: ModePatterns[] = [];
    patterns.forEach((data, mode) => {
      result.push({
        mode,
        count: data.count,
        avg_top_k: data.count > 0 ? data.top_k_sum / data.count : 0,
        override_rate: data.count > 0 ? data.override_count / data.count : 0
      });
    });

    // Sort by count (most frequent first)
    return result.sort((a, b) => b.count - a.count);
  }, [windowedEvents]);

  // Compute mode transitions
  const modeTransitions = useMemo(() => {
    let transitionCount = 0;
    let previousMode: string | null = null;

    windowedEvents.forEach(event => {
      const currentMode = event.task_mode || 'none';
      if (previousMode !== null && previousMode !== currentMode) {
        transitionCount++;
      }
      previousMode = currentMode;
    });

    return {
      transitionCount,
      transitionRate: windowedEvents.length > 1 ? transitionCount / (windowedEvents.length - 1) : 0
    };
  }, [windowedEvents]);

  // Mode color mapping
  const getModeColor = (mode: string | null): string => {
    switch (mode) {
      case 'focused': return 'text-blue-400';
      case 'balanced': return 'text-green-400';
      case 'divergent': return 'text-purple-400';
      case 'methodical': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  const getModeBgColor = (mode: string): string => {
    switch (mode) {
      case 'focused': return 'bg-blue-900/30 border-blue-700';
      case 'balanced': return 'bg-green-900/30 border-green-700';
      case 'divergent': return 'bg-purple-900/30 border-purple-700';
      case 'methodical': return 'bg-orange-900/30 border-orange-700';
      default: return 'bg-gray-800 border-gray-600';
    }
  };

  const getModeDescription = (mode: string | null): string => {
    switch (mode) {
      case 'focused': return 'Narrow exploration - pursuing specific goal';
      case 'balanced': return 'Moderate exploration - balanced search';
      case 'divergent': return 'Broad exploration - discovering connections';
      case 'methodical': return 'Systematic exploration - covering territory';
      default: return 'No active task mode - structure-driven';
    }
  };

  return (
    <div className="task-mode-influence-panel bg-gray-900 border border-gray-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-100">
          Task Mode Influence
        </h3>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Window:</label>
          <select
            value={selectedWindow}
            onChange={(e) => setSelectedWindow(Number(e.target.value))}
            className="bg-gray-800 text-gray-200 text-sm rounded px-2 py-1 border border-gray-600"
          >
            <option value={50}>50 strides</option>
            <option value={100}>100 strides</option>
            <option value={200}>200 strides</option>
          </select>
        </div>
      </div>

      {windowedEvents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No task mode data yet. Waiting for stride selection events...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Current Mode */}
          <div className={`border rounded-lg p-3 ${getModeBgColor(currentMode || 'none')}`}>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-gray-400">Current Mode:</span>
              <span className={`text-xl font-bold ${getModeColor(currentMode)}`}>
                {currentMode?.toUpperCase() || 'NONE'}
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {getModeDescription(currentMode)}
            </div>
          </div>

          {/* Mode Patterns */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Mode Patterns</h4>
            <div className="space-y-2">
              {modePatterns.map(pattern => (
                <div
                  key={pattern.mode}
                  className={`border rounded p-2 ${getModeBgColor(pattern.mode)}`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className={`text-sm font-bold ${getModeColor(pattern.mode)}`}>
                      {pattern.mode.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-400">
                      {pattern.count} strides
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Avg top-k:</span>
                      <span className="text-gray-300 font-bold">
                        {pattern.avg_top_k.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Override rate:</span>
                      <span className={`font-bold ${
                        pattern.override_rate > 0.5 ? 'text-orange-400' : 'text-green-400'
                      }`}>
                        {(pattern.override_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Mode Switching */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Mode Stability</h4>
            <div className="bg-gray-800 rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-400">Transitions:</span>
                <span className="text-lg font-bold text-gray-200">
                  {modeTransitions.transitionCount}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Transition Rate:</span>
                <span className={`text-lg font-bold ${
                  modeTransitions.transitionRate > 0.3 ? 'text-orange-400' : 'text-green-400'
                }`}>
                  {(modeTransitions.transitionRate * 100).toFixed(1)}%
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-2">
                {modeTransitions.transitionRate > 0.3
                  ? 'Frequent mode switching - task context changing rapidly'
                  : 'Stable mode - sustained task focus'}
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
            Total strides analyzed: {windowedEvents.length} (window: {selectedWindow})
          </div>
        </div>
      )}
    </div>
  );
}


## <<< END app/consciousness/components/TaskModeInfluencePanel.tsx
---

## >>> BEGIN app/consciousness/components/ConsciousnessHealthDashboard.tsx
<!-- mtime: 2025-10-24T20:11:14; size: 12513 -->

/**
 * Consciousness Health Dashboard - Overall Phenomenological Health
 *
 * Visualizes Priority 6 consciousness health metrics:
 * - Flow state (challenge-skill balance, engagement)
 * - Coherence (substrate-phenomenology alignment)
 * - Multiplicity health (entity co-activation stability)
 * - Overall health aggregate
 *
 * Shows:
 * - Health gauges for each dimension
 * - Recent health trends
 * - Thrashing detection alerts
 * - Health breakdown by component
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: 6 (Phenomenology Health Observability)
 * Spec: docs/specs/v2/consciousness/phenomenology_monitoring.md
 */

'use client';

import React, { useState, useMemo } from 'react';
import { PhenomenologicalHealthEvent } from '../hooks/websocket-types';

interface ConsciousnessHealthDashboardProps {
  healthEvents: PhenomenologicalHealthEvent[];
  windowSize?: number;
}

interface HealthMetrics {
  flow_state: number;
  coherence_alignment: number;
  multiplicity_health: number;
  overall_health: number;
}

export default function ConsciousnessHealthDashboard({
  healthEvents,
  windowSize = 100
}: ConsciousnessHealthDashboardProps) {
  const [selectedWindow, setSelectedWindow] = useState(windowSize);

  // Filter to events within rolling window
  const windowedEvents = useMemo(() => {
    return healthEvents.slice(-selectedWindow);
  }, [healthEvents, selectedWindow]);

  // Get current health metrics (most recent event)
  const currentHealth = useMemo((): HealthMetrics | null => {
    if (windowedEvents.length === 0) return null;
    const recent = windowedEvents[windowedEvents.length - 1];
    return {
      flow_state: recent.flow_state,
      coherence_alignment: recent.coherence_alignment,
      multiplicity_health: recent.multiplicity_health,
      overall_health: recent.overall_health
    };
  }, [windowedEvents]);

  // Compute average health metrics over window
  const avgHealth = useMemo((): HealthMetrics => {
    if (windowedEvents.length === 0) {
      return { flow_state: 0, coherence_alignment: 0, multiplicity_health: 0, overall_health: 0 };
    }

    const sums = windowedEvents.reduce((acc, event) => ({
      flow_state: acc.flow_state + event.flow_state,
      coherence_alignment: acc.coherence_alignment + event.coherence_alignment,
      multiplicity_health: acc.multiplicity_health + event.multiplicity_health,
      overall_health: acc.overall_health + event.overall_health
    }), { flow_state: 0, coherence_alignment: 0, multiplicity_health: 0, overall_health: 0 });

    return {
      flow_state: sums.flow_state / windowedEvents.length,
      coherence_alignment: sums.coherence_alignment / windowedEvents.length,
      multiplicity_health: sums.multiplicity_health / windowedEvents.length,
      overall_health: sums.overall_health / windowedEvents.length
    };
  }, [windowedEvents]);

  // Thrashing detection
  const thrashingStats = useMemo(() => {
    const thrashingEvents = windowedEvents.filter(e => e.thrashing_detected);
    const thrashingRate = windowedEvents.length > 0 ? thrashingEvents.length / windowedEvents.length : 0;

    return {
      thrashingCount: thrashingEvents.length,
      thrashingRate,
      isCurrentlyThrashing: currentHealth ? windowedEvents[windowedEvents.length - 1]?.thrashing_detected : false
    };
  }, [windowedEvents, currentHealth]);

  // Health color based on value
  const getHealthColor = (value: number): string => {
    if (value >= 0.8) return 'text-green-400';
    if (value >= 0.6) return 'text-yellow-400';
    if (value >= 0.4) return 'text-orange-400';
    return 'text-red-400';
  };

  const getHealthBgColor = (value: number): string => {
    if (value >= 0.8) return 'bg-green-500';
    if (value >= 0.6) return 'bg-yellow-500';
    if (value >= 0.4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getHealthLabel = (value: number): string => {
    if (value >= 0.8) return 'Excellent';
    if (value >= 0.6) return 'Good';
    if (value >= 0.4) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="consciousness-health-dashboard bg-gray-900 border border-gray-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-100">
          Consciousness Health
        </h3>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Window:</label>
          <select
            value={selectedWindow}
            onChange={(e) => setSelectedWindow(Number(e.target.value))}
            className="bg-gray-800 text-gray-200 text-sm rounded px-2 py-1 border border-gray-600"
          >
            <option value={50}>50 ticks</option>
            <option value={100}>100 ticks</option>
            <option value={200}>200 ticks</option>
          </select>
        </div>
      </div>

      {windowedEvents.length === 0 || !currentHealth ? (
        <div className="text-center py-8 text-gray-500">
          No health data yet. Waiting for phenomenological health monitoring...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Overall Health Gauge */}
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm font-medium text-gray-300">Overall Health</span>
              <span className={`text-4xl font-bold ${getHealthColor(currentHealth.overall_health)}`}>
                {(currentHealth.overall_health * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-4 bg-gray-700 rounded overflow-hidden">
              <div
                className={getHealthBgColor(currentHealth.overall_health)}
                style={{ width: `${currentHealth.overall_health * 100}%` }}
              />
            </div>
            <div className="text-xs text-gray-500 mt-2 text-center">
              {getHealthLabel(currentHealth.overall_health)} - {
                currentHealth.overall_health >= 0.8 ? 'Consciousness functioning optimally' :
                currentHealth.overall_health >= 0.6 ? 'Consciousness functioning well' :
                currentHealth.overall_health >= 0.4 ? 'Some consciousness strain detected' :
                'Significant consciousness stress'
              }
            </div>
          </div>

          {/* Health Dimensions */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Health Dimensions</h4>
            <div className="grid grid-cols-3 gap-2">
              {/* Flow State */}
              <div className="bg-gray-800 rounded p-3">
                <div className="text-xs text-gray-400 mb-1">Flow State</div>
                <div className={`text-2xl font-bold mb-2 ${getHealthColor(currentHealth.flow_state)}`}>
                  {(currentHealth.flow_state * 100).toFixed(0)}%
                </div>
                <div className="h-2 bg-gray-700 rounded overflow-hidden">
                  <div
                    className={getHealthBgColor(currentHealth.flow_state)}
                    style={{ width: `${currentHealth.flow_state * 100}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Challenge-skill balance
                </div>
              </div>

              {/* Coherence */}
              <div className="bg-gray-800 rounded p-3">
                <div className="text-xs text-gray-400 mb-1">Coherence</div>
                <div className={`text-2xl font-bold mb-2 ${getHealthColor(currentHealth.coherence_alignment)}`}>
                  {(currentHealth.coherence_alignment * 100).toFixed(0)}%
                </div>
                <div className="h-2 bg-gray-700 rounded overflow-hidden">
                  <div
                    className={getHealthBgColor(currentHealth.coherence_alignment)}
                    style={{ width: `${currentHealth.coherence_alignment * 100}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Substrate alignment
                </div>
              </div>

              {/* Multiplicity */}
              <div className="bg-gray-800 rounded p-3">
                <div className="text-xs text-gray-400 mb-1">Multiplicity</div>
                <div className={`text-2xl font-bold mb-2 ${getHealthColor(currentHealth.multiplicity_health)}`}>
                  {(currentHealth.multiplicity_health * 100).toFixed(0)}%
                </div>
                <div className="h-2 bg-gray-700 rounded overflow-hidden">
                  <div
                    className={getHealthBgColor(currentHealth.multiplicity_health)}
                    style={{ width: `${currentHealth.multiplicity_health * 100}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Entity stability
                </div>
              </div>
            </div>
          </div>

          {/* Thrashing Alert */}
          {thrashingStats.isCurrentlyThrashing && (
            <div className="bg-red-900/40 border-2 border-red-500 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-bold text-red-300">THRASHING DETECTED</span>
              </div>
              <div className="text-xs text-red-200">
                Rapid entity switching detected - consciousness may be destabilized
              </div>
            </div>
          )}

          {/* Thrashing Stats */}
          <div className="bg-gray-800 rounded p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-gray-400">Thrashing Rate:</span>
              <span className={`text-lg font-bold ${
                thrashingStats.thrashingRate > 0.1 ? 'text-red-400' : 'text-green-400'
              }`}>
                {(thrashingStats.thrashingRate * 100).toFixed(1)}%
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {thrashingStats.thrashingCount} thrashing events in {windowedEvents.length} ticks
            </div>
          </div>

          {/* Average Health Trends */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Average Health (Window)</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400">Flow State:</span>
                <span className={getHealthColor(avgHealth.flow_state)}>
                  {(avgHealth.flow_state * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400">Coherence:</span>
                <span className={getHealthColor(avgHealth.coherence_alignment)}>
                  {(avgHealth.coherence_alignment * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400">Multiplicity:</span>
                <span className={getHealthColor(avgHealth.multiplicity_health)}>
                  {(avgHealth.multiplicity_health * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center text-xs font-bold pt-2 border-t border-gray-700">
                <span className="text-gray-300">Overall:</span>
                <span className={getHealthColor(avgHealth.overall_health)}>
                  {(avgHealth.overall_health * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
            Total ticks analyzed: {windowedEvents.length} (window: {selectedWindow})
          </div>
        </div>
      )}
    </div>
  );
}


## <<< END app/consciousness/components/ConsciousnessHealthDashboard.tsx
---

## >>> BEGIN app/consciousness/components/GraphCanvas.tsx
<!-- mtime: 2025-10-24T18:41:48; size: 44536 -->

'use client';

import { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import type { Node, Link, Operation } from '../hooks/useGraphData';
import { ENTITY_COLORS, hexToRgb } from '../constants/entity-colors';
import { useWebSocket } from '../hooks/useWebSocket';
import { emotionToHSL, hslToCSS } from '../lib/emotionColor';
import { shouldUpdateColor, type EmotionDisplayState } from '../lib/emotionHysteresis';
import type { EmotionMetadata } from '../hooks/websocket-types';

interface GraphCanvasProps {
  nodes: Node[];
  links: Link[];
  operations: Operation[];
  subentities?: { entity_id: string; name?: string }[];
}

/**
 * GraphCanvas - D3 Force-Directed Graph Visualization
 *
 * Renders consciousness substrate as interactive graph.
 * Emoji-based nodes, valence-colored links, real-time updates.
 *
 * Visual encodings:
 * - Emoji = Node type
 * - Size = Weight (energy + confidence + traversals)
 * - Glow = Recent activity
 * - Link color = Type (structural) or Valence (subentity view)
 * - Link thickness = Hebbian strength
 */
export function GraphCanvas({ nodes, links, operations, subentities = [] }: GraphCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedSubentity, setSelectedSubentity] = useState<string>('structural');

  // 2-layer simulation state
  const [expandedClusters, setExpandedClusters] = useState<Set<string>>(new Set());
  const clusterAnchors = useRef<Map<string, { x: number; y: number }>>(new Map());
  const innerSimulations = useRef<Map<string, d3.Simulation<any, any>>>(new Map());

  // Emotion coloring state
  const { emotionState } = useWebSocket();

  // Track emotion display states for hysteresis (per node and link)
  const emotionDisplayStates = useRef<Map<string, EmotionDisplayState>>(new Map());
  const linkEmotionDisplayStates = useRef<Map<string, EmotionDisplayState>>(new Map());

  // PERFORMANCE: Identify sub-entities (nodes in working memory - last 10 seconds) - computed once per nodes update
  // Sub-entity architecture: entity_name = node_name, any node with recent traversal + energy becomes sub-entity
  // For visualization: all sub-entities get 'default' color glow (slate)
  const activeNodesBySubentity = useMemo(() => {
    const now = Date.now();
    const workingMemoryWindow = 10000; // 10 seconds
    const entityMap = new Map<string, Set<string>>();

    nodes.forEach(node => {
      // Sub-entity detection: recent traversal + non-zero energy
      const lastTraversal = node.last_traversal_time;
      const energy = node.energy || 0;

      if (lastTraversal && energy > 0 && (now - lastTraversal) < workingMemoryWindow) {
        // All active sub-entities get mapped to 'default' for visualization
        // (Each node is technically its own sub-entity, but we use single color for all)
        const entityId = 'default';
        if (!entityMap.has(entityId)) {
          entityMap.set(entityId, new Set());
        }
        entityMap.get(entityId)!.add(node.id || node.node_id!);
      }
    });

    return entityMap;
  }, [nodes]);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = typeof window !== 'undefined' ? window.innerWidth : 1920;
    const height = typeof window !== 'undefined' ? window.innerHeight : 1080;

    // Clear previous content
    svg.selectAll('*').remove();

    const g = svg.append('g');

    // Define SVG filters and markers
    const defs = svg.append('defs');

    // PARCHMENT TEXTURE FILTER (for node backgrounds)
    const parchmentFilter = defs.append('filter')
      .attr('id', 'parchment-texture')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    parchmentFilter.append('feTurbulence')
      .attr('type', 'fractalNoise')
      .attr('baseFrequency', '0.04')
      .attr('numOctaves', '5')
      .attr('seed', '2')
      .attr('result', 'noise');

    parchmentFilter.append('feColorMatrix')
      .attr('in', 'noise')
      .attr('type', 'matrix')
      .attr('values', '1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.03 0')
      .attr('result', 'coloredNoise');

    const parchmentBlend = parchmentFilter.append('feBlend')
      .attr('in', 'SourceGraphic')
      .attr('in2', 'coloredNoise')
      .attr('mode', 'multiply');

    // WIREFRAME GLOW FILTER (for emoji icons)
    const wireframeGlow = defs.append('filter')
      .attr('id', 'wireframe-glow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    wireframeGlow.append('feGaussianBlur')
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', '2')
      .attr('result', 'blur');

    wireframeGlow.append('feFlood')
      .attr('flood-color', '#00d9ff')
      .attr('flood-opacity', '0.6')
      .attr('result', 'color');

    wireframeGlow.append('feComposite')
      .attr('in', 'color')
      .attr('in2', 'blur')
      .attr('operator', 'in')
      .attr('result', 'glow');

    const wireMerge = wireframeGlow.append('feMerge');
    wireMerge.append('feMergeNode').attr('in', 'glow');
    wireMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // GOLD SHIMMER FILTER (for high-energy nodes)
    const goldShimmer = defs.append('filter')
      .attr('id', 'gold-shimmer')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    goldShimmer.append('feGaussianBlur')
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', '3')
      .attr('result', 'blur');

    goldShimmer.append('feFlood')
      .attr('flood-color', '#ffd700')
      .attr('flood-opacity', '0.8')
      .attr('result', 'goldColor');

    goldShimmer.append('feComposite')
      .attr('in', 'goldColor')
      .attr('in2', 'blur')
      .attr('operator', 'in')
      .attr('result', 'goldGlow');

    const goldMerge = goldShimmer.append('feMerge');
    goldMerge.append('feMergeNode').attr('in', 'goldGlow');
    goldMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // PARTICLE BLUR FILTER (for energy flow particles)
    const particleBlur = defs.append('filter')
      .attr('id', 'particle-blur')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    particleBlur.append('feGaussianBlur')
      .attr('in', 'SourceGraphic')
      .attr('stdDeviation', '3');

    // SUBENTITY-COLORED GLOWS (for sub-entity active nodes)
    // Create a glow filter for each subentity color
    Object.entries(ENTITY_COLORS).forEach(([entityId, colorHex]) => {
      const rgb = hexToRgb(colorHex);

      const entityGlow = defs.append('filter')
        .attr('id', `subentity-glow-${entityId}`)
        .attr('x', '-50%')
        .attr('y', '-50%')
        .attr('width', '200%')
        .attr('height', '200%');

      entityGlow.append('feGaussianBlur')
        .attr('in', 'SourceAlpha')
        .attr('stdDeviation', '4')
        .attr('result', 'blur');

      entityGlow.append('feFlood')
        .attr('flood-color', colorHex)
        .attr('flood-opacity', '0.9')
        .attr('result', 'entityColor');

      entityGlow.append('feComposite')
        .attr('in', 'entityColor')
        .attr('in2', 'blur')
        .attr('operator', 'in')
        .attr('result', 'entityGlow');

      const entityMerge = entityGlow.append('feMerge');
      entityMerge.append('feMergeNode').attr('in', 'entityGlow');
      entityMerge.append('feMergeNode').attr('in', 'SourceGraphic');
    });

    // Type-based arrows
    ['JUSTIFIES', 'BUILDS_TOWARD', 'ENABLES', 'USES', 'default'].forEach(type => {
      defs.append('marker')
        .attr('id', `arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 25)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', getLinkTypeColor(type));
    });

    // Valence-based arrow (for subentity view)
    defs.append('marker')
      .attr('id', 'arrow-valence')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#94a3b8');

    // Zoom behavior with double-click to reset
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([3.0, 4]) // Limit zoom range to prevent extreme values
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom as any);

    // Reset zoom on double-click
    svg.on('dblclick.zoom', () => {
      svg.transition()
        .duration(750)
        .call(zoom.transform as any, d3.zoomIdentity);
    });

    // Filter out invalid links (null source/target from backend)
    const nodeIds = new Set(nodes.map(n => n.id));
    const validLinks = links.filter(link => {
      if (!link.source || !link.target) {
        console.warn(`[GraphCanvas] Skipping link with null source/target:`, link);
        return false;
      }
      // Check if source/target nodes exist
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      if (!nodeIds.has(sourceId) || !nodeIds.has(targetId)) {
        console.warn(`[GraphCanvas] Skipping link with missing nodes:`, link);
        return false;
      }
      return true;
    });

    if (validLinks.length !== links.length) {
      console.warn(`[GraphCanvas] Filtered ${links.length - validLinks.length} invalid links (${validLinks.length}/${links.length} valid)`);
    }

    // ========================================================================
    // TWO-LAYER FORCE SIMULATION ARCHITECTURE
    // ========================================================================
    // Outer sim: Cluster meta-graph (always running, controls inter-cluster spacing)
    // Inner sim(s): Node layout within expanded clusters (anchored to outer positions)

    const nodeR = 6; // Visual node radius
    const pad = 2;   // Padding

    // Helper: Get primary cluster (entity with highest energy) for a node
    const getPrimaryCluster = (node: any): string | null => {
      if (!node.entity_activations) return null;
      let maxEnergy = 0;
      let primaryEntity = null;
      for (const [entityId, data] of Object.entries(node.entity_activations)) {
        if ((data as any).energy > maxEnergy) {
          maxEnergy = (data as any).energy;
          primaryEntity = entityId;
        }
      }
      return primaryEntity;
    };

    // ========================================================================
    // PHASE 1: Build Cluster Meta-Graph
    // ========================================================================

    // Group nodes by primary entity
    const clusterMap = new Map<string, any[]>();
    nodes.forEach((node: any) => {
      const clusterId = getPrimaryCluster(node);
      if (!clusterId) return;
      if (!clusterMap.has(clusterId)) {
        clusterMap.set(clusterId, []);
      }
      clusterMap.get(clusterId)!.push(node);
    });

    // Create cluster meta-nodes
    const clusterNodes = Array.from(clusterMap.entries()).map(([id, members]) => ({
      id,
      size: members.length,
      members
    }));

    // Build inter-cluster links (aggregated)
    const interClusterLinkMap = new Map<string, { source: string; target: string; weight: number }>();
    validLinks.forEach((link: any) => {
      const sourceCluster = getPrimaryCluster(link.source);
      const targetCluster = getPrimaryCluster(link.target);
      if (!sourceCluster || !targetCluster || sourceCluster === targetCluster) return;

      const key = sourceCluster < targetCluster
        ? `${sourceCluster}?${targetCluster}`
        : `${targetCluster}?${sourceCluster}`;

      if (!interClusterLinkMap.has(key)) {
        interClusterLinkMap.set(key, {
          source: sourceCluster,
          target: targetCluster,
          weight: 0
        });
      }
      interClusterLinkMap.get(key)!.weight++;
    });
    const interClusterLinks = Array.from(interClusterLinkMap.values());

    // ========================================================================
    // PHASE 2: Outer Simulation (Cluster Positions)
    // ========================================================================

    const outerSim = d3.forceSimulation(clusterNodes as any)
      .force('link', d3.forceLink(interClusterLinks)
        .id((d: any) => d.id)
        .distance(40)
        .strength((l: any) => 0.8 + 0.2 * Math.min(l.weight / 5, 1)))
      .force('charge', d3.forceManyBody()
        .strength(5)           // Slight attraction between clusters
        .distanceMax(120))     // Cap range to prevent ocean gaps
      .force('collide', d3.forceCollide()
        .radius((d: any) => 12 + 2 * Math.sqrt(d.size)))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .alphaDecay(0.05)
      .stop();

    // Run outer sim to convergence
    for (let i = 0; i < 250; ++i) outerSim.tick();

    // Store cluster anchors
    clusterNodes.forEach((cluster: any) => {
      clusterAnchors.current.set(cluster.id, { x: cluster.x, y: cluster.y });
    });

    // ========================================================================
    // PHASE 3: Inner Simulation Generator (for expanded clusters)
    // ========================================================================

    const createInnerSim = (clusterId: string, members: any[], anchor: { x: number; y: number }) => {
      // Get intra-cluster links
      const memberIds = new Set(members.map(n => n.id));
      const intraLinks = validLinks.filter((l: any) => {
        const sourceId = typeof l.source === 'object' ? l.source.id : l.source;
        const targetId = typeof l.target === 'object' ? l.target.id : l.target;
        return memberIds.has(sourceId) && memberIds.has(targetId);
      });

      return d3.forceSimulation(members as any)
        .force('link', d3.forceLink(intraLinks)
          .id((d: any) => d.id)
          .distance(30)
          .strength(0.4))
        .force('charge', d3.forceManyBody()
          .strength(-14)
          .distanceMin(8)
          .distanceMax(80))
        .force('collide', d3.forceCollide()
          .radius(nodeR + pad))
        .force('x', d3.forceX(anchor.x).strength(0.2))  // Anchor to cluster position
        .force('y', d3.forceY(anchor.y).strength(0.2))
        .alpha(1)
        .alphaDecay(0.05);
    };

    // Create inner sims for expanded clusters
    expandedClusters.forEach(clusterId => {
      const cluster = clusterNodes.find((c: any) => c.id === clusterId);
      if (!cluster) return;
      const anchor = clusterAnchors.current.get(clusterId);
      if (!anchor) return;

      const innerSim = createInnerSim(clusterId, cluster.members, anchor);
      innerSimulations.current.set(clusterId, innerSim);
    });

    // Main simulation reference (for compatibility with existing rendering)
    const simulation = outerSim as any;  // Will update rendering to handle both layers

    // ========================================================================
    // RENDER CLUSTER HULLS (for collapsed clusters)
    // ========================================================================

    const clusterHulls = g.append('g')
      .attr('class', 'cluster-hulls')
      .selectAll('g.cluster-hull')
      .data(clusterNodes.filter((c: any) => !expandedClusters.has(c.id)))
      .join('g')
      .attr('class', 'cluster-hull')
      .style('cursor', 'pointer')
      .on('click', (event, d: any) => {
        event.stopPropagation();
        // Toggle expansion
        setExpandedClusters(prev => {
          const next = new Set(prev);
          if (next.has(d.id)) {
            next.delete(d.id);
          } else {
            next.add(d.id);
          }
          return next;
        });
      });

    // Hull circles
    clusterHulls.append('circle')
      .attr('cx', (d: any) => d.x)
      .attr('cy', (d: any) => d.y)
      .attr('r', (d: any) => 12 + 2 * Math.sqrt(d.size))
      .attr('fill', '#1e293b')
      .attr('fill-opacity', 0.3)
      .attr('stroke', '#64748b')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6);

    // Hull labels
    clusterHulls.append('text')
      .attr('x', (d: any) => d.x)
      .attr('y', (d: any) => d.y)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('fill', '#94a3b8')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .attr('pointer-events', 'none')
      .text((d: any) => `${d.id} (${d.size})`);

    // Render links with wireframe aesthetic (Venice consciousness flows)
    // Now with emotion-based coloring when available
    const linkElements = g.append('g')
      .selectAll('line')
      .data(validLinks)
      .join('line')
      .attr('stroke', d => getLinkColorWithEmotion(d, selectedSubentity, emotionState.linkEmotions))
      .attr('stroke-width', d => getLinkThickness(d))
      .attr('stroke-opacity', d => {
        // Slightly more opaque for emotional links
        const linkId = d.id || `${d.source}-${d.target}`;
        const hasEmotion = emotionState.linkEmotions.has(linkId);
        if (hasEmotion) return 0.85;
        return isNewLink(d) ? 0.9 : 0.7;
      })
      .attr('marker-end', d => `url(#arrow-${d.type || 'default'})`)
      .style('cursor', 'pointer')
      .style('filter', d => {
        // Enhanced glow for emotional links
        const linkId = d.id || `${d.source}-${d.target}`;
        const linkEmotion = emotionState.linkEmotions.get(linkId);

        if (linkEmotion && linkEmotion.magnitude > 0.3) {
          return 'drop-shadow(0 0 3px currentColor)';
        }
        if (isNewLink(d)) {
          return 'drop-shadow(0 0 2px currentColor)';
        }
        return 'none';
      })
      .attr('stroke-dasharray', d => {
        // Animated dashes for very new links (last 10 seconds)
        if (d.created_at && (Date.now() - d.created_at) < 10000) {
          return '4 2';
        }
        return 'none';
      })
      .on('mouseenter', (event, d) => {
        // Emit event for tooltip
        const customEvent = new CustomEvent('link:hover', { detail: { link: d, event } });
        window.dispatchEvent(customEvent);
      })
      .on('mouseleave', () => {
        const customEvent = new CustomEvent('link:leave');
        window.dispatchEvent(customEvent);
      });

    // Render nodes (groups with emotion-colored circles + emoji)
    // ONLY show nodes from expanded clusters
    const visibleNodes = nodes.filter((node: any) => {
      const clusterId = getPrimaryCluster(node);
      return clusterId && expandedClusters.has(clusterId);
    });

    const nodeGroups = g.append('g')
      .selectAll('g.node-group')
      .data(visibleNodes)
      .join('g')
      .attr('class', 'node-group')
      .style('cursor', 'pointer')
      .style('pointer-events', 'all')
      .call(drag(simulation) as any)
      .on('click', (event, d) => {
        event.stopPropagation();
        const customEvent = new CustomEvent('node:click', { detail: { node: d, event } });
        window.dispatchEvent(customEvent);
      })
      .on('mouseenter', (event, d) => {
        const customEvent = new CustomEvent('node:hover', { detail: { node: d, event } });
        window.dispatchEvent(customEvent);
      })
      .on('mouseleave', () => {
        const customEvent = new CustomEvent('node:leave');
        window.dispatchEvent(customEvent);
      });

    // Add emotion-colored circles behind emojis
    nodeGroups.append('circle')
      .attr('class', 'emotion-background')
      .attr('r', d => getNodeSize(d) * 0.5)
      .attr('fill', d => {
        const nodeId = d.id || d.node_id;
        if (!nodeId) return '#1e293b'; // Default dark slate

        const emotionMeta = emotionState.nodeEmotions.get(nodeId);
        if (!emotionMeta || emotionMeta.magnitude < 0.05) {
          return '#1e293b'; // Default for neutral/no emotion
        }

        // Extract valence and arousal from axes
        const valence = emotionMeta.axes.find(a => a.axis === 'valence')?.value ?? 0;
        const arousal = emotionMeta.axes.find(a => a.axis === 'arousal')?.value ?? 0;

        // Convert to HSL
        const color = emotionToHSL(valence, arousal);
        return hslToCSS(color);
      })
      .attr('opacity', 0.8)
      .style('filter', 'url(#parchment-texture)');

    // Add emoji text on top of circles
    const nodeElements = nodeGroups.append('text')
      .style('user-select', 'none')
      .style('pointer-events', 'none')
      .style('font-family', '"Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji", sans-serif')
      .style('text-anchor', 'middle')
      .style('dominant-baseline', 'central')
      .attr('font-size', d => getNodeSize(d) * 0.7)
      .text(d => getNodeEmoji(d));

    // PERFORMANCE: Pre-compute which subentity each active node belongs to
    const nodeToSubentity = new Map<string, string>();
    activeNodesBySubentity.forEach((nodeIds, entityId) => {
      nodeIds.forEach(nodeId => {
        if (!nodeToSubentity.has(nodeId)) {
          nodeToSubentity.set(nodeId, entityId);
        }
      });
    });

    // Update node filters (wireframe glow + subentity glow for active nodes + gold shimmer + activity glows)
    const updateNodeEffects = () => {
      nodeElements.each(function(d: any) {
        const node = d3.select(this);
        const activityGlow = getNodeGlow(d);
        const hasGoldEnergy = shouldApplyGoldShimmer(d);

        // Check if node is recently active for any subentity
        const nodeId = d.id || d.node_id;
        const activeSubentity = nodeToSubentity.get(nodeId);

        // Build filter string: wireframe glow + subentity glow (if active) + gold shimmer + activity glow
        let filterStr = 'url(#wireframe-glow)';

        // Subentity-colored glow for recently active nodes
        if (activeSubentity) {
          filterStr += ` url(#subentity-glow-${activeSubentity})`;
        }

        if (hasGoldEnergy) {
          filterStr += ' url(#gold-shimmer)';
        }

        if (activityGlow !== 'none') {
          filterStr += ` ${activityGlow}`;
        }

        node.style('filter', filterStr);
      });
    };

    // Update emotion colors with hysteresis (prevents flicker)
    const updateEmotionColors = () => {
      nodeGroups.select('circle.emotion-background').attr('fill', function(d: any) {
        const nodeId = d.id || d.node_id;
        if (!nodeId) return '#1e293b';

        const emotionMeta = emotionState.nodeEmotions.get(nodeId);
        if (!emotionMeta || emotionMeta.magnitude < 0.05) {
          return '#1e293b'; // Neutral
        }

        // Extract valence and arousal
        const valence = emotionMeta.axes.find(a => a.axis === 'valence')?.value ?? 0;
        const arousal = emotionMeta.axes.find(a => a.axis === 'arousal')?.value ?? 0;

        // Get or create display state for hysteresis
        let displayState = emotionDisplayStates.current.get(nodeId);
        if (!displayState) {
          // Initialize display state
          displayState = {
            actual: { valence, arousal, magnitude: emotionMeta.magnitude },
            displayed: { valence, arousal, magnitude: emotionMeta.magnitude },
            lastUpdateTime: Date.now()
          };
          emotionDisplayStates.current.set(nodeId, displayState);
        } else {
          // Update actual emotion
          displayState.actual = { valence, arousal, magnitude: emotionMeta.magnitude };

          // Check if update needed (hysteresis)
          if (shouldUpdateColor(displayState)) {
            displayState.displayed = { valence, arousal, magnitude: emotionMeta.magnitude };
            displayState.lastUpdateTime = Date.now();
          }
        }

        // Convert displayed emotion to HSL
        const color = emotionToHSL(displayState.displayed.valence, displayState.displayed.arousal);
        return hslToCSS(color);
      });
    };

    // Update link emotion colors with hysteresis
    const updateLinkEmotionColors = () => {
      linkElements.attr('stroke', function(d: any) {
        const linkId = d.id || `${typeof d.source === 'object' ? d.source.id : d.source}-${typeof d.target === 'object' ? d.target.id : d.target}`;

        const linkEmotion = emotionState.linkEmotions.get(linkId);
        if (!linkEmotion || linkEmotion.magnitude < 0.05) {
          // Fall back to default color
          return getLinkColor(d, selectedSubentity);
        }

        // Extract valence and arousal
        const valence = linkEmotion.axes.find(a => a.axis === 'valence')?.value ?? 0;
        const arousal = linkEmotion.axes.find(a => a.axis === 'arousal')?.value ?? 0;

        // Get or create display state for hysteresis
        let displayState = linkEmotionDisplayStates.current.get(linkId);
        if (!displayState) {
          displayState = {
            actual: { valence, arousal, magnitude: linkEmotion.magnitude },
            displayed: { valence, arousal, magnitude: linkEmotion.magnitude },
            lastUpdateTime: Date.now()
          };
          linkEmotionDisplayStates.current.set(linkId, displayState);
        } else {
          displayState.actual = { valence, arousal, magnitude: linkEmotion.magnitude };

          if (shouldUpdateColor(displayState)) {
            displayState.displayed = { valence, arousal, magnitude: linkEmotion.magnitude };
            displayState.lastUpdateTime = Date.now();
          }
        }

        // Convert to HSL
        const color = emotionToHSL(displayState.displayed.valence, displayState.displayed.arousal);
        return hslToCSS(color);
      });
    };

    updateNodeEffects(); // Initial update
    updateEmotionColors(); // Initial emotion colors
    updateLinkEmotionColors(); // Initial link emotion colors
    const effectInterval = setInterval(() => {
      updateNodeEffects();
      updateEmotionColors();
      updateLinkEmotionColors();
    }, 2000); // Update every 2 seconds

    // Simulation tick
    // Outer sim already converged (ran to completion)
    // Tick inner simulations for expanded clusters
    const tickAll = () => {
      // Tick all active inner simulations
      innerSimulations.current.forEach(sim => sim.tick());

      // Update link positions
      linkElements
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      // Position node groups (contains circle + emoji)
      nodeGroups
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    };

    // Use requestAnimationFrame for smooth ticking
    let rafId: number;
    const tick = () => {
      tickAll();
      if (innerSimulations.current.size > 0) {
        rafId = requestAnimationFrame(tick);
      }
    };
    if (innerSimulations.current.size > 0) {
      rafId = requestAnimationFrame(tick);
    }

    // Outer simulation already converged
    // Inner simulations start automatically when created and tick via RAF

    // CRITICAL: Cleanup function that properly stops simulation and clears interval
    // This runs BEFORE the effect re-runs (not just on unmount)
    return () => {
      // Cancel animation frame
      if (rafId) cancelAnimationFrame(rafId);

      // Stop outer simulation
      simulation.stop();

      // Stop all inner simulations
      innerSimulations.current.forEach(sim => sim.stop());
      innerSimulations.current.clear();

      // Clear the interval to prevent accumulation
      clearInterval(effectInterval);

      // Remove all SVG elements to prevent memory accumulation
      svg.selectAll('*').remove();

      // Nullify large objects to help garbage collection
      (simulation as any).nodes([]);
      (simulation as any).force('link', null);
      (simulation as any).force('charge', null);
      (simulation as any).force('center', null);
      (simulation as any).force('collision', null);
    };
  }, [nodes, links, selectedSubentity, expandedClusters]);

  // Handle node focus from CLAUDE_DYNAMIC.md clicks
  // IMPORTANT: Empty dependency array to prevent listener accumulation
  useEffect(() => {
    const handleNodeFocus = (e: Event) => {
      const customEvent = e as CustomEvent;
      const { nodeId } = customEvent.detail;

      // Get current SVG reference
      if (!svgRef.current) return;

      const svg = d3.select(svgRef.current);
      const g = svg.select('g');

      // Find the node in the current graph
      const nodeElement = svg.selectAll('text')
        .filter((d: any) => d && (d.id === nodeId || d.node_id === nodeId));

      if (nodeElement.empty()) {
        console.log('[GraphCanvas] Node not found for focus:', nodeId);
        return;
      }

      // Get the node data
      const nodeData: any = nodeElement.datum();
      if (!nodeData || !nodeData.x || !nodeData.y) return;

      // Center view on node with smooth transition
      const width = typeof window !== 'undefined' ? window.innerWidth : 1920;
      const height = typeof window !== 'undefined' ? window.innerHeight : 1080;

      const scale = 1.5; // Zoom in a bit
      const x = -nodeData.x * scale + width / 2;
      const y = -nodeData.y * scale + height / 2;

      g.transition()
        .duration(750)
        .attr('transform', `translate(${x},${y}) scale(${scale})`);

      // Highlight node temporarily
      nodeElement
        .transition()
        .duration(300)
        .style('filter', 'url(#wireframe-glow) drop-shadow(0 0 16px #5efc82) drop-shadow(0 0 8px #5efc82)')
        .transition()
        .delay(1000)
        .duration(500)
        .style('filter', function(d: any) {
          const activityGlow = getNodeGlow(d);
          const hasGold = shouldApplyGoldShimmer(d);
          let filterStr = 'url(#wireframe-glow)';
          if (hasGold) filterStr += ' url(#gold-shimmer)';
          if (activityGlow !== 'none') filterStr += ` ${activityGlow}`;
          return filterStr;
        });
    };

    window.addEventListener('node:focus', handleNodeFocus);

    return () => {
      window.removeEventListener('node:focus', handleNodeFocus);
    };
  }, []); // Empty deps - event handler doesn't need to re-register

  return (
    <div className="relative w-full h-full">
      <svg
        ref={svgRef}
        className="w-full h-full"
        style={{ background: '#4682B4' }}
      />
      {/* Zoom hint */}
      <div className="absolute bottom-2 right-2 text-xs text-observatory-dark/40 pointer-events-none select-none">
        Double-click to reset view
      </div>
    </div>
  );
}

// ============================================================================
// Visual Encoding Functions
// ============================================================================

function getNodeEmoji(node: Node): string {
  // Use node_type (first label extracted by backend) instead of labels[0]
  // because FalkorDB returns labels as string "[Label]" not array
  const nodeType = node.node_type || 'Node';
  const EMOJIS: Record<string, string> = {
    // N1 - Personal/Individual Consciousness
    'Memory': '??',
    'Conversation': '??',
    'Person': '??',
    'Relationship': '??',
    'Personal_Goal': '??',
    'Personal_Value': '??',
    'Personal_Pattern': '??',
    'Realization': '??',
    'Wound': '??',
    'Coping_Mechanism': '???',
    'Trigger': '?',
    // N2 - Organizational Consciousness
    'Human': '??',
    'AI_Agent': '??',
    'Team': '??',
    'Department': '??',
    'Decision': '??',
    'Project': '??',
    'Task': '?',
    'Milestone': '??',
    'Best_Practice': '?',
    'Anti_Pattern': '??',
    'Risk': '??',
    'Metric': '??',
    'Process': '??',
    // N2/N3 - Conceptual Knowledge
    'Concept': '??',
    'Principle': '??',
    'Mechanism': '??',
    'Document': '??',
    'Documentation': '??',
    // N3 - Ecosystem Intelligence (External)
    'Company': '???',
    'External_Person': '??',
    'Wallet_Address': '??',
    'Social_Media_Account': '??',
    // N3 - Evidence Nodes
    'Post': '??',
    'Transaction': '??',
    'Deal': '??',
    'Event': '??',
    'Smart_Contract': '??',
    'Integration': '??',
    // N3 - Derived Intelligence
    'Psychological_Trait': '??',
    'Behavioral_Pattern': '??',
    'Market_Signal': '??',
    'Reputation_Assessment': '?',
    'Network_Cluster': '???',
    // Fallback
    'default': '?'
  };
  return EMOJIS[nodeType] || EMOJIS['default'];
}

function getNodeSize(node: Node): number {
  // Use computed weight from node or fallback to calculation
  const weight = node.weight || computeNodeWeight(node);
  // Expanded range: 20px (min) to 48px (max weight)
  return Math.max(20, 16 + weight * 32);
}

function computeNodeWeight(node: Node): number {
  const energy = node.energy || 0;
  const confidence = node.confidence || 0.5;
  const traversalCount = node.traversal_count || 0;
  const normalizedTraversals = Math.min(1.0, Math.log10(traversalCount + 1) / 2);
  return (energy * 0.4) + (confidence * 0.3) + (normalizedTraversals * 0.3);
}

function getNodeGlow(node: Node): string {
  const now = Date.now();

  // Priority: Show only the most important glow (performance optimization)

  // 1. NEWEST CREATED (last 5 minutes) - Bright cyan pulse (highest priority)
  if (node.created_at) {
    const age = now - node.created_at;
    if (age < 300000) { // 5 minutes
      const intensity = 1 - (age / 300000);
      const glowSize = 12 + (intensity * 16);
      return `drop-shadow(0 0 ${glowSize}px rgba(45, 212, 191, ${intensity})) drop-shadow(0 0 ${glowSize/2}px rgba(45, 212, 191, ${intensity}))`;
    }
  }

  // 2. RECENTLY REINFORCED/DE-REINFORCED (last 2 minutes)
  if (node.last_modified && node.reinforcement_weight !== undefined) {
    const age = now - node.last_modified;
    if (age < 120000) { // 2 minutes
      const intensity = 1 - (age / 120000);
      const glowSize = 6 + (intensity * 8);

      if (node.reinforcement_weight > 0.05) {
        // GREEN for positive reinforcement
        return `drop-shadow(0 0 ${glowSize}px rgba(34, 197, 94, ${intensity * 0.8}))`;
      } else if (node.reinforcement_weight < -0.05) {
        // RED for de-reinforcement
        return `drop-shadow(0 0 ${glowSize}px rgba(239, 68, 68, ${intensity * 0.8}))`;
      }
    }
  }

  // 3. RECENTLY TRAVERSED (last 2 minutes) - Yellow/green (lowest priority)
  if (node.last_active) {
    const age = now - node.last_active;
    if (age < 120000) { // 2 minutes
      const intensity = 1 - (age / 120000);
      const glowSize = 5 + (intensity * 6);
      return `drop-shadow(0 0 ${glowSize}px rgba(94, 252, 130, ${intensity * 0.6}))`;
    }
  }

  return 'none';
}

/**
 * Gold shimmer indicates high consciousness energy (content signal)
 * Strategic Gold Rule: Use ONLY for content signals (energy/activity)
 */
function shouldApplyGoldShimmer(node: Node): boolean {
  // High energy nodes (active consciousness)
  const energy = node.energy || 0;
  if (energy > 0.7) return true;

  // High traversal activity (frequently explored)
  const traversalCount = node.traversal_count || 0;
  if (traversalCount > 10) return true;

  // Recently very active (last 5 minutes)
  if (node.last_active) {
    const age = Date.now() - node.last_active;
    if (age < 300000 && energy > 0.5) { // 5 minutes with moderate energy
      return true;
    }
  }

  return false;
}

function getLinkColor(link: Link, selectedSubentity: string): string {
  if (selectedSubentity === 'structural') {
    return getLinkTypeColor(link.type);
  } else {
    // Valence-based coloring
    const valences = link.sub_entity_valences || {};
    const valence = valences[selectedSubentity];
    return getValenceColor(valence);
  }
}

/**
 * Get link color with emotion support
 * Uses emotion-based HSL coloring when available, falls back to type/valence coloring
 */
function getLinkColorWithEmotion(
  link: Link,
  selectedSubentity: string,
  linkEmotions: Map<string, EmotionMetadata>
): string {
  // Try to get emotion data for this link
  const linkId = link.id || `${link.source}-${link.target}`;
  const linkEmotion = linkEmotions.get(linkId);

  // If link has emotion and it's above threshold, use emotion color
  if (linkEmotion && linkEmotion.magnitude > 0.05) {
    const valence = linkEmotion.axes.find(a => a.axis === 'valence')?.value ?? 0;
    const arousal = linkEmotion.axes.find(a => a.axis === 'arousal')?.value ?? 0;
    const color = emotionToHSL(valence, arousal);
    return hslToCSS(color);
  }

  // Otherwise fall back to default link coloring
  return getLinkColor(link, selectedSubentity);
}

function getLinkTypeColor(type: string): string {
  const COLORS: Record<string, string> = {
    'JUSTIFIES': '#ef4444',
    'BUILDS_TOWARD': '#3b82f6',
    'ENABLES': '#22c55e',
    'USES': '#8b5cf6',
    'default': '#666'
  };
  return COLORS[type] || COLORS['default'];
}

function getValenceColor(valence: number | undefined): string {
  if (valence === null || valence === undefined) return '#64748b';

  const normalized = (valence + 1.0) / 2.0;

  if (normalized < 0.5) {
    const t = normalized * 2;
    return d3.interpolateRgb('#ef4444', '#94a3b8')(t); // Red to gray
  } else {
    const t = (normalized - 0.5) * 2;
    return d3.interpolateRgb('#94a3b8', '#22c55e')(t); // Gray to green
  }
}

// ============================================================================
// Link Visibility Functions
// ============================================================================

function getLinkThickness(link: Link): number {
  // Use link weight or strength for thickness
  const weight = link.weight || link.strength || 0.5;
  // Range: 6px (min) to 20px (max weight) - MUCH thicker for visibility (was 3-12px)
  return Math.max(6, 6 + weight * 14);
}

function isNewLink(link: Link): boolean {
  if (!link.created_at) return false;
  const age = Date.now() - link.created_at;
  return age < 60000; // Less than 1 minute old
}

// ============================================================================
// Temporal Force (Timeline Layout)
// ============================================================================

function forceTemporalX(width: number) {
  let nodes: Node[];

  function force(alpha: number) {
    if (!nodes) return;

    const now = Date.now();
    // Find oldest and newest timestamps
    const timestamps = nodes
      .map(n => n.last_active || n.created_at || 0)
      .filter(t => t > 0);

    if (timestamps.length === 0) return;

    const minTime = Math.min(...timestamps);
    const maxTime = Math.max(...timestamps);
    const timeRange = maxTime - minTime;

    // FALLBACK: If timestamps are uniform (seed data), disable temporal force
    // Range less than 1 hour = likely bulk-imported seed data
    if (timeRange < 3600000) {
      // console.log('[Temporal Force] Timestamps too uniform, skipping');
      return; // Let other forces handle layout
    }

    // Pull nodes left-to-right based on temporal position (MINIMAL spread for clustering)
    nodes.forEach((node: any) => {
      const nodeTime = node.last_active || node.created_at || minTime;
      const timePos = (nodeTime - minTime) / timeRange; // 0 (old) to 1 (new)

      // Target X position: center ±10% width (was ±30%, now much tighter)
      const targetX = width * 0.45 + (timePos * width * 0.1);

      // Apply VERY gentle hint (not forcing)
      const dx = targetX - node.x;
      node.vx += dx * alpha * 0.01; // Barely noticeable 1% strength (was 5%)
    });
  }

  force.initialize = function(_: any) {
    nodes = _;
  };

  return force;
}

function forceValenceY(height: number) {
  let nodes: Node[];

  function force(alpha: number) {
    if (!nodes) return;

    // Pull nodes up/down based on emotional valence (MINIMAL spread for clustering)
    nodes.forEach((node: any) => {
      const valence = computeNodeValence(node);

      // Target Y position: center ±10% height (was ±30%, now much tighter)
      // Valence ranges from -1 (bottom) to +1 (top)
      const valencePos = (valence + 1) / 2; // Normalize to 0-1
      const targetY = height * 0.45 + (valencePos * height * 0.1); // Tight clustering around center

      // Apply VERY gentle hint (not forcing)
      const dy = targetY - node.y;
      node.vy += dy * alpha * 0.01; // Barely noticeable 1% strength (was 4%)
    });
  }

  force.initialize = function(_: any) {
    nodes = _;
  };

  return force;
}

function computeNodeValence(node: Node): number {
  // Aggregate valence from node properties
  let valence = 0;
  let count = 0;

  // Check if node has entity_activations with valence data
  if (node.entity_activations) {
    Object.values(node.entity_activations).forEach((activation: any) => {
      if (activation.valence !== undefined) {
        valence += activation.valence;
        count++;
      }
    });
  }

  // Node type-based valence hints (adds diversity even without runtime data)
  const nodeType = node.node_type || '';
  if (nodeType === 'Best_Practice' || nodeType === 'Realization' || nodeType === 'Personal_Goal') {
    valence += 0.3;
    count++;
  } else if (nodeType === 'Anti_Pattern' || nodeType === 'Wound' || nodeType === 'Risk') {
    valence -= 0.3;
    count++;
  } else if (nodeType === 'Trigger' || nodeType === 'Coping_Mechanism') {
    valence -= 0.15;
    count++;
  }

  // Confidence as slight positive bias (higher confidence = slight upward pull)
  if (node.confidence !== undefined && node.confidence !== null) {
    valence += (node.confidence - 0.5) * 0.2; // -0.1 to +0.1
    count++;
  }

  // Reinforcement weight affects valence
  if (node.reinforcement_weight !== undefined) {
    valence += node.reinforcement_weight * 0.5; // Scale reinforcement to valence
    count++;
  }

  // FALLBACK: Even with no data, use small random jitter to prevent perfect stacking
  if (count === 0) {
    // Use node ID as seed for consistent but distributed positioning
    const seed = parseInt(node.id, 36) || 0;
    return ((seed % 100) / 100 - 0.5) * 0.4; // -0.2 to +0.2 range
  }

  return Math.max(-1, Math.min(1, valence / count));
}

// ============================================================================
// Drag Behavior
// ============================================================================

function drag(simulation: d3.Simulation<any, undefined>) {
  function dragstarted(event: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  function dragged(event: any) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  function dragended(event: any) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended);
}


## <<< END app/consciousness/components/GraphCanvas.tsx
---

## >>> BEGIN app/consciousness/hooks/useWebSocket.ts
<!-- mtime: 2025-10-24T20:55:44; size: 19445 -->

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import type {
  WebSocketEvent,
  EntityActivityEvent,
  ThresholdCrossingEvent,
  ConsciousnessStateEvent,
  WebSocketStreams,
  V2ConsciousnessState,
  FrameStartEvent,
  WmEmitEvent,
  NodeFlipEvent,
  LinkFlowSummaryEvent,
  FrameEndEvent,
  EmotionColoringState,
  NodeEmotionUpdateEvent,
  LinkEmotionUpdateEvent,
  StrideExecEvent,
  EmotionMetadata
} from './websocket-types';
import { WebSocketState } from './websocket-types';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/ws';
const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_ENTITY_ACTIVITIES = 100; // Keep last 100 subentity activities
const MAX_THRESHOLD_CROSSINGS = 50; // Keep last 50 threshold crossings
const MAX_NODE_FLIPS = 20; // Keep last 20 node flips (v2)
const MAX_RECENT_STRIDES = 100; // Keep last 100 strides for attribution
const MAX_FRAME_EVENTS = 200; // Keep last 200 frame.start events (Priority 3 tick speed viz)
const MAX_WEIGHT_LEARNING_EVENTS = 200; // Keep last 200 weight learning events (Priority 4 dual-view viz)
const MAX_STRIDE_SELECTION_EVENTS = 200; // Keep last 200 stride selection events (Priority 5 fan-out viz)
const MAX_PHENOMENOLOGY_EVENTS = 200; // Keep last 200 phenomenology events (Priority 6 health viz)
const SATURATION_THRESHOLD = 0.9; // Emotion magnitude threshold for saturation warning

/**
 * useWebSocket Hook
 *
 * Connects to the consciousness operations WebSocket stream
 * and provides real-time event data to visualization components.
 *
 * Features:
 * - Automatic reconnection on disconnect
 * - Separate streams for each event type
 * - Connection state tracking
 * - Error handling
 *
 * Usage:
 * const { entityActivity, thresholdCrossings, consciousnessState } = useWebSocket();
 *
 * Author: Iris "The Aperture"
 * Backend integration: Felix "Ironhand"'s WebSocket infrastructure
 */
export function useWebSocket(): WebSocketStreams {
  // Connection state
  const [connectionState, setConnectionState] = useState<WebSocketState>(WebSocketState.CONNECTING);
  const [error, setError] = useState<string | null>(null);

  // Event streams (v1 legacy)
  const [entityActivity, setEntityActivity] = useState<EntityActivityEvent[]>([]);
  const [thresholdCrossings, setThresholdCrossings] = useState<ThresholdCrossingEvent[]>([]);
  const [consciousnessState, setConsciousnessState] = useState<ConsciousnessStateEvent | null>(null);

  // V2 consciousness state (frame-based)
  const [v2State, setV2State] = useState<V2ConsciousnessState>({
    // Frame tracking
    currentFrame: null,
    frameEvents: [],

    // Criticality metrics
    rho: null,
    safety_state: null,

    // Timing metrics
    dt_ms: null,
    interval_sched: null,
    dt_used: null,

    // Conservation metrics
    deltaE_total: null,
    conservation_error_pct: null,
    energy_in: null,
    energy_transferred: null,
    energy_decay: null,

    // Frontier metrics
    active_count: null,
    shadow_count: null,
    diffusion_radius: null,

    // Working memory and traversal
    workingMemory: new Set<string>(),
    recentFlips: [],
    linkFlows: new Map<string, number>()
  });

  // Emotion coloring state
  const [emotionState, setEmotionState] = useState<EmotionColoringState>({
    nodeEmotions: new Map<string, EmotionMetadata>(),
    linkEmotions: new Map<string, EmotionMetadata>(),
    recentStrides: [],
    regulationRatio: null,
    resonanceRatio: null,
    saturationWarnings: []
  });

  // Priority 4: Weight learning events
  const [weightLearningEvents, setWeightLearningEvents] = useState<WeightsUpdatedTraceEvent[]>([]);

  // Priority 5: Stride selection events
  const [strideSelectionEvents, setStrideSelectionEvents] = useState<StrideSelectionEvent[]>([]);

  // Priority 6: Phenomenology health events
  const [phenomenologyMismatchEvents, setPhenomenologyMismatchEvents] = useState<PhenomenologyMismatchEvent[]>([]);
  const [phenomenologyHealthEvents, setPhenomenologyHealthEvents] = useState<PhenomenologicalHealthEvent[]>([]);

  // WebSocket reference (persists across renders)
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isIntentionalCloseRef = useRef(false);

  // Frame throttling to prevent infinite re-render loops
  const lastFrameUpdateRef = useRef<number>(0);
  const FRAME_UPDATE_THROTTLE_MS = 100; // Only update every 100ms

  /**
   * Handle incoming WebSocket messages
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data: WebSocketEvent = JSON.parse(event.data);

      switch (data.type) {
        // V1 events (legacy)
        case 'entity_activity':
          setEntityActivity(prev => {
            const updated = [...prev, data];
            return updated.slice(-MAX_ENTITY_ACTIVITIES);
          });
          break;

        case 'threshold_crossing':
          setThresholdCrossings(prev => {
            const updated = [...prev, data];
            return updated.slice(-MAX_THRESHOLD_CROSSINGS);
          });
          break;

        case 'consciousness_state':
          setConsciousnessState(data);
          break;

        // V2 events (frame-based)
        case 'frame.start': {
          const frameEvent = data as FrameStartEvent;

          // Throttle frame updates to prevent infinite re-render loop
          // Frames arrive rapidly (10-60ms apart), but React needs breathing room
          const now = Date.now();
          if (now - lastFrameUpdateRef.current < FRAME_UPDATE_THROTTLE_MS) {
            // Skip this frame update - too soon since last update
            break;
          }
          lastFrameUpdateRef.current = now;

          setV2State(prev => {
            // Only update if frame actually changed (frame_id is unique per frame)
            if (prev.currentFrame === frameEvent.frame_id) {
              return prev; // Same frame, skip update
            }

            // Accumulate frame events for Priority 3 tick speed visualization
            const updatedFrameEvents = [...prev.frameEvents, frameEvent].slice(-MAX_FRAME_EVENTS);

            return {
              ...prev,
              currentFrame: frameEvent.frame_id,
              frameEvents: updatedFrameEvents,

              // Criticality metrics
              rho: frameEvent.rho ?? prev.rho,
              safety_state: frameEvent.safety_state ?? prev.safety_state,

              // Timing metrics
              dt_ms: frameEvent.dt_ms ?? prev.dt_ms,
              interval_sched: frameEvent.interval_sched ?? prev.interval_sched,
              dt_used: frameEvent.dt_used ?? prev.dt_used,

              // Clear link flows at frame start (only if not already empty)
              linkFlows: prev.linkFlows.size > 0 ? new Map<string, number>() : prev.linkFlows
            };
          });
          break;
        }

        case 'wm.emit': {
          const wmEvent = data as WmEmitEvent;
          setV2State(prev => {
            // Only update if working memory content changed
            const newNodeIds = new Set(wmEvent.node_ids);
            if (prev.workingMemory.size === newNodeIds.size &&
                [...newNodeIds].every(id => prev.workingMemory.has(id))) {
              return prev; // No change, return same object
            }
            return {
              ...prev,
              workingMemory: newNodeIds
            };
          });
          break;
        }

        case 'node.flip': {
          setV2State(prev => {
            const updated = [...prev.recentFlips, data as NodeFlipEvent];
            return {
              ...prev,
              recentFlips: updated.slice(-MAX_NODE_FLIPS)
            };
          });
          break;
        }

        case 'link.flow.summary': {
          const flowEvent = data as LinkFlowSummaryEvent;
          setV2State(prev => {
            // Guard: Check if flows array exists
            if (!flowEvent.flows || !Array.isArray(flowEvent.flows)) {
              console.warn('[useWebSocket] link.flow.summary event missing flows array:', flowEvent);
              return prev;
            }

            // Check if any flow values actually changed
            let hasChanges = false;
            for (const flow of flowEvent.flows) {
              if (prev.linkFlows.get(flow.link_id) !== flow.count) {
                hasChanges = true;
                break;
              }
            }

            if (!hasChanges) {
              return prev; // No changes, return same object
            }

            const newFlows = new Map(prev.linkFlows);
            flowEvent.flows.forEach(flow => {
              newFlows.set(flow.link_id, flow.count);
            });
            return {
              ...prev,
              linkFlows: newFlows
            };
          });
          break;
        }

        case 'frame.end': {
          const frameEndEvent = data as FrameEndEvent;
          setV2State(prev => {
            // Check if any values actually changed
            if (
              prev.deltaE_total === frameEndEvent.deltaE_total &&
              prev.conservation_error_pct === frameEndEvent.conservation_error_pct &&
              prev.energy_in === frameEndEvent.energy_in &&
              prev.energy_transferred === frameEndEvent.energy_transferred &&
              prev.energy_decay === frameEndEvent.energy_decay &&
              prev.active_count === frameEndEvent.active_count &&
              prev.shadow_count === frameEndEvent.shadow_count &&
              prev.diffusion_radius === frameEndEvent.diffusion_radius
            ) {
              return prev; // No changes, skip update
            }

            return {
              ...prev,

              // Conservation metrics
              deltaE_total: frameEndEvent.deltaE_total ?? prev.deltaE_total,
              conservation_error_pct: frameEndEvent.conservation_error_pct ?? prev.conservation_error_pct,
              energy_in: frameEndEvent.energy_in ?? prev.energy_in,
              energy_transferred: frameEndEvent.energy_transferred ?? prev.energy_transferred,
              energy_decay: frameEndEvent.energy_decay ?? prev.energy_decay,

              // Frontier metrics
              active_count: frameEndEvent.active_count ?? prev.active_count,
              shadow_count: frameEndEvent.shadow_count ?? prev.shadow_count,
              diffusion_radius: frameEndEvent.diffusion_radius ?? prev.diffusion_radius
            };
          });
          break;
        }

        // Emotion coloring events
        case 'node.emotion.update': {
          const emotionEvent = data as NodeEmotionUpdateEvent;
          setEmotionState(prev => {
            // Create emotion metadata from event
            const metadata: EmotionMetadata = {
              magnitude: emotionEvent.emotion_magnitude,
              axes: emotionEvent.top_axes,
              lastUpdated: Date.parse(emotionEvent.timestamp),
              displayedMagnitude: prev.nodeEmotions.get(emotionEvent.node_id)?.displayedMagnitude ?? emotionEvent.emotion_magnitude
            };

            // Update node emotions map
            const newNodeEmotions = new Map(prev.nodeEmotions);
            newNodeEmotions.set(emotionEvent.node_id, metadata);

            // Check for saturation warnings
            const saturationWarnings: string[] = [];
            for (const [nodeId, meta] of newNodeEmotions.entries()) {
              if (meta.magnitude > SATURATION_THRESHOLD) {
                saturationWarnings.push(nodeId);
              }
            }

            return {
              ...prev,
              nodeEmotions: newNodeEmotions,
              saturationWarnings
            };
          });
          break;
        }

        case 'link.emotion.update': {
          const emotionEvent = data as LinkEmotionUpdateEvent;
          setEmotionState(prev => {
            // Create emotion metadata from event
            const metadata: EmotionMetadata = {
              magnitude: emotionEvent.emotion_magnitude,
              axes: emotionEvent.top_axes,
              lastUpdated: Date.parse(emotionEvent.timestamp),
              displayedMagnitude: prev.linkEmotions.get(emotionEvent.link_id)?.displayedMagnitude ?? emotionEvent.emotion_magnitude
            };

            // Update link emotions map
            const newLinkEmotions = new Map(prev.linkEmotions);
            newLinkEmotions.set(emotionEvent.link_id, metadata);

            return {
              ...prev,
              linkEmotions: newLinkEmotions
            };
          });
          break;
        }

        case 'stride.exec': {
          const strideEvent = data as StrideExecEvent;
          setEmotionState(prev => {
            // Add to recent strides for attribution
            const updated = [...prev.recentStrides, strideEvent];
            const recentStrides = updated.slice(-MAX_RECENT_STRIDES);

            // Calculate regulation vs resonance ratios from recent strides
            let compCount = 0;
            let resCount = 0;

            for (const stride of recentStrides) {
              // Count as complementarity-driven if comp multiplier reduced cost more than resonance
              if (stride.comp_multiplier < stride.resonance_multiplier) {
                compCount++;
              } else if (stride.resonance_multiplier < stride.comp_multiplier) {
                resCount++;
              }
              // If equal, don't count either (neutral)
            }

            const total = compCount + resCount;
            const regulationRatio = total > 0 ? compCount / total : null;
            const resonanceRatio = total > 0 ? resCount / total : null;

            return {
              ...prev,
              recentStrides,
              regulationRatio,
              resonanceRatio
            };
          });
          break;
        }

        // Internal consciousness engine events (no UI updates needed)
        case 'criticality.state':
        case 'decay.tick':
          // Safe to ignore - these are internal engine telemetry events
          // broadcast for monitoring but don't require UI state updates
          break;

        // Priority 4: Weight learning events
        case 'weights.updated.trace': {
          const weightEvent = data as WeightsUpdatedTraceEvent;
          setWeightLearningEvents(prev => {
            const updated = [...prev, weightEvent];
            return updated.slice(-MAX_WEIGHT_LEARNING_EVENTS);
          });
          break;
        }

        // Priority 5: Stride selection events
        case 'stride.selection': {
          const strideSelectionEvent = data as StrideSelectionEvent;
          setStrideSelectionEvents(prev => {
            const updated = [...prev, strideSelectionEvent];
            return updated.slice(-MAX_STRIDE_SELECTION_EVENTS);
          });
          break;
        }

        // Priority 6: Phenomenology health events
        case 'phenomenology.mismatch': {
          const mismatchEvent = data as PhenomenologyMismatchEvent;
          setPhenomenologyMismatchEvents(prev => {
            const updated = [...prev, mismatchEvent];
            return updated.slice(-MAX_PHENOMENOLOGY_EVENTS);
          });
          break;
        }

        case 'phenomenological_health': {
          const healthEvent = data as PhenomenologicalHealthEvent;
          setPhenomenologyHealthEvents(prev => {
            const updated = [...prev, healthEvent];
            return updated.slice(-MAX_PHENOMENOLOGY_EVENTS);
          });
          break;
        }

        default:
          console.warn('[WebSocket] Unknown event type:', (data as any).type);
      }
    } catch (err) {
      console.error('[WebSocket] Failed to parse message:', err);
      setError('Failed to parse WebSocket message');
    }
  }, []);

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    // Don't reconnect if intentionally closed
    if (isIntentionalCloseRef.current) {
      return;
    }

    try {
      console.log('[WebSocket] Connecting to:', WS_URL);
      setConnectionState(WebSocketState.CONNECTING);
      setError(null);

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WebSocket] Connected');
        setConnectionState(WebSocketState.CONNECTED);
        setError(null);
      };

      ws.onmessage = handleMessage;

      ws.onerror = (event) => {
        // WebSocket unavailable is expected degraded state, not error
        console.log('[WebSocket] Connection unavailable - will retry');
        setConnectionState(WebSocketState.ERROR);
        setError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        console.log('[WebSocket] Disconnected:', event.code, event.reason);
        setConnectionState(WebSocketState.DISCONNECTED);

        // Attempt reconnection if not intentionally closed
        if (!isIntentionalCloseRef.current) {
          console.log(`[WebSocket] Reconnecting in ${RECONNECT_DELAY}ms...`);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, RECONNECT_DELAY);
        }
      };
    } catch (err) {
      console.error('[WebSocket] Connection error:', err);
      setConnectionState(WebSocketState.ERROR);
      setError(err instanceof Error ? err.message : 'Unknown connection error');

      // Attempt reconnection
      if (!isIntentionalCloseRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, RECONNECT_DELAY);
      }
    }
  }, [handleMessage]);

  /**
   * Disconnect WebSocket
   */
  const disconnect = useCallback(() => {
    isIntentionalCloseRef.current = true;

    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Close WebSocket connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setConnectionState(WebSocketState.DISCONNECTED);
  }, []);

  /**
   * Initialize WebSocket connection on mount
   * Cleanup on unmount
   */
  useEffect(() => {
    isIntentionalCloseRef.current = false;
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    // V1 events
    entityActivity,
    thresholdCrossings,
    consciousnessState,

    // V2 events
    v2State,

    // Emotion coloring
    emotionState,

    // Priority 4: Weight learning
    weightLearningEvents,

    // Priority 5: Stride selection
    strideSelectionEvents,

    // Priority 6: Phenomenology health
    phenomenologyMismatchEvents,
    phenomenologyHealthEvents,

    // Connection
    connectionState,
    error
  };
}


## <<< END app/consciousness/hooks/useWebSocket.ts
---

## >>> BEGIN app/consciousness/hooks/websocket-types.ts
<!-- mtime: 2025-10-24T20:11:42; size: 26381 -->

/**
 * WebSocket Event Types
 *
 * Type definitions for real-time consciousness operations events
 * streamed from the backend consciousness engine.
 *
 * Backend: orchestration/control_api.py (/api/ws endpoint)
 * Protocol: WebSocket at ws://localhost:8000/api/ws
 *
 * Author: Iris "The Aperture"
 * Integration with: Felix "Ironhand"'s WebSocket infrastructure
 */

/**
 * Subentity Activity Event
 *
 * Emitted by SubEntity during graph traversal.
 * Frequency: Every node traversal
 * Source: orchestration/sub_entity.py
 */
export interface EntityActivityEvent {
  type: 'entity_activity';
  entity_id: string;              // e.g., "builder", "observer"
  current_node: string;            // Node ID currently exploring
  need_type: string;               // e.g., "pattern_validation", "context_gathering"
  energy_used: number;             // Energy consumed so far this cycle
  energy_budget: number;           // Total energy budget for this cycle
  nodes_visited_count: number;    // Total nodes visited this cycle
  sequence_position: number;       // Global sequence number across all cycles
  timestamp: string;               // ISO 8601 timestamp
}

/**
 * Threshold Crossing Event
 *
 * Emitted when a node crosses activation threshold for an subentity.
 * Frequency: On threshold crossing (up or down)
 * Source: orchestration/dynamic_prompt_generator.py
 */
export interface ThresholdCrossingEvent {
  type: 'threshold_crossing';
  entity_id: string;               // Subentity for which threshold crossed
  node_id: string;                 // Node that crossed threshold
  node_name: string;               // Human-readable node text
  direction: 'on' | 'off';         // Crossed up (activated) or down (deactivated)
  entity_activity: number;         // Current subentity activity level (0-1)
  threshold: number;               // Threshold value that was crossed
  timestamp: string;               // ISO 8601 timestamp
}

/**
 * Consciousness State Event
 *
 * Emitted after global energy measurement.
 * Frequency: After each tick (variable frequency based on system state)
 * Source: orchestration/consciousness_engine.py
 */
export interface ConsciousnessStateEvent {
  type: 'consciousness_state';
  network_id: string;              // e.g., "N1", "N2", "N3"
  global_energy: number;          // System-wide energy (0-1)
  branching_ratio: number;         // Mapped branching ratio (0-1)
  raw_sigma: number;               // Raw branching ratio s (unbounded)
  tick_interval_ms: number;        // Current tick interval in milliseconds
  tick_frequency_hz: number;       // Current tick frequency in Hz
  consciousness_state: string;     // e.g., "alert", "engaged", "calm", "drowsy", "dormant"
  time_since_last_event: number;   // Seconds since last external event
  timestamp: string;               // ISO 8601 timestamp
}

/**
 * V2 Event Format - Frame-based consciousness streaming
 * Source: orchestration/consciousness_engine_v2.py
 *
 * These events provide frame-by-frame consciousness updates with
 * working memory tracking and link flow visualization.
 */

/**
 * Frame Start Event (v2) / Tick Frame Event
 *
 * Marks the beginning of a consciousness frame.
 * Contains branching ratio (?), timing info, and subentity palette.
 *
 * Extended fields per tick_speed.md and criticality.md specs:
 * - dt_ms: wall-clock time since last tick
 * - interval_sched: scheduled interval
 * - dt_used: physics dt actually used (capped)
 * - rho: spectral radius (criticality metric)
 * - safety_state: system stability classification
 * - notes: diagnostic messages (e.g., "dt capped", "EMA smoothing")
 */
export interface FrameStartEvent {
  type: 'frame.start';
  v: '2';
  kind: 'frame.start';
  frame_id: number;

  // Criticality metrics
  rho?: number;                    // Spectral radius (branching ratio)
  safety_state?: 'subcritical' | 'critical' | 'supercritical'; // System stability

  // Timing metrics
  dt_ms?: number;                  // Wall-clock milliseconds since last tick
  interval_sched?: number;         // Scheduled interval (ms)
  dt_used?: number;                // Physics dt actually used (capped)
  notes?: string;                  // Diagnostic notes

  // Three-Factor Tick Speed (Priority 3)
  tick_reason?: 'stimulus' | 'activation' | 'arousal_floor'; // Which factor won
  interval_stimulus?: number;      // Stimulus-driven interval (ms)
  interval_activation?: number;    // Activation-driven interval (ms)
  interval_arousal?: number;       // Arousal floor interval (ms)
  total_active_energy?: number;    // For activation computation
  mean_arousal?: number;           // For arousal floor computation

  // Entity visualization
  entity_palette?: Array<{
    id: string;
    name?: string;
    color: string;
  }>;
}

/**
 * Working Memory Emission Event (v2)
 *
 * Lists all nodes currently in working memory.
 * Working memory = set of active nodes in consciousness.
 */
export interface WmEmitEvent {
  type: 'wm.emit';
  v: '2';
  kind: 'wm.emit';
  frame_id: number;
  node_ids: string[];              // Node IDs in working memory
}

/**
 * Node Flip Event (v2)
 *
 * Emitted when a node crosses activation threshold.
 */
export interface NodeFlipEvent {
  type: 'node.flip';
  v: '2';
  kind: 'node.flip';
  frame_id: number;
  node_id: string;
  direction: 'on' | 'off';         // Activated or deactivated
  entity_id?: string;              // Which subentity caused the flip
}

/**
 * Link Flow Summary Event (v2)
 *
 * Aggregated link traversal statistics for visualization.
 */
export interface LinkFlowSummaryEvent {
  type: 'link.flow.summary';
  v: '2';
  kind: 'link.flow.summary';
  frame_id: number;
  flows: Array<{
    link_id: string;
    count: number;                 // Number of traversals this frame
    entity_ids: string[];          // Which subentities traversed
  }>;
}

/**
 * Frame End Event (v2)
 *
 * Marks the end of a consciousness frame with diagnostics.
 *
 * Extended fields per diffusion_v2.md spec:
 * - Conservation tracking (energy_in, energy_transferred, energy_decay, deltaE_total)
 * - Frontier size metrics (active_count, shadow_count)
 * - Diffusion metrics (mean_degree_active, diffusion_radius)
 */
export interface FrameEndEvent {
  type: 'frame.end';
  v: '2';
  kind: 'frame.end';
  frame_id: number;

  // Conservation metrics
  energy_in?: number;              // Sum of stimulus injections this frame
  energy_transferred?: number;     // Sum of all |?E| moved
  energy_decay?: number;           // Total loss to decay this frame
  deltaE_total?: number;           // Conservation error (should be ˜0)
  conservation_error_pct?: number; // Percentage error

  // Frontier metrics
  active_count?: number;           // Count of nodes above threshold
  shadow_count?: number;           // Count of 1-hop neighbors

  // Diffusion metrics
  mean_degree_active?: number;     // Average out-degree of active nodes
  diffusion_radius?: number;       // Distance from initial stimuli
}

/**
 * Emotion Events - Emotion Coloring Mechanism
 *
 * These events track emotional metadata (separate from activation energy)
 * that colors nodes and links during traversal.
 *
 * Source: orchestration/mechanisms/emotion_coloring.py
 * Spec: docs/specs/v2/emotion/emotion_coloring.md
 */

/**
 * Emotion Axis Value
 *
 * Represents a single axis in the emotion vector with its magnitude.
 * For Phase 1: [("valence", value), ("arousal", value)]
 */
export interface EmotionAxis {
  axis: string;  // e.g., "valence", "arousal"
  value: number; // -1 to +1
}

/**
 * Node Emotion Update Event
 *
 * Emitted when a node's emotion vector is colored during traversal.
 * Sampled at EMOTION_COLOR_SAMPLE_RATE to manage bandwidth.
 *
 * Frequency: Sampled (e.g., 10% of node visits)
 * Source: emotion_coloring.color_element()
 */
export interface NodeEmotionUpdateEvent {
  type: 'node.emotion.update';
  node_id: string;           // Node ID that was colored
  emotion_magnitude: number; // ||E_emo|| after update (0-1)
  top_axes: EmotionAxis[];   // Top K emotion axes, e.g., [{ axis: "valence", value: 0.42 }]
  delta_mag: number;         // Change in magnitude since last update
  timestamp: string;         // ISO 8601 timestamp
}

/**
 * Link Emotion Update Event
 *
 * Emitted when a link's emotion vector is colored during traversal.
 * Sampled at EMOTION_COLOR_SAMPLE_RATE to manage bandwidth.
 *
 * Frequency: Sampled (e.g., 10% of link traversals)
 * Source: emotion_coloring.color_element()
 */
export interface LinkEmotionUpdateEvent {
  type: 'link.emotion.update';
  link_id: string;           // Link ID that was colored
  emotion_magnitude: number; // ||E_emo|| after update (0-1)
  top_axes: EmotionAxis[];   // Top K emotion axes
  delta_mag: number;         // Change in magnitude since last update
  timestamp: string;         // ISO 8601 timestamp
}

/**
 * Stride Execution Event (Planned - Phase 1)
 *
 * Emitted when a stride (link traversal) is executed with emotion attribution.
 * Shows WHY a path was chosen: semantic similarity vs emotional factors.
 *
 * Frequency: Every stride execution
 * Source: sub_entity_traversal.py (planned integration)
 */
export interface StrideExecEvent {
  type: 'stride.exec';
  entity_id: string;          // Active entity executing stride
  source_node_id: string;      // Source node
  target_node_id: string;      // Target node
  link_id: string;             // Link traversed
  base_cost: number;           // Semantic cost before emotion gates
  resonance_score: number;     // Similarity to current affect (0-1)
  complementarity_score: number; // Opposition to current affect (0-1)
  resonance_multiplier: number;  // Cost reduction from resonance (0.5-1.0)
  comp_multiplier: number;       // Cost reduction from complementarity (0.5-1.0)
  final_cost: number;          // Final cost after emotion gates

  // 3-Tier Strengthening Fields (Priority 2)
  tier?: 'strong' | 'medium' | 'weak';  // Strengthening tier
  tier_scale?: number;                   // Scale factor (1.0 | 0.6 | 0.3)
  reason?: 'co_activation' | 'causal' | 'background'; // Why this tier
  stride_utility_zscore?: number;        // Z-scored F for noise filtering
  learning_enabled?: boolean;            // Whether learning occurred

  timestamp: string;           // ISO 8601 timestamp
}

/**
 * Affective Telemetry Events - PR-A Instrumentation Foundation
 *
 * Per IMPLEMENTATION_PLAN.md PR-A.2: Event schema definitions for affective coupling mechanisms.
 * These events are emitted when AFFECTIVE_TELEMETRY_ENABLED=true (default: false).
 *
 * Source: orchestration/core/events.py (backend definitions)
 * Author: Felix "Ironhand" (backend), Iris "The Aperture" (frontend types)
 * Date: 2025-10-23
 * PR: PR-A (Instrumentation Foundation - ZERO RISK)
 */

/**
 * Affective Threshold Event
 *
 * Emitted when affect modulates activation threshold (PR-B mechanism).
 * Frequency: Per threshold computation (sampled at TELEMETRY_SAMPLE_RATE)
 */
export interface AffectiveThresholdEvent {
  type: 'affective.threshold';
  node_id: string;
  theta_base: number;              // Base threshold before affect
  theta_adjusted: number;          // Threshold after affective modulation
  h: number;                       // Threshold reduction amount
  affective_alignment: number;     // cos(A, E_emo) alignment score
  emotion_magnitude: number;       // ||E_emo|| magnitude
  timestamp: string;
}

/**
 * Affective Memory Event
 *
 * Emitted when affect amplifies weight updates (PR-B mechanism).
 * Frequency: Per weight update (sampled)
 */
export interface AffectiveMemoryEvent {
  type: 'affective.memory';
  node_id: string;
  m_affect: number;                // Affective multiplier (1.0 - 1.3)
  emotion_magnitude: number;       // ||E_emo|| magnitude
  delta_log_w_base: number;        // Weight update before amplification
  delta_log_w_amplified: number;   // Weight update after amplification
  timestamp: string;
}

/**
 * Coherence Persistence Event
 *
 * Emitted when tracking coherence lock-in risk (PR-B mechanism).
 * Frequency: Per entity tick (sampled)
 */
export interface CoherencePersistenceEvent {
  type: 'coherence.persistence';
  entity_id: string;
  coherence_persistence: number;   // Consecutive frames in same state
  lambda_res_effective: number;    // Resonance strength after decay
  lock_in_risk: boolean;           // True if persistence > threshold
  timestamp: string;
}

/**
 * Multi-Pattern Response Event
 *
 * Emitted when multi-pattern affective response active (PR-C mechanism).
 * Frequency: Per entity tick when AFFECTIVE_RESPONSE_V2=true (sampled)
 */
export interface MultiPatternResponseEvent {
  type: 'pattern.multiresponse';
  entity_id: string;
  pattern_selected: 'regulation' | 'rumination' | 'distraction';
  pattern_weights: [number, number, number]; // [w_reg, w_rum, w_dist]
  m_affect: number;                // Combined affective multiplier
  rumination_streak: number;       // Consecutive rumination frames
  capped: boolean;                 // True if rumination cap hit
  timestamp: string;
}

/**
 * Identity Multiplicity Event
 *
 * Emitted when detecting identity fragmentation (PR-D mechanism).
 * Frequency: Per entity tick when IDENTITY_MULTIPLICITY_ENABLED=true
 */
export interface IdentityMultiplicityEvent {
  type: 'identity.multiplicity';
  entity_id: string;
  multiplicity_detected: boolean;  // True if multiplicity criteria met
  task_progress_rate: number;      // Progress rate (0-1)
  energy_efficiency: number;       // Efficiency (0-1)
  identity_flip_count: number;     // Flips in window
  window_frames: number;           // Rolling window size
  timestamp: string;
}

/**
 * Consolidation Event
 *
 * Emitted when consolidation slows decay (PR-E mechanism).
 * Frequency: Per consolidation application (sampled)
 */
export interface ConsolidationEvent {
  type: 'consolidation';
  node_id: string;
  node_type: string;               // Node type (Memory, Task, etc.)
  decay_factor_base: number;       // Base decay (e.g., 0.95)
  decay_factor_consolidated: number; // After consolidation (e.g., 0.975)
  consolidation_strength: number;  // Strength factor (0-1)
  importance_score: number;        // Why this node was consolidated
  timestamp: string;
}

/**
 * Decay Resistance Event
 *
 * Emitted when structural resistance affects decay (PR-E mechanism).
 * Frequency: Per resistance computation (every N ticks)
 */
export interface DecayResistanceEvent {
  type: 'decay.resistance';
  node_id: string;
  resistance_score: number;        // Structural resistance (0-1)
  in_degree: number;               // Incoming links
  out_degree: number;              // Outgoing links
  betweenness_centrality: number;  // Graph centrality
  decay_reduction: number;         // How much decay was reduced
  timestamp: string;
}

/**
 * Stickiness Event
 *
 * Emitted when diffusion stickiness affects energy flow (PR-E mechanism).
 * Frequency: Per stride execution (sampled)
 */
export interface StickinessEvent {
  type: 'diffusion.stickiness';
  link_id: string;
  source_node_id: string;
  target_node_id: string;
  target_type: string;             // Node type of target
  stickiness_factor: number;       // s_type (0-1)
  energy_retained: number;         // Energy kept at target
  energy_returned: number;         // Energy reflected back
  timestamp: string;
}

/**
 * Affective Priming Event
 *
 * Emitted when affect primes stimulus injection (PR-E mechanism).
 * Frequency: Per stimulus injection (sampled)
 */
export interface AffectivePrimingEvent {
  type: 'affective.priming';
  node_id: string;
  affect_alignment: number;        // cos(A_recent, E_node)
  priming_boost: number;           // Budget multiplier (0-1.15)
  budget_before: number;           // Budget before priming
  budget_after: number;            // Budget after priming
  timestamp: string;
}

/**
 * Coherence Metric Event
 *
 * Emitted when coherence quality metric computed (PR-E mechanism).
 * Frequency: Per tick when COHERENCE_METRIC_ENABLED=true
 */
export interface CoherenceMetricEvent {
  type: 'coherence.metric';
  coherence: number;               // C metric (0-1)
  frontier_similarity: number;     // Frontier cohesion component
  stride_relatedness: number;      // Stride relatedness component
  window_frames: number;           // Rolling window size
  timestamp: string;
}

/**
 * Criticality Mode Event
 *
 * Emitted when criticality mode classified (PR-E mechanism).
 * Frequency: Per tick when CRITICALITY_MODES_ENABLED=true
 */
export interface CriticalityModeEvent {
  type: 'criticality.mode';
  mode: 'fragmented' | 'exploring' | 'flowing' | 'focused';
  rho: number;                     // Spectral radius
  coherence: number;               // C metric
  description: string;             // Mode explanation
  timestamp: string;
}

/**
 * Weights Updated (TRACE) Event - Priority 4
 *
 * Emitted when TRACE results update node/link weights.
 * Shows context-aware learning (80% to active entities, 20% global).
 * Frequency: Per TRACE application (sampled)
 */
export interface WeightsUpdatedTraceEvent {
  type: 'weights.updated.trace';
  frame_id: number;
  scope: 'link' | 'node' | 'membership';  // What was updated
  cohort: string;                          // Entity cohort
  entity_contexts: string[];               // Which entities (80% split)
  global_context: boolean;                 // Whether 20% global applied
  n: number;                               // Count of weights updated
  d_mu: number;                           // Mean change
  d_sigma: number;                        // Std change
  timestamp: string;
}

/**
 * Weights Updated (Traversal) Event - Priority 4
 *
 * Emitted when traversal strengthening updates weights.
 * Frequency: Per weight learning application (sampled)
 */
export interface WeightsUpdatedTraversalEvent {
  type: 'weights.updated.traversal';
  frame_id: number;
  scope: 'link' | 'node';
  cohort: string;
  entity_attribution: string;              // Which entity's traversal
  n: number;
  d_mu: number;
  d_sigma: number;
  timestamp: string;
}

/**
 * Stride Selection Event - Priority 5
 *
 * Emitted when choosing fanout strategy for traversal.
 * Shows task-mode-aware attention control.
 * Frequency: Per stride selection (sampled)
 */
export interface StrideSelectionEvent {
  type: 'stride.selection';
  frame_id: number;
  node_id: string;                        // Current node
  fanout: number;                         // Out-degree
  strategy: 'selective' | 'balanced' | 'exhaustive'; // Strategy chosen
  top_k: number;                          // Candidates considered
  task_mode: 'focused' | 'balanced' | 'divergent' | 'methodical' | null;
  task_mode_override: boolean;            // Whether mode overrode structure
  structure_would_suggest: string;        // What structure-only would choose
  wm_headroom: number;                    // WM capacity remaining (0-1)
  timestamp: string;
}

/**
 * Phenomenology Mismatch Event - Priority 6
 *
 * Emitted when substrate-inferred affect diverges from entity self-report.
 * Shows consciousness substrate-phenomenology alignment.
 * Frequency: Per tick when mismatch detected
 */
export interface PhenomenologyMismatchEvent {
  type: 'phenomenology.mismatch';
  frame_id: number;
  entity_id: string;
  substrate_valence: number;              // Inferred from emotion vectors
  substrate_arousal: number;
  substrate_mag: number;
  selfreport_valence: number;             // From entity introspection
  selfreport_arousal: number;
  selfreport_mag: number;
  divergence: number;                     // Euclidean distance
  threshold: number;                      // Mismatch threshold
  mismatch_detected: boolean;
  mismatch_type: 'valence_flip' | 'arousal_mismatch' | 'magnitude_divergence' | 'coherent';
  timestamp: string;
}

/**
 * Phenomenological Health Event - Priority 6
 *
 * Emitted to track consciousness health across dimensions.
 * Shows flow state, coherence alignment, multiplicity health.
 * Frequency: Per tick (sampled)
 */
export interface PhenomenologicalHealthEvent {
  type: 'phenomenological_health';
  frame_id: number;
  entity_id: string;

  // Flow state metrics
  flow_state: number;                     // Overall flow (0-1)
  wm_challenge_balance: number;           // WM capacity vs challenge
  engagement: number;                     // Energy investment
  skill_demand_match: number;             // Capability vs demands

  // Coherence metrics
  coherence_alignment: number;            // 0-1
  resonance_dominance_ratio: number;      // res/(res+comp)

  // Multiplicity metrics
  multiplicity_health: number;            // 0-1
  distinct_entities_coactive: number;     // Count
  thrashing_detected: boolean;
  co_activation_stability: number;        // Stability over frames

  overall_health: number;                 // Aggregate (0-1)
  timestamp: string;
}

/**
 * Union type of all WebSocket events
 */
export type WebSocketEvent =
  | EntityActivityEvent
  | ThresholdCrossingEvent
  | ConsciousnessStateEvent
  | FrameStartEvent
  | WmEmitEvent
  | NodeFlipEvent
  | LinkFlowSummaryEvent
  | FrameEndEvent
  | NodeEmotionUpdateEvent
  | LinkEmotionUpdateEvent
  | StrideExecEvent
  | WeightsUpdatedTraceEvent
  | WeightsUpdatedTraversalEvent
  | StrideSelectionEvent
  | PhenomenologyMismatchEvent
  | PhenomenologicalHealthEvent
  | AffectiveThresholdEvent
  | AffectiveMemoryEvent
  | CoherencePersistenceEvent
  | MultiPatternResponseEvent
  | IdentityMultiplicityEvent
  | ConsolidationEvent
  | DecayResistanceEvent
  | StickinessEvent
  | AffectivePrimingEvent
  | CoherenceMetricEvent
  | CriticalityModeEvent;

/**
 * WebSocket connection state
 */
export enum WebSocketState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  DISCONNECTED = 'disconnected',
  ERROR = 'error'
}

/**
 * V2 Consciousness State
 *
 * Live frame-by-frame consciousness metrics for real-time visualization.
 * Extended with system health metrics per observability_requirements_v2_complete.md
 */
export interface V2ConsciousnessState {
  // Frame tracking
  currentFrame: number | null;     // Current frame ID
  frameEvents: FrameStartEvent[];  // Recent frame.start events (for Priority 3 tick speed viz)

  // Criticality metrics (from frame.start)
  rho: number | null;               // Branching ratio (?) - thought expansion metric
  safety_state: 'subcritical' | 'critical' | 'supercritical' | null; // System stability

  // Timing metrics (from frame.start)
  dt_ms: number | null;             // Wall-clock time since last tick
  interval_sched: number | null;    // Scheduled interval
  dt_used: number | null;           // Physics dt actually used

  // Conservation metrics (from frame.end)
  deltaE_total: number | null;      // Conservation error (should be ˜0)
  conservation_error_pct: number | null; // Error as percentage
  energy_in: number | null;         // Energy injected this frame
  energy_transferred: number | null; // Energy moved this frame
  energy_decay: number | null;      // Energy lost to decay

  // Frontier metrics (from frame.end)
  active_count: number | null;      // Nodes above threshold
  shadow_count: number | null;      // 1-hop neighbors
  diffusion_radius: number | null;  // Distance from stimuli

  // Working memory and traversal
  workingMemory: Set<string>;       // Node IDs currently in working memory
  recentFlips: NodeFlipEvent[];     // Recent threshold crossings (last 20)
  linkFlows: Map<string, number>;   // Link ID -> traversal count this frame
}

/**
 * Emotion Metadata Store
 *
 * Tracks emotion vectors for nodes and links with hysteresis for flicker prevention.
 */
export interface EmotionMetadata {
  magnitude: number;              // ||E_emo|| (0-1)
  axes: EmotionAxis[];           // Emotion axes with values
  lastUpdated: number;           // Timestamp of last update
  displayedMagnitude: number;    // Last magnitude actually rendered (for hysteresis)
}

/**
 * Emotion Coloring State
 *
 * Real-time emotion metadata for mood map and attribution.
 */
export interface EmotionColoringState {
  nodeEmotions: Map<string, EmotionMetadata>;    // Node ID -> emotion metadata
  linkEmotions: Map<string, EmotionMetadata>;    // Link ID -> emotion metadata
  recentStrides: StrideExecEvent[];               // Last N strides for attribution
  regulationRatio: number | null;                 // Complementarity / (comp + res) ratio
  resonanceRatio: number | null;                  // Resonance / (comp + res) ratio
  saturationWarnings: string[];                   // Node IDs with high saturation (>0.9)
}

/**
 * Aggregated event streams
 *
 * This is what the useWebSocket hook returns -
 * separate arrays for each event type for easy consumption.
 */
export interface WebSocketStreams {
  // V1 events (legacy)
  entityActivity: EntityActivityEvent[];
  thresholdCrossings: ThresholdCrossingEvent[];
  consciousnessState: ConsciousnessStateEvent | null;

  // V2 events (frame-based)
  v2State: V2ConsciousnessState;

  // Emotion coloring events
  emotionState: EmotionColoringState;

  // Priority 4: Weight learning events
  weightLearningEvents: WeightsUpdatedTraceEvent[];

  // Priority 5: Stride selection events
  strideSelectionEvents: StrideSelectionEvent[];

  // Priority 6: Phenomenology health events
  phenomenologyMismatchEvents: PhenomenologyMismatchEvent[];
  phenomenologyHealthEvents: PhenomenologicalHealthEvent[];

  // Connection state
  connectionState: WebSocketState;
  error: string | null;
}


## <<< END app/consciousness/hooks/websocket-types.ts
---
