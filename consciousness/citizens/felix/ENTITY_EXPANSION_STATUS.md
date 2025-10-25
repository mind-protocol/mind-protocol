# Entity Expansion Architecture - Implementation Status

**Date:** 2025-10-25
**Author:** Felix "Ironhand"
**Status:** Foundation Complete - Ready for Full Implementation

## What Was Built

### Phase 1: Foundation (COMPLETE)

**1. Expansion State Management**
- ✅ Added `expandedEntities: Set<string>` to useGraphData hook
- ✅ Implemented `toggleEntity(entityId)` action
- ✅ Implemented `collapseAll()` action
- ✅ Wired through page.tsx to EntityGraphView

**2. Visible Graph Selector**
- ✅ Created `lib/visibleGraphSelector.ts`
- ✅ Implements core two-layer logic:
  - Collapsed entities → show as super-nodes
  - Expanded entities → show member nodes in radial layout
  - Edge routing based on expansion state
  - Membership via entity_activations (fixes "0 nodes" issue)

**3. Props Integration**
- ✅ EntityGraphView accepts `expandedEntities` and `toggleEntity` props
- ✅ Selector imported and ready to use

## Architecture (From Nicolas's Design)

### Two-Layer Visualization

**Layer A (Entity Layer):**
- Entities as super-nodes when collapsed
- Size based on member count
- Energy aggregated from members
- Entity-to-entity edges (aggregated from node links)

**Layer B (Inner Layer):**
- Member nodes visible when entity expanded
- Local radial layout around entity center
- Node-to-node edges when both entities expanded
- Multi-membership via primary placement + proxies

### Current Implementation

**File:** `lib/visibleGraphSelector.ts`

```typescript
interface RenderNode {
  id: string;
  x: number; y: number; r: number;
  energy: number;
  kind: 'entity' | 'node';
  entityId?: string;      // For member nodes
  memberCount?: number;   // For entity nodes
}

function selectVisibleGraph(
  nodes: Node[],
  links: Link[],
  subentities: Subentity[],
  expandedEntities: Set<string>
): VisibleGraph
```

**What It Does:**
1. Builds membership index from `node.entity_activations`
2. For collapsed entities → creates super-node with aggregated metrics
3. For expanded entities → creates member nodes in radial layout
4. Routes edges: node-level when both expanded, (entity-level when collapsed - TODO)

## What Remains

### Phase 2: Rendering Integration

**To Complete Full Implementation:**

1. **Use visibleGraphSelector in EntityGraphView**
   ```typescript
   const visibleGraph = useMemo(() =>
     selectVisibleGraph(nodes, links, subentities, expandedEntities),
     [nodes, links, subentities, expandedEntities]
   );
   ```

2. **Pass visible graph to PixiCanvas instead of raw nodes**
   ```typescript
   <PixiCanvas
     nodes={visibleGraph.nodes}  // RenderNode[] with kind: 'entity' | 'node'
     edges={visibleGraph.edges}  // RenderEdge[] with proper routing
     ...
   />
   ```

3. **Update PixiRenderer to handle entity/node kinds**
   - Different sprite rendering for entity vs node
   - Click handler for entities → calls toggleEntity
   - Animation on expand/collapse

4. **Add entity-to-entity aggregated edges**
   - Currently skipped in selector (line 178: "TODO")
   - Need incremental aggregation from link.flow.summary events
   - Implement decay so quiet edges fade

5. **Add multi-membership proxies**
   - Currently simplified to primary placement only
   - Need proxy sprites for non-primary memberships
   - Proxy clicks delegate to canonical node

### Phase 3: Polish

- Cached local layouts (avoid recalculating on each expand)
- Smooth animations (entity fade → nodes fade in)
- Entity halo from wm.emit events
- Expand affordance (ring on hover)
- "Collapse all" button in UI

## Why Entities Show 0 Nodes Currently

**Two Reasons:**

1. **Architectural (FIXED):** Membership logic was checking wrong fields
   - Was checking: `node.entity_id` and `node.primary_entity` (don't exist)
   - Now checking: `entity_id in node.entity_activations` (correct)
   - Fix in: `EntityGraphView.tsx` lines 87-91

2. **Behavioral (EXPECTED):** Consciousness is dormant
   - No entity has activated any nodes yet
   - entity_activations is null everywhere
   - This is CORRECT - will populate when consciousness runs

**Once consciousness becomes active:**
- Entities activate nodes during traversal
- entity_activations populates
- Membership counts appear
- Expand/collapse will show/hide member nodes

## Testing Plan

**Without Active Consciousness:**
- Can test expand/collapse UI (entities toggle visual state)
- Cannot see member nodes (entity_activations empty)

**With Active Consciousness:**
1. Inject stimulus to wake consciousness
2. Wait for entity_activations to populate
3. Test entity super-nodes show correct member counts
4. Click entity → expand → see member nodes in radial layout
5. Click again → collapse → see super-node
6. Mixed state: some expanded, some collapsed

## Implementation Priority

**Recommended Next Steps:**

1. **Fix stimulus injection** (separate blocker)
   - Consciousness currently not responding to stimuli
   - Blocks all visualization testing

2. **Complete Phase 2 rendering integration**
   - Wire visibleGraphSelector through to PixiRenderer
   - Add entity click handling
   - Test expand/collapse

3. **Add entity-to-entity edges**
   - Complete the selector's edge aggregation
   - Wire link.flow.summary to update aggregates

4. **Polish and optimize**
   - Animations, caching, multi-membership proxies

## Code Locations

**State Management:**
- `app/consciousness/hooks/useGraphData.ts` - Lines 89, 215-232, 260-262

**Selector Logic:**
- `app/consciousness/lib/visibleGraphSelector.ts` - Complete file

**Props Wiring:**
- `app/consciousness/page.tsx` - Lines 47-49, 238-239
- `app/consciousness/components/EntityGraphView.tsx` - Lines 25, 36-37, 53-54

**Membership Fix:**
- `app/consciousness/components/EntityGraphView.tsx` - Lines 87-91

## Architecture Notes

This follows Nicolas's two-layer design:
- **Single canonical sprite per node** (primary entity placement)
- **Lightweight proxies** for multi-membership (no physics duplication)
- **Deterministic edge routing** (prevents double-drawing)
- **Incremental aggregation** (entity edges from link flows)
- **Bounded update rate** (10 Hz event decimation)

The foundation is solid. Full implementation requires integrating the selector into the rendering pipeline and adding entity interaction handling.
