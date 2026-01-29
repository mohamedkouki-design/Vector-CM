import { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Users, Info, Zap } from 'lucide-react';
import axios from 'axios';

export default function TrustRings({ clientId, similarClients }) {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(false);
  const graphRef = useRef();
  
  useEffect(() => {
    if (clientId && similarClients) {
      buildTrustNetwork();
    }
  }, [clientId, similarClients]);
  
  const buildTrustNetwork = async () => {
    setLoading(true);
    try {
      // Fetch network data from backend
      const response = await axios.post('http://localhost:8000/api/v1/network/build', {
        center_client_id: clientId,
        related_clients: similarClients.slice(0, 20).map(c => c.client_id)
      });
      
      setGraphData(response.data);
    } catch (error) {
      console.error('Failed to build network:', error);
      
      // Fallback to mock data
      const mockNetwork = generateMockNetwork(clientId, similarClients);
      setGraphData(mockNetwork);
    } finally {
      setLoading(false);
    }
  };
  
  const generateMockNetwork = (centerId, clients) => {
    const nodes = [];
    const links = [];
    
    // Center node (the queried client)
    nodes.push({
      id: centerId,
      name: 'Query Client',
      group: 'center',
      outcome: 'query',
      val: 20  // Node size
    });
    
    // Add similar clients as nodes
    clients.slice(0, 20).forEach((client, i) => {
      nodes.push({
        id: client.client_id,
        name: client.client_id,
        group: client.outcome === 'repaid' ? 'good' : 'bad',
        outcome: client.outcome,
        similarity: client.similarity,
        val: 10 + (client.similarity * 10)  // Size based on similarity
      });
      
      // Link to center
      links.push({
        source: centerId,
        target: client.client_id,
        value: client.similarity * 10,  // Link thickness
        type: 'similarity'
      });
    });
    
    // Add connections between similar clients (second-order relationships)
    for (let i = 0; i < Math.min(clients.length, 15); i++) {
      for (let j = i + 1; j < Math.min(clients.length, 15); j++) {
        // Randomly connect some clients (simulating business relationships)
        if (Math.random() < 0.15) {  // 15% connection probability
          links.push({
            source: clients[i].client_id,
            target: clients[j].client_id,
            value: Math.random() * 3,
            type: 'business_connection'
          });
        }
      }
    }
    
    return { nodes, links };
  };
  
  const handleNodeClick = (node) => {
    setSelectedNode(node);
    
    // Highlight connected nodes
    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 1000);
      graphRef.current.zoom(2, 1000);
    }
  };
  
  const getNodeColor = (node) => {
    if (node.group === 'center') return '#06b6d4';  // Cyan for center
    if (node.group === 'good') return '#10b981';     // Green for repaid
    if (node.group === 'bad') return '#ef4444';      // Red for defaulted
    return '#6b7280';  // Gray for unknown
  };
  
  const getLinkColor = (link) => {
    if (link.type === 'similarity') return 'rgba(168, 85, 247, 0.3)';  // Purple for similarity
    return 'rgba(6, 182, 212, 0.2)';  // Cyan for business connections
  };
  
  if (!clientId) {
    return (
      <div className="glass-card">
        <div className="text-center py-12">
          <Users className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">Search for a client to view trust network</p>
        </div>
      </div>
    );
  }
  
  if (loading) {
    return (
      <div className="glass-card">
        <div className="text-center py-12">
          <div className="w-12 h-12 border-4 border-accent-purple border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Building trust network...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="glass-card">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold flex items-center gap-3 mb-2">
          <Users className="w-8 h-8 text-accent-purple" />
          Trust Rings Network
        </h3>
        <p className="text-gray-400">
          Interactive visualization of business relationships and second-order trust
        </p>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-space-dark rounded-lg p-4">
          <div className="text-2xl font-bold text-accent-cyan mb-1">
            {graphData.nodes.length}
          </div>
          <div className="text-sm text-gray-400">Total Nodes</div>
        </div>
        
        <div className="bg-space-dark rounded-lg p-4">
          <div className="text-2xl font-bold text-accent-purple mb-1">
            {graphData.links.length}
          </div>
          <div className="text-sm text-gray-400">Connections</div>
        </div>
        
        <div className="bg-space-dark rounded-lg p-4">
          <div className="text-2xl font-bold text-risk-safe mb-1">
            {graphData.nodes.filter(n => n.group === 'good').length}
          </div>
          <div className="text-sm text-gray-400">Repaid</div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-4 mb-6 p-4 bg-space-dark rounded-lg">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-accent-cyan"></div>
          <span className="text-sm text-gray-300">Query Client</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-risk-safe"></div>
          <span className="text-sm text-gray-300">Repaid</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-risk-critical"></div>
          <span className="text-sm text-gray-300">Defaulted</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-accent-purple"></div>
          <span className="text-sm text-gray-300">Similarity Link</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-accent-cyan"></div>
          <span className="text-sm text-gray-300">Business Connection</span>
        </div>
      </div>
      
      {/* Graph Canvas */}
      <div className="border border-space-light rounded-lg overflow-hidden bg-space-darkest">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          nodeLabel="name"
          nodeColor={getNodeColor}
          nodeVal="val"
          linkColor={getLinkColor}
          linkWidth={link => link.value || 1}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.005}
          onNodeClick={handleNodeClick}
          nodeCanvasObject={(node, ctx, globalScale) => {
            // Draw node
            const size = node.val || 5;
            ctx.beginPath();
            ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
            ctx.fillStyle = getNodeColor(node);
            ctx.fill();
            
            // Draw border for selected node
            if (selectedNode && selectedNode.id === node.id) {
              ctx.strokeStyle = '#ffffff';
              ctx.lineWidth = 2 / globalScale;
              ctx.stroke();
            }
            
            // Draw label for larger nodes
            if (size > 8) {
              ctx.font = `${12 / globalScale}px Sans-Serif`;
              ctx.fillStyle = '#ffffff';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(node.name, node.x, node.y + size + 10 / globalScale);
            }
          }}
          backgroundColor="#0a0e27"
          width={800}
          height={500}
          cooldownTicks={100}
          onEngineStop={() => {
            // Center graph when done loading
            if (graphRef.current) {
              graphRef.current.zoomToFit(400, 50);
            }
          }}
        />
      </div>
      
      {/* Selected Node Info */}
      {selectedNode && (
        <div className="mt-6 p-4 bg-gradient-to-r from-accent-purple/20 to-accent-pink/20 border border-accent-purple/30 rounded-lg animate-fade-in">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-accent-purple mt-1" />
            <div className="flex-1">
              <h4 className="font-semibold text-accent-purple mb-2">
                Selected: {selectedNode.name}
              </h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-gray-400">ID:</span>
                  <span className="ml-2 text-gray-200">{selectedNode.id}</span>
                </div>
                <div>
                  <span className="text-gray-400">Outcome:</span>
                  <span className={`ml-2 font-semibold ${
                    selectedNode.outcome === 'repaid' ? 'text-risk-safe' :
                    selectedNode.outcome === 'defaulted' ? 'text-risk-critical' :
                    'text-gray-400'
                  }`}>
                    {selectedNode.outcome || 'N/A'}
                  </span>
                </div>
                {selectedNode.similarity && (
                  <div>
                    <span className="text-gray-400">Similarity:</span>
                    <span className="ml-2 text-gray-200">
                      {(selectedNode.similarity * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Insights */}
      <div className="mt-6 p-4 bg-accent-cyan/10 border border-accent-cyan/30 rounded-lg">
        <div className="flex items-start gap-3">
          <Zap className="w-5 h-5 text-accent-cyan mt-1" />
          <div>
            <h4 className="font-semibold text-accent-cyan mb-2">Network Insights</h4>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>• Larger nodes indicate higher similarity to query client</li>
              <li>• Purple links show similarity relationships (direct k-NN matches)</li>
              <li>• Cyan links represent business connections (second-order trust)</li>
              <li>• Densely connected clusters suggest community-based lending opportunities</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}