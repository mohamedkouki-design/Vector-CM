# Qdrant operations
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import pandas as pd
from embeddings_old import CreditEmbedder

class CreditMemory:
    def __init__(self, host="localhost", port=6333):
        self.client = QdrantClient(url=os.getenv("QDRANT_LINK"), api_key=os.getenv("QDRANT_API_KEY"))    
        self.embedder = CreditEmbedder()
        self.collection_name = "client_states"
        self.fraud_collection = "fraud_patterns"
        
        # Vector dimension - 12D from create_simple_vector()
        self.vector_dimension = 12
    
    def initialize_collections(self):
        """Create Qdrant collections with updated vector dimensions"""
        # Main client collection
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_dimension,  # Updated to 12D (numerical features from create_simple_vector)
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection: {self.collection_name} (dimension: {self.vector_dimension})")
        
        # Fraud collection
        if not self.client.collection_exists(self.fraud_collection):
            self.client.create_collection(
                collection_name=self.fraud_collection,
                vectors_config=VectorParams(
                    size=self.vector_dimension,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection: {self.fraud_collection} (dimension: {self.vector_dimension})")
    
    def load_historical_data(self, csv_path):
        """Load CSV data into Qdrant with new data structure from demo_data"""
        df = pd.read_csv(csv_path)
        
        points = []
        for idx, row in df.iterrows():
            vector = self.embedder.create_simple_vector(row)
            
            # Extract payload with all fields from new data structure
            payload = {
                "client_id": row['client_id'],
                "job_type": row.get('job_type', 'unknown'),
                "location": row.get('location', 'unknown'),
                "income": float(row['income']),
                "expenses": float(row['expenses']),
                "debt": float(row['debt']),
                "age": int(row['age']),
                "seniority_months": int(row['seniority_months']),
                "payment_consistency": float(row['payment_consistency']),
                "loan_amount": float(row['loan_amount']),
                "employment_type": row['employment_type'],
                "mobile_payment_ratio": float(row.get('mobile_payment_ratio', 0.5)),
                "ledger_quality_score": float(row.get('ledger_quality_score', 0.5)),
                "outcome": int(row.get('outcome', 0)),
                "outcome_label": row.get('outcome_label', 'unknown'),
                "risk_score": float(row.get('risk_score', 0.5)),
                "is_fraud": int(row.get('is_fraud', 0)),
                "timestamp": row.get('timestamp', '')
            }
            
            point = PointStruct(
                id=idx,
                vector=vector,
                payload=payload
            )
            points.append(point)
        
        # Upload in batches
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        print(f"✅ Loaded {len(points)} records into {self.collection_name}")
    
    def load_fraud_patterns(self, csv_path):
        """Load fraud cases with new data structure from demo_data"""
        df = pd.read_csv(csv_path)
        
        points = []
        for idx, row in df.iterrows():
            vector = self.embedder.create_simple_vector(row)
            
            # Extract payload with all fields from new fraud data structure
            payload = {
                "client_id": row['client_id'],
                "is_fraud": True,
                "job_type": row.get('job_type', 'unknown'),
                "location": row.get('location', 'unknown'),
                "income": float(row['income']),
                "expenses": float(row.get('expenses', 0)),
                "debt": float(row['debt']),
                "age": int(row['age']),
                "employment_type": row.get('employment_type', 'informal'),
                "risk_score": float(row.get('risk_score', 1.0)),
                "outcome_label": row.get('outcome_label', 'Fraud'),
                "risk_narrative": row.get('risk_narrative', ''),
                "timestamp": row.get('timestamp', '')
            }
            
            point = PointStruct(
                id=idx + 10000,  # Offset to avoid ID collision
                vector=vector,
                payload=payload
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.fraud_collection,
            points=points
        )
        
        print(f"✅ Loaded {len(points)} fraud patterns")
    
    def find_similar_clients(self, client_data, top_k=10):
        """Main similarity search using new data structure"""
        query_vector = self.embedder.create_simple_vector(client_data)
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )
        
        return results.points
    
    def search_by_risk_profile(self, client_data, top_k=10):
        """Search for similar risk profiles using risk-weighted vector"""
        query_vector = self.embedder.create_simple_vector(client_data)
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=None  # Can add filters like risk_score ranges
        )
        
        # Enrich results with outcome information
        enriched_results = []
        for point in results.points:
            enriched_results.append({
                'client_id': point.payload['client_id'],
                'similarity_score': point.score,
                'outcome_label': point.payload['outcome_label'],
                'risk_score': point.payload['risk_score'],
                'income': point.payload['income'],
                'debt': point.payload['debt'],
                'payment_consistency': point.payload['payment_consistency']
            })
        
        return enriched_results
    
    def check_fraud(self, client_data, threshold=0.75):
        """Check against fraud patterns using vector similarity (COSINE).
        Higher score = more similar. Threshold of 0.75+ = likely fraudulent.
        """
        query_vector = self.embedder.create_simple_vector(client_data)
        
        results = self.client.query_points(
            collection_name=self.fraud_collection,
            query=query_vector,
            limit=5
        )
        
        if results.points:
            top_match = results.points[0]
            is_fraudulent = top_match.score > threshold
            
            return {
                'is_fraud': is_fraudulent,
                'fraud_score': top_match.score,
                'similar_fraud': top_match.payload['client_id'],
                'fraud_narrative': top_match.payload.get('risk_narrative', ''),
                'threshold': threshold
            }
        
        return {
            'is_fraud': False,
            'fraud_score': 0.0,
            'similar_fraud': None,
            'fraud_narrative': '',
            'threshold': threshold
        }
    
    def load_from_demo_generator(self, generator, num_samples=100):
        """Load data directly from VectorCMDataGenerator (from demo_data.py)"""
        from demo_data import VectorCMDataGenerator
        
        points = []
        fraud_points = []
        for i in range(num_samples):
            client_profile = generator.generate_client_profile(i)
            vector = self.embedder.create_simple_vector(client_profile)
            
            # Build payload from client profile
            payload = {
                "client_id": client_profile['client_id'],
                "job_type": client_profile['job_type'],
                "location": client_profile['location'],
                "income": client_profile['income'],
                "expenses": client_profile['expenses'],
                "debt": client_profile['debt'],
                "age": client_profile['age'],
                "seniority_months": client_profile['seniority_months'],
                "payment_consistency": client_profile['payment_consistency'],
                "loan_amount": client_profile['loan_amount'],
                "employment_type": client_profile['employment_type'],
                "mobile_payment_ratio": client_profile['mobile_payment_ratio'],
                "ledger_quality_score": client_profile['ledger_quality_score'],
                "outcome": client_profile['outcome'],
                "outcome_label": client_profile['outcome_label'],
                "risk_score": client_profile['risk_score'],
                "risk_narrative": client_profile['risk_narrative'],
                "is_fraud": client_profile['is_fraud'],
                "timestamp": client_profile['timestamp']
            }
            
            if client_profile['is_fraud']:
                # Add to fraud collection
                fraud_points.append(PointStruct(
                    id=i + 10000,
                    vector=vector,
                    payload=payload
                ))
            else:
                # Add to client collection
                points.append(PointStruct(
                    id=i,
                    vector=vector,
                    payload=payload
                ))
        
        # Upsert both collections
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"✅ Loaded {len(points)} legitimate client profiles")
        
        if fraud_points:
            self.client.upsert(
                collection_name=self.fraud_collection,
                points=fraud_points
            )
            print(f"✅ Loaded {len(fraud_points)} fraud patterns")

# Initialize and load data
if __name__ == "__main__":
    from demo_data import VectorCMDataGenerator
    
    memory = CreditMemory()
    memory.initialize_collections()
    
    # Load from CSV files if they exist
    import os
    if os.path.exists('synthetic_clients.csv'):
        memory.load_historical_data('synthetic_clients.csv')
    
    if os.path.exists('synthetic_frauds.csv'):
        memory.load_fraud_patterns('synthetic_frauds.csv')
    
    # Alternatively, load directly from demo_data generator
    # generator = VectorCMDataGenerator()
    # memory.load_from_demo_generator(generator, num_samples=100)
    
    print("✅ Qdrant setup complete with new data structure!")