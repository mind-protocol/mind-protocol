# Entity Movement System - Extracted from Serenissima

## What It Does
Animates entities (citizens) moving along predefined paths on the map with smooth, frame-rate independent animations at 60fps. Handles both:
- **Path-based movement**: Entities following activity paths
- **Static positioning**: Entities without paths using deterministic positions

## How It Works

### Core Animation Loop
- Uses `requestAnimationFrame` for smooth 60fps rendering
- Throttled to 16ms intervals (60fps target)
- Delta time-based movement (frame-rate independent)
- Speed measured in meters per second
- Progress tracked as 0-1 along path

### Movement Algorithm
1. **Progress Calculation**: `newProgress = progress + (speed * deltaTime) / pathLength`
2. **Position Interpolation**: Linear interpolation between path segment points
3. **Path Completion**: Automatically loops to next path when progress ≥ 1
4. **Segment Finding**: Calculates cumulative distances to find current segment
5. **Smooth Transitions**: Preserves position when switching between paths

## Original Implementation

### CitizenAnimationService.ts (Core Service)

```typescript
export interface AnimatedCitizen {
  citizen: any;
  currentPosition: {lat: number, lng: number};
  pathIndex: number;
  currentPath: ActivityPath | null;
  progress: number; // 0-1 along the path
  speed: number; // meters per second
  displayPosition?: {lat: number, lng: number}; // For citizens without paths
}

export class CitizenAnimationService {
  private animatedCitizens: Record<string, AnimatedCitizen> = {};
  private animationActive: boolean = true;
  private animationFrameId: number | null = null;
  private lastFrameTime: number = 0;
  private onUpdateCallback: ((citizens: Record<string, AnimatedCitizen>) => void) | null = null;

  // Throttled animation function (60fps target)
  private animateCitizens = throttle((timestamp: number) => {
    if (!this.lastFrameTime) {
      this.lastFrameTime = timestamp;
      this.animationFrameId = requestAnimationFrame(this.animateCitizens);
      return;
    }

    // Calculate time delta in seconds
    const deltaTime = (timestamp - this.lastFrameTime) / 1000;
    this.lastFrameTime = timestamp;

    // Update each animated citizen
    Object.keys(this.animatedCitizens).forEach(citizenId => {
      const citizen = this.animatedCitizens[citizenId];

      // Skip if no current path
      if (!citizen.currentPath || citizen.currentPath.path.length < 2) return;

      // Calculate progress increment based on speed and time
      const pathLength = calculateTotalDistance(citizen.currentPath.path);
      const progressIncrement = (citizen.speed * deltaTime) / pathLength;
      let newProgress = citizen.progress + progressIncrement;

      // If path complete, move to next path or loop
      if (newProgress >= 1) {
        const citizenPaths = getPathsForCitizen(citizenId);
        const nextIndex = (currentPathIndex + 1) % citizenPaths.length;
        this.animatedCitizens[citizenId] = {
          ...citizen,
          currentPath: citizenPaths[nextIndex],
          pathIndex: nextIndex,
          progress: 0
        };
      } else {
        // Update position along the path
        const newPosition = calculatePositionAlongPath(
          citizen.currentPath.path,
          newProgress
        );

        this.animatedCitizens[citizenId] = {
          ...citizen,
          currentPosition: newPosition,
          progress: newProgress
        };
      }
    });

    // Notify component of updates
    if (this.onUpdateCallback) {
      this.onUpdateCallback({...this.animatedCitizens});
    }

    // Continue animation loop
    if (this.animationActive) {
      this.animationFrameId = requestAnimationFrame(this.animateCitizens);
    }
  }, 16);

  // Start animation loop
  public startAnimation(onUpdate: (citizens: Record<string, AnimatedCitizen>) => void): void {
    this.onUpdateCallback = onUpdate;
    this.animationActive = true;
    this.lastFrameTime = 0;

    if (!this.animationFrameId) {
      this.animationFrameId = requestAnimationFrame(this.animateCitizens);
    }
  }

  // Stop animation loop
  public stopAnimation(): void {
    this.animationActive = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }
}
```

