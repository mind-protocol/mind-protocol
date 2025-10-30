import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { SubEntityGraphView } from '../SubEntityGraphView';
import type { Node, Link, Subentity, Operation } from '../../hooks/useGraphData';

// Mock child components
jest.mock('../SubEntityMoodMap', () => ({
  SubEntityMoodMap: () => <div data-testid="mood-map">Mood Map</div>,
}));

jest.mock('../PixiCanvas', () => ({
  PixiCanvas: () => <div data-testid="pixi-canvas">Pixi Canvas</div>,
}));

jest.mock('../StrideSparks', () => ({
  StrideSparks: () => <div data-testid="stride-sparks">Stride Sparks</div>,
}));

jest.mock('../ActiveSubentitiesPanel', () => ({
  ActiveSubentitiesPanel: () => <div data-testid="active-panel">Active Panel</div>,
}));

// Mock useWebSocket hook
jest.mock('../../hooks/useWebSocket', () => ({
  useWebSocket: jest.fn(() => ({
    emotionState: {
      valence: 0.5,
      arousal: 0.3,
      dominance: 0.7,
      recentStrides: [],
    },
  })),
}));

// Mock utility functions
jest.mock('../../lib/subentityEmotion', () => ({
  aggregateSubEntityEmotion: jest.fn(() => ({ valence: 0, arousal: 0, dominance: 0 })),
  aggregateSubEntityEnergy: jest.fn(() => 0.5),
  calculateSubEntityCoherence: jest.fn(() => 0.8),
}));

jest.mock('../../lib/visibleGraphSelector', () => ({
  selectVisibleGraph: jest.fn(() => ({ nodes: [], links: [] })),
}));

jest.mock('../../lib/graph/selectVisibleGraphV2', () => ({
  selectVisibleGraphV2: jest.fn(() => ({ renderNodes: [], renderEdges: [] })),
}));

const mockNodes: Node[] = [
  {
    id: 'node1',
    node_id: 'node1',
    name: 'Test Node 1',
    node_type: 'Concept',
    energy: 0.8,
    theta: 0.5,
    text: 'Test node 1',
  },
  {
    id: 'node2',
    node_id: 'node2',
    name: 'Test Node 2',
    node_type: 'Concept',
    energy: 0.6,
    theta: 0.3,
    text: 'Test node 2',
  },
];

const mockLinks: Link[] = [
  {
    id: 'link1',
    source: 'node1',
    target: 'node2',
    type: 'RELATES_TO',
    weight: 0.7,
  },
];

const mockSubentities: Subentity[] = [
  {
    subentity_id: 'sub1',
    name: 'Translator',
    kind: 'semantic',
    energy: 0.8,
    threshold: 0.5,
    activation_level: 0.9,
    member_count: 5,
  },
  {
    subentity_id: 'sub2',
    name: 'Architect',
    kind: 'semantic',
    energy: 0.6,
    threshold: 0.5,
    activation_level: 0.7,
    member_count: 3,
  },
];

const mockOperations: Operation[] = [];

