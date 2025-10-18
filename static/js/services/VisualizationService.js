/**
 * VisualizationService
 *
 * Handles D3 force-directed graph rendering and visual encodings.
 * Subscribes to GraphDataService for data, renders consciousness substrate.
 *
 * Author: Iris "The Aperture"
 * Purpose: Separation of rendering concerns from data management
 */

import { graphDataService } from './GraphDataService.js';

class VisualizationService {
    constructor(svgSelector) {
        // D3 references
        this.svg = d3.select(svgSelector);
        this.g = this.svg.append("g");

        // Dimensions
        this.width = window.innerWidth;
        this.height = window.innerHeight - 70;

        // D3 simulation
        this.simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(this.width / 2, (this.height - 70) / 2))
            .force("collision", d3.forceCollide().radius(35));

        // Visual elements
        this.linkElements = null;
        this.emojiElements = null;
        this.labelGroups = null;

        // Visual state
        this.selectedNode = null;
        this.selectedEntity = 'structural';  // or entity_id for per-entity view
        this.showLabels = true;
        this.mouseX = this.width / 2;
        this.mouseY = this.height / 2;
        this.currentZoomScale = 1;

        // Time filtering
        this.timeRange = 3600000; // 1 hour
        this.showRecentOnly = false;

        // Initialize zoom and mouse tracking
        this._initializeInteractions();

