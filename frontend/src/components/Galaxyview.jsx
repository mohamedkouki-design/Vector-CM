import { useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

function ClientOrb({ position, outcome, similarity, onClick, isSelected }) {
  const meshRef = useRef();
  const [hovered, setHovered] = useState(false);
  
  // Color based on outcome
  const color = outcome === 'repaid' ? '#10b981' : '#ef4444';
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
    // Convert client similarities to 3D positions
    // Use simple mapping: similarity determines distance from center
    const newPositions = clients.map((client, i) => {
      const angle = (i / clients.length) * Math.PI * 2;
      const radius = 5 + (1 - client.similarity) * 10; // Less similar = further away
      
      return {
        ...client,
        position: [
          Math.cos(angle) * radius,
          (Math.random() - 0.5) * 3, // Random Y spread
          Math.sin(angle) * radius
        ]
      };
    });
    
    setPositions(newPositions);
  }, [clients]);
  
  if (clients.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-space-dark rounded-2xl">
        <p className="text-gray-400">Run a search to see Galaxy View</p>
      </div>
    );
  }
  
  return (
    <div className="w-full h-full bg-space-darkest rounded-2xl overflow-hidden relative">
      {/* Legend */}
      <div className="absolute top-4 right-4 z-10 glass-card p-4 space-y-2">
        <h3 className="font-semibold text-sm mb-2">Outcomes</h3>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-risk-safe"></div>
          <span className="text-xs">Repaid</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-risk-critical"></div>
          <span className="text-xs">Defaulted</span>
        </div>
        <p className="text-xs text-gray-400 mt-3">
          Size = Similarity<br/>
          Distance = Difference
        </p>
      </div>
      
      {/* 3D Canvas */}
      <Canvas>
        <PerspectiveCamera makeDefault position={[0, 5, 20]} />
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          rotateSpeed={0.5}
          minDistance={10}
          maxDistance={50}
        />
        
        {/* Lighting */}
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={0.8} color="#06b6d4" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#a855f7" />
        
        {/* Stars background */}
        <mesh>
          <sphereGeometry args={[100, 32, 32]} />
          <meshBasicMaterial
            color="#0a0e27"
            side={THREE.BackSide}
          />
        </mesh>
        
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
      <div className="absolute bottom-4 left-4 text-xs text-gray-400">
        Drag to rotate • Scroll to zoom • Click orb to select
      </div>
    </div>
  );
}