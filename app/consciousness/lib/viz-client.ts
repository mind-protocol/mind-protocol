/**
 * Mind Harbor Visualization Client
 *
 * Handles WebSocket streaming of consciousness graph state from engine.
 * Implements delta application, caching, ordering, and reconnection.
 *
 * Author: Iris "The Aperture" - Consciousness Observation Architect
 * Created: 2025-10-20
 */

// ============================================================================
// Type Definitions (matching wire protocol)
// ============================================================================

export interface VeniceLocation {
  type: 'campo' | 'canal' | 'bridge' | 'sottoportego' | 'lagoon';
  name: string;
  features: string[];
  connectivity: number;
  scale: 'small' | 'medium' | 'large' | 'grand';
  coordinates?: {
    venice_x: number;
    venice_y: number;
  };
}

export interface NodeDelta {
  id: string;
  entity_energies: Record<string, number>;
  total_energy: number;
  threshold: number;
  active: boolean;
  soft_activation: number;
  node_type?: string;
  venice_location?: VeniceLocation;
  pos?: [number, number];
  created_at?: number;
}

export interface LinkDelta {
  src: string;
  dst: string;
  type: string;
  weight: number;
  emotion: {
    valence: number;
    arousal: number;
  };
  yearning_strength: number;
  traversal_history?: {
    last_entity: string;
    last_tick: number;
    count_total: number;
    count_1m: number;
  };
  active: boolean;
  flow_rate: number;
}

export interface StateDelta {
  kind: 'state_delta.v1';
  tick_id: number;
  ts: string;
  dt_ms: number;
  coalesced_ticks: number;
  entity_filter: string | null;
  nodes?: NodeDelta[];
  nodes_removed?: string[];
  links?: LinkDelta[];
  links_removed?: [string, string][];
  metrics?: {
    rho: number;
    global_energy: number;
    active_nodes: number;
    active_links: number;
    active_entities: Record<string, { node_count: number; total_energy: number }>;
    budget: {
      nodes_sent: number;
      nodes_budget: number;
      links_sent: number;
      links_budget: number;
    };
  };
}

export interface TraversalEvent {
  event_id: string;
  subentity: string;
  type: 'traversal' | 'threshold_cross' | 'integration';

  // traversal fields
  from_node?: string;
  to_node?: string;
  link_type?: string;
  energy_transferred?: number;
  cost?: number;
  duration_ticks?: number;

  // threshold_cross fields
  node?: string;
  direction?: 'up' | 'down';
  old_energy?: number;
  new_energy?: number;
  threshold?: number;

  // integration fields
  entity_integrated?: string;
  at_node?: string;
  combined_energy?: number;
}

export interface TraversalEvents {
  kind: 'traversal_events.v1';
  tick_id: number;
  ts: string;
  events: TraversalEvent[];
}

export interface Snapshot {
  kind: 'snapshot.v1';
  tick_id: number;
  ts: string;
  graph: {
    nodes: NodeDelta[];
    links: LinkDelta[];
  };
  metrics?: any;
  history_available_since: number;
}

// ============================================================================
// VizClient Class
// ============================================================================

export type EventCallback = (event: TraversalEvent) => void;
export type StateCallback = (nodes: Map<string, NodeDelta>, links: Map<string, LinkDelta>) => void;

export class VizClient {
  // State cache
  private cacheNodes = new Map<string, NodeDelta>();
  private cacheLinks = new Map<string, LinkDelta>(); // key = `${src}→${dst}`
  private lastTick = -1;

  // WebSocket connection
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000; // ms, exponential backoff

  // Callbacks
  private onStateUpdate: StateCallback | null = null;
  private onTraversalEvent: EventCallback | null = null;
  private onConnected: (() => void) | null = null;
  private onDisconnected: (() => void) | null = null;

  // Render scheduling
  private renderScheduled = false;

  // Configuration
  private wsUrl: string;
  private httpBaseUrl: string;

