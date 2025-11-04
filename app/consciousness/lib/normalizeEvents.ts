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
  if (!e) {
    console.warn('[normalizeEvent] Null event received');
    return e;
  }

  // MIGRATION LAYER: Handle legacy "topic" field → "type"
  // Backend is transitioning from "topic" to normative "type" field
  if (!e.type && e.topic) {
    e.type = e.topic;
    console.log(`[normalizeEvent] Migrated legacy field: topic="${e.topic}" → type="${e.type}"`);
  }

  if (!e.type) {
    console.warn('[normalizeEvent] Event missing both type and topic:', e);
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
      // Handle two backend formats:
      // Format 1: {nodes: [{id, E, dE}]} - batch format
      // Format 2: {node, E_pre, E_post, Θ} - single flip format

      // Format 1: Batch format with nodes array (skip - too verbose for console)
      if (e.nodes && Array.isArray(e.nodes)) {
        return e; // Keep as-is, processed elsewhere
      }

      // Format 2: Single flip format
      const E_pre = e.E_pre ?? 0;  // Fallback to 0 if missing
      const E_post = e.E_post ?? e.energy_post ?? e.energy ?? 0;
      const theta = e.Θ ?? e.theta ?? e.threshold ?? 0;

      const normalized = {
        type: 'node.flip',
        node_id: e.node ?? e.id ?? e.node_id,  // Backend uses "node" field
        E_pre,
        E_post,
        theta,
        frame_id: e.frame_id,
        direction: E_post > theta ? 'on' : 'off',
        timestamp: e.timestamp ?? new Date().toISOString()
      };

      console.log(`[normalizeEvent] ✅ node.flip: ${normalized.node_id} ${normalized.direction} (E: ${E_pre.toFixed(2)} → ${E_post.toFixed(2)})`);
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

    // SubEntity activation events (normative format)
    case 'subentity.activation':
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

    // Stimulus injection debugging
    case 'stimulus.injection.debug':
      return e; // Diagnostic event

    // Emergence events (normative emergence.v1 spec)
    case 'emergence.gap.detected':
    case 'gap.detected':  // Backend variant (naming inconsistency)
    case 'emergence.coalition.formed':
    case 'emergence.coalition.assembled':  // Backend variant (naming inconsistency)
    case 'emergence.validation.passed':
    case 'emergence.validation.failed':
    case 'emergence.spawn.completed':
    case 'emergence.spawn':  // Backend variant (naming inconsistency)
    case 'emergence.reject':
    case 'emergence.redirect':
      return e; // Already canonical normative format

    // Mode detection events (mode.v1 spec)
    case 'mode.snapshot':
    case 'mode.metastable_pattern':
    case 'mode.community.detected':
      return e; // Already canonical

    // Topology events (topology.v1 spec)
    case 'rich_club.snapshot':
    case 'rich_club.hub_at_risk':
    case 'integration_metrics.node':
    case 'integration_metrics.population':
    case 'state_modulation.frame':
      return e; // Already canonical

    // Graph delta events (graph.delta.v1 spec)
    case 'graph.delta.node.upsert':
    case 'graph.delta.node.delete': {
      const payload = (e as any).payload ?? {};
      const node = payload.node ?? (e as any).node ?? {};
      const nodeId =
        node?.id ??
        payload.node_id ??
        (e as any).node_id ??
        (e as any).id ??
        payload.id;

      const mergedNode = nodeId
        ? {
            ...node,
            id: nodeId,
            type: node?.type ?? payload.node_type ?? (e as any).node_type,
            properties: node?.properties ?? payload.properties ?? (e as any).properties ?? undefined
          }
        : undefined;

      return {
        ...e,
        ...payload,
        node_id: nodeId,
        node: mergedNode
      };
    }
    case 'graph.delta.link.upsert':
    case 'graph.delta.link.delete': {
      const payload = (e as any).payload ?? {};
      const link = payload.link ?? (e as any).link ?? {};

      const source =
        link.source ??
        payload.source ??
        payload.source_id ??
        (e as any).source ??
        (e as any).source_id;
      const target =
        link.target ??
        payload.target ??
        payload.target_id ??
        (e as any).target ??
        (e as any).target_id;
      const linkType =
        link.type ??
        payload.link_type ??
        payload.type ??
        (e as any).link_type ??
        (e as any).type;
      const linkId =
        link.id ??
        payload.link_id ??
        (e as any).link_id ??
        (e as any).id ??
        (source && target ? `${source}->${target}:${linkType ?? 'link'}` : undefined);

      const weight =
        link.weight ??
        payload.weight ??
        payload.metadata?.weight ??
        (e as any).weight ??
        (e as any).metadata?.weight;

      const mergedLink = linkId
        ? {
            ...link,
            id: linkId,
            source,
            target,
            type: linkType,
            weight,
            metadata: {
              ...(link.metadata ?? {}),
              ...(payload.metadata ?? {}),
              ...((e as any).metadata ?? {})
            }
          }
        : undefined;

      return {
        ...e,
        ...payload,
        link_id: linkId,
        link: mergedLink
      };
    }
    case 'graph.delta.subentity.upsert':
    case 'graph.delta.subentity.delete': {
      const payload = (e as any).payload ?? {};
      const subentity = payload.subentity ?? (e as any).subentity ?? {};
      const subentityId =
        subentity.id ??
        payload.subentity_id ??
        (e as any).subentity_id ??
        (e as any).id ??
        payload.id;

      const mergedSubentity = subentityId
        ? {
            ...subentity,
            id: subentityId,
            kind: subentity.kind ?? payload.subentity_type ?? (e as any).subentity_type,
            properties: subentity.properties ?? payload.properties ?? (e as any).properties ?? undefined
          }
        : undefined;

      return {
        ...e,
        ...payload,
        subentity_id: subentityId,
        subentity: mergedSubentity
      };
    }

    // Control messages - pass through without normalization
    case 'subscribe.ack@1.0':
    case 'snapshot.begin@1.0':
    case 'snapshot.chunk@1.0':
    case 'snapshot.end@1.0':
      return e;

    // WebSocket keepalive - pass through silently
    case 'ping':
    case 'pong':
      return e;

    default:
      // Unknown event type - log warning but don't drop
      console.warn('[normalizeEvent] Unknown event type:', e.type, e);
      return e;
  }
}
