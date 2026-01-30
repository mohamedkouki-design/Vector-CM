from fastapi import APIRouter, HTTPException, UploadFile, File
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
import sys
import os
import torch
import shutil
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_path
from transformers import CLIPProcessor, CLIPModel

logger = logging.getLogger(__name__)
router = APIRouter()

client = QdrantClient(host="localhost", port=6333)

# Document fraud detection configuration
DOCUMENT_COLLECTION_NAME = "document_risk_engine"
FRAUD_THRESHOLD = 0.96 
SUSPICION_THRESHOLD = 0.85

# Load CLIP model for document analysis
try:
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
except Exception as e:
    logger.warning(f"Could not load CLIP model for document analysis: {e}")
    clip_model = None
    clip_processor = None

# Initialize Qdrant manager for fraud pattern storage
qdrant_manager = QdrantManager()

# Upload directory configuration
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), '../../uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

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


class OutcomeUpdateRequest(BaseModel):
    client_id: str
    outcome: str
    actual_outcome: str


def get_document_vector(image):
    """Converts a PIL Image object into a normalized 512-dim vector using CLIP."""
    if clip_model is None or clip_processor is None:
        return None
    
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        output = clip_model.get_image_features(**inputs)
    
    # Extract tensor from output object if needed
    image_features = output.pooler_output if hasattr(output, 'pooler_output') else output
    
    # Ensure it's a tensor and normalize
    if not isinstance(image_features, torch.Tensor):
        image_features = torch.tensor(image_features)
    
    # Normalize for Cosine Similarity
    return image_features / image_features.norm(p=2, dim=-1, keepdim=True)


def analyze_document(file_path: str) -> Dict[str, Any]:
    """Analyzes a document for fraud by comparing against known fake patterns.
    
    Returns dict with keys:
    - forged: bool (True if high confidence fraud detected)
    - reason: str (explanation)
    - indicators: list (fraud indicators)
    - risk_level: str ('safe', 'suspicious', or 'fraud')
    - score: float (similarity score to nearest fraud pattern)
    """
    
    if clip_model is None or clip_processor is None:
        logger.warning("Document analysis unavailable (CLIP model not loaded)")
        return {"forged": False, "reason": "document analysis unavailable", "risk_level": "unknown", "indicators": [], "score": 0}
    
    logger.info(f"Analyzing document: {file_path}")
    
    try:
        # Handle PDF or Image
        if file_path.lower().endswith('.pdf'):
            try:
                poppler_path = os.path.join(os.path.dirname(__file__), '../../doc_check/poppler-25.12.0/Library/bin')
                images = convert_from_path(file_path, poppler_path=poppler_path)
                query_img = images[0]
            except Exception as e:
                logger.error(f"Could not convert PDF: {e}")
                return {"forged": False, "reason": f"PDF processing error: {e}", "risk_level": "unknown", "indicators": [], "score": 0}
        else:
            query_img = Image.open(file_path)
        
        # Vectorize the document
        query_vector = get_document_vector(query_img)
        if query_vector is None:
            return {"forged": False, "reason": "vectorization failed", "risk_level": "unknown", "indicators": [], "score": 0}
        
        query_vector = query_vector[0].tolist()
        
        # Search for similar fraud patterns using qdrant_manager
        try:
            hits = qdrant_manager.client.query_points(
                collection_name=DOCUMENT_COLLECTION_NAME,
                query=query_vector,
                limit=3
            )
        except Exception as e:
            logger.error(f"Failed to query fraud patterns: {e}")
            return {"forged": False, "reason": "database query failed", "risk_level": "unknown", "indicators": [], "score": 0}
        
        if not hits or not hits.points:
            logger.info("No fraud patterns found in database")
            return {"forged": False, "reason": "no reference patterns available", "risk_level": "safe", "indicators": [], "score": 0}
        
        top_match = hits.points[0]
        score = top_match.score
        
        # Decision logic
        if score >= FRAUD_THRESHOLD:
            logger.warning(f"High risk fraud detected: {score:.4f}")
            return {
                "forged": True,
                "reason": f"Visual structure is {score*100:.1f}% identical to known fraud pattern",
                "risk_level": "fraud",
                "indicators": ["visual_match_to_fake", "high_similarity"],
                "score": score
            }
        elif score >= SUSPICION_THRESHOLD:
            logger.warning(f"Suspicious document detected: {score:.4f}")
            return {
                "forged": False,
                "reason": f"Document layout matches known fakes but with variance (similarity: {score:.4f})",
                "risk_level": "suspicious",
                "indicators": ["layout_similarity", "requires_review"],
                "score": score
            }
        else:
            logger.info(f"Document passed fraud check: {score:.4f}")
            return {
                "forged": False,
                "reason": "Document layout is distinct from known fraud patterns",
                "risk_level": "safe",
                "indicators": [],
                "score": score
            }
            
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        return {
            "forged": False,
            "reason": f"Analysis error: {str(e)}",
            "risk_level": "unknown",
            "indicators": ["analysis_error"],
            "score": 0
        }


