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
        # Search temporal_risk_memory collection for all 3 snapshots of this client
        results = qdrant.client.scroll(
            collection_name="temporal_risk_memory",
            scroll_filter={
                "must": [
                    {"key": "client_id", "match": {"value": client_id}}
                ]
            },
            limit=3
        )
        
        if not results or len(results[0]) == 0:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
        
        # Extract all 3 temporal points (T0, T1, T2)
        snapshots = []
        for point in results[0]:
            payload = point.payload
            snapshots.append({
                "timestamp": payload.get("timestamp", "unknown"),
                "date": payload.get("date", ""),
                "risk_score": payload.get("risk_score", 0.0),
                "status": payload.get("status", "unknown"),
                "debt_ratio": payload.get("debt_ratio", 0.0),
                "income_stability": payload.get("income_stability", 0.0),
                "payment_regularity": payload.get("payment_regularity", 0.0)
            })
        
        if not snapshots:
            raise HTTPException(
                status_code=404, 
                detail=f"No temporal data available for client {client_id}"
            )
        
        # Sort by timestamp (T0, T1, T2)
        timestamp_order = {"T0_application": 0, "T1_3months": 1, "T2_6months": 2}
        snapshots.sort(key=lambda x: timestamp_order.get(x["timestamp"], 999))
        
        return {
            "client_id": client_id,
            "snapshots": snapshots
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch temporal data: {e}")
        raise HTTPException(status_code=500, detail=str(e))