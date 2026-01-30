from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from services.qdrant_manager import QdrantManager
from services.embeddings import create_embedding
import numpy as np
EMBEDDING_SIZE = 384
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import uuid
from datetime import datetime
import logging
import json
import random

logger = logging.getLogger(__name__)
router = APIRouter()

client = QdrantClient(host="localhost", port=6333)

class ApplicationSubmission(BaseModel):
    applicant: Dict[str, Any]
    documents: List[str] = []

class ApplicationResponse(BaseModel):
    client_id: str
    status: str
    message: str
    created_point: Dict[str, Any] = {}

class ApplicationListResponse(BaseModel):
    applications: List[Dict[str, Any]] = []
    total: int = 0

class CreditHistorySubmission(BaseModel):
    name: str
    archetype: str
    years_active: float
    monthly_income: float
    debt_ratio: float = 0.45
    income_stability: float = 0.85
    payment_regularity: float = 0.88
    client_id: str = None  # Optional: use existing client_id if provided


def document_check_placeholder(documents: List[str]) -> Dict[str, Any]:
    """Placeholder for document authenticity check.
    Replace this with actual checks (e.g., call DocumentChecker with file bytes).
    Returns dict with keys: forged (bool), reason (str)
    """
    # TODO: integrate real document checker (e.g., import SimpleDocumentChecker)
    return {"forged": False, "reason": "placeholder: not checked"}