def document_check_placeholder(documents: List[str], applicant: Dict[str, Any] = None) -> Dict[str, Any]:
    """Analyzes documents for fraud and creates fraud_patterns points if score >= FRAUD_THRESHOLD.
    
    Args:
        documents: List of full file paths to analyze (from upload endpoint)
        applicant: Optional applicant data to include in fraud pattern payload
    
    Returns:
        Aggregated analysis result
    """
    if not documents:
        return {"forged": False, "reason": "no documents provided", "indicators": []}
    
    # Analyze each document
    results = []
    for doc_path in documents:
        if os.path.exists(doc_path):
            result = analyze_document(doc_path)
            results.append(result)
            
            # Create fraud_patterns point if score >= FRAUD_THRESHOLD
            if result.get("score", 0) >= FRAUD_THRESHOLD:
                try:
                    fraud_id = f"FRAUD_{uuid.uuid4().hex[:8].upper()}"
                    
                    # Build fraud payload matching the structure
                    fraud_payload = {
                        "fraud_id": fraud_id,
                        "fraud_type": "document_forgery",
                        "archetype": applicant.get("archetype") if applicant else "unknown",
                        "debt_ratio": float(applicant.get("debt_ratio", 0)) if applicant else 0.0,
                        "income_stability": float(applicant.get("income_stability", 0)) if applicant else 0.0,
                        "fraud_narrative": result.get("reason", "Document visual structure matches known forgery patterns"),
                        "fraud_indicators": result.get("indicators", []),
                        "document_path": doc_path,
                        "similarity_score": result.get("score", 0)
                    }
                    
                    # Create embedding for the fraud point
                    fraud_vector = create_embedding(fraud_payload)
                    fraud_vector = np.array(fraud_vector)
                    norm = np.linalg.norm(fraud_vector)
                    if norm > 0:
                        fraud_vector = fraud_vector / norm
                    fraud_vector_list = fraud_vector.tolist() if hasattr(fraud_vector, 'tolist') else list(fraud_vector)
                    
                    # Ensure correct dimension
                    if len(fraud_vector_list) != EMBEDDING_SIZE:
                        if len(fraud_vector_list) < EMBEDDING_SIZE:
                            fraud_vector_list += [0.0] * (EMBEDDING_SIZE - len(fraud_vector_list))
                        else:
                            fraud_vector_list = fraud_vector_list[:EMBEDDING_SIZE]
                    
                    # Create fraud point
                    fraud_point_id = int(datetime.utcnow().timestamp() * 1000000) % (2**31 - 1)
                    fraud_point = PointStruct(id=fraud_point_id, payload=fraud_payload, vector=fraud_vector_list)
                    
                    # Upsert to fraud_patterns collection
                    client.upsert(collection_name="fraud_patterns", points=[fraud_point])
                    logger.info(f"Created fraud pattern point: fraud_id={fraud_id}, score={result.get('score', 0):.4f}")
                    
                except Exception as e:
                    logger.error(f"Failed to create fraud pattern point: {e}")
        else:
            logger.warning(f"Document not found: {doc_path}")
            results.append({"forged": False, "reason": f"file not found: {doc_path}", "indicators": [], "score": 0})
    
    # Aggregate results
    forged = any(r.get("forged", False) for r in results)
    high_fraud_score = any(r.get("score", 0) >= FRAUD_THRESHOLD for r in results)
    risk_levels = [r.get("risk_level", "unknown") for r in results]
    
    return {
        "forged": forged or high_fraud_score,
        "reason": "fraud" if forged or high_fraud_score else "documents passed verification",
        "indicators": ["document_forgery"] if forged or high_fraud_score else [],
        "risk_levels": risk_levels,
        "details": results
    }


