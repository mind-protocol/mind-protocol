/**
 * Affective Telemetry Metrics API
 *
 * Returns current telemetry metrics for affective coupling mechanisms.
 *
 * PR-A: Instrumentation Foundation
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 */

import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Proxy request to Python backend
    const res = await fetch('http://localhost:8000/api/affective-telemetry/metrics', {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      // Backend not ready yet - return default values
      return NextResponse.json({
        metrics: {
          sampleRate: 1.0,
          bufferUtilization: 0,
          bufferSize: 1000,
          totalEventsEmitted: 0,
          totalEventsSampled: 0
        },
        eventCounts: {}
      });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    // Backend not running - return default values
    return NextResponse.json({
      metrics: {
        sampleRate: 1.0,
        bufferUtilization: 0,
        bufferSize: 1000,
        totalEventsEmitted: 0,
        totalEventsSampled: 0
      },
      eventCounts: {}
    });
  }
}