        // Subscribe to data updates
        graphDataService.subscribe('initialState', (state) => this.render(state));
        graphDataService.subscribe('graphUpdate', (update) => this.handleUpdate(update));
    }

    // ========================================================================
    // Public API
    // ========================================================================

    /**
     * Set entity view mode
     */
    setEntityView(entityId) {
        this.selectedEntity = entityId;
        this.render(graphDataService.getState());
    }

    /**
     * Set time range filter
     */
    setTimeRange(milliseconds) {
        this.timeRange = milliseconds;
        this.render(graphDataService.getState());
    }

    /**
     * Toggle label visibility
     */
    setShowLabels(show) {
        this.showLabels = show;
        this.render(graphDataService.getState());
    }

    /**
     * Select and highlight node
     */
    selectNode(node) {
        this.selectedNode = node;
        this._updateNodeSelection();
        this._highlightNeighborhood(node);
        return node;
    }

    /**
     * Clear selection
     */
    clearSelection() {
        this.selectedNode = null;
        this._clearHighlight();
    }

    /**
     * Zoom to specific node
     */
    zoomToNode(nodeId) {
        const state = graphDataService.getState();
        const node = state.nodes.find(n => n.id === nodeId);

        if (!node || !node.x || !node.y) {
            console.warn('Node not found or no position:', nodeId);
            return;
        }

        const transform = d3.zoomIdentity
            .translate(this.width / 2, (this.height - 70) / 2)
            .scale(2)
            .translate(-node.x, -node.y);

        this.svg.transition()
            .duration(750)
            .call(d3.zoom().transform, transform);

        setTimeout(() => {
            this.selectNode(node);
            this._highlightNeighborhood(node);
        }, 800);
    }

    // ========================================================================
    // Rendering
    // ========================================================================

    /**
     * Main render function - redraws entire visualization
     */
    render(state) {
        const { nodes, links } = this._filterByTime(state);

        // Update link elements
        this.linkElements = this.g.selectAll("line")
            .data(links, d => d.id)
            .join("line")
            .attr("stroke", d => this._getLinkColor(d))
            .attr("stroke-width", d => Math.max(2.5, (d.strength || 0.5) * 6))
            .attr("stroke-opacity", d => Math.max(0.6, this._getLinkOpacity(d, state.currentTime)))
            .attr("marker-end", d => this._getArrowMarker(d))
            .style("cursor", "pointer")
            .on("mouseenter", (event, d) => this._emitEvent('linkHover', { event, link: d }))
            .on("mouseleave", () => this._emitEvent('linkLeave'));

        // Update emoji elements (primary node visual)
        this.emojiElements = this.g.selectAll("text.emoji")
            .data(nodes, d => d.id)
            .join("text")
            .attr("class", "emoji")
            .text(d => this._getNodeEmoji(d))
            .attr("font-size", d => this._getNodeSize(d))
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "central")
            .style("pointer-events", "auto")
            .style("cursor", "pointer")
            .style("user-select", "none")
            .style("filter", d => this._getNodeGlowFilter(d, state.currentTime))
            .call(this._createDragBehavior())
            .on("click", (event, d) => {
                event.stopPropagation();
                this._emitEvent('nodeClick', { event, node: d });
            })
            .on("mouseenter", (event, d) => {
                this._emitEvent('nodeHover', { event, node: d });
                this._highlightConnectedLinks(d, links);
            })
            .on("mouseleave", () => {
                this._emitEvent('nodeLeave');
                this._unhighlightConnectedLinks();
            });

        // Update labels if enabled
        if (this.showLabels) {
            this._renderLabels(nodes);
        } else {
            this.g.selectAll("g.label-group").remove();
        }

        // Update simulation
        this.simulation.nodes(nodes).on("tick", () => this._ticked());
        this.simulation.force("link").links(links);
        this.simulation.alpha(0.3).restart();

        // Update label visibility
        setTimeout(() => this._updateLabelVisibility(), 0);
    }

    /**
     * Handle incremental updates (more efficient than full re-render)
     */
    handleUpdate(update) {
        const { state, operations } = update;

        // Animate operations
        if (operations && operations.length > 0) {
            operations.forEach(op => this._animateOperation(op));
        }

        // Full re-render for now (optimize later with targeted updates)
        this.render(state);
    }

    // ========================================================================
    // Visual Encodings
    // ========================================================================

    _getNodeEmoji(node) {
        const nodeType = (node.labels && node.labels[0]) || 'Node';
        const EMOJIS = {
            'Memory': '💭', 'Conversation': '💬', 'Person': '👤',
            'Relationship': '🤝', 'Personal_Goal': '🎯', 'Personal_Value': '💎',
            'Personal_Pattern': '🔄', 'Realization': '💡', 'Wound': '🩹',
            'default': '⚪'
        };
        return EMOJIS[nodeType] || EMOJIS['default'];
    }

    _getNodeSize(node) {
        const weight = this._computeNodeWeight(node);
        return Math.max(24, 16 + weight * 16);  // 24-32px
    }

    _getNodeGlowFilter(node, currentTime) {
        // Glow for recently active nodes
        const glow = this._getNodeGlow(node, currentTime);
        if (glow > 0) {
            return "drop-shadow(0 0 8px #5efc82) drop-shadow(0 0 4px #5efc82)";
        }
        // Selected node gets green outline
        if (this.selectedNode && node.id === this.selectedNode.id) {
            return "drop-shadow(0 0 6px #4CAF50) drop-shadow(0 0 3px #4CAF50)";
        }
        return "none";
    }

    _computeNodeWeight(node) {
        const arousal = node.arousal || 0;
        const confidence = node.confidence || 0.5;
        const traversalCount = node.traversal_count || 0;
        const normalizedTraversals = Math.min(1.0, Math.log10(traversalCount + 1) / 2);
        return (arousal * 0.4) + (confidence * 0.3) + (normalizedTraversals * 0.3);
    }

    _getNodeGlow(node, currentTime) {
        if (!node.last_active) return 0;
        const age = currentTime - node.last_active;
        const glowWindow = 5000; // 5 seconds
        return age < glowWindow ? (glowWindow - age) / glowWindow : 0;
    }

    _getLinkColor(link) {
        if (this.selectedEntity === 'structural') {
            // Type-based coloring
            const COLORS = {
                'JUSTIFIES': '#ef4444', 'BUILDS_TOWARD': '#3b82f6',
                'ENABLES': '#22c55e', 'USES': '#8b5cf6',
                'default': '#666'
            };
            return COLORS[link.type] || COLORS['default'];
        } else {
            // Valence-based coloring for selected entity
            const valences = link.sub_entity_valences || {};
            const valence = valences[this.selectedEntity];
            return this._getValenceColor(valence);
        }
    }

    _getValenceColor(valence) {
        if (valence === null || valence === undefined) return '#64748b';
        const normalized = (valence + 1.0) / 2.0;
        if (normalized < 0.5) {
            const t = normalized * 2;
            return d3.interpolateRgb('#ef4444', '#94a3b8')(t);  // Red to gray
        } else {
            const t = (normalized - 0.5) * 2;
            return d3.interpolateRgb('#94a3b8', '#22c55e')(t);  // Gray to green
        }
    }

    _getLinkOpacity(link, currentTime) {
        if (!link.last_traversed) return 0.3;
        const age = currentTime - link.last_traversed;
        return Math.max(0.2, 1 - (age / this.timeRange));
    }

    _getArrowMarker(link) {
        return this.selectedEntity !== 'structural'
            ? `url(#arrow-valence)`
            : `url(#arrow-${link.type || 'default'})`;
    }

    // ========================================================================
    // Interaction Helpers
    // ========================================================================

    _initializeInteractions() {
        // Zoom
        this.svg.call(d3.zoom()
            .scaleExtent([0.1, 10])
            .on("zoom", (event) => {
                this.g.attr("transform", event.transform);
                this.currentZoomScale = event.transform.k;
                this._updateLabelVisibility();
            }));

        // Mouse tracking
        this.svg.on("mousemove", (event) => {
            const [x, y] = d3.pointer(event, this.g.node());
            this.mouseX = x;
            this.mouseY = y;
            this._updateLabelVisibility();
        });

        // Click background to deselect
        this.svg.on("click", () => this.clearSelection());
    }

    _createDragBehavior() {
        return d3.drag()
            .on("start", (event) => {
                if (!event.active) this.simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            })
            .on("drag", (event) => {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            })
            .on("end", (event) => {
                if (!event.active) this.simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            });
    }

    _highlightNeighborhood(node) {
        const state = graphDataService.getState();
        const neighborIds = new Set([node.id]);

        state.links.forEach(l => {
            const sourceId = l.source.id || l.source;
            const targetId = l.target.id || l.target;
            if (sourceId === node.id) neighborIds.add(targetId);
            if (targetId === node.id) neighborIds.add(sourceId);
        });

        // Dim non-neighbors
        if (this.emojiElements) {
            this.emojiElements.style("opacity", d => neighborIds.has(d.id) ? 1.0 : 0.15);
        }

        // Highlight connecting links
        if (this.linkElements) {
            this.linkElements.attr("stroke-opacity", d => {
                const sourceId = d.source.id || d.source;
                const targetId = d.target.id || d.target;
                return (sourceId === node.id || targetId === node.id) ? 0.8 : 0.05;
            });
        }
    }

    _clearHighlight() {
        if (this.emojiElements) {
            this.emojiElements.style("opacity", 1.0);
        }
        if (this.linkElements) {
            const state = graphDataService.getState();
            this.linkElements.attr("stroke-opacity", d => this._getLinkOpacity(d, state.currentTime));
        }
    }

    _highlightConnectedLinks(node, links) {
        if (!this.linkElements) return;
        const state = graphDataService.getState();
        this.linkElements.attr("stroke-opacity", d => {
            const sourceId = d.source.id || d.source;
            const targetId = d.target.id || d.target;
            return (sourceId === node.id || targetId === node.id) ? 0.9 : this._getLinkOpacity(d, state.currentTime);
        });
    }

    _unhighlightConnectedLinks() {
        if (!this.linkElements) return;
        const state = graphDataService.getState();
        this.linkElements.attr("stroke-opacity", d => this._getLinkOpacity(d, state.currentTime));
    }

    _updateNodeSelection() {
        if (!this.emojiElements) return;
        const currentTime = graphDataService.getState().currentTime;
        this.emojiElements.style("filter", d => this._getNodeGlowFilter(d, currentTime));
    }

    // ========================================================================
    // Labels
    // ========================================================================

    _renderLabels(nodes) {
        const sortedNodes = [...nodes].sort((a, b) =>
            this._computeNodeWeight(a) - this._computeNodeWeight(b)
        );

        const labelGroups = this.g.selectAll("g.label-group")
            .data(sortedNodes, d => d.id)
            .join("g")
            .attr("class", "label-group")
            .style("pointer-events", "none")
            .style("opacity", 0);

        labelGroups.each((d, i, nodes) => {
            const group = d3.select(nodes[i]);
            const lines = this._wrapText(d.text, 20);
            group.selectAll("text").remove();

            const text = group.append("text")
                .attr("class", "label")
                .attr("x", 18)
                .attr("y", 0)
                .attr("font-size", 13)
                .attr("font-weight", 500)
                .attr("fill", "#e8e8e8")
                .style("text-shadow", "0 2px 8px rgba(0, 0, 0, 0.9)")
                .attr("transform", `scale(${1 / this.currentZoomScale})`);

            lines.forEach((line, i) => {
                text.append("tspan")
                    .attr("x", 18)
                    .attr("dy", i === 0 ? "-0.6em" : "1.1em")
                    .text(line);
            });
        });

        this.labelGroups = labelGroups;
    }

    _wrapText(text, maxChars) {
        if (!text) return [''];
        const words = text.split(/(\s+|_|-)/);
        const lines = [];
        let currentLine = '';

        for (let word of words) {
            if ((currentLine + word).length > maxChars && currentLine.length > 0) {
                lines.push(currentLine);
                currentLine = word;
            } else {
                currentLine += word;
            }
        }
        if (currentLine) lines.push(currentLine);
        return lines.slice(0, 3);
    }

    _updateLabelVisibility() {
        if (!this.showLabels || !this.labelGroups) return;
        const THRESHOLD = 150;

        this.labelGroups.each((d, i, nodes) => {
            if (!d.x || !d.y) return;
            const dx = d.x - this.mouseX;
            const dy = d.y - this.mouseY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const isNear = distance < THRESHOLD;

            d3.select(nodes[i])
                .style("opacity", isNear ? 1 : 0)
                .selectAll("text")
                .attr("transform", `scale(${1 / this.currentZoomScale})`);
        });
    }

    // ========================================================================
    // Animation
    // ========================================================================

    _ticked() {
        if (this.linkElements) {
            this.linkElements
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
        }

        if (this.emojiElements) {
            this.emojiElements
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }

        if (this.labelGroups) {
            this.labelGroups.attr("transform", d => `translate(${d.x},${d.y})`);
        }
    }

    _animateOperation(operation) {
        if (operation.type === 'entity_traversal') {
            // Pulse effect - implement later
        } else if (operation.type === 'hebbian_learning') {
            // Link glow - implement later
        } else if (operation.type === 'activation_increase') {
            // Ripple effect - implement later
        }
    }

    // ========================================================================
    // Filtering
    // ========================================================================

    _filterByTime(state) {
        const cutoffTime = state.currentTime - this.timeRange;

        if (this.showRecentOnly) {
            const activeNodes = state.nodes.filter(n =>
                n.last_active && n.last_active > cutoffTime
            );
            const activeNodeIds = new Set(activeNodes.map(n => n.id));
            const activeLinks = state.links.filter(l =>
                activeNodeIds.has(l.source.id || l.source) &&
                activeNodeIds.has(l.target.id || l.target)
            );
            return { nodes: activeNodes, links: activeLinks };
        }

        return { nodes: state.nodes, links: state.links };
    }

    // ========================================================================
    // Event Emission (for external components to subscribe)
    // ========================================================================

    _emitEvent(eventName, data) {
        const event = new CustomEvent(`visualization:${eventName}`, { detail: data });
        window.dispatchEvent(event);
    }
}

export { VisualizationService };
