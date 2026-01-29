"""
Temporal evolution endpoints for tracking risk over time
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import logging

from services.qdrant_manager import QdrantManager
from services.credit_oracle import get_oracle

logger = logging.getLogger(__name__)
router = APIRouter()

qdrant = QdrantManager(host="localhost", port=6333)


@router.get("/temporal/{client_id}")
async def get_temporal_evolution(client_id: str):
    """
    Get temporal evolution data for a specific client
    
    Returns snapshots at T0 (application), T1 (3 months), T2 (6 months)
    with risk scores and status at each point.
    """
    
    try:
        # Search temporal_risk_memory collection for this client's snapshots
        # In production, would use a filter on client_id
        # For demo, we'll fetch from credit_history_memory and extract temporal data
        
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
        
        client_data = results[0][0].payload
        
        # Parse temporal snapshots
        temporal_snapshots = json.loads(client_data.get('temporal_snapshots', '[]'))
        
        if not temporal_snapshots:
            raise HTTPException(
                status_code=404, 
                detail=f"No temporal data available for client {client_id}"
            )
        
        # Get Oracle narrative
        oracle = get_oracle()
        narrative = oracle.narrate_temporal_evolution(
            client_id=client_id,
            snapshots=temporal_snapshots,
            final_outcome=client_data.get('actual_outcome', 'unknown')
        )
        
        return {
            "client_id": client_id,
            "client_name": client_data.get('name', 'Unknown'),
            "employment_type": client_data.get('employment_type', 'unknown'),
            "final_outcome": client_data.get('actual_outcome', 'unknown'),
            "snapshots": temporal_snapshots,
            "narrative": narrative
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch temporal data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/temporal/compare/{client_id1}/{client_id2}")
async def compare_temporal_evolution(client_id1: str, client_id2: str):
    """
    Compare temporal evolution of two clients side-by-side
    
    Useful for understanding different trajectories
    """
    
    try:
        client1_data = await get_temporal_evolution(client_id1)
        client2_data = await get_temporal_evolution(client_id2)
        
        return {
            "client1": client1_data,
            "client2": client2_data,
            "comparison_narrative": f"Client {client_id1} demonstrated {client1_data['final_outcome']} while {client_id2} resulted in {client2_data['final_outcome']}. Comparing their temporal patterns reveals key behavioral differences."
        }
    
    except Exception as e:
        logger.error(f"Failed to compare temporal data: {e}")
        raise HTTPException(status_code=500, detail=str(e))