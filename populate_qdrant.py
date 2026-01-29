from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import pandas as pd
import numpy as np
from backend.services.embeddings import create_embedding
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_ultimate_dataset():
    """Populate Qdrant with ultimate dataset"""
    
    logger.info("="*70)
    logger.info("🚀 POPULATING QDRANT WITH ULTIMATE DATASET")
    logger.info("="*70)
    
    # Connect to Qdrant
    client = QdrantClient(host="localhost", port=6333)
    
    # Delete old collections
    collections = ['credit_history_memory', 'fraud_patterns', 'temporal_risk_memory']
    
    for collection in collections:
        try:
            client.delete_collection(collection)
            logger.info(f"  Deleted old collection: {collection}")
        except:
            pass
    
    # Create new collections
    logger.info("\n📦 Creating collections...")
    
    client.create_collection(
        collection_name="credit_history_memory",
        vectors_config=VectorParams(
            size=384,  # Standard embedding size
            distance=Distance.COSINE
        )
    )
    logger.info("  ✅ Created credit_history_memory")
    
    client.create_collection(
        collection_name="fraud_patterns",
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )
    logger.info("  ✅ Created fraud_patterns")
    
    client.create_collection(
        collection_name="temporal_risk_memory",
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )
    logger.info("  ✅ Created temporal_risk_memory")
    
    # Load clients
    logger.info("\n📊 Loading client data...")
    clients_df = pd.read_csv('data/synthetic_clients_ultimate.csv')
    logger.info(f"  Loaded {len(clients_df)} clients")
    
    # Populate credit_history_memory
    logger.info("\n💾 Populating credit_history_memory...")
    
    points = []
    for idx, row in clients_df.iterrows():
        # Create embedding
        vector = create_embedding(row)
        
        # Verify normalization
        norm = np.linalg.norm(vector)
        if abs(norm - 1.0) > 0.01:
            vector = vector / norm
        
        # Create point
        point = PointStruct(
            id=idx,
            vector=vector.tolist(),
            payload={
                'client_id': row['client_id'],
                'name': row['name'],
                'archetype': row['archetype'],
                'employment_type': row['employment_type'],
                'years_active': float(row['years_active']),
                'monthly_income': float(row['monthly_income']),
                'debt_ratio': float(row['debt_ratio']),
                'income_stability': float(row['income_stability']),
                'payment_regularity': float(row['payment_regularity']),
                'loan_source': row['loan_source'],
                'outcome': row['outcome'],
                'actual_outcome': row['actual_outcome'],
                'location': row['location'],
                'social_network': row['social_network']  # For Trust Rings
            }
        )
        points.append(point)
        
        # Upload in batches
        if len(points) >= 100:
            client.upsert(collection_name="credit_history_memory", points=points)
            logger.info(f"  Uploaded {len(points)} points (total: {idx + 1}/{len(clients_df)})")
            points = []
    
    # Upload remaining
    if points:
        client.upsert(collection_name="credit_history_memory", points=points)
        logger.info(f"  Uploaded final {len(points)} points")
    
    logger.info(f"  ✅ Populated credit_history_memory: {len(clients_df)} clients")
    
    # Populate temporal_risk_memory
    logger.info("\n⏰ Populating temporal_risk_memory...")
    
    temporal_points = []
    temporal_id = 0
    
    for idx, row in clients_df.iterrows():
        if row['outcome'] != 'approved':
            continue
        
        # Parse temporal snapshots
        try:
            snapshots = json.loads(row['temporal_snapshots'])
        except:
            continue
        
        # Create point for each snapshot
        for snapshot in snapshots:
            temp_data = {
                'archetype': row['archetype'],
                'debt_ratio': snapshot['debt_ratio'],
                'years_active': row['years_active'],
                'income_stability': snapshot['income_stability'],
                'payment_regularity': snapshot['payment_regularity'],
                'monthly_income': row['monthly_income']
            }
            
            vector = create_embedding(temp_data)
            vector = vector / np.linalg.norm(vector)
            
            point = PointStruct(
                id=temporal_id,
                vector=vector.tolist(),
                payload={
                    'client_id': row['client_id'],
                    'timestamp': snapshot['timestamp'],
                    'date': snapshot['date'],
                    'risk_score': snapshot['risk_score'],
                    'status': snapshot['status'],
                    'debt_ratio': snapshot['debt_ratio'],
                    'income_stability': snapshot['income_stability'],
                    'payment_regularity': snapshot['payment_regularity']
                }
            )
            temporal_points.append(point)
            temporal_id += 1
            
            if len(temporal_points) >= 100:
                client.upsert(collection_name="temporal_risk_memory", points=temporal_points)
                logger.info(f"  Uploaded {len(temporal_points)} temporal points")
                temporal_points = []
    
    if temporal_points:
        client.upsert(collection_name="temporal_risk_memory", points=temporal_points)
    
    logger.info(f"  ✅ Populated temporal_risk_memory: {temporal_id} snapshots")
    
    # Populate fraud_patterns
    logger.info("\n🚨 Populating fraud_patterns...")
    
    frauds_df = pd.read_csv('data/synthetic_frauds_ultimate.csv')
    logger.info(f"  Loaded {len(frauds_df)} fraud patterns")
    
    fraud_points = []
    for idx, row in frauds_df.iterrows():
        vector = create_embedding(row)
        vector = vector / np.linalg.norm(vector)
        
        point = PointStruct(
            id=idx + 10000,  # Offset to avoid collision
            vector=vector.tolist(),
            payload={
                'fraud_id': row['fraud_id'],
                'fraud_type': row['fraud_type'],
                'archetype': row['archetype'],
                'debt_ratio': float(row['debt_ratio']),
                'income_stability': float(row['income_stability']),
                'fraud_narrative': row['fraud_narrative'],
                'fraud_indicators': row['fraud_indicators']
            }
        )
        fraud_points.append(point)
        
        if len(fraud_points) >= 100:
            client.upsert(collection_name="fraud_patterns", points=fraud_points)
            logger.info(f"  Uploaded {len(fraud_points)} fraud patterns")
            fraud_points = []
    
    if fraud_points:
        client.upsert(collection_name="fraud_patterns", points=fraud_points)
    
    logger.info(f"  ✅ Populated fraud_patterns: {len(frauds_df)} patterns")
    
    # Final verification
    logger.info("\n✅ VERIFICATION")
    logger.info("="*70)
    
    for collection in collections:
        info = client.get_collection(collection)
        logger.info(f"  {collection}: {info.points_count} points")
    
    logger.info("\n🎉 POPULATION COMPLETE!")
    logger.info("="*70)

if __name__ == "__main__":
    populate_ultimate_dataset() 