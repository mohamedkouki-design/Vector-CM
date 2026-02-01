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
        # Extract client_id from request for filtering
        request_client_id = request.client_id
        
        logger.info(f"Search request for client_id: {request_client_id}")
        
        # Get archetype for logging
        if isinstance(request.client_data, dict):
            archetype = request.client_data.get('archetype')
        else:
            archetype = getattr(request.client_data, 'archetype', 'unknown')
        
        logger.info(f"Creating embedding for: {archetype}")
        vector = create_embedding(request.client_data)
        
        # Search Qdrant - request limit + 1 to account for filtering
        results = qdrant.search(
            collection_name="credit_history_memory",
            query_vector=vector.tolist(),
            limit=request.top_k + 1
        )

        logger.info(f"Found {len(results)} similar clients from Qdrant")

        # Filter out the requesting client_id if present in the results
        filtered_results = []
        for r in results:
            payload = getattr(r, 'payload', {}) or {}
            result_client_id = payload.get('client_id')
            
            logger.info(f"Checking result - client_id: {result_client_id} (type: {type(result_client_id).__name__}), request_client_id: {request_client_id} (type: {type(request_client_id).__name__})")
            
            # Skip if this is the requesting client (handle both string and int comparison)
            if request_client_id is not None:
                # Convert to string for comparison to handle int/str mismatches
                if str(result_client_id) == str(request_client_id):
                    logger.info(f"FILTERING OUT: {result_client_id} matches {request_client_id}")
                    continue
            
            filtered_results.append(r)

        logger.info(f"After filtering: {len(filtered_results)} clients remaining")

        # Parse results
        similar_clients = []
        repaid_count = 0

        for result in filtered_results:
            outcome = result.payload.get('actual_outcome', 'REJECTED').lower()
            if outcome == 'repaid':
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
        total = len(filtered_results)
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
            similar_clients=filtered_results,
            decision='approve' if confidence >= 0.7 else 'reject',
            confidence=confidence,
            repaid_count=repaid_count,
            total_count=total
        )
        print(oracle_explanation)
    
        
        
    
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


@router.get("/search/client/{client_id}")
async def get_client_payload(client_id: str):
    """Retrieve the full stored payload for a client by `client_id` from Qdrant."""
    try:
        # Attempt to fetch the point from the collection
        point = qdrant.client.get_point(collection_name="credit_history_memory", id=client_id)

        if not point or not getattr(point, 'payload', None):
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")

        return {"client_id": client_id, "payload": point.payload}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch client {client_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))