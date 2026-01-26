# Vector generation 
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

class CreditEmbedder:
    def __init__(self):
        # For text descriptions (if needed later)
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def _normalize_employment_type(self, employment_type):
        """Handle different employment type formats"""
        if pd.isna(employment_type):
            return 0
        emp_str = str(employment_type).lower()
        if 'formal' in emp_str:
            return 1.0
        elif 'mixed' in emp_str:
            return 0.5
        else:  # informal
            return 0.0
    
    def _safe_get(self, data, key, default=0.0):
        """Safely get value from dict/Series with default"""
        try:
            val = data.get(key) if isinstance(data, dict) else data[key]
            return float(val) if val is not None else default
        except (KeyError, TypeError, ValueError):
            return default
    
    def _normalize_value(self, value, min_val, max_val):
        """Normalize value to [0, 1] range using min-max scaling"""
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)
    
    def create_simple_vector(self, client_row):
        """Extended vector with full data structure (12 dimensions)
        Uses realistic financial bounds for MENA informal economy
        """
        features = [
            # Core financial (8D) - normalized to realistic ranges
            min(1.0, max(0.0, self._safe_get(client_row, 'income') / 5000)),  # 0-5000 maps to 0-1
            min(1.0, max(0.0, self._safe_get(client_row, 'expenses') / 5000)),
            min(1.0, max(0.0, self._safe_get(client_row, 'debt') / 10000)),  # 0-10000 maps to 0-1
            self._safe_get(client_row, 'age') / 100,  # 0-100 age
            min(1.0, self._safe_get(client_row, 'seniority_months') / 120),  # 0-120 months = 0-1
            min(1.0, max(0.0, self._safe_get(client_row, 'payment_consistency', 0.5))),  # Already 0-1
            min(1.0, max(0.0, self._safe_get(client_row, 'loan_amount') / 15000)),  # 0-15000 maps to 0-1
            self._normalize_employment_type(client_row.get('employment_type') if isinstance(client_row, dict) else client_row['employment_type']),
            # Extended informal economy (4D)
            min(1.0, max(0.0, self._safe_get(client_row, 'mobile_payment_ratio', 0.5))),
            min(1.0, max(0.0, self._safe_get(client_row, 'ledger_quality_score', 0.5))),
            min(1.0, max(0.0, self._safe_get(client_row, 'risk_score', 0.5))),
            float(self._safe_get(client_row, 'is_fraud', 0)),  # Fraud indicator (1.0 = fraud, 0.0 = legitimate)
        ]
        return features

# Test
if __name__ == "__main__":
    import pandas as pd
    from demo_data import VectorCMDataGenerator
    
    # Generate test data using demo_data
    generator = VectorCMDataGenerator()
    test_clients = [generator.generate_client_profile(i) for i in range(5)]
    
    embedder = CreditEmbedder()
    
    # Test simple version (faster for demo)
    test_vector = embedder.create_simple_vector(test_clients[0])
    print(f"✅ Simple Vector Dimension: {len(test_vector)} features")
    print(f"   Sample vector: {test_vector[:4]}")
    
    # Test full vector with text embedding
    full_vector = embedder.create_client_vector(test_clients[0])
    print(f"\n✅ Full Vector Dimension: {len(full_vector)} (12D numerical + text embedding)")
    
    # Display data structure used
    print(f"\n📊 Sample Client Data Structure:")
    client = test_clients[0]
    for key, value in client.items():
        if key != 'risk_narrative':  # Skip long narrative for display
            print(f"   {key}: {value}")

