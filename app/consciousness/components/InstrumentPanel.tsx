/**
 * Instrument Panel Component
 *
 * Left sidebar containing emotion regulation instruments:
 * - Regulation vs Coherence Index (comp vs res ratio)
 * - Staining Watch (emotion saturation monitoring)
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 */

'use client';

import { RegulationIndex } from './RegulationIndex';
import { StainingWatch } from './StainingWatch';

export function InstrumentPanel() {
  return (
    <div className="fixed left-4 top-24 z-40 w-80 max-h-[calc(100vh-7rem)] overflow-y-auto custom-scrollbar space-y-4">
      {/* Regulation vs Coherence Index */}
      <RegulationIndex />

      {/* Staining Watch */}
      <StainingWatch />
    </div>
  );
}
