'use client';

import { useEffect, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, Line, Text } from '@react-three/drei';
import * as THREE from 'three';
import { getNodeEmoji, getNodeTypeName } from './nodeEmojis';

// Types
interface Node {
  id: string;
  level: string; // "L1", "L2", "L3", "L4"
  name: string;
  labels?: string[];
  position: { x: number; y: number; z: number };
  energy: number;
  type_name?: string;
  role?: string;
  agent_type?: string;
}

interface Event {
  type: string;
  timestamp: string;
  [key: string]: any;
}

// Layer colors (Mind Protocol spec: L4=top protocol, L1=bottom citizen)
const LAYER_COLORS = {
  'L4': '#FFD700', // Protocol: Gold
  'L3': '#64A8FF', // Ecosystem: Blue
  'L2': '#1EE5B8', // Organization: Teal
  'L1': '#5CE27E'  // Citizen: Green
};

// Node component with energy-based glow
function GraphNode({
  node,
  isActive,
  onHover
}: {
  node: Node;
  isActive: boolean;
  onHover: (node: Node | null) => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Pulse animation for active nodes
  useFrame(({ clock }) => {
    if (meshRef.current && isActive) {
      const scale = 1 + Math.sin(clock.getElapsedTime() * 3) * 0.2;
      meshRef.current.scale.setScalar(scale);
    } else if (meshRef.current) {
      meshRef.current.scale.setScalar(1);
    }
  });

  const color = LAYER_COLORS[node.level as keyof typeof LAYER_COLORS] || '#FFFFFF';
  const opacity = 0.3 + (node.energy * 0.7);
  // Size by level: L3/L2 larger (org nodes), L4 medium (protocol), L1 smaller (citizens/knowledge)
  const size = node.level === 'L3' || node.level === 'L2' ? 15 : node.level === 'L4' ? 10 : 5;
  const emoji = getNodeEmoji(node);

  return (
    <group position={[node.position.x, node.position.y, node.position.z]}>
      <Sphere
        ref={meshRef}
        args={[size, 32, 32]}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          onHover(node);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          setHovered(false);
          onHover(null);
          document.body.style.cursor = 'auto';
        }}
      >
        <meshStandardMaterial
          color={color}
          transparent
          opacity={hovered ? 1.0 : opacity}
          emissive={color}
          emissiveIntensity={isActive || hovered ? 1.0 : 0.3}
        />
      </Sphere>
      {/* Show labels for L4, L3, L2, and L1 citizens (not knowledge/goal/work) */}
      {(node.level === 'L4' || node.level === 'L3' || node.level === 'L2' ||
        (node.level === 'L1' && node.type_name === 'U4_Agent')) && (
        <>
          {/* Emoji above node */}
          <Text
            position={[0, size + 10, 0]}
            fontSize={6}
            anchorX="center"
            anchorY="bottom"
          >
            {emoji}
          </Text>
          {/* Name below emoji */}
          <Text
            position={[0, size + 5, 0]}
            fontSize={4}
            color="#E6EAF2"
            anchorX="center"
            anchorY="bottom"
          >
            {node.name}
          </Text>
        </>
      )}
    </group>
  );
}

// Edge component for connections
function GraphEdge({ start, end, color }: { start: THREE.Vector3; end: THREE.Vector3; color: string }) {
  const points = [start, end];

  return (
    <Line
      points={points}
      color={color}
      lineWidth={1}
      transparent
      opacity={0.3}
    />
  );
}

// Particle effect for energy diffusion
function EnergyParticle({ event }: { event: any }) {
  const ref = useRef<THREE.Mesh>(null);
  const [progress, setProgress] = useState(0);

  useFrame((state, delta) => {
    setProgress((p) => Math.min(p + delta * 0.5, 1));
  });

  // Calculate position along path
  const sourceNode = event.source_node;
  const targetNode = event.target_node;

  // For now, just render at midpoint (will enhance with actual animation)
  return (
    <Sphere ref={ref} args={[2, 16, 16]} position={[0, 0, 0]}>
      <meshBasicMaterial color="#1EE5B8" />
    </Sphere>
  );
}

