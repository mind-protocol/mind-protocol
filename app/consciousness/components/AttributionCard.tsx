/**
 * Attribution Card Component
 *
 * Shows WHY a specific stride (edge traversal) was chosen, breaking down
 * the decision into semantic similarity, complementarity, and resonance factors.
 *
 * Displays:
 * - Active entity affect vector
 * - Local edge emotion vector
 * - Complementarity and resonance scores/multipliers
 * - Cost breakdown percentages
 *
 * Spec: emotion_color_mapping_v2_canonical.md § Attribution Cards
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 */

'use client';

import { useMemo } from 'react';
import type { StrideExecEvent, EmotionMetadata, EmotionAxis } from '../hooks/websocket-types';
import { getQuadrantLabel, getAxisBadges } from '../lib/emotionColor';

interface AttributionCardProps {
  stride: StrideExecEvent | null;
  edgeEmotion?: EmotionMetadata;
}

/**
 * Calculate cost contribution percentages
 *
 * Attribution logic:
 * - Base cost represents semantic similarity
 * - Comp multiplier < 1.0 means complementarity reduced cost
 * - Res multiplier < 1.0 means resonance reduced cost
 *
 * @param stride Stride execution event
 * @returns Percentage breakdown {semantic, comp, res}
 */
function calculateAttribution(stride: StrideExecEvent): {
  semantic: number;
  comp: number;
  res: number;
} {
  // Cost reductions
  const compReduction = 1 - stride.comp_multiplier;  // 0 if no effect, 0.5 if multiplier = 0.5
  const resReduction = 1 - stride.resonance_multiplier;

  const totalReduction = compReduction + resReduction;

  if (totalReduction < 0.01) {
    // No emotional contribution - 100% semantic
    return { semantic: 100, comp: 0, res: 0 };
  }

  // Total "influence" = base (semantic) + reductions (emotional)
  // Assume base cost was 1.0 before multipliers
  const semanticInfluence = 1.0; // Always present
  const totalInfluence = semanticInfluence + totalReduction;

  return {
    semantic: (semanticInfluence / totalInfluence) * 100,
    comp: (compReduction / totalInfluence) * 100,
    res: (resReduction / totalInfluence) * 100
  };
}

/**
 * Format emotion axes for display
 */
function formatAxes(axes: EmotionAxis[]): string {
  return axes.map(a => `${a.axis}: ${a.value.toFixed(2)}`).join(', ');
}

