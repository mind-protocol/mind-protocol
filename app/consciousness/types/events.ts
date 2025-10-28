/**
 * Consciousness Event Types
 *
 * TypeScript type definitions for consciousness events emitted via WebSocket.
 * Events capture real-time state changes in consciousness substrate (nodes, links, entities).
 *
 * Usage:
 *   import type { ConsciousnessEvent, SubentityWeightsUpdatedV1 } from './types/events';
 *
 * Author: Atlas (Infrastructure Engineer)
 * Integration: MEMBER_OF_EDGE_PERSISTENCE_INTEGRATION.md Integration 5
 * Created: 2025-10-25
 */

// === Base Event Types ===

export type NodeFlipV1 = {
  topic: "node.flip";
  v: "1";
  ts_ms: number;
  level: "N1" | "N2" | "N3";
  citizen_id: string;
  frame_id?: number;
  run_id: string;
  mission_id?: string;
  stimulus_id?: string;
  dedupe_key: string;
  payload: {
    node_id: string;
    name?: string;
    E_new: number;
    E_prev?: number;
    delta?: number;
  };
};

export type LinkFlowSummaryV1 = {
  topic: "link.flow.summary";
  v: "1";
  ts_ms: number;
  level: "N1" | "N2" | "N3";
  citizen_id: string;
  frame_id?: number;
  run_id: string;
  dedupe_key: string;
  payload: {
    link_id: string;
    source_id: string;
    target_id: string;
    flow_magnitude: number;
  };
};

// === Subentity (Entity) Membership Events ===

export type SubentityWeightsUpdatedV1 = {
  topic: "subentity.weights.updated";
  v: "1";
  ts_ms: number;
  level: "N1" | "N2" | "N3";
  citizen_id: string;
  frame_id?: number;
  run_id: string;
  mission_id?: string;
  stimulus_id?: string;
  dedupe_key: string;
  payload: {
    subentity: {
      id: string;
      name?: string;
      cohesion_before?: number;
      cohesion_after?: number;
      stability_z?: number;
      formation_quality_q?: number;
    };
    stats: {
      num_updated: number;
      num_pruned: number;
      budget_method?: "sainte-lague" | "hamilton" | string;
      ema_alpha?: number;
    };
    memberships: Array<{
      node_id: string;
      weight_prev?: number;
      weight_new?: number;
      delta?: number;
      activation_ema?: number;
      activation_count_inc?: number;
      last_activated_ts?: number;
    }>;
  };
};

export type SubentityMembershipPrunedV1 = {
  topic: "subentity.membership.pruned";
  v: "1";
  ts_ms: number;
  level: "N1" | "N2" | "N3";
  citizen_id: string;
  frame_id?: number;
  run_id: string;
  dedupe_key: string;
  payload: {
    subentity_id: string;
    node_id: string;
    weight_prev: number;
    activation_ema_prev: number;
    reason: "below_learned_floor" | "stale_membership" | "entity_dissolved";
  };
};

export type SubentityLifecycleV1 = {
  topic: "subentity.lifecycle";
  v: "1";
  ts_ms: number;
  level: "N1" | "N2" | "N3";
  citizen_id: string;
  run_id: string;
  dedupe_key: string;
  payload: {
    subentity_id: string;
    prev_status: "candidate" | "provisional" | "mature";
    new_status: "candidate" | "provisional" | "mature" | "dissolved";
    evidence: {
      formation_quality_q?: number;
      stability_z?: number;
      membership_drift_q?: number;
    };
  };
};

// === Consciousness Event Union Type ===

/**
 * Union of all consciousness event types.
 *
 * Use this type for event handlers that process multiple event types:
 *
 * @example
 *   function handleEvent(event: ConsciousnessEvent) {
 *     switch (event.topic) {
 *       case "node.flip":
 *         // TypeScript narrows to NodeFlipV1
 *         console.log(event.payload.node_id);
 *         break;
 *       case "subentity.weights.updated":
 *         // TypeScript narrows to SubentityWeightsUpdatedV1
 *         console.log(event.payload.subentity.id);
 *         break;
 *     }
 *   }
 */
export type ConsciousnessEvent =
  | NodeFlipV1
  | LinkFlowSummaryV1
  | SubentityWeightsUpdatedV1
  | SubentityMembershipPrunedV1
  | SubentityLifecycleV1;

// === Helper Type Guards ===

export function isNodeFlip(event: ConsciousnessEvent): event is NodeFlipV1 {
  return event.topic === "node.flip";
}

export function isLinkFlow(event: ConsciousnessEvent): event is LinkFlowSummaryV1 {
  return event.topic === "link.flow.summary";
}

export function isWeightsUpdated(event: ConsciousnessEvent): event is SubentityWeightsUpdatedV1 {
  return event.topic === "subentity.weights.updated";
}

export function isMembershipPruned(event: ConsciousnessEvent): event is SubentityMembershipPrunedV1 {
  return event.topic === "subentity.membership.pruned";
}

export function isLifecycleEvent(event: ConsciousnessEvent): event is SubentityLifecycleV1 {
  return event.topic === "subentity.lifecycle";
}
