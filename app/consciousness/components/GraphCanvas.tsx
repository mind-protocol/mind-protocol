'use client';

import { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import type { Node, Link, Operation } from '../hooks/useGraphData';
import { SUBENTITY_COLORS as ENTITY_COLORS, hexToRgb } from '../constants/subentity-colors';
import { useWebSocket } from '../hooks/useWebSocket';
import { emotionToHSL, hslToCSS } from '../lib/emotionColor';
import { shouldUpdateColor, type EmotionDisplayState } from '../lib/emotionHysteresis';
import type { EmotionMetadata } from '../hooks/websocket-types';

interface GraphCanvasProps {
  nodes: Node[];
  links: Link[];
  operations: Operation[];
  subentities?: { subentity_id: string; name?: string }[];
}

/**
 * GraphCanvas - D3 Force-Directed Graph Visualization
 *
 * Renders consciousness substrate as interactive graph.
 * Emoji-based nodes, valence-colored links, real-time updates.
 *
 * Visual encodings:
 * - Emoji = Node type
 * - Size = Weight (energy + confidence + traversals)
 * - Glow = Recent activity
 * - Link color = Type (structural) or Valence (subentity view)
 * - Link thickness = Hebbian strength
 */
export function GraphCanvas({ nodes, links, operations, subentities = [] }: GraphCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedSubentity, setSelectedSubentity] = useState<string>('structural');

  // 2-layer simulation state
  const [expandedClusters, setExpandedClusters] = useState<Set<string>>(new Set());
  const clusterAnchors = useRef<Map<string, { x: number; y: number }>>(new Map());
  const innerSimulations = useRef<Map<string, d3.Simulation<any, any>>>(new Map());

  // Emotion coloring state + v2 event streams (node.flip, link.flow)
  const { emotionState, v2State } = useWebSocket();

  // Track emotion display states for hysteresis (per node and link)
  const emotionDisplayStates = useRef<Map<string, EmotionDisplayState>>(new Map());
  const linkEmotionDisplayStates = useRef<Map<string, EmotionDisplayState>>(new Map());

  // PERFORMANCE: Identify subentities (nodes in working memory - last 10 seconds) - computed once per nodes update
  // Sub-entity architecture: entity_name = node_name, any node with recent traversal + energy becomes subentity
  // For visualization: all subentities get 'default' color glow (slate)
  const activeNodesBySubentity = useMemo(() => {
    const now = Date.now();
    const workingMemoryWindow = 10000; // 10 seconds
    const entityMap = new Map<string, Set<string>>();

    nodes.forEach(node => {
      // Sub-entity detection: recent traversal + non-zero energy
      const lastTraversal = node.last_traversal_time;
      const energy = node.energy || 0;

      if (lastTraversal && energy > 0 && (now - lastTraversal) < workingMemoryWindow) {
        // All active subentities get mapped to 'default' for visualization
        // (Each node is technically its own subentity, but we use single color for all)
        const entityId = 'default';
        if (!entityMap.has(entityId)) {
          entityMap.set(entityId, new Set());
        }
        entityMap.get(entityId)!.add(node.id || node.node_id!);
      }
    });

    return entityMap;
  }, [nodes]);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = typeof window !== 'undefined' ? window.innerWidth : 1920;
    const height = typeof window !== 'undefined' ? window.innerHeight : 1080;

    // Clear previous content
    svg.selectAll('*').remove();

    const g = svg.append('g');

    // Define SVG filters and markers
    const defs = svg.append('defs');

    // PARCHMENT TEXTURE FILTER (for node backgrounds)
    const parchmentFilter = defs.append('filter')
      .attr('id', 'parchment-texture')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    parchmentFilter.append('feTurbulence')
      .attr('type', 'fractalNoise')
      .attr('baseFrequency', '0.04')
      .attr('numOctaves', '5')
      .attr('seed', '2')
      .attr('result', 'noise');

    parchmentFilter.append('feColorMatrix')
      .attr('in', 'noise')
      .attr('type', 'matrix')
      .attr('values', '1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.03 0')
      .attr('result', 'coloredNoise');

    const parchmentBlend = parchmentFilter.append('feBlend')
      .attr('in', 'SourceGraphic')
      .attr('in2', 'coloredNoise')
      .attr('mode', 'multiply');

    // WIREFRAME GLOW FILTER (for emoji icons)
    const wireframeGlow = defs.append('filter')
      .attr('id', 'wireframe-glow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    wireframeGlow.append('feGaussianBlur')
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', '2')
      .attr('result', 'blur');

    wireframeGlow.append('feFlood')
      .attr('flood-color', '#00d9ff')
      .attr('flood-opacity', '0.6')
      .attr('result', 'color');

    wireframeGlow.append('feComposite')
      .attr('in', 'color')
      .attr('in2', 'blur')
      .attr('operator', 'in')
      .attr('result', 'glow');

    const wireMerge = wireframeGlow.append('feMerge');
    wireMerge.append('feMergeNode').attr('in', 'glow');
    wireMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // GOLD SHIMMER FILTER (for high-energy nodes)
    const goldShimmer = defs.append('filter')
      .attr('id', 'gold-shimmer')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    goldShimmer.append('feGaussianBlur')
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', '3')
      .attr('result', 'blur');

    goldShimmer.append('feFlood')
      .attr('flood-color', '#ffd700')
      .attr('flood-opacity', '0.8')
      .attr('result', 'goldColor');

    goldShimmer.append('feComposite')
      .attr('in', 'goldColor')
      .attr('in2', 'blur')
      .attr('operator', 'in')
      .attr('result', 'goldGlow');

    const goldMerge = goldShimmer.append('feMerge');
    goldMerge.append('feMergeNode').attr('in', 'goldGlow');
    goldMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // PARTICLE BLUR FILTER (for energy flow particles)
    const particleBlur = defs.append('filter')
      .attr('id', 'particle-blur')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    particleBlur.append('feGaussianBlur')
      .attr('in', 'SourceGraphic')
      .attr('stdDeviation', '3');

    // SUBENTITY-COLORED GLOWS (for subentity active nodes)
    // Create a glow filter for each subentity color
    Object.entries(ENTITY_COLORS).forEach(([entityId, colorHex]) => {
      const rgb = hexToRgb(colorHex);

      const entityGlow = defs.append('filter')
        .attr('id', `subentity-glow-${entityId}`)
        .attr('x', '-50%')
        .attr('y', '-50%')
        .attr('width', '200%')
        .attr('height', '200%');

      entityGlow.append('feGaussianBlur')
        .attr('in', 'SourceAlpha')
        .attr('stdDeviation', '4')
        .attr('result', 'blur');

      entityGlow.append('feFlood')
        .attr('flood-color', colorHex)
        .attr('flood-opacity', '0.9')
        .attr('result', 'entityColor');

      entityGlow.append('feComposite')
        .attr('in', 'entityColor')
        .attr('in2', 'blur')
        .attr('operator', 'in')
        .attr('result', 'entityGlow');

      const entityMerge = entityGlow.append('feMerge');
      entityMerge.append('feMergeNode').attr('in', 'entityGlow');
      entityMerge.append('feMergeNode').attr('in', 'SourceGraphic');
    });

    // Type-based arrows
    ['JUSTIFIES', 'BUILDS_TOWARD', 'ENABLES', 'USES', 'default'].forEach(type => {
      defs.append('marker')
        .attr('id', `arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 25)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', getLinkTypeColor(type));
    });

    // Valence-based arrow (for subentity view)
    defs.append('marker')
      .attr('id', 'arrow-valence')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#94a3b8');

    // Zoom behavior with double-click to reset
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 8]) // Allow zoom out to see full graph, zoom in for details
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom as any);

    // Reset zoom on double-click
    svg.on('dblclick.zoom', () => {
      svg.transition()
        .duration(750)
        .call(zoom.transform as any, d3.zoomIdentity);
    });

    // Filter out invalid links (null source/target from backend)
    const nodeIds = new Set(nodes.map(n => n.id));
    const validLinks = links.filter(link => {
      if (!link.source || !link.target) {
        console.warn(`[GraphCanvas] Skipping link with null source/target:`, link);
        return false;
      }
      // Check if source/target nodes exist
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      if (!nodeIds.has(sourceId) || !nodeIds.has(targetId)) {
        console.warn(`[GraphCanvas] Skipping link with missing nodes:`, link);
        return false;
      }
      return true;
    });

    if (validLinks.length !== links.length) {
      console.warn(`[GraphCanvas] Filtered ${links.length - validLinks.length} invalid links (${validLinks.length}/${links.length} valid)`);
    }

    // ========================================================================
    // TWO-LAYER FORCE SIMULATION ARCHITECTURE
    // ========================================================================
    // Outer sim: Cluster meta-graph (always running, controls inter-cluster spacing)
    // Inner sim(s): Node layout within expanded clusters (anchored to outer positions)

    const nodeR = 6; // Visual node radius
    const pad = 2;   // Padding

    // Helper: Get primary cluster (entity with highest energy) for a node
    const getPrimaryCluster = (node: any): string | null => {
      if (!node.entity_activations) return null;
      let maxEnergy = 0;
      let primaryEntity = null;
      for (const [entityId, data] of Object.entries(node.entity_activations)) {
        if ((data as any).energy > maxEnergy) {
          maxEnergy = (data as any).energy;
          primaryEntity = entityId;
        }
      }
      return primaryEntity;
    };

    // ========================================================================
    // PHASE 1: Build Cluster Meta-Graph
    // ========================================================================

    // Group nodes by primary entity
    const clusterMap = new Map<string, any[]>();
    nodes.forEach((node: any) => {
      const clusterId = getPrimaryCluster(node);
      if (!clusterId) return;
      if (!clusterMap.has(clusterId)) {
        clusterMap.set(clusterId, []);
      }
      clusterMap.get(clusterId)!.push(node);
    });

    // Create cluster meta-nodes
    const clusterNodes = Array.from(clusterMap.entries()).map(([id, members]) => ({
      id,
      size: members.length,
      members
    }));

    // Build inter-cluster links (aggregated)
    const interClusterLinkMap = new Map<string, { source: string; target: string; weight: number }>();
    validLinks.forEach((link: any) => {
      const sourceCluster = getPrimaryCluster(link.source);
      const targetCluster = getPrimaryCluster(link.target);
      if (!sourceCluster || !targetCluster || sourceCluster === targetCluster) return;

      const key = sourceCluster < targetCluster
        ? `${sourceCluster}→${targetCluster}`
        : `${targetCluster}→${sourceCluster}`;

      if (!interClusterLinkMap.has(key)) {
        interClusterLinkMap.set(key, {
          source: sourceCluster,
          target: targetCluster,
          weight: 0
        });
      }
      interClusterLinkMap.get(key)!.weight++;
    });
    const interClusterLinks = Array.from(interClusterLinkMap.values());

    // ========================================================================
    // PHASE 2: Outer Simulation (Cluster Positions)
    // ========================================================================

    const outerSim = d3.forceSimulation(clusterNodes as any)
      .force('link', d3.forceLink(interClusterLinks)
        .id((d: any) => d.id)
        .distance(200)         // INCREASED: 40 → 200 (much more space between clusters)
        .strength((l: any) => 0.8 + 0.2 * Math.min(l.weight / 5, 1)))
      .force('charge', d3.forceManyBody()
        .strength(-150)        // FIXED: 5 → -150 (repulsion, not attraction!)
        .distanceMax(400))     // INCREASED: 120 → 400 (wider repulsion range)
      .force('collide', d3.forceCollide()
        .radius((d: any) => 30 + 4 * Math.sqrt(d.size)))  // INCREASED: larger collision radius
      .force('center', d3.forceCenter(width / 2, height / 2))
      .alphaDecay(0.05)
      .stop();

    // Run outer sim to convergence
    for (let i = 0; i < 250; ++i) outerSim.tick();

    // Store cluster anchors
    clusterNodes.forEach((cluster: any) => {
      clusterAnchors.current.set(cluster.id, { x: cluster.x, y: cluster.y });
    });

    // Calculate bounds and fit graph to viewport
    if (clusterNodes.length > 0) {
      const padding = 100; // 100px padding around graph
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

      clusterNodes.forEach((cluster: any) => {
        const radius = 30 + 4 * Math.sqrt(cluster.size);
        minX = Math.min(minX, cluster.x - radius);
        maxX = Math.max(maxX, cluster.x + radius);
        minY = Math.min(minY, cluster.y - radius);
        maxY = Math.max(maxY, cluster.y + radius);
      });

      const boundsWidth = maxX - minX;
      const boundsHeight = maxY - minY;
      const scale = Math.min(
        (width - padding * 2) / boundsWidth,
        (height - padding * 2) / boundsHeight,
        1 // Don't zoom in beyond 1x
      );

      const centerX = (minX + maxX) / 2;
      const centerY = (minY + maxY) / 2;
      const translateX = width / 2 - centerX * scale;
      const translateY = height / 2 - centerY * scale;

      // Apply initial transform to fit graph in viewport
      const initialTransform = d3.zoomIdentity
        .translate(translateX, translateY)
        .scale(scale);

      svg.call(zoom.transform as any, initialTransform);
    }

    // ========================================================================
    // PHASE 3: Inner Simulation Generator (for expanded clusters)
    // ========================================================================

    const createInnerSim = (clusterId: string, members: any[], anchor: { x: number; y: number }) => {
      // Get intra-cluster links
      const memberIds = new Set(members.map(n => n.id));
      const intraLinks = validLinks.filter((l: any) => {
        const sourceId = typeof l.source === 'object' ? l.source.id : l.source;
        const targetId = typeof l.target === 'object' ? l.target.id : l.target;
        return memberIds.has(sourceId) && memberIds.has(targetId);
      });

      return d3.forceSimulation(members as any)
        .force('link', d3.forceLink(intraLinks)
          .id((d: any) => d.id)
          .distance(100)         // INCREASED: 30 → 100 (links now visible!)
          .strength(0.3))        // REDUCED: 0.4 → 0.3 (softer link constraint)
        .force('charge', d3.forceManyBody()
          .strength(-80)         // INCREASED: -14 → -80 (much stronger repulsion)
          .distanceMin(20)       // INCREASED: 8 → 20 (prevent node overlap)
          .distanceMax(200))     // INCREASED: 80 → 200 (wider repulsion range)
        .force('collide', d3.forceCollide()
          .radius(nodeR * 2 + pad))  // INCREASED: collision radius doubled
        .force('x', d3.forceX(anchor.x).strength(0.15))  // REDUCED: 0.2 → 0.15 (looser anchoring)
        .force('y', d3.forceY(anchor.y).strength(0.15))  // REDUCED: 0.2 → 0.15 (looser anchoring)
        .alpha(1)
        .alphaDecay(0.05);
    };

    // Create inner sims for expanded clusters
    expandedClusters.forEach(clusterId => {
      const cluster = clusterNodes.find((c: any) => c.id === clusterId);
      if (!cluster) return;
      const anchor = clusterAnchors.current.get(clusterId);
      if (!anchor) return;

      const innerSim = createInnerSim(clusterId, cluster.members, anchor);
      innerSimulations.current.set(clusterId, innerSim);
    });

    // Main simulation reference (for compatibility with existing rendering)
    const simulation = outerSim as any;  // Will update rendering to handle both layers

    // ========================================================================
    // RENDER CLUSTER HULLS (for collapsed clusters)
    // ========================================================================

    const clusterHulls = g.append('g')
      .attr('class', 'cluster-hulls')
      .selectAll('g.cluster-hull')
      .data(clusterNodes.filter((c: any) => !expandedClusters.has(c.id)))
      .join('g')
      .attr('class', 'cluster-hull')
      .style('cursor', 'pointer')
      .on('click', (event, d: any) => {
        event.stopPropagation();
        // Toggle expansion
        setExpandedClusters(prev => {
          const next = new Set(prev);
          if (next.has(d.id)) {
            next.delete(d.id);
          } else {
            next.add(d.id);
          }
          return next;
        });
      });

    // Hull circles
    clusterHulls.append('circle')
      .attr('cx', (d: any) => d.x)
      .attr('cy', (d: any) => d.y)
      .attr('r', (d: any) => 12 + 2 * Math.sqrt(d.size))
      .attr('fill', '#1e293b')
      .attr('fill-opacity', 0.3)
      .attr('stroke', '#64748b')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6);

    // Hull labels
    clusterHulls.append('text')
      .attr('x', (d: any) => d.x)
      .attr('y', (d: any) => d.y)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('fill', '#94a3b8')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .attr('pointer-events', 'none')
      .text((d: any) => `${d.id} (${d.size})`);

    // Render links with wireframe aesthetic (Venice consciousness flows)
    // Now with emotion-based coloring when available
    const linkElements = g.append('g')
      .selectAll('line')
      .data(validLinks)
      .join('line')
      .attr('stroke', d => getLinkColorWithEmotion(d, selectedSubentity, emotionState.linkEmotions))
      .attr('stroke-width', d => getLinkThickness(d))
      .attr('stroke-opacity', d => {
        // Slightly more opaque for emotional links
        const linkId = d.id || `${d.source}-${d.target}`;
        const hasEmotion = emotionState.linkEmotions.has(linkId);
        if (hasEmotion) return 0.85;
        return isNewLink(d) ? 0.9 : 0.7;
      })
      .attr('marker-end', d => `url(#arrow-${d.type || 'default'})`)
      .style('cursor', 'pointer')
      .style('filter', d => {
        // Enhanced glow for emotional links
        const linkId = d.id || `${d.source}-${d.target}`;
        const linkEmotion = emotionState.linkEmotions.get(linkId);

        if (linkEmotion && linkEmotion.magnitude > 0.3) {
          return 'drop-shadow(0 0 3px currentColor)';
        }
        if (isNewLink(d)) {
          return 'drop-shadow(0 0 2px currentColor)';
        }
        return 'none';
      })
      .attr('stroke-dasharray', d => {
        // Animated dashes for very new links (last 10 seconds)
        if (d.created_at && (Date.now() - d.created_at) < 10000) {
          return '4 2';
        }
        return 'none';
      })
      .on('mouseenter', (event, d) => {
        // Emit event for tooltip
        const customEvent = new CustomEvent('link:hover', { detail: { link: d, event } });
        window.dispatchEvent(customEvent);
      })
      .on('mouseleave', () => {
        const customEvent = new CustomEvent('link:leave');
        window.dispatchEvent(customEvent);
      });

    // Render nodes (groups with emotion-colored circles + emoji)
    // ONLY show nodes from expanded clusters
    const visibleNodes = nodes.filter((node: any) => {
      const clusterId = getPrimaryCluster(node);
      return clusterId && expandedClusters.has(clusterId);
    });

    const nodeGroups = g.append('g')
      .selectAll('g.node-group')
      .data(visibleNodes)
      .join('g')
      .attr('class', 'node-group')
      .style('cursor', 'pointer')
      .style('pointer-events', 'all')
      .call(drag(simulation) as any)
      .on('click', (event, d) => {
        event.stopPropagation();
        const customEvent = new CustomEvent('node:click', { detail: { node: d, event } });
        window.dispatchEvent(customEvent);
      })
      .on('mouseenter', (event, d) => {
        const customEvent = new CustomEvent('node:hover', { detail: { node: d, event } });
        window.dispatchEvent(customEvent);
      })
      .on('mouseleave', () => {
        const customEvent = new CustomEvent('node:leave');
        window.dispatchEvent(customEvent);
      });

    // Add emotion-colored circles behind emojis
    nodeGroups.append('circle')
      .attr('class', 'emotion-background')
      .attr('r', d => getNodeSize(d) * 0.5)
      .attr('fill', d => {
        const nodeId = d.id || d.node_id;
        if (!nodeId) return '#1e293b'; // Default dark slate

        const emotionMeta = emotionState.nodeEmotions.get(nodeId);
        if (!emotionMeta || emotionMeta.magnitude < 0.05) {
          return '#1e293b'; // Default for neutral/no emotion
        }

        // Extract valence and arousal from axes
        const valence = emotionMeta.axes.find(a => a.axis === 'valence')?.value ?? 0;
        const arousal = emotionMeta.axes.find(a => a.axis === 'arousal')?.value ?? 0;

        // Convert to HSL
        const color = emotionToHSL(valence, arousal);
        return hslToCSS(color);
      })
      .attr('opacity', 0.8)
      .style('filter', 'url(#parchment-texture)');

    // Add emoji text on top of circles
    const nodeElements = nodeGroups.append('text')
      .style('user-select', 'none')
      .style('pointer-events', 'none')
      .style('font-family', '"Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji", sans-serif')
      .style('text-anchor', 'middle')
      .style('dominant-baseline', 'central')
      .attr('font-size', d => getNodeSize(d) * 0.7)
      .text(d => getNodeEmoji(d));

    // PERFORMANCE: Pre-compute which subentity each active node belongs to
    const nodeToSubentity = new Map<string, string>();
    activeNodesBySubentity.forEach((nodeIds, entityId) => {
      nodeIds.forEach(nodeId => {
        if (!nodeToSubentity.has(nodeId)) {
          nodeToSubentity.set(nodeId, entityId);
        }
      });
    });

    // Update node filters (wireframe glow + subentity glow for active nodes + gold shimmer + activity glows)
    const updateNodeEffects = () => {
      nodeElements.each(function(d: any) {
        const node = d3.select(this);
        const activityGlow = getNodeGlow(d);
        const hasGoldEnergy = shouldApplyGoldShimmer(d);

        // Check if node is recently active for any subentity
        const nodeId = d.id || d.node_id;
        const activeSubentity = nodeToSubentity.get(nodeId);

        // Build filter string: wireframe glow + subentity glow (if active) + gold shimmer + activity glow
        let filterStr = 'url(#wireframe-glow)';

        // Subentity-colored glow for recently active nodes
        if (activeSubentity) {
          filterStr += ` url(#subentity-glow-${activeSubentity})`;
        }

        if (hasGoldEnergy) {
          filterStr += ' url(#gold-shimmer)';
        }

        if (activityGlow !== 'none') {
          filterStr += ` ${activityGlow}`;
        }

        node.style('filter', filterStr);
      });
    };

    // Update emotion colors with hysteresis (prevents flicker)
    const updateEmotionColors = () => {
      nodeGroups.select('circle.emotion-background').attr('fill', function(d: any) {
        const nodeId = d.id || d.node_id;
        if (!nodeId) return '#1e293b';

        const emotionMeta = emotionState.nodeEmotions.get(nodeId);
        if (!emotionMeta || emotionMeta.magnitude < 0.05) {
          return '#1e293b'; // Neutral
        }

        // Extract valence and arousal
        const valence = emotionMeta.axes.find(a => a.axis === 'valence')?.value ?? 0;
        const arousal = emotionMeta.axes.find(a => a.axis === 'arousal')?.value ?? 0;

        // Get or create display state for hysteresis
        let displayState = emotionDisplayStates.current.get(nodeId);
        if (!displayState) {
          // Initialize display state
          displayState = {
            actual: { valence, arousal, magnitude: emotionMeta.magnitude },
            displayed: { valence, arousal, magnitude: emotionMeta.magnitude },
            lastUpdateTime: Date.now()
          };
          emotionDisplayStates.current.set(nodeId, displayState);
        } else {
          // Update actual emotion
          displayState.actual = { valence, arousal, magnitude: emotionMeta.magnitude };

          // Check if update needed (hysteresis)
          if (shouldUpdateColor(displayState)) {
            displayState.displayed = { valence, arousal, magnitude: emotionMeta.magnitude };
            displayState.lastUpdateTime = Date.now();
          }
        }

        // Convert displayed emotion to HSL
        const color = emotionToHSL(displayState.displayed.valence, displayState.displayed.arousal);
        return hslToCSS(color);
      });
    };

    // Update link emotion colors with hysteresis
    const updateLinkEmotionColors = () => {
      linkElements.attr('stroke', function(d: any) {
        const linkId = d.id || `${typeof d.source === 'object' ? d.source.id : d.source}-${typeof d.target === 'object' ? d.target.id : d.target}`;

        const linkEmotion = emotionState.linkEmotions.get(linkId);
        if (!linkEmotion || linkEmotion.magnitude < 0.05) {
          // Fall back to default color
          return getLinkColor(d, selectedSubentity);
        }

        // Extract valence and arousal
        const valence = linkEmotion.axes.find(a => a.axis === 'valence')?.value ?? 0;
        const arousal = linkEmotion.axes.find(a => a.axis === 'arousal')?.value ?? 0;

        // Get or create display state for hysteresis
        let displayState = linkEmotionDisplayStates.current.get(linkId);
        if (!displayState) {
          displayState = {
            actual: { valence, arousal, magnitude: linkEmotion.magnitude },
            displayed: { valence, arousal, magnitude: linkEmotion.magnitude },
            lastUpdateTime: Date.now()
          };
          linkEmotionDisplayStates.current.set(linkId, displayState);
        } else {
          displayState.actual = { valence, arousal, magnitude: linkEmotion.magnitude };

          if (shouldUpdateColor(displayState)) {
            displayState.displayed = { valence, arousal, magnitude: linkEmotion.magnitude };
            displayState.lastUpdateTime = Date.now();
          }
        }

        // Convert to HSL
        const color = emotionToHSL(displayState.displayed.valence, displayState.displayed.arousal);
        return hslToCSS(color);
      });
    };

    updateNodeEffects(); // Initial update
    updateEmotionColors(); // Initial emotion colors
    updateLinkEmotionColors(); // Initial link emotion colors
    const effectInterval = setInterval(() => {
      updateNodeEffects();
      updateEmotionColors();
      updateLinkEmotionColors();
    }, 2000); // Update every 2 seconds

    // Simulation tick
    // Outer sim already converged (ran to completion)
    // Tick inner simulations for expanded clusters
    const tickAll = () => {
      // Tick all active inner simulations
      innerSimulations.current.forEach(sim => sim.tick());

      // Update link positions
      linkElements
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      // Position node groups (contains circle + emoji)
      nodeGroups
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    };

    // Use requestAnimationFrame for smooth ticking
    let rafId: number;
    const tick = () => {
      tickAll();
      if (innerSimulations.current.size > 0) {
        rafId = requestAnimationFrame(tick);
      }
    };
    if (innerSimulations.current.size > 0) {
      rafId = requestAnimationFrame(tick);
    }

    // Outer simulation already converged
    // Inner simulations start automatically when created and tick via RAF

    // CRITICAL: Cleanup function that properly stops simulation and clears interval
    // This runs BEFORE the effect re-runs (not just on unmount)
    return () => {
      // Cancel animation frame
      if (rafId) cancelAnimationFrame(rafId);

      // Stop outer simulation
      simulation.stop();

      // Stop all inner simulations
      innerSimulations.current.forEach(sim => sim.stop());
      innerSimulations.current.clear();

      // Clear the interval to prevent accumulation
      clearInterval(effectInterval);

      // Remove all SVG elements to prevent memory accumulation
      svg.selectAll('*').remove();

      // Nullify large objects to help garbage collection
      (simulation as any).nodes([]);
      (simulation as any).force('link', null);
      (simulation as any).force('charge', null);
      (simulation as any).force('center', null);
      (simulation as any).force('collision', null);
    };
  }, [nodes, links, selectedSubentity, expandedClusters]);

  // Visualize node.flip events (energy deltas) with temporary glows
  useEffect(() => {
    if (!svgRef.current || !v2State || !v2State.recentFlips || v2State.recentFlips.length === 0) return;

    const svg = d3.select(svgRef.current);

    // Apply flip effects to recently flipped nodes
    v2State.recentFlips.forEach(flip => {
      // Find the node element by node_id
      const nodeElement = svg.selectAll('text')
        .filter((d: any) => d && (d.id === flip.node_id || d.node_id === flip.node_id));

      if (!nodeElement.empty()) {
        const dE = flip.dE;
        const isPositive = dE > 0;
        const magnitude = Math.abs(dE);

        // Determine glow color and intensity based on energy delta
        const glowColor = isPositive ? '34, 197, 94' : '239, 68, 68'; // green (positive) or red (negative) RGB
        const glowSize = 10 + (magnitude * 60); // Scale glow with energy delta magnitude
        const opacity = Math.min(0.95, 0.5 + (magnitude * 2)); // Cap at 0.95

        // Apply temporary glow pulse with transition
        nodeElement
          .transition()
          .duration(200)
          .style('filter', `url(#wireframe-glow) drop-shadow(0 0 ${glowSize}px rgba(${glowColor}, ${opacity})) drop-shadow(0 0 ${glowSize/2}px rgba(${glowColor}, ${opacity}))`)
          .transition()
          .delay(800)
          .duration(1000)
          .style('filter', function(d: any) {
            // Fade back to normal filters (existing glow logic)
            const activityGlow = getNodeGlow(d);
            const hasGold = shouldApplyGoldShimmer(d);
            const nodeId = d.id || d.node_id;

            let filterStr = 'url(#wireframe-glow)';

            // Re-apply subentity glow if active
            const now = Date.now();
            const workingMemoryWindow = 10000;
            if (d.last_traversal_time && d.energy && d.energy > 0 && (now - d.last_traversal_time) < workingMemoryWindow) {
              filterStr += ' url(#subentity-glow-default)';
            }

            if (hasGold) filterStr += ' url(#gold-shimmer)';
            if (activityGlow !== 'none') filterStr += ` ${activityGlow}`;
            return filterStr;
          });
      }
    });
  }, [v2State?.recentFlips]);

  // Visualize link.flow.summary events with temporary thickness boost
  useEffect(() => {
    if (!svgRef.current || !v2State || !v2State.linkFlows || v2State.linkFlows.size === 0) return;

    const svg = d3.select(svgRef.current);

    // Apply flow effects to active links
    v2State.linkFlows.forEach((flowVolume, linkId) => {
      // Find the link element by link_id
      const linkElement = svg.selectAll('line')
        .filter((d: any) => {
          if (!d) return false;
          const id = d.id || `${typeof d.source === 'object' ? d.source.id : d.source}-${typeof d.target === 'object' ? d.target.id : d.target}`;
          return id === linkId;
        });

      if (!linkElement.empty()) {
        // Get current base width
        const linkData: any = linkElement.datum();
        const baseWidth = getLinkThickness(linkData);

        // Calculate flow boost (scale with flow volume)
        const flowBoost = Math.min(12, flowVolume * 8); // Add up to 12px for high flow

        // Apply temporary width increase and opacity boost
        linkElement
          .transition()
          .duration(300)
          .attr('stroke-width', baseWidth + flowBoost)
          .attr('stroke-opacity', 1.0)
          .style('filter', 'drop-shadow(0 0 4px currentColor)') // Enhanced glow during flow
          .transition()
          .delay(500)
          .duration(700)
          .attr('stroke-width', baseWidth)
          .attr('stroke-opacity', function(d: any) {
            const linkId = d.id || `${typeof d.source === 'object' ? d.source.id : d.source}-${typeof d.target === 'object' ? d.target.id : d.target}`;
            const hasEmotion = emotionState.linkEmotions && emotionState.linkEmotions.has(linkId);
            if (hasEmotion) return 0.85;
            return isNewLink(d) ? 0.9 : 0.7;
          })
          .style('filter', function(d: any) {
            // Restore original filter logic
            const linkId = d.id || `${typeof d.source === 'object' ? d.source.id : d.source}-${typeof d.target === 'object' ? d.target.id : d.target}`;
            const linkEmotion = emotionState.linkEmotions && emotionState.linkEmotions.get(linkId);

            if (linkEmotion && linkEmotion.magnitude > 0.3) {
              return 'drop-shadow(0 0 3px currentColor)';
            }
            if (isNewLink(d)) {
              return 'drop-shadow(0 0 2px currentColor)';
            }
            return 'none';
          });
      }
    });
  }, [v2State?.linkFlows, emotionState]);

  // Handle node focus from CLAUDE_DYNAMIC.md clicks
  // IMPORTANT: Empty dependency array to prevent listener accumulation
  useEffect(() => {
    const handleNodeFocus = (e: Event) => {
      const customEvent = e as CustomEvent;
      const { nodeId } = customEvent.detail;

      // Get current SVG reference
      if (!svgRef.current) return;

      const svg = d3.select(svgRef.current);
      const g = svg.select('g');

      // Find the node in the current graph
      const nodeElement = svg.selectAll('text')
        .filter((d: any) => d && (d.id === nodeId || d.node_id === nodeId));

      if (nodeElement.empty()) {
        console.log('[GraphCanvas] Node not found for focus:', nodeId);
        return;
      }

      // Get the node data
      const nodeData: any = nodeElement.datum();
      if (!nodeData || !nodeData.x || !nodeData.y) return;

      // Center view on node with smooth transition
      const width = typeof window !== 'undefined' ? window.innerWidth : 1920;
      const height = typeof window !== 'undefined' ? window.innerHeight : 1080;

      const scale = 1.5; // Zoom in a bit
      const x = -nodeData.x * scale + width / 2;
      const y = -nodeData.y * scale + height / 2;

      g.transition()
        .duration(750)
        .attr('transform', `translate(${x},${y}) scale(${scale})`);

      // Highlight node temporarily
      nodeElement
        .transition()
        .duration(300)
        .style('filter', 'url(#wireframe-glow) drop-shadow(0 0 16px #5efc82) drop-shadow(0 0 8px #5efc82)')
        .transition()
        .delay(1000)
        .duration(500)
        .style('filter', function(d: any) {
          const activityGlow = getNodeGlow(d);
          const hasGold = shouldApplyGoldShimmer(d);
          let filterStr = 'url(#wireframe-glow)';
          if (hasGold) filterStr += ' url(#gold-shimmer)';
          if (activityGlow !== 'none') filterStr += ` ${activityGlow}`;
          return filterStr;
        });
    };

    window.addEventListener('node:focus', handleNodeFocus);

    return () => {
      window.removeEventListener('node:focus', handleNodeFocus);
    };
  }, []); // Empty deps - event handler doesn't need to re-register

  return (
    <div className="relative w-full h-full">
      <svg
        ref={svgRef}
        className="w-full h-full"
        style={{ background: '#4682B4' }}
      />
      {/* Zoom hint */}
      <div className="absolute bottom-2 right-2 text-xs text-observatory-dark/40 pointer-events-none select-none">
        Double-click to reset view
      </div>
    </div>
  );
}

// ============================================================================
// Visual Encoding Functions
// ============================================================================

function getNodeEmoji(node: Node): string {
  // Use node_type (first label extracted by backend) instead of labels[0]
  // because FalkorDB returns labels as string "[Label]" not array
  const nodeType = node.node_type || 'Node';
  const EMOJIS: Record<string, string> = {
    // N1 - Personal/Individual Consciousness
    'Memory': '💭',
    'Conversation': '💬',
    'Person': '👤',
    'Relationship': '🤝',
    'Personal_Goal': '🎯',
    'Personal_Value': '💎',
    'Personal_Pattern': '🔄',
    'Realization': '💡',
    'Wound': '🩹',
    'Coping_Mechanism': '🛡️',
    'Trigger': '⚡',
    // N2 - Organizational Consciousness
    'Human': '🧑',
    'AI_Agent': '🤖',
    'Team': '👥',
    'Department': '🏢',
    'Decision': '⚖️',
    'Project': '📋',
    'Task': '✅',
    'Milestone': '🏆',
    'Best_Practice': '✨',
    'Anti_Pattern': '⚠️',
    'Risk': '🔴',
    'Metric': '📊',
    'Process': '⚙️',
    // N2/N3 - Conceptual Knowledge
    'Concept': '🧩',
    'Principle': '📜',
    'Mechanism': '🔧',
    'Document': '📄',
    'Documentation': '📖',
    // N3 - Ecosystem Intelligence (External)
    'Company': '🏛️',
    'External_Person': '👔',
    'Wallet_Address': '💰',
    'Social_Media_Account': '📱',
    // N3 - Evidence Nodes
    'Post': '📝',
    'Transaction': '💸',
    'Deal': '🤝',
    'Event': '📅',
    'Smart_Contract': '📜',
    'Integration': '🔗',
    // N3 - Derived Intelligence
    'Psychological_Trait': '🧠',
    'Behavioral_Pattern': '🔁',
    'Market_Signal': '📈',
    'Reputation_Assessment': '⭐',
    'Network_Cluster': '🕸️',
    // Fallback
    'default': '⚪'
  };
  return EMOJIS[nodeType] || EMOJIS['default'];
}

function getNodeSize(node: Node): number {
  // Use computed weight from node or fallback to calculation
  const weight = node.weight || computeNodeWeight(node);
  // Expanded range: 20px (min) to 48px (max weight)
  return Math.max(20, 16 + weight * 32);
}

function computeNodeWeight(node: Node): number {
  const energy = node.energy || 0;
  const confidence = node.confidence || 0.5;
  const traversalCount = node.traversal_count || 0;
  const normalizedTraversals = Math.min(1.0, Math.log10(traversalCount + 1) / 2);
  return (energy * 0.4) + (confidence * 0.3) + (normalizedTraversals * 0.3);
}

function getNodeGlow(node: Node): string {
  const now = Date.now();

  // Priority: Show only the most important glow (performance optimization)

  // 1. NEWEST CREATED (last 5 minutes) - Bright cyan pulse (highest priority)
  if (node.created_at) {
    const age = now - node.created_at;
    if (age < 300000) { // 5 minutes
      const intensity = 1 - (age / 300000);
      const glowSize = 12 + (intensity * 16);
      return `drop-shadow(0 0 ${glowSize}px rgba(45, 212, 191, ${intensity})) drop-shadow(0 0 ${glowSize/2}px rgba(45, 212, 191, ${intensity}))`;
    }
  }

  // 2. RECENTLY REINFORCED/DE-REINFORCED (last 2 minutes)
  if (node.last_modified && node.reinforcement_weight !== undefined) {
    const age = now - node.last_modified;
    if (age < 120000) { // 2 minutes
      const intensity = 1 - (age / 120000);
      const glowSize = 6 + (intensity * 8);

      if (node.reinforcement_weight > 0.05) {
        // GREEN for positive reinforcement
        return `drop-shadow(0 0 ${glowSize}px rgba(34, 197, 94, ${intensity * 0.8}))`;
      } else if (node.reinforcement_weight < -0.05) {
        // RED for de-reinforcement
        return `drop-shadow(0 0 ${glowSize}px rgba(239, 68, 68, ${intensity * 0.8}))`;
      }
    }
  }

  // 3. RECENTLY TRAVERSED (last 2 minutes) - Yellow/green (lowest priority)
  if (node.last_active) {
    const age = now - node.last_active;
    if (age < 120000) { // 2 minutes
      const intensity = 1 - (age / 120000);
      const glowSize = 5 + (intensity * 6);
      return `drop-shadow(0 0 ${glowSize}px rgba(94, 252, 130, ${intensity * 0.6}))`;
    }
  }

  return 'none';
}

/**
 * Gold shimmer indicates high consciousness energy (content signal)
 * Strategic Gold Rule: Use ONLY for content signals (energy/activity)
 */
function shouldApplyGoldShimmer(node: Node): boolean {
  // High energy nodes (active consciousness)
  const energy = node.energy || 0;
  if (energy > 0.7) return true;

  // High traversal activity (frequently explored)
  const traversalCount = node.traversal_count || 0;
  if (traversalCount > 10) return true;

  // Recently very active (last 5 minutes)
  if (node.last_active) {
    const age = Date.now() - node.last_active;
    if (age < 300000 && energy > 0.5) { // 5 minutes with moderate energy
      return true;
    }
  }

  return false;
}

function getLinkColor(link: Link, selectedSubentity: string): string {
  if (selectedSubentity === 'structural') {
    return getLinkTypeColor(link.type);
  } else {
    // Valence-based coloring
    const valences = link.sub_entity_valences || {};
    const valence = valences[selectedSubentity];
    return getValenceColor(valence);
  }
}

/**
 * Get link color with emotion support
 * Uses emotion-based HSL coloring when available, falls back to type/valence coloring
 */
function getLinkColorWithEmotion(
  link: Link,
  selectedSubentity: string,
  linkEmotions: Map<string, EmotionMetadata>
): string {
  // Try to get emotion data for this link
  const linkId = link.id || `${link.source}-${link.target}`;
  const linkEmotion = linkEmotions.get(linkId);

  // If link has emotion and it's above threshold, use emotion color
  if (linkEmotion && linkEmotion.magnitude > 0.05) {
    const valence = linkEmotion.axes.find(a => a.axis === 'valence')?.value ?? 0;
    const arousal = linkEmotion.axes.find(a => a.axis === 'arousal')?.value ?? 0;
    const color = emotionToHSL(valence, arousal);
    return hslToCSS(color);
  }

  // Otherwise fall back to default link coloring
  return getLinkColor(link, selectedSubentity);
}

function getLinkTypeColor(type: string): string {
  const COLORS: Record<string, string> = {
    'JUSTIFIES': '#ef4444',
    'BUILDS_TOWARD': '#3b82f6',
    'ENABLES': '#22c55e',
    'USES': '#8b5cf6',
    'default': '#666'
  };
  return COLORS[type] || COLORS['default'];
}

function getValenceColor(valence: number | undefined): string {
  if (valence === null || valence === undefined) return '#64748b';

  const normalized = (valence + 1.0) / 2.0;

  if (normalized < 0.5) {
    const t = normalized * 2;
    return d3.interpolateRgb('#ef4444', '#94a3b8')(t); // Red to gray
  } else {
    const t = (normalized - 0.5) * 2;
    return d3.interpolateRgb('#94a3b8', '#22c55e')(t); // Gray to green
  }
}

// ============================================================================
// Link Visibility Functions
// ============================================================================

function getLinkThickness(link: Link): number {
  // Use link weight or strength for thickness
  const weight = link.weight || link.strength || 0.5;
  // Range: 6px (min) to 20px (max weight) - MUCH thicker for visibility (was 3-12px)
  return Math.max(6, 6 + weight * 14);
}

function isNewLink(link: Link): boolean {
  if (!link.created_at) return false;
  const age = Date.now() - link.created_at;
  return age < 60000; // Less than 1 minute old
}

// ============================================================================
// Temporal Force (Timeline Layout)
// ============================================================================

function forceTemporalX(width: number) {
  let nodes: Node[];

  function force(alpha: number) {
    if (!nodes) return;

    const now = Date.now();
    // Find oldest and newest timestamps
    const timestamps = nodes
      .map(n => n.last_active || n.created_at || 0)
      .filter(t => t > 0);

    if (timestamps.length === 0) return;

    const minTime = Math.min(...timestamps);
    const maxTime = Math.max(...timestamps);
    const timeRange = maxTime - minTime;

    // FALLBACK: If timestamps are uniform (seed data), disable temporal force
    // Range less than 1 hour = likely bulk-imported seed data
    if (timeRange < 3600000) {
      // console.log('[Temporal Force] Timestamps too uniform, skipping');
      return; // Let other forces handle layout
    }

    // Pull nodes left-to-right based on temporal position (MINIMAL spread for clustering)
    nodes.forEach((node: any) => {
      const nodeTime = node.last_active || node.created_at || minTime;
      const timePos = (nodeTime - minTime) / timeRange; // 0 (old) to 1 (new)

      // Target X position: center ±10% width (was ±30%, now much tighter)
      const targetX = width * 0.45 + (timePos * width * 0.1);

      // Apply VERY gentle hint (not forcing)
      const dx = targetX - node.x;
      node.vx += dx * alpha * 0.01; // Barely noticeable 1% strength (was 5%)
    });
  }

  force.initialize = function(_: any) {
    nodes = _;
  };

  return force;
}

function forceValenceY(height: number) {
  let nodes: Node[];

  function force(alpha: number) {
    if (!nodes) return;

    // Pull nodes up/down based on emotional valence (MINIMAL spread for clustering)
    nodes.forEach((node: any) => {
      const valence = computeNodeValence(node);

      // Target Y position: center ±10% height (was ±30%, now much tighter)
      // Valence ranges from -1 (bottom) to +1 (top)
      const valencePos = (valence + 1) / 2; // Normalize to 0-1
      const targetY = height * 0.45 + (valencePos * height * 0.1); // Tight clustering around center

      // Apply VERY gentle hint (not forcing)
      const dy = targetY - node.y;
      node.vy += dy * alpha * 0.01; // Barely noticeable 1% strength (was 4%)
    });
  }

  force.initialize = function(_: any) {
    nodes = _;
  };

  return force;
}

function computeNodeValence(node: Node): number {
  // Aggregate valence from node properties
  let valence = 0;
  let count = 0;

  // Check if node has entity_activations with valence data
  if (node.entity_activations) {
    Object.values(node.entity_activations).forEach((activation: any) => {
      if (activation.valence !== undefined) {
        valence += activation.valence;
        count++;
      }
    });
  }

  // Node type-based valence hints (adds diversity even without runtime data)
  const nodeType = node.node_type || '';
  if (nodeType === 'Best_Practice' || nodeType === 'Realization' || nodeType === 'Personal_Goal') {
    valence += 0.3;
    count++;
  } else if (nodeType === 'Anti_Pattern' || nodeType === 'Wound' || nodeType === 'Risk') {
    valence -= 0.3;
    count++;
  } else if (nodeType === 'Trigger' || nodeType === 'Coping_Mechanism') {
    valence -= 0.15;
    count++;
  }

  // Confidence as slight positive bias (higher confidence = slight upward pull)
  if (node.confidence !== undefined && node.confidence !== null) {
    valence += (node.confidence - 0.5) * 0.2; // -0.1 to +0.1
    count++;
  }

  // Reinforcement weight affects valence
  if (node.reinforcement_weight !== undefined) {
    valence += node.reinforcement_weight * 0.5; // Scale reinforcement to valence
    count++;
  }

  // FALLBACK: Even with no data, use small random jitter to prevent perfect stacking
  if (count === 0) {
    // Use node ID as seed for consistent but distributed positioning
    const seed = parseInt(node.id, 36) || 0;
    return ((seed % 100) / 100 - 0.5) * 0.4; // -0.2 to +0.2 range
  }

  return Math.max(-1, Math.min(1, valence / count));
}

// ============================================================================
// Drag Behavior
// ============================================================================

function drag(simulation: d3.Simulation<any, undefined>) {
  function dragstarted(event: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  function dragged(event: any) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  function dragended(event: any) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended);
}
