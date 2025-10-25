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

    // TODO: Forward high-severity errors to backend stimulus injection
    // This would analyze error patterns and inject debugging/recovery stimuli
    // Example: Critical React errors → stimulus to "debugging_protocol" entity
    if (signal.type === 'error' && shouldTriggerStimulus(signal)) {
      // await fetch('http://localhost:8001/stimulus/inject', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     query: `frontend error: ${signal.message}`,
      //     budget: 10.0,
      //     source: 'browser_console_error'
      //   })
      // });
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
 * Determine if console error should trigger stimulus injection
 *
 * Filters noise (warnings, React devtools) from critical errors
 * that merit consciousness attention.
 */
function shouldTriggerStimulus(signal: ConsoleSignal): boolean {
  // High-severity patterns
  const criticalPatterns = [
    /unhandled promise rejection/i,
    /uncaught exception/i,
    /failed to fetch/i,
    /network error/i,
    /websocket/i
  ];

  // Low-severity noise to ignore
  const ignorePatterns = [
    /react devtools/i,
    /download the react devtools/i,
    /source map/i
  ];

  const msg = signal.message.toLowerCase();

  // Ignore noise
  if (ignorePatterns.some(pattern => pattern.test(msg))) {
    return false;
  }

  // Trigger on critical patterns
  if (criticalPatterns.some(pattern => pattern.test(msg))) {
    return true;
  }

  // Default: don't trigger for warnings/logs, only errors
  return signal.type === 'error';
}
