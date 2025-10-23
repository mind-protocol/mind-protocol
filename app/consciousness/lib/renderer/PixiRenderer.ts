/**
 * PixiRenderer - WebGL graph renderer using PixiJS
 *
 * Day 1 POC: Render 2500+ nodes and 1000+ links at 60fps
 * - Instanced sprites for nodes
 * - Batched lines for links
 * - Color-picking for hit detection
 *
 * Architecture:
 * - Separate containers for links (bottom) and nodes (top)
 * - Color-picking FBO for efficient hit testing
 * - Camera via Container transform (will add proper camera later)
 */

import * as PIXI from 'pixi.js';
import * as d3 from 'd3';
import {
  RendererAdapter,
  ViewModel,
  CameraState,
  PickResult,
  RendererStats,
  RendererConfig,
  NodeData,
  LinkData,
} from './types';

// Node emoji map (same as SVG version)
const NODE_TYPE_EMOJI: Record<string, string> = {
  Realization: '💡',
  Principle: '🎯',
  Mechanism: '⚙️',
  Concept: '💭',
  Personal_Goal: '🎯',
  Personal_Pattern: '🔄',
  Coping_Mechanism: '🛡️',
  Best_Practice: '✅',
  Anti_Pattern: '⚠️',
  Decision: '🔱',
  Code: '📜',
  Documentation: '📖',
  Process: '🔄',
  Team: '👥',
  Person: '👤',
  Relationship: '🤝',
  Memory: '📸',
  // ... add more as needed
};

// Subentity colors (from constants)
const ENTITY_COLORS: Record<string, number> = {
  default: 0x64748b,    // slate-500
  validator: 0x3b82f6,  // blue-500
  architect: 0x8b5cf6,  // purple-500
  translator: 0x06b6d4, // cyan-500
  // ... add more subentities
};

export class PixiRenderer implements RendererAdapter {
  private app: PIXI.Application;
  private mounted = false;

  // Scene containers
  private worldContainer!: PIXI.Container;
  private linksContainer!: PIXI.Container;
  private nodesContainer!: PIXI.Container;
  private entitiesContainer!: PIXI.Container;  // Subentity nodes (collapsed layer)
  private entityBoundariesContainer!: PIXI.Container;  // RELATES_TO edges

  // Data
  private viewModel: ViewModel = {
    nodes: [],
    links: [],
    subentities: [],
    operations: [],
  };

  // Subentity caches (from WebSocket)
  private entityCache = new Map<string, any>();
  private entityBoundaryCache = new Map<string, any>();
  private expandedSubentities = new Set<string>();

  // Camera state
  private camera: CameraState = {
    x: 0,
    y: 0,
    scale: 1,
  };

  // Pick rendering (color-coded FBO)
  private pickRenderTexture: PIXI.RenderTexture | null = null;
  private pickContainer: PIXI.Container | null = null;
  private pickNodeMap = new Map<number, NodeData>(); // color -> node
  private pickLinkMap = new Map<number, LinkData>(); // color -> link

  // Performance tracking
  private stats = {
    fps: 0,
    frameTime: 0,
    drawCalls: 0,
    nodeCount: 0,
    linkCount: 0,
  };

  private lastFrameTime = performance.now();
  private frameCount = 0;

  // Event handlers (for cleanup)
  private containerElement: HTMLElement | null = null;
  private eventHandlers: {
    pointerdown?: (e: PointerEvent) => void;
    pointermove?: (e: PointerEvent) => void;
    pointerup?: () => void;
    wheel?: (e: WheelEvent) => void;
  } = {};

  // D3 force simulation for dynamic layout
  private simulation: d3.Simulation<NodeData, LinkData> | null = null;
  private needsRedraw = false;

  // Visual effects containers
  private flashContainer: PIXI.Container | null = null;
  private linkCurrentContainer: PIXI.Container | null = null;
  private trailContainer: PIXI.Container | null = null;

  // Animation tracking
  private activeFlashes: Map<string, { graphics: PIXI.Graphics; startTime: number }> = new Map();
  private activeLinkCurrents: Map<string, { graphics: PIXI.Graphics; phase: number }> = new Map();
  private trailSegments: Array<{ from: string; to: string; startTime: number; graphics: PIXI.Graphics }> = [];

  constructor(private config: RendererConfig = {}) {
    // Application will be created in mount()
    this.app = null as any;
  }

