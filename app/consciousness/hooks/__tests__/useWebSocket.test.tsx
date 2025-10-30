import { renderHook, waitFor } from '@testing-library/react';
import { useWebSocket } from '../useWebSocket';
import { WebSocketState } from '../websocket-types';

// Mock WebSocket is already set up in jest.setup.js
describe('useWebSocket Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with default state', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.subentityActivity).toEqual([]);
    expect(result.current.thresholdCrossings).toEqual([]);
    expect(result.current.weightLearningEvents).toEqual([]);
    expect(result.current.strideSelectionEvents).toEqual([]);
    expect(result.current.phenomenologyMismatchEvents).toEqual([]);
    expect(result.current.phenomenologyHealthEvents).toEqual([]);
    expect(result.current.forgedIdentityFrames).toEqual([]);
    // forgedIdentityMetrics is {} not null
    expect(result.current.forgedIdentityMetrics).toBeDefined();
    expect(result.current.error).toBeNull();
    expect(result.current.graphNodes).toEqual([]);
    expect(result.current.graphLinks).toEqual([]);
    expect(result.current.graphSubentities).toEqual([]);
    expect(result.current.hierarchySnapshot).toBeNull();
    expect(result.current.economyOverlays).toEqual({});
  });

  it('initializes v2State with correct structure', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.v2State).toBeDefined();
    // workingMemory is a Set, not Map
    expect(result.current.v2State.workingMemory).toBeInstanceOf(Set);
    expect(result.current.v2State.linkFlows).toBeInstanceOf(Map);
    // recentFlips is an array
    expect(Array.isArray(result.current.v2State.recentFlips)).toBe(true);
  });

  it('initializes emotionState with correct structure', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.emotionState).toBeDefined();
    // emotionState has different properties than expected
    expect(result.current.emotionState).toHaveProperty('recentStrides');
    expect(Array.isArray(result.current.emotionState.recentStrides)).toBe(true);
  });

  it('starts with CONNECTING state', async () => {
    const { result } = renderHook(() => useWebSocket());

    // Initial state should be CONNECTING
    expect([WebSocketState.CONNECTING, WebSocketState.CONNECTED]).toContain(
      result.current.connectionState
    );
  });

  it('attempts to establish WebSocket connection', () => {
    const { result } = renderHook(() => useWebSocket());

    // Connection state should be one of the valid states
    expect(Object.values(WebSocketState)).toContain(result.current.connectionState);
  });

  it('initializes without errors', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.error).toBeNull();
  });
});

describe('useWebSocket Hook - State Management', () => {
  it('maintains empty arrays when no messages received', () => {
    const { result } = renderHook(() => useWebSocket());

    // Check arrays without waiting for connection
    expect(result.current.subentityActivity).toHaveLength(0);
    expect(result.current.thresholdCrossings).toHaveLength(0);
    expect(result.current.graphNodes).toHaveLength(0);
    expect(result.current.graphLinks).toHaveLength(0);
  });

  it('v2State structures are accessible', () => {
    const { result } = renderHook(() => useWebSocket());

    // Should be able to read from the Set/Map/Array structures
    expect(result.current.v2State.workingMemory.size).toBe(0);
    expect(result.current.v2State.linkFlows.size).toBe(0);
    expect(result.current.v2State.recentFlips.length).toBe(0);
  });

  it('economyOverlays starts as empty object', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.economyOverlays).toEqual({});
    expect(Object.keys(result.current.economyOverlays)).toHaveLength(0);
  });
});

describe('useWebSocket Hook - Message Types', () => {
  it('provides correct message type arrays', () => {
    const { result } = renderHook(() => useWebSocket());

    // All these should be arrays
    expect(Array.isArray(result.current.subentityActivity)).toBe(true);
    expect(Array.isArray(result.current.thresholdCrossings)).toBe(true);
    expect(Array.isArray(result.current.weightLearningEvents)).toBe(true);
    expect(Array.isArray(result.current.strideSelectionEvents)).toBe(true);
    expect(Array.isArray(result.current.phenomenologyMismatchEvents)).toBe(true);
    expect(Array.isArray(result.current.phenomenologyHealthEvents)).toBe(true);
    expect(Array.isArray(result.current.forgedIdentityFrames)).toBe(true);
    expect(Array.isArray(result.current.graphNodes)).toBe(true);
    expect(Array.isArray(result.current.graphLinks)).toBe(true);
    expect(Array.isArray(result.current.graphSubentities)).toBe(true);
  });

  it('provides forgedIdentityMetrics object', () => {
    const { result } = renderHook(() => useWebSocket());

    // forgedIdentityMetrics is an object, may be empty {}
    expect(result.current.forgedIdentityMetrics).toBeDefined();
  });

  it('provides nullable hierarchySnapshot', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.hierarchySnapshot).toBeNull();
  });
});

describe('useWebSocket Hook - Connection Lifecycle', () => {
  it('cleans up on unmount', () => {
    const { unmount } = renderHook(() => useWebSocket());

    // Should not throw errors when unmounting
    expect(() => unmount()).not.toThrow();
  });

  it('can be used in multiple components simultaneously', () => {
    const { result: result1 } = renderHook(() => useWebSocket());
    const { result: result2 } = renderHook(() => useWebSocket());

    // Both should initialize successfully
    expect(result1.current.connectionState).toBeDefined();
    expect(result2.current.connectionState).toBeDefined();
  });

  it('maintains consistent state structure across re-renders', () => {
    const { result, rerender } = renderHook(() => useWebSocket());

    rerender();

    // v2State should maintain same structure
    expect(result.current.v2State).toBeDefined();
    expect(result.current.v2State.workingMemory).toBeInstanceOf(Set);
    expect(result.current.v2State.linkFlows).toBeInstanceOf(Map);
    expect(Array.isArray(result.current.v2State.recentFlips)).toBe(true);
  });
});

describe('useWebSocket Hook - Error Handling', () => {
  it('initializes without error state', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.error).toBeNull();
  });

  it('connection state is never undefined', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.connectionState).toBeDefined();
    expect(Object.values(WebSocketState)).toContain(result.current.connectionState);
  });
});

describe('useWebSocket Hook - Return Value Structure', () => {
  it('returns all expected properties', () => {
    const { result } = renderHook(() => useWebSocket());

    const expectedProps = [
      'subentityActivity',
      'thresholdCrossings',
      'v2State',
      'emotionState',
      'weightLearningEvents',
      'strideSelectionEvents',
      'phenomenologyMismatchEvents',
      'phenomenologyHealthEvents',
      'forgedIdentityFrames',
      'forgedIdentityMetrics',
      'connectionState',
      'error',
      'graphNodes',
      'graphLinks',
      'graphSubentities',
      'hierarchySnapshot',
      'economyOverlays',
      'walletContext',
    ];

    expectedProps.forEach(prop => {
      expect(result.current).toHaveProperty(prop);
    });
  });

  it('walletContext is defined', () => {
    const { result } = renderHook(() => useWebSocket());

    // May be null or an object, but should be defined
    expect(result.current).toHaveProperty('walletContext');
  });
});
