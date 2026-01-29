"""
Multimodal endpoints for document upload and processing
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import shutil
from pathlib import Path
import json
import logging

from services.embeddings import create_multimodal_embedding, MULTIMODAL_AVAILABLE
from services.qdrant_manager import QdrantManager
from services.credit_oracle import get_oracle

logger = logging.getLogger(__name__)
router = APIRouter()

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

qdrant = QdrantManager(host="localhost", port=6333)


class MultimodalSearchRequest(BaseModel):
    client_data: Dict[str, Any]
    top_k: int = 50


class MultimodalSearchResponse(BaseModel):
    similar_clients: List[Dict[str, Any]]
    risk_level: str
    confidence: float
    recommendation: str
    oracle_explanation: str
    document_count: int
    multimodal_used: bool


@router.post("/upload-documents")
async def upload_documents(
    files: List[UploadFile] = File(...),
    client_id: str = Form(...)
):
    """
    Upload multiple document images for a client
    
    Supported: invoices, receipts, ID cards, bank statements
    """
    
    if not MULTIMODAL_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Multimodal features not available. Install transformers and torch."
        )
    
    uploaded_paths = []
    
    # Create client directory
    client_dir = UPLOAD_DIR / client_id
    client_dir.mkdir(exist_ok=True)
    
    for file in files:
        # Validate file type
        if not file.content_type.startswith('image/'):
            logger.warning(f"Skipping non-image file: {file.filename}")
            continue
        
        # Save file
        file_path = client_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        uploaded_paths.append(str(file_path))
        logger.info(f"Saved document: {file_path}")
    
    return {
        "client_id": client_id,
        "uploaded_files": len(uploaded_paths),
        "paths": uploaded_paths
    }


@router.post("/search/multimodal", response_model=MultimodalSearchResponse)
async def search_with_documents(request: MultimodalSearchRequest):
    """
    Search using both client data AND uploaded documents
    
    Combines numerical features with document image embeddings
    """
    
    if not MULTIMODAL_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Multimodal features not available"
        )
    
    try:
        # Get uploaded documents for this client
        client_id = request.client_data.get('client_id', 'unknown')
        client_dir = UPLOAD_DIR / client_id
        
        image_paths = []
        if client_dir.exists():
            image_paths = [
                str(p) for p in client_dir.glob("*")
                if p.suffix.lower() in ['.jpg', '.jpeg', '.png']
            ]
        
        logger.info(f"Found {len(image_paths)} documents for client {client_id}")
        
        # Create multimodal embedding
        multimodal_embedding = create_multimodal_embedding(
            client_data=request.client_data,
            image_paths=image_paths
        )
        
        # Search Qdrant
        # Note: Need to update collection to support 896-dim vectors
        results = qdrant.search(
            collection_name="credit_history_memory",
            query_vector=multimodal_embedding.tolist(),
            limit=request.top_k
        )
        
        # Process results (same as regular search)
        similar_clients = []
        repaid_count = 0
        
        for result in results:
            outcome = result.payload.get("actual_outcome", "unknown")
            if outcome == "repaid":
                repaid_count += 1
            
            similar_clients.append({
                "client_id": result.payload.get("client_id"),
                "similarity": result.score,
                "outcome": outcome,
                "loan_source": result.payload.get("loan_source")
            })
        
        # Calculate metrics
        total = len(results)
        confidence = repaid_count / total if total > 0 else 0.0
        
        # Determine risk
        if confidence >= 0.8:
            risk = "LOW"
        elif confidence >= 0.6:
            risk = "MEDIUM"
        else:
            risk = "HIGH"
        
        # Get Oracle explanation
        oracle = get_oracle()
        explanation = oracle.explain_credit_decision(
            client_data=request.client_data,
            similar_clients=similar_clients,
            decision='approve' if confidence >= 0.7 else 'reject',
            confidence=confidence
        )
        
        recommendation = f"MULTIMODAL ANALYSIS: {repaid_count}/{total} similar profiles repaid"
        
        return MultimodalSearchResponse(
            similar_clients=similar_clients,
            risk_level=risk,
            confidence=confidence,
            recommendation=recommendation,
            oracle_explanation=explanation,
            document_count=len(image_paths),
            multimodal_used=len(image_paths) > 0
        )
    
    except Exception as e:
        logger.error(f"Multimodal search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{client_id}")
async def list_documents(client_id: str):
    """List uploaded documents for a client"""
    
    client_dir = UPLOAD_DIR / client_id
    
    if not client_dir.exists():
        return {"client_id": client_id, "documents": []}
    
    documents = [
        {
            "filename": p.name,
            "size": p.stat().st_size,
            "path": str(p)
        }
        for p in client_dir.glob("*")
        if p.is_file()
    ]
    
    return {
        "client_id": client_id,
        "documents": documents,
        "count": len(documents)
    }