  constructor(wsUrl: string, httpBaseUrl?: string) {
    this.wsUrl = wsUrl;
    this.httpBaseUrl = httpBaseUrl || wsUrl.replace('ws://', 'http://').replace('wss://', 'https://');
  }

  // ========================================================================
  // Public API
  // ========================================================================

  /**
   * Connect to visualization stream
   */
  async connect(): Promise<void> {
    console.log('[VizClient] Connecting to', this.wsUrl);

    // 1) Bootstrap with snapshot
    await this.loadSnapshot();

    // 2) Connect WebSocket for live updates
    this.connectWebSocket();
  }

  /**
   * Disconnect and clean up
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.reconnectAttempts = 0;
  }

  /**
   * Register callback for state updates
   */
  onState(callback: StateCallback): void {
    this.onStateUpdate = callback;
  }

  /**
   * Register callback for traversal events
   */
  onEvent(callback: EventCallback): void {
    this.onTraversalEvent = callback;
  }

  /**
   * Register connection callbacks
   */
  onConnection(onConnected: () => void, onDisconnected: () => void): void {
    this.onConnected = onConnected;
    this.onDisconnected = onDisconnected;
  }

  /**
   * Get current node state
   */
  getNodes(): Map<string, NodeDelta> {
    return new Map(this.cacheNodes);
  }

  /**
   * Get current link state
   */
  getLinks(): Map<string, LinkDelta> {
    return new Map(this.cacheLinks);
  }

  /**
   * Get specific node by ID
   */
  getNode(id: string): NodeDelta | undefined {
    return this.cacheNodes.get(id);
  }

  /**
   * Get specific link by src/dst
   */
  getLink(src: string, dst: string): LinkDelta | undefined {
    return this.cacheLinks.get(`${src}→${dst}`);
  }

  /**
   * Get all active nodes (above threshold)
   */
  getActiveNodes(): NodeDelta[] {
    return Array.from(this.cacheNodes.values()).filter(n => n.active);
  }

  /**
   * Get all active links (being traversed)
   */
  getActiveLinks(): LinkDelta[] {
    return Array.from(this.cacheLinks.values()).filter(l => l.active);
  }

  /**
   * Get nodes by subentity activation
   */
  getNodesBySubentity(subentity: string, minEnergy: number = 0): NodeDelta[] {
    return Array.from(this.cacheNodes.values()).filter(node => {
      const energy = node.entity_energies[subentity] || 0;
      return energy >= minEnergy;
    });
  }

  // ========================================================================
  // Private Methods - Connection
  // ========================================================================

