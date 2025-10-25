/**
 * Event Normalization Layer
 *
 * Maps backend event types (both old and new) to canonical frontend format.
 * Enables graceful backend evolution without breaking frontend.
 *
 * Strategy:
 * - Accept both old event types (tick.update, frame.start) and new (tick_frame_v1, node.flip)
 * - Map to canonical types that frontend components expect
 * - Warn on unknown event types (catches schema drift)
 * - Remove old mappings once backend fully migrated
 *
 * Author: Iris "The Aperture"
 * Context: Part B of dynamic graph rescue plan (backend emitter evolution)
 * Date: 2025-10-25
 */

export function normalizeEvent(e: any): any {
  if (!e || !e.type) {
    console.warn('[normalizeEvent] Event missing type:', e);
    return e;
  }

  switch (e.type) {
    // Timebase events - canonical: tick_frame_v1
    case 'tick_frame_v1':
      return e; // Already canonical

    case 'frame.end':
      return e; // Keep as-is

    case 'tick.update':
      // Legacy event - map to frame.end temporarily
      return {
        type: 'frame.end',
        frame_id: e.frame_id ?? e.frame,
        timestamp: e.timestamp
      };

    case 'frame.start':
      return e; // Keep as-is

    // Node energy changes - canonical: node.flip
    case 'node.flip':
      return {
        type: 'node.flip',
        node_id: e.id ?? e.node_id,
        E_pre: e.E_pre,
        E_post: e.E_post ?? e.energy_post ?? e.energy,
        theta: e.theta ?? e.threshold,
        frame_id: e.frame_id,
        direction: (e.E_post ?? e.energy_post ?? e.energy ?? 0) > (e.theta ?? e.threshold ?? 0) ? 'on' : 'off',
        timestamp: e.timestamp ?? new Date().toISOString()
      };

    // Working memory - canonical: wm.emit
    case 'wm.emit':
      return {
        type: 'wm.emit',
        frame_id: e.frame_id,
        node_ids: e.selected_entities?.map((se: any) => se.id ?? se) ?? e.node_ids ?? [],
        timestamp: e.timestamp ?? new Date().toISOString()
      };

    // Link flows - canonical: link.flow.summary
    case 'link.flow.summary':
      return e; // Already canonical

    // Phenomenology events (P2.1.1, P2.1.4)
    case 'phenomenological_health':
    case 'health.phenomenological': // Alternative naming
      return { ...e, type: 'phenomenological_health' }; // Canonical

    case 'phenomenology.mismatch':
      return e; // Already canonical

    // Learning events (P2.1.2, P2.1.3, P2.1.4)
    case 'weights.updated.trace':
    case 'tier.link.strengthened':
      return e; // Already canonical

    // Stride events
    case 'stride.exec':
    case 'stride.selection':
      return e; // Already canonical

    // All other events pass through unchanged
    case 'node.emotion.update':
    case 'link.emotion.update':
    case 'criticality.state':
    case 'decay.tick':
      return e;

    default:
      // Unknown event type - log warning but don't drop
      console.warn('[normalizeEvent] Unknown event type:', e.type, e);
      return e;
  }
}
