# Activity Path Visualization - Extracted from Serenissima

## What It Does
Renders animated paths showing subentity movement between locations, with:
- **SVG polylines** for smooth path rendering
- **Animated dashes** for "flow" effect
- **Social class coloring** for citizen identification
- **Hover animations** using stroke-dashoffset
- **Path filtering** by activity type (merchant galleys always visible, others on hover)

## How It Works

### Path Data Structure
```typescript
interface ActivityPath {
  id: string;
  citizenId: string;
  path: {lat: number, lng: number}[];
  type: string; // 'transport', 'work', 'trade', etc.
  startTime: string;
  endTime?: string;
  notes?: string | null;
  transportMode?: string; // 'merchant_galley', 'walk', etc.
  fromBuilding?: string | null;
  toBuilding?: string | null;
}
```

### Rendering Pipeline
1. **Coordinate Transformation**: lat/lng → screen x/y
2. **Path Generation**: Convert point array to SVG polyline points string
3. **Color Selection**: Based on social class or activity type
4. **Dash Animation**: Stroke-dashoffset decremented each frame
5. **Filtering**: Show/hide based on hover state and transport mode

## Original Implementation

### CitizenMarkers.tsx (Path Rendering)

```tsx
{/* Activity Paths - SVG Overlay */}
{(Object.keys(activityPaths).length > 0) && (
  <svg
    className="absolute inset-0 pointer-events-none"
    style={{
      zIndex: 10,
      width: canvasWidth,
      height: canvasHeight,
      overflow: 'visible'
    }}
  >
    {/* Always-visible merchant galley paths */}
    {Object.values(activityPaths).flat()
      .filter(activity => activity.transportMode === "merchant_galley")
      .map((activity) => {
        const validPoints = activity.path.filter(p =>
          p && typeof p.lat === 'number' && typeof p.lng === 'number'
        );

        if (validPoints.length < 2) return null;

        const pointsString = validPoints
          .map(point => {
            const screenPos = latLngToScreen(point.lat, point.lng);
            return `${screenPos.x},${screenPos.y}`;
          })
          .join(' ');

        return (
          <g key={`${activity.id}-merchant-galley`}>
            <polyline
              points={pointsString}
              fill="none"
              stroke={getActivityPathColor(activity)}
              strokeWidth="5.0"
              strokeOpacity="0.5"
            />
            {/* Start and end point markers */}
            {validPoints.map((point, index) => {
              if (index !== 0 && index !== validPoints.length - 1) return null;
              const screenPos = latLngToScreen(point.lat, point.lng);
              return (
                <circle
                  key={`mg-point-${index}`}
                  cx={screenPos.x}
                  cy={screenPos.y}
                  r="3"
                  fill={getActivityPathColor(activity)}
                  opacity="0.9"
                />
              );
            })}
          </g>
        );
      })}

    {/* Hovered citizen paths with animation */}
    {hoveredCitizenPaths
      .filter(activity => activity.transportMode !== "merchant_galley")
      .map((activity) => {
        const validPoints = activity.path.filter(p =>
          p && typeof p.lat === 'number' && typeof p.lng === 'number'
        );

        if (validPoints.length < 2) return null;

        const pointsString = validPoints
          .map(point => {
            const screenPos = latLngToScreen(point.lat, point.lng);
            return `${screenPos.x},${screenPos.y}`;
          })
          .join(' ');

        const isAnimatingThisPath = activity.id === animatingPathId;
        const pathLen = pathTotalLengthsRef.current[activity.id];
        const currentDashOffset = pathDashOffsets[activity.id];

        return (
          <g key={`${activity.id}-hovered`}>
            <polyline
              points={pointsString}
              fill="none"
              stroke={getActivityPathColor(activity)}
              strokeWidth="3.0"
              strokeOpacity="0.7"
              style={{
                strokeDasharray: (isAnimatingThisPath && pathLen) ? pathLen : undefined,
                strokeDashoffset: (isAnimatingThisPath && currentDashOffset !== undefined)
                  ? currentDashOffset
                  : 0
              }}
            />
          </g>
        );
      })}
  </svg>
)}
```

