from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from services.qdrant_manager import QdrantManager
from services.embeddings import create_embedding
from services.credit_oracle import get_oracle
import numpy as np
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

qdrant = QdrantManager(host="localhost", port=6333)

class CounterfactualRequest(BaseModel):
    original_client: Dict[str, Any]
    modifications: Dict[str, Any]

class CounterfactualResponse(BaseModel):
    original_risk: str
    modified_risk: str
    risk_change: str
    improvement_path: List[str]
    confidence_before: float
    confidence_after: float

def calculate_risk_level(confidence: float) -> str:
    """Calculate risk level from confidence score"""
    if confidence >= 0.8:
        return "LOW"
    elif confidence >= 0.6:
        return "MEDIUM"
    elif confidence >= 0.4:
        return "HIGH"
    else:
        return "CRITICAL"

def apply_modifications(original_data: dict, modifications: dict) -> dict:
    """Apply modifications to client data"""
    modified = original_data.copy()
    
    for key, change in modifications.items():
        if key in modified:
            original_value = modified[key]
            # Apply change (can be absolute or relative)
            if abs(change) < 1:  # Treat as relative change
                modified[key] = original_value + (original_value * change)
            else:  # Treat as absolute change
                modified[key] = original_value + change
            
            # Clamp to valid ranges
            if key == 'debt_ratio':
                modified[key] = max(0.0, min(1.0, modified[key]))
            elif key in ['income_stability', 'payment_regularity']:
                modified[key] = max(0.0, min(1.0, modified[key]))
            elif key == 'years_active':
                modified[key] = max(0, modified[key])
    
    return modified

def generate_improvement_path(original_data: dict, modifications: dict, 
                              original_risk: str, modified_risk: str) -> List[str]:
    """Generate actionable advice based on modifications"""
    advice = []
    
    risk_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    
    for key, change in modifications.items():
        if change != 0:
            if key == 'debt_ratio':
                if change < 0:
                    reduction = abs(change) * 100
                    advice.append(
                        f"Reduce debt ratio by {reduction:.0f}% "
                        f"(pay down approximately {reduction * 10:.0f} TND)"
                    )
            elif key == 'years_active':
                if change > 0:
                    advice.append(
                        f"Continue stable business operations for {abs(change):.1f} more years"
                    )
            elif key == 'income_stability':
                if change > 0:
                    advice.append(
                        f"Improve income consistency by {abs(change)*100:.0f}% "
                        f"(reduce month-to-month variance)"
                    )
            elif key == 'payment_regularity':
                if change > 0:
                    advice.append(
                        f"Increase on-time payment rate to {(original_data.get(key, 0.8) + change)*100:.0f}%"
                    )
    
    # Add summary
    if risk_levels[modified_risk] < risk_levels[original_risk]:
        advice.append(
            f"✅ These changes would improve risk level from {original_risk} to {modified_risk}"
        )
    elif risk_levels[modified_risk] > risk_levels[original_risk]:
        advice.append(
            f"⚠️ These changes would worsen risk level from {original_risk} to {modified_risk}"
        )
    else:
        advice.append(f"➡️ Risk level remains {original_risk}")
    
    return advice



@router.post("/counterfactual/analyze", response_model=CounterfactualResponse)
async def analyze_counterfactual(request: CounterfactualRequest):
    """
    What-if analysis: How would changes affect credit decision?
    """
    try:
        # Create embedding for original client
        original_vector = create_embedding(request.original_client)
        
        # Search with original
        original_results = qdrant.search(
            collection_name="credit_history_memory",
            query_vector=original_vector.tolist(),
            limit=50
        )
        
        # Calculate original confidence
        original_repaid = sum(1 for r in original_results if r.payload.get('actual_outcome') == 'repaid')
        original_confidence = original_repaid / len(original_results) if original_results else 0
        original_risk = calculate_risk_level(original_confidence)
        
        # Apply modifications
        modified_client = apply_modifications(request.original_client, request.modifications)
        
        # Create embedding for modified client
        modified_vector = create_embedding(modified_client)
        
        # Search with modified
        modified_results = qdrant.search(
            collection_name="credit_history_memory",
            query_vector=modified_vector.tolist(),
            limit=50
        )
        
        # Calculate modified confidence
        modified_repaid = sum(1 for r in modified_results if r.payload.get('actual_outcome') == 'repaid')
        modified_confidence = modified_repaid / len(modified_results) if modified_results else 0
        modified_risk = calculate_risk_level(modified_confidence)
        
        # Generate improvement path
        improvement_path = generate_improvement_path(
            request.original_client,
            request.modifications,
            original_risk,
            modified_risk
        )
        
        # Calculate risk change
        risk_change = "improved" if modified_confidence > original_confidence else \
                     "worsened" if modified_confidence < original_confidence else "unchanged"
        
        logger.info(f"Counterfactual: {original_risk} -> {modified_risk} ({risk_change})")
        oracle = get_oracle()
        improvement_path = oracle.generate_improvement_path(
            original_data = request.original_client,
            modifications = request.modifications,
            risk_change = {
                'from':original_risk,
                'to':modified_risk
            }
        )
        
        return CounterfactualResponse(
            original_risk=original_risk,
            modified_risk=modified_risk,
            risk_change=risk_change,
            improvement_path=improvement_path,
            confidence_before=original_confidence,
            confidence_after=modified_confidence
        )
    
    except Exception as e:
        logger.error(f"Counterfactual analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))