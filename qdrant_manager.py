# Qdrant operations
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import pandas as pd
from embeddings import CreditEmbedder
class CreditMemory:
    def __init__(self, host="localhost", port=6333):
        self.client = QdrantClient(url="https://8f4992f2-2c36-4260-8e52-2faaecd1011d.europe-west3-0.gcp.cloud.qdrant.io", api_key=os.getenv("QDRANT_API_KEY"))
        
        self.embedder = CreditEmbedder()
        self.collection_name = "client_states"
        self.fraud_collection = "fraud_patterns"
    
    def initialize_collections(self):
        """Create Qdrant collections"""
        # Main client collection
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=8,  # Our simple vector dimension
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection: {self.collection_name}")
        
        # Fraud collection
        if not self.client.collection_exists(self.fraud_collection):
            self.client.create_collection(
                collection_name=self.fraud_collection,
                vectors_config=VectorParams(
                    size=8,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection: {self.fraud_collection}")
    
    def load_historical_data(self, csv_path):
        """Load CSV data into Qdrant"""
        df = pd.read_csv(csv_path)
        
        points = []
        for idx, row in df.iterrows():
            vector = self.embedder.create_simple_vector(row)
            
            point = PointStruct(
                id=idx,
                vector=vector,
                payload={
                    "client_id": row['client_id'],
                    "income": float(row['income']),
                    "expenses": float(row['expenses']),
                    "debt": float(row['debt']),
                    "age": int(row['age']),
                    "seniority_months": int(row['seniority_months']),
                    "payment_consistency": float(row['payment_consistency']),
                    "loan_amount": float(row['loan_amount']),
                    "employment_type": row['employment_type'],
                    "outcome": int(row['outcome']),
                    "timestamp": row['timestamp']
                }
            )
            points.append(point)
        
        # Upload in batches
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        print(f"✅ Loaded {len(points)} records into {self.collection_name}")
    
    def load_fraud_patterns(self, csv_path):
        """Load fraud cases"""
        df = pd.read_csv(csv_path)
        
        points = []
        for idx, row in df.iterrows():
            vector = self.embedder.create_simple_vector(row)
            
            point = PointStruct(
                id=idx + 10000,  # Offset to avoid ID collision
                vector=vector,
                payload={
                    "client_id": row['client_id'],
                    "is_fraud": True,
                    "income": float(row['income']),
                    "debt": float(row['debt'])
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.fraud_collection,
            points=points
        )
        
        print(f"✅ Loaded {len(points)} fraud patterns")
    
    def find_similar_clients(self, client_data, top_k=10):
        """Main similarity search"""
        query_vector = self.embedder.create_simple_vector(client_data)
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )
        
        return results.points
    
    def check_fraud(self, client_data, threshold=0.85):
        """Check against fraud patterns"""
        query_vector = self.embedder.create_simple_vector(client_data)
        
        results = self.client.query_points(
            collection_name=self.fraud_collection,
            query=query_vector,
            limit=5
        )
        
        if results.points and results.points[0].score > threshold:
            return True, results.points[0].score
        return False, 0.0

# Initialize and load data
if __name__ == "__main__":
    memory = CreditMemory()
    memory.initialize_collections()
    memory.load_historical_data('synthetic_clients.csv')
    memory.load_fraud_patterns('synthetic_frauds.csv')
    
    print("✅ Qdrant setup complete!")