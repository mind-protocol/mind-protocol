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
