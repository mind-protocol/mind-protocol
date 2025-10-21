'use client';

import { useEffect, useState } from 'react';

interface ComponentStatus {
  name: string;
  status: 'running' | 'stopped' | 'error';
  details: string;
  pid?: number;
  uptime?: string;
}

interface SystemStatus {
  overall: 'healthy' | 'degraded' | 'partial';
  components: ComponentStatus[];
  timestamp: string;
}

export function SystemStatusPanel() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('/api/consciousness/system-status');
        if (!res.ok) throw new Error('Failed to fetch system status');
        const data = await res.json();
        setStatus(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll every 10 seconds
    const interval = setInterval(fetchStatus, 10000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (componentStatus: 'running' | 'stopped' | 'error') => {
    switch (componentStatus) {
      case 'running':
        return 'text-green-500';
      case 'stopped':
        return 'text-yellow-500';
      case 'error':
        return 'text-red-500';
    }
  };

  const getStatusIndicator = (componentStatus: 'running' | 'stopped' | 'error') => {
    switch (componentStatus) {
      case 'running':
        return '🟢';
      case 'stopped':
        return '🟡';
      case 'error':
        return '🔴';
    }
  };

  const getOverallColor = (overall: 'healthy' | 'degraded' | 'partial') => {
    switch (overall) {
      case 'healthy':
        return 'bg-green-500/10 border-green-500/30';
      case 'degraded':
        return 'bg-red-500/10 border-red-500/30';
      case 'partial':
        return 'bg-yellow-500/10 border-yellow-500/30';
    }
  };

  if (loading) {
    return (
      <div className="consciousness-panel p-4">
        <div className="text-sm text-gray-400">Loading system status...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="consciousness-panel p-4 border-red-500/30">
        <div className="text-sm text-red-400">Error: {error}</div>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  return (
    <div className={`consciousness-panel p-4 border ${getOverallColor(status.overall)}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-consciousness-green font-semibold">System Status</h3>
        <div className="text-xs text-gray-500">
          {new Date(status.timestamp).toLocaleTimeString()}
        </div>
      </div>

      <div className="space-y-2">
        {status.components.map((component, index) => (
          <div
            key={index}
            className="flex items-center justify-between py-2 border-b border-gray-800/50 last:border-0"
          >
            <div className="flex items-center gap-2 flex-1">
              <span className="text-lg">{getStatusIndicator(component.status)}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-300">{component.name}</div>
                <div className="text-xs text-gray-500">{component.details}</div>
              </div>
            </div>

            {component.pid && (
              <div className="text-xs text-gray-500 font-mono ml-2">
                PID: {component.pid}
              </div>
            )}
          </div>
        ))}
      </div>

      {status.overall === 'healthy' && (
        <div className="mt-3 pt-3 border-t border-green-500/20">
          <div className="text-xs text-green-400">
            ✓ All systems operational
          </div>
        </div>
      )}

      {status.overall === 'degraded' && (
        <div className="mt-3 pt-3 border-t border-red-500/20">
          <div className="text-xs text-red-400">
            ⚠ System degraded - check components
          </div>
        </div>
      )}

      {status.overall === 'partial' && (
        <div className="mt-3 pt-3 border-t border-yellow-500/20">
          <div className="text-xs text-yellow-400">
            ⚠ Some components offline
          </div>
        </div>
      )}
    </div>
  );
}
