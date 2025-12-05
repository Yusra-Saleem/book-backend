import os
from qdrant_client import QdrantClient
from src.core.config import settings

def check_qdrant_health():
    """
    Checks the health of the Qdrant vector database and returns collection statistics.
    """
    try:
        client = QdrantClient(
            host=os.getenv("QDRANT_HOST"),
            port=int(os.getenv("QDRANT_PORT", "6333")),
            api_key=settings.QDRANT_API_KEY,
        )
        collection_name = settings.QDRANT_COLLECTION_NAME
        
        # Check if collection exists
        collections = client.get_collections()
        exists = any(c.name == collection_name for c in collections.collections)
        
        if not exists:
            return {"status": "error", "message": f"Collection '{collection_name}' does not exist."}
        
        # Get collection info
        info = client.get_collection(collection_name)
        return {
            "status": "healthy",
            "collection_name": collection_name,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status.name
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
