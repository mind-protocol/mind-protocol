/**
 * Console Signals Proxy - Browser Console Error Collection
 *
 * Collects browser console errors/logs and forwards them to the backend
 * signals collector for potential stimulus injection based on error patterns.
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

interface ConsoleSignal {
  type: 'error' | 'warn' | 'log' | 'info';
  message: string;
  stack?: string;
  timestamp: string;
  url: string;
  line?: number;
  column?: number;
}

export async function POST(request: Request) {
  try {
    const signal: ConsoleSignal = await request.json();

    // Validate signal
    if (!signal.type || !signal.message) {
      return NextResponse.json(
        { error: 'Invalid signal format - missing type or message' },
        { status: 400 }
      );
    }

    // Ensure log directory exists
    const logDir = path.join(process.cwd(), 'claude-logs');
    await fs.mkdir(logDir, { recursive: true });

    // Append to browser console log
    const logPath = path.join(logDir, 'browser-console.log');
    const logEntry = JSON.stringify({
      ...signal,
      timestamp: signal.timestamp || new Date().toISOString()
    }) + '\n';

    await fs.appendFile(logPath, logEntry);

    // Forward to signals collector backend (port 8010)
    // Signals collector will deduplicate, rate limit, and forward to stimulus injection
    try {
      const collectorUrl = process.env.SIGNALS_COLLECTOR_URL || 'http://localhost:8010';
      const response = await fetch(`${collectorUrl}/ingest/console`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          severity: signal.type === 'error' ? 'error' : signal.type === 'warn' ? 'warning' : 'info',
          message: signal.message,
          stack_trace: signal.stack,
          source: 'browser_console',
          metadata: {
            url: signal.url,
            line: signal.line,
            column: signal.column,
            timestamp: signal.timestamp
          }
        })
      });

      if (!response.ok) {
        console.warn('[Console Proxy] Signals collector returned error:', response.status);
      }
    } catch (error) {
      // Non-fatal - local logging succeeded even if forwarding failed
      console.warn('[Console Proxy] Failed to forward to signals collector:', error);
    }

    return NextResponse.json({
      success: true,
      logged: true
    });

  } catch (error) {
    console.error('[Console Proxy] Error processing signal:', error);
    return NextResponse.json(
      { error: 'Failed to process console signal' },
      { status: 500 }
    );
  }
}

/**
 * Note: Signal filtering and stimulus triggering now handled by signals_collector backend.
 * The collector service (port 8010) implements deduplication, rate limiting, and
 * pattern-based routing to appropriate consciousness entities via orchestrator templates.
 */
