/**
 * Affective Coupling Recent Events API
 *
 * Returns recent events for PR-B mechanisms:
 * - Threshold modulation events
 * - Affective memory amplification events
 * - Coherence persistence states
 *
 * PR-B: Emotion Couplings
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 */

import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Proxy request to Python backend
    const res = await fetch('http://localhost:8000/api/affective-coupling/recent-events', {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      // Backend not ready yet - return empty arrays
      return NextResponse.json({
        thresholds: [],
        memory: [],
        coherence: []
      });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    // Backend not running - return empty arrays
    return NextResponse.json({
      thresholds: [],
      memory: [],
      coherence: []
    });
  }
}
