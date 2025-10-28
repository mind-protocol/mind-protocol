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
    // Parse FormData from browser
    const formData = await request.formData();
    const file = formData.get('file');

    // Validate file provided
    if (!file || !(file instanceof File)) {
      return NextResponse.json(
        { error: 'file is required (must be Blob/File in FormData)' },
        { status: 400 }
      );
    }

    // Save screenshot to evidence directory
    const fs = require('fs').promises;
    const path = require('path');
    const timestamp = Date.now();
    const filename = `screenshot-${timestamp}.png`;
    const evidenceDir = path.join(process.cwd(), 'data', 'evidence');
    const filepath = path.join(evidenceDir, filename);

    // Ensure evidence directory exists
    await fs.mkdir(evidenceDir, { recursive: true });

    // Write file to disk
    const buffer = Buffer.from(await file.arrayBuffer());
    await fs.writeFile(filepath, buffer);

    // Forward to signals collector with filepath
    const response = await fetch(`${SIGNALS_COLLECTOR_URL}/screenshot`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        screenshot_path: filepath,
        context: formData.get('context') || 'periodic_capture',
        timestamp_ms: timestamp,
      }),
    });

    if (!response.ok) {
      throw new Error(`Signals collector returned ${response.status}`);
    }

    const result = await response.json();

    return NextResponse.json(
      {
        ...result,
        screenshot_path: filepath
      },
      { status: 200 }
    );

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
