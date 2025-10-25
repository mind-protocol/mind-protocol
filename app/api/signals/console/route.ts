import { NextRequest, NextResponse } from 'next/server';

/**
 * Console Error Signal Proxy
 * 
 * Forwards console errors from dashboard to signals_collector service.
 * This allows frontend to report errors without CORS issues.
 * 
 * Created: 2025-10-25 by Atlas (Infrastructure Engineer)
 * Spec: Phase-A Autonomy - P3.1 Signals Collector MVP
 */

const SIGNALS_COLLECTOR_URL = process.env.SIGNALS_COLLECTOR_URL || 'http://localhost:8010';

export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body = await request.json();

    // Forward to signals collector
    const response = await fetch(`${SIGNALS_COLLECTOR_URL}/console`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        error_message: body.error_message,
        stack_trace: body.stack_trace,
        url: body.url || request.headers.get('referer'),
        user_agent: request.headers.get('user-agent'),
        timestamp_ms: Date.now(),
      }),
    });

    if (!response.ok) {
      throw new Error(`Signals collector returned ${response.status}`);
    }

    const result = await response.json();

    return NextResponse.json(result, { status: 200 });

  } catch (error) {
    console.error('[SignalsAPI] Console error forwarding failed:', error);
    
    // Return success even if forwarding fails (don't break dashboard)
    return NextResponse.json(
      { 
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 200 } // Still 200 to avoid dashboard error loops
    );
  }
}