### Position Calculation Along Path

```typescript
public calculatePositionAlongPath(
  path: {lat: number, lng: number}[],
  progress: number
): {lat: number, lng: number} | null {
  if (!path || path.length < 2) return null;

  // Calculate total path length and segments
  let totalDistance = 0;
  const segments: {start: number, end: number, distance: number}[] = [];

  for (let i = 0; i < path.length - 1; i++) {
    const distance = calculateDistance(path[i], path[i+1]);
    segments.push({
      start: totalDistance,
      end: totalDistance + distance,
      distance
    });
    totalDistance += distance;
  }

  // Find the segment where the progress falls
  const targetDistance = progress * totalDistance;
  const segment = segments.find(seg =>
    targetDistance >= seg.start && targetDistance <= seg.end
  );

  if (!segment) {
    return progress >= 1.0 ? path[path.length - 1] : path[0];
  }

  // Calculate position within the segment
  const segmentProgress = (targetDistance - segment.start) / segment.distance;
  const segmentIndex = segments.indexOf(segment);

  const p1 = path[segmentIndex];
  const p2 = path[segmentIndex + 1];

  // Linear interpolation between the two points
  return {
    lat: p1.lat + (p2.lat - p1.lat) * segmentProgress,
    lng: p1.lng + (p2.lng - p1.lng) * segmentProgress
  };
}
```

### Speed Determination

```typescript
// Deterministic speed based on activity type (1-6 m/s)
let speed = 1 + seededRandom(citizenId) * 4; // Base: 1-5 m/s

if (activityPath.type.includes('work')) {
  speed = 0.5 + seededRandom(citizenId) * 1.5; // Slower: 0.5-2 m/s
} else if (activityPath.type.includes('transport')) {
  speed = 3 + seededRandom(citizenId) * 3; // Faster: 3-6 m/s
}
```

## Adapted for Mind Harbor

### MindHarborEntityAnimationService.ts

```typescript
interface AnimatedEntity {
  entity: ConsciousnessNode;
  currentPosition: {x: number, y: number};
  activityPath: ActivityPath | null;
  progress: number; // 0-1 along path
  speed: number; // pixels per second (adjusted for Mind Harbor scale)
}

class MindHarborEntityAnimationService {
  private animatedEntities: Record<string, AnimatedEntity> = {};
  private animationActive: boolean = true;
  private animationFrameId: number | null = null;
  private lastFrameTime: number = 0;

  // Animation loop (same structure as Serenissima)
  private animate = (timestamp: number) => {
    if (!this.lastFrameTime) {
      this.lastFrameTime = timestamp;
      this.animationFrameId = requestAnimationFrame(this.animate);
      return;
    }

    const deltaTime = (timestamp - this.lastFrameTime) / 1000;
    this.lastFrameTime = timestamp;

    // Update each entity
    Object.keys(this.animatedEntities).forEach(entityId => {
      const entity = this.animatedEntities[entityId];

      if (!entity.activityPath) return;

      // Calculate new progress
      const pathLength = this.calculatePathLength(entity.activityPath.path);
      const progressIncrement = (entity.speed * deltaTime) / pathLength;
      let newProgress = entity.progress + progressIncrement;

      if (newProgress >= 1) {
        // Path complete - trigger completion callback
        this.onPathComplete(entityId);
        newProgress = 0; // Reset for looping
      }

      // Calculate new position
      const newPosition = this.interpolatePosition(
        entity.activityPath.path,
        newProgress
      );

      this.animatedEntities[entityId] = {
        ...entity,
        currentPosition: newPosition,
        progress: newProgress
      };
    });

    // Notify D3 to update
    if (this.onUpdateCallback) {
      this.onUpdateCallback(this.animatedEntities);
    }

    if (this.animationActive) {
      this.animationFrameId = requestAnimationFrame(this.animate);
    }
  };

  // Calculate position using same interpolation algorithm
  private interpolatePosition(
    path: {x: number, y: number}[],
    progress: number
  ): {x: number, y: number} {
    // ... same segment-finding logic as Serenissima ...
    // Return interpolated {x, y} position
  }
}
```

