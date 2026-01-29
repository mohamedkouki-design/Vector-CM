import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Singleton model
_encoder = None

def get_encoder():
    """Get or create encoder (singleton)"""
    global _encoder
    if _encoder is None:
        logger.info("Loading sentence transformer model...")
        _encoder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
    return _encoder

def create_embedding(client_data):
    """
    Create 384-dim embedding from client data
    
    Args:
        client_data: dict or Series with keys:
            - archetype
            - debt_ratio
            - years_active
            - income_stability
            - payment_regularity
            - monthly_income (optional)
    
    Returns:
        numpy array of shape (384,) - L2 normalized
    """
    encoder = get_encoder()
    
    # Extract features with defaults
    archetype = str(client_data.get('archetype', 'unknown'))
    debt_ratio = float(client_data.get('debt_ratio', 0.5))
    years_active = float(client_data.get('years_active', 5))
    income_stability = float(client_data.get('income_stability', 0.7))
    payment_regularity = float(client_data.get('payment_regularity', 0.8))
    monthly_income = float(client_data.get('monthly_income', 1500))
    
    # Part 1: Text embedding (128 dims)
    text = f"{archetype} business"
    text_emb = encoder.encode(text)
    text_features = text_emb[:128]
    
    # Part 2: Financial features (128 dims)
    financial = np.array([
        debt_ratio,
        years_active / 20,  # Normalize to [0,1]
        income_stability,
        monthly_income / 5000,  # Normalize
        payment_regularity
    ])
    financial_padded = np.pad(financial, (0, 128 - len(financial)))
    
    # Part 3: Behavioral features (128 dims)
    behavioral = np.zeros(128)
    behavioral[0] = calculate_risk_score(client_data)
    behavioral[1] = income_stability * payment_regularity  # Combined metric
    
    # Combine all parts
    full_vector = np.concatenate([
        text_features,
        financial_padded,
        behavioral
    ])
    
    # CRITICAL: L2 normalize
    norm = np.linalg.norm(full_vector)
    if norm > 0:
        normalized = full_vector / norm
    else:
        normalized = full_vector
    
    logger.debug(f"Created embedding with norm: {np.linalg.norm(normalized):.4f}")
    
    return normalized

def calculate_risk_score(client_data):
    """Calculate simple risk score [0,1]"""
    debt_ratio = float(client_data.get('debt_ratio', 0.5))
    income_stability = float(client_data.get('income_stability', 0.7))
    payment_regularity = float(client_data.get('payment_regularity', 0.8))
    
    risk = (
        debt_ratio * 0.4 +
        (1 - income_stability) * 0.3 +
        (1 - payment_regularity) * 0.3
    )
    
    return min(1.0, max(0.0, risk))

# Backward compatibility
def create_client_embedding(client_data):
    """Alias for create_embedding"""
    return create_embedding(client_data)