@router.get("/applications", response_model=ApplicationListResponse)
async def get_applications(client_id: str = None, limit: int = 50):
    """Fetch applications from temporal_risk_memory where client has exactly 1 T0 point."""
    try:
        # Scroll through temporal_risk_memory collection and group by client_id
        all_points_by_client = {}
        offset = 0
        batch_size = 1000
        max_iterations = 100
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            try:
                batch, next_offset = client.scroll(
                    collection_name="temporal_risk_memory",
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
            except Exception as e:
                logger.error(f"Failed to scroll temporal_risk_memory: {e}")
                break
            
            if not batch:
                break
            
            # Group points by client_id
            for point in batch:
                cid = point.payload.get("client_id")
                if cid:
                    if cid not in all_points_by_client:
                        all_points_by_client[cid] = []
                    all_points_by_client[cid].append(point)
            
            # If next_offset is same as current offset or no more batches, break
            if next_offset == offset or len(batch) < batch_size:
                break
            
            offset = next_offset
        
        # Filter to only clients with exactly 1 T0 point
        applications = []
        for cid, pts in all_points_by_client.items():
            if len(pts) == 1:
                point = pts[0]
                # Check if it's a T0 point
                timestamp = point.payload.get("timestamp", "")
                if timestamp.startswith("T0"):
                    # Optionally filter by client_id if provided
                    if client_id and cid != client_id:
                        continue
                    
                    applications.append({
                        "id": point.id,
                        "client_id": point.payload.get("client_id"),
                        "timestamp": point.payload.get("timestamp"),
                        "date": point.payload.get("date"),
                        "risk_score": point.payload.get("risk_score"),
                        "status": point.payload.get("status"),
                        "debt_ratio": point.payload.get("debt_ratio"),
                        "income_stability": point.payload.get("income_stability"),
                        "payment_regularity": point.payload.get("payment_regularity")
                    })
        
        # Sort by date descending (newest first)
        applications.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return ApplicationListResponse(
            applications=applications[:limit],
            total=len(applications)
        )
    except Exception as e:
        logger.error(f"Failed to fetch applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/submit", response_model=ApplicationResponse)
async def submit_application(request: ApplicationSubmission):
    """Receive a submitted application, create a T0 temporal point and optionally flag fraud."""
    try:
        applicant = request.applicant
        # Generate client id
        client_id = applicant.get('client_id') or f"CLIENT_{uuid.uuid4().hex[:8]}"

        # Compute a simple risk score heuristic
        debt_ratio = float(applicant.get('debt_ratio', 0.0))
        income_stability = float(applicant.get('income_stability', 0.0))
        payment_regularity = float(applicant.get('payment_regularity', 0.0))
        risk_score = round(debt_ratio * 0.6 + (1 - income_stability) * 0.2 + (1 - payment_regularity) * 0.2, 3)

        # Build temporal payload matching populate_qdrant.py structure
        payload = {
            "client_id": client_id,
            "timestamp": "T0_application",
            "date": datetime.utcnow().isoformat(),
            "risk_score": risk_score,
            "status": "pending",
            "debt_ratio": debt_ratio,
            "income_stability": income_stability,
            "payment_regularity": payment_regularity
        }

        # Create embedding from a compact temporal representation (same as populate_qdrant)
        try:
            temp_data = {
                'archetype': applicant.get('archetype') or applicant.get('business_type'),
                'debt_ratio': debt_ratio,
                'years_active': float(applicant.get('years_active', 0)),
                'income_stability': income_stability,
                'payment_regularity': payment_regularity,
                'monthly_income': float(applicant.get('monthly_income', 0))
            }
            vector = create_embedding(temp_data)
            # normalize if numpy array
            try:
                vector = np.array(vector)
                norm = np.linalg.norm(vector)
                if norm > 0:
                    vector = vector / norm
            except Exception:
                pass
            vector_list = vector.tolist() if hasattr(vector, 'tolist') else None
            # Validate embedding length and pad/trim if necessary
            if isinstance(vector_list, list):
                if len(vector_list) != EMBEDDING_SIZE:
                    logger.warning(f"Embedding length {len(vector_list)} != {EMBEDDING_SIZE}, attempting fallback using full applicant data")
                    # Try fallback embedding using full applicant dict
                    try:
                        fb_vector = create_embedding(applicant)
                        fb_vector = np.array(fb_vector)
                        norm = np.linalg.norm(fb_vector)
                        if norm > 0:
                            fb_vector = fb_vector / norm
                        fb_list = fb_vector.tolist()
                        if len(fb_list) == EMBEDDING_SIZE:
                            vector_list = fb_list
                        else:
                            # Pad or trim to expected size
                            if len(fb_list) < EMBEDDING_SIZE:
                                fb_list += [0.0] * (EMBEDDING_SIZE - len(fb_list))
                            else:
                                fb_list = fb_list[:EMBEDDING_SIZE]
                            vector_list = fb_list
                    except Exception:
                        # As a last resort, pad/trim the original vector
                        if len(vector_list) < EMBEDDING_SIZE:
                            vector_list += [0.0] * (EMBEDDING_SIZE - len(vector_list))
                        else:
                            vector_list = vector_list[:EMBEDDING_SIZE]
            else:
                vector_list = None
        except Exception:
            vector_list = None

        # If vector creation failed entirely, create a zero-vector fallback to satisfy collection vector schema
        if vector_list is None:
            logger.warning("Embedding creation failed; using zero-vector fallback to avoid Qdrant 400 error")
            vector_list = [0.0] * EMBEDDING_SIZE

        # Upsert point into temporal_risk_memory
        # Use integer point id (temporal points in populate_qdrant use integer ids)
        point_id = int(datetime.utcnow().timestamp() * 1000)
        payload["client_id"] = client_id
        point = PointStruct(id=point_id, payload=payload, vector=vector_list)

        # Debug: ensure payload is JSON serializable and log vector length/type
        try:
            _ = json.dumps(payload)
        except Exception as e:
            logger.error(f"Temporal payload not JSON serializable: {e} - payload keys: {list(payload.keys())}")

        try:
            v_len = len(vector_list) if isinstance(vector_list, list) else None
        except Exception:
            v_len = None
        logger.info(f"Upserting temporal point id={point_id} client_id={client_id} vector_len={v_len}")

        try:
            client.upsert(collection_name="temporal_risk_memory", points=[point])
        except Exception as e:
            # Some qdrant-client versions use upsert_points
            logger.error(f"Upsert failed (first attempt): {e}")
            try:
                client.upsert_points(collection_name="temporal_risk_memory", points=[point])
            except Exception as e2:
                logger.error(f"Upsert failed (fallback attempt): {e2}")
                raise HTTPException(status_code=500, detail=f"Failed to store application point: {e2}")

        # Run document check placeholder
        doc_result = document_check_placeholder(request.documents)
        if doc_result.get('forged'):
            # create fraud pattern point using same fields as populate_qdrant
            fraud_payload = {
                'fraud_id': f"fraud_{client_id}",
                'fraud_type': 'document_forgery',
                'archetype': applicant.get('archetype') or applicant.get('business_type'),
                'debt_ratio': float(debt_ratio),
                'income_stability': float(income_stability),
                'fraud_narrative': doc_result.get('reason', 'forged documents'),
                'fraud_indicators': doc_result.get('indicators', [])
            }
            fraud_point_id = point_id + 1
            fraud_point = PointStruct(id=fraud_point_id, payload=fraud_payload, vector=vector_list)
            try:
                client.upsert(collection_name="fraud_patterns", points=[fraud_point])
            except Exception as e:
                logger.error(f"Fraud upsert failed (first attempt): {e}")
                try:
                    client.upsert_points(collection_name="fraud_patterns", points=[fraud_point])
                except Exception as e2:
                    logger.error(f"Failed to create fraud point: {e2}")

        return ApplicationResponse(
            client_id=client_id,
            status="submitted",
            message="Application received and stored.",
            created_point=payload
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Application submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


LOCATIONS = ['Tunis', 'Sfax', 'Sousse', 'Gabes', 'Ariana', 'Ben Arous', 'Bizerte', 'Nabeul']


@router.post("/applications/add-to-credit-history", response_model=Dict[str, Any])
async def add_to_credit_history(request: CreditHistorySubmission):
    """Create a 384-dim vector point in credit_history_memory with pending outcomes and random location."""
    try:
        # Use provided client_id or generate a new one
        client_id = request.client_id if request.client_id else f"CLIENT_{uuid.uuid4().hex[:8].upper()}"
        
        # Create embedding from applicant data
        applicant_data = {
            'archetype': request.archetype,
            'debt_ratio': request.debt_ratio,
            'years_active': request.years_active,
            'income_stability': request.income_stability,
            'payment_regularity': request.payment_regularity,
            'monthly_income': request.monthly_income
        }
        
        vector = create_embedding(applicant_data)
        vector = np.array(vector)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        vector_list = vector.tolist() if hasattr(vector, 'tolist') else list(vector)
        
        # Ensure 384 dimensions
        if len(vector_list) != EMBEDDING_SIZE:
            if len(vector_list) < EMBEDDING_SIZE:
                vector_list += [0.0] * (EMBEDDING_SIZE - len(vector_list))
            else:
                vector_list = vector_list[:EMBEDDING_SIZE]
        
        # Create payload with pending outcomes and random location
        payload = {
            'client_id': client_id,
            'name': request.name,
            'archetype': request.archetype,
            'employment_type': 'informal',  # Default based on payment pattern
            'years_active': float(request.years_active),
            'monthly_income': float(request.monthly_income),
            'debt_ratio': float(request.debt_ratio),
            'income_stability': float(request.income_stability),
            'payment_regularity': float(request.payment_regularity),
            'loan_source': 'community_lending',
            'outcome': 'pending',
            'actual_outcome': 'pending',
            'location': random.choice(LOCATIONS),
            'social_network': '[]'  # Empty social network for new applicant
        }
        
        # Use timestamp-based id for uniqueness
        point_id = int(datetime.utcnow().timestamp() * 1000000) % (2**31 - 1)
        point = PointStruct(id=point_id, vector=vector_list, payload=payload)
        
        # Upsert into credit_history_memory
        client.upsert(collection_name="credit_history_memory", points=[point])
        logger.info(f"✅ Created credit history point id={point_id} client_id={client_id} location={payload['location']}")
        
        return {
            'client_id': client_id,
            'point_id': point_id,
            'location': payload['location'],
            'status': 'pending',
            'message': 'Successfully created credit history point'
        }
        
    except Exception as e:
        logger.error(f"Failed to create credit history point: {e}")
        raise HTTPException(status_code=500, detail=str(e))
