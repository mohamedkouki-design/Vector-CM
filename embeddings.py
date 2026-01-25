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
    
    def create_client_vector(self, client_row):       
        """Convert client data to vector with full data structure"""
        # Core financial features (8D)
        features = [
            self._safe_get(client_row, 'income') / 5000,
            self._safe_get(client_row, 'expenses') / 5000,
            self._safe_get(client_row, 'debt') / 10000,
            self._safe_get(client_row, 'age') / 100,
            self._safe_get(client_row, 'seniority_months') / 120,
            self._safe_get(client_row, 'payment_consistency', 0.5),
            self._safe_get(client_row, 'loan_amount') / 10000,
            self._normalize_employment_type(client_row.get('employment_type') if isinstance(client_row, dict) else client_row['employment_type']),
        ]
        
        # Extended features from informal economy (4D)
        extended_features = [
            self._safe_get(client_row, 'mobile_payment_ratio', 0.5),
            self._safe_get(client_row, 'ledger_quality_score', 0.5),
            self._safe_get(client_row, 'risk_score', 0.5),
            1.0 if self._safe_get(client_row, 'is_fraud', 0) == 0 else 0.0,  # Non-fraud indicator
        ]
        
        # Create rich text description for semantic embedding
        description = f"""
        Income: {self._safe_get(client_row, 'income'):.0f}, 
        Expenses: {self._safe_get(client_row, 'expenses'):.0f},
        Debt: {self._safe_get(client_row, 'debt'):.0f}, 
        Business seniority: {self._safe_get(client_row, 'seniority_months'):.0f} months,
        Payment consistency: {self._safe_get(client_row, 'payment_consistency', 0.5):.2f},
        Mobile payment usage: {self._safe_get(client_row, 'mobile_payment_ratio', 0.5):.2f},
        Ledger quality: {self._safe_get(client_row, 'ledger_quality_score', 0.5):.2f},
        Age: {self._safe_get(client_row, 'age'):.0f},
        Loan request: {self._safe_get(client_row, 'loan_amount'):.0f},
        Employment: {client_row.get('employment_type', 'informal') if isinstance(client_row, dict) else client_row.get('employment_type', 'informal')}
        """
        
        # Get text embedding
        text_embedding = self.text_model.encode(description)
        
        # Combine all features (late fusion)
        numerical_vector = np.array(features + extended_features)
        
        # Weighted combination of numerical and text features
        combined = np.concatenate([
            numerical_vector * 10,  # Weight numerical features
            text_embedding
        ])
        
        return combined.tolist()
    
    def create_simple_vector(self, client_row):
        """Extended vector with full data structure (12 dimensions)"""
        features = [
            # Core financial (8D)
            self._safe_get(client_row, 'income') / 5000,
            self._safe_get(client_row, 'expenses') / 5000,
            self._safe_get(client_row, 'debt') / 10000,
            self._safe_get(client_row, 'age') / 100,
            self._safe_get(client_row, 'seniority_months') / 120,
            self._safe_get(client_row, 'payment_consistency', 0.5),
            self._safe_get(client_row, 'loan_amount') / 10000,
            self._normalize_employment_type(client_row.get('employment_type') if isinstance(client_row, dict) else client_row['employment_type']),
            # Extended informal economy (4D)
            self._safe_get(client_row, 'mobile_payment_ratio', 0.5),
            self._safe_get(client_row, 'ledger_quality_score', 0.5),
            self._safe_get(client_row, 'risk_score', 0.5),
            1.0 if self._safe_get(client_row, 'is_fraud', 0) == 0 else 0.0,  # Non-fraud indicator
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

