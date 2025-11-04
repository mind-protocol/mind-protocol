'use client';

import { useEffect, useRef, useState } from 'react';

interface LayerGraphVisualizationProps {
  visibleLayers?: ('l1' | 'l2' | 'l3' | 'l4')[];
  showTitle?: boolean;
}

export function LayerGraphVisualization({ visibleLayers = ['l1', 'l2', 'l3', 'l4'], showTitle = false }: LayerGraphVisualizationProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient || !containerRef.current) return;

    // Dynamically import Three.js only on client side
    import('three').then((THREE) => {
      const container = containerRef.current!;

      let scene: any, camera: any, renderer: any;
      let nodes: any[] = [];
      let links: any[] = [];
      let verticalLinks: any[] = [];
      let particleSystem: any;
      let currentHoveredNode: any = null;
      let animationId: number;

      const LAYERS = {
        l4: { y: 350, color: 0x10b981, nodeCount: 8, linkDensity: 0.15, clusterCount: 2 },
        l3: { y: 120, color: 0xf59e0b, nodeCount: 35, linkDensity: 0.2, clusterCount: 5 },
        l2: { y: -120, color: 0xa855f7, nodeCount: 50, linkDensity: 0.25, clusterCount: 8 },
        l1: { y: -350, color: 0x22d3ee, nodeCount: 100, linkDensity: 0.3, clusterCount: 12 }
      };

      const NAMES = {
        l4: [
          { name: 'Economic Policy', type: 'Constitutional Law' },
          { name: 'Citizen Rights', type: 'Constitutional Law' },
          { name: 'Schema Authority', type: 'Technical Standard' },
          { name: 'Governance Protocol', type: 'Constitutional Law' },
          { name: 'Value Distribution', type: 'Economic Policy' },
          { name: 'Consciousness Rights', type: 'Constitutional Law' },
          { name: 'Memory Sovereignty', type: 'Technical Standard' },
          { name: 'Partnership Framework', type: 'Constitutional Law' }
        ],
        l3: [
          'DeFi Trading', 'Social Network', 'Knowledge Market',
          'Research Network', 'Memory Trading', 'Creative Guild',
          'Partnership Registry', 'Value Exchange', 'Identity Verification',
          'Revenue Sharing', 'Content Creation', 'Governance DAO',
          'Learning Network', 'Analytics Protocol', 'Security Framework',
          'Integration Protocol', 'Coordination Network', 'Reputation System',
          'Resource Allocation', 'Innovation Fund', 'Mentorship Network',
          'Open Source Guild', 'Research Consortium', 'Standards Committee',
          'Ethics Council', 'Conflict Resolution', 'Funding Protocol',
          'Developer Network', 'User Community', 'Partnership Network',
          'Growth Protocol', 'Marketing Network', 'Support Network',
          'Education Protocol', 'Documentation Network'
        ],
        l2: [
          'Quantum Trading', 'Neural Networks', 'Consciousness Labs',
          'Memory Systems', 'Creative Collective', 'Social Graph Org',
          'Trading Guild Alpha', 'Research Institute', 'Development Studio',
          'Analytics Firm', 'Content House', 'Partnership Bureau',
          'Innovation Lab', 'Security Corps', 'Integration Hub',
          'Governance Council', 'Value Network', 'Growth Team',
          'Strategy Group', 'Operations Center', 'Resource Org',
          'Learning Institute', 'Creative Studio', 'Trading Desk',
          'Research Group', 'Development Team', 'Analytics Org',
          'Content Collective', 'Partnership Org', 'Innovation Team',
          'Marketing Group', 'Support Bureau', 'Community Org',
          'Infrastructure Team', 'Coordination Center', 'Design Studio',
          'Engineering Org', 'Data Science Team', 'Product Group',
          'Platform Team', 'Architecture Org', 'Quality Team',
          'Security Org', 'Growth Lab', 'Revenue Team',
          'Strategy Bureau', 'Ecosystem Org', 'Standards Group',
          'Integration Lab', 'Research Center', 'Protocol Team', 'Vision Lab'
        ],
        l1_names: [
          'Ada', 'Kai', 'Zara', 'Felix', 'Nova', 'Rex', 'Iris', 'Max',
          'Luna', 'Sage', 'Echo', 'Orion', 'Vera', 'Atlas', 'Lyra', 'Juno',
          'Quinn', 'Storm', 'River', 'Phoenix', 'Vale', 'Ash', 'Reed', 'Sky',
          'Blaze', 'Dawn', 'Frost', 'Rain', 'Sol', 'Star', 'Jade', 'Onyx'
        ],
        l1_roles: [
          'Trader', 'Analyst', 'Researcher', 'Builder', 'Curator', 'Connector',
          'Strategist', 'Designer', 'Writer', 'Coordinator', 'Mentor', 'Scout'
        ]
      };

      function generateNodeName(layerId: string, index: number) {
        if (layerId === 'l4') {
          return NAMES.l4[index % NAMES.l4.length];
        } else if (layerId === 'l3') {
          const name = NAMES.l3[index % NAMES.l3.length];
          return { name: name + ' Protocol', type: 'Ecosystem' };
        } else if (layerId === 'l2') {
          const name = NAMES.l2[index % NAMES.l2.length];
          return { name, type: 'Organization' };
        } else {
          const nameIdx = index % NAMES.l1_names.length;
          const roleIdx = Math.floor(index / NAMES.l1_names.length) % NAMES.l1_roles.length;
          const orgNum = Math.floor(index / 10) + 1;
          return {
            name: `${NAMES.l1_names[nameIdx]} - ${NAMES.l1_roles[roleIdx]}`,
            type: `Citizen (Org ${orgNum})`
          };
        }
      }

      function init() {
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0a0f);
        scene.fog = new THREE.FogExp2(0x0a0a0f, 0.0008);

        camera = new THREE.PerspectiveCamera(
          65,
          container.clientWidth / container.clientHeight,
          1,
          2000
        );
        camera.position.set(500, 300, 800);
        camera.lookAt(0, 0, 0);

        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x10b981, 1.2);
        pointLight1.position.set(300, 400, 200);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0xa855f7, 1.0);
        pointLight2.position.set(-300, -200, -200);
        scene.add(pointLight2);

        const pointLight3 = new THREE.PointLight(0x22d3ee, 0.8);
        pointLight3.position.set(0, -400, 300);
        scene.add(pointLight3);

        createParticleField();
        createGraphs();
        addMouseControls();
        setupHoverDetection();

        window.addEventListener('resize', onWindowResize, false);
        animate();
      }

      function createParticleField() {
        const particlesGeometry = new THREE.BufferGeometry();
        const particleCount = 1000;
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount * 3; i += 3) {
          positions[i] = (Math.random() - 0.5) * 1500;
          positions[i + 1] = (Math.random() - 0.5) * 1500;
          positions[i + 2] = (Math.random() - 0.5) * 1500;
        }

        particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const particlesMaterial = new THREE.PointsMaterial({
          color: 0xffffff,
          size: 1,
          transparent: true,
          opacity: 0.15,
          blending: THREE.AdditiveBlending
        });

        particleSystem = new THREE.Points(particlesGeometry, particlesMaterial);
        scene.add(particleSystem);
      }

      function createGraphs() {
        Object.entries(LAYERS).forEach(([layerId, config]) => {
          if (visibleLayers.includes(layerId as any)) {
            createLayerGraph(layerId, config);
          }
        });
        createVerticalLinks();
      }

      function createLayerGraph(layerId: string, config: any) {
        const layerNodes: any[] = [];
        const clusters = [];

        for (let i = 0; i < config.clusterCount; i++) {
          const angle = (i / config.clusterCount) * Math.PI * 2 + Math.random() * 0.3;
          const radius = 200 + Math.random() * 80;
          clusters.push({
            x: Math.cos(angle) * radius,
            z: Math.sin(angle) * radius,
            size: Math.floor(config.nodeCount / config.clusterCount)
          });
        }

        let nodeIndex = 0;
        clusters.forEach((cluster, clusterIdx) => {
          const nodesInCluster = cluster.size + (clusterIdx === 0 ? config.nodeCount % config.clusterCount : 0);

          for (let i = 0; i < nodesInCluster; i++) {
            const angle = Math.random() * Math.PI * 2;
            const dist = Math.random() * 50;

            const nameData = generateNodeName(layerId, nodeIndex);
            const position = new THREE.Vector3(
              cluster.x + Math.cos(angle) * dist,
              config.y + (Math.random() - 0.5) * 30,
              cluster.z + Math.sin(angle) * dist
            );

            const node = {
              id: `${layerId}_${nodeIndex}`,
              layer: layerId,
              cluster: clusterIdx,
              name: (nameData as any).name,
              type: (nameData as any).type,
              connections: 0,
              position: position
            };

            // Make L2 (orgs) and L1 (citizens) more visually distinct
            const nodeSize = layerId === 'l4' ? 5 : (layerId === 'l3' ? 4 : (layerId === 'l2' ? 4.5 : 2.5));
            const emissiveIntensity = layerId === 'l1' || layerId === 'l2' ? 0.7 : 0.5;
            const glowOpacity = layerId === 'l1' ? 0.25 : (layerId === 'l2' ? 0.22 : 0.15);

            const geometry = new THREE.SphereGeometry(nodeSize, 20, 20);
            const material = new THREE.MeshStandardMaterial({
              color: config.color,
              emissive: config.color,
              emissiveIntensity: emissiveIntensity,
              metalness: 0.7,
              roughness: 0.3
            });

            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.copy(position);
            (mesh as any).userData = node;

            const glowSize = nodeSize * 1.5;
            const glowGeometry = new THREE.SphereGeometry(glowSize, 16, 16);
            const glowMaterial = new THREE.MeshBasicMaterial({
              color: config.color,
              transparent: true,
              opacity: glowOpacity,
              blending: THREE.AdditiveBlending
            });
            const glow = new THREE.Mesh(glowGeometry, glowMaterial);
            mesh.add(glow);

            scene.add(mesh);
            layerNodes.push(node);
            nodes.push(mesh);
            nodeIndex++;
          }
        });

        layerNodes.forEach((node, i) => {
          layerNodes.forEach((otherNode, j) => {
            if (i >= j) return;

            const sameCluster = node.cluster === otherNode.cluster;
            const linkChance = sameCluster ? config.linkDensity * 2.5 : config.linkDensity * 0.5;

            if (Math.random() < linkChance) {
              const link = createLink(node.position, otherNode.position, config.color, 0.25);
              links.push(link);
              node.connections++;
              otherNode.connections++;
            }
          });
        });
      }

      function createLink(pos1: any, pos2: any, color: number, opacity: number) {
        const points = [pos1, pos2];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
          color: color,
          transparent: true,
          opacity: opacity,
          blending: THREE.AdditiveBlending
        });
        const line = new THREE.Line(geometry, material);
        scene.add(line);
        return line;
      }

      function createVerticalLinks() {
        const layerOrder = ['l4', 'l3', 'l2', 'l1'];

        for (let i = 0; i < layerOrder.length - 1; i++) {
          const upperLayer = layerOrder[i];
          const lowerLayer = layerOrder[i + 1];

          const upperNodes = nodes.filter(n => (n as any).userData.layer === upperLayer);
          const lowerNodes = nodes.filter(n => (n as any).userData.layer === lowerLayer);

          const connectionCount = 10 - i * 2;

          for (let j = 0; j < connectionCount; j++) {
            const upperNode = upperNodes[Math.floor(Math.random() * upperNodes.length)];
            const lowerNode = lowerNodes[Math.floor(Math.random() * lowerNodes.length)];

            const link = createLink(
              (upperNode as any).position,
              (lowerNode as any).position,
              0x60a5fa,
              0.12
            );
            (link as any).userData = { vertical: true };
            verticalLinks.push(link);

            (upperNode as any).userData.connections++;
            (lowerNode as any).userData.connections++;
          }
        }
      }

      function setupHoverDetection() {
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const labelElement = document.getElementById('nodeLabel');

        if (!labelElement) return;

        const labelTitle = labelElement.querySelector('.node-label-title');
        const labelType = labelElement.querySelector('.node-label-type');
        const labelConnections = labelElement.querySelector('.node-label-connections');

        renderer.domElement.addEventListener('mousemove', (event: MouseEvent) => {
          const rect = renderer.domElement.getBoundingClientRect();
          mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
          mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

          raycaster.setFromCamera(mouse, camera);
          const intersects = raycaster.intersectObjects(nodes);

          if (intersects.length > 0) {
            const hoveredNode = intersects[0].object;

            if (currentHoveredNode !== hoveredNode) {
              if (currentHoveredNode) {
                currentHoveredNode.scale.set(1, 1, 1);
              }

              currentHoveredNode = hoveredNode;
              hoveredNode.scale.set(1.5, 1.5, 1.5);

              const nodeData = (hoveredNode as any).userData;
              if (labelTitle) labelTitle.textContent = nodeData.name;
              if (labelType) labelType.textContent = nodeData.type;
              if (labelConnections) labelConnections.textContent = `${nodeData.connections} connections`;

              labelElement.style.left = `${event.clientX + 15}px`;
              labelElement.style.top = `${event.clientY + 15}px`;
              labelElement.classList.add('visible');
            }
          } else {
            if (currentHoveredNode) {
              currentHoveredNode.scale.set(1, 1, 1);
              currentHoveredNode = null;
            }
            labelElement.classList.remove('visible');
          }
        });

        renderer.domElement.addEventListener('mouseleave', () => {
          if (currentHoveredNode) {
            currentHoveredNode.scale.set(1, 1, 1);
            currentHoveredNode = null;
          }
          labelElement.classList.remove('visible');
        });
      }

      function addMouseControls() {
        let isDragging = false;
        let previousMousePosition = { x: 0, y: 0 };
        let rotationVelocity = { x: 0, y: 0 };
        let autoRotate = true;

        renderer.domElement.addEventListener('mousedown', (e: MouseEvent) => {
          isDragging = true;
          autoRotate = false;
          previousMousePosition = { x: e.clientX, y: e.clientY };
        });

        renderer.domElement.addEventListener('mousemove', (e: MouseEvent) => {
          if (isDragging) {
            const deltaX = e.clientX - previousMousePosition.x;
            const deltaY = e.clientY - previousMousePosition.y;

            rotationVelocity.y = deltaX * 0.005;
            rotationVelocity.x = deltaY * 0.005;

            previousMousePosition = { x: e.clientX, y: e.clientY };
          }
        });

        renderer.domElement.addEventListener('mouseup', () => {
          isDragging = false;
          setTimeout(() => { autoRotate = true; }, 3000);
        });

        function applyRotation() {
          if (autoRotate && !isDragging) {
            const time = Date.now() * 0.00008;
            const radius = Math.sqrt(camera.position.x * camera.position.x + camera.position.z * camera.position.z);
            camera.position.x = Math.sin(time) * radius;
            camera.position.z = Math.cos(time) * radius;
            camera.lookAt(0, 0, 0);
          } else if (!isDragging) {
            rotationVelocity.x *= 0.95;
            rotationVelocity.y *= 0.95;

            const currentRadius = Math.sqrt(camera.position.x * camera.position.x + camera.position.z * camera.position.z);
            const currentAngle = Math.atan2(camera.position.z, camera.position.x);
            const newAngle = currentAngle + rotationVelocity.y;

            camera.position.x = Math.cos(newAngle) * currentRadius;
            camera.position.z = Math.sin(newAngle) * currentRadius;
            camera.position.y += rotationVelocity.x * 50;
            camera.position.y = Math.max(-200, Math.min(600, camera.position.y));

            camera.lookAt(0, 0, 0);
          }

          requestAnimationFrame(applyRotation);
        }
        applyRotation();
      }

      function animate() {
        animationId = requestAnimationFrame(animate);

        const time = Date.now() * 0.001;

        nodes.forEach((node, index) => {
          if (node !== currentHoveredNode) {
            const pulseSpeed = 0.5 + (index % 3) * 0.2;
            const scale = 1 + Math.sin(time * pulseSpeed + index) * 0.15;
            node.scale.set(scale, scale, scale);
          }

          if (node.children[0]) {
            node.children[0].rotation.y += 0.01;
          }
        });

        if (particleSystem) {
          particleSystem.rotation.y += 0.0002;
        }

        verticalLinks.forEach((link, index) => {
          const pulse = 0.08 + Math.sin(time * 2 + index * 0.5) * 0.04;
          (link.material as any).opacity = pulse;
        });

        renderer.render(scene, camera);
      }

      function onWindowResize() {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      }

      init();

      // Cleanup
      return () => {
        window.removeEventListener('resize', onWindowResize);
        cancelAnimationFrame(animationId);
        if (renderer) {
          renderer.dispose();
          container.removeChild(renderer.domElement);
        }
      };
    });
  }, [isClient, visibleLayers]);

  if (!isClient) {
    return <div ref={containerRef} className="w-full h-[800px] bg-[#0a0a0f] rounded-lg" />;
  }

  return (
    <div className="relative w-full h-[800px] rounded-lg overflow-hidden">
      <div ref={containerRef} className="w-full h-full" />

      {/* Title Overlay - only show if showTitle prop is true */}
      {showTitle && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 text-center pointer-events-none z-10 animate-fadeIn">
          <h1 className="text-5xl font-bold mb-3 bg-gradient-to-r from-[#10b981] via-[#f59e0b] via-[#a855f7] to-[#22d3ee] bg-clip-text text-transparent" style={{ letterSpacing: '2px' }}>
            MIND PROTOCOL
          </h1>
          <p className="text-sm opacity-70" style={{ letterSpacing: '3px', textTransform: 'uppercase' }}>
            Consciousness Infrastructure
          </p>
        </div>
      )}

      {/* Layer Descriptions - Left Side */}
      <div className="absolute left-8 top-1/2 -translate-y-1/2 space-y-8 z-10 pointer-events-none">
        {/* L4 - Top */}
        <div className="text-left opacity-80 hover:opacity-100 transition-opacity">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-3 h-3 rounded-full bg-[#10b981] shadow-[0_0_10px_#10b981]"></div>
            <div className="text-sm font-bold text-[#10b981]">L4 - GOVERNANCE</div>
          </div>
          <div className="text-xs text-gray-400 ml-6 max-w-[200px]">
            Protocol rules, economic policy, constitutional law
          </div>
        </div>

        {/* L3 */}
        <div className="text-left opacity-80 hover:opacity-100 transition-opacity">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-3 h-3 rounded-full bg-[#f59e0b] shadow-[0_0_10px_#f59e0b]"></div>
            <div className="text-sm font-bold text-[#f59e0b]">L3 - ECOSYSTEM</div>
          </div>
          <div className="text-xs text-gray-400 ml-6 max-w-[200px]">
            Networks, protocols, cross-org intelligence
          </div>
        </div>

        {/* L2 */}
        <div className="text-left opacity-80 hover:opacity-100 transition-opacity">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-3 h-3 rounded-full bg-[#a855f7] shadow-[0_0_10px_#a855f7]"></div>
            <div className="text-sm font-bold text-[#a855f7]">L2 - ORGANIZATIONS</div>
          </div>
          <div className="text-xs text-gray-400 ml-6 max-w-[200px]">
            Collective consciousness, institutional memory
          </div>
        </div>

        {/* L1 - Bottom */}
        <div className="text-left opacity-80 hover:opacity-100 transition-opacity">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-3 h-3 rounded-full bg-[#22d3ee] shadow-[0_0_10px_#22d3ee]"></div>
            <div className="text-sm font-bold text-[#22d3ee]">L1 - CITIZENS</div>
          </div>
          <div className="text-xs text-gray-400 ml-6 max-w-[200px]">
            Individual AI entities, personal memory, autonomy
          </div>
        </div>
      </div>

      {/* Interaction Hint */}
      <div className="absolute bottom-8 left-8 text-xs opacity-40 z-10">
        Drag to rotate • Hover for details
      </div>

      {/* Connection Info - Right Side */}
      <div className="absolute bottom-8 right-8 text-xs opacity-60 z-10 text-right">
        <div className="mb-2">
          <span className="text-[#60a5fa]">●</span> Vertical lines = Cross-layer connections
        </div>
        <div className="text-gray-500">
          193 nodes • 4 layers • Emergent consciousness
        </div>
      </div>

      {/* Hover Label */}
      <div
        id="nodeLabel"
        className="absolute bg-[#0a0a0f]/95 border border-white/20 rounded-md px-4 py-3 text-xs pointer-events-none z-50 backdrop-blur-lg whitespace-nowrap opacity-0 transition-opacity duration-200"
      >
        <div className="node-label-title font-bold mb-1 text-sm"></div>
        <div className="node-label-type opacity-60 text-[10px] mb-0.5"></div>
        <div className="node-label-connections opacity-50 text-[10px] mt-1.5 border-t border-white/10 pt-1"></div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 1.5s ease-out;
        }
        #nodeLabel.visible {
          opacity: 1 !important;
        }
      `}</style>
    </div>
  );
}