  async mount(container: HTMLElement): Promise<void> {
    if (this.mounted) return;

    // Initialize PixiJS (v7 pattern - no async init)
    this.app = new PIXI.Application({
      width: container.clientWidth,
      height: container.clientHeight,
      backgroundColor: 0x1e40af, // Deep blue-800 (darker, correct shade)
      resolution: window.devicePixelRatio || 1,
      autoDensity: true,
      antialias: true,
    });

    container.appendChild(this.app.view as HTMLCanvasElement);

    // Create scene hierarchy
    this.worldContainer = new PIXI.Container();
    this.entityBoundariesContainer = new PIXI.Container();  // Subentity RELATES_TO edges (bottom)
    this.entitiesContainer = new PIXI.Container();  // Subentity nodes (middle)
    this.linksContainer = new PIXI.Container();  // Node links (when expanded)
    this.trailContainer = new PIXI.Container();  // Trail effects (above links)
    this.linkCurrentContainer = new PIXI.Container();  // Link current effects (above trails)
    this.nodesContainer = new PIXI.Container();  // Nodes (when expanded)
    this.flashContainer = new PIXI.Container();  // Flash effects (top - most visible)

    this.worldContainer.addChild(this.entityBoundariesContainer);
    this.worldContainer.addChild(this.entitiesContainer);
    this.worldContainer.addChild(this.linksContainer);
    this.worldContainer.addChild(this.trailContainer);
    this.worldContainer.addChild(this.linkCurrentContainer);
    this.worldContainer.addChild(this.nodesContainer);
    this.worldContainer.addChild(this.flashContainer);
    this.app.stage.addChild(this.worldContainer);

    // Create pick render texture (for hit testing)
    this.pickRenderTexture = PIXI.RenderTexture.create({
      width: this.app.screen.width,
      height: this.app.screen.height,
    });
    this.pickContainer = new PIXI.Container();

    // Setup camera (pan/zoom via pointer events)
    this.setupCamera(container);

    // Start render loop
    this.app.ticker.add(this.onTick, this);

    this.mounted = true;
    console.log('[PixiRenderer] Mounted successfully');
  }

  unmount(): void {
    if (!this.mounted) return;

    // Stop force simulation
    if (this.simulation) {
      this.simulation.stop();
      this.simulation = null;
    }

    // Remove event listeners
    if (this.containerElement) {
      if (this.eventHandlers.pointerdown) {
        this.containerElement.removeEventListener('pointerdown', this.eventHandlers.pointerdown);
      }
      if (this.eventHandlers.pointermove) {
        this.containerElement.removeEventListener('pointermove', this.eventHandlers.pointermove);
      }
      if (this.eventHandlers.pointerup) {
        this.containerElement.removeEventListener('pointerup', this.eventHandlers.pointerup);
      }
      if (this.eventHandlers.wheel) {
        this.containerElement.removeEventListener('wheel', this.eventHandlers.wheel);
      }
    }

    this.app.ticker.remove(this.onTick, this);
    this.app.destroy(true, {
      children: true,
      texture: true,
      baseTexture: true,
    });

    this.pickRenderTexture?.destroy(true);
    this.pickContainer?.destroy({ children: true });

    this.containerElement = null;
    this.eventHandlers = {};
    this.mounted = false;
    console.log('[PixiRenderer] Unmounted');
  }

  setCamera(camera: CameraState): void {
    this.camera = { ...camera };
    this.updateCameraTransform();
  }

  getCamera(): CameraState {
    return { ...this.camera };
  }

  setData(viewModel: ViewModel): void {
    this.viewModel = viewModel;
    this.stats.nodeCount = viewModel.nodes.length;
    this.stats.linkCount = viewModel.links.length;

    // Stop previous simulation
    if (this.simulation) {
      this.simulation.stop();
    }

    // Create D3 force simulation (matching GraphCanvas.tsx)
    const nodeCount = viewModel.nodes.length;
    const chargeStrength = nodeCount > 500 ? -150 : nodeCount > 100 ? -200 : -300;
    const collisionIterations = nodeCount > 500 ? 1 : nodeCount > 100 ? 1 : 2;
    const linkIterations = nodeCount > 500 ? 1 : 2;

    // Filter valid links (non-null source/target)
    const validLinks = viewModel.links.filter(l => {
      const source = viewModel.nodes.find(n => n.id === l.source);
      const target = viewModel.nodes.find(n => n.id === l.target);
      return source && target;
    });

    // Get viewport dimensions for force positioning
    const width = this.app.screen.width;
    const height = this.app.screen.height;

    this.simulation = d3.forceSimulation(viewModel.nodes as any)
      .force('link', d3.forceLink(validLinks as any)
        .id((d: any) => d.id)
        .distance(50) // REDUCED from 100 - nodes closer together
        .iterations(linkIterations))
      .force('charge', d3.forceManyBody().strength(chargeStrength))
      .force('center', d3.forceCenter(0, 0)) // Center at world origin
      .force('collision', d3.forceCollide().radius(25).iterations(collisionIterations)) // REDUCED from 40
      .force('temporal', this.forceTemporalY(height))  // Recent nodes → top (layers of thinking)
      .force('semantic', this.forceSemanticX(width))   // Semantic domains → horizontal spread
      .alphaDecay(0.02) // Slower decay for smoother animation
      .on('tick', () => {
        this.needsRedraw = true;
      }) as any;

    // Initial rebuild
    this.rebuildScene();
  }