describe.skip('SubEntityGraphView', () => {
  const defaultProps = {
    nodes: mockNodes,
    links: mockLinks,
    operations: mockOperations,
    subentities: mockSubentities,
    workingMemory: new Set<string>(),
    linkFlows: new Map<string, number>(),
    recentFlips: [],
    expandedSubEntities: new Set<string>(),
    toggleSubEntity: jest.fn(),
    subentityFlows: {},
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset window dimensions mock
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1920,
    });
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 1080,
    });
  });

  it('renders without crashing', () => {
    render(<SubEntityGraphView {...defaultProps} />);
    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('renders mood map by default', () => {
    render(<SubEntityGraphView {...defaultProps} />);
    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('renders stride sparks', () => {
    render(<SubEntityGraphView {...defaultProps} />);
    expect(screen.getByTestId('stride-sparks')).toBeInTheDocument();
  });

  it('renders active subentities panel', () => {
    render(<SubEntityGraphView {...defaultProps} />);
    expect(screen.getByTestId('active-panel')).toBeInTheDocument();
  });

  it('handles empty nodes array', () => {
    render(<SubEntityGraphView {...defaultProps} nodes={[]} />);
    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('handles empty subentities array', () => {
    render(<SubEntityGraphView {...defaultProps} subentities={[]} />);
    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('handles empty links array', () => {
    render(<SubEntityGraphView {...defaultProps} links={[]} />);
    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('updates dimensions on window resize', async () => {
    render(<SubEntityGraphView {...defaultProps} />);

    // Trigger resize
    Object.defineProperty(window, 'innerWidth', { value: 1024, writable: true });
    Object.defineProperty(window, 'innerHeight', { value: 768, writable: true });
    window.dispatchEvent(new Event('resize'));

    // Component should handle resize without crashing
    await waitFor(() => {
      expect(screen.getByTestId('mood-map')).toBeInTheDocument();
    });
  });

  it('cleans up resize listener on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');

    const { unmount } = render(<SubEntityGraphView {...defaultProps} />);
    unmount();

    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));
    removeEventListenerSpy.mockRestore();
  });
});

describe.skip('SubEntityGraphView - Props Handling', () => {
  const defaultProps = {
    nodes: mockNodes,
    links: mockLinks,
    operations: mockOperations,
    subentities: mockSubentities,
    workingMemory: new Set<string>(),
    linkFlows: new Map<string, number>(),
    recentFlips: [],
    expandedSubEntities: new Set<string>(),
    toggleSubEntity: jest.fn(),
    subentityFlows: {},
  };

  it('passes working memory to child components', () => {
    const workingMemory = new Set(['node1', 'node2']);
    render(<SubEntityGraphView {...defaultProps} workingMemory={workingMemory} />);

    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('passes link flows to child components', () => {
    const linkFlows = new Map([['link1', 5], ['link2', 3]]);
    render(<SubEntityGraphView {...defaultProps} linkFlows={linkFlows} />);

    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('passes recent flips to child components', () => {
    const recentFlips = [
      { node_id: 'node1', direction: 'on' as const, dE: 0.5, timestamp: Date.now() },
    ];
    render(<SubEntityGraphView {...defaultProps} recentFlips={recentFlips} />);

    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('passes expanded subentities set', () => {
    const expandedSubEntities = new Set(['sub1', 'sub2']);
    render(<SubEntityGraphView {...defaultProps} expandedSubEntities={expandedSubEntities} />);

    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('passes subentity flows object', () => {
    const subentityFlows = {
      'sub1->sub2': 0.7,
      'sub2->sub1': 0.3,
    };
    render(<SubEntityGraphView {...defaultProps} subentityFlows={subentityFlows} />);

    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });
});

describe.skip('SubEntityGraphView - Integration', () => {
  const defaultProps = {
    nodes: mockNodes,
    links: mockLinks,
    operations: mockOperations,
    subentities: mockSubentities,
    workingMemory: new Set<string>(),
    linkFlows: new Map<string, number>(),
    recentFlips: [],
    expandedSubEntities: new Set<string>(),
    toggleSubEntity: jest.fn(),
    subentityFlows: {},
  };

  it('uses emotion state from useWebSocket', () => {
    const { useWebSocket } = require('../../hooks/useWebSocket');
    useWebSocket.mockReturnValue({
      emotionState: {
        valence: 0.8,
        arousal: 0.9,
        dominance: 0.6,
        recentStrides: [],
      },
    });

    render(<SubEntityGraphView {...defaultProps} />);
    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('handles complex subentity data', () => {
    const complexSubentities: Subentity[] = [
      {
        subentity_id: 'sub1',
        name: 'Complex SubEntity',
        kind: 'semantic',
        energy: 0.95,
        threshold: 0.7,
        activation_level: 0.99,
        member_count: 20,
        quality: 0.85,
        stability: 0.92,
      },
    ];

    render(<SubEntityGraphView {...defaultProps} subentities={complexSubentities} />);
    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });

  it('handles large node/link datasets', () => {
    const largeNodes = Array.from({ length: 100 }, (_, i) => ({
      id: `node${i}`,
      node_id: `node${i}`,
      name: `Node ${i}`,
      node_type: 'Concept',
      energy: Math.random(),
      theta: Math.random(),
      text: `Node ${i}`,
    }));

    render(<SubEntityGraphView {...defaultProps} nodes={largeNodes} />);
    expect(screen.getByTestId('mood-map')).toBeInTheDocument();
  });
});