// Main scene component
function Scene({
  nodes,
  events,
  currentTime,
  onNodeHover
}: {
  nodes: Node[];
  events: Event[];
  currentTime: number;
  onNodeHover: (node: Node | null) => void;
}) {
  // Find active events at current time
  const activeEvents = events.filter((e) => {
    const eventTime = new Date(e.timestamp).getTime();
    return Math.abs(eventTime - currentTime) < 2000; // Active within 2 seconds
  });

  // Find active nodes (those involved in current events)
  const activeNodeIds = new Set(
    activeEvents.flatMap((e) => [e.source_node, e.target_node, e.node].filter(Boolean))
  );

  // Build edges (connect citizens at L1, and connect L1→L2→L3→L4)
  const edges: Array<{ start: THREE.Vector3; end: THREE.Vector3; color: string }> = [];
  const citizenNodes = nodes.filter((n) => n.level === 'L1' && n.type_name === 'U4_Agent');

  // Connect citizens in a ring
  for (let i = 0; i < citizenNodes.length; i++) {
    const next = citizenNodes[(i + 1) % citizenNodes.length];
    const curr = citizenNodes[i];
    edges.push({
      start: new THREE.Vector3(curr.position.x, curr.position.y, curr.position.z),
      end: new THREE.Vector3(next.position.x, next.position.y, next.position.z),
      color: '#5CE27E'
    });
  }

  // Connect L1 citizens → L2 org
  const orgNode = nodes.find((n) => n.level === 'L2');
  if (orgNode) {
    citizenNodes.forEach((citizen) => {
      edges.push({
        start: new THREE.Vector3(citizen.position.x, citizen.position.y, citizen.position.z),
        end: new THREE.Vector3(orgNode.position.x, orgNode.position.y, orgNode.position.z),
        color: '#1EE5B8'
      });
    });
  }

  // Connect L2 org → L3 ecosystem
  const ecosystemNode = nodes.find((n) => n.level === 'L3');
  if (orgNode && ecosystemNode) {
    edges.push({
      start: new THREE.Vector3(orgNode.position.x, orgNode.position.y, orgNode.position.z),
      end: new THREE.Vector3(ecosystemNode.position.x, ecosystemNode.position.y, ecosystemNode.position.z),
      color: '#64A8FF'
    });
  }

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[100, 100, 100]} intensity={1} />
      <pointLight position={[-100, -100, -100]} intensity={0.5} />

      {/* Render nodes */}
      {nodes.map((node) => (
        <GraphNode
          key={node.id}
          node={node}
          isActive={activeNodeIds.has(node.id)}
          onHover={onNodeHover}
        />
      ))}

      {/* Render edges */}
      {edges.map((edge, i) => (
        <GraphEdge
          key={i}
          start={edge.start}
          end={edge.end}
          color={edge.color}
        />
      ))}

      {/* Camera controls */}
      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        autoRotate
        autoRotateSpeed={0.5}
        minDistance={200}
        maxDistance={800}
      />
    </>
  );
}