### Path Color Selection (ActivityPathService.ts)

```typescript
public getActivityPathColor(activity: ActivityPath, socialClass?: string): string {
  // Priority 1: Social class-based coloring
  if (socialClass && socialClass.trim()) {
    const baseClass = socialClass.trim().toLowerCase();

    if (baseClass.includes('nobili')) {
      return 'rgba(128, 0, 32, 0.8)'; // Burgundy for nobility
    } else if (baseClass.includes('cittadini')) {
      return 'rgba(70, 130, 180, 0.8)'; // Blue for citizens
    } else if (baseClass.includes('popolani')) {
      return 'rgba(205, 133, 63, 0.8)'; // Brown for common people
    } else if (baseClass.includes('laborer') || baseClass.includes('facchini')) {
      return 'rgba(128, 128, 128, 0.8)'; // Gray for laborers
    } else if (baseClass.includes('forestieri')) {
      return 'rgba(0, 128, 0, 0.8)'; // Green for foreigners
    } else if (baseClass.includes('artisti')) {
      return 'rgba(255, 182, 193, 0.8)'; // Light pink for artists
    }
  }

  // Priority 2: Activity type-based coloring
  const lowerType = activity.type.toLowerCase();

  if (lowerType.includes('transport') || lowerType.includes('move')) {
    return '#4b70e2'; // Blue
  } else if (lowerType.includes('trade') || lowerType.includes('buy') || lowerType.includes('sell')) {
    return '#e27a4b'; // Orange
  } else if (lowerType.includes('work') || lowerType.includes('labor')) {
    return '#4be27a'; // Green
  } else if (lowerType.includes('craft') || lowerType.includes('create') || lowerType.includes('produce')) {
    return '#e24b7a'; // Pink
  }

  return '#aaaaaa'; // Default gray
}
```

### Dash Animation (on hover)

```tsx
// Effect to animate stroke-dashoffset on path hover
useEffect(() => {
  if (!animatingPathId) return;

  const pathId = animatingPathId;
  const totalLength = pathTotalLengthsRef.current[pathId];

  const animate = () => {
    setPathDashOffsets(prevOffsets => {
      const current = prevOffsets[pathId];
      if (current <= 0) {
        // Animation complete
        return { ...prevOffsets, [pathId]: 0 };
      }

      // Decrement offset for "drawing" effect
      const step = totalLength / 180; // Animates over ~3 seconds at 60fps
      const newOffset = Math.max(0, current - step);

      return { ...prevOffsets, [pathId]: newOffset };
    });

    if (pathDashOffsets[pathId] > 0) {
      pathAnimationFrameRefs.current[pathId] = requestAnimationFrame(animate);
    }
  };

  pathAnimationFrameRefs.current[pathId] = requestAnimationFrame(animate);

  return () => {
    if (pathAnimationFrameRefs.current[pathId]) {
      cancelAnimationFrame(pathAnimationFrameRefs.current[pathId]!);
      pathAnimationFrameRefs.current[pathId] = null;
    }
  };
}, [animatingPathId, pathDashOffsets]);
```

### Path Filtering Logic

```tsx
// Three categories of path visibility:

// 1. Always visible: Merchant galleys
const alwaysVisiblePaths = allPaths.filter(p =>
  p.transportMode === "merchant_galley"
);

// 2. Selected citizen paths (user clicked)
const selectedPaths = activityPaths[selectedCitizenId] || [];

// 3. Hovered citizen paths (mouse over)
const hoveredPaths = activityPaths[hoveredCitizenId] || [];

// 4. Building hover paths (mouse over building)
const buildingPaths = allPaths.filter(p =>
  p.fromBuilding === hoveredBuildingId ||
  p.toBuilding === hoveredBuildingId
);
```