  pick(screenX: number, screenY: number): PickResult {
    // Render pick scene to texture with unique colors
    this.renderPickScene();

    // Read pixel at cursor position
    const pickColor = this.readPickPixel(screenX, screenY);

    // Look up node/link by color
    const node = this.pickNodeMap.get(pickColor);
    if (node) {
      return {
        type: 'node',
        id: node.id,
        data: node,
        screenX,
        screenY,
        worldX: (screenX - this.camera.x) / this.camera.scale,
        worldY: (screenY - this.camera.y) / this.camera.scale,
      };
    }

    const link = this.pickLinkMap.get(pickColor);
    if (link) {
      return {
        type: 'link',
        id: link.id,
        data: link,
        screenX,
        screenY,
        worldX: (screenX - this.camera.x) / this.camera.scale,
        worldY: (screenY - this.camera.y) / this.camera.scale,
      };
    }

    return {
      type: 'none',
      screenX,
      screenY,
      worldX: (screenX - this.camera.x) / this.camera.scale,
      worldY: (screenY - this.camera.y) / this.camera.scale,
    };
  }

  resize(width: number, height: number): void {
    this.app.renderer.resize(width, height);

    // Recreate pick texture at new size
    this.pickRenderTexture?.destroy(true);
    this.pickRenderTexture = PIXI.RenderTexture.create({ width, height });
  }

  getStats(): RendererStats {
    return { ...this.stats };
  }

  // ========================================================================
  // Custom D3 Forces (Temporal & Semantic Layout)
  // ========================================================================

  /**
   * Temporal force: Pull nodes top-to-bottom based on last_active/created_at
   * Like layers of thinking stacking up over time
   * Recent nodes → top (floating)
   * Old nodes → bottom (settled)
   */
  private forceTemporalY(height: number) {
    let nodes: NodeData[];

    function force(alpha: number) {
      if (!nodes) return;

      const now = Date.now();
      // Find oldest and newest timestamps
      const timestamps = nodes
        .map(n => n.last_active || (n as any).created_at || 0)
        .filter(t => t > 0);

      if (timestamps.length === 0) return;

      const minTime = Math.min(...timestamps);
      const maxTime = Math.max(...timestamps);
      const timeRange = maxTime - minTime;

      // FALLBACK: If timestamps are uniform (seed data), disable temporal force
      // Range less than 1 hour = likely bulk-imported seed data
      if (timeRange < 3600000) {
        return; // Let other forces handle layout
      }

      // Pull nodes top-to-bottom based on temporal position
      nodes.forEach((node: any) => {
        const nodeTime = node.last_active || node.created_at || minTime;
        const timePos = (nodeTime - minTime) / timeRange; // 0 (old) to 1 (recent)

        // Target Y position: recent on top (negative Y), old at bottom (positive Y)
        // Centered around 0 (world origin)
        const targetY = (0.5 - timePos) * height * 0.5; // Recent → top

        // Apply very gentle force toward target position (much weaker)
        const dy = targetY - node.y;
        node.vy += dy * alpha * 0.01; // Very gentle 1% strength (was 5%)
      });
    }

    force.initialize = function(_: any) {
      nodes = _;
    };

    return force;
  }

  /**
   * Semantic force: Pull nodes left/right based on semantic domain
   * Different areas of thinking spread horizontally for natural clustering
   * Uses node_type and entity_id to determine semantic polarity
   */
  private forceSemanticX(width: number) {
    let nodes: NodeData[];

    function force(alpha: number) {
      if (!nodes) return;

      // Pull nodes left/right based on semantic domain
      nodes.forEach((node: any) => {
        const semanticPolarity = computeSemanticPolarity(node);

        // Target X position: spread semantic domains horizontally
        // Polarity ranges from -1 (left) to +1 (right)
        // Centered around 0 (world origin)
        const targetX = semanticPolarity * width * 0.4;

        // Apply very gentle force toward target position (much weaker)
        const dx = targetX - node.x;
        node.vx += dx * alpha * 0.01; // Very gentle 1% strength (was 5%)
      });
    }

    force.initialize = function(_: any) {
      nodes = _;
    };

    return force;
  }

  // ========================================================================
  // Private Methods
  // ========================================================================