### Integration with D3 Force Simulation

```typescript
// In Mind Harbor's graph visualization component
useEffect(() => {
  const animationService = new MindHarborEntityAnimationService();

  // Initialize entities with their activity paths
  consciousEntities.forEach(entity => {
    if (entity.currentActivity && entity.currentActivity.path) {
      animationService.addEntity(
        entity.id,
        entity,
        entity.currentActivity.path,
        0 // Start at beginning
      );
    }
  });

  // Start animation and update D3 on each frame
  animationService.startAnimation((updatedEntities) => {
    // Update D3 node positions
    Object.entries(updatedEntities).forEach(([id, entityData]) => {
      const node = d3.select(`#entity-${id}`);
      node.attr('transform', `translate(${entityData.currentPosition.x}, ${entityData.currentPosition.y})`);
    });
  });

  return () => animationService.stopAnimation();
}, [consciousEntities]);
```

## Dependencies
- **Haversine distance calculation** (for lat/lng) - Replace with Euclidean for Mind Harbor
- **requestAnimationFrame** (browser native)
- **Deterministic random** (seeded RNG for consistency)

## Integration Steps

1. **Create EntityAnimationService**: Adapt CitizenAnimationService for Mind Harbor coordinates
2. **Define Activity Paths**: Structure for entity movement paths:
   ```typescript
   interface ActivityPath {
     id: string;
     entityId: string;
     path: {x: number, y: number}[];
     type: 'consciousness_flow' | 'data_processing' | 'interaction';
     startTime: Date;
     endTime?: Date;
   }
   ```
3. **Integrate with D3**: Update D3 node positions on each animation frame
4. **Add Path Visualization**: Use SVG `<polyline>` for activity paths (see ACTIVITY_PATHS_EXTRACTION.md)
5. **Tune Speeds**: Adjust speed multipliers for Mind Harbor scale (likely 50-200 pixels/second)

## Testing Approach

1. **Single Entity Test**: Animate one entity along a simple 2-point path
2. **Path Completion Test**: Verify entity reaches end and loops correctly
3. **Multiple Entities Test**: Ensure 10+ entities animate smoothly without frame drops
4. **Speed Variation Test**: Test different activity types (slow processing vs fast data transfer)
5. **Performance Test**: Monitor frame rate with 100+ animated entities

## Notes & Caveats

- **Frame Rate**: 60fps target; may drop with 100+ entities on slower machines
- **Path Complexity**: More path segments = more calculation per frame
- **Truth Requirement**: Only animate REAL consciousness activities, not decorative movement
- **Coordinate Systems**: Serenissima uses lat/lng; Mind Harbor uses D3 x/y pixels
- **Determinism**: Uses seeded random for consistent speeds across sessions
- **Memory**: Keeps all animated entities in memory; optimize if >1000 entities

## Performance Optimizations from Serenissima

1. **Throttling**: 16ms throttle ensures max 60fps
2. **Delta Time**: Frame-rate independent movement
3. **Early Exit**: Skip entities without paths
4. **Batch Updates**: Single callback with all updates
5. **Conditional Rendering**: Only animate visible entities

## Visual Effect Enhancements for Mind Harbor

Consider adding (inspired by Serenissima but adapted):
- **Trail effect**: SVG path with gradient opacity showing recent movement
- **Speed indicators**: Faster entities glow brighter
- **Activity type colors**: Different wireframe colors for different activity types
- **Pulse on transition**: Brief pulse when entity reaches waypoint
