/**
 * GraphDataService
 *
 * Manages WebSocket connection, graph state, and real-time updates.
 * Single source of truth for all consciousness substrate data.
 *
 * Author: Iris "The Aperture"
 * Purpose: Clean separation between data management and visualization
 */

class GraphDataService {
    constructor() {
        // Connection state
        this.ws = null;
        this.connected = false;
        this.currentGraphType = 'citizen';
        this.currentGraphId = null;

        // Graph data (state)
        this.nodes = [];
        this.links = [];
        this.entities = [];

        // Available graphs from server
        this.availableGraphs = {};

        // Subscribers for state changes
        this.subscribers = {
            connection: [],
            initialState: [],
            graphUpdate: [],
            error: []
        };

        // Time tracking
        this.currentTime = Date.now();
    }

    // ========================================================================
    // Public API
    // ========================================================================

    /**
     * Fetch available graphs from server
     */
    async fetchAvailableGraphs() {
        try {
            const response = await fetch('/api/graphs');
            this.availableGraphs = await response.json();
            return this.availableGraphs;
        } catch (error) {
            console.error('Error fetching graphs:', error);
            this._notifySubscribers('error', { message: 'Failed to fetch graphs', error });
            return { citizens: [], organizations: [], ecosystems: [] };
        }
    }

    /**
     * Connect to specific graph via WebSocket
     */
    connectToGraph(graphType, graphId) {
        if (!graphId) {
            console.error('No graph ID provided');
            return;
        }

        // Close existing connection
        if (this.ws) {
            this.ws.close();
        }

        this.currentGraphType = graphType;
        this.currentGraphId = graphId;

        // Establish WebSocket connection
        const wsUrl = `ws://${window.location.host}/ws/graph/${graphType}/${graphId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => this._handleOpen();
        this.ws.onmessage = (event) => this._handleMessage(event);
        this.ws.onerror = (error) => this._handleError(error);
        this.ws.onclose = () => this._handleClose();
    }

    /**
     * Subscribe to state changes
     * @param {string} event - 'connection', 'initialState', 'graphUpdate', 'error'
     * @param {function} callback - Called when event occurs
     */
    subscribe(event, callback) {
        if (this.subscribers[event]) {
            this.subscribers[event].push(callback);
        }
    }

    /**
     * Unsubscribe from state changes
     */
    unsubscribe(event, callback) {
        if (this.subscribers[event]) {
            const index = this.subscribers[event].indexOf(callback);
            if (index > -1) {
                this.subscribers[event].splice(index, 1);
            }
        }
    }

    /**
     * Get current graph state (immutable copy)
     */
    getState() {
        return {
            nodes: [...this.nodes],
            links: [...this.links],
            entities: [...this.entities],
            currentTime: this.currentTime,
            connected: this.connected,
            graphType: this.currentGraphType,
            graphId: this.currentGraphId
        };
    }

    /**
     * Get unique entity IDs from graph data
     */
    getEntityIds() {
        const entityIds = new Set();

        // From SubEntity nodes
        this.entities.forEach(e => {
            if (e.entity_id) entityIds.add(e.entity_id);
        });

        // From link valences
        this.links.forEach(link => {
            if (link.sub_entity_valences) {
                Object.keys(link.sub_entity_valences).forEach(id => entityIds.add(id));
            }
        });

        // From node activations
        this.nodes.forEach(node => {
            if (node.entity_activations) {
                Object.keys(node.entity_activations).forEach(id => entityIds.add(id));
            }
        });

        return Array.from(entityIds);
    }

    // ========================================================================
    // WebSocket Event Handlers
    // ========================================================================

    _handleOpen() {
        console.log('Connected to', this.currentGraphType, this.currentGraphId);
        this.connected = true;
        this._notifySubscribers('connection', {
            status: 'connected',
            graphType: this.currentGraphType,
            graphId: this.currentGraphId
        });
    }

    _handleMessage(event) {
        this.currentTime = Date.now();
        const message = JSON.parse(event.data);

        if (message.type === 'initial_state') {
            // Full state load
            this.nodes = message.data.nodes || [];
            this.links = message.data.links || [];
            this.entities = message.data.entities || [];

            this._notifySubscribers('initialState', this.getState());
        }
        else if (message.type === 'graph_update') {
            // Incremental update
            this._applyDiff(message.diff);

            this._notifySubscribers('graphUpdate', {
                state: this.getState(),
                operations: message.operations || [],
                timestamp: message.timestamp
            });
        }
        else if (message.type === 'error') {
            console.error('Server error:', message.message);
            this._notifySubscribers('error', { message: message.message });
        }
    }

    _handleError(error) {
        console.error('WebSocket error:', error);
        this.connected = false;
        this._notifySubscribers('connection', { status: 'error' });
        this._notifySubscribers('error', { message: 'WebSocket error', error });
    }

    _handleClose() {
        console.log('WebSocket closed');
        this.connected = false;
        this._notifySubscribers('connection', { status: 'disconnected' });
    }

    // ========================================================================
    // Internal State Management
    // ========================================================================

    /**
     * Apply incremental diff to current state
     */
    _applyDiff(diff) {
        // Add new nodes
        if (diff.nodes_added) {
            this.nodes.push(...diff.nodes_added);
        }

        // Update existing nodes
        if (diff.nodes_updated) {
            diff.nodes_updated.forEach(updated => {
                const index = this.nodes.findIndex(n => n.id === updated.id);
                if (index !== -1) {
                    this.nodes[index] = updated;
                }
            });
        }

        // Add new links
        if (diff.links_added) {
            this.links.push(...diff.links_added);
        }

        // Update existing links
        if (diff.links_updated) {
            diff.links_updated.forEach(updated => {
                const index = this.links.findIndex(l => l.id === updated.id);
                if (index !== -1) {
                    this.links[index] = updated;
                }
            });
        }
    }

    /**
     * Notify all subscribers of an event
     */
    _notifySubscribers(event, data) {
        if (this.subscribers[event]) {
            this.subscribers[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in ${event} subscriber:`, error);
                }
            });
        }
    }
}

// Export singleton instance
export const graphDataService = new GraphDataService();