  private setupCamera(container: HTMLElement): void {
    this.containerElement = container;
    let isDragging = false;
    let lastX = 0;
    let lastY = 0;

    // Pan on drag
    this.eventHandlers.pointerdown = (e: PointerEvent) => {
      isDragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
    };

    this.eventHandlers.pointermove = (e: PointerEvent) => {
      if (!isDragging) return;

      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;

      this.camera.x += dx;
      this.camera.y += dy;

      lastX = e.clientX;
      lastY = e.clientY;

      this.updateCameraTransform();
    };

    this.eventHandlers.pointerup = () => {
      isDragging = false;
    };

    // Zoom on wheel (smoother sensitivity to match D3)
    this.eventHandlers.wheel = (e: WheelEvent) => {
      e.preventDefault();

      // Much smoother zoom delta (was 1.1/0.9, now 1.02/0.98)
      const zoomDelta = e.deltaY < 0 ? 1.02 : 0.98;
      const newScale = this.camera.scale * zoomDelta;

      // Clamp scale to [0.3, 4] to match D3 zoom
      this.camera.scale = Math.max(0.3, Math.min(4, newScale));

      this.updateCameraTransform();
    };

    // Attach event listeners
    container.addEventListener('pointerdown', this.eventHandlers.pointerdown);
    container.addEventListener('pointermove', this.eventHandlers.pointermove);
    container.addEventListener('pointerup', this.eventHandlers.pointerup);
    container.addEventListener('wheel', this.eventHandlers.wheel);

    // Center camera initially (zoomed to see full graph)
    this.camera.x = this.app.screen.width / 2;
    this.camera.y = this.app.screen.height / 2;
    this.camera.scale = 1.0; // Start at 1:1 zoom so graph is visible
    this.updateCameraTransform();
  }

  private updateCameraTransform(): void {
    if (!this.worldContainer) return;
    this.worldContainer.position.set(this.camera.x, this.camera.y);
    this.worldContainer.scale.set(this.camera.scale);
  }

  private rebuildScene(): void {
    // Clear existing
    this.linksContainer.removeChildren();
    this.nodesContainer.removeChildren();

    // Ensure all nodes have positions (random if missing - will use D3 layout later)
    this.ensureNodePositions();

    // Rebuild links (batched lines)
    this.buildLinks();

    // Rebuild nodes (text sprites with emoji)
    this.buildNodes();

    // Rebuild pick scene
    this.buildPickScene();
  }

  private ensureNodePositions(): void {
    // Give nodes random positions if they don't have x/y
    // TODO: Replace with D3 force layout or Venice tile positions
    const width = this.app.screen.width;
    const height = this.app.screen.height;

    let nodesWithoutPos = 0;
    this.viewModel.nodes.forEach((node) => {
      if (node.x === undefined || node.y === undefined) {
        nodesWithoutPos++;
        // Circular layout for now (looks better than pure random)
        const index = this.viewModel.nodes.indexOf(node);
        const total = this.viewModel.nodes.length;
        const angle = (index / total) * Math.PI * 2;
        const radius = Math.min(width, height) * 0.4; // LARGE radius so graph is visible!

        node.x = Math.cos(angle) * radius;
        node.y = Math.sin(angle) * radius;
      }
    });

    if (nodesWithoutPos > 0) {
      console.log('[PixiRenderer] Assigned positions to', nodesWithoutPos, 'nodes. First node:', this.viewModel.nodes[0]?.id, 'at', this.viewModel.nodes[0]?.x, this.viewModel.nodes[0]?.y);
    }
  }

