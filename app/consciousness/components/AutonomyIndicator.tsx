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
