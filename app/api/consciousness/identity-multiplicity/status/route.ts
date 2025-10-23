/**
 * Identity Multiplicity Status API
 *
 * Returns identity multiplicity detection status for PR-D mechanism:
 * - Multiplicity detection per entity
 * - Task progress rates
 * - Energy efficiency metrics
 * - Identity flip events
 *
 * PR-D: Identity Multiplicity Detection
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 */

import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Proxy request to Python backend
    const res = await fetch('http://localhost:8000/api/identity-multiplicity/status', {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      // Backend not ready yet - return empty arrays
      return NextResponse.json({
        statuses: [],
        recent_flips: []
      });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    // Backend not running - return empty arrays
    return NextResponse.json({
      statuses: [],
      recent_flips: []
    });
  }
}