export function AttributionCard({ stride, edgeEmotion }: AttributionCardProps) {
  // Calculate attribution breakdown
  const attribution = useMemo(() => {
    if (!stride) return null;
    return calculateAttribution(stride);
  }, [stride]);

  if (!stride) {
    return (
      <div className="attribution-card bg-slate-900 border border-slate-700 rounded-lg p-4 text-slate-300">
        <h3 className="text-sm font-semibold mb-2">Edge Choice Attribution</h3>
        <p className="text-xs text-slate-500">Click a link to see attribution</p>
      </div>
    );
  }

  // Extract emotion data if available
  const edgeValence = edgeEmotion?.axes.find(a => a.axis === 'valence')?.value ?? null;
  const edgeArousal = edgeEmotion?.axes.find(a => a.axis === 'arousal')?.value ?? null;

  return (
    <div className="attribution-card bg-slate-900 border border-slate-700 rounded-lg p-4 text-slate-300 space-y-3">
      <h3 className="text-sm font-semibold border-b border-slate-700 pb-2">
        Edge Choice Attribution
      </h3>

      {/* Entity ID */}
      <div className="text-xs">
        <span className="text-slate-500">Entity:</span>{' '}
        <span className="font-mono text-slate-300">{stride.entity_id}</span>
      </div>

      {/* Edge info */}
      <div className="text-xs">
        <span className="text-slate-500">Edge:</span>{' '}
        <span className="font-mono text-slate-400">
          {stride.source_node_id} → {stride.target_node_id}
        </span>
      </div>

      {/* Edge emotion (if available) */}
      {edgeEmotion && edgeValence !== null && edgeArousal !== null && (
        <div className="bg-slate-800 rounded p-2 space-y-1">
          <div className="text-xs font-semibold text-slate-400">Local Edge Emotion</div>
          <div className="text-xs font-mono">
            Valence: <span className="text-slate-300">{edgeValence.toFixed(2)}</span>,{' '}
            Arousal: <span className="text-slate-300">{edgeArousal.toFixed(2)}</span>
          </div>
          <div className="text-xs">
            <span className="text-slate-500">Quadrant:</span>{' '}
            <span className="text-slate-300">
              {getQuadrantLabel(edgeValence, edgeArousal)}
            </span>
          </div>
          {getAxisBadges(edgeValence, edgeArousal).length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {getAxisBadges(edgeValence, edgeArousal).map(badge => (
                <span
                  key={badge}
                  className="text-xs px-2 py-0.5 bg-slate-700 text-slate-300 rounded"
                >
                  {badge}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Scores */}
      <div className="space-y-2 pt-2 border-t border-slate-700">
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-500">Complementarity Score</span>
          <span className="font-mono text-blue-400">
            {stride.complementarity_score.toFixed(2)}
          </span>
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-500">Resonance Score</span>
          <span className="font-mono text-orange-400">
            {stride.resonance_score.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Multipliers */}
      <div className="space-y-2 pt-2 border-t border-slate-700">
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-500">Comp Multiplier</span>
          <span className="font-mono text-blue-400">
            {stride.comp_multiplier.toFixed(2)}
            {stride.comp_multiplier < 1 && (
              <span className="text-xs text-blue-300 ml-1">
                (↓{((1 - stride.comp_multiplier) * 100).toFixed(0)}% cost)
              </span>
            )}
          </span>
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-500">Res Multiplier</span>
          <span className="font-mono text-orange-400">
            {stride.resonance_multiplier.toFixed(2)}
            {stride.resonance_multiplier < 1 && (
              <span className="text-xs text-orange-300 ml-1">
                (↓{((1 - stride.resonance_multiplier) * 100).toFixed(0)}% cost)
              </span>
            )}
          </span>
        </div>
      </div>

      {/* Cost breakdown */}
      {attribution && (
        <div className="space-y-2 pt-2 border-t border-slate-700">
          <div className="text-xs font-semibold text-slate-400">
            Decision Breakdown
          </div>
          <div className="space-y-1">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-500">Semantic Similarity</span>
              <span className="font-mono text-slate-300">
                {attribution.semantic.toFixed(0)}%
              </span>
            </div>
            {attribution.comp > 0.5 && (
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Complementarity (regulation)</span>
                <span className="font-mono text-blue-400">
                  {attribution.comp.toFixed(0)}%
                </span>
              </div>
            )}
            {attribution.res > 0.5 && (
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Resonance (coherence)</span>
                <span className="font-mono text-orange-400">
                  {attribution.res.toFixed(0)}%
                </span>
              </div>
            )}
          </div>

          {/* Explanation text */}
          <div className="text-xs text-slate-400 italic mt-2 pt-2 border-t border-slate-800">
            This edge chosen because:{' '}
            {attribution.semantic > 70
              ? 'primarily semantic similarity'
              : attribution.comp > attribution.res
              ? 'seeking emotional balance (complementarity)'
              : 'maintaining emotional coherence (resonance)'}
          </div>
        </div>
      )}

      {/* Costs (if available) */}
      {stride.base_cost !== undefined && stride.final_cost !== undefined && (
        <div className="space-y-1 pt-2 border-t border-slate-700 text-xs">
          <div className="flex justify-between">
            <span className="text-slate-500">Base Cost</span>
            <span className="font-mono text-slate-400">
              {stride.base_cost.toFixed(3)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Final Cost</span>
            <span className="font-mono text-green-400">
              {stride.final_cost.toFixed(3)}
            </span>
          </div>
          {stride.base_cost > stride.final_cost && (
            <div className="text-xs text-green-400">
              ↓ {((1 - stride.final_cost / stride.base_cost) * 100).toFixed(0)}% reduction
            </div>
          )}
        </div>
      )}
    </div>
  );
}