  private buildLinks(): void {
    let linksDrawn = 0;
    let linksSkippedNoNodes = 0;
    let linksSkippedInvalidPos = 0;

    console.log('[PixiRenderer.buildLinks] START - Total links:', this.viewModel.links.length, 'linksContainer children before clear:', this.linksContainer.children.length);

    this.viewModel.links.forEach((link, index) => {
      // Handle both string IDs and D3 object references
      // After D3 runs, it mutates link.source/target from strings to object refs
      let sourceNode: NodeData | undefined;
      let targetNode: NodeData | undefined;

      // Try to find source node
      if (typeof link.source === 'string') {
        sourceNode = this.viewModel.nodes.find((n) => n.id === link.source);
      } else if (link.source && typeof link.source === 'object') {
        // D3 has mutated this to an object - find it by ID
        const sourceId = (link.source as any).id;
        sourceNode = this.viewModel.nodes.find((n) => n.id === sourceId);
      }

      // Try to find target node
      if (typeof link.target === 'string') {
        targetNode = this.viewModel.nodes.find((n) => n.id === link.target);
      } else if (link.target && typeof link.target === 'object') {
        // D3 has mutated this to an object - find it by ID
        const targetId = (link.target as any).id;
        targetNode = this.viewModel.nodes.find((n) => n.id === targetId);
      }

      if (!sourceNode || !targetNode) {
        linksSkippedNoNodes++;
        if (index < 5) { // Log first 5 failures for debugging
          console.warn('[PixiRenderer] Link skipped - nodes not found:', {
            linkIndex: index,
            sourceType: typeof link.source,
            targetType: typeof link.target,
            sourceValue: typeof link.source === 'string' ? link.source : (link.source as any)?.id,
            targetValue: typeof link.target === 'string' ? link.target : (link.target as any)?.id,
          });
        }
        return;
      }

      // Use stored positions or default to center
      const sx = sourceNode.x ?? 0;
      const sy = sourceNode.y ?? 0;
      const tx = targetNode.x ?? 0;
      const ty = targetNode.y ?? 0;

      // Skip if positions are invalid
      if (!isFinite(sx) || !isFinite(sy) || !isFinite(tx) || !isFinite(ty)) {
        linksSkippedInvalidPos++;
        if (linksSkippedInvalidPos <= 3) {
          console.warn('[PixiRenderer] Invalid link positions:', { sx, sy, tx, ty, sourceId: sourceNode.id, targetId: targetNode.id });
        }
        return;
      }

      // Link color based on type
      const color = this.getLinkColor(link);
      const alpha = link.created_at && Date.now() - link.created_at < 10000 ? 0.9 : 0.8;
      const thickness = this.getLinkThickness(link);

      // Create separate Graphics for each link (better for batching)
      const graphics = new PIXI.Graphics();

      // Draw line (PixiJS v7 API)
      graphics.lineStyle(thickness, color, alpha);
      graphics.moveTo(sx, sy);
      graphics.lineTo(tx, ty);

      // Draw arrowhead at target
      const dx = tx - sx;
      const dy = ty - sy;
      const length = Math.sqrt(dx * dx + dy * dy);

      if (length > 5) { // Only draw arrow if link is long enough
        const angle = Math.atan2(dy, dx);
        const arrowSize = thickness * 3;

        // Arrow triangle
        const arrowTip = { x: tx, y: ty };
        const arrowLeft = {
          x: tx - arrowSize * Math.cos(angle - Math.PI / 6),
          y: ty - arrowSize * Math.sin(angle - Math.PI / 6)
        };
        const arrowRight = {
          x: tx - arrowSize * Math.cos(angle + Math.PI / 6),
          y: ty - arrowSize * Math.sin(angle + Math.PI / 6)
        };

        graphics.beginFill(color, alpha);
        graphics.drawPolygon([
          arrowTip.x, arrowTip.y,
          arrowLeft.x, arrowLeft.y,
          arrowRight.x, arrowRight.y
        ]);
        graphics.endFill();
      }

      this.linksContainer.addChild(graphics);
      linksDrawn++;
    });

    // Summary logging (only log if there were issues)
    const totalLinks = this.viewModel.links.length;
    if (linksSkippedNoNodes > 0 || linksSkippedInvalidPos > 0) {
      console.warn(`[PixiRenderer] Link rendering issues:`, {
        total: totalLinks,
        drawn: linksDrawn,
        skippedNoNodes: linksSkippedNoNodes,
        skippedInvalidPos: linksSkippedInvalidPos
      });
    }

    console.log('[PixiRenderer.buildLinks] COMPLETE - linksDrawn:', linksDrawn, 'linksContainer.children.length:', this.linksContainer.children.length, 'linksContainer.visible:', this.linksContainer.visible, 'linksContainer.alpha:', this.linksContainer.alpha);

    if (linksDrawn === 0 && totalLinks > 0) {
      console.error(`[PixiRenderer] CRITICAL: No links drawn! Check node positions and link source/target resolution.`);
      console.log('[PixiRenderer] First link for debugging:', this.viewModel.links[0]);
      console.log('[PixiRenderer] First node for debugging:', this.viewModel.nodes[0]);
    }

    // Force linksContainer to be visible
    this.linksContainer.visible = true;
    this.linksContainer.alpha = 1.0;
  }

  private buildNodes(): void {
    const workingMemory = this.viewModel.workingMemory || new Set<string>();

    this.viewModel.nodes.forEach((node) => {
      const emoji = this.getNodeEmoji(node);
      const size = this.getNodeSize(node);
      const color = this.getNodeColor(node);
      const isInWorkingMemory = workingMemory.has(node.id);

      // Draw glow circle behind node if in working memory
      if (isInWorkingMemory) {
        const glowRadius = size / 2 + 8; // Glow extends 8px beyond node
        const glow = new PIXI.Graphics();

        // Outer glow ring (cyan/white gradient effect using multiple circles)
        glow.beginFill(0x00FFFF, 0.15); // Very subtle cyan outer
        glow.drawCircle(0, 0, glowRadius + 4);
        glow.endFill();

        glow.beginFill(0x00FFFF, 0.25); // Medium cyan middle
        glow.drawCircle(0, 0, glowRadius);
        glow.endFill();

        glow.beginFill(0xFFFFFF, 0.35); // Brighter white inner
        glow.drawCircle(0, 0, glowRadius - 4);
        glow.endFill();

        glow.position.set(node.x ?? 0, node.y ?? 0);
        this.nodesContainer.addChild(glow);

        // Store reference for fade-out animation (future enhancement)
        (glow as any).__nodeId = node.id;
      }

      // Create text sprite (PixiJS v7 API)
      const text = new PIXI.Text(emoji, {
        fontSize: size,
        fill: color,
      });

      text.anchor.set(0.5);
      text.position.set(node.x ?? 0, node.y ?? 0);

      // Store node reference for picking
      text.eventMode = 'static';
      text.cursor = 'pointer';
      (text as any).__nodeData = node;

      this.nodesContainer.addChild(text);
    });
  }

