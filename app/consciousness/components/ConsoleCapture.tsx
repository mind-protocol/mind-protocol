/**
 * ConsoleCapture - Browser console log + screenshot capture for Claude Code
 *
 * Intercepts console.log/error/warn from Nicolas's actual Chrome tab
 * and sends to Python backend for Claude Code to read.
 *
 * Also captures screenshots every 30 seconds + on errors for visual debugging.
 *
 * Architecture:
 * - Overrides console methods (preserves original output)
 * - Batches logs with 500ms debounce
 * - Sends to http://localhost:8000/api/logs
 * - Captures DOM screenshots with html2canvas every 30s
 * - Sends screenshots to http://localhost:8000/api/screenshot
 * - Captures unhandled exceptions + screenshot on error
 * - Only active in development mode
 *
 * Purpose: Synchronize awareness between human browser and AI consciousness
 *
 * Designer: Iris "The Aperture"
 * Date: 2025-10-21
 */

'use client';

import { useEffect } from 'react';

export function ConsoleCapture() {
  useEffect(() => {
    // Only capture in development
    if (process.env.NODE_ENV !== 'development') return;

    const buffer: any[] = [];
    let flushTimeout: NodeJS.Timeout;
    let lastScreenshotTime = 0;
    const MIN_SCREENSHOT_INTERVAL = 10000; // 10 seconds between error screenshots

    // Store original console methods
    const originalConsole = {
      log: console.log,
      error: console.error,
      warn: console.warn,
      info: console.info,
    };

    const captureLog = (type: string, args: any[]) => {
      // Still show in browser console (preserve developer experience)
      originalConsole[type as keyof typeof originalConsole](...args);

      // Serialize arguments for transmission
      const serialized = args.map(arg => {
        if (arg instanceof Error) {
          return {
            message: arg.message,
            stack: arg.stack,
            name: arg.name,
          };
        }
        if (typeof arg === 'object') {
          try {
            return JSON.stringify(arg, null, 2);
          } catch (e) {
            return '[Circular or non-serializable object]';
          }
        }
        return String(arg);
      });

      // Add to buffer
      buffer.push({
        timestamp: Date.now(),
        type,
        message: serialized.join(' '),
      });

      // Debounced flush (avoid flooding)
      clearTimeout(flushTimeout);
      flushTimeout = setTimeout(flushLogs, 500);
    };

    const flushLogs = async () => {
      if (buffer.length === 0) return;

      const logs = [...buffer];
      buffer.length = 0;

      try {
        const response = await fetch('http://localhost:8000/api/logs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ logs }),
        });

        if (!response.ok) {
          originalConsole.error('[ConsoleCapture] Failed to send logs:', response.statusText);
        }
      } catch (err) {
        // Don't break the app if logging fails
        // (Could happen if backend is down)
        originalConsole.error('[ConsoleCapture] Network error sending logs:', err);
      }
    };

    // Screenshot capture using native Screen Capture API
    let screenStream: MediaStream | null = null;
    let videoElement: HTMLVideoElement | null = null;

    const initializeScreenCapture = async () => {
      try {
        // Request screen capture permission (shows browser popup)
        screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: true
        });

        // Create video element to capture frames
        videoElement = document.createElement('video');
        videoElement.srcObject = screenStream;
        videoElement.play();

        originalConsole.log('[ConsoleCapture] Screen capture initialized - will auto-capture every 30s');
      } catch (err) {
        originalConsole.error('[ConsoleCapture] Screen capture permission denied or failed:', err);
        // Fallback: user needs to manually grant permission
      }
    };

    const captureScreenshot = async (force = false) => {
      // Rate limit: Only capture if enough time has passed since last screenshot
      const now = Date.now();
      if (!force && (now - lastScreenshotTime) < MIN_SCREENSHOT_INTERVAL) {
        originalConsole.warn('[ConsoleCapture] Screenshot rate-limited (10s minimum interval)');
        return;
      }

      lastScreenshotTime = now;

      // Initialize screen capture if not already done
      if (!screenStream || !videoElement) {
        originalConsole.warn('[ConsoleCapture] Screen capture not initialized - call initializeScreenCapture() first');
        return;
      }

      try {
        // Capture current video frame to canvas
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.drawImage(videoElement, 0, 0);

        // Convert canvas to blob
        canvas.toBlob(async (blob) => {
          if (!blob) return;

          const formData = new FormData();
          formData.append('screenshot', blob, `screenshot-${Date.now()}.png`);
          formData.append('timestamp', Date.now().toString());
          formData.append('url', window.location.href);

          try {
            const response = await fetch('http://localhost:8000/api/screenshot', {
              method: 'POST',
              body: formData,
            });

            if (!response.ok) {
              originalConsole.error('[ConsoleCapture] Failed to send screenshot:', response.statusText);
            }
          } catch (err) {
            originalConsole.error('[ConsoleCapture] Network error sending screenshot:', err);
          }
        }, 'image/png');

      } catch (err) {
        originalConsole.error('[ConsoleCapture] Failed to capture screenshot:', err);
      }
    };

    // Override console methods
    console.log = (...args) => captureLog('log', args);
    console.error = (...args) => {
      captureLog('error', args);
      // Capture screenshot on error (rate-limited to prevent flood)
      captureScreenshot(false); // force=false, respect rate limit
    };
    console.warn = (...args) => captureLog('warn', args);
    console.info = (...args) => captureLog('info', args);

    // Initialize screen capture after 2 seconds (gives time for page to load)
    const initTimeout = setTimeout(async () => {
      await initializeScreenCapture();
      // Capture first screenshot after initialization
      setTimeout(() => captureScreenshot(true), 1000);
    }, 2000);

    // Capture screenshot every 30 seconds (force=true, bypass rate limit)
    const screenshotInterval = setInterval(() => captureScreenshot(true), 30000);

    // Capture unhandled errors
    const errorHandler = (event: ErrorEvent) => {
      buffer.push({
        timestamp: Date.now(),
        type: 'exception',
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        stack: event.error?.stack,
      });
      flushLogs();
      // Capture screenshot on exception (rate-limited)
      captureScreenshot(false);
    };

    window.addEventListener('error', errorHandler);

    // Capture unhandled promise rejections
    const rejectionHandler = (event: PromiseRejectionEvent) => {
      buffer.push({
        timestamp: Date.now(),
        type: 'unhandledRejection',
        message: event.reason?.message || String(event.reason),
        stack: event.reason?.stack,
      });
      flushLogs();
      // Capture screenshot on unhandled rejection (rate-limited)
      captureScreenshot(false);
    };

    window.addEventListener('unhandledrejection', rejectionHandler);

    // Cleanup on unmount
    return () => {
      // Restore original console
      console.log = originalConsole.log;
      console.error = originalConsole.error;
      console.warn = originalConsole.warn;
      console.info = originalConsole.info;

      // Remove event listeners
      window.removeEventListener('error', errorHandler);
      window.removeEventListener('unhandledrejection', rejectionHandler);

      // Clear timeouts and intervals
      clearTimeout(flushTimeout);
      clearTimeout(initTimeout);
      clearInterval(screenshotInterval);

      // Stop screen capture stream
      if (screenStream) {
        screenStream.getTracks().forEach(track => track.stop());
      }
      if (videoElement) {
        videoElement.srcObject = null;
      }

      // Flush any remaining logs
      if (buffer.length > 0) {
        flushLogs();
      }
    };
  }, []);

  return null; // This component renders nothing
}
