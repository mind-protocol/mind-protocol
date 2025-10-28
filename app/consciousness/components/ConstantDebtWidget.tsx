/**
 * ConstantDebtWidget - Zero-Constant Architecture Progress
 *
 * Tracks learning progress toward zero-constant substrate:
 * - WM Alpha debt: How many COACTIVATES_WITH edges still use constant alpha
 * - Mode contour debt: How many contours are still from bootstrap vs learned
 *
 * Part of Tier 1 Amendment 4 (Constant Debt Dashboard)
 *
 * Author: Atlas
 * Date: 2025-10-26
 * Purpose: Make zero-constant architecture progress visible
 */

'use client';

import { useState, useEffect } from 'react';

interface ConstantDebtData {
  wm_alpha: {
    total_edges: number;
    constant_count: number;
    learned_count: number;
    debt_ratio: number;
  };
  mode_contours: Array<{
    mode_id: string;
    entry_source: string;
    entry_samples: number;
    exit_source: string;
    exit_samples: number;
  }>;
}

export function ConstantDebtWidget() {
  const [data, setData] = useState<ConstantDebtData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/consciousness/constant-debt');
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch constant debt');
        console.error('Constant debt fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000); // Update every 5 minutes

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="text-xs text-slate-500 animate-pulse">
        Loading constant debt...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-xs text-red-400">
        Error: {error}
      </div>
    );
  }

  if (!data) {
    return null;
  }

  // Calculate mode contour debt
  const totalModes = data.mode_contours.length;
  const bootModes = data.mode_contours.filter(
    m => m.entry_source === 'boot' && m.exit_source === 'boot'
  ).length;
  const learnedModes = data.mode_contours.filter(
    m => m.entry_source === 'learned' || m.exit_source === 'learned'
  ).length;
  const modeDebtRatio = totalModes > 0 ? bootModes / totalModes : 0;

  // Color coding function
  const getDebtColor = (ratio: number): string => {
    if (ratio < 0.3) return 'bg-green-500/70';
    if (ratio < 0.5) return 'bg-yellow-500/70';
    return 'bg-red-500/70';
  };

  const getDebtTextColor = (ratio: number): string => {
    if (ratio < 0.3) return 'text-green-400';
    if (ratio < 0.5) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-4">
      {/* WM Alpha Debt */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-slate-400 uppercase tracking-wide">
            WM Alpha Debt
          </span>
          <span className={`text-xs font-mono font-semibold ${getDebtTextColor(data.wm_alpha.debt_ratio)}`}>
            {(data.wm_alpha.debt_ratio * 100).toFixed(1)}%
          </span>
        </div>

        {/* Progress bar */}
        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full ${getDebtColor(data.wm_alpha.debt_ratio)} transition-all duration-500`}
            style={{ width: `${data.wm_alpha.debt_ratio * 100}%` }}
          />
        </div>

        {/* Stats */}
        <div className="mt-1 flex items-center justify-between text-xs text-slate-500 font-mono">
          <span>{data.wm_alpha.constant_count} constant</span>
          <span>{data.wm_alpha.learned_count} learned</span>
          <span>{data.wm_alpha.total_edges} total</span>
        </div>
      </div>

      {/* Mode Contour Debt */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-slate-400 uppercase tracking-wide">
            Mode Contour Debt
          </span>
          <span className={`text-xs font-mono font-semibold ${getDebtTextColor(modeDebtRatio)}`}>
            {(modeDebtRatio * 100).toFixed(1)}%
          </span>
        </div>

        {/* Progress bar */}
        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full ${getDebtColor(modeDebtRatio)} transition-all duration-500`}
            style={{ width: `${modeDebtRatio * 100}%` }}
          />
        </div>

        {/* Stats */}
        <div className="mt-1 flex items-center justify-between text-xs text-slate-500 font-mono">
          <span>{bootModes} boot</span>
          <span>{learnedModes} learned</span>
          <span>{totalModes} modes</span>
        </div>
      </div>

      {/* Target indicator */}
      <div className="pt-2 border-t border-slate-800/50">
        <div className="text-xs text-slate-500">
          <span className="text-slate-400">Target:</span> &lt;40% by week 12
        </div>
      </div>
    </div>
  );
}