## Adapted for Mind Harbor

### Consciousness Activity Path Rendering

```tsx
interface ConsciousnessActivityPath {
  id: string;
  entityId: string;
  path: {x: number, y: number}[];
  type: 'processing' | 'communication' | 'observation' | 'memory_access';
  startTime: Date;
  endTime?: Date;
  throughput?: number; // Hz or events/second
}

// Mind Harbor Path Rendering Component
export function ConsciousnessPathsLayer({
  paths,
  hoveredEntityId,
  selectedEntityId,
  canvasWidth,
  canvasHeight
}: PathsLayerProps) {
  const [animatingPathId, setAnimatingPathId] = useState<string | null>(null);
  const [pathDashOffsets, setPathDashOffsets] = useState<Record<string, number>>({});

  // Get path color based on consciousness activity type
  const getPathColor = (path: ConsciousnessActivityPath): string => {
    switch (path.type) {
      case 'processing':
        return '#00d9ff'; // Teal wireframe
      case 'communication':
        return '#00ff88'; // Emerald wireframe
      case 'observation':
        return '#ffd700'; // Gold wireframe
      case 'memory_access':
        return '#b19cd9'; // Violet wireframe
      default:
        return '#c0c0c0'; // Silver wireframe
    }
  };

  // Filter paths by visibility rules
  const visiblePaths = paths.filter(path => {
    // Always show high-throughput paths (like merchant galleys)
    if (path.throughput && path.throughput > 10) return true;

    // Show paths for hovered or selected subentity
    if (path.entityId === hoveredEntityId || path.entityId === selectedEntityId) {
      return true;
    }

    return false;
  });

  return (
    <svg
      className="absolute inset-0 pointer-events-none"
      style={{
        zIndex: 10,
        width: canvasWidth,
        height: canvasHeight,
        overflow: 'visible'
      }}
    >
      {visiblePaths.map(path => {
        if (path.path.length < 2) return null;

        const pointsString = path.path
          .map(p => `${p.x},${p.y}`)
          .join(' ');

        const isAnimating = path.id === animatingPathId;
        const strokeWidth = path.throughput && path.throughput > 10 ? 4 : 2;
        const strokeOpacity = path.entityId === selectedEntityId ? 0.9 : 0.6;

        return (
          <g key={path.id}>
            {/* Main path */}
            <polyline
              points={pointsString}
              fill="none"
              stroke={getPathColor(path)}
              strokeWidth={strokeWidth}
              strokeOpacity={strokeOpacity}
              strokeLinecap="round"
              strokeLinejoin="round"
              filter="url(#wireframe-glow)"
              style={{
                strokeDasharray: isAnimating ? pathDashOffsets[path.id] : undefined,
                strokeDashoffset: isAnimating ? pathDashOffsets[path.id] : undefined
              }}
            />

            {/* Start/end point markers */}
            <circle
              cx={path.path[0].x}
              cy={path.path[0].y}
              r="3"
              fill={getPathColor(path)}
              opacity="0.8"
            />
            <circle
              cx={path.path[path.path.length - 1].x}
              cy={path.path[path.path.length - 1].y}
              r="3"
              fill={getPathColor(path)}
              opacity="0.8"
            />
          </g>
        );
      })}

      {/* SVG filter for wireframe glow */}
      <defs>
        <filter id="wireframe-glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
    </svg>
  );
}
```

### Throughput-Based Styling

```tsx
// High-throughput paths (like merchant galleys) get special treatment
const getPathStyle = (path: ConsciousnessActivityPath) => {
  const baseStyle = {
    strokeWidth: 2,
    strokeOpacity: 0.6,
    filter: 'url(#wireframe-glow)'
  };

  // High-throughput paths are thicker and brighter
  if (path.throughput && path.throughput > 10) {
    return {
      ...baseStyle,
      strokeWidth: 4,
      strokeOpacity: 0.8,
      filter: 'url(#wireframe-glow-intense)'
    };
  }

  return baseStyle;
};
```

