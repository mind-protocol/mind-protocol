import { NextRequest, NextResponse } from 'next/server';

/**
 * Screenshot Signal Proxy
 * 
 * Forwards screenshot evidence to signals_collector service.
 * Allows frontend to report screenshot captures for autonomy processing.
 * 
 * Created: 2025-10-25 by Atlas (Infrastructure Engineer)
 * Spec: Phase-A Autonomy - P3.1 Signals Collector MVP
 */

const SIGNALS_COLLECTOR_URL = process.env.SIGNALS_COLLECTOR_URL || 'http://localhost:8010';

export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body = await request.json();

    // Validate screenshot_path provided
    if (!body.screenshot_path) {
      return NextResponse.json(
        { error: 'screenshot_path is required' },
        { status: 400 }
      );
    }

    // Forward to signals collector
    const response = await fetch(`${SIGNALS_COLLECTOR_URL}/screenshot`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        screenshot_path: body.screenshot_path,
        context: body.context,
        timestamp_ms: Date.now(),
      }),
    });

    if (!response.ok) {
      throw new Error(`Signals collector returned ${response.status}`);
    }

    const result = await response.json();

    return NextResponse.json(result, { status: 200 });

  } catch (error) {
    console.error('[SignalsAPI] Screenshot forwarding failed:', error);
    
    return NextResponse.json(
      { 
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
