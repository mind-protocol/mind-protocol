import React from 'react';
import { render, screen } from '@testing-library/react';
import ConsciousnessPage from '../page';
import { WebSocketState } from '../hooks/websocket-types';

// Mock all the complex visualization components
jest.mock('../components/PixiCanvas', () => ({
  PixiCanvas: () => <div data-testid="pixi-canvas">Pixi Canvas</div>,
}));

jest.mock('../components/SubEntityGraphView', () => ({
  SubEntityGraphView: () => <div data-testid="subentity-graph">SubEntity Graph</div>,
}));

jest.mock('../components/SubEntityClusterOverlay', () => ({
  SubEntityClusterOverlay: () => <div data-testid="cluster-overlay">Cluster Overlay</div>,
}));

jest.mock('../components/EnergyFlowParticles', () => ({
  EnergyFlowParticles: () => <div data-testid="energy-particles">Energy Particles</div>,
}));

jest.mock('../components/ActivationBubbles', () => ({
  ActivationBubbles: () => <div data-testid="activation-bubbles">Activation Bubbles</div>,
}));

jest.mock('../components/Tooltip', () => ({
  Tooltip: () => <div data-testid="tooltip">Tooltip</div>,
}));

jest.mock('../components/DetailPanel', () => ({
  DetailPanel: () => <div data-testid="detail-panel">Detail Panel</div>,
}));

jest.mock('../components/Legend', () => ({
  Legend: () => <div data-testid="legend">Legend</div>,
}));

jest.mock('../components/Header', () => ({
  Header: () => <div data-testid="header">Header</div>,
}));

jest.mock('../components/LeftSidebarMenu', () => ({
  LeftSidebarMenu: () => <div data-testid="left-sidebar">Left Sidebar</div>,
}));

jest.mock('../components/ChatPanel', () => ({
  ChatPanel: () => <div data-testid="chat-panel">Chat Panel</div>,
}));

jest.mock('../components/GraphChatInterface', () => ({
  GraphChatInterface: () => <div data-testid="graph-chat">Graph Chat</div>,
}));

jest.mock('../components/ForgedIdentityViewer', () => ({
  ForgedIdentityViewer: () => <div data-testid="forged-identity">Forged Identity</div>,
}));

// Mock useWebSocket hook with empty data
jest.mock('../hooks/useWebSocket', () => ({
  useWebSocket: jest.fn(() => ({
    subentityActivity: [],
    thresholdCrossings: [],
    v2State: {
      workingMemory: new Map(),
      linkFlows: new Map(),
      recentFlips: new Set(),
    },
    emotionState: {
      valence: 0,
      arousal: 0,
      dominance: 0,
      recentStrides: [],
    },
    weightLearningEvents: [],
    strideSelectionEvents: [],
    phenomenologyMismatchEvents: [],
    phenomenologyHealthEvents: [],
    forgedIdentityFrames: [],
    forgedIdentityMetrics: null,
    connectionState: WebSocketState.CONNECTED,
    error: null,
    graphNodes: [],
    graphLinks: [],
    graphSubentities: [],
    hierarchySnapshot: null,
    economyOverlays: {},
  })),
}));

describe('ConsciousnessPage', () => {
  it('renders without crashing', () => {
    render(<ConsciousnessPage />);
    expect(screen.getByTestId('header')).toBeInTheDocument();
  });

  it('renders all major visualization components', () => {
    render(<ConsciousnessPage />);

    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('pixi-canvas')).toBeInTheDocument();
    expect(screen.getByTestId('subentity-graph')).toBeInTheDocument();
    expect(screen.getByTestId('cluster-overlay')).toBeInTheDocument();
    expect(screen.getByTestId('energy-particles')).toBeInTheDocument();
    expect(screen.getByTestId('activation-bubbles')).toBeInTheDocument();
    expect(screen.getByTestId('detail-panel')).toBeInTheDocument();
    expect(screen.getByTestId('graph-chat')).toBeInTheDocument();
  });

  it('renders utility components', () => {
    render(<ConsciousnessPage />);

    expect(screen.getByTestId('tooltip')).toBeInTheDocument();
    expect(screen.getByTestId('legend')).toBeInTheDocument();
    expect(screen.getByTestId('left-sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('chat-panel')).toBeInTheDocument();
  });

  it('does not render forged identity viewer by default', () => {
    render(<ConsciousnessPage />);
    expect(screen.queryByTestId('forged-identity')).not.toBeInTheDocument();
  });

  it('applies correct background class', () => {
    const { container } = render(<ConsciousnessPage />);
    const mainDiv = container.firstChild as HTMLElement;
    expect(mainDiv).toHaveClass('bg-observatory-dark');
  });

  it('has proper layout structure', () => {
    const { container } = render(<ConsciousnessPage />);
    const mainDiv = container.firstChild as HTMLElement;

    expect(mainDiv).toHaveClass('relative');
    expect(mainDiv).toHaveClass('w-full');
    expect(mainDiv).toHaveClass('h-screen');
    expect(mainDiv).toHaveClass('overflow-hidden');
  });
});

describe('ConsciousnessPage - Error Handling', () => {
  it('displays error overlay when WebSocket error occurs', () => {
    const { useWebSocket } = require('../hooks/useWebSocket');
    useWebSocket.mockImplementation(() => ({
      subentityActivity: [],
      thresholdCrossings: [],
      v2State: {
        workingMemory: new Map(),
        linkFlows: new Map(),
        recentFlips: new Set(),
      },
      emotionState: {
        valence: 0,
        arousal: 0,
        dominance: 0,
        recentStrides: [],
      },
      weightLearningEvents: [],
      strideSelectionEvents: [],
      phenomenologyMismatchEvents: [],
      phenomenologyHealthEvents: [],
      forgedIdentityFrames: [],
      forgedIdentityMetrics: null,
      connectionState: WebSocketState.ERROR,
      error: 'WebSocket connection failed',
      graphNodes: [],
      graphLinks: [],
      graphSubentities: [],
      hierarchySnapshot: null,
      economyOverlays: {},
    }));

    render(<ConsciousnessPage />);
    expect(screen.getByTestId('error-overlay')).toBeInTheDocument();
    expect(screen.getByText('WebSocket connection failed')).toBeInTheDocument();
  });
});
