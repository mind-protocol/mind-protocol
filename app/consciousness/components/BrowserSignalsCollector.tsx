/**
 * Browser Signals Collector - Autonomous Observability Infrastructure
 *
 * Captures browser console errors and screenshots, forwarding them to backend
 * for autonomous debugging. Enables Iris to see what Nicolas sees without
 * requiring explicit bug reports.
 *
 * Architecture:
 * - Global error handlers (window.onerror, unhandledrejection)
 * - Periodic screenshots (every 30s)
 * - Error-triggered screenshots (on exceptions)
 * - Rate limiting (max 1 screenshot per 10s)
 * - POST to /api/signals/console and /api/signals/screenshot
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: P3 Signals Bridge - Foundational for autonomous debugging
 */

'use client';

import { useEffect, useRef } from 'react';

interface ConsoleSignal {
  type: 'error' | 'warn' | 'log' | 'info';
  message: string;
  stack?: string;
  timestamp: string;
  url: string;
  line?: number;
  column?: number;
}

interface ScreenshotSignal {
  imageData: string;
  timestamp: string;
  trigger: 'error' | 'periodic' | 'manual';
  errorContext?: {
    type: string;
    message: string;
  };
}

export function BrowserSignalsCollector() {
  const lastScreenshotTime = useRef<number>(0);
  const screenshotIntervalId = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    console.log('[BrowserSignalsCollector] Initializing autonomous observability...');

    // Global error handler
    const handleError = async (event: ErrorEvent) => {
      const signal: ConsoleSignal = {
        type: 'error',
        message: event.message,
        stack: event.error?.stack,
        timestamp: new Date().toISOString(),
        url: event.filename || window.location.href,
        line: event.lineno,
        column: event.colno
      };

      await sendConsoleSignal(signal);

      // Capture screenshot on error (rate limited)
      await captureScreenshot('error', {
        type: 'error',
        message: event.message
      });
    };

    // Unhandled promise rejection handler
    const handleUnhandledRejection = async (event: PromiseRejectionEvent) => {
      const signal: ConsoleSignal = {
        type: 'error',
        message: `Unhandled Promise Rejection: ${event.reason}`,
        stack: event.reason?.stack,
        timestamp: new Date().toISOString(),
        url: window.location.href
      };

      await sendConsoleSignal(signal);

      // Capture screenshot on rejection (rate limited)
      await captureScreenshot('error', {
        type: 'error',
        message: signal.message
      });
    };

    // Console error interceptor
    const originalConsoleError = console.error;
    console.error = async (...args: any[]) => {
      // Call original console.error
      originalConsoleError.apply(console, args);

      // Send to backend
      const signal: ConsoleSignal = {
        type: 'error',
        message: args.map(arg =>
          typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
        ).join(' '),
        timestamp: new Date().toISOString(),
        url: window.location.href
      };

      await sendConsoleSignal(signal);
    };

    // Register handlers
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    // Periodic screenshots (every 30 seconds)
    screenshotIntervalId.current = setInterval(() => {
      captureScreenshot('periodic');
    }, 30000);

    // Initial screenshot
    setTimeout(() => captureScreenshot('periodic'), 2000);

    console.log('[BrowserSignalsCollector] ✓ Autonomous observability active');

    // Cleanup
    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      console.error = originalConsoleError;

      if (screenshotIntervalId.current) {
        clearInterval(screenshotIntervalId.current);
      }
    };
  }, []);

  /**
   * Send console signal to backend
   */
  async function sendConsoleSignal(signal: ConsoleSignal): Promise<void> {
    try {
      await fetch('/api/signals/console', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signal)
      });
    } catch (err) {
      // Don't let signal collection errors break the app
      console.warn('[BrowserSignalsCollector] Failed to send console signal:', err);
    }
  }

  /**
   * Capture screenshot and send to backend
   *
   * Rate limited: max 1 screenshot per 10 seconds to avoid spam
   */
  async function captureScreenshot(
    trigger: 'error' | 'periodic' | 'manual',
    errorContext?: { type: string; message: string }
  ): Promise<void> {
    const now = Date.now();

    // Rate limiting: max 1 screenshot per 10 seconds
    if (now - lastScreenshotTime.current < 10000) {
      return;
    }

    try {
      // Use html2canvas for screenshot capture
      // Dynamic import to avoid SSR issues
      const html2canvas = (await import('html2canvas')).default;

      const canvas = await html2canvas(document.body, {
        logging: false,
        useCORS: true,
        allowTaint: true,
        width: window.innerWidth,
        height: window.innerHeight
      });

      // Convert canvas to Blob
      const blob = await new Promise<Blob | null>(resolve =>
        canvas.toBlob(resolve, 'image/png', 0.9)
      );

      if (!blob) {
        throw new Error('toBlob() failed');
      }

      // Create FormData with File object (required by backend multipart handler)
      const formData = new FormData();
      formData.set('file', new File([blob], `screenshot_${Date.now()}.png`, {
        type: 'image/png'
      }));

      // Add metadata as separate fields
      formData.set('timestamp', new Date().toISOString());
      formData.set('trigger', trigger);
      if (errorContext) {
        formData.set('errorContext', JSON.stringify(errorContext));
      }

      const response = await fetch('/api/signals/screenshot', {
        method: 'POST',
        body: formData // No Content-Type header - browser sets multipart/form-data automatically
      });

      if (!response.ok) {
        const text = await response.text();
        console.warn('[BrowserSignalsCollector] Screenshot upload failed', response.status, text);
        return;
      }

      lastScreenshotTime.current = now;

      console.log(`[BrowserSignalsCollector] Screenshot captured (${trigger})`);

    } catch (err) {
      // Don't let screenshot errors break the app
      console.warn('[BrowserSignalsCollector] Failed to capture screenshot:', err);
    }
  }

  // This component doesn't render anything - pure side effects
  return null;
}
