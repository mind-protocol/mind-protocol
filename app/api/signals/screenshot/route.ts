/**
 * Screenshot Signals Proxy - Browser Visual State Collection
 *
 * Collects browser screenshots and stores them with metadata for debugging
 * and visual state tracking. Enables autonomous debugging by providing
 * visual context for console errors and state transitions.
 *
 * Part of P3 Signals Bridge - browser observability to consciousness substrate.
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: P3 (Signals → Stimuli Bridge)
 */

import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

interface ScreenshotSignal {
  imageData: string;  // Base64 data URL
  timestamp: string;
  trigger: 'error' | 'periodic' | 'manual';
  errorContext?: {
    type: string;
    message: string;
  };
}

export async function POST(request: Request) {
  try {
    const signal: ScreenshotSignal = await request.json();

    // Validate signal
    if (!signal.imageData || !signal.timestamp) {
      return NextResponse.json(
        { error: 'Invalid signal format - missing imageData or timestamp' },
        { status: 400 }
      );
    }

    // Ensure screenshot directory exists
    const screenshotDir = path.join(process.cwd(), 'claude-screenshots');
    await fs.mkdir(screenshotDir, { recursive: true });

    // Parse base64 data URL
    const matches = signal.imageData.match(/^data:image\/(\w+);base64,(.+)$/);
    if (!matches) {
      return NextResponse.json(
        { error: 'Invalid image data format' },
        { status: 400 }
      );
    }

    const [, format, base64Data] = matches;
    const buffer = Buffer.from(base64Data, 'base64');

    // Generate filename from timestamp
    const timestamp = new Date(signal.timestamp).getTime();
    const filename = `screenshot-${timestamp}.${format}`;
    const filepath = path.join(screenshotDir, filename);

    // Save screenshot
    await fs.writeFile(filepath, buffer);

    // Save metadata to screenshots log
    const logDir = path.join(process.cwd(), 'claude-logs');
    await fs.mkdir(logDir, { recursive: true });

    const logPath = path.join(logDir, 'screenshots.log');
    const metadataEntry = JSON.stringify({
      filepath,
      timestamp: signal.timestamp,
      trigger: signal.trigger,
      errorContext: signal.errorContext || null
    }) + '\n';

    await fs.appendFile(logPath, metadataEntry);

    // Forward to signals collector backend (port 8010)
    // Screenshots provide visual context for autonomous debugging
    // Note: signals_collector expects multipart/form-data file upload, not JSON
    try {
      const collectorUrl = process.env.SIGNALS_COLLECTOR_URL || 'http://localhost:8010';

      // Create form data with the screenshot file
      const formData = new FormData();
      const blob = new Blob([buffer], { type: `image/${format}` });
      formData.append('file', blob, filename);

      const response = await fetch(`${collectorUrl}/ingest/screenshot`, {
        method: 'POST',
        body: formData  // No Content-Type header - browser sets it with boundary
      });

      if (!response.ok) {
        console.warn('[Screenshot Proxy] Signals collector returned error:', response.status);
      }
    } catch (error) {
      // Non-fatal - local storage succeeded even if forwarding failed
      console.warn('[Screenshot Proxy] Failed to forward to signals collector:', error);
    }

    return NextResponse.json({
      success: true,
      filepath,
      filename
    });

  } catch (error) {
    console.error('[Screenshot Proxy] Error processing signal:', error);
    return NextResponse.json(
      { error: 'Failed to process screenshot signal' },
      { status: 500 }
    );
  }
}

/**
 * GET endpoint to retrieve screenshot by timestamp
 *
 * Allows querying screenshots closest to a specific error timestamp
 * for autonomous debugging workflows.
 */
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const timestamp = searchParams.get('timestamp');

    if (!timestamp) {
      return NextResponse.json(
        { error: 'Missing timestamp parameter' },
        { status: 400 }
      );
    }

    const targetTime = new Date(timestamp).getTime();

    // Read screenshots log to find closest screenshot
    const logPath = path.join(process.cwd(), 'claude-logs', 'screenshots.log');

    try {
      const logContent = await fs.readFile(logPath, 'utf-8');
      const entries = logContent
        .trim()
        .split('\n')
        .filter(line => line.length > 0)
        .map(line => JSON.parse(line));

      // Find screenshot closest to target time (before or at target)
      let closest = null;
      let minDiff = Infinity;

      for (const entry of entries) {
        const entryTime = new Date(entry.timestamp).getTime();
        const diff = targetTime - entryTime;

        // Only consider screenshots at or before target time
        if (diff >= 0 && diff < minDiff) {
          minDiff = diff;
          closest = entry;
        }
      }

      if (closest) {
        return NextResponse.json({
          success: true,
          screenshot: closest,
          timeDiff: minDiff
        });
      } else {
        return NextResponse.json(
          { error: 'No screenshot found before target timestamp' },
          { status: 404 }
        );
      }

    } catch (err) {
      // Log file doesn't exist or is empty
      return NextResponse.json(
        { error: 'No screenshots available' },
        { status: 404 }
      );
    }

  } catch (error) {
    console.error('[Screenshot Proxy] Error retrieving screenshot:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve screenshot' },
      { status: 500 }
    );
  }
}
