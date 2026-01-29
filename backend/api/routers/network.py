"""
Network graph endpoints for trust rings visualization
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import logging

from services.qdrant_manager import QdrantManager

logger = logging.getLogger(__name__)
router = APIRouter()

qdrant = QdrantManager(host="localhost", port=6333)


class NetworkBuildRequest(BaseModel):
    center_client_id: str
    related_clients: List[str]


@router.post("/network/build")
async def build_trust_network(request: NetworkBuildRequest):
    """
    Build a network graph of business relationships
    
    Args:
        center_client_id: The client at the center of the network
        related_clients: List of similar client IDs to include
    
    Returns:
        Graph data with nodes and links
    """
    
    try:
        nodes = []
        links = []
        
        # Fetch all client data
        all_clients = [request.center_client_id] + request.related_clients[:20]
        
        client_data_map = {}
        
        for client_id in all_clients:
            try:
                results = qdrant.client.scroll(
                    collection_name="credit_history_memory",
                    scroll_filter={
                        "must": [
                            {"key": "client_id", "match": {"value": client_id}}
                        ]
                    },
                    limit=1
                )
                
                if results and len(results[0]) > 0:
                    payload = results[0][0].payload
                    client_data_map[client_id] = payload
            except Exception as e:
                logger.warning(f"Could not fetch data for {client_id}: {e}")
                continue
        
        # Build nodes
        for client_id, data in client_data_map.items():
            is_center = (client_id == request.center_client_id)
            outcome = data.get('actual_outcome', 'unknown')
            
            nodes.append({
                "id": client_id,
                "name": data.get('name', client_id),
                "group": "center" if is_center else ("good" if outcome == "repaid" else "bad"),
                "outcome": outcome,
                "employment_type": data.get('employment_type', 'unknown'),
                "val": 20 if is_center else 10
            })
        
        # Build links from social network data
        for client_id, data in client_data_map.items():
            social_network_str = data.get('social_network', '[]')
            try:
                social_network = json.loads(social_network_str)
                
                for connection in social_network:
                    target_id = connection.get('connection_id')
                    connection_type = connection.get('type', 'unknown')
                    strength = connection.get('strength', 0.5)
                    
                    # Only add link if target is in our node set
                    if target_id in client_data_map:
                        links.append({
                            "source": client_id,
                            "target": target_id,
                            "value": strength * 5,
                            "type": connection_type
                        })
            except json.JSONDecodeError:
                logger.warning(f"Could not parse social network for {client_id}")
                continue
        
        logger.info(f"Built network with {len(nodes)} nodes and {len(links)} links")
        
        return {
            "nodes": nodes,
            "links": links
        }
    
    except Exception as e:
        logger.error(f"Failed to build network: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network/analyze/{client_id}")
async def analyze_network_position(client_id: str):
    """
    Analyze a client's position in the trust network
    
    Returns network metrics like:
    - Degree centrality (number of connections)
    - Cluster coefficient (how connected neighbors are)
    - Trust score (based on connected nodes' outcomes)
    """
    
    try:
        # Fetch client data
        results = qdrant.client.scroll(
            collection_name="credit_history_memory",
            scroll_filter={
                "must": [
                    {"key": "client_id", "match": {"value": client_id}}
                ]
            },
            limit=1
        )
        
        if not results or len(results[0]) == 0:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
        
        payload = results[0][0].payload
        social_network_str = payload.get('social_network', '[]')
        social_network = json.loads(social_network_str)
        
        # Calculate network metrics
        degree = len(social_network)
        avg_strength = sum(c.get('strength', 0) for c in social_network) / degree if degree > 0 else 0
        
        # Fetch connected clients' outcomes
        connected_outcomes = []
        for connection in social_network:
            conn_id = connection.get('connection_id')
            try:
                conn_results = qdrant.client.scroll(
                    collection_name="credit_history_memory",
                    scroll_filter={
                        "must": [
                            {"key": "client_id", "match": {"value": conn_id}}
                        ]
                    },
                    limit=1
                )
                if conn_results and len(conn_results[0]) > 0:
                    outcome = conn_results[0][0].payload.get('actual_outcome')
                    if outcome:
                        connected_outcomes.append(outcome)
            except:
                continue
        
        # Calculate trust score
        repaid_count = sum(1 for o in connected_outcomes if o == 'repaid')
        trust_score = repaid_count / len(connected_outcomes) if connected_outcomes else 0.5
        
        return {
            "client_id": client_id,
            "network_metrics": {
                "degree_centrality": degree,
                "average_connection_strength": round(avg_strength, 3),
                "connected_repayment_rate": round(trust_score, 3),
                "network_trust_score": round((degree * avg_strength * trust_score) / 10, 3)
            },
            "insights": [
                f"Client has {degree} business connections",
                f"Average connection strength: {avg_strength:.1%}",
                f"{repaid_count}/{len(connected_outcomes)} connected clients repaid successfully" if connected_outcomes else "No connected client data available",
                f"Network trust score: {trust_score:.1%}"
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze network: {e}")
        raise HTTPException(status_code=500, detail=str(e))