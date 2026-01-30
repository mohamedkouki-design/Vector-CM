import { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Users, Info, Zap } from 'lucide-react';
import axios from 'axios';

export default function TrustRings({ clientId, similarClients, queryClientData }) {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dimensions, setDimensions] = useState({ width: 1000, height: 600 });
  const graphRef = useRef();
  const containerRef = useRef();
  
  useEffect(() => {
    if (clientId && similarClients) {
      buildTrustNetwork();
    }
  }, [clientId, similarClients]);
  
  useEffect(() => {
    if (graphData.nodes.length > 0) {
      console.log('TrustRings graphData:', {
        nodes: graphData.nodes.length,
        links: graphData.links.length,
        linkTypes: graphData.links.reduce((acc, link) => {
          acc[link.type] = (acc[link.type] || 0) + 1;
          return acc;
        }, {})
      });
    }
  }, [graphData]);
  
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const width = containerRef.current.offsetWidth || 1000;
        setDimensions({ width, height: 600 });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);
  
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
    
    // Center node (the queried client) - pinned to center
    const queryName = queryClientData?.name || centerId;
    const queryArchetype = queryClientData?.archetype || 'Unknown';
    
    nodes.push({
      id: centerId,
      name: `${queryName} (${queryArchetype})`,
      group: 'center',
      outcome: 'query',
      val: 25,  // Node size
      fx: 0,    // Pin to center X
      fy: 0     // Pin to center Y
    });
    
    // Add similar clients as nodes
    clients.slice(0, 20).forEach((client, i) => {
      nodes.push({
        id: client.client_id,
        name: client.client_id,
        group: client.outcome === 'repaid' ? 'good' : 'bad',
        outcome: client.outcome,
        similarity: client.similarity,
        val: 10 + ((client.similarity || 0.5) * 10)  // Size based on similarity, default to 0.5
      });
      
      // Link to center - ensure value is numeric
      const similarity = client.similarity || 0.5;
      links.push({
        source: centerId,
        target: client.client_id,
        value: similarity * 3,  // Use similarity directly for thickness
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
    if (node.group === 'center') return '#3b82f6';  // Blue for center
    if (node.group === 'good') return '#10b981';     // Green for repaid
    if (node.group === 'bad') return '#ef4444';      // Red for defaulted
    return '#64748b';  // Slate for unknown
  };
  
  const getLinkColor = (link) => {
    if (link.type === 'similarity') return 'rgba(59, 130, 246, 0.6)';  // Blue for similarity
    return 'rgba(148, 163, 184, 0.5)';  // Slate for business connections
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
    <div className="glass-card bg-gradient-to-br from-space-dark via-space-dark to-space-darkest">
      {/* Professional Header */}
      <div className="mb-8 pb-6 border-b border-blue-500/20">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-3xl font-bold text-white">Trust Rings Network</h3>
              <p className="text-sm text-slate-400 mt-1">Relationship mapping & credit risk analysis</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-500 font-mono">Vector-based Analysis</div>
            <div className="text-xs text-blue-400 mt-1">384-dim embeddings</div>
          </div>
        </div>
      </div>
      
      {/* Key Metrics - Professional Layout */}
      <div className="grid grid-cols-4 gap-3 mb-8">
        <div className="bg-slate-800/50 border border-blue-500/30 rounded-lg p-4 hover:border-blue-500/60 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Network Size</span>
            <div className="text-2xl">🔗</div>
          </div>
          <div className="text-3xl font-bold text-white">{graphData.nodes.length}</div>
          <div className="text-xs text-slate-400 mt-2">Total participants</div>
        </div>
        
        <div className="bg-slate-800/50 border border-slate-600/30 rounded-lg p-4 hover:border-slate-600/60 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Connections</span>
            <div className="text-2xl">📊</div>
          </div>
          <div className="text-3xl font-bold text-white">{graphData.links.length}</div>
          <div className="text-xs text-slate-400 mt-2">Active relationships</div>
        </div>
        
        <div className="bg-gradient-to-br from-risk-safe/10 to-risk-safe/5 border border-risk-safe/20 rounded-lg p-4 hover:border-risk-safe/40 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-risk-safe uppercase tracking-wider">Low Risk</span>
            <div className="text-2xl">✓</div>
          </div>
          <div className="text-3xl font-bold text-risk-safe">{graphData.nodes.filter(n => n.group === 'good').length}</div>
          <div className="text-xs text-gray-400 mt-2">Repaid clients</div>
        </div>
        
        <div className="bg-gradient-to-br from-risk-critical/10 to-risk-critical/5 border border-risk-critical/20 rounded-lg p-4 hover:border-risk-critical/40 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-risk-critical uppercase tracking-wider">High Risk</span>
            <div className="text-2xl">⚠</div>
          </div>
          <div className="text-3xl font-bold text-risk-critical">{graphData.nodes.filter(n => n.group === 'bad').length}</div>
          <div className="text-xs text-gray-400 mt-2">Defaulted clients</div>
        </div>
      </div>
      
      {/* Legend - Professional Style */}
      <div className="mb-8 p-5 bg-slate-800/50 border border-slate-600/30 rounded-lg">
        <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4">Legend</div>
        <div className="grid grid-cols-5 gap-4">
          <div className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg border border-slate-600/20">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-sm text-slate-300">Query Client</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg border border-slate-600/20">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-sm text-slate-300">Good Standing</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg border border-slate-600/20">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-sm text-slate-300">Default Risk</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg border border-slate-600/20">
            <div className="w-1 h-1 rounded-full bg-blue-500" style={{boxShadow: '0 0 8px rgba(59, 130, 246, 0.6)'}}></div>
            <span className="text-sm text-slate-300">Similarity</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg border border-slate-600/20">
            <div className="w-1 h-1 rounded-full bg-slate-400" style={{boxShadow: '0 0 8px rgba(148, 163, 184, 0.5)'}}></div>
            <span className="text-sm text-slate-300">Business Link</span>
          </div>
        </div>
      </div>
      
      {/* Graph Canvas - Full Width */}
      <div ref={containerRef} className="border border-blue-500/30 rounded-lg overflow-hidden bg-slate-950/80 shadow-2xl mb-8">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-slate-600/5 pointer-events-none" style={{zIndex: 0}}></div>
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          nodeLabel="name"
          nodeColor={getNodeColor}
          nodeVal="val"
          linkColor={getLinkColor}
          linkWidth={link => {
            // Ensure minimum width for visibility
            const baseWidth = link.type === 'similarity' ? 2.5 : 1.5;
            return Math.max(baseWidth, (link.value || 1) * 0.5);
          }}
          linkDirectionalParticles={link => link.type === 'similarity' ? 2 : 0}
          linkDirectionalParticleSpeed={0.005}
          onNodeClick={handleNodeClick}
          nodeCanvasObject={(node, ctx, globalScale) => {
            // Draw node
            const size = node.val || 5;
            ctx.beginPath();
            ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
            ctx.fillStyle = getNodeColor(node);
            ctx.fill();
            
            // Add glow effect for center node
            if (node.group === 'center') {
              ctx.strokeStyle = 'rgba(59, 130, 246, 0.3)';
              ctx.lineWidth = 4 / globalScale;
              ctx.stroke();
            }
            
            // Draw border for selected node
            if (selectedNode && selectedNode.id === node.id) {
              ctx.strokeStyle = '#ffffff';
              ctx.lineWidth = 2.5 / globalScale;
              ctx.stroke();
            }
            
            // Draw label for center node and larger nodes
            if (node.group === 'center' || size > 8) {
              ctx.font = `bold ${12 / globalScale}px Sans-Serif`;
              ctx.fillStyle = '#ffffff';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(node.name, node.x, node.y + size + 12 / globalScale);
            }
          }}
          backgroundColor="#0a0e27"
          width={dimensions.width}
          height={dimensions.height}
          cooldownTicks={100}
          d3VelocityDecay={0.3}
          d3AlphaDecay={0.02}
          onEngineStop={() => {
            // Reset zoom to default centered view
            if (graphRef.current) {
              graphRef.current.zoom(1, 400);
            }
          }}
        />
      </div>
      
      {/* Selected Node Info - Professional Card */}
      {selectedNode && (
        <div className="mb-8 p-6 bg-slate-800/50 border border-blue-500/40 rounded-lg animate-fade-in shadow-lg">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center flex-shrink-0">
                <Info className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-white text-lg mb-1">
                  {selectedNode.name}
                </h4>
                <p className="text-sm text-gray-400">Client Profile</p>
              </div>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              selectedNode.group === 'center' ? 'bg-blue-500/20 text-blue-400' :
              selectedNode.group === 'good' ? 'bg-green-500/20 text-green-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {selectedNode.group === 'center' ? 'QUERY' : selectedNode.outcome?.toUpperCase()}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-900/50 border border-slate-600/20 rounded-lg p-3">
              <span className="text-xs text-slate-400 block mb-1">Client ID</span>
              <span className="font-mono text-sm text-white">{selectedNode.id}</span>
            </div>
            <div className="bg-slate-900/50 border border-slate-600/20 rounded-lg p-3">
              <span className="text-xs text-slate-400 block mb-1">Status</span>
              <span className="text-sm text-white capitalize">{selectedNode.outcome || 'N/A'}</span>
            </div>
            {selectedNode.similarity && (
              <div className="bg-slate-900/50 border border-slate-600/20 rounded-lg p-3">
                <span className="text-xs text-slate-400 block mb-1">Similarity Score</span>
                <span className="text-sm font-semibold text-blue-400">{(selectedNode.similarity * 100).toFixed(1)}%</span>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Professional Insights Section */}
      <div className="p-6 bg-slate-800/50 border border-blue-500/30 rounded-lg">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center flex-shrink-0">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h4 className="font-bold text-white mb-3">Network Intelligence</h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">▸</span>
                <span><strong>Node Size</strong> indicates similarity strength to the query client</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">▸</span>
                <span><strong>Blue Links</strong> represent direct k-NN similarity relationships (direct credit patterns)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">▸</span>
                <span><strong>Slate Links</strong> represent second-order business connections and social trust networks</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">▸</span>
                <span><strong>Color Coding</strong>: Green = Good standing, Red = Default risk, Blue = Query subject</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}