  private async loadSnapshot(): Promise<void> {
    try {
      console.log('[VizClient] Loading snapshot from', `${this.httpBaseUrl}/viz/snapshot`);
      const response = await fetch(`${this.httpBaseUrl}/viz/snapshot`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const snapshot: Snapshot = await response.json();
      console.log('[VizClient] Loaded snapshot:', {
        tick: snapshot.tick_id,
        nodes: snapshot.graph.nodes.length,
        links: snapshot.graph.links.length
      });

      // Apply snapshot as initial state
      this.applySnapshot(snapshot);

    } catch (error) {
      console.error('[VizClient] Failed to load snapshot:', error);
      throw error;
    }
  }

  private connectWebSocket(): void {
    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        console.log('[VizClient] WebSocket connected');
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        if (this.onConnected) {
          this.onConnected();
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('[VizClient] Failed to parse message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('[VizClient] WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('[VizClient] WebSocket closed');
        if (this.onDisconnected) {
          this.onDisconnected();
        }
        this.attemptReconnect();
      };

    } catch (error) {
      console.error('[VizClient] Failed to connect WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[VizClient] Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff

    console.log(`[VizClient] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.connectWebSocket();
    }, delay);
  }

  // ========================================================================
  // Private Methods - Message Handling
  // ========================================================================

  private handleMessage(message: any): void {
    switch (message.kind) {
      case 'state_delta.v1':
        this.applyStateDelta(message as StateDelta);
        break;

      case 'traversal_events.v1':
        this.applyTraversalEvents(message as TraversalEvents);
        break;

      case 'snapshot.v1':
        this.applySnapshot(message as Snapshot);
        break;

      default:
        console.warn('[VizClient] Unknown message kind:', message.kind);
    }
  }

  private applySnapshot(snapshot: Snapshot): void {
    console.log('[VizClient] Applying snapshot', snapshot.tick_id);

    // Clear cache
    this.cacheNodes.clear();
    this.cacheLinks.clear();

    // Apply all nodes
    snapshot.graph.nodes.forEach(node => {
      this.cacheNodes.set(node.id, node);
    });

    // Apply all links
    snapshot.graph.links.forEach(link => {
      const key = `${link.src}→${link.dst}`;
      this.cacheLinks.set(key, link);
    });

    // Update tick
    this.lastTick = snapshot.tick_id;

    // Trigger render
    this.scheduleRender();
  }

  private applyStateDelta(delta: StateDelta): void {
    // Drop out-of-order frames
    if (delta.tick_id <= this.lastTick) {
      console.warn('[VizClient] Dropping out-of-order frame:', delta.tick_id, '<=', this.lastTick);
      return;
    }

    // Apply node updates
    if (delta.nodes) {
      delta.nodes.forEach(node => {
        this.cacheNodes.set(node.id, node);
      });
    }

    // Apply node removals
    if (delta.nodes_removed) {
      delta.nodes_removed.forEach(id => {
        this.cacheNodes.delete(id);
      });
    }

    // Apply link updates
    if (delta.links) {
      delta.links.forEach(link => {
        const key = `${link.src}→${link.dst}`;
        this.cacheLinks.set(key, link);
      });
    }

    // Apply link removals
    if (delta.links_removed) {
      delta.links_removed.forEach(([src, dst]) => {
        const key = `${src}→${dst}`;
        this.cacheLinks.delete(key);
      });
    }

    // Update tick
    this.lastTick = delta.tick_id;

    // Log stats occasionally
    if (delta.tick_id % 100 === 0) {
      console.log('[VizClient] State update:', {
        tick: delta.tick_id,
        nodes: this.cacheNodes.size,
        links: this.cacheLinks.size,
        dt_ms: delta.dt_ms,
        coalesced: delta.coalesced_ticks
      });
    }

    // Trigger render
    this.scheduleRender();
  }

  private applyTraversalEvents(events: TraversalEvents): void {
    if (!this.onTraversalEvent) {
      return; // No callback registered
    }

    // Process events sequentially
    events.events.forEach(event => {
      this.onTraversalEvent!(event);
    });
  }

  private scheduleRender(): void {
    if (this.renderScheduled) {
      return; // Already scheduled
    }

    this.renderScheduled = true;

    requestAnimationFrame(() => {
      this.renderScheduled = false;

      // Notify state callback
      if (this.onStateUpdate) {
        this.onStateUpdate(this.cacheNodes, this.cacheLinks);
      }
    });
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get dominant subentity for a node (highest energy)
 */
export function getDominantSubentity(node: NodeDelta): string | null {
  let maxEnergy = 0;
  let dominant: string | null = null;

  for (const [subentity, energy] of Object.entries(node.entity_energies)) {
    if (energy > maxEnergy) {
      maxEnergy = energy;
      dominant = subentity;
    }
  }

  return dominant;
}

/**
 * Get all subentities active at a node (above threshold)
 */
export function getActiveSubentities(node: NodeDelta, threshold: number = 0.01): string[] {
  return Object.entries(node.entity_energies)
    .filter(([_, energy]) => energy >= threshold)
    .map(([subentity, _]) => subentity);
}

/**
 * Compute link key for cache lookup
 */
export function linkKey(src: string, dst: string): string {
  return `${src}→${dst}`;
}

/**
 * Parse link key back to src/dst
 */
export function parseLinkKey(key: string): [string, string] | null {
  const parts = key.split('→');
  if (parts.length !== 2) return null;
  return [parts[0], parts[1]];
}
