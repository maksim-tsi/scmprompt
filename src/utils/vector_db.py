"""
Vector database interface for the Maritime Case Generation pipeline.
Provides integration with Qdrant Cloud and Google embeddings.
"""
import os
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parents[2]))

# Import configuration
from dotenv import load_dotenv
load_dotenv()

def create_embeddings(text: str) -> Optional[List[float]]:
    """Generate embeddings for the given text using Google's API."""
    try:
        import google.generativeai as genai
        
        # Ensure API is configured with key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("Missing GOOGLE_API_KEY environment variable")
            return None
        
        # Configure the API explicitly each time
        genai.configure(api_key=api_key)
        
        # Use the embedding model from environment or default
        model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
        
        # Generate the embedding
        result = genai.embed_content(
            model=model,
            content=text,
            task_type="retrieval_document"
        )
        
        # Extract embedding from result (handle both response formats)
        if isinstance(result, dict) and "embedding" in result:
            return result["embedding"]
        elif hasattr(result, "embedding"):
            return result.embedding
        else:
            logger.error(f"Unexpected embedding result format: {type(result)}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating embeddings: {str(e)}")
        return None

def get_qdrant_client():
    """Initialize and return a Qdrant client using environment variables."""
    try:
        from qdrant_client import QdrantClient
        
        # Check for Cloud URL first (preferred)
        cloud_url = os.getenv("QDRANT_URL") or os.getenv("QDRANT_CLOUD_URL")
        api_key = os.getenv("QDRANT_API_KEY")
        
        if cloud_url and api_key:
            logger.info(f"Connecting to Qdrant Cloud at {cloud_url}")
            return QdrantClient(url=cloud_url, api_key=api_key)
        
        # Fall back to local connection
        host = os.getenv("QDRANT_HOST", "localhost")
        port = int(os.getenv("QDRANT_PORT", "6333"))
        logger.info(f"Connecting to Qdrant at {host}:{port}")
        return QdrantClient(host=host, port=port)
        
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return MockQdrantClient()

class MockQdrantClient:
    """Mock Qdrant client for when connections fail."""
    
    def __init__(self):
        logger.warning("Using mock Qdrant client - vector search disabled")
    
    def search(self, *args, **kwargs):
        return []
    
    def scroll(self, *args, **kwargs):
        return [], None
    
    def count(self, *args, **kwargs):
        class MockCount:
            def __init__(self):
                self.count = 0
        return MockCount()

# Replace the existing get_collection_names function with this one
def get_collection_name(collection_type: str = "datapoints") -> str:
    """
    Get standardized collection name from environment variables.
    
    Args:
        collection_type: Type of collection ('datapoints' or 'references')
        
    Returns:
        Collection name string
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    if collection_type == "references":
        return os.getenv("REFERENCES_COLLECTION", "case_generation_references")
    else:  # Default to datapoints
        return os.getenv("DATAPOINTS_COLLECTION", "logistics_datapoints")

def search_datapoints(query: str, limit: int = 5, collection_name: str = None) -> List[Dict[str, Any]]:
    """
    Search for datapoints matching the query.
    
    Args:
        query: The search query text
        limit: Maximum number of results to return
        collection_name: Optional collection name to override default
        
    Returns:
        List of matched datapoints
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Use provided collection name or get default from environment
    if not collection_name:
        collection_name = os.getenv("DATAPOINTS_COLLECTION", "logistics_datapoints")
    
    # Create embedding for query
    query_embedding = create_embeddings(query)
    if not query_embedding:
        logger.error(f"Failed to create embedding for query: {query}")
        return []
    
    # Get client and search
    try:
        client = get_qdrant_client()
        
        # Execute search
        results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=0.6,
            with_payload=True,
            with_vectors=False
        )
        
        # Format results with metadata
        datapoints = []
        for result in results:
            # Add metadata to the payload
            result.payload["search_score"] = result.score
            result.payload["matched_query"] = query
            result.payload["result_position"] = len(datapoints) + 1
            datapoints.append(result.payload)
        
        return datapoints
        
    except Exception as e:
        logger.error(f"Error searching datapoints with query '{query}' in collection '{collection_name}': {str(e)}")
        return []