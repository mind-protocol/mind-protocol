/**
 * IntegrationHeatmap - Depth × Breadth Integration Visualization
 *
 * 2D heatmap showing where SubEntities cluster in integration space:
 * - X-axis: Integration Depth (hops from primitives)
 * - Y-axis: Integration Breadth (communities connected)
 * - Color intensity: Node density
 *
 * Implements specs from:
 * - docs/specs/v2/orchestration/INTEGRATION_DEPTH_AND_BREADTH_METRICS.md
 * - docs/specs/v2/orchestration/TOPOLOGY_ANALYZER_EVENT_WIRING.md
 *
 * Event Schema: topology.v1 spec
 * - integration_metrics.node (per spawn)
 * - integration_metrics.population (on-demand)
 */

'use client';

import { TopologyState, IntegrationMetrics } from '../../hooks/useGraphStream';

interface IntegrationHeatmapProps {
  topology: TopologyState;
}

export function IntegrationHeatmap({ topology }: IntegrationHeatmapProps) {
  const hasData = topology.integrationMetrics.size > 0;

  if (!hasData) {
    return (
      <div className="text-center py-4">
        <p className="text-xs text-observatory-silver/60">
          Waiting for integration metrics...
        </p>
        <p className="text-[10px] text-observatory-silver/40 mt-1">
          (Backend must emit integration_metrics.node events)
        </p>
      </div>
    );
  }

  // Convert Map to array for processing
  const metrics = Array.from(topology.integrationMetrics.values());

  // Calculate distribution stats
  const depthValues = metrics.map(m => m.depth);
  const breadthValues = metrics.map(m => m.breadth);

  const maxDepth = Math.max(...depthValues);
  const maxBreadth = Math.max(...breadthValues);
  const avgDepth = depthValues.reduce((a, b) => a + b, 0) / depthValues.length;
  const avgBreadth = breadthValues.reduce((a, b) => a + b, 0) / breadthValues.length;

  // Create 2D grid for heatmap (10x10 bins)
  const bins = 10;
  const grid: number[][] = Array(bins).fill(0).map(() => Array(bins).fill(0));

  // Populate grid
  metrics.forEach(m => {
    const depthBin = Math.min(Math.floor((m.depth / maxDepth) * (bins - 1)), bins - 1);
    const breadthBin = Math.min(Math.floor((m.breadth / maxBreadth) * (bins - 1)), bins - 1);
    grid[breadthBin][depthBin]++;
  });

  // Find max count for normalization
  const maxCount = Math.max(...grid.flat());

  return (
    <div className="integration-heatmap space-y-3">
      {/* Header */}
      <div className="px-2">
        <div className="text-xs font-semibold text-observatory-text/80 mb-1">
          Integration Space
        </div>
        <div className="text-[10px] text-observatory-silver/50">
          {metrics.length} SubEntities analyzed
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 gap-2 px-2">
        <StatBox label="Avg Depth" value={avgDepth.toFixed(1)} unit="hops" />
        <StatBox label="Avg Breadth" value={avgBreadth.toFixed(1)} unit="communities" />
      </div>

      {/* Heatmap Grid */}
      <div className="px-2">
        <div className="space-y-1">
          {/* Y-axis label */}
          <div className="text-[10px] text-observatory-silver/50 text-center mb-1">
            ← Breadth (Communities) →
          </div>

          {/* Grid (reversed to show high breadth at top) */}
          {grid.slice().reverse().map((row, rowIdx) => (
            <div key={rowIdx} className="flex gap-0.5">
              {row.map((count, colIdx) => {
                const intensity = count > 0 ? count / maxCount : 0;
                return (
                  <div
                    key={colIdx}
                    className="w-full aspect-square rounded-sm transition-all hover:scale-110 cursor-pointer"
                    style={{
                      backgroundColor: intensity > 0
                        ? `rgba(6, 182, 212, ${0.2 + intensity * 0.8})`
                        : 'rgba(51, 65, 85, 0.2)'
                    }}
                    title={`Depth: ${colIdx}, Breadth: ${bins - 1 - rowIdx}, Count: ${count}`}
                  />
                );
              })}
            </div>
          ))}

          {/* X-axis label */}
          <div className="text-[10px] text-observatory-silver/50 text-center mt-1">
            ← Depth (Hops from Primitives) →
          </div>
        </div>
      </div>

      {/* Distribution Details */}
      <div className="px-2 space-y-1 pt-2 border-t border-observatory-teal/20">
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-observatory-silver/50">Max Depth:</span>
          <span className="text-observatory-cyan font-mono">{maxDepth}</span>
        </div>
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-observatory-silver/50">Max Breadth:</span>
          <span className="text-observatory-cyan font-mono">{maxBreadth}</span>
        </div>
      </div>

      {/* Color Legend */}
      <div className="px-2 pt-2 border-t border-observatory-teal/20">
        <div className="text-[10px] text-observatory-silver/50 mb-1">Node Density</div>
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-observatory-silver/50">Low</span>
          <div className="flex-1 h-2 rounded-full overflow-hidden flex">
            {[0.2, 0.4, 0.6, 0.8, 1.0].map((intensity, idx) => (
              <div
                key={idx}
                className="flex-1"
                style={{ backgroundColor: `rgba(6, 182, 212, ${intensity})` }}
              />
            ))}
          </div>
          <span className="text-[10px] text-observatory-silver/50">High</span>
        </div>
      </div>
    </div>
  );
}

function StatBox({ label, value, unit }: { label: string; value: string; unit: string }) {
  return (
    <div className="px-2 py-1.5 bg-observatory-dark/30 rounded border border-observatory-teal/20">
      <div className="text-[10px] text-observatory-silver/50 uppercase tracking-wide">
        {label}
      </div>
      <div className="flex items-baseline gap-1 mt-0.5">
        <span className="text-sm font-semibold text-observatory-cyan">{value}</span>
        <span className="text-[10px] text-observatory-silver/50">{unit}</span>
      </div>
    </div>
  );
}