  private buildPickScene(): void {
    if (!this.pickContainer) return;

    this.pickContainer.removeChildren();
    this.pickNodeMap.clear();
    this.pickLinkMap.clear();

    let colorIndex = 1; // 0 = background

    // Render nodes with unique colors
    this.viewModel.nodes.forEach((node) => {
      const color = colorIndex++;
      this.pickNodeMap.set(color, node);

      const circle = new PIXI.Graphics();
      circle.beginFill(color);
      circle.drawCircle(0, 0, this.getNodeSize(node) / 2);
      circle.endFill();
      circle.position.set(node.x ?? 0, node.y ?? 0);

      this.pickContainer!.addChild(circle);
    });

    // Render links with unique colors
    this.viewModel.links.forEach((link) => {
      // Handle both string IDs and D3 object references
      const sourceNode = this.viewModel.nodes.find((n) =>
        n.id === link.source || n === link.source
      );
      const targetNode = this.viewModel.nodes.find((n) =>
        n.id === link.target || n === link.target
      );

      if (!sourceNode || !targetNode) return;

      const color = colorIndex++;
      this.pickLinkMap.set(color, link);

      const line = new PIXI.Graphics();
      line.lineStyle(this.getLinkThickness(link) + 4, color); // Thicker for easier picking
      line.moveTo(sourceNode.x ?? 0, sourceNode.y ?? 0);
      line.lineTo(targetNode.x ?? 0, targetNode.y ?? 0);

      this.pickContainer!.addChild(line);
    });
  }

  private renderPickScene(): void {
    if (!this.pickContainer || !this.pickRenderTexture) return;

    // Match world transform
    this.pickContainer.position.copyFrom(this.worldContainer.position);
    this.pickContainer.scale.copyFrom(this.worldContainer.scale);

    // Render to texture (PixiJS v7 API)
    this.app.renderer.render(this.pickContainer, { renderTexture: this.pickRenderTexture });
  }

  private readPickPixel(x: number, y: number): number {
    if (!this.pickRenderTexture) return 0;

    // PixiJS v7 API: extract.pixels() reads entire texture
    // For POC, we'll use a simpler approach - TODO: optimize for Day 2
    try {
      const pixels = this.app.renderer.plugins.extract.pixels(this.pickRenderTexture);
      const width = this.pickRenderTexture.width;

      // Calculate pixel index (RGBA = 4 bytes per pixel)
      const index = (Math.floor(y) * width + Math.floor(x)) * 4;

      // Convert RGBA to single color value
      return (pixels[index] << 16) | (pixels[index + 1] << 8) | pixels[index + 2];
    } catch (err) {
      console.warn('[PixiRenderer] Pick pixel read failed:', err);
      return 0;
    }
  }

  private onTick = (): void => {
    // Update stats
    this.frameCount++;
    const now = performance.now();
    const elapsed = now - this.lastFrameTime;

    if (elapsed >= 1000) {
      this.stats.fps = Math.round((this.frameCount * 1000) / elapsed);
      this.stats.frameTime = this.app.ticker.deltaMS;
      this.frameCount = 0;
      this.lastFrameTime = now;
    }

    // Redraw scene if force simulation updated positions
    if (this.needsRedraw) {
      this.updateNodeAndLinkPositions();
      this.needsRedraw = false;
    }

    // Animate visual effects
    this.animateFlashes(now);
    this.animateLinkCurrents(now);
    this.animateTrails(now);

    // Log stats if enabled
    if (this.config.showStats && this.frameCount % 60 === 0) {
      console.log(`[PixiRenderer] FPS: ${this.stats.fps}, Frame: ${this.stats.frameTime.toFixed(2)}ms, Nodes: ${this.stats.nodeCount}, Links: ${this.stats.linkCount}`);
    }
  };

  /**
   * Update node and link positions from force simulation
   * More efficient than full rebuild - just updates transforms
   */
  private updateNodeAndLinkPositions(): void {
    // Update node positions
    this.nodesContainer.children.forEach((child, i) => {
      const node = this.viewModel.nodes[i];
      if (node && node.x !== undefined && node.y !== undefined) {
        child.position.set(node.x, node.y);
      }
    });

    // Rebuild links (necessary because lines can't be transformed easily)
    this.linksContainer.removeChildren();
    this.buildLinks();

    // Update pick scene
    this.buildPickScene();
  }

  // ========================================================================
  // Visual Helpers (match SVG version)
  // ========================================================================

  private getNodeEmoji(node: NodeData): string {
    return NODE_TYPE_EMOJI[node.node_type] || '⚪';
  }

  private getNodeSize(node: NodeData): number {
    const baseSize = 48; // INCREASED from 32 - larger nodes
    const weight = node.weight ?? 0.5;
    const energy = typeof node.energy === 'number' ? node.energy : 0;
    const traversals = Math.min((node.traversal_count ?? 0) / 10, 1);

    return baseSize * (0.8 + weight * 0.4 + energy * 0.3 + traversals * 0.3);
  }