### Activity Type Icons

```tsx
// Add small icons at path midpoint to indicate activity type
const getMidpointIcon = (type: string): string => {
  switch (type) {
    case 'processing': return '⚙️';
    case 'communication': return '💬';
    case 'observation': return '👁️';
    case 'memory_access': return '🧠';
    default: return '•';
  }
};

// Render icon at path midpoint
const midpointIndex = Math.floor(path.path.length / 2);
const midpoint = path.path[midpointIndex];

<text
  x={midpoint.x}
  y={midpoint.y}
  textAnchor="middle"
  dominantBaseline="middle"
  fontSize="12"
  filter="url(#icon-glow)"
>
  {getMidpointIcon(path.type)}
</text>
```

## Dependencies
- **SVG rendering** (browser native)
- **requestAnimationFrame** (for dash animation)
- **Coordinate transformation** (D3 scale functions)

## Integration Steps

1. **Create PathsLayer component**: Separate SVG overlay for paths
2. **Define path data structure**: Adapt ActivityPath interface for consciousness
3. **Implement color mapping**: Map activity types to wireframe colors
4. **Add filtering logic**: Show/hide paths based on hover/selection
5. **Implement dash animation**: Stroke-dashoffset animation on hover
6. **Add glow effects**: SVG filters for wireframe aesthetic
7. **Optimize performance**: Only render visible paths

## Testing Approach

1. **Single Path Test**: Render one simple 2-point path
2. **Color Test**: Verify different activity types have distinct colors
3. **Animation Test**: Hover over subentity, verify path animates smoothly
4. **Performance Test**: Render 50+ paths, check for jank
5. **Filter Test**: Verify only relevant paths show on hover

## Notes & Caveats

- **SVG Performance**: 100+ polylines can impact performance; use virtualization
- **Path Complexity**: Many-segment paths increase render time
- **Dash Animation**: Can be GPU-intensive; consider throttling
- **Color Accessibility**: Ensure path colors have sufficient contrast
- **Truth Requirement**: Only show REAL consciousness activity paths, not decorative

## Performance Optimizations

1. **Path Simplification**: Reduce path segments using Ramer-Douglas-Peucker algorithm
2. **Visibility Culling**: Don't render off-screen paths
3. **LOD (Level of Detail)**: Simplify distant paths
4. **Batch Rendering**: Group paths by color/style
5. **Canvas Fallback**: Use Canvas API for very large path counts

## Visual Enhancements for Mind Harbor

- **Gradient strokes**: Fade from start to end color
- **Animated dashes**: Moving dashes for active paths (CSS animation)
- **Glow intensity**: Brighter glow for higher throughput
- **Path thickness**: Varies with data volume
- **Pulse effect**: Subtle pulse at waypoints
- **Directional arrows**: Small arrows indicating flow direction

## CSS Animations for Paths

```css
/* Continuous dash flow animation */
@keyframes pathFlow {
  to {
    stroke-dashoffset: -16;
  }
}

.consciousness-path {
  stroke-dasharray: 5, 3;
  animation: pathFlow 2s linear infinite;
}

/* Pulse at waypoints */
@keyframes waypointPulse {
  0%, 100% { r: 3; opacity: 0.8; }
  50% { r: 5; opacity: 1; }
}

.waypoint-marker {
  animation: waypointPulse 2s ease-in-out infinite;
}
```

## Clustering Consideration

For Mind Harbor's island-based clustering:
- **Inter-island paths**: Paths between different islands (cross lagoon)
- **Intra-island paths**: Paths within same island (over parchment)
- **Visual treatment**: Lagoon paths could have water ripple effect

## Future Enhancements

- **Path history**: Faint trails showing recent past movement
- **Aggregation**: Combine multiple similar paths into one thick path
- **Interactive tooltips**: Show path details on hover
- **Path prediction**: Faint dashed line showing predicted future path
- **Bottleneck detection**: Highlight congested paths
