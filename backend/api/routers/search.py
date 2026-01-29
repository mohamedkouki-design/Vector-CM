from fastapi import APIRouter, HTTPException
from models.schemas import SearchRequest, SearchResponse, SimilarClient
from services.qdrant_manager import  QdrantManager
from services.embeddings import create_embedding
import logging
from services.credit_oracle import CreditOracle

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Qdrant
qdrant = QdrantManager(host="localhost", port=6333)

@router.post("/search/similar", response_model=SearchResponse)
async def search_similar(request: SearchRequest):
    """
    Find similar clients using k-NN search
    """
    try:
        # Create embedding
        logger.info(f"Creating embedding for: {request.client_data.get('archetype')}")
        vector = create_embedding(request.client_data)
        
        # Search Qdrant
        results = qdrant.search(
            collection_name="credit_history_memory",
            query_vector=vector.tolist(),
            limit=request.top_k
        )
        
        logger.info(f"Found {len(results)} similar clients")
        
        # Parse results
        similar_clients = []
        repaid_count = 0
        
        for result in results:
            outcome = result.payload.get('outcome', 'unknown')
            if outcome == 'approved':
                repaid_count += 1
            
            similar_clients.append(SimilarClient(
                client_id=result.payload.get('client_id', 'unknown'),
                similarity=result.score,
                outcome=outcome,
                loan_source=result.payload.get('loan_source', 'unknown'),
                debt_ratio=result.payload.get('debt_ratio', 0.0),
                years_active=result.payload.get('years_active', 0.0)
            ))
        
        # Calculate metrics
        total = len(results)
        confidence = repaid_count / total if total > 0 else 0
        
        # Determine risk level
        if confidence >= 0.8:
            risk_level = "LOW"
        elif confidence >= 0.6:
            risk_level = "MEDIUM"
        elif confidence >= 0.4:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
        
        # Generate recommendation
        if confidence >= 0.7:
            recommendation = f"APPROVE: {repaid_count}/{total} similar clients were approved successfully"
        else:
            recommendation = f"REVIEW REQUIRED: Only {repaid_count}/{total} similar clients were approved"
        # Generate AI explanation
        oracle = CreditOracle()
        oracle_explanation = oracle.explain_decision(
            client_data=request.client_data,
            similar_clients=results,
            decision='approve' if confidence >= 0.7 else 'reject',
            confidence=confidence,
            repaid_count=repaid_count,
            total_count=total
        )
    
        
        
    
        return SearchResponse(
            similar_clients=similar_clients,
            risk_level=risk_level,
            confidence=confidence,
            recommendation=recommendation,
            repaid_count=repaid_count,
            total_count=total,
            oracle_explanation=oracle_explanation
        )
    
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/stats")
async def get_stats():
    """Get collection statistics"""
    try:
        collection = qdrant.client.get_collection("credit_history_memory")
        return {
            "total_clients": collection.points_count,
            "vector_size": collection.config.params.vectors.size,
            "distance_metric": str(collection.config.params.vectors.distance)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))