  private getNodeColor(node: NodeData): number {
    // Check for active subentity
    if (node.entity_activations) {
      const entries = Object.entries(node.entity_activations);
      if (entries.length > 0) {
        const [entityId] = entries[0];
        return ENTITY_COLORS[entityId] ?? ENTITY_COLORS.default;
      }
    }

    return 0xffffff; // White by default
  }

  private getLinkColor(link: LinkData): number {
    // BRIGHT colors for maximum visibility
    const typeColors: Record<string, number> = {
      JUSTIFIES: 0x22ff88,   // bright green
      ENABLES: 0x66aaff,     // bright blue
      BLOCKS: 0xff4466,      // bright red
      RELATES_TO: 0xcccccc,  // bright gray/white
    };

    return typeColors[link.type ?? 'RELATES_TO'] ?? 0xffffff; // default white
  }

  private getLinkThickness(link: LinkData): number {
    return 4; // THICK constant width for visibility testing
  }

  // ========================================================================
  // Visual Effects Animation
  // ========================================================================

  /**
   * Animate threshold crossing flashes
   * Flashes appear when nodes cross activation threshold (node.flip events)
   */
  private animateFlashes(now: number): void {
    if (!this.flashContainer) return;

    const FLASH_DURATION = 500; // 500ms flash duration

    // Trigger new flashes for recent threshold crossings
    const recentFlips = this.viewModel.recentFlips || [];
    for (const flip of recentFlips) {
      // Only flash nodes crossing "on" (activation)
      if (flip.direction === 'on' && !this.activeFlashes.has(flip.node_id)) {
        this.createFlash(flip.node_id, now);
      }
    }

    // Animate existing flashes
    for (const [nodeId, flash] of this.activeFlashes.entries()) {
      const elapsed = now - flash.startTime;
      const progress = elapsed / FLASH_DURATION;

      if (progress >= 1) {
        // Flash complete - remove
        this.flashContainer.removeChild(flash.graphics);
        this.activeFlashes.delete(nodeId);
      } else {
        // Animate flash (fade out with expanding ring)
        const alpha = 1 - progress;
        const scale = 1 + progress * 0.5;

        flash.graphics.alpha = alpha;
        flash.graphics.scale.set(scale);
      }
    }
  }

  /**
   * Create a flash effect on a node
   */
  private createFlash(nodeId: string, now: number): void {
    if (!this.flashContainer) return;

    const node = this.viewModel.nodes.find(n => n.id === nodeId);
    if (!node || !node.x || !node.y) return;

    const graphics = new PIXI.Graphics();

    // Initial flash ring (bright white/yellow)
    graphics.beginFill(0xFFFF00, 0.8); // Yellow flash
    graphics.drawCircle(0, 0, this.getNodeSize(node) / 2 + 12);
    graphics.endFill();

    graphics.position.set(node.x, node.y);
    this.flashContainer.addChild(graphics);

    this.activeFlashes.set(nodeId, { graphics, startTime: now });
  }

  /**
   * Animate link current effects
   * Wave/pulse animation showing energy flow along active links
   */
  private animateLinkCurrents(now: number): void {
    if (!this.linkCurrentContainer) return;

    const linkFlows = this.viewModel.linkFlows || new Map<string, number>();

    // Update existing currents
    for (const [linkId, current] of this.activeLinkCurrents.entries()) {
      const flowCount = linkFlows.get(linkId) || 0;

      if (flowCount === 0) {
        // Link no longer active - remove current effect
        this.linkCurrentContainer.removeChild(current.graphics);
        this.activeLinkCurrents.delete(linkId);
      } else {
        // Animate wave phase (continuous wave motion)
        current.phase = (current.phase + 0.05) % 1; // Increment phase for wave motion
        this.updateLinkCurrentGraphics(current.graphics, linkId, current.phase, flowCount);
      }
    }

    // Add new currents for newly active links
    for (const [linkId, count] of linkFlows.entries()) {
      if (!this.activeLinkCurrents.has(linkId) && count > 0) {
        const graphics = new PIXI.Graphics();
        this.linkCurrentContainer.addChild(graphics);
        this.activeLinkCurrents.set(linkId, { graphics, phase: 0 });
        this.updateLinkCurrentGraphics(graphics, linkId, 0, count);
      }
    }
  }

