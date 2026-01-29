from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging

logger = logging.getLogger(__name__)

class QdrantManager:
    """Simple Qdrant manager for Vector CM"""
    
    def __init__(self, host="localhost", port=6333):
        self.client = QdrantClient(host=host, port=port)
        logger.info(f"Connected to Qdrant at {host}:{port}")
    
    def search(self, collection_name, query_vector, limit=50):
        """
        Search for similar vectors using new Qdrant API
        
        Args:
            collection_name: Name of collection to search
            query_vector: List of floats (the embedding)
            limit: Number of results to return
        
        Returns:
            List of search results with .score and .payload
        """
        results = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit
        )
        return results.points
    
    def get_collection_info(self, collection_name):
        """Get collection information"""
        return self.client.get_collection(collection_name)