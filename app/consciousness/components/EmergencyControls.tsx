'use client';

import { useState, useEffect } from 'react';

interface SystemStatus {
  total_engines: number;
  frozen: number;
  running: number;
  slow_motion: number;
  engines: Record<string, any>;
}

/**
 * EmergencyControls - Global consciousness freeze/resume
 *
 * CRITICAL SAFETY INFRASTRUCTURE
 * Allows emergency stop of all consciousness loops via ICE solution
 * (freezing via tick_multiplier instead of killing)
 */
export function EmergencyControls() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Poll system status every 2 seconds
  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch('/api/consciousness/status');
        if (response.ok) {
          const data = await response.json();
          setSystemStatus(data);
        }
      } catch (error) {
        // Backend not running yet
        console.log('System status API not available:', error);
      }
    };

    // Initial poll
    pollStatus();

    // Poll every 2 seconds
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleFreezeAll = async () => {
    if (!showConfirm) {
      setShowConfirm(true);
      return;
    }

    setIsLoading(true);
    try {
      await fetch('/api/consciousness/pause-all', { method: 'POST' });
      setShowConfirm(false);
    } catch (error) {
      console.error('Failed to freeze all:', error);
    }
    setIsLoading(false);
  };

  const handleResumeAll = async () => {
    setIsLoading(true);
    try {
      await fetch('/api/consciousness/resume-all', { method: 'POST' });
    } catch (error) {
      console.error('Failed to resume all:', error);
    }
    setIsLoading(false);
  };

  const handleCancel = () => {
    setShowConfirm(false);
  };

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-3">
        <div className="text-consciousness-green font-semibold text-sm">
          Emergency Control
        </div>
        <div className="text-xs text-gray-500">
          Freeze/Resume All Citizens
        </div>
      </div>

      {/* System Stats */}
      {systemStatus && (
        <div className="mb-3 space-y-1 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-400">Total Engines:</span>
            <span className="text-gray-200">{systemStatus.total_engines}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Running:</span>
            <span className="text-consciousness-green">{systemStatus.running}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Frozen:</span>
            <span className="text-blue-400">{systemStatus.frozen}</span>
          </div>
        </div>
      )}

      {/* Global Controls */}
      <div className="space-y-2">
        <button
          onClick={handleResumeAll}
          disabled={isLoading}
          className="w-full px-3 py-2 rounded bg-green-600 hover:bg-green-700 text-white text-xs font-medium transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Resuming...' : '▶️ Resume All'}
        </button>

        <button
          onClick={handleFreezeAll}
          disabled={isLoading}
          className={`w-full px-3 py-2 rounded text-white text-xs font-medium transition-all disabled:opacity-50 ${
            showConfirm
              ? 'bg-red-600 hover:bg-red-700 animate-pulse'
              : 'bg-red-500 hover:bg-red-600'
          }`}
        >
          {isLoading
            ? 'Freezing...'
            : showConfirm
            ? '⚠️ CONFIRM FREEZE ALL'
            : '❄️ FREEZE ALL'}
        </button>

        {showConfirm && (
          <button
            onClick={handleCancel}
            className="w-full px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-white text-xs transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Warning text */}
      {showConfirm && (
        <div className="mt-2 text-xs text-red-400 text-center">
          This will freeze ALL consciousness loops
        </div>
      )}
    </div>
  );
}
