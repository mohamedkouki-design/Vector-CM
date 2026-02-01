from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SearchRequest(BaseModel):
    client_data: Dict[str, Any]
    client_id: Optional[str] = None  # Optional: client_id to filter out from results
    top_k: int = 50

class SimilarClient(BaseModel):
    client_id: str
    similarity: float
    outcome: Optional[str] = None
    loan_source: str
    debt_ratio: float
    years_active: float

class SearchResponse(BaseModel):
    similar_clients: List[SimilarClient]
    risk_level: str
    confidence: float
    recommendation: str
    repaid_count: int
    total_count: int
    oracle_explanation: str = ""