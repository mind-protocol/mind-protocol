import { useState, useEffect, useCallback } from 'react';

export interface Node {
  id: string;
  node_id?: string;
  labels?: string[];
  node_type?: string;
  text?: string;
  energy?: number;
  confidence?: number;
  entity_activations?: Record<string, { energy: number; last_activated?: number }>;
  last_active?: number;
  last_traversal_time?: number;
  last_traversed_by?: string;
  traversal_count?: number;
  created_at?: number;
  last_modified?: number;
  base_weight?: number;
  reinforcement_weight?: number;
  weight?: number;
  x?: number;
  y?: number;
}

export interface Link {
  id: string;
  source: string | Node;
  target: string | Node;
  type: string;
  strength?: number;
  last_traversed?: number;
  created_at?: number;
  weight?: number;
  sub_entity_valences?: Record<string, number>;
  sub_entity_emotion_vectors?: Record<string, Record<string, number>>;
  entity_activations?: Record<string, { energy: number }>;
}

export interface Subentity {
  entity_id: string;
  name?: string;
}

export interface Operation {
  type: string;
  node_id?: string;
  link_id?: string;
  entity_id?: string;
  timestamp: number;
  data?: any;
}

export interface AvailableGraphs {
  citizens: Array<{ id: string; name: string }>;
  organizations: Array<{ id: string; name: string }>;
  ecosystems: Array<{ id: string; name: string }>;
}

/**
 * useGraphData Hook
 *
 * Manages graph state via REST API for initial load
 * Provides methods to update state from WebSocket events
 *
 * Architecture:
 * - Initial load: REST API /api/graph/{type}/{id}
 * - Real-time updates: WebSocket events via useWebSocket hook
 *
 * Author: Iris "The Aperture"
 * Integration with: Felix "Ironhand"'s REST API
 */
export function useGraphData() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [links, setLinks] = useState<Link[]>([]);
  const [subentities, setSubentities] = useState<Subentity[]>([]);
  const [operations, setOperations] = useState<Operation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableGraphs, setAvailableGraphs] = useState<AvailableGraphs>({
    citizens: [],
    organizations: [],
    ecosystems: []
  });

  const [currentGraphType, setCurrentGraphType] = useState<string>('citizen');
  const [currentGraphId, setCurrentGraphId] = useState<string | null>(null);

  // Fetch available graphs from server
  useEffect(() => {
    const fetchGraphs = async () => {
      try {
        const response = await fetch('/api/graphs');
        const data = await response.json();

        console.log('Raw graphs data:', data);

        // Transform backend format (string arrays) to frontend format (object arrays)
        const normalizeGraphs = (graphs: string[] | Array<{id: string, name: string}>) => {
          if (!graphs || graphs.length === 0) return [];

          // If already objects, return as-is
          if (typeof graphs[0] === 'object') {
            return graphs as Array<{id: string, name: string}>;
          }

          // If strings, convert to objects
          return (graphs as string[]).map(id => ({
            id,
            name: id.charAt(0).toUpperCase() + id.slice(1) // Capitalize first letter
          }));
        };

        const normalizedGraphs = {
          citizens: normalizeGraphs(data.citizens || []),
          organizations: normalizeGraphs(data.organizations || []),
          ecosystems: normalizeGraphs(data.ecosystems || [])
        };

        console.log('Normalized graphs:', normalizedGraphs);
        setAvailableGraphs(normalizedGraphs);
      } catch (error) {
        console.error('Error fetching graphs:', error);
      }
    };

    fetchGraphs();
  }, []); // Run once on mount

  /**
   * Load graph from REST API
   * Called when user selects a graph from the dropdown
   */
  const selectGraph = useCallback(async (graphType: string, graphId: string) => {
    if (!graphId) return;

    setCurrentGraphType(graphType);
    setCurrentGraphId(graphId);
    setLoading(true);
    setError(null);

    try {
      console.log(`[useGraphData] Fetching graph: ${graphType}/${graphId}`);
      const response = await fetch(`/api/graph/${graphType}/${graphId}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch graph: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      setNodes(data.nodes || []);
      setLinks(data.links || []);
      setSubentities(data.subentities || []);
      setLoading(false);
    } catch (err) {
      console.error('[useGraphData] Error fetching graph:', err);
      setError(err instanceof Error ? err.message : 'Failed to load graph');
      setLoading(false);
    }
  }, []);

  /**
   * Update node based on WebSocket events
   * Called when threshold_crossing or entity_activity events arrive
   * FIXED: Properly merges entity_activations and increments traversal_count
   */
  const updateNodeFromEvent = useCallback((nodeId: string, updates: Partial<Node>) => {
    setNodes(prev => prev.map(node => {
      if (node.id === nodeId || node.node_id === nodeId) {
        // Handle special cases for incremental updates
        const merged: Node = { ...node };

        // Merge entity_activations instead of replacing
        if (updates.entity_activations) {
          merged.entity_activations = {
            ...node.entity_activations,
            ...updates.entity_activations
          };
        }

        // Increment traversal_count instead of replacing
        if (updates.traversal_count) {
          merged.traversal_count = (node.traversal_count || 0) + updates.traversal_count;
        }

        // Apply all other updates normally
        return { ...merged, ...updates, entity_activations: merged.entity_activations, traversal_count: merged.traversal_count };
      }
      return node;
    }));
  }, []);

  /**
   * Update link based on WebSocket events
   * Called when subentity traverses a link
   */
  const updateLinkFromEvent = useCallback((linkId: string, updates: Partial<Link>) => {
    setLinks(prev => prev.map(link => {
      if (link.id === linkId) {
        return { ...link, ...updates };
      }
      return link;
    }));
  }, []);

  /**
   * Add operation for animation tracking
   */
  const addOperation = useCallback((operation: Operation) => {
    setOperations(prev => [operation, ...prev].slice(0, 50)); // Keep last 50
  }, []);

  // Auto-load first available graph
  useEffect(() => {
    if (availableGraphs.citizens && availableGraphs.citizens.length > 0 && !currentGraphId) {
      const firstCitizen = availableGraphs.citizens[0];
      console.log('[useGraphData] Auto-loading first graph:', firstCitizen);
      selectGraph('citizen', firstCitizen.id);
    }
  }, [availableGraphs, currentGraphId, selectGraph]);

  return {
    // Graph state
    nodes,
    links,
    subentities,
    operations,

    // Loading state
    loading,
    error,

    // Graph selection
    selectGraph,
    availableGraphs,
    currentGraphType,
    currentGraphId,

    // Event-driven updates (called by parent component with WebSocket events)
    updateNodeFromEvent,
    updateLinkFromEvent,
    addOperation
  };
}