  /**
   * Update link current graphics with wave effect
   */
  private updateLinkCurrentGraphics(graphics: PIXI.Graphics, linkId: string, phase: number, intensity: number): void {
    graphics.clear();

    // Find the link
    const link = this.viewModel.links.find(l => l.id === linkId);
    if (!link) return;

    // Find source and target nodes
    const sourceNode = this.viewModel.nodes.find(n => n.id === link.source || (typeof link.source === 'object' && n === link.source));
    const targetNode = this.viewModel.nodes.find(n => n.id === link.target || (typeof link.target === 'object' && n === link.target));

    if (!sourceNode || !targetNode || !sourceNode.x || !sourceNode.y || !targetNode.x || !targetNode.y) return;

    // Draw pulsing wave along link (like electrical current)
    const numWaves = 3; // 3 waves traveling along the link
    const waveLength = 1 / numWaves;

    for (let i = 0; i < numWaves; i++) {
      const wavePhase = (phase + i * waveLength) % 1;
      const x = sourceNode.x + (targetNode.x - sourceNode.x) * wavePhase;
      const y = sourceNode.y + (targetNode.y - sourceNode.y) * wavePhase;

      // Pulsing glow effect (cyan with intensity based on flow count)
      const alpha = 0.4 + intensity * 0.1; // More intense = more visible
      const radius = 4 + intensity * 2;

      graphics.beginFill(0x00FFFF, alpha);
      graphics.drawCircle(x, y, radius);
      graphics.endFill();
    }
  }

  /**
   * Animate trail effects
   * Shows recent traversal paths fading over time
   */
  private animateTrails(now: number): void {
    if (!this.trailContainer) return;

    const TRAIL_DURATION = 2000; // 2 seconds trail lifetime

    // Animate existing trails (fade out)
    this.trailSegments = this.trailSegments.filter(segment => {
      const elapsed = now - segment.startTime;
      const progress = elapsed / TRAIL_DURATION;

      if (progress >= 1) {
        // Trail expired - remove
        this.trailContainer!.removeChild(segment.graphics);
        return false;
      } else {
        // Fade out trail
        segment.graphics.alpha = 1 - progress;
        return true;
      }
    });

    // Note: Trail creation would happen when processing subentity activity events
    // For now, trails are created based on working memory changes
  }

  /**
   * Create a new trail segment between two nodes
   */
  private createTrailSegment(fromNodeId: string, toNodeId: string, now: number): void {
    if (!this.trailContainer) return;

    const fromNode = this.viewModel.nodes.find(n => n.id === fromNodeId);
    const toNode = this.viewModel.nodes.find(n => n.id === toNodeId);

    if (!fromNode || !toNode || !fromNode.x || !fromNode.y || !toNode.x || !toNode.y) return;

    const graphics = new PIXI.Graphics();

    // Draw translucent line from -> to
    graphics.lineStyle(3, 0xFFA500, 0.6); // Orange trail
    graphics.moveTo(fromNode.x, fromNode.y);
    graphics.lineTo(toNode.x, toNode.y);

    this.trailContainer.addChild(graphics);
    this.trailSegments.push({ from: fromNodeId, to: toNodeId, startTime: now, graphics });
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Simple string hash function (djb2)
 * Returns consistent integer for same string input
 */
function hashString(str: string): number {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i); // hash * 33 + c
  }
  return hash;
}

/**
 * Compute semantic polarity from node properties
 * Used by forceSemanticX to position nodes horizontally
 * Returns value between -1 (left) and +1 (right)
 *
 * Without embeddings, we use available numerical signals:
 * 1. Weight/confidence/energy (if available)
 * 2. Traversal patterns
 * 3. Last subentity that touched this node
 * 4. Text content hash (fallback)
 */
function computeSemanticPolarity(node: NodeData): number {
  let polarity = 0;
  let totalWeight = 0;

  // Signal 1: Weight-based polarity (40% weight)
  // Higher weight nodes cluster right, lower weight left
  const weight = node.weight || node.base_weight || 0.5;
  if (weight > 0) {
    polarity += (weight - 0.5) * 2 * 0.4; // Map [0,1] to [-1,1]
    totalWeight += 0.4;
  }

  // Signal 2: Subentity activation energy (30% weight)
  // If entity_activations exists, use it
  if (node.entity_activations && Object.keys(node.entity_activations).length > 0) {
    const activations = Object.values(node.entity_activations);
    const avgEnergy = activations.reduce((sum, a: any) => sum + (a.energy || 0), 0) / activations.length;

    polarity += (avgEnergy - 0.5) * 2 * 0.3; // Map [0,1] to [-1,1]
    totalWeight += 0.3;
  }

  // Signal 3: Last traversed subentity hash (20% weight)
  // Nodes last touched by same subentity cluster together
  const lastSubentity = node.last_traversed_by || (node as any).created_by;
  if (lastSubentity) {
    const entityHash = hashString(lastSubentity);
    polarity += ((entityHash % 1000) / 500 - 1) * 0.2;
    totalWeight += 0.2;
  }

  // Signal 4: Text content hash (10% weight - fallback)
  // Very crude semantic proxy
  const text = (node as any).text || node.name || node.description || node.id;
  if (text) {
    const textHash = hashString(text);
    polarity += ((textHash % 1000) / 500 - 1) * 0.1;
    totalWeight += 0.1;
  }

  // Normalize by total weight used (handles missing signals)
  return totalWeight > 0 ? polarity / totalWeight : 0;
}