@router.post("/applications/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents and return their saved file paths."""
    try:
        uploaded_paths = []
        
        for file in files:
            # Generate unique filename to avoid conflicts
            file_ext = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            file_path = os.path.join(UPLOADS_DIR, unique_filename)
            
            # Save file to disk
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_paths.append({
                "original_name": file.filename,
                "saved_name": unique_filename,
                "path": file_path
            })
            logger.info(f"Document uploaded: {unique_filename}")
        
        return {
            "status": "success",
            "count": len(uploaded_paths),
            "files": uploaded_paths
        }
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.get("/applications/status/{client_id}")
async def check_application_status(client_id: str):
    """Check the status of an application by client_id from credit_history_memory."""
    try:
        # Scroll through credit_history_memory to find the client
        offset = 0
        batch_size = 1000
        max_iterations = 100
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            try:
                batch, next_offset = client.scroll(
                    collection_name="credit_history_memory",
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
            except Exception as e:
                logger.error(f"Failed to scroll credit_history_memory: {e}")
                break

            if not batch:
                break

            for point in batch:
                try:
                    payload = getattr(point, 'payload', {})
                    if not payload:
                        continue
                    
                    cid = payload.get('client_id')
                    if cid == client_id:
                        # Found the client, return their status
                        return {
                            'client_id': client_id,
                            'status': payload.get('outcome') or payload.get('status') or 'pending',
                            'outcome': payload.get('outcome') or 'pending',
                            'rejection_reason': payload.get('actual_outcome') if payload.get('outcome') == 'rejected' else None
                        }
                except Exception:
                    continue

            if next_offset == offset or len(batch) < batch_size:
                break

            offset = next_offset

        # Client not found
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check application status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications", response_model=ApplicationListResponse)
async def get_applications(client_id: str = None, limit: int = 50):
    """Fetch recent applications from `credit_history_memory` where payload.outcome == 'pending'."""
    try:
        applications = []
        offset = 0
        batch_size = 1000
        max_iterations = 100
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            try:
                batch, next_offset = client.scroll(
                    collection_name="credit_history_memory",
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
            except Exception as e:
                logger.error(f"Failed to scroll credit_history_memory: {e}")
                break

            if not batch:
                break

            for point in batch:
                try:
                    payload = getattr(point, 'payload', {})
                    if not payload:
                        continue
                    # Only include pending outcomes
                    if payload.get('outcome') != 'pending':
                        continue

                    cid = payload.get('client_id')
                    if client_id and cid != client_id:
                        continue

                    # Map to legacy application response shape expected by frontend
                    debt_ratio = payload.get('debt_ratio')
                    income_stability = payload.get('income_stability')
                    payment_regularity = payload.get('payment_regularity')

                    # Compute fallback risk_score if not present in credit_history point
                    try:
                        if payload.get('risk_score') is not None:
                            risk_score = payload.get('risk_score')
                        else:
                            dr = float(debt_ratio) if debt_ratio is not None else 0.0
                            inc = float(income_stability) if income_stability is not None else 0.0
                            pay = float(payment_regularity) if payment_regularity is not None else 0.0
                            risk_score = round(dr * 0.6 + (1 - inc) * 0.2 + (1 - pay) * 0.2, 3)
                    except Exception:
                        risk_score = payload.get('risk_score')

                    # Attempt to find matching T0 point in temporal_risk_memory to get authoritative date and risk_score and use its id
                    temporal_date = None
                    temporal_risk = None
                    temporal_id = None
                    try:
                        t_offset = 0
                        t_batch_size = 500
                        t_iters = 0
                        while t_iters < 20:
                            t_iters += 1
                            t_batch, t_next = client.scroll(
                                collection_name='temporal_risk_memory',
                                limit=t_batch_size,
                                offset=t_offset,
                                with_payload=True,
                                with_vectors=False
                            )
                            if not t_batch:
                                break
                            for tpoint in t_batch:
                                t_payload = getattr(tpoint, 'payload', {}) or {}
                                if t_payload.get('client_id') == cid and str(t_payload.get('timestamp', '')).startswith('T0'):
                                    temporal_date = t_payload.get('date')
                                    temporal_risk = t_payload.get('risk_score')
                                    temporal_id = getattr(tpoint, 'id', None)
                                    break
                            if temporal_id is not None:
                                break
                            if t_next == t_offset or len(t_batch) < t_batch_size:
                                break
                            t_offset = t_next
                    except Exception as e:
                        logger.debug(f"Temporal lookup failed for {cid}: {e}")

                    # Prefer temporal values if found
                    final_date = temporal_date or (payload.get('date') or payload.get('created_at') or None)
                    final_risk = temporal_risk if temporal_risk is not None else risk_score
                    final_id = temporal_id or getattr(point, 'id', None)

                    applications.append({
                        'id': final_id,
                        'client_id': cid,
                        'timestamp': payload.get('timestamp', 'T0_application'),
                        'date': final_date,
                        'risk_score': final_risk,
                        'status': payload.get('status') or payload.get('outcome') or 'pending',
                        'debt_ratio': debt_ratio,
                        'income_stability': income_stability,
                        'payment_regularity': payment_regularity
                    })
                except Exception:
                    continue

            if next_offset == offset or len(batch) < batch_size:
                break

            offset = next_offset

        # Sort by id descending as a proxy for recency
        applications.sort(key=lambda x: x.get('id') or 0, reverse=True)

        return ApplicationListResponse(applications=applications[:limit], total=len(applications))
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

        # Run document check and create fraud patterns if needed
        doc_result = document_check_placeholder(request.documents, applicant)

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


@router.post("/applications/update-outcome", response_model=Dict[str, Any])
async def update_outcome(request: OutcomeUpdateRequest):
    """Update application outcome in credit_history_memory."""
    try:
        # Get all points and find the one with matching client_id
        all_points = []
        offset = 0
        batch_size = 1000
        
        while True:
            batch, next_offset = client.scroll(
                collection_name="credit_history_memory",
                limit=batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )
            if not batch:
                break
            all_points.extend(batch)
            if next_offset == offset or len(batch) < batch_size:
                break
            offset = next_offset
        
        # Find point with matching client_id
        target_point = None
        for point in all_points:
            if point.payload.get('client_id') == request.client_id:
                target_point = point
                break
        
        if not target_point:
            raise HTTPException(status_code=404, detail=f"Client {request.client_id} not found")
        
        # Update payload
        target_point.payload['outcome'] = request.outcome
        target_point.payload['actual_outcome'] = request.actual_outcome
        
        # Convert scrolled Record into PointStruct for upsert
        try:
            vec = None
            # Record may have attribute 'vector' or 'vectors'
            if hasattr(target_point, 'vector'):
                vec = getattr(target_point, 'vector')
            elif hasattr(target_point, 'vectors'):
                vec = getattr(target_point, 'vectors')

            upsert_point = PointStruct(
                id=getattr(target_point, 'id', None),
                payload=getattr(target_point, 'payload', {}),
                vector=vec
            )

            client.upsert(
                collection_name="credit_history_memory",
                points=[upsert_point]
            )
        except Exception as e:
            # Fallback: try to build a dict payload accepted by the client
            try:
                point_dict = {
                    'id': getattr(target_point, 'id', None),
                    'payload': getattr(target_point, 'payload', {}),
                    'vector': getattr(target_point, 'vector', None) or getattr(target_point, 'vectors', None)
                }
                client.upsert(collection_name="credit_history_memory", points=[point_dict])
            except Exception as e2:
                logger.error(f"Failed to upsert updated point: {e2}")
                raise
        
        logger.info(f"Updated {request.client_id}: outcome={request.outcome}, actual_outcome={request.actual_outcome}")
        
        return {
            'status': 'success',
            'client_id': request.client_id,
            'outcome': request.outcome,
            'actual_outcome': request.actual_outcome
        }
    except Exception as e:
        logger.error(f"Failed to update outcome: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
