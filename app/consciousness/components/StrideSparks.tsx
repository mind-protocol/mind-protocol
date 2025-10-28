/**
 * Stride Sparks Component
 *
 * Animates tiny "sparks" along edges when stride.exec events fire.
 * Makes consciousness traversal VISIBLE in real-time.
 *
 * Per visualization_patterns.md § 2.2:
 * - Tiny "spark" along edges for sampled stride.exec
 * - Shows actual movement through graph
 * - Color-coded by entity
 * - Respects sampling rate
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 */

'use client';

import { useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import type { Node, Link } from '../hooks/useGraphData';

interface StrideSparkProps {
  nodes: Node[];
  links: Link[];
}

interface Spark {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  progress: number;  // 0 to 1
  color: string;
  entityId: string;
  timestamp: number;
}

const SPARK_DURATION_MS = 500;  // How long spark takes to traverse edge
const SPARK_CLEANUP_MS = 600;   // When to remove finished sparks

/**
 * Stride Sparks
 *
 * Canvas overlay that animates particles along edges during traversal.
 */
export function StrideSparks({ nodes, links }: StrideSparkProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sparksRef = useRef<Spark[]>([]);
  const animationFrameRef = useRef<number | null>(null);

  const { emotionState } = useWebSocket();

  // Build node position lookup
  const nodePositions = useRef<Map<string, { x: number; y: number }>>(new Map());

  useEffect(() => {
    // Update node positions
    nodePositions.current.clear();
    nodes.forEach(node => {
      const nodeId = node.id || node.node_id;
      if (nodeId && node.x !== undefined && node.y !== undefined) {
        nodePositions.current.set(nodeId, { x: node.x, y: node.y });
      }
    });
  }, [nodes]);

  // Listen for stride.exec events and create sparks
  useEffect(() => {
    // Subscribe to stride events from emotionState.recentStrides
    // New strides are appended to the array
    const lastStride = emotionState.recentStrides[emotionState.recentStrides.length - 1];
    if (!lastStride) return;

    const sourcePos = nodePositions.current.get(lastStride.source_node_id);
    const targetPos = nodePositions.current.get(lastStride.target_node_id);

    if (!sourcePos || !targetPos) return;

    // Create new spark
    const spark: Spark = {
      id: `${lastStride.subentity_id}-${lastStride.source_node_id}-${lastStride.target_node_id}-${Date.now()}`,
      sourceX: sourcePos.x,
      sourceY: sourcePos.y,
      targetX: targetPos.x,
      targetY: targetPos.y,
      progress: 0,
      color: getEntityColor(lastStride.subentity_id),
      entityId: lastStride.subentity_id,
      timestamp: Date.now()
    };

    sparksRef.current.push(spark);
  }, [emotionState.recentStrides]);

  // Animation loop
  useEffect(() => {
    // Guard against SSR
    if (typeof window === 'undefined') return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const animate = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const now = Date.now();

      // Update and draw sparks
      sparksRef.current = sparksRef.current.filter(spark => {
        const elapsed = now - spark.timestamp;

        // Remove old sparks
        if (elapsed > SPARK_CLEANUP_MS) {
          return false;
        }

        // Update progress (0 to 1)
        spark.progress = Math.min(elapsed / SPARK_DURATION_MS, 1);

        // Interpolate position along edge
        const x = spark.sourceX + (spark.targetX - spark.sourceX) * spark.progress;
        const y = spark.sourceY + (spark.targetY - spark.sourceY) * spark.progress;

        // Calculate opacity (fade in/out)
        let opacity = 1;
        if (spark.progress < 0.2) {
          // Fade in
          opacity = spark.progress / 0.2;
        } else if (spark.progress > 0.8) {
          // Fade out
          opacity = (1 - spark.progress) / 0.2;
        }

        // Draw spark
        ctx.save();
        ctx.globalAlpha = opacity;

        // Spark glow
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 6);
        gradient.addColorStop(0, spark.color);
        gradient.addColorStop(1, 'rgba(0,0,0,0)');

        ctx.fillStyle = gradient;
        ctx.fillRect(x - 6, y - 6, 12, 12);

        // Spark core
        ctx.fillStyle = spark.color;
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        return true;  // Keep spark
      });

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none z-30"
      style={{ mixBlendMode: 'screen' }}
    />
  );
}

/**
 * Get entity color for spark
 */
function getEntityColor(entityId: string): string {
  // Simple hash-based color assignment
  // Could be replaced with actual entity colors from palette
  const colors = [
    '#5efc82', // consciousness green
    '#3b82f6', // blue
    '#8b5cf6', // purple
    '#f59e0b', // amber
    '#ec4899', // pink
    '#10b981', // emerald
  ];

  let hash = 0;
  for (let i = 0; i < entityId.length; i++) {
    hash = ((hash << 5) - hash) + entityId.charCodeAt(i);
    hash = hash & hash;
  }

  return colors[Math.abs(hash) % colors.length];
}