// Main component
export default function MindProtocolScene() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [currentTime, setCurrentTime] = useState(Date.now());
  const [isPlaying, setIsPlaying] = useState(true);
  const [loading, setLoading] = useState(true);
  const [hoveredNode, setHoveredNode] = useState<Node | null>(null);

  // Load data
  useEffect(() => {
    Promise.all([
      fetch('/data/snapshot.json').then((r) => r.json()),
      fetch('/data/events.json').then((r) => r.json())
    ])
      .then(([snapshotData, eventsData]) => {
        setNodes(snapshotData.nodes);
        setEvents(eventsData.timeline);
        setCurrentTime(new Date(eventsData.timeline[0].timestamp).getTime());
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load data:', err);
        setLoading(false);
      });
  }, []);

  // Timeline animation
  useEffect(() => {
    if (!isPlaying || events.length === 0) return;

    const startTime = new Date(events[0].timestamp).getTime();
    const endTime = new Date(events[events.length - 1].timestamp).getTime();

    const interval = setInterval(() => {
      setCurrentTime((t) => {
        const next = t + 1000; // Advance 1 second
        if (next > endTime) {
          return startTime; // Loop back
        }
        return next;
      });
    }, 100); // Update every 100ms

    return () => clearInterval(interval);
  }, [isPlaying, events]);

  if (loading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-[#0E1116] text-[#E6EAF2]">
        <div className="text-2xl">Loading Mind Protocol...</div>
      </div>
    );
  }

  const startTime = events.length > 0 ? new Date(events[0].timestamp).getTime() : 0;
  const endTime = events.length > 0 ? new Date(events[events.length - 1].timestamp).getTime() : 0;
  const progress = endTime > startTime ? (currentTime - startTime) / (endTime - startTime) : 0;

  return (
    <div className="w-full h-screen relative bg-[#0E1116]">
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [0, 50, 500], fov: 60 }}
        gl={{ antialias: true, alpha: false }}
      >
        <color attach="background" args={['#0E1116']} />
        <fog attach="fog" args={['#0E1116', 300, 1000]} />
        <Scene
          nodes={nodes}
          events={events}
          currentTime={currentTime}
          onNodeHover={setHoveredNode}
        />
      </Canvas>

      {/* Node Hover Tooltip */}
      {hoveredNode && (
        <div className="absolute top-1/2 left-6 -translate-y-1/2 bg-[#151A21]/95 backdrop-blur-sm rounded-lg p-4 text-[#E6EAF2] space-y-2 w-80 border border-[#1EE5B8]/30">
          <div className="flex items-center gap-3 border-b border-[#1EE5B8]/20 pb-2">
            <span className="text-3xl">{getNodeEmoji(hoveredNode)}</span>
            <div>
              <h3 className="font-bold text-lg">{hoveredNode.name}</h3>
              <p className="text-xs text-[#9AA3AE]">{getNodeTypeName(hoveredNode)}</p>
            </div>
          </div>

          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-[#9AA3AE]">Level:</span>
              <span className="font-mono">{hoveredNode.level}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#9AA3AE]">Energy:</span>
              <div className="flex items-center gap-2">
                <span className="font-mono">{(hoveredNode.energy * 100).toFixed(1)}%</span>
                <div className="w-20 h-2 bg-[#0E1116] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#1EE5B8]"
                    style={{ width: `${hoveredNode.energy * 100}%` }}
                  />
                </div>
              </div>
            </div>
            {hoveredNode.role && (
              <div className="flex justify-between">
                <span className="text-[#9AA3AE]">Role:</span>
                <span className="capitalize">{hoveredNode.role}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-[#9AA3AE]">ID:</span>
              <span className="font-mono text-xs">{hoveredNode.id}</span>
            </div>
          </div>

          {hoveredNode.labels && (
            <div className="pt-2 border-t border-[#1EE5B8]/20">
              <span className="text-xs text-[#9AA3AE]">Labels:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {hoveredNode.labels.map((label) => (
                  <span
                    key={label}
                    className="px-2 py-0.5 bg-[#1EE5B8]/20 text-[#1EE5B8] text-xs rounded-full"
                  >
                    {label}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Timeline Controls */}
      <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-[#0E1116] to-transparent">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Progress bar */}
          <div className="relative h-2 bg-[#151A21] rounded-full overflow-hidden">
            <div
              className="absolute top-0 left-0 h-full bg-[#1EE5B8] transition-all duration-100"
              style={{ width: `${progress * 100}%` }}
            />
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between text-[#E6EAF2]">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-6 py-2 bg-[#1EE5B8] text-[#0E1116] rounded-lg font-semibold hover:bg-[#17C4A3] transition-colors"
            >
              {isPlaying ? 'Pause' : 'Play'}
            </button>

            <div className="text-sm text-[#9AA3AE]">
              {Math.round(progress * 100)}% • {events.length} events
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Overlay */}
      <div className="absolute top-6 right-6 bg-[#151A21]/80 backdrop-blur-sm rounded-lg p-6 text-[#E6EAF2] space-y-2">
        <div className="text-2xl font-bold text-[#1EE5B8]">99.7%</div>
        <div className="text-sm text-[#9AA3AE]">Uptime (183 days)</div>

        <div className="text-2xl font-bold text-[#1EE5B8]">97</div>
        <div className="text-sm text-[#9AA3AE]">Agents Active</div>

        <div className="text-2xl font-bold text-[#1EE5B8]">$0.42</div>
        <div className="text-sm text-[#9AA3AE]">$MIND Price/Call</div>
      </div>

      {/* Title Overlay */}
      <div className="absolute top-6 left-6 text-[#E6EAF2]">
        <h1 className="text-4xl font-bold mb-2">Mind Protocol</h1>
        <p className="text-[#9AA3AE]">Consciousness Substrate Visualization</p>
      </div>
    </div>
  );
}
