import { useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

function Stars() {
  const ref = useRef();
  
  useEffect(() => {
    const starCount = 1000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(starCount * 3);
    
    for (let i = 0; i < starCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 300;
      positions[i + 1] = (Math.random() - 0.5) * 300;
      positions[i + 2] = (Math.random() - 0.5) * 300;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const material = new THREE.PointsMaterial({
      color: '#94a3b8',
      size: 0.3,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.8
    });
    
    if (ref.current) {
      ref.current.geometry = geometry;
      ref.current.material = material;
    }
  }, []);
  
  return <points ref={ref} />;
}

function ClientOrb({ position, outcome, similarity, onClick, isSelected }) {
  const meshRef = useRef();
  const [hovered, setHovered] = useState(false);
  
  // Color based on outcome
  const color = outcome == 'repaid' ? '#10b981' : '#ef4444';
  const size = 0.2 + (similarity * 0.3); // Bigger = more similar
  
  useEffect(() => {
    if (meshRef.current) {
      const scale = (hovered || isSelected) ? 1.5 : 1;
      meshRef.current.scale.set(scale, scale, scale);
    }
  }, [hovered, isSelected]);
  
  return (
    <mesh
      ref={meshRef}
      position={position}
      onClick={onClick}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <sphereGeometry args={[size, 32, 32]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={hovered || isSelected ? 0.8 : 0.3}
        transparent
        opacity={0.9}
      />
      
      {/* Glow effect */}
      {(hovered || isSelected) && (
        <mesh scale={1.3}>
          <sphereGeometry args={[size, 16, 16]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.2}
          />
        </mesh>
      )}
    </mesh>
  );
}

export default function GalaxyView({ clients = [], onSelectClient, selectedClientId }) {
  const [positions, setPositions] = useState([]);
  
  useEffect(() => {
    // Convert client similarities to 3D positions using Fibonacci sphere distribution
    const newPositions = clients.map((client, i) => {
      const phi = Math.acos(2 * (i / clients.length) - 1); // Golden angle
      const theta = Math.PI * (1 + Math.sqrt(5)) * i; // Fibonacci angle
      
      // Base radius increases with dissimilarity
      const baseRadius = 8 + (1 - client.similarity) * 15;
      
      return {
        ...client,
        position: [
          Math.cos(theta) * Math.sin(phi) * baseRadius,
          Math.cos(phi) * baseRadius,
          Math.sin(theta) * Math.sin(phi) * baseRadius
        ]
      };
    });
    
    setPositions(newPositions);
  }, [clients]);
  
  if (clients.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-950 rounded-2xl border border-slate-800">
        <div className="text-center">
          <div className="text-4xl mb-3">🔍</div>
          <p className="text-slate-400">Run a search to view the Galaxy</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="w-full h-full bg-slate-950 rounded-2xl overflow-hidden relative">
      {/* Legend */}
      <div className="absolute top-4 right-4 z-10 bg-slate-900/80 backdrop-blur-sm border border-slate-700/50 rounded-lg p-4 space-y-2 shadow-lg">
        <h3 className="font-semibold text-sm text-white mb-2">Client Outcomes</h3>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500 shadow-lg" style={{boxShadow: '0 0 8px rgba(34, 197, 94, 0.6)'}}></div>
          <span className="text-xs text-slate-300">Repaid</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500 shadow-lg" style={{boxShadow: '0 0 8px rgba(239, 68, 68, 0.6)'}}></div>
          <span className="text-xs text-slate-300">Defaulted</span>
        </div>
        <div className="border-t border-slate-700/50 pt-3 mt-3">
          <p className="text-xs text-slate-400">
            <span className="text-blue-400 font-semibold">●</span> Size = Similarity<br/>
            <span className="text-blue-400 font-semibold">●</span> Distance = Difference
          </p>
        </div>
      </div>
      
      {/* 3D Canvas */}
      <Canvas>
        <PerspectiveCamera makeDefault position={[0, 40, 5]} />
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          rotateSpeed={0.5}
          minDistance={15}
          maxDistance={80}
        />
        
        {/* Lighting - Professional Blue/Slate Theme */}
        <ambientLight intensity={0.4} />
        <pointLight position={[15, 15, 15]} intensity={1} color="#3b82f6" />
        <pointLight position={[-15, -10, -15]} intensity={0.6} color="#64748b" />
        <pointLight position={[0, 20, 0]} intensity={0.5} color="#1e40af" />
        
        {/* Stars background with gradient effect */}
        <mesh>
          <sphereGeometry args={[150, 64, 64]} />
          <meshBasicMaterial
            color="#0f172a"
            side={THREE.BackSide}
          />
        </mesh>
        
        {/* Subtle nebula effect layer */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[145, 32, 32]} />
          <meshBasicMaterial
            color="#1e3a8a"
            transparent
            opacity={0.1}
            side={THREE.BackSide}
          />
        </mesh>
        
        {/* Starfield */}
        <Stars />
        
        {/* Client orbs */}
        {positions.map((client, i) => (
          <ClientOrb
            key={i}
            position={client.position}
            outcome={client.outcome}
            similarity={client.similarity}
            isSelected={client.client_id === selectedClientId}
            onClick={() => onSelectClient(client)}
          />
        ))}
        
        {/* Center reference point */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
      </Canvas>
      
      {/* Controls hint */}
      <div className="absolute bottom-4 left-4 text-xs text-slate-400 bg-slate-900/60 px-3 py-2 rounded-lg backdrop-blur-sm border border-slate-700/30">
        🖱️ Drag to rotate • 🔍 Scroll to zoom • 👆 Click to select
      </div>
    </div>
  );
}