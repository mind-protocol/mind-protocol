'use client';

/**
 * Legend Component
 *
 * Shows link type colors and valence gradient.
 * Bottom left corner, always visible.
 */
export function Legend() {
  return (
    <div className="fixed bottom-24 left-6 z-40 space-y-3">
      {/* Link Type Legend */}
      <div className="consciousness-panel px-4 py-3">
        <div className="text-xs text-observatory-text/70 uppercase tracking-wider mb-3">
          Link Types
        </div>
        <div className="space-y-2">
          <LegendItem color="#ef4444" label="JUSTIFIES" />
          <LegendItem color="#3b82f6" label="BUILDS_TOWARD" />
          <LegendItem color="#22c55e" label="ENABLES" />
          <LegendItem color="#8b5cf6" label="USES" />
          <LegendItem color="#666" label="Other" />
        </div>
      </div>

      {/* Valence Legend */}
      <div className="consciousness-panel px-4 py-3">
        <div className="text-xs text-observatory-text/70 uppercase tracking-wider mb-3">
          Valence (Subentity View)
        </div>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-gradient-to-r from-red-500 via-gray-400 to-green-500"></div>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-red-500">Negative</span>
            <span className="text-observatory-text/60">Neutral</span>
            <span className="text-green-500">Positive</span>
          </div>
          <div className="text-xs text-observatory-text/50 mt-2">
            Shows subjective link experience per subentity
          </div>
        </div>
      </div>
    </div>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className="w-6 h-0.5"
        style={{ backgroundColor: color }}
      ></div>
      <span className="text-xs text-observatory-text/80">{label}</span>
    </div>
  );
}
