from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from services.qdrant_manager import QdrantManager
from services.embeddings import create_embedding
import logging
from services.credit_oracle import get_oracle
from qdrant_client.models import PointStruct
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

qdrant = QdrantManager(host="localhost", port=6333)

class FraudCheckRequest(BaseModel):
    client_data: Dict[str, Any]

class FraudCheckResponse(BaseModel):
    is_suspicious: bool
    fraud_score: float
    alert_level: str
    similar_frauds: List[Dict[str, Any]]
    recommendation: str
    oracle_narrative: str = ""

@router.post("/fraud/check", response_model=FraudCheckResponse)
async def check_fraud(request: FraudCheckRequest):
    """
    Check if client profile matches known fraud patterns
    """
    try:
        # Create embedding
        vector = create_embedding(request.client_data)
        
        # Search fraud collection using qdrant client
        fraud_results = qdrant.client.query_points(
            collection_name="fraud_patterns",
            query=vector.tolist() if hasattr(vector, 'tolist') else vector,
            limit=5
        )
        
        if not fraud_results or not fraud_results.points:
            return FraudCheckResponse(
                is_suspicious=False,
                fraud_score=0.0,
                alert_level="none",
                similar_frauds=[],
                recommendation="No fraud patterns detected. Profile appears legitimate."
            )
        
        # Analyze top match
        top_match = fraud_results.points[0]
        fraud_score = top_match.score
        
        # Deduct 0.2 from fraud_score if it's less than 0.8
        if fraud_score < 0.8:
            fraud_score = max(0.0, fraud_score - 0.2)
        
        # Determine suspicion level
        if fraud_score >= 0.90:
            is_suspicious = True
            alert_level = "critical"
            recommendation = "⛔ HIGH FRAUD RISK: Extremely similar to known fraud patterns. Recommend manual review and verification."
        elif fraud_score >= 0.80:
            is_suspicious = True
            alert_level = "high"
            recommendation = "⚠️ MODERATE FRAUD RISK: Similar to known fraud patterns. Recommend additional verification."
        elif fraud_score >= 0.70:
            is_suspicious = True
            alert_level = "medium"
            recommendation = "🔍 LOW FRAUD RISK: Some similarity to fraud patterns. Consider extra due diligence."
        else:
            is_suspicious = False
            alert_level = "low"
            recommendation = "✅ MINIMAL FRAUD RISK: Profile does not match known fraud patterns."
            
        indicators = []
        fraud_type = 'unknown'
        if fraud_results and fraud_results.points and len(fraud_results.points) > 0:
            top_fraud = fraud_results.points[0]
            indicators_str = top_fraud.payload.get('fraud_indicators','')
            indicators = indicators_str.split(',')[:3] if isinstance(indicators_str, str) else indicators_str[:3] if isinstance(indicators_str, list) else []
            fraud_type = top_fraud.payload.get('fraud_type', 'unknown')
        
        # Generate AI explanation
        oracle = get_oracle()
        oracle_narrative = oracle.explain_fraud(
            fraud_score=fraud_score,
            fraud_type=fraud_type if is_suspicious else 'none',
            similar_frauds=[
                {
                    'fraud_id': r.payload.get('fraud_id'),
                    'fraud_type':r.payload.get('fraud_type')
                }
                for r in fraud_results.points[:3]
            ],
            fraud_indicators=indicators
        )
        
        # Extract similar frauds
        similar_frauds = [
            {
                "fraud_id": r.payload.get('fraud_id', 'unknown'),
                "fraud_type": r.payload.get('fraud_type', 'unknown'),
                "similarity": r.score,
                "debt_ratio": r.payload.get('debt_ratio', 0),
                "income_stability": r.payload.get('income_stability', 0)
            }
            for r in fraud_results.points[:3]
        ]
        
        logger.info(f"Fraud check: score={fraud_score:.3f}, level={alert_level}")
        
        return FraudCheckResponse(
            is_suspicious=is_suspicious,
            fraud_score=fraud_score,
            alert_level=alert_level,
            similar_frauds=similar_frauds,
            recommendation=recommendation,
            oracle_narrative=oracle_narrative
        )
    
    except Exception as e:
        logger.error(f"Fraud check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))