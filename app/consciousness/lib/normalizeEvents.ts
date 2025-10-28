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
      // Removed verbose logging - these events fire every frame (multiple/sec)
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
    case 'node.flip': {
      const normalized = {
        type: 'node.flip',
        node_id: e.node ?? e.id ?? e.node_id,  // Backend uses "node" field
        E_pre: e.E_pre,
        E_post: e.E_post ?? e.energy_post ?? e.energy,
        theta: e.Θ ?? e.theta ?? e.threshold,  // Backend uses Greek "Θ"
        frame_id: e.frame_id,
        direction: (e.E_post ?? e.energy_post ?? e.energy ?? 0) > (e.Θ ?? e.theta ?? e.threshold ?? 0) ? 'on' : 'off',
        timestamp: e.timestamp ?? new Date().toISOString()
      };
      console.log(`[normalizeEvent] ✅ node.flip: ${normalized.node_id} ${normalized.direction} (E: ${normalized.E_pre.toFixed(2)} → ${normalized.E_post.toFixed(2)})`);
      return normalized;
    }

    // Working memory - canonical: wm.emit
    case 'wm.emit':
      return e; // Preserve rich payload (mode, shares, anchors)

    case 'wm.selected':
      return e;

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

    case 'weights.updated':
      return e;

    case 'subentity.weights.updated':
    case 'subentity.membership.pruned':
      return e;

    // Stride events
    case 'stride.exec':
    case 'stride.selection':
      return e; // Already canonical

    // Subentity activation snapshot (active subentities panel)
    case 'subentity.snapshot':
      return e; // Already canonical

    // Legacy V1 events (pass through)
    case 'consciousness_state':
    case 'subentity_activity':
    case 'threshold_crossing':
      return e;

    // All other events pass through unchanged
    case 'node.emotion.update':
    case 'link.emotion.update':
    case 'criticality.state':
    case 'decay.tick':
    case 'se.boundary.summary':
    case 'entity.multiplicity_assessment':
    case 'entity.productive_multiplicity':
    case 'percept.frame':
    case 'membrane.inject.ack':
      return e;

    case 'forged.identity.frame':
    case 'forged.identity.metrics':
      return e;

    default:
      // Unknown event type - log warning but don't drop
      console.warn('[normalizeEvent] Unknown event type:', e.type, e);
      return e;
  }
}
