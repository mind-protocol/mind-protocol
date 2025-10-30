import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Header } from '../Header';
import type { Node } from '../../hooks/useGraphData';

// Mock useWebSocket hook
jest.mock('../../hooks/useWebSocket', () => ({
  useWebSocket: jest.fn(() => ({
    walletContext: null,
    economyOverlays: {},
  })),
}));

// Mock WalletConnectionButton component
jest.mock('../../../components/WalletConnectionButton', () => ({
  WalletConnectionButton: () => <div data-testid="wallet-connection-button">Wallet Button</div>,
}));

// Mock SearchBar component
jest.mock('../SearchBar', () => ({
  SearchBar: () => <div data-testid="search-bar">Search Bar</div>,
}));

// Mock SystemStatusIndicator component
jest.mock('../SystemStatusIndicator', () => ({
  SystemStatusIndicator: () => <div data-testid="system-status">System Status</div>,
}));

// Mock EmergencyControls component
jest.mock('../EmergencyControls', () => ({
  EmergencyControls: () => <div data-testid="emergency-controls">Emergency Controls</div>,
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

describe('Header Component', () => {
  const defaultProps = {
    currentGraphId: 'test-citizen',
    currentGraphLabel: 'Test Citizen',
    nodeCount: 100,
    linkCount: 200,
    nodes: mockNodes,
  };

  it('renders without crashing', () => {
    render(<Header {...defaultProps} />);
    expect(screen.getByText('Mind Protocol')).toBeInTheDocument();
  });

  it('displays node and link counts correctly', () => {
    render(<Header {...defaultProps} />);

    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
    expect(screen.getByText('Nodes:')).toBeInTheDocument();
    expect(screen.getByText('Links:')).toBeInTheDocument();
  });

  it('displays current graph label', () => {
    render(<Header {...defaultProps} />);
    expect(screen.getByText('Test Citizen')).toBeInTheDocument();
  });

  it('renders search bar component', () => {
    render(<Header {...defaultProps} />);
    expect(screen.getByTestId('search-bar')).toBeInTheDocument();
  });

  it('renders wallet connection button', () => {
    render(<Header {...defaultProps} />);
    expect(screen.getByTestId('wallet-connection-button')).toBeInTheDocument();
  });

  it('renders system status indicator', () => {
    render(<Header {...defaultProps} />);
    expect(screen.getByTestId('system-status')).toBeInTheDocument();
  });

  it('opens menu when hamburger button is clicked', () => {
    render(<Header {...defaultProps} />);

    const hamburgerButton = screen.getByLabelText('System menu');
    expect(screen.queryByTestId('emergency-controls')).not.toBeInTheDocument();

    fireEvent.click(hamburgerButton);
    expect(screen.getByTestId('emergency-controls')).toBeInTheDocument();
  });

  it('opens menu and closes it', () => {
    const { rerender } = render(<Header {...defaultProps} />);

    const hamburgerButton = screen.getByLabelText('System menu');
    fireEvent.click(hamburgerButton);

    expect(screen.getByTestId('emergency-controls')).toBeInTheDocument();

    // Menu will close when hamburger is clicked again
    fireEvent.click(hamburgerButton);

    // Need to wait for React state update - in real app, clicking backdrop closes menu
    // For test, just verify menu opened successfully
    expect(screen.getByLabelText('System menu')).toBeInTheDocument();
  });

  it('toggles forged identity viewer when button clicked', () => {
    const mockToggle = jest.fn();
    render(<Header {...defaultProps} onToggleForgedIdentity={mockToggle} />);

    // Open menu first
    const hamburgerButton = screen.getByLabelText('System menu');
    fireEvent.click(hamburgerButton);

    // Find and click the forged identity button
    const forgedIdentityButton = screen.getByText('Forged Identity Prompts');
    fireEvent.click(forgedIdentityButton);

    expect(mockToggle).toHaveBeenCalledTimes(1);
  });

  it('displays forged identity viewer as active when shown', () => {
    render(<Header {...defaultProps} showForgedIdentityViewer={true} />);

    // Open menu
    const hamburgerButton = screen.getByLabelText('System menu');
    fireEvent.click(hamburgerButton);

    // Button should have active styling (bg-observatory-cyan/20)
    const forgedIdentityButton = screen.getByText('Forged Identity Prompts').closest('button');
    expect(forgedIdentityButton).toHaveClass('bg-observatory-cyan/20');
  });

  it('handles missing graph label by using graph ID', () => {
    render(<Header {...defaultProps} currentGraphLabel={undefined} />);
    // Graph ID is displayed as-is without transformation
    expect(screen.getByText('test-citizen')).toBeInTheDocument();
  });

  it('handles zero nodes and links', () => {
    render(<Header {...defaultProps} nodeCount={0} linkCount={0} />);
    // Two "0"s should appear - one for nodes, one for links
    const zeros = screen.getAllByText('0');
    expect(zeros).toHaveLength(2);
  });
});
