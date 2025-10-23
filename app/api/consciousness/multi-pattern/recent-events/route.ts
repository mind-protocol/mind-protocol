/**
 * Multi-Pattern Response Recent Events API
 *
 * Returns pattern effectiveness events for PR-C mechanism:
 * - Regulation/rumination/distraction pattern weights
 * - Rumination cap warnings
 * - Pattern effectiveness metrics
 *
 * PR-C: Multi-Pattern Response
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 */

import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Proxy request to Python backend
    const res = await fetch('http://localhost:8000/api/multi-pattern/recent-events', {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      // Backend not ready yet - return empty arrays
      return NextResponse.json({
        patterns: [],
        rumination_caps: []
      });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    // Backend not running - return empty arrays
    return NextResponse.json({
      patterns: [],
      rumination_caps: []
    });
  }
}
