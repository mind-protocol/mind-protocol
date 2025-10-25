/**
 * WebSocket Transport Diagnostics
 *
 * Minimal event counter to prove browser receives frame ticks.
 * Exposes window.__diag for devtools inspection.
 *
 * Author: Iris "The Aperture"
 * Purpose: 15-minute dynamic rescue - Step A (transport sanity)
 */

let lastFrame = 0;
let frames = 0;

export function diagOnEvent(e: any) {
  if (e?.type === "tick_frame_v1" || e?.type === "frame.end" || e?.type === "frame.start") {
    frames++;
    lastFrame = e.frame_id ?? e.frame ?? lastFrame + 1;
    (window as any).__diag = { frames, lastFrame, t: Date.now() };
  }
}
