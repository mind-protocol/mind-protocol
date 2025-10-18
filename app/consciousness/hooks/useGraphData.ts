import { useState, useEffect, useCallback, useRef } from 'react';

export interface Node {
  id: string;
  node_id?: string;
  labels?: string[];
  node_type?: string;
  text?: string;
  arousal?: number;
  confidence?: number;
  entity_activations?: Record<string, { energy: number; last_activated?: number }>;
  last_active?: number;
  last_traversed_by?: string;
  traversal_count?: number;
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
  sub_entity_valences?: Record<string, number>;
  sub_entity_emotion_vectors?: Record<string, Record<string, number>>;
  entity_activations?: Record<string, { energy: number }>;
}

export interface Entity {
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
 * Manages WebSocket connection to visualization_server.py
 * Provides real-time consciousness substrate state
 */
export function useGraphData() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [links, setLinks] = useState<Link[]>([]);
  const [entities, setEntities] = useState<Entity[]>([]);
  const [operations, setOperations] = useState<Operation[]>([]);
  const [connected, setConnected] = useState(false);
  const [availableGraphs, setAvailableGraphs] = useState<AvailableGraphs>({
    citizens: [],
    organizations: [],
    ecosystems: []
  });

  const wsRef = useRef<WebSocket | null>(null);
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

  // Connect to specific graph
  const selectGraph = useCallback((graphType: string, graphId: string) => {
    if (!graphId) return;

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    setCurrentGraphType(graphType);
    setCurrentGraphId(graphId);

    // Establish WebSocket connection
    // Connect directly to backend (bypassing Next.js proxy for WebSocket)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
    const wsUrl = `${wsProtocol}//${wsHost}/ws/graph/${graphType}/${graphId}`;

    console.log('Connecting to WebSocket:', wsUrl);
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Connected to', graphType, graphId);
      setConnected(true);
    };

    ws.onmessage = (event) => {
      console.log('WebSocket message received:', event.data);
      try {
        const message = JSON.parse(event.data);

        if (message.type === 'initial_state') {
          // Full state load
          console.log('Initial state received:', message.data);
          setNodes(message.data.nodes || []);
          setLinks(message.data.links || []);
          setEntities(message.data.entities || []);
        }
        else if (message.type === 'graph_update') {
          // Incremental update
          applyDiff(message.diff);

          // Track operations for animations
          if (message.operations && message.operations.length > 0) {
            setOperations(prev => [...message.operations, ...prev].slice(0, 50));
          }
        }
        else if (message.type === 'error') {
          console.error('Server error:', message.message);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed. Code:', event.code, 'Reason:', event.reason);
      setConnected(false);
    };

    wsRef.current = ws;
  }, []);

  // Apply incremental diff to state
  const applyDiff = (diff: any) => {
    if (diff.nodes_added) {
      setNodes(prev => [...prev, ...diff.nodes_added]);
    }

    if (diff.nodes_updated) {
      setNodes(prev => prev.map(node => {
        const updated = diff.nodes_updated.find((n: Node) => n.id === node.id);
        return updated || node;
      }));
    }

    if (diff.links_added) {
      setLinks(prev => [...prev, ...diff.links_added]);
    }

    if (diff.links_updated) {
      setLinks(prev => prev.map(link => {
        const updated = diff.links_updated.find((l: Link) => l.id === link.id);
        return updated || link;
      }));
    }
  };

  // Auto-connect to first available graph
  useEffect(() => {
    if (availableGraphs.citizens && availableGraphs.citizens.length > 0 && !currentGraphId) {
      const firstCitizen = availableGraphs.citizens[0];
      console.log('Auto-connecting to:', firstCitizen);
      selectGraph('citizen', firstCitizen.id);
    }
  }, [availableGraphs, currentGraphId, selectGraph]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    nodes,
    links,
    entities,
    operations,
    connected,
    selectGraph,
    availableGraphs,
    currentGraphType,
    currentGraphId
  };
}
